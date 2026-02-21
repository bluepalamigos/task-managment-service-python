from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Task Management Service"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/taskdb"

    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
