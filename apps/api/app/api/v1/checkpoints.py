from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_pagination, validate_uuid
from app.repositories import checkpoints as checkpoint_repository
from app.schemas.checkpoints import (
    CheckpointCreate,
    CheckpointListResponse,
    CheckpointResponse,
)
from app.schemas.common import ModuleStatusResponse
from app.schemas.pagination import PaginationParams

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])


@router.get("/status", response_model=ModuleStatusResponse)
def checkpoints_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="checkpoints",
        status="available",
        detail="Checkpoint API module is registered and database-backed endpoints are available.",
    )


@router.post(
    "",
    response_model=CheckpointResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_checkpoint(
    payload: CheckpointCreate,
    db: Session = Depends(get_db),
) -> CheckpointResponse:
    checkpoint = checkpoint_repository.create_checkpoint(db, payload)
    return CheckpointResponse.model_validate(checkpoint)


@router.get("", response_model=CheckpointListResponse)
def list_checkpoints(
    pagination: PaginationParams = Depends(get_pagination),
    training_session_id: str | None = Query(default=None),
    is_best: bool | None = Query(default=None),
    sort_by: Literal[
        "created_at",
        "step",
        "reward_mean",
        "success_rate",
        "collision_rate",
    ] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> CheckpointListResponse:
    parsed_training_session_id = (
        validate_uuid(training_session_id, "training_session_id")
        if training_session_id is not None
        else None
    )

    items, total = checkpoint_repository.list_checkpoints(
        db,
        pagination=pagination,
        training_session_id=parsed_training_session_id,
        is_best=is_best,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return CheckpointListResponse.create(
        items=[CheckpointResponse.model_validate(item) for item in items],
        total=total,
        pagination=pagination,
    )


@router.get("/best", response_model=CheckpointResponse)
def get_best_checkpoint(
    training_session_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> CheckpointResponse:
    parsed_training_session_id = (
        validate_uuid(training_session_id, "training_session_id")
        if training_session_id is not None
        else None
    )

    checkpoint = checkpoint_repository.get_best_checkpoint(
        db,
        training_session_id=parsed_training_session_id,
    )

    return CheckpointResponse.model_validate(checkpoint)


@router.get("/{checkpoint_id}", response_model=CheckpointResponse)
def get_checkpoint(
    checkpoint_id: str,
    db: Session = Depends(get_db),
) -> CheckpointResponse:
    parsed_checkpoint_id = validate_uuid(checkpoint_id, "checkpoint_id")
    checkpoint = checkpoint_repository.require_checkpoint_by_id(
        db,
        parsed_checkpoint_id,
    )

    return CheckpointResponse.model_validate(checkpoint)
