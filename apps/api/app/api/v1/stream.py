from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter(prefix="/stream", tags=["stream"])


@router.get("/status", response_model=ModuleStatusResponse)
def stream_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="stream",
        status="available",
        detail="Stream API module is registered. WebSocket endpoints will be added in Phase 4E.",
    )
