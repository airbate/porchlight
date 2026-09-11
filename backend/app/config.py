from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All external knobs live here. .env at the backend/ root overrides defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PorchLight"
    database_path: str = "porchlight.db"

    # Amazon Bedrock
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.amazon.nova-lite-v1:0"

    # Alert policy
    fall_confidence_threshold: float = 0.6
    loitering_confidence_threshold: float = 0.7
    quiet_hours_start: int = 22  # local hour, loitering at night escalates
    quiet_hours_end: int = 7

    # Ring integration (exact endpoints verified in M0 — docs/ring-integration.md)
    ring_simulator_base_url: str | None = None
    ring_poll_interval_seconds: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
