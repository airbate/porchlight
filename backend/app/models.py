from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


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
    """Normalised event coming from the Ring simulator / device (or fixtures)."""

    event_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    scenario: str = "unknown"  # simulator scenario label, e.g. "visitor"
    image: bytes | None = None  # doorbell frame, jpeg
    metadata: dict[str, str] = Field(default_factory=dict)


class DoorstepEvent(BaseModel):
    """Stored, analysed event — the unit the family dashboard renders."""

    event_id: str
    occurred_at: datetime
    scenario: str
    analysis: DoorstepAnalysis
    snapshot_ref: str | None = None  # S3 key in live mode
    alerted: bool = False


class Alert(BaseModel):
    level: str  # "critical" | "high" | "none"
    reason: str


class CareDigest(BaseModel):
    date: str  # ISO date
    text: str
    anomaly: str | None = None  # rhythm anomaly note, e.g. "no movement for 24h"
    offline: bool = False
