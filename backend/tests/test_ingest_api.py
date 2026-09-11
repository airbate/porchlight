"""HTTP-level tests: signed webhook ingest, snapshot serving, alert ack flow."""

import base64
import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.fixtures import render_frame
from app.main import app
from app.main import settings as app_settings

SECRET = "test-webhook-secret"


def _signed_payload(scenario: str) -> tuple[bytes, dict[str, str]]:
    payload = {
        "event_id": uuid.uuid4().hex,
        "occurred_at": datetime.now(UTC).isoformat(),
        "scenario": scenario,
        "image": base64.b64encode(render_frame(scenario)).decode(),
        "metadata": {"source": "pytest"},
    }
    body = json.dumps(payload).encode()
    sig = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return body, {"content-type": "application/json", "x-ring-signature": f"sha256={sig}"}


def test_webhook_rejects_bad_signature():
    app_settings.ring_webhook_secret = SECRET
    try:
        with TestClient(app) as client:
            body, headers = _signed_payload("visitor")
            wrong = {**headers, "x-ring-signature": "sha256=" + "0" * 64}
            assert client.post("/events/ingest", content=body, headers=wrong).status_code == 401
            unsigned = {"content-type": "application/json"}
            assert client.post("/events/ingest", content=body, headers=unsigned).status_code == 401
    finally:
        app_settings.ring_webhook_secret = None


def test_webhook_accepts_signed_event_with_snapshot_and_ack():
    app_settings.ring_webhook_secret = SECRET
    try:
        with TestClient(app) as client:
            body, headers = _signed_payload("fall_suspected")
            res = client.post("/events/ingest", content=body, headers=headers)
            assert res.status_code == 200
            data = res.json()
            assert data["alert"]["level"] == "critical"
            event = data["event"]
            assert event["snapshot_ref"]

            snap = client.get(f"/snapshots/{event['event_id']}")
            assert snap.status_code == 200
            assert snap.headers["content-type"] == "image/jpeg"
            assert snap.content[:2] == b"\xff\xd8"

            alerts = client.get("/alerts").json()
            assert any(a["event_id"] == event["event_id"] for a in alerts)

            ack = client.post(f"/alerts/{event['event_id']}/ack")
            assert ack.status_code == 200
            assert ack.json()["acknowledged"] is True
            assert client.post(f"/alerts/{event['event_id']}/ack").status_code == 404
    finally:
        app_settings.ring_webhook_secret = None


def test_dev_simulate_endpoint():
    with TestClient(app) as client:
        res = client.post("/dev/simulate?scenario=visitor")
        assert res.status_code == 200
        event = res.json()["event"]
        assert event["analysis"]["category"] == "visitor"
        assert event["snapshot_ref"]

        bad = client.post("/dev/simulate?scenario=meteor")
        assert bad.status_code == 400
