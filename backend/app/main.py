"""PorchLight API — Ring events in, family-readable care out."""

import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from .analysis.bedrock_vision import BedrockVision
from .config import get_settings
from .digest import build_daily_digest
from .fixtures import render_frame
from .models import CareDigest, RawRingEvent
from .notifiers import Notifier
from .pipeline import Pipeline
from .ring_client import SCENARIOS, verify_signature
from .snapshots import CONTENT_TYPE, SnapshotStore
from .store import EventStore

settings = get_settings()
store = EventStore(settings.database_path)
vision = BedrockVision(settings)
snapshots = SnapshotStore(settings)
notifier = Notifier(settings)
pipeline = Pipeline(store, vision, snapshots, notifier,
                    merge_window_minutes=settings.merge_window_minutes)


@asynccontextmanager
async def lifespan(_: FastAPI):
    print(
        f"{settings.app_name} up — Bedrock model: {settings.bedrock_model_id} | "
        f"snapshots: {snapshots.mode} | webhook auth: "
        f"{'HMAC' if settings.ring_webhook_secret else 'OFF (dev)'}"
    )
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "bedrock_model": settings.bedrock_model_id,
        "bedrock_live": not vision.offline,
        "snapshot_store": snapshots.mode,
        "webhook_auth": bool(settings.ring_webhook_secret),
    }


async def _ingest_body(request: Request) -> RawRingEvent:
    """Shared ingest path: HMAC-verified webhook body → RawRingEvent."""
    body = await request.body()
    if not verify_signature(
        body, request.headers.get(settings.ring_signature_header), settings.ring_webhook_secret
    ):
        raise HTTPException(status_code=401, detail="invalid webhook signature")
    try:
        return RawRingEvent.model_validate_json(body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/events/ingest")
async def ingest_event(request: Request) -> dict:
    """Real adapter endpoint — the Ring sandbox (or dev simulator) posts here."""
    raw = await _ingest_body(request)
    event, alert = pipeline.ingest(raw)
    return {"event": event.model_dump(mode="json"), "alert": alert.model_dump()}


@app.post("/dev/simulate")
def simulate(scenario: str = "visitor") -> dict:
    """Dev/demo helper: render a synthetic frame and push it through the
    signed ingest path (bypasses HTTP but reuses pipeline+snapshot+alerts)."""
    if scenario not in SCENARIOS:
        raise HTTPException(status_code=400, detail=f"scenario must be one of {SCENARIOS}")
    raw = RawRingEvent(
        event_id=uuid.uuid4().hex,
        occurred_at=datetime.now(UTC),
        scenario=scenario,
        image=render_frame(scenario),
        metadata={"source": "dev-simulate"},
    )
    event, alert = pipeline.ingest(raw)
    return {"event": event.model_dump(mode="json"), "alert": alert.model_dump()}


@app.get("/events")
def list_events(limit: int = 100) -> list[dict]:
    return [e.model_dump(mode="json") for e in store.list_events(limit=limit)]


@app.get("/alerts")
def list_alerts(limit: int = 50) -> list[dict]:
    return [e.model_dump(mode="json") for e in store.list_alerts(limit=limit)]


@app.post("/alerts/{event_id}/ack")
def ack_alert(event_id: str) -> dict:
    if not store.ack_alert(event_id):
        raise HTTPException(status_code=404, detail="event not found")
    return {"event_id": event_id, "acknowledged": True}


@app.get("/snapshots/{event_id}")
def get_snapshot(event_id: str):
    """Serve the doorstep frame for an event (file in local mode, presigned
    redirect in S3 mode)."""
    event = store.get_event(event_id)
    if not event or not event.snapshot_ref:
        raise HTTPException(status_code=404, detail="no snapshot for event")
    image, redirect_url = snapshots.resolve(event.snapshot_ref)
    if redirect_url:
        return RedirectResponse(redirect_url)
    if image:
        return FileResponse(snapshots.local_path(event.snapshot_ref), media_type=CONTENT_TYPE)
    raise HTTPException(status_code=404, detail="snapshot unavailable")


@app.get("/digest/today", response_model=CareDigest)
def digest_today() -> CareDigest:
    return build_daily_digest(store, vision, day=datetime.now(UTC))
