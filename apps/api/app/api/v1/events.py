from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/status", response_model=ModuleStatusResponse)
def events_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="events",
        status="available",
        detail="Events API module is registered. Event ingestion will be added in Phase 4D.",
    )
