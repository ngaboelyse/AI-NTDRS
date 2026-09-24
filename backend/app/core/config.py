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
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
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
