import re

from src.adapters.aws import S3Config
from src.db.models.opportunity_models import Opportunity
from src.util import file_util


def get_s3_attachment_path(
    file_name: str, opportunity_attachment_id: int, opportunity: Opportunity, s3_config: S3Config
) -> str:
    """Construct a path to the attachments on s3

    Will be formatted like:

        s3://<bucket>/opportunities/<opportunity_id>/attachments/<attachment_id>/<file_name>

    Note that we store the files under a "folder" with the attachment ID as
    the legacy system doesn't guarantee file names are unique within an opportunity.
    """

    base_path = (
        s3_config.draft_files_bucket_path
        if opportunity.is_draft
        else s3_config.public_files_bucket_path
    )

    return file_util.join(
        base_path,
        "opportunities",
        str(opportunity.opportunity_id),
        "attachments",
        str(opportunity_attachment_id),
        file_name,
    )


def adjust_legacy_file_name(existing_file_name: str) -> str:
    """Correct the file names to remove any characters problematic for URL/s3 processing.

    We only keep the following characters:
    * A-Z
    * a-z
    * 0-9
    * _
    * -
    * ~
    * .

    Whitespace will be replaced with underscores.

    All other characters will be removed.
    """

    # Replace one-or-more whitespace with a single underscore
    file_name = re.sub(r"\s+", "_", existing_file_name)

    # Remove all non-accepted characters
    file_name = re.sub(r"[^a-zA-Z0-9_.\-~]", "", file_name)

    return file_name
