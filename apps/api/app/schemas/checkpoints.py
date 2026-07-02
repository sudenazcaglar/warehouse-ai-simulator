from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pagination import PaginatedResponse


class CheckpointCreate(BaseModel):
    training_session_id: UUID
    step: int = Field(..., ge=0)
    reward_mean: float | None = None
    success_rate: float | None = Field(default=None, ge=0, le=1)
    collision_rate: float | None = Field(default=None, ge=0, le=1)
    file_path: str = Field(..., min_length=1, max_length=500)
    storage_backend: str = Field(default="minio", min_length=1, max_length=80)
    is_best: bool = False
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class CheckpointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    training_session_id: UUID
    step: int
    reward_mean: float | None
    success_rate: float | None
    collision_rate: float | None
    file_path: str
    storage_backend: str
    created_at: datetime
    is_best: bool
    metadata_json: dict[str, Any]


class CheckpointListResponse(PaginatedResponse):
    items: list[CheckpointResponse]
