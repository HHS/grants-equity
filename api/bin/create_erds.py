# Generate database schema diagrams from our SQLAlchemy models
import inspect
import logging
import pathlib
import pdb
import subprocess
from typing import Any

from eralchemy import render_er
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_schemadisplay import create_uml_graph

import src.db.models.staging.forecast as staging_forecast_models
import src.db.models.staging.opportunity as staging_opportunity_models
import src.db.models.staging.synopsis as staging_synopsis_models
import src.logging
from src.constants.schema import Schemas
from src.db.models import agency_models, opportunity_models
from src.db.models.base import ApiSchemaTable, Base
from src.db.models.staging.staging_base import StagingBase
from src.db.models.transfer import topportunity_models

logger = logging.getLogger(__name__)

# Construct the path to the folder this file is within
# This gets an absolute path so that where you run the script from won't matter
# and should always resolve to the app/erds folder
ERD_FOLDER = pathlib.Path(__file__).parent.resolve()

# If we want to generate separate files for more specific groups, we can set that up here
STAGING_BASE_METADATA = StagingBase.metadata
API_BASE_METADATA = ApiSchemaTable.metadata


# Any modules you add above, merge together for the full schema to be generated
ALL_METADATA = [StagingBase.metadata, ApiSchemaTable.metadata]


def _combine_metadata(metadata: list) -> MetaData:

    combined_metadata = MetaData()
    for m in metadata:
        for table in m.sorted_tables:
            table.to_metadata(combined_metadata)
    return combined_metadata


def create_erds(metadata: Any, file_name: str) -> None:
    logger.info("Generating ERD diagrams for %s", file_name)

    if isinstance(metadata, list):
        metadata = _combine_metadata(metadata)

    png_file_path = str(ERD_FOLDER / f"{file_name}.png")
    render_er(metadata, png_file_path)


def main() -> None:
    with src.logging.init(__package__):
        logger.info("Generating ERD diagrams")

        create_erds(STAGING_BASE_METADATA, "staging-schema")
        create_erds(API_BASE_METADATA, "api-schema")
        create_erds(ALL_METADATA, "full-schema")
