from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_JWT_SECRET = "dev-only-secret-change-me-0123456789"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "FastAPI Service"
    environment: str = "development"
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/app_dev"
    )
    jwt_secret: str = Field(default=DEV_JWT_SECRET, min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=720, ge=1)
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"
    docs_enabled: bool = True
    seed_admin_email: str = ""
    seed_admin_password: str = ""
    seed_admin_name: str = "管理员"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @field_validator("jwt_secret")
    @classmethod
    def validate_secret_length(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("JWT_SECRET 至少 32 位")
        return value

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret == DEV_JWT_SECRET:
            raise ValueError("生产环境必须设置真实的 JWT_SECRET")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
