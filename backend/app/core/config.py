from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-NTDRS"
    environment: str = "development"
    # Default to SQLite for local development and tests so the app can boot without
    # a PostgreSQL server or the optional psycopg dependency installed.
    database_url: str = "sqlite:///./ai_ntdrs.db"
    secret_key: str = "change-me-in-env"
    access_token_expire_minutes: int = 60
    demo_admin_email: str = "admin@ai-ntdrs.local"
    demo_admin_password: str = "ChangeMe123!"
    demo_seed_enabled: bool = True
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    sensor_api_key: str = ""
    flow_model_enabled: bool = True
    flow_model_validated: bool = False
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3.5:4b"
    ollama_timeout_seconds: int = 180

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def validate_production_settings() -> None:
    """Fail closed when production still has development-only credentials or settings."""
    if settings.environment.lower() not in {"production", "prod"}:
        return
    if len(settings.secret_key) < 32 or settings.secret_key == "change-me-in-env":
        raise RuntimeError("Production requires SECRET_KEY with at least 32 characters")
    if settings.secret_key.lower().startswith("replace-with-"):
        raise RuntimeError("Production SECRET_KEY must be randomly generated, not copied from the example")
    if settings.demo_seed_enabled:
        raise RuntimeError("Production requires DEMO_SEED_ENABLED=false")
    if settings.demo_admin_password == "ChangeMe123!":
        raise RuntimeError("Production must not use the demo administrator password")
    if settings.database_url.startswith("sqlite:"):
        raise RuntimeError("Production requires PostgreSQL or another shared database")
    if settings.flow_model_enabled and not settings.flow_model_validated:
        raise RuntimeError("Production cannot use the synthetic demo model; validate an operational model or set FLOW_MODEL_ENABLED=false")
    if len(settings.sensor_api_key) < 32 or settings.sensor_api_key.lower().startswith("replace-with-"):
        raise RuntimeError("Production requires SENSOR_API_KEY with at least 32 randomly generated characters")
    if not settings.cors_origins or any("localhost" in origin or "127.0.0.1" in origin for origin in settings.cors_origins):
        raise RuntimeError("Production CORS_ORIGINS must contain only deployed frontend origins")
