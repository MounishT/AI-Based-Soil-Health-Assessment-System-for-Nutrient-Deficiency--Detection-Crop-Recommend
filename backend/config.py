"""
config.py
---------
Centralised application configuration loaded from environment variables.
Uses pydantic-settings for type-safe, validated settings.

Priority order:
  1. Actual environment variables
  2. Values in the .env file
  3. Default values defined below
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings — all values can be overridden via .env"""

    # ── Application ────────────────────────────────────────────────────────
    APP_NAME: str = "AI-Based Soil Health Assessment System"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "A production-ready FastAPI backend for soil health assessment, "
        "crop recommendation, and fertilizer prediction using machine learning."
    )
    DEBUG: bool = False

    # ── Database ───────────────────────────────────────────────────────────
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "soil_health_db"

    # Constructed DATABASE_URL (can also be overridden directly in .env)
    DATABASE_URL: str = ""

    # Log SQL queries — set True only in development
    DB_ECHO: bool = False

    # ── File Storage ────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: list[str] = ["jpg", "jpeg", "png", "webp", "bmp"]
    MAX_FILE_SIZE_MB: int = 10   # Maximum upload size in megabytes

    # ── ML Model Paths ──────────────────────────────────────────────────────
    CROP_MODEL_PATH: str = "models/crop_model.pkl"
    FERTILIZER_MODEL_PATH: str = "models/fertilizer_model.pkl"

    # ── CORS ────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]   # Restrict in production

    # ── Authentication (JWT) ──────────────────────────────────────────────
    JWT_SECRET_KEY: str = "soil-health-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── Logging ─────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # Pydantic-settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",           # ignore unknown env vars
    )

    def model_post_init(self, __context) -> None:
        """
        Build DATABASE_URL from components if not explicitly provided.
        Runs automatically after __init__.
        """
        if not self.DATABASE_URL:
            object.__setattr__(
                self,
                "DATABASE_URL",
                (
                    f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                    f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
                ),
            )


# ─── Singleton Settings Instance ──────────────────────────────────────────────
# @lru_cache ensures Settings is loaded only once (avoids repeated .env reads)
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Convenience alias used throughout the app:  from backend.config import settings
settings: Settings = get_settings()
