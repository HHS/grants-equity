import logging

import src.adapters.db as db
import src.adapters.db.flask_db as flask_db
import src.api.extracts_v1.extract_schema as extract_schema
import src.api.response as response
from src.api.extracts_v1.extract_blueprint import extract_blueprint
from src.auth.api_key_auth import api_key_auth
from src.logging.flask_logger import add_extra_data_to_current_request_logs
from src.services.extracts_v1.get_extracts import ExtractListParams, get_extracts

logger = logging.getLogger(__name__)

examples = {
    "example1": {
        "summary": "No filters",
        "value": {
            "pagination": {
                "sort_order": [
                    {
                        "order_by": "created_at",
                        "sort_direction": "descending",
                    }
                ],
                "page_offset": 1,
                "page_size": 25,
            },
        },
    },
}


@extract_blueprint.post("/extracts")
@extract_blueprint.input(
    extract_schema.ExtractMetadataRequestSchema,
    arg_name="raw_list_params",
    examples=examples,
)
@extract_blueprint.output(extract_schema.ExtractMetadataListResponseSchema)
@extract_blueprint.auth_required(api_key_auth)
@flask_db.with_db_session()
def extract_metadata_get(db_session: db.Session, raw_list_params: dict) -> response.ApiResponse:
    list_params: ExtractListParams = ExtractListParams.model_validate(raw_list_params)

    # Call service with params to get results
    with db_session.begin():
        results, pagination_info = get_extracts(db_session, list_params)

    add_extra_data_to_current_request_logs(
        {
            "response.pagination.total_pages": pagination_info.total_pages,
            "response.pagination.total_records": pagination_info.total_records,
        }
    )
    logger.info("Successfully fetched extracts")

    # Serialize results
    return response.ApiResponse(message="Success", data=results, pagination_info=pagination_info)
