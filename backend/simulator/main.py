"""Trigger endpoint: renders a synthetic frame and posts a signed webhook."""

import base64
import hashlib
import hmac
import json
import os
import uuid
from datetime import UTC, datetime

import httpx
from fastapi import FastAPI, HTTPException

from app.fixtures import render_frame
from app.ring_client import SCENARIOS

INGEST_URL = os.getenv("PORCHLIGHT_INGEST_URL", "http://127.0.0.1:8000/events/ingest")
WEBHOOK_SECRET = os.getenv("RING_WEBHOOK_SECRET", "")

app = FastAPI(title="PorchLight Ring Sandbox Simulator (dev)")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "ingest_url": INGEST_URL, "signed": bool(WEBHOOK_SECRET)}


@app.post("/trigger")
def trigger(scenario: str = "visitor") -> dict:
    if scenario not in SCENARIOS:
        raise HTTPException(status_code=400, detail=f"scenario must be one of {SCENARIOS}")

    frame = render_frame(scenario)
    payload = {
        "event_id": uuid.uuid4().hex,
        "occurred_at": datetime.now(UTC).isoformat(),
        "scenario": scenario,
        "image": base64.b64encode(frame).decode(),
        "metadata": {"source": "ring-sandbox-simulator"},
    }
    body = json.dumps(payload).encode()
    headers = {"content-type": "application/json"}
    if WEBHOOK_SECRET:
        sig = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
        headers["x-ring-signature"] = f"sha256={sig}"

    try:
        resp = httpx.post(INGEST_URL, content=body, headers=headers, timeout=30.0)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"cannot reach ingest endpoint {INGEST_URL} — is the backend up? ({exc})",
        ) from exc
    return {
        "simulator": "ok",
        "scenario": scenario,
        "backend_status": resp.status_code,
        "backend_response": _safe_json(resp),
    }


def _safe_json(resp: httpx.Response) -> object:
    try:
        return resp.json()
    except ValueError:
        return resp.text
