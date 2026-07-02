from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_pagination, validate_uuid
from app.models.enums import AgentEventType
from app.repositories import events as event_repository
from app.schemas.common import ModuleStatusResponse
from app.schemas.events import EventCreate, EventListResponse, EventResponse
from app.schemas.pagination import PaginationParams

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/status", response_model=ModuleStatusResponse)
def events_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="events",
        status="available",
        detail="Events API module is registered and event ingestion endpoints are available.",
    )


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
) -> EventResponse:
    event = event_repository.create_event(db, payload)
    return EventResponse.model_validate(event)


@router.get("", response_model=EventListResponse)
def list_events(
    pagination: PaginationParams = Depends(get_pagination),
    simulation_run_id: str | None = Query(default=None),
    agent_id: str | None = Query(default=None),
    episode_id: str | None = Query(default=None),
    event_type: AgentEventType | None = Query(default=None),
    reason_code: str | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> EventListResponse:
    parsed_simulation_run_id = (
        validate_uuid(simulation_run_id, "simulation_run_id")
        if simulation_run_id is not None
        else None
    )
    parsed_agent_id = (
        validate_uuid(agent_id, "agent_id")
        if agent_id is not None
        else None
    )
    parsed_episode_id = (
        validate_uuid(episode_id, "episode_id")
        if episode_id is not None
        else None
    )

    items, total = event_repository.list_events(
        db,
        pagination=pagination,
        simulation_run_id=parsed_simulation_run_id,
        agent_id=parsed_agent_id,
        episode_id=parsed_episode_id,
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
