from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Enum, Float, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AgentStatus, enum_values
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.agent_event import AgentEvent
    from app.models.collision import Collision
    from app.models.delivery import Delivery
    from app.models.simulation_run import SimulationRun


class Agent(TimestampMixin, Base):
    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    simulation_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    agent_name: Mapped[str] = mapped_column(String(120), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(80), nullable=False, server_default="warehouse_robot")
    policy_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    spawn_position_x: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    spawn_position_z: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    status: Mapped[AgentStatus] = mapped_column(
        Enum(
            AgentStatus,
            name="agent_status",
            values_callable=enum_values,
        ),
        nullable=False,
        default=AgentStatus.IDLE,
        server_default=AgentStatus.IDLE.value,
    )
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    simulation_run: Mapped[SimulationRun] = relationship(back_populates="agents")
    events: Mapped[list[AgentEvent]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    collisions: Mapped[list[Collision]] = relationship(
        back_populates="agent",
        foreign_keys="Collision.agent_id",
    )
    deliveries: Mapped[list[Delivery]] = relationship(back_populates="agent")

    __table_args__ = (
        UniqueConstraint("simulation_run_id", "agent_name", name="uq_agents_run_agent_name"),
        Index("ix_agents_run_status", "simulation_run_id", "status"),
    )
