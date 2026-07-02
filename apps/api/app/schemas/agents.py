from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import AgentStatus
from app.schemas.pagination import PaginatedResponse


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    simulation_run_id: UUID
    agent_name: str
    agent_type: str
    policy_name: str | None
    spawn_position_x: float
    spawn_position_z: float
    status: AgentStatus
    metadata_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class AgentListResponse(PaginatedResponse):
    items: list[AgentResponse]
