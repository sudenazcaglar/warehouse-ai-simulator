from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

from app.api.errors import ConflictError, NotFoundError
from app.models import Agent, AgentEvent, Episode, SimulationRun
from app.models.enums import AgentEventType
from app.schemas.events import EventCreate
from app.schemas.pagination import PaginationParams

SortOrder = Literal["asc", "desc"]


def get_event_by_id(db: Session, event_id: UUID) -> AgentEvent | None:
    return db.get(AgentEvent, event_id)


def validate_event_relationships(db: Session, data: EventCreate) -> None:
    run = db.get(SimulationRun, data.simulation_run_id)

    if run is None:
        raise NotFoundError(
            message="Simulation run not found.",
            details={"simulation_run_id": str(data.simulation_run_id)},
        )

    agent = db.get(Agent, data.agent_id)

    if agent is None:
        raise NotFoundError(
            message="Agent not found.",
            details={"agent_id": str(data.agent_id)},
        )

    if agent.simulation_run_id != data.simulation_run_id:
        raise ConflictError(
            message="Agent does not belong to the provided simulation run.",
            code="agent_run_mismatch",
            details={
                "agent_id": str(data.agent_id),
                "agent_simulation_run_id": str(agent.simulation_run_id),
                "provided_simulation_run_id": str(data.simulation_run_id),
            },
        )

    if data.episode_id is not None:
        episode = db.get(Episode, data.episode_id)

        if episode is None:
            raise NotFoundError(
                message="Episode not found.",
                details={"episode_id": str(data.episode_id)},
            )

        if episode.simulation_run_id != data.simulation_run_id:
            raise ConflictError(
                message="Episode does not belong to the provided simulation run.",
                code="episode_run_mismatch",
                details={
                    "episode_id": str(data.episode_id),
                    "episode_simulation_run_id": str(episode.simulation_run_id),
                    "provided_simulation_run_id": str(data.simulation_run_id),
                },
            )


def create_event(db: Session, data: EventCreate) -> AgentEvent:
    validate_event_relationships(db, data)

    payload = data.model_dump(exclude_none=True)
    event = AgentEvent(**payload)

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def build_event_filters(
    *,
    simulation_run_id: UUID | None = None,
    agent_id: UUID | None = None,
    episode_id: UUID | None = None,
    event_type: AgentEventType | None = None,
    reason_code: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list:
    filters = []

    if simulation_run_id is not None:
        filters.append(AgentEvent.simulation_run_id == simulation_run_id)

    if agent_id is not None:
        filters.append(AgentEvent.agent_id == agent_id)

    if episode_id is not None:
        filters.append(AgentEvent.episode_id == episode_id)

    if event_type is not None:
        filters.append(AgentEvent.event_type == event_type)

    if reason_code:
        filters.append(AgentEvent.reason_code.ilike(f"%{reason_code}%"))

    if start_time is not None:
        filters.append(AgentEvent.timestamp >= start_time)

    if end_time is not None:
        filters.append(AgentEvent.timestamp <= end_time)

    return filters


def apply_event_sorting(
    query: Select[tuple[AgentEvent]],
    *,
    sort_order: SortOrder,
) -> Select[tuple[AgentEvent]]:
    order_clause = asc(AgentEvent.timestamp) if sort_order == "asc" else desc(AgentEvent.timestamp)
    return query.order_by(order_clause)


def list_events(
    db: Session,
    *,
    pagination: PaginationParams,
    simulation_run_id: UUID | None = None,
    agent_id: UUID | None = None,
    episode_id: UUID | None = None,
    event_type: AgentEventType | None = None,
    reason_code: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    sort_order: SortOrder = "desc",
) -> tuple[list[AgentEvent], int]:
    filters = build_event_filters(
        simulation_run_id=simulation_run_id,
        agent_id=agent_id,
        episode_id=episode_id,
        event_type=event_type,
        reason_code=reason_code,
        start_time=start_time,
        end_time=end_time,
    )

    total_query = select(func.count()).select_from(AgentEvent)

    if filters:
        total_query = total_query.where(*filters)

    total = int(db.execute(total_query).scalar_one())

    query = select(AgentEvent)

    if filters:
        query = query.where(*filters)

    query = apply_event_sorting(query, sort_order=sort_order)
    query = query.offset(pagination.offset).limit(pagination.limit)

    items = db.execute(query).scalars().all()

    return list(items), total
