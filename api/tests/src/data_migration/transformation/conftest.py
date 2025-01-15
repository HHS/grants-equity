from datetime import date, datetime
from typing import Tuple

import pytest

import tests.src.db.models.factories as f
from src.adapters.aws import S3Config
from src.constants.lookup_constants import ApplicantType, FundingCategory, FundingInstrument
from src.data_migration.transformation.transform_oracle_data_task import TransformOracleDataTask
from src.db.models import staging
from src.db.models.agency_models import Agency
from src.db.models.opportunity_models import (
    LinkOpportunitySummaryApplicantType,
    LinkOpportunitySummaryFundingCategory,
    LinkOpportunitySummaryFundingInstrument,
    Opportunity,
    OpportunityAssistanceListing,
    OpportunityAttachment,
    OpportunitySummary,
)
from src.services.opportunity_attachments import attachment_util
from src.util import file_util
from tests.conftest import BaseTestClass


class BaseTransformTestClass(BaseTestClass):
    @pytest.fixture()
    def transform_oracle_data_task(
        self, db_session, enable_factory_create, truncate_opportunities
    ) -> TransformOracleDataTask:
        return TransformOracleDataTask(db_session)


def setup_opportunity(
    create_existing: bool,
    is_delete: bool = False,
    is_already_processed: bool = False,
    source_values: dict | None = None,
    all_fields_null: bool = False,
) -> staging.opportunity.Topportunity:
    if source_values is None:
        source_values = {}

    source_opportunity = f.StagingTopportunityFactory.create(
        **source_values,
        is_deleted=is_delete,
        already_transformed=is_already_processed,
        all_fields_null=all_fields_null,
        cfdas=[],
    )

    if create_existing:
        f.OpportunityFactory.create(
            opportunity_id=source_opportunity.opportunity_id,
            opportunity_attachments=[],
            # set created_at/updated_at to an earlier time so its clear
            # when they were last updated
            timestamps_in_past=True,
        )

    return source_opportunity


def setup_cfda(
    create_existing: bool,
    is_delete: bool = False,
    is_already_processed: bool = False,
    source_values: dict | None = None,
    all_fields_null: bool = False,
    opportunity: Opportunity | None = None,
) -> staging.opportunity.TopportunityCfda:
    if source_values is None:
        source_values = {}

    # If you don't provide an opportunity, you need to provide an ID
    if opportunity is not None:
        source_values["opportunity_id"] = opportunity.opportunity_id

    source_cfda = f.StagingTopportunityCfdaFactory.create(
        **source_values,
        opportunity=None,  # To override the factory trying to create something
        is_deleted=is_delete,
        already_transformed=is_already_processed,
        all_fields_null=all_fields_null,
    )

    if create_existing:
        f.OpportunityAssistanceListingFactory.create(
            opportunity=opportunity,
            opportunity_assistance_listing_id=source_cfda.opp_cfda_id,
            # set created_at/updated_at to an earlier time so its clear
            # when they were last updated
            timestamps_in_past=True,
        )

    return source_cfda


def setup_synopsis_forecast(
    is_forecast: bool,
    revision_number: int | None,
    create_existing: bool,
    opportunity: Opportunity | None,
    is_delete: bool = False,
    is_already_processed: bool = False,
    is_existing_current_opportunity_summary: bool = False,
    source_values: dict | None = None,
):
    if source_values is None:
        source_values = {}

    if is_forecast:
        if revision_number is None:
            factory_cls = f.StagingTforecastFactory
        else:
            factory_cls = f.StagingTforecastHistFactory
    else:
        if revision_number is None:
            factory_cls = f.StagingTsynopsisFactory
        else:
            factory_cls = f.StagingTsynopsisHistFactory

    if revision_number is not None:
        source_values["revision_number"] = revision_number

    if opportunity is not None:
        source_values["opportunity_id"] = opportunity.opportunity_id

    source_summary = factory_cls.create(
        **source_values,
        opportunity=None,  # To override the factory trying to create something
        is_deleted=is_delete,
        already_transformed=is_already_processed,
    )

    if create_existing:
        opportunity_summary = f.OpportunitySummaryFactory.create(
            opportunity=opportunity, is_forecast=is_forecast, revision_number=revision_number
        )
        if is_existing_current_opportunity_summary:
            f.CurrentOpportunitySummaryFactory.create(
                opportunity=opportunity, opportunity_summary=opportunity_summary
            )

    return source_summary


def setup_applicant_type(
    create_existing: bool,
    opportunity_summary: OpportunitySummary,
    legacy_lookup_value: str,
    applicant_type: ApplicantType | None = None,
    is_delete: bool = False,
    is_already_processed: bool = False,
    source_values: dict | None = None,
):
    if create_existing and is_delete is False and applicant_type is None:
        raise Exception(
            "If create_existing is True, is_delete is False - must provide the properly converted / mapped value for applicant_type"
        )

    if source_values is None:
        source_values = {}

    if opportunity_summary.is_forecast:
        source_values["forecast"] = None
        if opportunity_summary.revision_number is None:
            factory_cls = f.StagingTapplicanttypesForecastFactory
        else:
            factory_cls = f.StagingTapplicanttypesForecastHistFactory
            source_values["revision_number"] = opportunity_summary.revision_number
    else:
        source_values["synopsis"] = None
        if opportunity_summary.revision_number is None:
            factory_cls = f.StagingTapplicanttypesSynopsisFactory
        else:
            factory_cls = f.StagingTapplicanttypesSynopsisHistFactory
            source_values["revision_number"] = opportunity_summary.revision_number

    source_applicant_type = factory_cls.create(
        **source_values,
        opportunity_id=opportunity_summary.opportunity_id,
        is_deleted=is_delete,
        already_transformed=is_already_processed,
        at_id=legacy_lookup_value,
    )

    if create_existing:
        if opportunity_summary.is_forecast:
            legacy_id = source_applicant_type.at_frcst_id
        else:
            legacy_id = source_applicant_type.at_syn_id

        f.LinkOpportunitySummaryApplicantTypeFactory.create(
            opportunity_summary=opportunity_summary,
            legacy_applicant_type_id=legacy_id,
            applicant_type=applicant_type,
        )

    return source_applicant_type


def setup_funding_instrument(
    create_existing: bool,
    opportunity_summary: OpportunitySummary,
    legacy_lookup_value: str,
    funding_instrument: FundingInstrument | None = None,
    is_delete: bool = False,
    is_already_processed: bool = False,
    source_values: dict | None = None,
):
    if create_existing and is_delete is False and funding_instrument is None:
        raise Exception(
            "If create_existing is True, is_delete is False - must provide the properly converted / mapped value for funding_instrument"
        )

    if source_values is None:
        source_values = {}

    if opportunity_summary.is_forecast:
        source_values["forecast"] = None
        if opportunity_summary.revision_number is None:
            factory_cls = f.StagingTfundinstrForecastFactory
        else:
            factory_cls = f.StagingTfundinstrForecastHistFactory
            source_values["revision_number"] = opportunity_summary.revision_number
    else:
        source_values["synopsis"] = None
        if opportunity_summary.revision_number is None:
            factory_cls = f.StagingTfundinstrSynopsisFactory
        else:
            factory_cls = f.StagingTfundinstrSynopsisHistFactory
            source_values["revision_number"] = opportunity_summary.revision_number

    source_funding_instrument = factory_cls.create(
        **source_values,
        opportunity_id=opportunity_summary.opportunity_id,
        is_deleted=is_delete,
        already_transformed=is_already_processed,
        fi_id=legacy_lookup_value,
    )

    if create_existing:
        if opportunity_summary.is_forecast:
            legacy_id = source_funding_instrument.fi_frcst_id
        else:
            legacy_id = source_funding_instrument.fi_syn_id

        f.LinkOpportunitySummaryFundingInstrumentFactory.create(
            opportunity_summary=opportunity_summary,
            legacy_funding_instrument_id=legacy_id,
            funding_instrument=funding_instrument,
        )

    return source_funding_instrument


def setup_funding_category(
    create_existing: bool,
    opportunity_summary: OpportunitySummary,
    legacy_lookup_value: str,
    funding_category: FundingCategory | None = None,
    is_delete: bool = False,
    is_already_processed: bool = False,
    source_values: dict | None = None,
):
    if create_existing and is_delete is False and funding_category is None:
        raise Exception(
            "If create_existing is True, is_delete is False - must provide the properly converted / mapped value for funding_category"
        )

    if source_values is None:
        source_values = {}

    if opportunity_summary.is_forecast:
        source_values["forecast"] = None
        if opportunity_summary.revision_number is None:
            factory_cls = f.StagingTfundactcatForecastFactory
        else:
            factory_cls = f.StagingTfundactcatForecastHistFactory
            source_values["revision_number"] = opportunity_summary.revision_number
    else:
        source_values["synopsis"] = None
        if opportunity_summary.revision_number is None:
            factory_cls = f.StagingTfundactcatSynopsisFactory
        else:
            factory_cls = f.StagingTfundactcatSynopsisHistFactory
            source_values["revision_number"] = opportunity_summary.revision_number

    source_funding_category = factory_cls.create(
        **source_values,
        opportunity_id=opportunity_summary.opportunity_id,
        is_deleted=is_delete,
        already_transformed=is_already_processed,
        fac_id=legacy_lookup_value,
    )

    if create_existing:
        if opportunity_summary.is_forecast:
            legacy_id = source_funding_category.fac_frcst_id
        else:
            legacy_id = source_funding_category.fac_syn_id

        f.LinkOpportunitySummaryFundingCategoryFactory.create(
            opportunity_summary=opportunity_summary,
            legacy_funding_category_id=legacy_id,
            funding_category=funding_category,
        )

    return source_funding_category


def setup_agency(
    agency_code: str,
    create_existing: bool,
    is_already_processed: bool = False,
    deleted_fields: set | None = None,
    already_processed_fields: set | None = None,
    source_values: dict | None = None,
):
    if source_values is None:
        source_values = {}

    tgroups = f.create_tgroups_agency(
        agency_code,
        is_already_processed=is_already_processed,
        deleted_fields=deleted_fields,
        already_processed_fields=already_processed_fields,
        **source_values,
    )

    if create_existing:
        f.AgencyFactory.create(agency_code=agency_code)

    return tgroups


def setup_opportunity_attachment(
    create_existing: bool,
    opportunity: Opportunity,
    config: S3Config,
    is_delete: bool = False,
    is_already_processed: bool = False,
    source_values: dict | None = None,
):
    if source_values is None:
        source_values = {}

    synopsis_attachment = f.StagingTsynopsisAttachmentFactory.create(
        opportunity=None,
        opportunity_id=opportunity.opportunity_id,
        is_deleted=is_delete,
        already_transformed=is_already_processed,
        **source_values,
    )

    if create_existing:
        s3_path = attachment_util.get_s3_attachment_path(
            synopsis_attachment.file_name, synopsis_attachment.syn_att_id, opportunity, config
        )

        with file_util.open_stream(s3_path, "w") as outfile:
            outfile.write(f.fake.sentence(25))

        f.OpportunityAttachmentFactory.create(
            attachment_id=synopsis_attachment.syn_att_id,
            opportunity=opportunity,
            file_location=s3_path,
        )

    return synopsis_attachment


def validate_matching_fields(
    source, destination, fields: list[Tuple[str, str]], expect_all_to_match: bool
):
    mismatched_fields = []

    for source_field, destination_field in fields:
        if isinstance(source, dict):
            source_value = source.get(source_field)
        else:
            source_value = getattr(source, source_field)

        destination_value = getattr(destination, destination_field)

        # Some fields that we copy in are datetime typed (although behave as dates and we convert as such)
        # If so, we need to make sure they're both dates for the purposes of comparison
        if isinstance(source_value, datetime) and isinstance(destination_value, date):
            source_value = source_value.date()

        if source_value != destination_value:
            mismatched_fields.append(
                f"{source_field}/{destination_field}: '{source_value}' != '{destination_value}'"
            )

    # If a values weren't copied in an update
    # then we should expect most things to not match,
    # but randomness in the factories might cause some overlap
    if expect_all_to_match:
        assert (
            len(mismatched_fields) == 0
        ), f"Expected all fields to match between {source.__class__} and {destination.__class__}, but found mismatched fields: {','.join(mismatched_fields)}"
    else:
        assert (
            len(mismatched_fields) != 0
        ), f"Did not expect all fields to match between {source.__class__} and {destination.__class__}, but they did which means an unexpected update occurred"


def validate_opportunity(
    db_session,
    source_opportunity: staging.opportunity.Topportunity,
    expect_in_db: bool = True,
    expect_values_to_match: bool = True,
):
    opportunity = (
        db_session.query(Opportunity)
        .filter(Opportunity.opportunity_id == source_opportunity.opportunity_id)
        .one_or_none()
    )

    if not expect_in_db:
        assert opportunity is None
        return

    assert opportunity is not None
    # For fields that we expect to match 1:1, verify that they match as expected
    validate_matching_fields(
        source_opportunity,
        opportunity,
        [
            ("oppnumber", "opportunity_number"),
            ("opptitle", "opportunity_title"),
            ("owningagency", "agency"),
            ("category_explanation", "category_explanation"),
            ("revision_number", "revision_number"),
            ("modified_comments", "modified_comments"),
            ("publisheruid", "publisher_user_id"),
            ("publisher_profile_id", "publisher_profile_id"),
        ],
        expect_values_to_match,
    )

    # Validation of fields that aren't copied exactly
    if expect_values_to_match:
        # Deliberately validating is_draft with a different calculation
        if source_opportunity.is_draft == "N":
            assert opportunity.is_draft is False
        else:
            assert opportunity.is_draft is True


def validate_assistance_listing(
    db_session,
    source_cfda: staging.opportunity.TopportunityCfda,
    expect_in_db: bool = True,
    expect_values_to_match: bool = True,
):
    assistance_listing = (
        db_session.query(OpportunityAssistanceListing)
        .filter(
            OpportunityAssistanceListing.opportunity_assistance_listing_id
            == source_cfda.opp_cfda_id
        )
        .one_or_none()
    )

    if not expect_in_db:
        assert assistance_listing is None
        return

    assert assistance_listing is not None
    # For fields that we expect to match 1:1, verify that they match as expected
    validate_matching_fields(
        source_cfda,
        assistance_listing,
        [
            ("cfdanumber", "assistance_listing_number"),
            ("programtitle", "program_title"),
        ],
        expect_values_to_match,
    )


def get_summary_from_source(db_session, source_summary):
    revision_number = None
    is_forecast = source_summary.is_forecast
    if isinstance(source_summary, (staging.synopsis.TsynopsisHist, staging.forecast.TforecastHist)):
        revision_number = source_summary.revision_number

    opportunity_summary = (
        db_session.query(OpportunitySummary)
        .filter(
            OpportunitySummary.opportunity_id == source_summary.opportunity_id,
            OpportunitySummary.revision_number == revision_number,
            OpportunitySummary.is_forecast == is_forecast,
            # Populate existing to force it to fetch updates from the DB
        )
        .execution_options(populate_existing=True)
        .one_or_none()
    )

    return opportunity_summary


def validate_opportunity_summary(
    db_session, source_summary, expect_in_db: bool = True, expect_values_to_match: bool = True
):
    opportunity_summary = get_summary_from_source(db_session, source_summary)

    if not expect_in_db:
        assert opportunity_summary is None
        return

    matching_fields = [
        ("version_nbr", "version_number"),
        ("posting_date", "post_date"),
        ("archive_date", "archive_date"),
        ("fd_link_url", "additional_info_url"),
        ("fd_link_desc", "additional_info_url_description"),
        ("modification_comments", "modification_comments"),
        ("oth_cat_fa_desc", "funding_category_description"),
        ("applicant_elig_desc", "applicant_eligibility_description"),
        ("ac_name", "agency_name"),
        ("ac_email_addr", "agency_email_address"),
        ("ac_email_desc", "agency_email_address_description"),
        ("publisher_profile_id", "publisher_profile_id"),
        ("publisheruid", "publisher_user_id"),
        ("last_upd_id", "updated_by"),
        ("creator_id", "created_by"),
    ]

    if isinstance(source_summary, (staging.synopsis.Tsynopsis, staging.synopsis.TsynopsisHist)):
        matching_fields.extend(
            [
                ("syn_desc", "summary_description"),
                ("a_sa_code", "agency_code"),
                ("ac_phone_number", "agency_phone_number"),
                ("agency_contact_desc", "agency_contact_description"),
                ("response_date", "close_date"),
                ("response_date_desc", "close_date_description"),
                ("unarchive_date", "unarchive_date"),
            ]
        )
    else:  # Forecast+ForecastHist
        matching_fields.extend(
            [
                ("forecast_desc", "summary_description"),
                ("agency_code", "agency_code"),
                ("ac_phone", "agency_phone_number"),
                ("est_synopsis_posting_date", "forecasted_post_date"),
                ("est_appl_response_date", "forecasted_close_date"),
                ("est_appl_response_date_desc", "forecasted_close_date_description"),
                ("est_award_date", "forecasted_award_date"),
                ("est_project_start_date", "forecasted_project_start_date"),
                ("fiscal_year", "fiscal_year"),
            ]
        )

    # History only fields
    is_deleted = False
    if isinstance(source_summary, (staging.synopsis.TsynopsisHist, staging.forecast.TforecastHist)):
        matching_fields.extend([("revision_number", "revision_number")])

        is_deleted = source_summary.action_type == "D"

    assert opportunity_summary is not None
    validate_matching_fields(
        source_summary, opportunity_summary, matching_fields, expect_values_to_match
    )

    assert opportunity_summary.is_deleted == is_deleted


def validate_summary_and_nested(
    db_session,
    source_summary,
    expected_applicant_types: list[ApplicantType],
    expected_funding_categories: list[FundingCategory],
    expected_funding_instruments: list[FundingInstrument],
    expect_in_db: bool = True,
    expect_values_to_match: bool = True,
):
    validate_opportunity_summary(db_session, source_summary, expect_in_db, expect_values_to_match)

    if not expect_in_db:
        return

    created_record = get_summary_from_source(db_session, source_summary)

    assert set(created_record.applicant_types) == set(expected_applicant_types)
    assert set(created_record.funding_categories) == set(expected_funding_categories)
    assert set(created_record.funding_instruments) == set(expected_funding_instruments)


def validate_applicant_type(
    db_session,
    source_applicant_type,
    expect_in_db: bool = True,
    expected_applicant_type: ApplicantType | None = None,
    was_processed: bool = True,
    expect_values_to_match: bool = True,
):
    assert (source_applicant_type.transformed_at is not None) == was_processed

    # In order to properly find the link table value, need to first determine
    # the opportunity summary in a subquery
    opportunity_summary_id = (
        db_session.query(OpportunitySummary.opportunity_summary_id)
        .filter(
            OpportunitySummary.revision_number == source_applicant_type.revision_number,
            OpportunitySummary.is_forecast == source_applicant_type.is_forecast,
            OpportunitySummary.opportunity_id == source_applicant_type.opportunity_id,
        )
        .scalar()
    )

    link_applicant_type = (
        db_session.query(LinkOpportunitySummaryApplicantType)
        .filter(
            LinkOpportunitySummaryApplicantType.legacy_applicant_type_id
            == source_applicant_type.legacy_applicant_type_id,
            LinkOpportunitySummaryApplicantType.opportunity_summary_id == opportunity_summary_id,
        )
        .one_or_none()
    )

    if not expect_in_db:
        assert link_applicant_type is None
        return

    assert link_applicant_type is not None
    assert link_applicant_type.applicant_type == expected_applicant_type

    validate_matching_fields(
        source_applicant_type,
        link_applicant_type,
        [("creator_id", "created_by"), ("last_upd_id", "updated_by")],
        expect_values_to_match,
    )


def validate_funding_instrument(
    db_session,
    source_funding_instrument,
    expect_in_db: bool = True,
    expected_funding_instrument: FundingInstrument | None = None,
    was_processed: bool = True,
    expect_values_to_match: bool = True,
):
    assert (source_funding_instrument.transformed_at is not None) == was_processed

    # In order to properly find the link table value, need to first determine
    # the opportunity summary in a subquery
    opportunity_summary_id = (
        db_session.query(OpportunitySummary.opportunity_summary_id)
        .filter(
            OpportunitySummary.revision_number == source_funding_instrument.revision_number,
            OpportunitySummary.is_forecast == source_funding_instrument.is_forecast,
            OpportunitySummary.opportunity_id == source_funding_instrument.opportunity_id,
        )
        .scalar()
    )

    link_funding_instrument = (
        db_session.query(LinkOpportunitySummaryFundingInstrument)
        .filter(
            LinkOpportunitySummaryFundingInstrument.legacy_funding_instrument_id
            == source_funding_instrument.legacy_funding_instrument_id,
            LinkOpportunitySummaryFundingInstrument.opportunity_summary_id
            == opportunity_summary_id,
        )
        .one_or_none()
    )

    if not expect_in_db:
        assert link_funding_instrument is None
        return

    assert link_funding_instrument is not None
    assert link_funding_instrument.funding_instrument == expected_funding_instrument

    validate_matching_fields(
        source_funding_instrument,
        link_funding_instrument,
        [("creator_id", "created_by"), ("last_upd_id", "updated_by")],
        expect_values_to_match,
    )


def validate_funding_category(
    db_session,
    source_funding_category,
    expect_in_db: bool = True,
    expected_funding_category: FundingCategory | None = None,
    was_processed: bool = True,
    expect_values_to_match: bool = True,
):
    assert (source_funding_category.transformed_at is not None) == was_processed

    # In order to properly find the link table value, need to first determine
    # the opportunity summary in a subquery
    opportunity_summary_id = (
        db_session.query(OpportunitySummary.opportunity_summary_id)
        .filter(
            OpportunitySummary.revision_number == source_funding_category.revision_number,
            OpportunitySummary.is_forecast == source_funding_category.is_forecast,
            OpportunitySummary.opportunity_id == source_funding_category.opportunity_id,
        )
        .scalar()
    )

    link_funding_category = (
        db_session.query(LinkOpportunitySummaryFundingCategory)
        .filter(
            LinkOpportunitySummaryFundingCategory.legacy_funding_category_id
            == source_funding_category.legacy_funding_category_id,
            LinkOpportunitySummaryFundingCategory.opportunity_summary_id == opportunity_summary_id,
        )
        .one_or_none()
    )

    if not expect_in_db:
        assert link_funding_category is None
        return

    assert link_funding_category is not None
    assert link_funding_category.funding_category == expected_funding_category

    validate_matching_fields(
        source_funding_category,
        link_funding_category,
        [("creator_id", "created_by"), ("last_upd_id", "updated_by")],
        expect_values_to_match,
    )


AGENCY_FIELD_MAPPING = [
    ("AgencyName", "agency_name"),
    ("AgencyCode", "sub_agency_code"),
    ("AgencyCFDA", "assistance_listing_number"),
    ("ldapGp", "ldap_group"),
    ("description", "description"),
    ("label", "label"),
]

AGENCY_CONTACT_FIELD_MAPPING = [
    ("AgencyContactName", "contact_name"),
    ("AgencyContactAddress1", "address_line_1"),
    ("AgencyContactCity", "city"),
    ("AgencyContactState", "state"),
    ("AgencyContactZipCode", "zip_code"),
    ("AgencyContactTelephone", "phone_number"),
    ("AgencyContactEMail", "primary_email"),
]


def validate_agency(
    db_session,
    source_tgroups: list[staging.tgroups.Tgroups],
    expect_in_db: bool = True,
    expect_values_to_match: bool = True,
    is_test_agency: bool = False,
    non_matching_fields: set | None = None,
    deleted_fields: set | None = None,
):
    agency_code = source_tgroups[0].get_agency_code()
    agency = db_session.query(Agency).filter(Agency.agency_code == agency_code).one_or_none()

    if not expect_in_db:
        assert agency is None
        return

    assert agency is not None

    # need to restructure the tgroups into a dict
    tgroup_map = {tgroup.get_field_name(): tgroup.value for tgroup in source_tgroups}

    if non_matching_fields is not None:
        agency_field_mapping = [m for m in AGENCY_FIELD_MAPPING if m[0] not in non_matching_fields]
    else:
        agency_field_mapping = AGENCY_FIELD_MAPPING

    if deleted_fields is not None:
        agency_field_mapping = [m for m in agency_field_mapping if m[0] not in deleted_fields]

        deleted_field_mapping = [m for m in AGENCY_FIELD_MAPPING if m[0] in deleted_fields]
        for deleted_field in deleted_field_mapping:
            assert getattr(agency, deleted_field[1]) is None

    validate_matching_fields(tgroup_map, agency, agency_field_mapping, expect_values_to_match)
    assert agency.is_test_agency == is_test_agency

    if non_matching_fields is not None:
        agency_contact_field_mapping = [
            m for m in AGENCY_CONTACT_FIELD_MAPPING if m[0] not in non_matching_fields
        ]
    else:
        agency_contact_field_mapping = AGENCY_CONTACT_FIELD_MAPPING

    validate_matching_fields(
        tgroup_map, agency.agency_contact_info, agency_contact_field_mapping, expect_values_to_match
    )


def validate_opportunity_attachment(
    db_session,
    source_attachment,
    expect_in_db: bool = True,
    expect_values_to_match: bool = True,
):

    opportunity_attachment = (
        db_session.query(OpportunityAttachment)
        .filter(OpportunityAttachment.attachment_id == source_attachment.syn_att_id)
        .one_or_none()
    )

    if not expect_in_db:
        assert opportunity_attachment is None
        return

    assert opportunity_attachment is not None
    validate_matching_fields(
        source_attachment,
        opportunity_attachment,
        [
            ("syn_att_id", "attachment_id"),
            ("opportunity_id", "opportunity_id"),
            ("mime_type", "mime_type"),
            ("file_name", "file_name"),
            ("file_desc", "file_description"),
            ("file_lob_size", "file_size_bytes"),
            ("creator_id", "created_by"),
            ("last_upd_id", "updated_by"),
            ("syn_att_folder_id", "legacy_folder_id"),
        ],
        expect_values_to_match,
    )

    # Validate the contents of the file and that the file exists on s3
    with file_util.open_stream(opportunity_attachment.file_location) as s3_file:
        contents = s3_file.read()

        if expect_values_to_match:
            assert contents.encode() == source_attachment.file_lob
        else:
            assert contents.encode() != source_attachment.file_lob
