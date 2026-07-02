from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

from app.api.errors import ConflictError, NotFoundError
from app.models import EnvironmentConfig, SimulationRun, TrainingSession
from app.models.enums import TrainingStatus
from app.schemas.pagination import PaginationParams
from app.schemas.training import TrainingStartRequest

TrainingSortBy = Literal["created_at", "started_at", "updated_at", "status", "algorithm"]
SortOrder = Literal["asc", "desc"]

TRAINING_SORT_COLUMNS = {
    "created_at": TrainingSession.created_at,
    "started_at": TrainingSession.started_at,
    "updated_at": TrainingSession.updated_at,
    "status": TrainingSession.status,
    "algorithm": TrainingSession.algorithm,
}

TERMINAL_TRAINING_STATUSES = {
    TrainingStatus.COMPLETED,
    TrainingStatus.FAILED,
    TrainingStatus.CANCELLED,
}


def get_training_session_by_id(
    db: Session,
    training_session_id: UUID,
) -> TrainingSession | None:
    return db.get(TrainingSession, training_session_id)


def require_training_session_by_id(
    db: Session,
    training_session_id: UUID,
) -> TrainingSession:
    training_session = get_training_session_by_id(db, training_session_id)

    if training_session is None:
        raise NotFoundError(
            message="Training session not found.",
            details={"training_session_id": str(training_session_id)},
        )

    return training_session


def validate_training_start_relationships(
    db: Session,
    data: TrainingStartRequest,
) -> None:
    run = db.get(SimulationRun, data.simulation_run_id)

    if run is None:
        raise NotFoundError(
            message="Simulation run not found.",
            details={"simulation_run_id": str(data.simulation_run_id)},
        )

    if data.environment_config_id is not None:
        environment_config = db.get(EnvironmentConfig, data.environment_config_id)

        if environment_config is None:
            raise NotFoundError(
                message="Environment config not found.",
                details={"environment_config_id": str(data.environment_config_id)},
            )


def start_training_session(
    db: Session,
    data: TrainingStartRequest,
) -> TrainingSession:
    validate_training_start_relationships(db, data)

    training_session = TrainingSession(
        **data.model_dump(),
        current_step=0,
        status=TrainingStatus.RUNNING,
    )

    db.add(training_session)
    db.commit()
    db.refresh(training_session)

    return training_session


def stop_training_session(
    db: Session,
    training_session_id: UUID,
    *,
    target_status: TrainingStatus = TrainingStatus.CANCELLED,
) -> TrainingSession:
    training_session = require_training_session_by_id(db, training_session_id)

    if training_session.status in TERMINAL_TRAINING_STATUSES:
        raise ConflictError(
            message="Training session is already in a terminal state.",
            code="training_already_stopped",
            details={
                "training_session_id": str(training_session_id),
                "status": training_session.status.value,
            },
        )

    if target_status not in TERMINAL_TRAINING_STATUSES:
        raise ConflictError(
            message="Training session can only be stopped with a terminal status.",
            code="invalid_training_stop_status",
            details={
                "training_session_id": str(training_session_id),
                "target_status": target_status.value,
            },
        )

    training_session.status = target_status
    training_session.ended_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(training_session)

    return training_session


def build_training_filters(
    *,
    simulation_run_id: UUID | None = None,
    status: TrainingStatus | None = None,
    algorithm: str | None = None,
) -> list:
    filters = []

    if simulation_run_id is not None:
        filters.append(TrainingSession.simulation_run_id == simulation_run_id)

    if status is not None:
        filters.append(TrainingSession.status == status)

    if algorithm:
        filters.append(TrainingSession.algorithm.ilike(f"%{algorithm}%"))

    return filters


def apply_training_sorting(
    query: Select[tuple[TrainingSession]],
    *,
    sort_by: TrainingSortBy,
    sort_order: SortOrder,
) -> Select[tuple[TrainingSession]]:
    column = TRAINING_SORT_COLUMNS[sort_by]
    order_clause = asc(column) if sort_order == "asc" else desc(column)

    return query.order_by(order_clause)


def list_training_sessions(
    db: Session,
    *,
    pagination: PaginationParams,
    simulation_run_id: UUID | None = None,
    status: TrainingStatus | None = None,
    algorithm: str | None = None,
    sort_by: TrainingSortBy = "started_at",
    sort_order: SortOrder = "desc",
) -> tuple[list[TrainingSession], int]:
    filters = build_training_filters(
        simulation_run_id=simulation_run_id,
        status=status,
        algorithm=algorithm,
    )

    total_query = select(func.count()).select_from(TrainingSession)

    if filters:
        total_query = total_query.where(*filters)

    total = int(db.execute(total_query).scalar_one())

    query = select(TrainingSession)

    if filters:
        query = query.where(*filters)

    query = apply_training_sorting(
        query,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    query = query.offset(pagination.offset).limit(pagination.limit)

    items = db.execute(query).scalars().all()

    return list(items), total
