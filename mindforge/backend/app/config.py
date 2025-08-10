from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./mindforge.db"
    google_client_id: str | None = None
    google_client_secret: str | None = None
    jwt_secret_key: str = "change_me"
    redis_url: str | None = None
    frontend_origin: str = "http://localhost:5173"
    allowed_origins: List[str] = ["http://localhost:5173"]
    log_level: str = "INFO"
    session_secret: str = "session_secret_change_me"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()