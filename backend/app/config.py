from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "PayCollection API"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://paycollection:paycollection@127.0.0.1:5432/paycollection",
    )

    JWT_SECRET_KEY: str = Field(
        default="dev-only-change-in-production-use-openssl-rand-hex-32",
        min_length=32,
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = Field(default="ChangeMeAdmin123!", min_length=8)
    ADMIN_DISPLAY_NAME: str = "مدیر سیستم"

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    TRUSTED_HOSTS: str = "localhost,127.0.0.1"

    LOGIN_RATE_LIMIT_MAX_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 900
    API_MAX_PAGE_SIZE: int = 100

    INTERNAL_API_KEY: str | None = None

    BOT_TOKEN: str | None = None
    BOT_HEALTH_URL: str | None = None
    PAYMENT_CARD_NUMBER: str = ""
    UPLOADS_DIR: str = "data/uploads/receipts"
    MIN_TOPUP_RIAL: int = 10_000

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql"):
            raise ValueError("DATABASE_URL must use PostgreSQL with asyncpg driver")
        if "+asyncpg" not in value:
            if value.startswith("postgresql://"):
                return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def trusted_host_list(self) -> list[str]:
        return [host.strip() for host in self.TRUSTED_HOSTS.split(",") if host.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Settings:
        if self.is_production:
            if "dev-only" in self.JWT_SECRET_KEY or "change-me" in self.JWT_SECRET_KEY.lower():
                raise ValueError("JWT_SECRET_KEY must be set to a strong random value in production")
            if self.ADMIN_PASSWORD.lower() in {"admin", "admin123", "password", "changeme"}:
                raise ValueError("ADMIN_PASSWORD is too weak for production")
            if not self.INTERNAL_API_KEY:
                raise ValueError("INTERNAL_API_KEY is required in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
