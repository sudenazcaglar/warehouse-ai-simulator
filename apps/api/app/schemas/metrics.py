from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MetricSource
from app.schemas.pagination import PaginatedResponse


class MetricCreate(BaseModel):
    simulation_run_id: UUID | None = None
    training_session_id: UUID | None = None
    metric_name: str = Field(..., min_length=1, max_length=120)
    metric_value: float
    metric_unit: str | None = Field(default=None, max_length=40)
    source: MetricSource = MetricSource.API
    timestamp: datetime | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class MetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    simulation_run_id: UUID | None
    training_session_id: UUID | None
    metric_name: str
    metric_value: float
    metric_unit: str | None
    source: MetricSource
    timestamp: datetime
    metadata_json: dict[str, Any]


class MetricListResponse(PaginatedResponse):
    items: list[MetricResponse]
