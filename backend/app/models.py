import base64
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AnalysisCategory(str, Enum):
    VISITOR = "visitor"
    PACKAGE_DELIVERY = "package_delivery"
    LOITERING = "loitering"
    FALL_SUSPECTED = "fall_suspected"
    AMBIENT_NOISE = "ambient_noise"
    UNKNOWN = "unknown"


class DoorstepAnalysis(BaseModel):
    category: AnalysisCategory
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str  # one plain-language sentence, shown to family
    model: str = "offline-stub"
    offline: bool = False  # True when Bedrock was unreachable and we used the stub


class RawRingEvent(BaseModel):
    """Normalised event coming from the Ring sandbox / simulator (or fixtures).

    Over JSON the frame arrives base64-encoded; the validator decodes it so
    `image` is always raw JPEG bytes in Python.
    """

    event_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    scenario: str = "unknown"  # simulator scenario label, e.g. "visitor"
    image: bytes | None = None  # doorbell frame, jpeg
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("image", mode="before")
    @classmethod
    def _decode_base64_frame(cls, v):
        if isinstance(v, str):
            return base64.b64decode(v)
        return v


class DoorstepEvent(BaseModel):
    """Stored, analysed event — the unit the family dashboard renders."""

    event_id: str
    occurred_at: datetime
    scenario: str
    analysis: DoorstepAnalysis
    snapshot_ref: str | None = None  # local:// or s3:// ref in live mode
    alert_level: str = "none"  # "critical" | "high" | "none"
    alert_reason: str = ""
    acknowledged: bool = False


class Alert(BaseModel):
    level: str  # "critical" | "high" | "none"
    reason: str


class CareDigest(BaseModel):
    date: str  # ISO date
    text: str
    anomaly: str | None = None  # rhythm anomaly note, e.g. "no movement for 24h"
    offline: bool = False
