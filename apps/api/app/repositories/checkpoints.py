from typing import Literal
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

from app.api.errors import ConflictError, NotFoundError
from app.models import Checkpoint, TrainingSession
from app.schemas.checkpoints import CheckpointCreate
from app.schemas.pagination import PaginationParams

CheckpointSortBy = Literal[
    "created_at",
    "step",
    "reward_mean",
    "success_rate",
    "collision_rate",
]
SortOrder = Literal["asc", "desc"]

CHECKPOINT_SORT_COLUMNS = {
    "created_at": Checkpoint.created_at,
    "step": Checkpoint.step,
    "reward_mean": Checkpoint.reward_mean,
    "success_rate": Checkpoint.success_rate,
    "collision_rate": Checkpoint.collision_rate,
}


def get_checkpoint_by_id(db: Session, checkpoint_id: UUID) -> Checkpoint | None:
    return db.get(Checkpoint, checkpoint_id)


def require_checkpoint_by_id(db: Session, checkpoint_id: UUID) -> Checkpoint:
    checkpoint = get_checkpoint_by_id(db, checkpoint_id)

    if checkpoint is None:
        raise NotFoundError(
            message="Checkpoint not found.",
            details={"checkpoint_id": str(checkpoint_id)},
        )

    return checkpoint


def require_training_session(db: Session, training_session_id: UUID) -> TrainingSession:
    training_session = db.get(TrainingSession, training_session_id)

    if training_session is None:
        raise NotFoundError(
            message="Training session not found.",
            details={"training_session_id": str(training_session_id)},
        )

    return training_session


def ensure_checkpoint_step_is_unique(
    db: Session,
    *,
    training_session_id: UUID,
    step: int,
) -> None:
    existing_checkpoint = (
        db.execute(
            select(Checkpoint).where(
                Checkpoint.training_session_id == training_session_id,
                Checkpoint.step == step,
            )
        )
        .scalars()
        .first()
    )

    if existing_checkpoint is not None:
        raise ConflictError(
            message="Checkpoint already exists for this training session and step.",
            code="checkpoint_step_exists",
            details={
                "training_session_id": str(training_session_id),
                "step": step,
            },
        )


def unset_existing_best_checkpoints(
    db: Session,
    *,
    training_session_id: UUID,
) -> None:
    existing_best_checkpoints = (
        db.execute(
            select(Checkpoint).where(
                Checkpoint.training_session_id == training_session_id,
                Checkpoint.is_best.is_(True),
            )
        )
        .scalars()
        .all()
    )

    for checkpoint in existing_best_checkpoints:
        checkpoint.is_best = False


def create_checkpoint(db: Session, data: CheckpointCreate) -> Checkpoint:
    require_training_session(db, data.training_session_id)

    ensure_checkpoint_step_is_unique(
        db,
        training_session_id=data.training_session_id,
        step=data.step,
    )

    if data.is_best:
        unset_existing_best_checkpoints(
            db,
            training_session_id=data.training_session_id,
        )

    checkpoint = Checkpoint(**data.model_dump())

    db.add(checkpoint)
    db.commit()
    db.refresh(checkpoint)

    return checkpoint


def build_checkpoint_filters(
    *,
    training_session_id: UUID | None = None,
    is_best: bool | None = None,
) -> list:
    filters = []

    if training_session_id is not None:
        filters.append(Checkpoint.training_session_id == training_session_id)

    if is_best is not None:
        filters.append(Checkpoint.is_best.is_(is_best))

    return filters


def apply_checkpoint_sorting(
    query: Select[tuple[Checkpoint]],
    *,
    sort_by: CheckpointSortBy,
    sort_order: SortOrder,
) -> Select[tuple[Checkpoint]]:
    column = CHECKPOINT_SORT_COLUMNS[sort_by]
    order_clause = asc(column) if sort_order == "asc" else desc(column)

    return query.order_by(order_clause)


def list_checkpoints(
    db: Session,
    *,
    pagination: PaginationParams,
    training_session_id: UUID | None = None,
    is_best: bool | None = None,
    sort_by: CheckpointSortBy = "created_at",
    sort_order: SortOrder = "desc",
) -> tuple[list[Checkpoint], int]:
    filters = build_checkpoint_filters(
        training_session_id=training_session_id,
        is_best=is_best,
    )

    total_query = select(func.count()).select_from(Checkpoint)

    if filters:
        total_query = total_query.where(*filters)

    total = int(db.execute(total_query).scalar_one())

    query = select(Checkpoint)

    if filters:
        query = query.where(*filters)

    query = apply_checkpoint_sorting(
        query,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    query = query.offset(pagination.offset).limit(pagination.limit)

    items = db.execute(query).scalars().all()

    return list(items), total


def get_best_checkpoint(
    db: Session,
    *,
    training_session_id: UUID | None = None,
) -> Checkpoint:
    if training_session_id is not None:
        require_training_session(db, training_session_id)

    query = select(Checkpoint).where(Checkpoint.is_best.is_(True))

    if training_session_id is not None:
        query = query.where(Checkpoint.training_session_id == training_session_id)

    query = query.order_by(
        desc(Checkpoint.reward_mean).nullslast(),
        desc(Checkpoint.success_rate).nullslast(),
        asc(Checkpoint.collision_rate).nullslast(),
        desc(Checkpoint.created_at),
    )

    checkpoint = db.execute(query).scalars().first()

    if checkpoint is None:
        raise NotFoundError(
            message="Best checkpoint not found.",
            details={
                "training_session_id": str(training_session_id)
                if training_session_id is not None
                else None,
            },
        )

    return checkpoint
