import os
from dataclasses import dataclass


def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return ["*"]

    origins = [origin.strip() for origin in value.split(",") if origin.strip()]
    return origins or ["*"]


@dataclass(frozen=True)
class Settings:
    app_env: str
    cors_origins: list[str]


def load_settings() -> Settings:
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    cors_origins = _parse_origins(os.getenv("CORS_ORIGINS"))

    if app_env == "production" and cors_origins == ["*"]:
        raise RuntimeError(
            "CORS_ORIGINS must be explicitly configured when APP_ENV=production"
        )

    return Settings(
        app_env=app_env,
        cors_origins=cors_origins,
    )


settings = load_settings()
