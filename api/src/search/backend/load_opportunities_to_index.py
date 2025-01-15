import base64
import logging
from enum import StrEnum
from typing import Iterator, Sequence

import smart_open
from opensearchpy.exceptions import ConnectionTimeout, TransportError
from pydantic import Field
from pydantic_settings import SettingsConfigDict
from sqlalchemy import delete, select
from sqlalchemy.orm import noload, selectinload
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

import src.adapters.db as db
import src.adapters.search as search
from src.api.opportunities_v1.opportunity_schemas import OpportunityV1Schema
from src.db.models.agency_models import Agency
from src.db.models.opportunity_models import (
    CurrentOpportunitySummary,
    Opportunity,
    OpportunityAttachment,
    OpportunitySearchIndexQueue,
)
from src.task.task import Task
from src.util.datetime_util import get_now_us_eastern_datetime
from src.util.env_config import PydanticBaseEnvConfig

logger = logging.getLogger(__name__)


class LoadOpportunitiesToIndexConfig(PydanticBaseEnvConfig):
    model_config = SettingsConfigDict(env_prefix="LOAD_OPP_SEARCH_")

    shard_count: int = Field(default=1)  # LOAD_OPP_SEARCH_SHARD_COUNT
    replica_count: int = Field(default=1)  # LOAD_OPP_SEARCH_REPLICA_COUNT

    # TODO - these might make sense to come from some sort of opportunity-search-index-config?
    # look into this a bit more when we setup the search endpoint itself.
    alias_name: str = Field(default="opportunity-index-alias")  # LOAD_OPP_SEARCH_ALIAS_NAME
    index_prefix: str = Field(default="opportunity-index")  # LOAD_OPP_INDEX_PREFIX

    enable_opportunity_attachment_pipeline: bool = Field(
        default=False, alias="ENABLE_OPPORTUNITY_ATTACHMENT_PIPELINE"
    )


class LoadOpportunitiesToIndex(Task):
    class Metrics(StrEnum):
        RECORDS_LOADED = "records_loaded"
        TEST_RECORDS_SKIPPED = "test_records_skipped"

    def __init__(
        self,
        db_session: db.Session,
        search_client: search.SearchClient,
        is_full_refresh: bool = True,
        config: LoadOpportunitiesToIndexConfig | None = None,
    ) -> None:
        super().__init__(db_session)

        self.search_client = search_client
        self.is_full_refresh = is_full_refresh
        if config is None:
            config = LoadOpportunitiesToIndexConfig()
        self.config = config

        if is_full_refresh:
            current_timestamp = get_now_us_eastern_datetime().strftime("%Y-%m-%d_%H-%M-%S")
            self.index_name = f"{self.config.index_prefix}-{current_timestamp}"
        else:
            self.index_name = self.config.alias_name
        self.set_metrics({"index_name": self.index_name})

    def run_task(self) -> None:
        logger.info("Creating multi-attachment pipeline")
        self._create_multi_attachment_pipeline()
        if self.is_full_refresh:
            logger.info("Running full refresh")
            self.full_refresh()
        else:
            logger.info("Running incremental load")
            self.incremental_updates_and_deletes()

    def _create_multi_attachment_pipeline(self) -> None:
        """
        Create multi-attachment processor
        """
        pipeline = {
            "description": "Extract attachment information",
            "processors": [
                {
                    "foreach": {
                        "field": "attachments",
                        "processor": {
                            "attachment": {
                                "target_field": "_ingest._value.attachment",
                                "field": "_ingest._value.data",
                            }
                        },
                    }
                }
            ],
        }

        self.search_client.put_pipeline(pipeline, "multi-attachment")

    def incremental_updates_and_deletes(self) -> None:
        existing_opportunity_ids = self.fetch_existing_opportunity_ids_in_index()

        # Handle updates/inserts
        self._handle_incremental_upserts(existing_opportunity_ids)

        # Handle deletes
        self._handle_incremental_delete(existing_opportunity_ids)

    def _handle_incremental_upserts(self, existing_opportunity_ids: set[int]) -> None:
        """Handle updates/inserts of opportunities into the search index when running incrementally"""

        # Fetch opportunities that need processing from the queue
        queued_opportunities = (
            self.db_session.execute(
                select(Opportunity)
                .join(OpportunitySearchIndexQueue)
                .join(CurrentOpportunitySummary)
                .where(
                    Opportunity.is_draft.is_(False),
                    CurrentOpportunitySummary.opportunity_status.isnot(None),
                )
                .options(selectinload("*"), noload(Opportunity.all_opportunity_summaries))
            )
            .scalars()
            .all()
        )

        # Process updates and inserts
        processed_opportunity_ids = set()
        opportunities_to_index = []

        for opportunity in queued_opportunities:
            logger.info(
                "Processing queued opportunity",
                extra={
                    "opportunity_id": opportunity.opportunity_id,
                    "status": (
                        "update"
                        if opportunity.opportunity_id in existing_opportunity_ids
                        else "insert"
                    ),
                },
            )

            # Add to index batch if it's indexable
            opportunities_to_index.append(opportunity)
            processed_opportunity_ids.add(opportunity.opportunity_id)

        # Bulk index the opportunities (handles both inserts and updates)
        if opportunities_to_index:
            loaded_ids = self.load_records(opportunities_to_index)
            logger.info(f"Indexed {len(loaded_ids)} opportunities")

        # Clear processed / skipped entries from the queue
        self.db_session.execute(
            delete(OpportunitySearchIndexQueue).where(
                OpportunitySearchIndexQueue.opportunity_id.in_(processed_opportunity_ids)
            )
        )

    def _handle_incremental_delete(self, existing_opportunity_ids: set[int]) -> None:
        """Handle deletion of opportunities when running incrementally

        Scenarios in which we delete an opportunity from the index:
        * An opportunity is no longer in our database
        * An opportunity is a draft (unlikely to ever happen, would require published->draft)
        * An opportunity loses its opportunity status
        * An opportunity has a test agency
        """

        # Fetch the opportunity IDs of opportunities we would expect to be in the index
        opportunity_ids_we_want_in_search: set[int] = set(
            self.db_session.execute(
                select(Opportunity.opportunity_id)
                .join(CurrentOpportunitySummary)
                .join(Agency, Opportunity.agency_code == Agency.agency_code, isouter=True)
                .where(
                    Opportunity.is_draft.is_(False),
                    CurrentOpportunitySummary.opportunity_status.isnot(None),
                    # We treat a null agency as fine
                    # We only want to filter out if is_test_agency=True specifically
                    Agency.is_test_agency.isnot(True),
                )
            )
            .scalars()
            .all()
        )

        opportunity_ids_to_delete = existing_opportunity_ids - opportunity_ids_we_want_in_search

        for opportunity_id in opportunity_ids_to_delete:
            logger.info(
                "Deleting opportunity from search",
                extra={"opportunity_id": opportunity_id, "status": "delete"},
            )

        if opportunity_ids_to_delete:
            self.search_client.bulk_delete(self.index_name, opportunity_ids_to_delete)

    def full_refresh(self) -> None:
        # create the index
        self.search_client.create_index(
            self.index_name,
            shard_count=self.config.shard_count,
            replica_count=self.config.replica_count,
        )

        # load the records
        for opp_batch in self.fetch_opportunities():
            self.load_records(opp_batch)

        # handle aliasing of endpoints
        self.search_client.swap_alias_index(
            self.index_name,
            self.config.alias_name,
        )

        # cleanup old indexes
        self.search_client.cleanup_old_indices(self.config.index_prefix, [self.index_name])

    def fetch_opportunities(self) -> Iterator[Sequence[Opportunity]]:
        """
        Fetch the opportunities in batches. The iterator returned
        will give you each individual batch to be processed.

        Fetches all opportunities where:
            * is_draft = False
            * current_opportunity_summary is not None
        """
        return (
            self.db_session.execute(
                select(Opportunity)
                .join(CurrentOpportunitySummary)
                .where(
                    Opportunity.is_draft.is_(False),
                    CurrentOpportunitySummary.opportunity_status.isnot(None),
                )
                .options(selectinload("*"), noload(Opportunity.all_opportunity_summaries))
                # Top level agency won't be automatically fetched up front unless we add this
                # due to the odd nature of the relationship we have setup for the agency table
                # Adding it here improves performance when serializing to JSON as we won't need to
                # call out to the DB repeatedly.
                .options(
                    selectinload(Opportunity.agency_record).selectinload(Agency.top_level_agency)
                )
                .execution_options(yield_per=1000)
            )
            .scalars()
            .partitions()
        )

    def fetch_existing_opportunity_ids_in_index(self) -> set[int]:
        if not self.search_client.alias_exists(self.index_name):
            raise RuntimeError(
                "Alias %s does not exist, please run the full refresh job before the incremental job"
                % self.index_name
            )

        opportunity_ids: set[int] = set()

        for response in self.search_client.scroll(
            self.config.alias_name,
            {"size": 10000, "_source": ["opportunity_id"]},
            include_scores=False,
        ):
            for record in response.records:
                opportunity_ids.add(record["opportunity_id"])

        return opportunity_ids

    def filter_attachments(
        self, attachments: list[OpportunityAttachment]
    ) -> list[OpportunityAttachment]:
        return [attachment for attachment in attachments]

    def get_attachment_json_for_opportunity(
        self, opp_attachments: list[OpportunityAttachment]
    ) -> list[dict]:

        attachments = []
        for att in opp_attachments:
            with smart_open.open(
                att.file_location,
                "rb",
            ) as file:
                file_content = file.read()
                attachments.append(
                    {
                        "filename": att.file_name,
                        "data": base64.b64encode(file_content).decode("utf-8"),
                    }
                )

        return attachments

    @retry(
        stop=stop_after_attempt(3),  # Retry up to 3 times
        wait=wait_fixed(2),  # Wait 2 seconds between retries
        retry=retry_if_exception_type(
            (TransportError, ConnectionTimeout)
        ),  # Retry on TransportError (including timeouts)
    )
    def load_records(self, records: Sequence[Opportunity]) -> set[int]:
        logger.info("Loading batch of opportunities...")

        schema = OpportunityV1Schema()
        json_records = []

        loaded_opportunity_ids = set()

        for record in records:
            log_extra = {
                "opportunity_id": record.opportunity_id,
                "opportunity_status": record.opportunity_status,
            }
            logger.info("Preparing opportunity for upload to search index", extra=log_extra)

            # If the opportunity has a test agency, skip uploading it to the index
            if record.agency_record and record.agency_record.is_test_agency:
                logger.info(
                    "Skipping upload of opportunity as agency is a test agency",
                    extra=log_extra | {"agency": record.agency_code},
                )
                self.increment(self.Metrics.TEST_RECORDS_SKIPPED)
                continue

            json_record = schema.dump(record)
            if self.config.enable_opportunity_attachment_pipeline:
                json_record["attachments"] = self.get_attachment_json_for_opportunity(
                    record.opportunity_attachments
                )

            json_records.append(json_record)
            self.increment(self.Metrics.RECORDS_LOADED)

            loaded_opportunity_ids.add(record.opportunity_id)

        self.search_client.bulk_upsert(
            self.index_name, json_records, "opportunity_id", pipeline="multi-attachment"
        )

        return loaded_opportunity_ids
