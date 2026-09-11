"""PorchLight API — Ring events in, family-readable care out."""

import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI

from .analysis.bedrock_vision import BedrockVision
from .config import get_settings
from .digest import build_daily_digest
from .models import CareDigest, RawRingEvent
from .pipeline import Pipeline
from .ring_client import SCENARIOS, FixtureSource
from .store import EventStore

settings = get_settings()
store = EventStore(settings.database_path)
vision = BedrockVision(settings)
pipeline = Pipeline(store, vision)
fixtures = FixtureSource()


@asynccontextmanager
async def lifespan(_: FastAPI):
    print(f"{settings.app_name} up — Bedrock model: {settings.bedrock_model_id} "
          f"(offline stub active until first successful call)")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "bedrock_model": settings.bedrock_model_id,
        "bedrock_live": not vision.offline,
    }


@app.post("/dev/simulate")
def simulate(scenario: str = "visitor") -> dict:
    """Dev helper: push one synthetic Ring event through the full pipeline."""
    if scenario not in SCENARIOS:
        return {"error": f"scenario must be one of {SCENARIOS}"}
    raw = RawRingEvent(
        event_id=uuid.uuid4().hex, occurred_at=datetime.now(UTC), scenario=scenario
    )
    event, alert = pipeline.ingest(raw)
    return {"event": event.model_dump(mode="json"), "alert": alert.model_dump()}


@app.post("/events/ingest")
def ingest(raw: RawRingEvent) -> dict:
    """Real adapter endpoint — RingSimulatorSource posts here after M0 wiring."""
    event, alert = pipeline.ingest(raw)
    return {"event": event.model_dump(mode="json"), "alert": alert.model_dump()}


@app.get("/events")
def list_events(limit: int = 100) -> list[dict]:
    return [e.model_dump(mode="json") for e in store.list_events(limit=limit)]


@app.get("/digest/today", response_model=CareDigest)
def digest_today() -> CareDigest:
    return build_daily_digest(store, vision, day=datetime.now(UTC))
