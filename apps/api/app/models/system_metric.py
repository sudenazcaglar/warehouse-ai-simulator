from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import MetricSource, enum_values

if TYPE_CHECKING:
    from app.models.simulation_run import SimulationRun
    from app.models.training_session import TrainingSession


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    simulation_run_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=True,
    )
    training_session_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=True,
    )
    metric_name: Mapped[str] = mapped_column(String(120), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_unit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    source: Mapped[MetricSource] = mapped_column(
        Enum(
            MetricSource,
            name="metric_source",
            values_callable=enum_values,
        ),
        nullable=False,
        default=MetricSource.SYSTEM,
        server_default=MetricSource.SYSTEM.value,
    )
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

    simulation_run: Mapped[SimulationRun | None] = relationship(back_populates="system_metrics")
    training_session: Mapped[TrainingSession | None] = relationship(back_populates="system_metrics")

    __table_args__ = (
        Index("ix_system_metrics_name_timestamp", "metric_name", "timestamp"),
        Index("ix_system_metrics_run_timestamp", "simulation_run_id", "timestamp"),
        Index("ix_system_metrics_training_timestamp", "training_session_id", "timestamp"),
        Index("ix_system_metrics_source", "source"),
    )
