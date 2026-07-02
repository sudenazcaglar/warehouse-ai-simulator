from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    database: str
    timestamp: datetime


class APIInfoResponse(BaseModel):
    service: str
    version: str
    environment: str
    modules: list[str] = Field(default_factory=list)


class ModuleStatusResponse(BaseModel):
    module: str
    status: str
    detail: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
