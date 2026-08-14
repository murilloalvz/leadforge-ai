from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LeadForge AI"
    environment: str = "development"
    database_url: str = "sqlite:///./leadforge.db"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LEADFORGE_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
