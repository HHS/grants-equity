import boto3

from src.util.env_config import PydanticBaseEnvConfig


class BaseAwsConfig(PydanticBaseEnvConfig):
    is_local_aws: bool = False


_base_aws_config: BaseAwsConfig | None = None


def get_base_aws_config() -> BaseAwsConfig:
    global _base_aws_config
    if _base_aws_config is None:
        _base_aws_config = BaseAwsConfig()

    return _base_aws_config


def is_local_aws() -> bool:
    """Whether we are running against local AWS which affects the credentials we use (forces them to be not real)"""
    return get_base_aws_config().is_local_aws


def get_boto_session() -> boto3.Session:
    if is_local_aws():
        # Locally, set fake creds in a region we don't actually use so we can't hit actual AWS resources
        return boto3.Session(
            aws_access_key_id="NO_CREDS", aws_secret_access_key="NO_CREDS", region_name="us-west-2"
        )

    return boto3.Session()
