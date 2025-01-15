import pytest

import tests.src.db.models.factories as f
from src.constants.lookup_constants import ApplicantType, FundingCategory, FundingInstrument
from src.data_migration.transformation.transform_oracle_data_task import TransformOracleDataTask
from src.db.models import staging
from src.db.models.opportunity_models import Opportunity
from tests.conftest import BaseTestClass
from tests.src.data_migration.transformation.conftest import (
    get_summary_from_source,
    setup_agency,
    setup_cfda,
    setup_opportunity,
    setup_synopsis_forecast,
    validate_agency,
    validate_applicant_type,
    validate_assistance_listing,
    validate_funding_category,
    validate_funding_instrument,
    validate_opportunity,
    validate_opportunity_summary,
    validate_summary_and_nested,
)


class TestTransformFullRunTask(BaseTestClass):
    # The above tests validated we could run the tests

    @pytest.fixture()
    def truncate_all_staging_tables(self, db_session):
        # Iterate over all the staging tables and truncate them to avoid
        # any collisions with prior test data. There are no foreign keys
        # between these tables, so the order doesn't matter here.
        for table in staging.metadata.tables.values():
            db_session.query(table).delete()

    @pytest.fixture()
    def transform_oracle_data_task(
        self,
        db_session,
        enable_factory_create,
        truncate_opportunities,
        truncate_all_staging_tables,
        s3_config,
    ) -> TransformOracleDataTask:
        return TransformOracleDataTask(db_session)

    def test_all_inserts(self, db_session, transform_oracle_data_task):
        # Test that we're fully capable of processing inserts across an entire opportunity record
        parent_agency = setup_agency("INSERTAGENCY", create_existing=False)
        subagency = setup_agency("INSERTAGENCY-ABC", create_existing=False)

        opportunity = setup_opportunity(
            create_existing=False, source_values={"owningagency": "INSERTAGENCY-ABC"}
        )

        cfda1 = setup_cfda(create_existing=False, opportunity=opportunity)
        cfda2 = setup_cfda(create_existing=False, opportunity=opportunity)

        ### Forecast
        forecast = setup_synopsis_forecast(
            create_existing=False, is_forecast=True, revision_number=None, opportunity=opportunity
        )
        f.StagingTapplicanttypesForecastFactory(forecast=forecast, at_id="01")
        # This is a duplicate record (same at_id, but will have a different at_frcst_id), verifying we handle duplicates
        f.StagingTapplicanttypesForecastFactory(forecast=forecast, at_id="01")
        f.StagingTfundactcatForecastFactory(forecast=forecast, fac_id="RA")
        f.StagingTfundactcatForecastFactory(forecast=forecast, fac_id="HO")
        # Duplicate here too
        f.StagingTfundactcatForecastFactory(forecast=forecast, fac_id="HO")

        f.StagingTfundinstrForecastFactory(forecast=forecast, fi_id="CA")
        f.StagingTfundinstrForecastFactory(forecast=forecast, fi_id="G")
        # Duplicate here as well
        f.StagingTfundinstrForecastFactory(forecast=forecast, fi_id="G")

        ### Forecast Hist 1 (only applicant types)
        forecast_hist1 = setup_synopsis_forecast(
            create_existing=False, is_forecast=True, revision_number=1, opportunity=opportunity
        )
        f.StagingTapplicanttypesForecastHistFactory(forecast=forecast_hist1, at_id="05")
        f.StagingTapplicanttypesForecastHistFactory(forecast=forecast_hist1, at_id="06")
        f.StagingTapplicanttypesForecastHistFactory(forecast=forecast_hist1, at_id="25")
        f.StagingTapplicanttypesForecastHistFactory(forecast=forecast_hist1, at_id="13")
        f.StagingTapplicanttypesForecastHistFactory(forecast=forecast_hist1, at_id="11")

        ### Forecast Hist 2 (only funding instrument and funding categories)
        forecast_hist2 = setup_synopsis_forecast(
            create_existing=False, is_forecast=True, revision_number=2, opportunity=opportunity
        )
        f.StagingTfundactcatForecastHistFactory(forecast=forecast_hist2, fac_id="ED")
        f.StagingTfundactcatForecastHistFactory(forecast=forecast_hist2, fac_id="HU")
        f.StagingTfundactcatForecastHistFactory(forecast=forecast_hist2, fac_id="IIJ")
        f.StagingTfundactcatForecastHistFactory(forecast=forecast_hist2, fac_id="T")
        f.StagingTfundinstrForecastHistFactory(forecast=forecast_hist2, fi_id="G")
        f.StagingTfundinstrForecastHistFactory(forecast=forecast_hist2, fi_id="CA")
        f.StagingTfundinstrForecastHistFactory(forecast=forecast_hist2, fi_id="PC")

        ### Synopsis (has some invalid values)
        synopsis = setup_synopsis_forecast(
            create_existing=False, is_forecast=False, revision_number=None, opportunity=opportunity
        )
        f.StagingTapplicanttypesSynopsisFactory(synopsis=synopsis, at_id="06")
        f.StagingTapplicanttypesSynopsisFactory(synopsis=synopsis, at_id="07")
        f.StagingTapplicanttypesSynopsisFactory(synopsis=synopsis, at_id="11")
        # Invalid value
        f.StagingTapplicanttypesSynopsisFactory(synopsis=synopsis, at_id="x")
        f.StagingTfundactcatSynopsisFactory(synopsis=synopsis, fac_id="ACA")
        f.StagingTfundactcatSynopsisFactory(synopsis=synopsis, fac_id="O")
        # Invalid value
        f.StagingTfundactcatSynopsisFactory(synopsis=synopsis, fac_id="BOB")
        f.StagingTfundinstrSynopsisFactory(synopsis=synopsis, fi_id="G")
        # Invalid value
        f.StagingTfundinstrSynopsisFactory(synopsis=synopsis, fi_id="x")

        # Synopsis Hist (has no link values, is also marked as deleted)
        synopsis_hist = setup_synopsis_forecast(
            create_existing=False, is_forecast=False, revision_number=5, opportunity=opportunity
        )

        transform_oracle_data_task.run()

        created_opportunity: Opportunity = (
            db_session.query(Opportunity)
            .filter(Opportunity.opportunity_id == opportunity.opportunity_id)
            .one_or_none()
        )

        # Validate that all of the expected records were created
        # not worrying about all of the transforms specifically here,
        # just that everything is in place

        assert created_opportunity is not None
        validate_opportunity(db_session, opportunity)
        assert {
            al.opportunity_assistance_listing_id
            for al in created_opportunity.opportunity_assistance_listings
        } == {cfda1.opp_cfda_id, cfda2.opp_cfda_id}

        assert len(created_opportunity.all_opportunity_summaries) == 5

        created_forecast = get_summary_from_source(db_session, forecast)
        assert created_forecast is not None
        validate_summary_and_nested(
            db_session,
            forecast,
            [ApplicantType.COUNTY_GOVERNMENTS],
            [FundingCategory.RECOVERY_ACT, FundingCategory.HOUSING],
            [FundingInstrument.GRANT, FundingInstrument.COOPERATIVE_AGREEMENT],
        )
        validate_summary_and_nested(
            db_session,
            forecast_hist1,
            [
                ApplicantType.OTHER,
                ApplicantType.INDEPENDENT_SCHOOL_DISTRICTS,
                ApplicantType.PUBLIC_AND_STATE_INSTITUTIONS_OF_HIGHER_EDUCATION,
                ApplicantType.NONPROFITS_NON_HIGHER_EDUCATION_WITHOUT_501C3,
                ApplicantType.OTHER_NATIVE_AMERICAN_TRIBAL_ORGANIZATIONS,
            ],
            [],
            [],
        )
        validate_summary_and_nested(
            db_session,
            forecast_hist2,
            [],
            [
                FundingCategory.TRANSPORTATION,
                FundingCategory.EDUCATION,
                FundingCategory.INFRASTRUCTURE_INVESTMENT_AND_JOBS_ACT,
                FundingCategory.HUMANITIES,
            ],
            [
                FundingInstrument.COOPERATIVE_AGREEMENT,
                FundingInstrument.GRANT,
                FundingInstrument.PROCUREMENT_CONTRACT,
            ],
        )
        validate_summary_and_nested(
            db_session,
            synopsis,
            [
                ApplicantType.PUBLIC_AND_STATE_INSTITUTIONS_OF_HIGHER_EDUCATION,
                ApplicantType.FEDERALLY_RECOGNIZED_NATIVE_AMERICAN_TRIBAL_GOVERNMENTS,
                ApplicantType.OTHER_NATIVE_AMERICAN_TRIBAL_ORGANIZATIONS,
            ],
            [FundingCategory.AFFORDABLE_CARE_ACT, FundingCategory.OTHER],
            [FundingInstrument.GRANT],
        )
        validate_summary_and_nested(db_session, synopsis_hist, [], [], [])

        validate_agency(db_session, parent_agency)
        validate_agency(db_session, subagency)

        assert {
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_PROCESSED: 39,
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_INSERTED: 33,
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_UPDATED: 0,
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_DELETED: 0,
            transform_oracle_data_task.Metrics.TOTAL_DUPLICATE_RECORDS_SKIPPED: 3,
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_ORPHANED: 0,
            transform_oracle_data_task.Metrics.TOTAL_ERROR_COUNT: 3,
        }.items() <= transform_oracle_data_task.metrics.items()

    def test_mix_of_inserts_updates_deletes(self, db_session, transform_oracle_data_task):
        parent_agency = setup_agency("UPDATEAGENCY", create_existing=True)
        subagency = setup_agency(
            "UPDATEAGENCY-XYZ",
            create_existing=True,
            deleted_fields={"AgencyContactEMail2", "ldapGp", "description"},
        )

        existing_opportunity = f.OpportunityFactory(
            no_current_summary=True, opportunity_assistance_listings=[], agency_code="UPDATEAGENCY"
        )
        opportunity = f.StagingTopportunityFactory(
            opportunity_id=existing_opportunity.opportunity_id, cfdas=[]
        )

        cfda_insert = setup_cfda(create_existing=False, opportunity=existing_opportunity)
        cfda_update = setup_cfda(create_existing=True, opportunity=existing_opportunity)
        setup_cfda(create_existing=True, is_delete=True, opportunity=existing_opportunity)

        ### Forecast (update)
        summary_forecast = f.OpportunitySummaryFactory(
            is_forecast=True, opportunity=existing_opportunity, no_link_values=True
        )
        forecast_update = f.StagingTforecastFactory(opportunity=opportunity)

        ## Forecast applicant type
        # insert
        f.StagingTapplicanttypesForecastFactory(forecast=forecast_update, at_id="01")
        # update
        f.StagingTapplicanttypesForecastFactory(
            forecast=forecast_update, at_id="02", at_frcst_id=1000
        )
        f.LinkOpportunitySummaryApplicantTypeFactory(
            opportunity_summary=summary_forecast,
            applicant_type=ApplicantType.CITY_OR_TOWNSHIP_GOVERNMENTS,
            legacy_applicant_type_id=1000,
        )
        # delete
        f.StagingTapplicanttypesForecastFactory(
            forecast=forecast_update, at_id="04", at_frcst_id=1001, is_deleted=True
        )
        f.LinkOpportunitySummaryApplicantTypeFactory(
            opportunity_summary=summary_forecast,
            applicant_type=ApplicantType.SPECIAL_DISTRICT_GOVERNMENTS,
            legacy_applicant_type_id=1001,
        )

        ## Forecast funding category
        # insert
        f.StagingTfundactcatForecastFactory(forecast=forecast_update, fac_id="OZ")
        # update
        f.StagingTfundactcatForecastFactory(
            forecast=forecast_update, fac_id="NR", fac_frcst_id=2000
        )
        f.LinkOpportunitySummaryFundingCategoryFactory(
            opportunity_summary=summary_forecast,
            funding_category=FundingCategory.NATURAL_RESOURCES,
            legacy_funding_category_id=2000,
        )
        # delete
        f.StagingTfundactcatForecastFactory(
            forecast=forecast_update, fac_id="ST", fac_frcst_id=2001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingCategoryFactory(
            opportunity_summary=summary_forecast,
            funding_category=FundingCategory.SCIENCE_TECHNOLOGY_AND_OTHER_RESEARCH_AND_DEVELOPMENT,
            legacy_funding_category_id=2001,
        )

        ## Forecast funding instrument
        # insert
        f.StagingTfundinstrForecastFactory(forecast=forecast_update, fi_id="G")
        # update
        f.StagingTfundinstrForecastFactory(forecast=forecast_update, fi_id="CA", fi_frcst_id=3000)
        f.LinkOpportunitySummaryFundingInstrumentFactory(
            opportunity_summary=summary_forecast,
            funding_instrument=FundingInstrument.COOPERATIVE_AGREEMENT,
            legacy_funding_instrument_id=3000,
        )
        # delete
        f.StagingTfundinstrForecastFactory(
            forecast=forecast_update, fi_id="O", fi_frcst_id=3001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingInstrumentFactory(
            opportunity_summary=summary_forecast,
            funding_instrument=FundingInstrument.OTHER,
            legacy_funding_instrument_id=3001,
        )

        ### Forecast Hist (deleted)
        # note that by default the factory creates 1-3 of each link value, those will automatically get deleted uneventfully by cascades
        f.OpportunitySummaryFactory(
            is_forecast=True, revision_number=1, opportunity=existing_opportunity
        )
        forecast_hist_delete = f.StagingTforecastHistFactory(
            revision_number=1, is_deleted=True, opportunity=opportunity
        )

        ### Synopsis (not modified as the update was already processed)
        summary_synopsis = f.OpportunitySummaryFactory(
            is_forecast=False, opportunity=existing_opportunity, no_link_values=True
        )
        synopsis_already_processed = f.StagingTsynopsisFactory(
            opportunity=opportunity, already_transformed=True
        )

        ## Synopsis applicant type (many duplicates)
        # insert
        f.StagingTapplicanttypesSynopsisFactory(synopsis=synopsis_already_processed, at_id="99")
        f.StagingTapplicanttypesSynopsisFactory(synopsis=synopsis_already_processed, at_id="99")
        f.StagingTapplicanttypesSynopsisFactory(synopsis=synopsis_already_processed, at_id="99")
        # update
        f.StagingTapplicanttypesSynopsisFactory(
            synopsis=synopsis_already_processed, at_id="07", at_syn_id=1000
        )
        f.StagingTapplicanttypesSynopsisFactory(
            synopsis=synopsis_already_processed, at_id="07", at_syn_id=11000
        )
        f.LinkOpportunitySummaryApplicantTypeFactory(
            opportunity_summary=summary_synopsis,
            applicant_type=ApplicantType.FEDERALLY_RECOGNIZED_NATIVE_AMERICAN_TRIBAL_GOVERNMENTS,
            legacy_applicant_type_id=1000,
        )
        # delete
        f.StagingTapplicanttypesSynopsisFactory(
            synopsis=synopsis_already_processed, at_id="21", at_syn_id=1001, is_deleted=True
        )
        # this will actually error because we don't yet handle these dupe deletes
        f.StagingTapplicanttypesSynopsisFactory(
            synopsis=synopsis_already_processed, at_id="21", at_syn_id=11001, is_deleted=True
        )
        f.LinkOpportunitySummaryApplicantTypeFactory(
            opportunity_summary=summary_synopsis,
            applicant_type=ApplicantType.INDIVIDUALS,
            legacy_applicant_type_id=1001,
        )

        ## Synopsis funding category
        # insert
        f.StagingTfundactcatSynopsisFactory(synopsis=synopsis_already_processed, fac_id="IIJ")
        f.StagingTfundactcatSynopsisFactory(synopsis=synopsis_already_processed, fac_id="IIJ")
        f.StagingTfundactcatSynopsisFactory(synopsis=synopsis_already_processed, fac_id="IIJ")
        f.StagingTfundactcatSynopsisFactory(synopsis=synopsis_already_processed, fac_id="IIJ")
        # update
        f.StagingTfundactcatSynopsisFactory(
            synopsis=synopsis_already_processed, fac_id="FN", fac_syn_id=2000
        )
        f.StagingTfundactcatSynopsisFactory(
            synopsis=synopsis_already_processed, fac_id="FN", fac_syn_id=20000
        )
        f.StagingTfundactcatSynopsisFactory(
            synopsis=synopsis_already_processed, fac_id="FN", fac_syn_id=21000
        )
        f.StagingTfundactcatSynopsisFactory(
            synopsis=synopsis_already_processed, fac_id="FN", fac_syn_id=22000
        )
        f.LinkOpportunitySummaryFundingCategoryFactory(
            opportunity_summary=summary_synopsis,
            funding_category=FundingCategory.FOOD_AND_NUTRITION,
            legacy_funding_category_id=2000,
        )
        # delete
        f.StagingTfundactcatSynopsisFactory(
            synopsis=synopsis_already_processed, fac_id="HL", fac_syn_id=2001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingCategoryFactory(
            opportunity_summary=summary_synopsis,
            funding_category=FundingCategory.HEALTH,
            legacy_funding_category_id=2001,
        )

        ## Synopsis funding instrument
        # insert
        f.StagingTfundinstrSynopsisFactory(synopsis=synopsis_already_processed, fi_id="PC")
        f.StagingTfundinstrSynopsisFactory(synopsis=synopsis_already_processed, fi_id="PC")
        f.StagingTfundinstrSynopsisFactory(synopsis=synopsis_already_processed, fi_id="PC")
        f.StagingTfundinstrSynopsisFactory(synopsis=synopsis_already_processed, fi_id="PC")
        f.StagingTfundinstrSynopsisFactory(synopsis=synopsis_already_processed, fi_id="PC")
        # update
        f.StagingTfundinstrSynopsisFactory(
            synopsis=synopsis_already_processed, fi_id="O", fi_syn_id=3000
        )
        f.StagingTfundinstrSynopsisFactory(
            synopsis=synopsis_already_processed, fi_id="O", fi_syn_id=30000
        )
        f.StagingTfundinstrSynopsisFactory(
            synopsis=synopsis_already_processed, fi_id="O", fi_syn_id=31000
        )
        f.LinkOpportunitySummaryFundingInstrumentFactory(
            opportunity_summary=summary_synopsis,
            funding_instrument=FundingInstrument.OTHER,
            legacy_funding_instrument_id=3000,
        )
        # delete
        f.StagingTfundinstrSynopsisFactory(
            synopsis=synopsis_already_processed, fi_id="G", fi_syn_id=3001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingInstrumentFactory(
            opportunity_summary=summary_synopsis,
            funding_instrument=FundingInstrument.GRANT,
            legacy_funding_instrument_id=3001,
        )

        ### Synopsis Hist (Insert - no nested values created)
        synopsis_hist_insert = f.StagingTsynopsisHistFactory(opportunity=opportunity)

        transform_oracle_data_task.run()

        updated_opportunity: Opportunity = (
            db_session.query(Opportunity)
            .filter(Opportunity.opportunity_id == opportunity.opportunity_id)
            .one_or_none()
        )

        assert updated_opportunity is not None
        validate_opportunity(db_session, opportunity)
        assert {
            al.opportunity_assistance_listing_id
            for al in updated_opportunity.opportunity_assistance_listings
        } == {cfda_insert.opp_cfda_id, cfda_update.opp_cfda_id}

        validate_summary_and_nested(
            db_session,
            forecast_update,
            [ApplicantType.COUNTY_GOVERNMENTS, ApplicantType.CITY_OR_TOWNSHIP_GOVERNMENTS],
            [FundingCategory.OPPORTUNITY_ZONE_BENEFITS, FundingCategory.NATURAL_RESOURCES],
            [FundingInstrument.GRANT, FundingInstrument.COOPERATIVE_AGREEMENT],
        )
        validate_summary_and_nested(
            db_session, forecast_hist_delete, [], [], [], expect_in_db=False
        )
        validate_summary_and_nested(
            db_session,
            synopsis_already_processed,
            [
                ApplicantType.UNRESTRICTED,
                ApplicantType.FEDERALLY_RECOGNIZED_NATIVE_AMERICAN_TRIBAL_GOVERNMENTS,
            ],
            [
                FundingCategory.INFRASTRUCTURE_INVESTMENT_AND_JOBS_ACT,
                FundingCategory.FOOD_AND_NUTRITION,
            ],
            [FundingInstrument.PROCUREMENT_CONTRACT, FundingInstrument.OTHER],
            expect_values_to_match=False,
        )
        validate_summary_and_nested(db_session, synopsis_hist_insert, [], [], [])

        validate_agency(db_session, parent_agency)
        validate_agency(db_session, subagency, deleted_fields={"ldapGp", "description"})

        assert {
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_PROCESSED: 43,
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_INSERTED: 8,
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_UPDATED: 11,
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_DELETED: 8,
            transform_oracle_data_task.Metrics.TOTAL_DUPLICATE_RECORDS_SKIPPED: 15,
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_ORPHANED: 0,
            transform_oracle_data_task.Metrics.TOTAL_DELETE_ORPHANS_SKIPPED: 1,
        }.items() <= transform_oracle_data_task.metrics.items()

    def test_delete_opportunity_with_deleted_children(self, db_session, transform_oracle_data_task):
        agency = setup_agency("AGENCYXYZ", create_existing=True)

        # We create an opportunity with a synopsis/forecast record, and various other child values
        # We then delete all of them at once. Deleting the opportunity will recursively delete the others
        # but we'll still have delete events for the others - this verfies how we handle that.

        existing_opportunity = f.OpportunityFactory(
            no_current_summary=True,
            opportunity_assistance_listings=[],
            agency_code="AGENCYXYZ",
            opportunity_attachments=[],
        )
        opportunity = f.StagingTopportunityFactory(
            opportunity_id=existing_opportunity.opportunity_id, cfdas=[], is_deleted=True
        )

        cfda = setup_cfda(create_existing=True, is_delete=True, opportunity=existing_opportunity)

        ### Forecast - has several children that will be deleted
        summary_forecast = f.OpportunitySummaryFactory(
            is_forecast=True, opportunity=existing_opportunity, no_link_values=True
        )
        forecast = f.StagingTforecastFactory(opportunity=opportunity, is_deleted=True)
        forecast_applicant_type = f.StagingTapplicanttypesForecastFactory(
            forecast=forecast, at_id="04", at_frcst_id=91001, is_deleted=True
        )
        f.LinkOpportunitySummaryApplicantTypeFactory(
            opportunity_summary=summary_forecast,
            applicant_type=ApplicantType.SPECIAL_DISTRICT_GOVERNMENTS,
            legacy_applicant_type_id=91001,
        )
        forecast_funding_category = f.StagingTfundactcatForecastFactory(
            forecast=forecast, fac_id="ST", fac_frcst_id=92001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingCategoryFactory(
            opportunity_summary=summary_forecast,
            funding_category=FundingCategory.SCIENCE_TECHNOLOGY_AND_OTHER_RESEARCH_AND_DEVELOPMENT,
            legacy_funding_category_id=92001,
        )
        forecast_funding_instrument = f.StagingTfundinstrForecastFactory(
            forecast=forecast, fi_id="O", fi_frcst_id=93001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingInstrumentFactory(
            opportunity_summary=summary_forecast,
            funding_instrument=FundingInstrument.OTHER,
            legacy_funding_instrument_id=93001,
        )

        ### Synopsis
        summary_synopsis = f.OpportunitySummaryFactory(
            is_forecast=False, opportunity=existing_opportunity, no_link_values=True
        )
        synopsis = f.StagingTsynopsisFactory(opportunity=opportunity, is_deleted=True)
        synopsis_applicant_type = f.StagingTapplicanttypesSynopsisFactory(
            synopsis=synopsis, at_id="21", at_syn_id=81001, is_deleted=True
        )
        f.LinkOpportunitySummaryApplicantTypeFactory(
            opportunity_summary=summary_synopsis,
            applicant_type=ApplicantType.INDIVIDUALS,
            legacy_applicant_type_id=81001,
        )
        synopsis_funding_category = f.StagingTfundactcatSynopsisFactory(
            synopsis=synopsis, fac_id="HL", fac_syn_id=82001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingCategoryFactory(
            opportunity_summary=summary_synopsis,
            funding_category=FundingCategory.HEALTH,
            legacy_funding_category_id=82001,
        )
        synopsis_funding_instrument = f.StagingTfundinstrSynopsisFactory(
            synopsis=synopsis, fi_id="G", fi_syn_id=83001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingInstrumentFactory(
            opportunity_summary=summary_synopsis,
            funding_instrument=FundingInstrument.GRANT,
            legacy_funding_instrument_id=83001,
        )
        # Need to put an expire all so SQLAlchemy doesn't read from its cache
        # otherwise when it does the recursive deletes, it doesn't see the later-added link table objects
        db_session.expire_all()

        transform_oracle_data_task.run_task()

        # verify everything is not in the DB
        validate_opportunity(db_session, opportunity, expect_in_db=False)
        validate_assistance_listing(db_session, cfda, expect_in_db=False)
        validate_opportunity_summary(db_session, forecast, expect_in_db=False)
        validate_opportunity_summary(db_session, synopsis, expect_in_db=False)

        validate_applicant_type(db_session, forecast_applicant_type, expect_in_db=False)
        validate_applicant_type(db_session, synopsis_applicant_type, expect_in_db=False)

        validate_funding_category(db_session, forecast_funding_category, expect_in_db=False)
        validate_funding_category(db_session, synopsis_funding_category, expect_in_db=False)

        validate_funding_instrument(db_session, forecast_funding_instrument, expect_in_db=False)
        validate_funding_instrument(db_session, synopsis_funding_instrument, expect_in_db=False)

        validate_agency(db_session, agency)

        assert {
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_PROCESSED: 11,
            # Despite processing 11 records, only the opportunity is actually deleted directly
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_DELETED: 1,
            f"opportunity.{transform_oracle_data_task.Metrics.TOTAL_RECORDS_DELETED}": 1,
            transform_oracle_data_task.Metrics.TOTAL_DELETE_ORPHANS_SKIPPED: 9,
        }.items() <= transform_oracle_data_task.metrics.items()

    def test_delete_opportunity_summary_with_deleted_children(
        self, db_session, transform_oracle_data_task
    ):
        # Similar to the above test, but we're leaving the opportunity alone and just deleting
        # an opportunity summary. Should be the same thing, just on a smaller scale.
        existing_opportunity = f.OpportunityFactory(
            no_current_summary=True, opportunity_assistance_listings=[]
        )
        opportunity = f.StagingTopportunityFactory(
            opportunity_id=existing_opportunity.opportunity_id, cfdas=[], already_transformed=True
        )

        summary_synopsis = f.OpportunitySummaryFactory(
            is_forecast=False, opportunity=existing_opportunity, no_link_values=True
        )
        synopsis = f.StagingTsynopsisFactory(opportunity=opportunity, is_deleted=True)
        synopsis_applicant_type = f.StagingTapplicanttypesSynopsisFactory(
            synopsis=synopsis, at_id="21", at_syn_id=71001, is_deleted=True
        )
        f.LinkOpportunitySummaryApplicantTypeFactory(
            opportunity_summary=summary_synopsis,
            applicant_type=ApplicantType.INDIVIDUALS,
            legacy_applicant_type_id=71001,
        )
        synopsis_funding_category = f.StagingTfundactcatSynopsisFactory(
            synopsis=synopsis, fac_id="HL", fac_syn_id=72001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingCategoryFactory(
            opportunity_summary=summary_synopsis,
            funding_category=FundingCategory.HEALTH,
            legacy_funding_category_id=72001,
        )
        synopsis_funding_instrument = f.StagingTfundinstrSynopsisFactory(
            synopsis=synopsis, fi_id="G", fi_syn_id=73001, is_deleted=True
        )
        f.LinkOpportunitySummaryFundingInstrumentFactory(
            opportunity_summary=summary_synopsis,
            funding_instrument=FundingInstrument.GRANT,
            legacy_funding_instrument_id=73001,
        )
        # Need to put an expire all so SQLAlchemy doesn't read from its cache
        # otherwise when it does the recursive deletes, it doesn't see the later-added link table objects
        db_session.expire_all()

        transform_oracle_data_task.run_task()

        # verify everything is not in the DB
        validate_opportunity(
            db_session, opportunity, expect_in_db=True, expect_values_to_match=False
        )
        validate_opportunity_summary(db_session, synopsis, expect_in_db=False)
        validate_applicant_type(db_session, synopsis_applicant_type, expect_in_db=False)
        validate_funding_category(db_session, synopsis_funding_category, expect_in_db=False)
        validate_funding_instrument(db_session, synopsis_funding_instrument, expect_in_db=False)

        assert {
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_PROCESSED: 4,
            # Despite processing 4 records, only the opportunity_summary is actually deleted directly
            transform_oracle_data_task.Metrics.TOTAL_RECORDS_DELETED: 1,
            f"opportunity_summary.{transform_oracle_data_task.Metrics.TOTAL_RECORDS_DELETED}": 1,
            transform_oracle_data_task.Metrics.TOTAL_DELETE_ORPHANS_SKIPPED: 3,
        }.items() <= transform_oracle_data_task.metrics.items()
