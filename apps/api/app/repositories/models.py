from typing import Literal
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

from app.api.errors import ConflictError, NotFoundError
from app.models import Checkpoint, ModelVersion, TrainingSession
from app.schemas.models import ModelVersionCreate
from app.schemas.pagination import PaginationParams

ModelSortBy = Literal[
    "created_at",
    "model_name",
    "version",
    "reward_mean",
    "success_rate",
    "collision_rate",
]
SortOrder = Literal["asc", "desc"]

MODEL_SORT_COLUMNS = {
    "created_at": ModelVersion.created_at,
    "model_name": ModelVersion.model_name,
    "version": ModelVersion.version,
    "reward_mean": ModelVersion.reward_mean,
    "success_rate": ModelVersion.success_rate,
    "collision_rate": ModelVersion.collision_rate,
}


def get_model_version_by_id(db: Session, model_id: UUID) -> ModelVersion | None:
    return db.get(ModelVersion, model_id)


def require_model_version_by_id(db: Session, model_id: UUID) -> ModelVersion:
    model_version = get_model_version_by_id(db, model_id)

    if model_version is None:
        raise NotFoundError(
            message="Model version not found.",
            details={"model_id": str(model_id)},
        )

    return model_version


def require_training_session(db: Session, training_session_id: UUID) -> TrainingSession:
    training_session = db.get(TrainingSession, training_session_id)

    if training_session is None:
        raise NotFoundError(
            message="Training session not found.",
            details={"training_session_id": str(training_session_id)},
        )

    return training_session


def require_checkpoint_if_provided(
    db: Session,
    *,
    checkpoint_id: UUID | None,
    training_session_id: UUID,
) -> Checkpoint | None:
    if checkpoint_id is None:
        return None

    checkpoint = db.get(Checkpoint, checkpoint_id)

    if checkpoint is None:
        raise NotFoundError(
            message="Checkpoint not found.",
            details={"checkpoint_id": str(checkpoint_id)},
        )

    if checkpoint.training_session_id != training_session_id:
        raise ConflictError(
            message="Checkpoint does not belong to the provided training session.",
            code="checkpoint_training_mismatch",
            details={
                "checkpoint_id": str(checkpoint_id),
                "checkpoint_training_session_id": str(checkpoint.training_session_id),
                "provided_training_session_id": str(training_session_id),
            },
        )

    return checkpoint


def ensure_model_version_is_unique(
    db: Session,
    *,
    model_name: str,
    version: str,
) -> None:
    existing_model = (
        db.execute(
            select(ModelVersion).where(
                ModelVersion.model_name == model_name,
                ModelVersion.version == version,
            )
        )
        .scalars()
        .first()
    )

    if existing_model is not None:
        raise ConflictError(
            message="Model version already exists.",
            code="model_version_exists",
            details={
                "model_name": model_name,
                "version": version,
            },
        )


def deactivate_existing_active_models(
    db: Session,
    *,
    model_name: str,
) -> None:
    active_models = (
        db.execute(
            select(ModelVersion).where(
                ModelVersion.model_name == model_name,
                ModelVersion.is_active.is_(True),
            )
        )
        .scalars()
        .all()
    )

    for model_version in active_models:
        model_version.is_active = False


def create_model_version(db: Session, data: ModelVersionCreate) -> ModelVersion:
    require_training_session(db, data.training_session_id)

    require_checkpoint_if_provided(
        db,
        checkpoint_id=data.checkpoint_id,
        training_session_id=data.training_session_id,
    )

    ensure_model_version_is_unique(
        db,
        model_name=data.model_name,
        version=data.version,
    )

    if data.is_active:
        deactivate_existing_active_models(db, model_name=data.model_name)

    model_version = ModelVersion(**data.model_dump())

    db.add(model_version)
    db.commit()
    db.refresh(model_version)

    return model_version


def build_model_filters(
    *,
    training_session_id: UUID | None = None,
    checkpoint_id: UUID | None = None,
    model_name: str | None = None,
    version: str | None = None,
    is_active: bool | None = None,
) -> list:
    filters = []

    if training_session_id is not None:
        filters.append(ModelVersion.training_session_id == training_session_id)

    if checkpoint_id is not None:
        filters.append(ModelVersion.checkpoint_id == checkpoint_id)

    if model_name:
        filters.append(ModelVersion.model_name.ilike(f"%{model_name}%"))

    if version:
        filters.append(ModelVersion.version.ilike(f"%{version}%"))

    if is_active is not None:
        filters.append(ModelVersion.is_active.is_(is_active))

    return filters


def apply_model_sorting(
    query: Select[tuple[ModelVersion]],
    *,
    sort_by: ModelSortBy,
    sort_order: SortOrder,
) -> Select[tuple[ModelVersion]]:
    column = MODEL_SORT_COLUMNS[sort_by]
    order_clause = asc(column) if sort_order == "asc" else desc(column)

    return query.order_by(order_clause)


def list_model_versions(
    db: Session,
    *,
    pagination: PaginationParams,
    training_session_id: UUID | None = None,
    checkpoint_id: UUID | None = None,
    model_name: str | None = None,
    version: str | None = None,
    is_active: bool | None = None,
    sort_by: ModelSortBy = "created_at",
    sort_order: SortOrder = "desc",
) -> tuple[list[ModelVersion], int]:
    filters = build_model_filters(
        training_session_id=training_session_id,
        checkpoint_id=checkpoint_id,
        model_name=model_name,
        version=version,
        is_active=is_active,
    )

    total_query = select(func.count()).select_from(ModelVersion)

    if filters:
        total_query = total_query.where(*filters)

    total = int(db.execute(total_query).scalar_one())

    query = select(ModelVersion)

    if filters:
        query = query.where(*filters)

    query = apply_model_sorting(
        query,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    query = query.offset(pagination.offset).limit(pagination.limit)

    items = db.execute(query).scalars().all()

    return list(items), total
