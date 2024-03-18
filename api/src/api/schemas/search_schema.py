from enum import StrEnum
from typing import Type

from src.api.schemas.extension import Schema, fields, validators


class StrSearchSchemaBuilder:
    """
    Builder for setting up a filter in a search endpoint schema.

    Our schemas are setup to look like:

        {
            "filters": {
                "field": {
                    "one_of": ["x", "y", "z"]
                }
            }
        }

    This helps generate the filters for a given field. At the moment,
    only a one_of filter is implemented.

    Usage::

        # In a search request schema, you would use it like so

        class OpportunitySearchFilterSchema(Schema):
            example_enum_field = fields.Nested(
                StrSearchSchemaBuilder("ExampleEnumFieldSchema")
                    .with_one_of(allowed_values=ExampleEnum)
                    .build()
            )

            example_str_field = fields.Nested(
                StrSearchSchemaBuilder("ExampleStrFieldSchema")
                    .with_one_of(example="example_value", minimum_length=5)
                    .build()
            )
    """

    def __init__(self, schema_class_name: str):
        # The schema class name is used on the endpoint
        self.schema_fields: dict[str, fields.MixinField] = {}
        self.schema_class_name = schema_class_name

    def with_one_of(
        self,
        *,
        allowed_values: Type[StrEnum] | None = None,
        example: str | None = None,
        minimum_length: int | None = None
    ) -> "StrSearchSchemaBuilder":
        metadata = {}
        if example:
            metadata["example"] = example

        # We assume it's just a list of strings
        if allowed_values is None:
            params: dict = {"metadata": metadata}
            if minimum_length is not None:
                params["validate"] = [validators.Length(min=2)]

            list_type: fields.MixinField = fields.String(**params)

        # Otherwise it is an enum type which handles allowed values
        else:
            list_type = fields.Enum(allowed_values, metadata=metadata)

        self.schema_fields["one_of"] = fields.List(list_type)

        return self

    def build(self) -> Schema:
        return Schema.from_dict(self.schema_fields, name=self.schema_class_name)  # type: ignore
