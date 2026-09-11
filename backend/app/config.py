from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All external knobs live here. .env at the backend/ root overrides defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PorchLight"
    database_path: str = "porchlight.db"

    # CORS: the family dashboard origin
    frontend_origin: str = "http://127.0.0.1:5173"

    # Amazon Bedrock
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.amazon.nova-lite-v1:0"

    # Snapshots: S3 bucket name enables S3 storage, otherwise local dir
    s3_bucket: str | None = None
    snapshots_dir: str = "snapshots"
    snapshot_presign_seconds: int = 3600

    # Alert fan-out: optional outbound webhook (e.g. push/email bridge)
    alert_webhook_url: str | None = None

    # Ring integration (exact endpoints verified in M0 — docs/ring-integration.md).
    # Webhooks from the Ring sandbox carry an HMAC signature we verify.
    ring_webhook_secret: str | None = None  # None = verification off (local dev only)
    ring_signature_header: str = "x-ring-signature"
    ring_api_base_url: str | None = None  # sandbox base URL once M0 confirms
    ring_bearer_token: str | None = None

    # Alert policy
    fall_confidence_threshold: float = 0.6
    loitering_confidence_threshold: float = 0.7
    quiet_hours_start: int = 22  # local hour, loitering at night escalates
    quiet_hours_end: int = 7


@lru_cache
def get_settings() -> Settings:
    return Settings()
