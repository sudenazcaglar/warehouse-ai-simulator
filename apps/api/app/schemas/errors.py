from typing import Any

from pydantic import BaseModel, Field


class ValidationErrorDetail(BaseModel):
    location: list[str | int]
    message: str
    error_type: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
