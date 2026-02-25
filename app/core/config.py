"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings populated from environment variables and .env file.

    Attributes:
        app_name: Display name used in OpenAPI docs.
        debug: Enable debug mode.
        database_url: Async PostgreSQL connection string.
        log_level: Python logging level name (e.g. DEBUG, INFO, WARNING).
    """

    app_name: str = "Task Management Service"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/taskdb"

    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
