import pytest

import src.data_migration.transformation.transform_constants as transform_constants
from src.data_migration.transformation.subtask.transform_opportunity import TransformOpportunity
from src.services.opportunity_attachments import attachment_util
from src.util import file_util
from tests.src.data_migration.transformation.conftest import (
    BaseTransformTestClass,
    setup_opportunity,
    validate_opportunity,
)
from tests.src.db.models.factories import OpportunityAttachmentFactory, OpportunityFactory


class TestTransformOpportunity(BaseTransformTestClass):
    @pytest.fixture()
    def transform_opportunity(self, transform_oracle_data_task, truncate_staging_tables, s3_config):
        return TransformOpportunity(transform_oracle_data_task, s3_config)

    def test_process_opportunities(self, db_session, transform_opportunity):
        ordinary_delete = setup_opportunity(
            create_existing=True, is_delete=True, all_fields_null=True
        )
        ordinary_delete2 = setup_opportunity(
            create_existing=True, is_delete=True, all_fields_null=False
        )
        delete_but_current_missing = setup_opportunity(create_existing=False, is_delete=True)

        basic_insert = setup_opportunity(create_existing=False)
        basic_insert2 = setup_opportunity(create_existing=False, all_fields_null=True)
        basic_insert3 = setup_opportunity(create_existing=False)

        basic_update = setup_opportunity(
            create_existing=True,
        )
        basic_update2 = setup_opportunity(create_existing=True, all_fields_null=True)
        basic_update3 = setup_opportunity(create_existing=True, all_fields_null=True)
        basic_update4 = setup_opportunity(create_existing=True)

        # Something else deleted it
        already_processed_insert = setup_opportunity(
            create_existing=False, is_already_processed=True
        )
        already_processed_update = setup_opportunity(
            create_existing=True, is_already_processed=True
        )

        insert_that_will_fail = setup_opportunity(
            create_existing=False, source_values={"oppcategory": "X"}
        )

        transform_opportunity.run_subtask()

        validate_opportunity(db_session, ordinary_delete, expect_in_db=False)
        validate_opportunity(db_session, ordinary_delete2, expect_in_db=False)
        validate_opportunity(db_session, delete_but_current_missing, expect_in_db=False)

        validate_opportunity(db_session, basic_insert)
        validate_opportunity(db_session, basic_insert2)
        validate_opportunity(db_session, basic_insert3)

        validate_opportunity(db_session, basic_update)
        validate_opportunity(db_session, basic_update2)
        validate_opportunity(db_session, basic_update3)
        validate_opportunity(db_session, basic_update4)

        validate_opportunity(db_session, already_processed_insert, expect_in_db=False)
        validate_opportunity(db_session, already_processed_update, expect_values_to_match=False)

        validate_opportunity(db_session, insert_that_will_fail, expect_in_db=False)

        metrics = transform_opportunity.metrics
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_PROCESSED] == 11
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_DELETED] == 2
        # Note this insert counts the case where the category fails
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_INSERTED] == 3
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_UPDATED] == 4
        assert metrics[transform_constants.Metrics.TOTAL_ERROR_COUNT] == 1
        assert metrics[transform_constants.Metrics.TOTAL_DELETE_ORPHANS_SKIPPED] == 1

        # Rerunning does mostly nothing, it will attempt to re-process the one that errored
        # but otherwise won't find anything else
        db_session.commit()  # commit to end any existing transactions as run_subtask starts a new one
        transform_opportunity.run_subtask()
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_PROCESSED] == 12
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_DELETED] == 2
        # Note this insert counts the case where the category fails
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_INSERTED] == 3
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_UPDATED] == 4
        assert metrics[transform_constants.Metrics.TOTAL_ERROR_COUNT] == 2
        assert metrics[transform_constants.Metrics.TOTAL_DELETE_ORPHANS_SKIPPED] == 1

    def test_process_opportunity_invalid_category(self, db_session, transform_opportunity):
        # This will error in the transform as that isn't a category we have configured
        insert_that_will_fail = setup_opportunity(
            create_existing=False, source_values={"oppcategory": "X"}
        )

        with pytest.raises(ValueError, match="Unrecognized opportunity category"):
            transform_opportunity.process_opportunity(insert_that_will_fail, None)

        validate_opportunity(db_session, insert_that_will_fail, expect_in_db=False)

    def test_process_opportunity_delete_with_attachments(
        self, db_session, transform_opportunity, s3_config
    ):

        source_opportunity = setup_opportunity(create_existing=False, is_delete=True)

        target_opportunity = OpportunityFactory.create(
            opportunity_id=source_opportunity.opportunity_id, opportunity_attachments=[]
        )

        attachments = []
        for i in range(10):
            s3_path = attachment_util.get_s3_attachment_path(
                f"my_file{i}.txt", i, target_opportunity, s3_config
            )

            with file_util.open_stream(s3_path, "w") as outfile:
                outfile.write(f"This is the {i}th file")

            attachment = OpportunityAttachmentFactory.create(
                opportunity=target_opportunity, file_location=s3_path
            )
            attachments.append(attachment)

        transform_opportunity.process_opportunity(source_opportunity, target_opportunity)

        validate_opportunity(db_session, source_opportunity, expect_in_db=False)

        # Verify all of the files were deleted
        for attachment in attachments:
            assert file_util.file_exists(attachment.file_location) is False

    def test_process_opportunity_update_to_non_draft_with_attachments(
        self, db_session, transform_opportunity, s3_config
    ):

        source_opportunity = setup_opportunity(
            create_existing=False, source_values={"is_draft": "N"}
        )

        target_opportunity = OpportunityFactory.create(
            opportunity_id=source_opportunity.opportunity_id,
            is_draft=True,
            opportunity_attachments=[],
        )

        attachments = []
        for i in range(10):
            s3_path = attachment_util.get_s3_attachment_path(
                f"my_file{i}.txt", i, target_opportunity, s3_config
            )
            assert s3_path.startswith(s3_config.draft_files_bucket_path) is True

            with file_util.open_stream(s3_path, "w") as outfile:
                outfile.write(f"This is the {i}th file")

            attachment = OpportunityAttachmentFactory.create(
                opportunity=target_opportunity, file_location=s3_path
            )
            attachments.append(attachment)

        transform_opportunity.process_opportunity(source_opportunity, target_opportunity)

        validate_opportunity(db_session, source_opportunity)

        # Verify all of the files were moved to the public bucket
        for attachment in attachments:
            assert attachment.file_location.startswith(s3_config.public_files_bucket_path) is True
            assert file_util.file_exists(attachment.file_location) is True
