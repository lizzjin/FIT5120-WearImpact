"""Epic 1 application configuration.

Reads all environment variables required by the Epic 1 Local Eco-Shop Navigator.
Used by maps_service (API key, timeout) and the Redis cache layer (URL, TTL).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # Google Maps Platform credentials
    google_maps_api_key: str = ""

    # Outbound HTTP timeout for all Google Places API calls (seconds)
    google_places_timeout_seconds: int = 6

    # Redis connection URL — used by Epic 1 Step 4 place-details cache
    redis_url: str = "redis://localhost:6379"

    # Place details cache TTL: 24 hours keeps Google API quota low
    place_details_cache_ttl: int = 86400

    # CORS origins allowed to call the backend (comma-separated in .env)
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Module-level singleton — import this instance everywhere
settings = Settings()
