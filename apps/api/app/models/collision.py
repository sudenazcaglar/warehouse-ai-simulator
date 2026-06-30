from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CollisionType, enum_values

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.episode import Episode
    from app.models.simulation_run import SimulationRun


class Collision(Base):
    __tablename__ = "collisions"

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
    other_agent_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
    )
    collision_type: Mapped[CollisionType] = mapped_column(
        Enum(
            CollisionType,
            name="collision_type",
            values_callable=enum_values,
        ),
        nullable=False,
        default=CollisionType.UNKNOWN,
        server_default=CollisionType.UNKNOWN.value,
    )
    position_x: Mapped[float] = mapped_column(Float, nullable=False)
    position_z: Mapped[float] = mapped_column(Float, nullable=False)
    impact_force: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    simulation_run: Mapped[SimulationRun] = relationship(back_populates="collisions")
    episode: Mapped[Episode | None] = relationship(back_populates="collisions")
    agent: Mapped[Agent] = relationship(
        back_populates="collisions",
        foreign_keys=[agent_id],
    )
    other_agent: Mapped[Agent | None] = relationship(
        foreign_keys=[other_agent_id],
    )

    __table_args__ = (
        Index("ix_collisions_run_timestamp", "simulation_run_id", "timestamp"),
        Index("ix_collisions_agent_timestamp", "agent_id", "timestamp"),
        Index("ix_collisions_type", "collision_type"),
    )
