from __future__ import annotations

from pydantic import BaseModel, Field


class ApiError(BaseModel):
    message: str
    code: str | None = None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int = Field(alias="page")
    page_size: int = Field(alias="pageSize")
