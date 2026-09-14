from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VOID API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = Field(default="sqlite:///./.local/void.sqlite3")
    runtime_db_path: str = ".local/void.sqlite3"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_echo: bool = False
    max_upload_bytes: int = 10 * 1024 * 1024
    allowed_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()