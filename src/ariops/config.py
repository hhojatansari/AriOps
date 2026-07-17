"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    app_name: str = "ariops"
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ARIOPS_")


settings = Settings()
