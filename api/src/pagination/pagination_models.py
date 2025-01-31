import dataclasses
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field

from src.pagination.paginator import Paginator


class SortDirection(StrEnum):
    ASCENDING = "ascending"
    DESCENDING = "descending"

    def short_form(self) -> str:
        if self == SortDirection.DESCENDING:
            return "desc"
        return "asc"


class SortOrderParams(BaseModel):
    order_by: str
    sort_direction: SortDirection


class PaginationParams(BaseModel):
    page_offset: int
    page_size: int

    sort_order: list[SortOrderParams] = Field(default_factory=list)


@dataclasses.dataclass
class SortOrder:
    order_by: str
    sort_direction: SortDirection


@dataclasses.dataclass
class PaginationInfo:
    page_offset: int
    page_size: int

    total_records: int
    total_pages: int

    sort_order: list[SortOrder]

    @classmethod
    def from_pagination_params(
        cls, pagination_params: PaginationParams, paginator: Paginator
    ) -> Self:
        return cls(
            page_offset=pagination_params.page_offset,
            page_size=pagination_params.page_size,
            total_records=paginator.total_records,
            total_pages=paginator.total_pages,
            sort_order=[
                SortOrder(p.order_by, p.sort_direction) for p in pagination_params.sort_order
            ],
        )
