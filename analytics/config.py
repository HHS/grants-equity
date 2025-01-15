"""Loads configuration variables from settings files

"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# reads environment variables from .env files defaulting to "local.env"
class PydanticBaseEnvConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file="%s.env" % os.getenv("ENVIRONMENT", "local"), extra="allow")

class DBSettings(PydanticBaseEnvConfig):
     db_host: str = Field(alias="DB_HOST")
     name: str = Field(alias="DB_NAME")
     port: int = Field(5432,alias="DB_PORT")
     user: str = Field (alias="DB_USER")
     password: Optional[str] = Field(None, alias="DB_PASSWORD")
     ssl_mode: str = Field("require", alias="DB_SSL_MODE")
     db_schema: str = Field ("app", alias="DB_SCHEMA")
     slack_bot_token: str = Field(alias="ANALYTICS_SLACK_BOT_TOKEN")
     github_token: str = Field(alias="GH_TOKEN")
     reporting_channel_id: str = Field(alias="ANALYTICS_REPORTING_CHANNEL_ID")
     aws_region: Optional[str] = Field(None, alias="AWS_REGION")
     local_env: bool = True if os.getenv("ENVIRONMENT", "local") == "local" else False

def get_db_settings() -> DBSettings:
     return DBSettings()
