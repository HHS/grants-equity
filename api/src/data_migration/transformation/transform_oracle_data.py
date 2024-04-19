import logging
from enum import StrEnum
from typing import Tuple

from sqlalchemy import select, delete

from src.adapters.db import PostgresDBClient
from src.db.models.opportunity_models import Opportunity
from src.db.models.transfer.topportunity_models import TransferTopportunity
from src.task.task import Task


from src.constants.lookup_constants import OpportunityCategory

logger = logging.getLogger(__name__)


class TransformOracleData(Task):
    class Metrics(StrEnum):
        TOTAL_RECORDS_PROCESSED = "total_records_processed"
        TOTAL_RECORDS_DELETED = "total_records_deleted"
        TOTAL_RECORDS_INSERTED = "total_records_inserted"
        TOTAL_RECORDS_UPDATED = "total_records_updated"



    def run_task(self) -> None:
        with self.db_session.begin():
            self.process_opportunities()
            # Opportunities

            # Assistance Listings

            # Opportunity Summary

            # One-to-many lookups

    def process_opportunities(self) -> None:

        # Fetch all opportunities that were modified
        # Alongside that, grab the existing opportunity record
        # TODO - add filters so it only contains updates
        # TODO - add a yield_per
        opportunities: list[Tuple[TransferTopportunity, Opportunity | None]] = self.db_session.execute(
            select(TransferTopportunity, Opportunity).join(Opportunity, TransferTopportunity.opportunity_id == Opportunity.opportunity_id, isouter=True)
        ).all()

        for source_opportunity, target_opportunity in opportunities:
            try:
                self.process_opportunity(source_opportunity, target_opportunity)
            except Exception:
                # TODO - more info
                # TODO - metric
                logger.exception("Failed to process opportunity")

    def process_opportunity(self, source_opportunity: TransferTopportunity, target_opportunity: Opportunity | None) -> None:
        extra = {"opportunity_id": source_opportunity.opportunity_id}
        logger.info("Processing opportunity", extra=extra)

        # TODO - whatever check we need to do to see if something should be deleted
        if source_opportunity.publisheruid == "should be deleted":
            logger.info("Deleting opportunity", extra=extra)

            if target_opportunity is None:
                raise Exception("Cannot delete opportunity as it does not exist")

            self.increment(self.Metrics.TOTAL_RECORDS_DELETED)
            self.db_session.delete(target_opportunity)


        else:
            logger.info("Transforming and upserting opportunity", extra=extra)
            transformed_opportunity = self.transform_opportunity(
                source_opportunity, target_opportunity
            )
            self.db_session.add(transformed_opportunity)


        logger.info("Processed opportunity", extra=extra)
        # TODO - set the field we query by to null (or set it? which way are we doing it?)
        # target_opportunity.whatever_field = None

    def process_assistance_listings(self) -> None:
        # TODO - https://github.com/HHS/simpler-grants-gov/issues/1746

        pass

    def process_opportunity_summaries(self) -> None:
        # TODO - https://github.com/HHS/simpler-grants-gov/issues/1747
        pass

    def process_one_to_many_lookup_tables(self) -> None:
        # TODO - https://github.com/HHS/simpler-grants-gov/issues/1749
        pass


    def transform_opportunity(
        self, source_opportunity: TransferTopportunity, target_opportunity: Opportunity | None
    ) -> Opportunity:
        if target_opportunity is None:
            self.increment(self.Metrics.TOTAL_RECORDS_INSERTED)
            target_opportunity = Opportunity(opportunity_id=source_opportunity.opportunity_id)
        else:
            self.increment(self.Metrics.TOTAL_RECORDS_UPDATED)

        target_opportunity.opportunity_number = source_opportunity.oppnumber
        target_opportunity.opportunity_title = source_opportunity.opptitle
        target_opportunity.agency = source_opportunity.owningagency
        target_opportunity.opportunity_category = transform_opportunity_category(
            source_opportunity.oppcategory
        )
        target_opportunity.category_explanation = source_opportunity.category_explanation
        target_opportunity.is_draft = source_opportunity.is_draft != "N"
        target_opportunity.revision_number = source_opportunity.revision_number
        target_opportunity.modified_comments = source_opportunity.modified_comments
        target_opportunity.publisher_user_id = source_opportunity.publisheruid
        target_opportunity.publisher_profile_id = source_opportunity.publisher_profile_id

        return target_opportunity

def transform_opportunity_category(value: str | None) -> OpportunityCategory | None:
    if value is None or value == "":
        return None

    match value:
        case "D":
            return OpportunityCategory.DISCRETIONARY
        case "M":
            return OpportunityCategory.MANDATORY
        case "C":
            return OpportunityCategory.CONTINUATION
        case "E":
            return OpportunityCategory.EARMARK
        case "O":
            return OpportunityCategory.OTHER

    raise ValueError(f"Unrecognized opportunity category")


# TODO - this is likely going to be run as part of a separate script
# but just to help build it out at the moment and test it, setting
# an entrypoint for easy local manual testing
def main():
    import src.logging

    with src.logging.init("transform_oracle_data"):
        db_client = PostgresDBClient()

        with db_client.get_session() as db_session:
            TransformOracleData(db_session).run()

main()