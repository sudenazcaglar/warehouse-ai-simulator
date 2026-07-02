from typing import Literal
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

from app.api.errors import NotFoundError
from app.models import Agent
from app.models.enums import AgentStatus
from app.schemas.pagination import PaginationParams

AgentSortBy = Literal["created_at", "agent_name", "status"]
SortOrder = Literal["asc", "desc"]

AGENT_SORT_COLUMNS = {
    "created_at": Agent.created_at,
    "agent_name": Agent.agent_name,
    "status": Agent.status,
}


def get_agent_by_id(db: Session, agent_id: UUID) -> Agent | None:
    return db.get(Agent, agent_id)


def require_agent_by_id(db: Session, agent_id: UUID) -> Agent:
    agent = get_agent_by_id(db, agent_id)

    if agent is None:
        raise NotFoundError(
            message="Agent not found.",
            details={"agent_id": str(agent_id)},
        )

    return agent


def build_agent_filters(
    *,
    status: AgentStatus | None = None,
    simulation_run_id: UUID | None = None,
    agent_name: str | None = None,
    policy_name: str | None = None,
) -> list:
    filters = []

    if status is not None:
        filters.append(Agent.status == status)

    if simulation_run_id is not None:
        filters.append(Agent.simulation_run_id == simulation_run_id)

    if agent_name:
        filters.append(Agent.agent_name.ilike(f"%{agent_name}%"))

    if policy_name:
        filters.append(Agent.policy_name.ilike(f"%{policy_name}%"))

    return filters


def apply_agent_sorting(
    query: Select[tuple[Agent]],
    *,
    sort_by: AgentSortBy,
    sort_order: SortOrder,
) -> Select[tuple[Agent]]:
    column = AGENT_SORT_COLUMNS[sort_by]
    order_clause = asc(column) if sort_order == "asc" else desc(column)

    return query.order_by(order_clause)


def list_agents(
    db: Session,
    *,
    pagination: PaginationParams,
    status: AgentStatus | None = None,
    simulation_run_id: UUID | None = None,
    agent_name: str | None = None,
    policy_name: str | None = None,
    sort_by: AgentSortBy = "created_at",
    sort_order: SortOrder = "desc",
) -> tuple[list[Agent], int]:
    filters = build_agent_filters(
        status=status,
        simulation_run_id=simulation_run_id,
        agent_name=agent_name,
        policy_name=policy_name,
    )

    total_query = select(func.count()).select_from(Agent)

    if filters:
        total_query = total_query.where(*filters)

    total = int(db.execute(total_query).scalar_one())

    query = select(Agent)

    if filters:
        query = query.where(*filters)

    query = apply_agent_sorting(
        query,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    query = query.offset(pagination.offset).limit(pagination.limit)

    items = db.execute(query).scalars().all()

    return list(items), total
