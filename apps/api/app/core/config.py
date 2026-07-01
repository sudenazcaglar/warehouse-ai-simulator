from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "warehouse-ai-simulator"
    environment: str = "development"
    api_version: str = "0.1.0"

    database_url: str = (
        "postgresql+psycopg://warehouse_user:warehouse_password@postgres:5432/warehouse_ai"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
