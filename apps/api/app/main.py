from datetime import datetime, timezone

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "warehouse-ai-simulator"
    environment: str = "development"
    api_version: str = "0.1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

app = FastAPI(
    title="Warehouse AI Simulator API",
    description="Backend API for simulation runs, training metrics, checkpoints, and LLM explanations.",
    version=settings.api_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {
        "project": settings.project_name,
        "service": "api",
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
        "service": "api",
        "project": settings.project_name,
        "environment": settings.environment,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics")
def metrics() -> Response:
    content = "\n".join(
        [
            "# HELP warehouse_api_up API availability status.",
            "# TYPE warehouse_api_up gauge",
            "warehouse_api_up 1",
            "# HELP warehouse_api_info Static API information.",
            "# TYPE warehouse_api_info gauge",
            f'warehouse_api_info{{project="{settings.project_name}",environment="{settings.environment}"}} 1',
            "",
        ]
    )

    return Response(content=content, media_type="text/plain")
