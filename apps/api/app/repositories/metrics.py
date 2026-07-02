from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

from app.api.errors import ConflictError, NotFoundError
from app.models import SimulationRun, SystemMetric, TrainingSession
from app.models.enums import MetricSource
from app.schemas.metrics import MetricCreate
from app.schemas.pagination import PaginationParams

SortOrder = Literal["asc", "desc"]


def require_training_session_by_id(db: Session, training_session_id: UUID) -> TrainingSession:
    training_session = db.get(TrainingSession, training_session_id)

    if training_session is None:
        raise NotFoundError(
            message="Training session not found.",
            details={"training_session_id": str(training_session_id)},
        )

    return training_session


def validate_metric_relationships(db: Session, data: MetricCreate) -> None:
    run = None

    if data.simulation_run_id is not None:
        run = db.get(SimulationRun, data.simulation_run_id)

        if run is None:
            raise NotFoundError(
                message="Simulation run not found.",
                details={"simulation_run_id": str(data.simulation_run_id)},
            )

    if data.training_session_id is not None:
        training_session = require_training_session_by_id(db, data.training_session_id)

        if (
            data.simulation_run_id is not None
            and training_session.simulation_run_id != data.simulation_run_id
        ):
            raise ConflictError(
                message="Training session does not belong to the provided simulation run.",
                code="training_run_mismatch",
                details={
                    "training_session_id": str(data.training_session_id),
                    "training_session_run_id": str(training_session.simulation_run_id),
                    "provided_simulation_run_id": str(data.simulation_run_id),
                },
            )


def create_metric(db: Session, data: MetricCreate) -> SystemMetric:
    validate_metric_relationships(db, data)

    payload = data.model_dump(exclude_none=True)
    metric = SystemMetric(**payload)

    db.add(metric)
    db.commit()
    db.refresh(metric)

    return metric


def build_metric_filters(
    *,
    simulation_run_id: UUID | None = None,
    training_session_id: UUID | None = None,
    metric_name: str | None = None,
    source: MetricSource | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list:
    filters = []

    if simulation_run_id is not None:
        filters.append(SystemMetric.simulation_run_id == simulation_run_id)

    if training_session_id is not None:
        filters.append(SystemMetric.training_session_id == training_session_id)

    if metric_name:
        filters.append(SystemMetric.metric_name.ilike(f"%{metric_name}%"))

    if source is not None:
        filters.append(SystemMetric.source == source)

    if start_time is not None:
        filters.append(SystemMetric.timestamp >= start_time)

    if end_time is not None:
        filters.append(SystemMetric.timestamp <= end_time)

    return filters


def apply_metric_sorting(
    query: Select[tuple[SystemMetric]],
    *,
    sort_order: SortOrder,
) -> Select[tuple[SystemMetric]]:
    order_clause = asc(SystemMetric.timestamp) if sort_order == "asc" else desc(SystemMetric.timestamp)
    return query.order_by(order_clause)


def list_metrics(
    db: Session,
    *,
    pagination: PaginationParams,
    simulation_run_id: UUID | None = None,
    training_session_id: UUID | None = None,
    metric_name: str | None = None,
    source: MetricSource | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    sort_order: SortOrder = "desc",
) -> tuple[list[SystemMetric], int]:
    filters = build_metric_filters(
        simulation_run_id=simulation_run_id,
        training_session_id=training_session_id,
        metric_name=metric_name,
        source=source,
        start_time=start_time,
        end_time=end_time,
    )

    total_query = select(func.count()).select_from(SystemMetric)

    if filters:
        total_query = total_query.where(*filters)

    total = int(db.execute(total_query).scalar_one())

    query = select(SystemMetric)

    if filters:
        query = query.where(*filters)

    query = apply_metric_sorting(query, sort_order=sort_order)
    query = query.offset(pagination.offset).limit(pagination.limit)

    items = db.execute(query).scalars().all()

    return list(items), total
