from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Index, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.simulation_run import SimulationRun
    from app.models.training_session import TrainingSession


class EnvironmentConfig(TimestampMixin, Base):
    __tablename__ = "environment_configs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    map_name: Mapped[str] = mapped_column(String(120), nullable=False)
    map_version: Mapped[str] = mapped_column(String(40), nullable=False)
    agent_count: Mapped[int] = mapped_column(Integer, nullable=False)
    obstacle_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    shelf_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    delivery_zone_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    config_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    simulation_runs: Mapped[list[SimulationRun]] = relationship(
        back_populates="environment_config",
    )
    training_sessions: Mapped[list[TrainingSession]] = relationship(
        back_populates="environment_config",
    )

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_environment_configs_name_version"),
        Index("ix_environment_configs_map_version", "map_name", "map_version"),
    )
