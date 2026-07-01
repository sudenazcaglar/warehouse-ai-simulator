from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SimulationStatus, enum_values
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.agent_event import AgentEvent
    from app.models.collision import Collision
    from app.models.delivery import Delivery
    from app.models.environment_config import EnvironmentConfig
    from app.models.episode import Episode
    from app.models.system_metric import SystemMetric
    from app.models.training_session import TrainingSession


class SimulationRun(TimestampMixin, Base):
    __tablename__ = "simulation_runs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    environment_config_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("environment_configs.id", ondelete="SET NULL"),
        nullable=True,
    )
    run_name: Mapped[str] = mapped_column(String(160), nullable=False)
    environment_name: Mapped[str] = mapped_column(String(120), nullable=False)
    agent_count: Mapped[int] = mapped_column(Integer, nullable=False)
    map_version: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[SimulationStatus] = mapped_column(
        Enum(
            SimulationStatus,
            name="simulation_status",
            values_callable=enum_values,
        ),
        nullable=False,
        default=SimulationStatus.CREATED,
        server_default=SimulationStatus.CREATED.value,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    config_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    environment_config: Mapped[EnvironmentConfig | None] = relationship(
        back_populates="simulation_runs",
    )
    training_sessions: Mapped[list[TrainingSession]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
    )
    episodes: Mapped[list[Episode]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
    )
    agents: Mapped[list[Agent]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
    )
    agent_events: Mapped[list[AgentEvent]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
    )
    collisions: Mapped[list[Collision]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
    )
    deliveries: Mapped[list[Delivery]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
    )
    system_metrics: Mapped[list[SystemMetric]] = relationship(
        back_populates="simulation_run",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_simulation_runs_status_started_at", "status", "started_at"),
        Index("ix_simulation_runs_environment_name", "environment_name"),
    )
