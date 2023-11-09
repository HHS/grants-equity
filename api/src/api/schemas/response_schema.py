
from src.pagination.pagination_schema import PaginationInfoSchema
from src.api.schemas.extension import fields, Schema


class ValidationIssueSchema(Schema):
    type = fields.String(metadata={"description": "The type of error"})
    message = fields.String(metadata={"description": "The message to return"})
    field = fields.String(metadata={"description": "The field that failed"})
    value = fields.String(metadata={"description": "The value that failed"})


class BaseResponseSchema(Schema):
    message = fields.String(metadata={"description": "The message to return"})
    data = fields.MixinField(metadata={"description": "The REST resource object"}, dump_default={})
    status_code = fields.Integer(metadata={"description": "The HTTP status code"}, dump_default=200)

    pagination_info = fields.Nested(
        PaginationInfoSchema(),
        metadata={"description": "The pagination information for paginated endpoints"},
    )

class ErrorResponseSchema(BaseResponseSchema):
    errors = fields.List(fields.Nested(ValidationIssueSchema()), dump_default=[])

class ResponseSchema(BaseResponseSchema):
    warnings = fields.List(fields.Nested(ValidationIssueSchema()), dump_default=[])