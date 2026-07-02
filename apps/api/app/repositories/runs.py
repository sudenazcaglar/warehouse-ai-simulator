from typing import Literal
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

from app.api.errors import NotFoundError
from app.models import EnvironmentConfig, SimulationRun
from app.models.enums import SimulationStatus
from app.schemas.pagination import PaginationParams
from app.schemas.runs import RunCreate

RunSortBy = Literal["created_at", "started_at", "run_name", "status"]
SortOrder = Literal["asc", "desc"]

RUN_SORT_COLUMNS = {
    "created_at": SimulationRun.created_at,
    "started_at": SimulationRun.started_at,
    "run_name": SimulationRun.run_name,
    "status": SimulationRun.status,
}


def get_run_by_id(db: Session, run_id: UUID) -> SimulationRun | None:
    return db.get(SimulationRun, run_id)


def require_run_by_id(db: Session, run_id: UUID) -> SimulationRun:
    run = get_run_by_id(db, run_id)

    if run is None:
        raise NotFoundError(
            message="Simulation run not found.",
            details={"run_id": str(run_id)},
        )

    return run


def create_run(db: Session, data: RunCreate) -> SimulationRun:
    if data.environment_config_id is not None:
        environment_config = db.get(EnvironmentConfig, data.environment_config_id)

        if environment_config is None:
            raise NotFoundError(
                message="Environment config not found.",
                details={"environment_config_id": str(data.environment_config_id)},
            )

    run = SimulationRun(**data.model_dump())

    db.add(run)
    db.commit()
    db.refresh(run)

    return run


def build_run_filters(
    *,
    status: SimulationStatus | None = None,
    run_name: str | None = None,
    environment_name: str | None = None,
) -> list:
    filters = []

    if status is not None:
        filters.append(SimulationRun.status == status)

    if run_name:
        filters.append(SimulationRun.run_name.ilike(f"%{run_name}%"))

    if environment_name:
        filters.append(SimulationRun.environment_name.ilike(f"%{environment_name}%"))

    return filters


def apply_run_sorting(
    query: Select[tuple[SimulationRun]],
    *,
    sort_by: RunSortBy,
    sort_order: SortOrder,
) -> Select[tuple[SimulationRun]]:
    column = RUN_SORT_COLUMNS[sort_by]
    order_clause = asc(column) if sort_order == "asc" else desc(column)

    return query.order_by(order_clause)


def list_runs(
    db: Session,
    *,
    pagination: PaginationParams,
    status: SimulationStatus | None = None,
    run_name: str | None = None,
    environment_name: str | None = None,
    sort_by: RunSortBy = "started_at",
    sort_order: SortOrder = "desc",
) -> tuple[list[SimulationRun], int]:
    filters = build_run_filters(
        status=status,
        run_name=run_name,
        environment_name=environment_name,
    )

    total_query = select(func.count()).select_from(SimulationRun)

    if filters:
        total_query = total_query.where(*filters)

    total = int(db.execute(total_query).scalar_one())

    query = select(SimulationRun)

    if filters:
        query = query.where(*filters)

    query = apply_run_sorting(
        query,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    query = query.offset(pagination.offset).limit(pagination.limit)

    items = db.execute(query).scalars().all()

    return list(items), total
