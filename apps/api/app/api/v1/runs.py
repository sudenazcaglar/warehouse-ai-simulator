from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/status", response_model=ModuleStatusResponse)
def runs_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="runs",
        status="available",
        detail="Runs API module is registered. CRUD endpoints will be added in Phase 4C.",
    )
