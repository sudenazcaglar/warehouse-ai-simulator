from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_pagination, validate_uuid
from app.models.enums import MetricSource
from app.repositories import metrics as metric_repository
from app.schemas.common import ModuleStatusResponse
from app.schemas.metrics import MetricCreate, MetricListResponse, MetricResponse
from app.schemas.pagination import PaginationParams
from app.services.websocket_manager import websocket_manager

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/status", response_model=ModuleStatusResponse)
def metrics_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="metrics",
        status="available",
        detail="Metrics API module is registered and metric ingestion endpoints are available.",
    )


@router.post(
    "",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_metric(
    payload: MetricCreate,
    db: Session = Depends(get_db),
) -> MetricResponse:
    metric = metric_repository.create_metric(db, payload)
    response = MetricResponse.model_validate(metric)

    if metric.simulation_run_id is not None:
        await websocket_manager.broadcast_run_metric(
            str(metric.simulation_run_id),
            {
                "type": "metric",
                "data": response.model_dump(mode="json"),
            },
        )

    return response


@router.get("", response_model=MetricListResponse)
def list_metrics(
    pagination: PaginationParams = Depends(get_pagination),
    simulation_run_id: str | None = Query(default=None),
    training_session_id: str | None = Query(default=None),
    metric_name: str | None = Query(default=None),
    source: MetricSource | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> MetricListResponse:
    parsed_simulation_run_id = (
        validate_uuid(simulation_run_id, "simulation_run_id")
        if simulation_run_id is not None
        else None
    )
    parsed_training_session_id = (
        validate_uuid(training_session_id, "training_session_id")
        if training_session_id is not None
        else None
    )

    items, total = metric_repository.list_metrics(
        db,
        pagination=pagination,
        simulation_run_id=parsed_simulation_run_id,
        training_session_id=parsed_training_session_id,
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
