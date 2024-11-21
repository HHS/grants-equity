from src.api.schemas.extension import Schema, fields
from src.api.schemas.response_schema import AbstractResponseSchema, FileResponseSchema
from src.constants.lookup_constants import ExtractType
from src.pagination.pagination_schema import generate_pagination_schema


class DateRangeSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)


class ExtractMetadataFilterV1Schema(Schema):
    extract_type = fields.Enum(
        ExtractType,
        allow_none=True,
        metadata={
            "description": "The type of extract to filter by",
            "example": "opportunities_json",
        },
    )
    created_at = fields.Nested(DateRangeSchema, required=False)


class ExtractMetadataRequestSchema(AbstractResponseSchema):
    filters = fields.Nested(ExtractMetadataFilterV1Schema())
    pagination = fields.Nested(
        generate_pagination_schema(
            "ExtractMetadataPaginationV1Schema",
            ["created_at"],
        ),
        required=True,
    )


class ExtractMetadataResponseSchema(FileResponseSchema):
    extract_metadata_id = fields.Integer(
        metadata={"description": "The ID of the extract metadata", "example": 1}
    )
    extract_type = fields.String(
        metadata={"description": "The type of extract", "example": "opportunity_data_extract"}
    )


class ExtractMetadataListResponseSchema(AbstractResponseSchema):
    data = fields.List(
        fields.Nested(ExtractMetadataResponseSchema),
        metadata={"description": "A list of extract metadata records"},
    )
