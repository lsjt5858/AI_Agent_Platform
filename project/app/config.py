"""
Configuration management module using pydantic-settings.
Handles LLM API, database connection, and other environment variables.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = "AI Agent Platform"
    debug: bool = False

    # Database settings
    database_url: str = "sqlite+aiosqlite:///./ai_agent.db"

    # LLM API settings
    llm_api_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_api_key: Optional[str] = None
    llm_model: str = "qwen-turbo"
    llm_timeout: int = 30  # seconds

    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
