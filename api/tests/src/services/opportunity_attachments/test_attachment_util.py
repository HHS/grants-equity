import pytest

from src.adapters.aws import S3Config
from src.services.opportunity_attachments import attachment_util
from tests.src.db.models.factories import OpportunityFactory


@pytest.mark.parametrize(
    "is_draft,opportunity_id,attachment_id,file_name,expected_path",
    [
        (
            False,
            123,
            456,
            "my_file.txt",
            "s3://test-public-bucket/opportunities/123/attachments/456/my_file.txt",
        ),
        (
            True,
            12345,
            45678,
            "example.pdf",
            "s3://test-draft-bucket/opportunities/12345/attachments/45678/example.pdf",
        ),
        (
            False,
            1,
            1,
            "example.docx",
            "s3://test-public-bucket/opportunities/1/attachments/1/example.docx",
        ),
    ],
)
def test_get_s3_attachment_path(is_draft, opportunity_id, attachment_id, file_name, expected_path):
    config = S3Config(
        PUBLIC_FILES_BUCKET="s3://test-public-bucket", DRAFT_FILES_BUCKET="s3://test-draft-bucket"
    )

    opp = OpportunityFactory.build(opportunity_id=opportunity_id, is_draft=is_draft)

    assert (
        attachment_util.get_s3_attachment_path(file_name, attachment_id, opp, config)
        == expected_path
    )


@pytest.mark.parametrize(
    "existing_file_name,expected_file_name",
    [
        ("abc.txt", "abc.txt"),
        ("my file.pdf", "my_file.pdf"),
        ("a.b.c.wav", "a.b.c.wav"),
        ("my-valid~file_is.good.txt", "my-valid~file_is.good.txt"),
        ("!@#$%^&*()'\",/;'myfile.txt", "myfile.txt"),
        ("0123456789 |[]", "0123456789_"),
        ("many       spaces.txt", "many_spaces.txt"),
        ("other\t\twhitespace\n\nremoved.txt", "other_whitespace_removed.txt"),
    ],
)
def test_adjust_legacy_file_name(existing_file_name, expected_file_name):
    assert attachment_util.adjust_legacy_file_name(existing_file_name) == expected_file_name
