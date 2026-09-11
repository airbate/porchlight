"""Daily Care Digest: the day at the door, in plain language."""

from datetime import UTC, datetime, timedelta

from .analysis.bedrock_vision import BedrockVision
from .models import AnalysisCategory, CareDigest
from .store import EventStore

_DIGEST_PROMPT = """You write the daily "Care Digest" for a family whose elderly parent \
lives alone. Below are today's doorstep events from their Ring doorbell, already analysed.

Events (local times):
{events}

Write a short, warm, factual digest (max 120 words): what happened at the door today, \
anything worth noting (unusual visitors, a package they may not have picked up, \
someone lingering), and close with one reassuring line. No headers, no bullet points."""


def build_daily_digest(
    store: EventStore, vision: BedrockVision, day: datetime | None = None
) -> CareDigest:
    day = day or datetime.now(UTC)
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    events = store.events_between(start, start + timedelta(days=1))

    interesting = [e for e in events if e.analysis.category != AnalysisCategory.AMBIENT_NOISE]
    lines = [f"{e.occurred_at:%H:%M} — {e.analysis.summary}" for e in interesting] or [
        "No notable doorstep activity today."
    ]

    anomaly = _rhythm_anomaly(store, events, day)
    offline = vision.offline
    text = "\n".join(lines)
    try:
        text = vision.summarize_text(_DIGEST_PROMPT.format(events="\n".join(lines)))
    except Exception:  # noqa: BLE001 — digest is a nice-to-have, never a crash
        offline = True

    return CareDigest(date=start.date().isoformat(), text=text, anomaly=anomaly, offline=offline)


def _rhythm_anomaly(store: EventStore, day_events: list, day: datetime) -> str | None:
    """Detect a broken daily rhythm: the door going unusually quiet is itself a signal."""
    interesting = [e for e in day_events if e.analysis.category != AnalysisCategory.AMBIENT_NOISE]
    if interesting:
        return None
    previous = [
        e
        for e in store.events_between(day - timedelta(hours=48), day)
        if e.analysis.category != AnalysisCategory.AMBIENT_NOISE
    ]
    if previous:
        return "No real door activity for over 24 hours — worth a quick check-in call."
    return "A very quiet day at the door — no visitors yet."
