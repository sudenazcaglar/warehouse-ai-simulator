from math import ceil
from typing import Any

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(
        cls,
        *,
        items: list[Any],
        total: int,
        pagination: PaginationParams,
    ) -> "PaginatedResponse":
        pages = ceil(total / pagination.page_size) if total > 0 else 0

        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=pages,
            has_next=pagination.page < pages,
            has_previous=pagination.page > 1,
        )
