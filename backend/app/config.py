import os
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret")
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./mindforge.db")

    GOOGLE_CLIENT_ID: str | None = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str | None = os.environ.get("GOOGLE_CLIENT_SECRET")
    OAUTH_REDIRECT_URI: str = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")

    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "http://localhost:5173")

    OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: str | None = os.environ.get("GOOGLE_API_KEY")

class OAuthUser(BaseModel):
    sub: str
    email: str
    name: str | None = None
    picture: str | None = None

@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore