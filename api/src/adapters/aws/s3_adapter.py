import boto3
import botocore.client
import botocore.config
from pydantic import Field

from src.util.env_config import PydanticBaseEnvConfig


class S3Config(PydanticBaseEnvConfig):
    # We should generally not need to set this except
    # locally to use localstack
    s3_endpoint_url: str | None = None
    presigned_s3_duration: int = 7200  # 2 hours in seconds

    ### S3 Buckets
    # note that we default these to None
    # so that we don't need to set all of these for every
    # process that uses S3

    # Note these env vars get set as "s3://..."
    public_files_bucket_path: str = Field(alias="PUBLIC_FILES_BUCKET")
    draft_files_bucket_path: str = Field(alias="DRAFT_FILES_BUCKET")


def get_s3_client(
    s3_config: S3Config | None = None,
    session: boto3.Session | None = None,
    boto_config: botocore.config.Config | None = None,
) -> botocore.client.BaseClient:
    if s3_config is None:
        s3_config = S3Config()

    params = {}
    if s3_config.s3_endpoint_url is not None:
        params["endpoint_url"] = s3_config.s3_endpoint_url

    if boto_config is None:
        boto_config = botocore.config.Config(signature_version="s3v4")

    params["config"] = boto_config

    if session is not None:
        return session.client("s3", **params)

    return boto3.client("s3", **params)
