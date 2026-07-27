"""Application settings.

Loads environment variables from the .env file in a typed way using
pydantic-settings. get_settings() is cached, guaranteeing a single instance
(Singleton) across the application lifetime.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "FastAPI Start Project"
    app_description: str = "A production-ready FastAPI starter project."
    app_version: str = "1.0.0"
    app_env: str = "development"

    # Database
    database_url: str = "sqlite:///./app.db"

    # Security
    secret_key: str
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"


@lru_cache
def get_settings() -> Settings:
    """Return the application settings (cached — created once per lifetime)."""
    return Settings()