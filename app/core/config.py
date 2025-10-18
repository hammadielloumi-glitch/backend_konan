from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json
import os

class Settings(BaseSettings):
    APP_ENV: str = os.getenv("APP_ENV", "production")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "default_jwt_secret")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Base de données
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:pass123@localhost:5432/konan_db"
    )

    # Services IA
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "./chroma_store")

    # Réseau
    CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
    EXPO_PUBLIC_API_URL: str = os.getenv("EXPO_PUBLIC_API_URL", "http://localhost:8000")
    EXPO_PUBLIC_API_BASE: str = os.getenv("EXPO_PUBLIC_API_BASE", "http://192.168.0.133:8000")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _coerce_cors(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v.strip())
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @property
    def db_url(self) -> str:
        return self.DATABASE_URL

settings = Settings()
