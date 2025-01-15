import logging

import boto3
import botocore.client
import botocore.exceptions

import src.logging
from src.adapters.aws import S3Config, get_s3_client
from src.util import file_util
from src.util.local import error_if_not_local

logger = logging.getLogger(__name__)


def does_s3_bucket_exist(s3_client: botocore.client.BaseClient, bucket_name: str) -> bool:
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except botocore.exceptions.ClientError as e:
        # We'll assume that if the error code is a 404 that means
        # it could not find the bucket and thus it needs to be created
        # as there are not more specific errors than this available
        error_code = e.response.get("Error", {}).get("Code")
        if error_code != "404":
            raise e

    return False


def create_bucket_if_not_exists(s3_client: botocore.client.BaseClient, bucket_name: str) -> None:
    if not does_s3_bucket_exist(s3_client, bucket_name):
        logger.info("Creating S3 bucket %s", bucket_name)
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        logger.info("S3 bucket %s already exists - skipping creation", bucket_name)


def setup_s3() -> None:
    s3_config = S3Config()
    # This is only used locally - to avoid any accidental running of commands here
    # against a real AWS account (ie. you've authed in your local terminal where you're running this)
    # we'll override the access keys explicitly.
    s3_client = get_s3_client(
        s3_config, boto3.Session(aws_access_key_id="NO_CREDS", aws_secret_access_key="NO_CREDS")
    )

    create_bucket_if_not_exists(
        s3_client, file_util.get_s3_bucket(s3_config.public_files_bucket_path)
    )
    create_bucket_if_not_exists(
        s3_client, file_util.get_s3_bucket(s3_config.draft_files_bucket_path)
    )


def main() -> None:
    with src.logging.init("setup_localstack"):
        error_if_not_local()
        setup_s3()


if __name__ == "__main__":
    main()
