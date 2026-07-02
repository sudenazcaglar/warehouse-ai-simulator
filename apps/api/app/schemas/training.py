from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TrainingStatus
from app.schemas.pagination import PaginatedResponse


class TrainingStartRequest(BaseModel):
    simulation_run_id: UUID
    environment_config_id: UUID | None = None
    algorithm: str = Field(default="ppo", min_length=1, max_length=60)
    max_steps: int = Field(..., ge=1)
    learning_rate: float = Field(..., gt=0)
    batch_size: int = Field(..., ge=1)
    buffer_size: int = Field(..., ge=1)
    checkpoint_interval: int = Field(..., ge=1)


class TrainingStopRequest(BaseModel):
    status: Literal[
        TrainingStatus.COMPLETED,
        TrainingStatus.CANCELLED,
        TrainingStatus.FAILED,
    ] = TrainingStatus.CANCELLED


class TrainingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    simulation_run_id: UUID
    environment_config_id: UUID | None
    algorithm: str
    max_steps: int
    current_step: int
    learning_rate: float
    batch_size: int
    buffer_size: int
    checkpoint_interval: int
    status: TrainingStatus
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TrainingListResponse(PaginatedResponse):
    items: list[TrainingResponse]
