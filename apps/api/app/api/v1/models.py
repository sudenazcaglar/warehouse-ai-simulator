from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_pagination, validate_uuid
from app.repositories import models as model_repository
from app.schemas.common import ModuleStatusResponse
from app.schemas.models import (
    ModelVersionCreate,
    ModelVersionListResponse,
    ModelVersionResponse,
)
from app.schemas.pagination import PaginationParams

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/status", response_model=ModuleStatusResponse)
def models_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="models",
        status="available",
        detail="Model registry API module is registered and database-backed endpoints are available.",
    )


@router.post(
    "",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_model_version(
    payload: ModelVersionCreate,
    db: Session = Depends(get_db),
) -> ModelVersionResponse:
    model_version = model_repository.create_model_version(db, payload)
    return ModelVersionResponse.model_validate(model_version)


@router.get("", response_model=ModelVersionListResponse)
def list_model_versions(
    pagination: PaginationParams = Depends(get_pagination),
    training_session_id: str | None = Query(default=None),
    checkpoint_id: str | None = Query(default=None),
    model_name: str | None = Query(default=None),
    version: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    sort_by: Literal[
        "created_at",
        "model_name",
        "version",
        "reward_mean",
        "success_rate",
        "collision_rate",
    ] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> ModelVersionListResponse:
    parsed_training_session_id = (
        validate_uuid(training_session_id, "training_session_id")
        if training_session_id is not None
        else None
    )
    parsed_checkpoint_id = (
        validate_uuid(checkpoint_id, "checkpoint_id")
        if checkpoint_id is not None
        else None
    )

    items, total = model_repository.list_model_versions(
        db,
        pagination=pagination,
        training_session_id=parsed_training_session_id,
        checkpoint_id=parsed_checkpoint_id,
        model_name=model_name,
        version=version,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return ModelVersionListResponse.create(
        items=[ModelVersionResponse.model_validate(item) for item in items],
        total=total,
        pagination=pagination,
    )


@router.get("/active", response_model=ModelVersionListResponse)
def list_active_models(
    pagination: PaginationParams = Depends(get_pagination),
    model_name: str | None = Query(default=None),
    sort_by: Literal[
        "created_at",
        "model_name",
        "version",
        "reward_mean",
        "success_rate",
        "collision_rate",
    ] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> ModelVersionListResponse:
    items, total = model_repository.list_model_versions(
        db,
        pagination=pagination,
        model_name=model_name,
        is_active=True,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return ModelVersionListResponse.create(
        items=[ModelVersionResponse.model_validate(item) for item in items],
        total=total,
        pagination=pagination,
    )


@router.get("/{model_id}", response_model=ModelVersionResponse)
def get_model_version(
    model_id: str,
    db: Session = Depends(get_db),
) -> ModelVersionResponse:
    parsed_model_id = validate_uuid(model_id, "model_id")
    model_version = model_repository.require_model_version_by_id(
        db,
        parsed_model_id,
    )

    return ModelVersionResponse.model_validate(model_version)
