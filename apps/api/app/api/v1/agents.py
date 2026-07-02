from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_pagination, validate_uuid
from app.models.enums import AgentEventType, AgentStatus
from app.repositories import agents as agent_repository
from app.repositories import events as event_repository
from app.schemas.agents import AgentListResponse, AgentResponse
from app.schemas.common import ModuleStatusResponse
from app.schemas.events import EventListResponse, EventResponse
from app.schemas.pagination import PaginationParams

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/status", response_model=ModuleStatusResponse)
def agents_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="agents",
        status="available",
        detail="Agents API module is registered and database-backed endpoints are available.",
    )


@router.get("", response_model=AgentListResponse)
def list_agents(
    pagination: PaginationParams = Depends(get_pagination),
    status_filter: AgentStatus | None = Query(default=None, alias="status"),
    simulation_run_id: str | None = Query(default=None),
    agent_name: str | None = Query(default=None),
    policy_name: str | None = Query(default=None),
    sort_by: Literal["created_at", "agent_name", "status"] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> AgentListResponse:
    parsed_simulation_run_id = (
        validate_uuid(simulation_run_id, "simulation_run_id")
        if simulation_run_id is not None
        else None
    )

    items, total = agent_repository.list_agents(
        db,
        pagination=pagination,
        status=status_filter,
        simulation_run_id=parsed_simulation_run_id,
        agent_name=agent_name,
        policy_name=policy_name,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return AgentListResponse.create(
        items=[AgentResponse.model_validate(item) for item in items],
        total=total,
        pagination=pagination,
    )


@router.get("/{agent_id}/timeline", response_model=EventListResponse)
def get_agent_timeline(
    agent_id: str,
    pagination: PaginationParams = Depends(get_pagination),
    event_type: AgentEventType | None = Query(default=None),
    reason_code: str | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    sort_order: Literal["asc", "desc"] = Query(default="asc"),
    db: Session = Depends(get_db),
) -> EventListResponse:
    parsed_agent_id = validate_uuid(agent_id, "agent_id")
    agent_repository.require_agent_by_id(db, parsed_agent_id)

    items, total = event_repository.list_events(
        db,
        pagination=pagination,
        agent_id=parsed_agent_id,
        event_type=event_type,
        reason_code=reason_code,
        start_time=start_time,
        end_time=end_time,
        sort_order=sort_order,
    )

    return EventListResponse.create(
        items=[EventResponse.model_validate(item) for item in items],
        total=total,
        pagination=pagination,
    )


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
) -> AgentResponse:
    parsed_agent_id = validate_uuid(agent_id, "agent_id")
    agent = agent_repository.require_agent_by_id(db, parsed_agent_id)

    return AgentResponse.model_validate(agent)
