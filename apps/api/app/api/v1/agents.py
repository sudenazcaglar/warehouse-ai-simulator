from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/status", response_model=ModuleStatusResponse)
def agents_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="agents",
        status="available",
        detail="Agents API module is registered. Agent endpoints will be added in Phase 4C.",
    )
