from typing import Annotated

from pydantic import BeforeValidator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: str | list[str]) -> list[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.backend", "../.env.backend"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Endpoint Sentinel X"
    ENVIRONMENT: str = "development"

    # CORS configuration
    BACKEND_CORS_ORIGINS: Annotated[list[str], BeforeValidator(parse_cors)] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Database
    # Neon PostgreSQL is postgresql-compatible. Under clean architecture, we use asyncpg driver.
    DATABASE_URL: str = (
        "postgresql+asyncpg://esx_admin:esx_password@localhost:5432/endpoint_sentinel"
    )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    # 64 character randomly generated string in production
    JWT_SECRET_KEY: str = "super_secret_jwt_key_for_sentinel_x_platform_development_123!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            # Auto-correct standard postgres to postgresql+asyncpg for async usage if needed
            if v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            else:
                raise ValueError(
                    "DATABASE_URL must be an asyncpg connection string (postgresql+asyncpg://)"
                )

        # Clean up any unsupported asyncpg parameters like sslmode and channel_binding
        if "?" in v:
            base_url, query_str = v.split("?", 1)
            from urllib.parse import parse_qsl, urlencode

            params = dict(parse_qsl(query_str))

            # Map sslmode to ssl
            if "sslmode" in params:
                ssl_val = params.pop("sslmode")
                if ssl_val in ("require", "prefer", "allow"):
                    params["ssl"] = "require"

            # Remove unsupported options
            params.pop("channel_binding", None)

            # Reconstruct query string
            if params:
                v = f"{base_url}?{urlencode(params)}"
            else:
                v = base_url

        return v


settings = Settings()
