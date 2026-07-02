from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_pagination, validate_uuid
from app.models.enums import SimulationStatus
from app.repositories import agents as agent_repository
from app.repositories import runs as run_repository
from app.schemas.agents import AgentListResponse
from app.schemas.common import ModuleStatusResponse
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.runs import RunCreate, RunListResponse, RunResponse

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/status", response_model=ModuleStatusResponse)
def runs_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="runs",
        status="available",
        detail="Runs API module is registered and database-backed endpoints are available.",
    )


@router.post(
    "",
    response_model=RunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_run(
    payload: RunCreate,
    db: Session = Depends(get_db),
) -> RunResponse:
    run = run_repository.create_run(db, payload)
    return RunResponse.model_validate(run)


@router.get("", response_model=RunListResponse)
def list_runs(
    pagination: PaginationParams = Depends(get_pagination),
    status_filter: SimulationStatus | None = Query(default=None, alias="status"),
    run_name: str | None = Query(default=None),
    environment_name: str | None = Query(default=None),
    sort_by: Literal["created_at", "started_at", "run_name", "status"] = Query(
        default="started_at"
    ),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> RunListResponse:
    items, total = run_repository.list_runs(
        db,
        pagination=pagination,
        status=status_filter,
        run_name=run_name,
        environment_name=environment_name,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return RunListResponse.create(
        items=[RunResponse.model_validate(item) for item in items],
        total=total,
        pagination=pagination,
    )


@router.get("/{run_id}/agents", response_model=AgentListResponse)
def list_run_agents(
    run_id: str,
    pagination: PaginationParams = Depends(get_pagination),
    status_filter: str | None = Query(default=None, alias="status"),
    agent_name: str | None = Query(default=None),
    sort_by: Literal["created_at", "agent_name", "status"] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> AgentListResponse:
    parsed_run_id = validate_uuid(run_id, "run_id")
    run_repository.require_run_by_id(db, parsed_run_id)

    agent_status = None
    if status_filter is not None:
        from app.models.enums import AgentStatus

        try:
            agent_status = AgentStatus(status_filter)
        except ValueError as exc:
            from app.api.errors import BadRequestError

            raise BadRequestError(
                message="Invalid agent status.",
                code="invalid_agent_status",
                details={"status": status_filter},
            ) from exc

    items, total = agent_repository.list_agents(
        db,
        pagination=pagination,
        status=agent_status,
        simulation_run_id=parsed_run_id,
        agent_name=agent_name,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    from app.schemas.agents import AgentResponse

    return AgentListResponse.create(
        items=[AgentResponse.model_validate(item) for item in items],
        total=total,
        pagination=pagination,
    )


@router.get("/{run_id}", response_model=RunResponse)
def get_run(
    run_id: str,
    db: Session = Depends(get_db),
) -> RunResponse:
    parsed_run_id = validate_uuid(run_id, "run_id")
    run = run_repository.require_run_by_id(db, parsed_run_id)

    return RunResponse.model_validate(run)
