from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.agent_event import AgentEvent
    from app.models.collision import Collision
    from app.models.delivery import Delivery
    from app.models.simulation_run import SimulationRun
    from app.models.training_session import TrainingSession


class Episode(TimestampMixin, Base):
    __tablename__ = "episodes"

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
    training_session_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_total: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    step_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    collision_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    delivery_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    simulation_run: Mapped[SimulationRun] = relationship(back_populates="episodes")
    training_session: Mapped[TrainingSession | None] = relationship(back_populates="episodes")
    agent_events: Mapped[list[AgentEvent]] = relationship(back_populates="episode")
    collisions: Mapped[list[Collision]] = relationship(back_populates="episode")
    deliveries: Mapped[list[Delivery]] = relationship(back_populates="episode")

    __table_args__ = (
        UniqueConstraint(
            "simulation_run_id",
            "episode_number",
            name="uq_episodes_run_episode_number",
        ),
        Index("ix_episodes_training_session_number", "training_session_id", "episode_number"),
        Index("ix_episodes_success", "success"),
    )
