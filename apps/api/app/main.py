from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.api.errors import register_exception_handlers
from app.api.middleware import RequestLoggingMiddleware
from app.api.router import router as api_router
from app.api.v1.stream import ws_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import check_database_connection
from app.schemas.common import APIInfoResponse, HealthResponse

configure_logging()

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


app = FastAPI(
    title="Warehouse AI Simulator API",
    description=(
        "Backend API for the Explainable Multi-Agent Warehouse Robot "
        "Training Simulator."
    ),
    version="0.4.0-dev",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/", response_model=APIInfoResponse, tags=["root"])
def root() -> APIInfoResponse:
    return APIInfoResponse(
        service=getattr(settings, "app_name", "warehouse-ai-simulator-api"),
        version="0.4.0-dev",
        environment=getattr(settings, "environment", "development"),
        modules=API_MODULES,
    )


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    database_status = "healthy" if check_database_connection() else "unhealthy"

    return HealthResponse(
        status="healthy" if database_status == "healthy" else "degraded",
        service=getattr(settings, "app_name", "warehouse-ai-simulator-api"),
        environment=getattr(settings, "environment", "development"),
        database=database_status,
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/metrics", response_class=PlainTextResponse, tags=["metrics"])
def metrics() -> str:
    return "\n".join(
        [
            "# HELP warehouse_api_up API availability",
            "# TYPE warehouse_api_up gauge",
            "warehouse_api_up 1",
            "",
        ]
    )
