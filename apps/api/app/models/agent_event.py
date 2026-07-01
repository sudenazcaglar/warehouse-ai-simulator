from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AgentEventType, enum_values

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.episode import Episode
    from app.models.llm_explanation import LLMExplanation
    from app.models.simulation_run import SimulationRun


class AgentEvent(Base):
    __tablename__ = "agent_events"

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
    episode_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("episodes.id", ondelete="SET NULL"),
        nullable=True,
    )
    agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    step: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_x: Mapped[float] = mapped_column(Float, nullable=False)
    position_z: Mapped[float] = mapped_column(Float, nullable=False)
    velocity: Mapped[float | None] = mapped_column(Float, nullable=True)
    action: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reward_delta: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    event_type: Mapped[AgentEventType] = mapped_column(
        Enum(
            AgentEventType,
            name="agent_event_type",
            values_callable=enum_values,
        ),
        nullable=False,
        default=AgentEventType.CUSTOM,
        server_default=AgentEventType.CUSTOM.value,
    )
    reason_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    simulation_run: Mapped[SimulationRun] = relationship(back_populates="agent_events")
    episode: Mapped[Episode | None] = relationship(back_populates="agent_events")
    agent: Mapped[Agent] = relationship(back_populates="events")
    llm_explanations: Mapped[list[LLMExplanation]] = relationship(
        back_populates="agent_event",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_agent_events_run_timestamp", "simulation_run_id", "timestamp"),
        Index("ix_agent_events_agent_timestamp", "agent_id", "timestamp"),
        Index("ix_agent_events_episode_step", "episode_id", "step"),
        Index("ix_agent_events_event_type", "event_type"),
        Index("ix_agent_events_reason_code", "reason_code"),
    )
