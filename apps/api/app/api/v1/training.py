from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_pagination, validate_uuid
from app.models.enums import MetricSource, TrainingStatus
from app.repositories import metrics as metric_repository
from app.repositories import training as training_repository
from app.schemas.common import ModuleStatusResponse
from app.schemas.metrics import MetricListResponse, MetricResponse
from app.schemas.pagination import PaginationParams
from app.schemas.training import (
    TrainingListResponse,
    TrainingResponse,
    TrainingStartRequest,
    TrainingStopRequest,
)

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/status", response_model=ModuleStatusResponse)
def training_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="training",
        status="available",
        detail="Training API module is registered and database-backed endpoints are available.",
    )


@router.post(
    "/start",
    response_model=TrainingResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_training(
    payload: TrainingStartRequest,
    db: Session = Depends(get_db),
) -> TrainingResponse:
    training_session = training_repository.start_training_session(db, payload)
    return TrainingResponse.model_validate(training_session)


@router.get("", response_model=TrainingListResponse)
def list_training_sessions(
    pagination: PaginationParams = Depends(get_pagination),
    simulation_run_id: str | None = Query(default=None),
    status_filter: TrainingStatus | None = Query(default=None, alias="status"),
    algorithm: str | None = Query(default=None),
    sort_by: Literal["created_at", "started_at", "updated_at", "status", "algorithm"] = Query(
        default="started_at"
    ),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> TrainingListResponse:
    parsed_simulation_run_id = (
        validate_uuid(simulation_run_id, "simulation_run_id")
        if simulation_run_id is not None
        else None
    )

    items, total = training_repository.list_training_sessions(
        db,
        pagination=pagination,
        simulation_run_id=parsed_simulation_run_id,
        status=status_filter,
        algorithm=algorithm,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return TrainingListResponse.create(
        items=[TrainingResponse.model_validate(item) for item in items],
        total=total,
        pagination=pagination,
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
    training_repository.require_training_session_by_id(db, parsed_training_id)

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


@router.post("/{training_id}/stop", response_model=TrainingResponse)
def stop_training(
    training_id: str,
    payload: TrainingStopRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> TrainingResponse:
    parsed_training_id = validate_uuid(training_id, "training_id")
    target_status = payload.status if payload is not None else TrainingStatus.CANCELLED

    training_session = training_repository.stop_training_session(
        db,
        parsed_training_id,
        target_status=target_status,
    )

    return TrainingResponse.model_validate(training_session)


@router.get("/{training_id}", response_model=TrainingResponse)
def get_training_session(
    training_id: str,
    db: Session = Depends(get_db),
) -> TrainingResponse:
    parsed_training_id = validate_uuid(training_id, "training_id")
    training_session = training_repository.require_training_session_by_id(
        db,
        parsed_training_id,
    )

    return TrainingResponse.model_validate(training_session)
