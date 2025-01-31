from typing import Type

from marshmallow import pre_load

from src.api.schemas.extension import Schema, fields, validators
from src.pagination.pagination_models import SortDirection


class BasePaginationSchema(Schema):

    @pre_load
    def before_load(self, item: dict, many: bool, **kwargs: dict) -> dict:
        # If sort_order is used, don't change anything
        # We'll assume they've migrated properly
        if item.get("sort_order") is not None:
            return item

        # While we wait for the frontend to start using the new multi-sort, automatically
        # setup a monosort for them from the old fields.
        if item.get("order_by") is not None and item.get("sort_direction") is not None:
            item["sort_order"] = [
                {"order_by": item["order_by"], "sort_direction": item["sort_direction"]}
            ]
        return item


def generate_pagination_schema(
    cls_name: str,
    order_by_fields: list[str],
    max_page_size: int = 5000,
    default_sort_order: list[dict] | None = None,
) -> Type[Schema]:
    """
    Generate a schema that describes the pagination for a pagination endpoint.

        cls_name will be what the model is named internally by Marshmallow and what OpenAPI shows.
        order_by_fields can be a list of fields that the endpoint allows you to sort the response by

    This is functionally equivalent to specifying your own class like so:

        class MyPaginationSchema(Schema):
            order_by = fields.String(
                validate=[validators.OneOf(["id","created_at","updated_at"])],
                required=True,
                metadata={"description": "The field to sort the response by"}
            )
            sort_direction = fields.Enum(
                SortDirection,
                required=True,
                metadata={"description": "Whether to sort the response ascending or descending"},
            )
            page_size = fields.Integer(
                required=True,
                validate=[validators.Range(min=1)],
                metadata={"description": "The size of the page to fetch", "example": 25},
            )
            page_offset = fields.Integer(
                required=True,
                validate=[validators.Range(min=1)],
                metadata={"description": "The page number to fetch, starts counting from 1", "example": 1},
            )

    """

    sort_order_schema = Schema.from_dict(
        {
            "order_by": fields.String(
                validate=[validators.OneOf(order_by_fields)],
                required=True,
                metadata={"description": "The field to sort the response by"},
            ),
            "sort_direction": fields.Enum(
                SortDirection,
                required=True,
                metadata={"description": "Whether to sort the response ascending or descending"},
            ),
        },
        name=f"SortOrder{cls_name}",
    )

    additional_sort_order_params: dict = {}
    if default_sort_order is not None:
        additional_sort_order_params["load_default"] = default_sort_order
    else:
        additional_sort_order_params["required"] = True

    pagination_schema_fields = {
        "sort_order": fields.List(
            fields.Nested(sort_order_schema()),
            metadata={"description": "The list of sorting rules"},
            validate=[validators.Length(min=1, max=5)],
            **additional_sort_order_params,
        ),
        "page_size": fields.Integer(
            required=True,
            validate=[validators.Range(min=1, max=max_page_size)],
            metadata={"description": "The size of the page to fetch", "example": 25},
        ),
        "page_offset": fields.Integer(
            required=True,
            validate=[validators.Range(min=1)],
            metadata={
                "description": "The page number to fetch, starts counting from 1",
                "example": 1,
            },
        ),
    }
    return BasePaginationSchema.from_dict(pagination_schema_fields, name=cls_name)  # type: ignore


class SortOrderSchema(Schema):
    order_by = fields.String(
        metadata={"description": "The field that the records were sorted by", "example": "id"}
    )
    sort_direction = fields.Enum(
        SortDirection,
        metadata={"description": "The direction the records are sorted"},
    )


class PaginationInfoSchema(Schema):
    # This is part of the response schema to provide all pagination information back to a user

    page_offset = fields.Integer(
        metadata={"description": "The page number that was fetched", "example": 1}
    )
    page_size = fields.Integer(
        metadata={"description": "The size of the page fetched", "example": 25}
    )
    total_records = fields.Integer(
        metadata={"description": "The total number of records fetchable", "example": 42}
    )
    total_pages = fields.Integer(
        metadata={"description": "The total number of pages that can be fetched", "example": 2}
    )

    sort_order = fields.List(
        fields.Nested(SortOrderSchema()),
        metadata={"description": "The sort order passed in originally"},
    )
