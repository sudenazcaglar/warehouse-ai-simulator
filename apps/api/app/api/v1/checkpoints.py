from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])


@router.get("/status", response_model=ModuleStatusResponse)
def checkpoints_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="checkpoints",
        status="available",
        detail="Checkpoints API module is registered. Checkpoint endpoints will be added in Phase 4G.",
    )
