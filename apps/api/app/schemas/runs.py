from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SimulationStatus
from app.schemas.pagination import PaginatedResponse


class RunCreate(BaseModel):
    environment_config_id: UUID | None = None
    run_name: str = Field(..., min_length=1, max_length=160)
    environment_name: str = Field(..., min_length=1, max_length=120)
    agent_count: int = Field(..., ge=1)
    map_version: str = Field(..., min_length=1, max_length=40)
    status: SimulationStatus = SimulationStatus.CREATED
    config_json: dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    environment_config_id: UUID | None
    run_name: str
    environment_name: str
    agent_count: int
    map_version: str
    status: SimulationStatus
    started_at: datetime
    ended_at: datetime | None
    config_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class RunListResponse(PaginatedResponse):
    items: list[RunResponse]
