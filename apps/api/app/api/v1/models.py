from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/status", response_model=ModuleStatusResponse)
def models_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="models",
        status="available",
        detail="Model registry API module is registered. Model endpoints will be added in Phase 4G.",
    )
