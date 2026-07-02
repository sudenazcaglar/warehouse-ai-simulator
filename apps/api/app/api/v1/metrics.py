from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/status", response_model=ModuleStatusResponse)
def metrics_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="metrics",
        status="available",
        detail="Metrics API module is registered. Metric ingestion will be added in Phase 4E.",
    )
