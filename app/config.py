from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from .core.config import Settings, settings


class Settings(BaseSettings):
    # === Environnement ===
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    # === Sécurité / Auth ===
    SECRET_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === Base de données PostgreSQL ===
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None  # construit automatiquement si absent

    # === Redis / Celery ===
    REDIS_URL: Optional[str] = None
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # === Réseau / Sécurité ===
    CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    LOG_LEVEL: str = "INFO"

    # === Base locale alternative ===
    USE_SQLITE: bool = False

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,   # cohérent avec MAJUSCULES du .env
        extra="ignore",        # ignore les clés inconnues
    )

    # Normalisation de CORS_ORIGINS
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _coerce_cors(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            try:
                import json
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [item.strip() for item in s.split(",") if item.strip()]
        return v

    # Générateur d’URL DB
    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.USE_SQLITE:
            return "sqlite:///./konan.db"
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
