from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.episode import Episode
    from app.models.simulation_run import SimulationRun


class Delivery(TimestampMixin, Base):
    __tablename__ = "deliveries"

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
    pickup_location: Mapped[str] = mapped_column(String(120), nullable=False)
    delivery_location: Mapped[str] = mapped_column(String(120), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    reward: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    simulation_run: Mapped[SimulationRun] = relationship(back_populates="deliveries")
    episode: Mapped[Episode | None] = relationship(back_populates="deliveries")
    agent: Mapped[Agent] = relationship(back_populates="deliveries")

    __table_args__ = (
        Index("ix_deliveries_run_success", "simulation_run_id", "success"),
        Index("ix_deliveries_agent_completed_at", "agent_id", "completed_at"),
    )
