from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AgentEventType
from app.schemas.pagination import PaginatedResponse


class EventCreate(BaseModel):
    simulation_run_id: UUID
    episode_id: UUID | None = None
    agent_id: UUID
    timestamp: datetime | None = None
    step: int | None = Field(default=None, ge=0)
    position_x: float
    position_z: float
    velocity: float | None = None
    action: str | None = Field(default=None, max_length=120)
    reward_delta: float = 0.0
    event_type: AgentEventType = AgentEventType.CUSTOM
    reason_code: str | None = Field(default=None, max_length=120)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    simulation_run_id: UUID
    episode_id: UUID | None
    agent_id: UUID
    timestamp: datetime
    step: int | None
    position_x: float
    position_z: float
    velocity: float | None
    action: str | None
    reward_delta: float
    event_type: AgentEventType
    reason_code: str | None
    metadata_json: dict[str, Any]
    created_at: datetime


class EventListResponse(PaginatedResponse):
    items: list[EventResponse]
