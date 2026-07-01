from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.checkpoint import Checkpoint
    from app.models.training_session import TrainingSession


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    training_session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    checkpoint_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("checkpoints.id", ondelete="SET NULL"),
        nullable=True,
    )
    model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(60), nullable=False, server_default="ppo")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    onnx_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reward_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    success_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    collision_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    training_session: Mapped[TrainingSession] = relationship(back_populates="model_versions")
    checkpoint: Mapped[Checkpoint | None] = relationship(back_populates="model_versions")

    __table_args__ = (
        UniqueConstraint("model_name", "version", name="uq_model_versions_name_version"),
        Index("ix_model_versions_active", "is_active"),
        Index("ix_model_versions_training_session", "training_session_id"),
    )
