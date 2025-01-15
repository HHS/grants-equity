import pytest

import tests.src.db.models.factories as f
from src.data_migration.transformation import transform_constants
from src.data_migration.transformation.subtask.transform_opportunity_attachment import (
    TransformOpportunityAttachment,
)
from src.services.opportunity_attachments import attachment_util
from src.util import file_util
from tests.src.data_migration.transformation.conftest import (
    BaseTransformTestClass,
    setup_opportunity_attachment,
    validate_opportunity_attachment,
)


class TestTransformOpportunitySummary(BaseTransformTestClass):

    @pytest.fixture()
    def transform_opportunity_attachment(self, transform_oracle_data_task, s3_config):
        return TransformOpportunityAttachment(transform_oracle_data_task, s3_config)

    def test_transform_opportunity_attachment(
        self, db_session, transform_opportunity_attachment, s3_config
    ):

        opportunity1 = f.OpportunityFactory.create(opportunity_attachments=[])

        insert1 = setup_opportunity_attachment(
            create_existing=False, opportunity=opportunity1, config=s3_config
        )
        insert2 = setup_opportunity_attachment(
            create_existing=False, opportunity=opportunity1, config=s3_config
        )

        update1 = setup_opportunity_attachment(
            create_existing=True, opportunity=opportunity1, config=s3_config
        )
        update2 = setup_opportunity_attachment(
            create_existing=True, opportunity=opportunity1, config=s3_config
        )

        delete1 = setup_opportunity_attachment(
            create_existing=True,
            is_delete=True,
            opportunity=opportunity1,
            config=s3_config,
        )

        opportunity2 = f.OpportunityFactory.create(opportunity_attachments=[])

        insert3 = setup_opportunity_attachment(
            create_existing=False, opportunity=opportunity2, config=s3_config
        )
        update3 = setup_opportunity_attachment(
            create_existing=True, opportunity=opportunity2, config=s3_config
        )
        delete2 = setup_opportunity_attachment(
            create_existing=True,
            is_delete=True,
            opportunity=opportunity2,
            config=s3_config,
        )

        already_processed_insert = setup_opportunity_attachment(
            create_existing=False,
            opportunity=opportunity2,
            is_already_processed=True,
            config=s3_config,
        )
        already_processed_update = setup_opportunity_attachment(
            create_existing=True,
            opportunity=opportunity2,
            is_already_processed=True,
            config=s3_config,
        )

        delete_but_current_missing = setup_opportunity_attachment(
            create_existing=False,
            opportunity=opportunity2,
            is_delete=True,
            config=s3_config,
        )

        # Draft opportunity
        opportunity3 = f.OpportunityFactory.create(is_draft=True, opportunity_attachments=[])
        insert4 = setup_opportunity_attachment(
            create_existing=False, opportunity=opportunity3, config=s3_config
        )
        update4 = setup_opportunity_attachment(
            create_existing=True, opportunity=opportunity3, config=s3_config
        )
        delete3 = setup_opportunity_attachment(
            create_existing=True,
            is_delete=True,
            opportunity=opportunity3,
            config=s3_config,
        )

        transform_opportunity_attachment.run_subtask()

        validate_opportunity_attachment(db_session, insert1)
        validate_opportunity_attachment(db_session, insert2)
        validate_opportunity_attachment(db_session, insert3)
        validate_opportunity_attachment(db_session, insert4)

        validate_opportunity_attachment(db_session, update1)
        validate_opportunity_attachment(db_session, update2)
        validate_opportunity_attachment(db_session, update3)
        validate_opportunity_attachment(db_session, update4)

        validate_opportunity_attachment(db_session, delete1, expect_in_db=False)
        validate_opportunity_attachment(db_session, delete2, expect_in_db=False)
        validate_opportunity_attachment(db_session, delete3, expect_in_db=False)

        validate_opportunity_attachment(db_session, already_processed_insert, expect_in_db=False)
        validate_opportunity_attachment(
            db_session, already_processed_update, expect_values_to_match=False
        )

        validate_opportunity_attachment(db_session, delete_but_current_missing, expect_in_db=False)

        metrics = transform_opportunity_attachment.metrics
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_PROCESSED] == 12
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_DELETED] == 3
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_INSERTED] == 4
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_UPDATED] == 4
        assert metrics[transform_constants.Metrics.TOTAL_DELETE_ORPHANS_SKIPPED] == 1

        db_session.commit()  # commit to end any existing transactions as run_subtask starts a new one
        transform_opportunity_attachment.run_subtask()
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_PROCESSED] == 12
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_DELETED] == 3
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_INSERTED] == 4
        assert metrics[transform_constants.Metrics.TOTAL_RECORDS_UPDATED] == 4
        assert metrics[transform_constants.Metrics.TOTAL_DELETE_ORPHANS_SKIPPED] == 1

    def test_transform_opportunity_attachment_delete_but_current_missing(
        self, db_session, transform_opportunity_attachment, s3_config
    ):
        opportunity = f.OpportunityFactory.create(opportunity_attachments=[])
        delete_but_current_missing = setup_opportunity_attachment(
            create_existing=False,
            opportunity=opportunity,
            is_delete=True,
            config=s3_config,
        )

        transform_opportunity_attachment.process_opportunity_attachment(
            delete_but_current_missing, None, opportunity
        )

        validate_opportunity_attachment(db_session, delete_but_current_missing, expect_in_db=False)
        assert delete_but_current_missing.transformed_at is not None
        assert delete_but_current_missing.transformation_notes == "orphaned_delete_record"

    def test_transform_opportunity_attachment_no_opportunity(
        self, db_session, transform_opportunity_attachment, s3_config
    ):
        opportunity = f.OpportunityFactory.create(opportunity_attachments=[])
        insert = setup_opportunity_attachment(
            create_existing=False, opportunity=opportunity, config=s3_config
        )

        # Don't pass the opportunity in - as if it wasn't found
        with pytest.raises(
            ValueError,
            match="Opportunity attachment cannot be processed as the opportunity for it does not exist",
        ):
            transform_opportunity_attachment.process_opportunity_attachment(insert, None, None)

        assert insert.transformed_at is None

    def test_transform_opportunity_attachment_update_file_renamed(
        self, db_session, transform_opportunity_attachment, s3_config
    ):
        opportunity = f.OpportunityFactory.create(is_draft=False, opportunity_attachments=[])
        update = setup_opportunity_attachment(
            # Don't create the existing, we'll do that below
            create_existing=False,
            opportunity=opportunity,
            config=s3_config,
        )

        old_s3_path = attachment_util.get_s3_attachment_path(
            "old_file_name.txt", update.syn_att_id, opportunity, s3_config
        )

        with file_util.open_stream(old_s3_path, "w") as outfile:
            outfile.write(f.fake.sentence(25))

        target_attachment = f.OpportunityAttachmentFactory.create(
            attachment_id=update.syn_att_id,
            opportunity=opportunity,
            file_location=old_s3_path,
            file_name="old_file_name.txt",
        )

        transform_opportunity_attachment.process_opportunity_attachment(
            update, target_attachment, opportunity
        )

        validate_opportunity_attachment(db_session, update)

        # Verify the old file name was deleted
        assert file_util.file_exists(old_s3_path) is False

    def test_transform_opportunity_attachment_delete_file_missing_on_s3(
        self, db_session, transform_opportunity_attachment, s3_config
    ):
        opportunity = f.OpportunityFactory.create(opportunity_attachments=[])

        synopsis_attachment = f.StagingTsynopsisAttachmentFactory.create(
            opportunity=None,
            opportunity_id=opportunity.opportunity_id,
            is_deleted=True,
        )

        # Make a realistic path, but don't actually create the file
        s3_path = attachment_util.get_s3_attachment_path(
            synopsis_attachment.file_name, synopsis_attachment.syn_att_id, opportunity, s3_config
        )

        target_attachment = f.OpportunityAttachmentFactory.create(
            attachment_id=synopsis_attachment.syn_att_id,
            opportunity=opportunity,
            file_location=s3_path,
        )

        # This won't error, s3 delete object doesn't error if the object doesn't exist
        transform_opportunity_attachment.process_opportunity_attachment(
            synopsis_attachment, target_attachment, opportunity
        )

        validate_opportunity_attachment(db_session, synopsis_attachment, expect_in_db=False)
