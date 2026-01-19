"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Settings
    api_title: str = "Java CFG/DDG Parser API"
    api_description: str = "A FastAPI service for generating Control Flow and Data Dependence Graphs from Java source code"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Parser Settings
    max_file_size_mb: int = 10
    max_code_length: int = 100000


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
