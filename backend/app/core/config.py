from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LeadForge AI"
    environment: str = "development"
    database_url: str = "sqlite:///./leadforge.db"
    overpass_endpoint: str = "https://overpass-api.de/api/interpreter"
    overpass_timeout_seconds: float = 25.0
    google_places_api_key: str = ""
    google_places_endpoint: str = "https://places.googleapis.com/v1/places:searchText"
    google_places_timeout_seconds: float = 12.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LEADFORGE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
