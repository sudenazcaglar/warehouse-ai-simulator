from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_pagination, validate_uuid
from app.models.enums import MetricSource
from app.repositories import metrics as metric_repository
from app.schemas.common import ModuleStatusResponse
from app.schemas.metrics import MetricListResponse, MetricResponse
from app.schemas.pagination import PaginationParams

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/status", response_model=ModuleStatusResponse)
def training_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="training",
        status="available",
        detail="Training API module is registered. Metrics endpoint is available; training lifecycle endpoints will be added in Phase 4F.",
    )


@router.get("/{training_id}/metrics", response_model=MetricListResponse)
def list_training_metrics(
    training_id: str,
    pagination: PaginationParams = Depends(get_pagination),
    metric_name: str | None = Query(default=None),
    source: MetricSource | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> MetricListResponse:
    parsed_training_id = validate_uuid(training_id, "training_id")
    metric_repository.require_training_session_by_id(db, parsed_training_id)

    items, total = metric_repository.list_metrics(
        db,
        pagination=pagination,
        training_session_id=parsed_training_id,
        metric_name=metric_name,
        source=source,
        start_time=start_time,
        end_time=end_time,
        sort_order=sort_order,
    )

    return MetricListResponse.create(
        items=[MetricResponse.model_validate(item) for item in items],
        total=total,
        pagination=pagination,
    )
