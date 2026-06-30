from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import TrainingStatus, enum_values
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.checkpoint import Checkpoint
    from app.models.environment_config import EnvironmentConfig
    from app.models.episode import Episode
    from app.models.model_version import ModelVersion
    from app.models.simulation_run import SimulationRun
    from app.models.system_metric import SystemMetric


class TrainingSession(TimestampMixin, Base):
    __tablename__ = "training_sessions"

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
    environment_config_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("environment_configs.id", ondelete="SET NULL"),
        nullable=True,
    )
    algorithm: Mapped[str] = mapped_column(String(60), nullable=False, server_default="ppo")
    max_steps: Mapped[int] = mapped_column(Integer, nullable=False)
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    learning_rate: Mapped[float] = mapped_column(Float, nullable=False)
    batch_size: Mapped[int] = mapped_column(Integer, nullable=False)
    buffer_size: Mapped[int] = mapped_column(Integer, nullable=False)
    checkpoint_interval: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TrainingStatus] = mapped_column(
        Enum(
            TrainingStatus,
            name="training_status",
            values_callable=enum_values,
        ),
        nullable=False,
        default=TrainingStatus.CREATED,
        server_default=TrainingStatus.CREATED.value,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    simulation_run: Mapped[SimulationRun] = relationship(back_populates="training_sessions")
    environment_config: Mapped[EnvironmentConfig | None] = relationship(
        back_populates="training_sessions",
    )
    episodes: Mapped[list[Episode]] = relationship(back_populates="training_session")
    checkpoints: Mapped[list[Checkpoint]] = relationship(
        back_populates="training_session",
        cascade="all, delete-orphan",
    )
    model_versions: Mapped[list[ModelVersion]] = relationship(
        back_populates="training_session",
        cascade="all, delete-orphan",
    )
    system_metrics: Mapped[list[SystemMetric]] = relationship(back_populates="training_session")

    __table_args__ = (
        Index("ix_training_sessions_run_status", "simulation_run_id", "status"),
        Index("ix_training_sessions_algorithm", "algorithm"),
    )
