from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/status", response_model=ModuleStatusResponse)
def training_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="training",
        status="available",
        detail="Training API module is registered. Training endpoints will be added in Phase 4F.",
    )
