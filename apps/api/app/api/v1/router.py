from fastapi import APIRouter

from app.api.v1 import (
    agents,
    checkpoints,
    events,
    explanations,
    metrics,
    models,
    runs,
    stream,
    training,
)
from app.schemas.common import APIInfoResponse
from app.core.config import get_settings

api_router = APIRouter()

settings = get_settings()

API_MODULES = [
    "runs",
    "training",
    "agents",
    "events",
    "metrics",
    "checkpoints",
    "models",
    "explanations",
    "stream",
]


@api_router.get("", response_model=APIInfoResponse, tags=["api"])
def api_v1_info() -> APIInfoResponse:
    return APIInfoResponse(
        service=getattr(settings, "app_name", "warehouse-ai-simulator-api"),
        version="v1",
        environment=getattr(settings, "environment", "development"),
        modules=API_MODULES,
    )


api_router.include_router(runs.router)
api_router.include_router(training.router)
api_router.include_router(agents.router)
api_router.include_router(events.router)
api_router.include_router(metrics.router)
api_router.include_router(checkpoints.router)
api_router.include_router(models.router)
api_router.include_router(explanations.router)
api_router.include_router(stream.router)
