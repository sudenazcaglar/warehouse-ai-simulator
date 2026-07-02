from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pagination import PaginatedResponse


class ModelVersionCreate(BaseModel):
    training_session_id: UUID
    checkpoint_id: UUID | None = None
    model_name: str = Field(..., min_length=1, max_length=160)
    version: str = Field(..., min_length=1, max_length=80)
    algorithm: str = Field(default="ppo", min_length=1, max_length=60)
    file_path: str = Field(..., min_length=1, max_length=500)
    onnx_path: str | None = Field(default=None, max_length=500)
    reward_mean: float | None = None
    success_rate: float | None = Field(default=None, ge=0, le=1)
    collision_rate: float | None = Field(default=None, ge=0, le=1)
    is_active: bool = False
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ModelVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    training_session_id: UUID
    checkpoint_id: UUID | None
    model_name: str
    version: str
    algorithm: str
    file_path: str
    onnx_path: str | None
    reward_mean: float | None
    success_rate: float | None
    collision_rate: float | None
    is_active: bool
    created_at: datetime
    metadata_json: dict[str, Any]


class ModelVersionListResponse(PaginatedResponse):
    items: list[ModelVersionResponse]
