from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import noload, selectinload

import src.adapters.db as db
import src.util.datetime_util as datetime_util
from src.adapters.aws import S3Config
from src.api.route_utils import raise_flask_error
from src.db.models.agency_models import Agency
from src.db.models.opportunity_models import Opportunity, OpportunityAttachment, OpportunitySummary
from src.util.env_config import PydanticBaseEnvConfig
from src.util.file_util import convert_public_s3_to_cdn_url, pre_sign_file_location


class AttachmentConfig(PydanticBaseEnvConfig):
    # If the CDN URL is set, we'll use it instead of pre-signing the file locations
    cdn_url: str | None = None


def _fetch_opportunity(
    db_session: db.Session, opportunity_id: int, load_all_opportunity_summaries: bool
) -> Opportunity:
    stmt = (
        select(Opportunity)
        .where(Opportunity.opportunity_id == opportunity_id)
        .where(Opportunity.is_draft.is_(False))
        .options(selectinload("*"))
        # To get the top_level_agency field set properly upfront,
        # we need to explicitly join here as the "*" approach doesn't
        # seem to work with the way our agency relationships are setup
        .options(selectinload(Opportunity.agency_record).selectinload(Agency.top_level_agency))
    )

    if not load_all_opportunity_summaries:
        stmt = stmt.options(noload(Opportunity.all_opportunity_summaries))

    opportunity = db_session.execute(stmt).unique().scalar_one_or_none()

    if opportunity is None:
        raise_flask_error(404, message=f"Could not find Opportunity with ID {opportunity_id}")

    return opportunity


def pre_sign_opportunity_file_location(
    opp_atts: list,
) -> list[OpportunityAttachment]:
    for opp_att in opp_atts:
        opp_att.download_path = pre_sign_file_location(opp_att.file_location)

    return opp_atts


def get_opportunity(db_session: db.Session, opportunity_id: int) -> Opportunity:
    opportunity = _fetch_opportunity(
        db_session, opportunity_id, load_all_opportunity_summaries=False
    )

    attachment_config = AttachmentConfig()
    if attachment_config.cdn_url is not None:
        s3_config = S3Config()
        for opp_att in opportunity.opportunity_attachments:
            opp_att.download_path = convert_public_s3_to_cdn_url(  # type: ignore
                opp_att.file_location, attachment_config.cdn_url, s3_config
            )
    else:
        pre_sign_opportunity_file_location(opportunity.opportunity_attachments)

    return opportunity


def get_opportunity_versions(db_session: db.Session, opportunity_id: int) -> dict:
    opportunity = _fetch_opportunity(
        db_session, opportunity_id, load_all_opportunity_summaries=True
    )

    now_us_eastern = datetime_util.get_now_us_eastern_date()

    forecasts = _filter_summaries(opportunity.all_forecasts, now_us_eastern)
    non_forecasts = _filter_summaries(opportunity.all_non_forecasts, now_us_eastern)

    return {"opportunity": opportunity, "forecasts": forecasts, "non_forecasts": non_forecasts}


def _filter_summaries(
    summaries: list[OpportunitySummary], current_date: date
) -> list[OpportunitySummary]:
    # Find the most recent summary
    most_recent_summary: OpportunitySummary | None = None
    for summary in summaries:
        if summary.revision_number is None:
            most_recent_summary = summary
            summaries.remove(summary)
            break

    # If there is no most recent summary, even if there is any history records
    # we have to filter all of the summaries. Effectively this would mean the most recent
    # was deleted, and we never show deleted summaries (or anything that comes before them).
    if most_recent_summary is None:
        return []

    # If the most recent summary isn't able to be public itself, we can't display any history
    # for this type of summary object.
    if not most_recent_summary.can_summary_be_public(current_date):
        return []

    summaries_to_keep = [most_recent_summary]

    # We want to process these in reverse order (most recent first)
    # as soon as we hit one that we need to filter, we stop adding records.
    #
    # For example, if a summary is marked as deleted, we won't add that, and
    # we also filter out all summaries that came before it (by just breaking the loop)
    summaries = sorted(summaries, key=lambda s: s.version_number, reverse=True)  # type: ignore

    for summary in summaries:
        if summary.is_deleted:
            break

        if summary.post_date is None:
            break

        # If a historical record was updated (or initially created) before
        # its own post date (ie. would have been visible when created) regardless
        # of what the current date may be
        # TODO - leaving this out of the implementation for the moment
        # as we need to investigate why this is being done and if there is a better
        # way as this ends up filtering out records we don't want removed
        # if summary.updated_at.date() < summary.post_date:
        #    break

        summaries_to_keep.append(summary)

    return summaries_to_keep
