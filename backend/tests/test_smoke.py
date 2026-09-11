from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.alerts import evaluate_alert
from app.analysis.bedrock_vision import BedrockVision
from app.config import Settings
from app.digest import build_daily_digest
from app.fixtures import render_frame
from app.main import app
from app.models import AnalysisCategory, DoorstepAnalysis, DoorstepEvent, RawRingEvent
from app.notifiers import Notifier
from app.pipeline import Pipeline
from app.ring_client import verify_signature
from app.snapshots import SnapshotStore
from app.store import EventStore


def _offline_pipeline(tmp_path):
    store = EventStore(str(tmp_path / "t.db"))
    vision = BedrockVision(Settings(aws_region="us-east-1"))
    vision._offline = True  # force the stub so tests never touch AWS
    snapshots = SnapshotStore(Settings(snapshots_dir=str(tmp_path / "snaps")))
    pipeline = Pipeline(store, vision, snapshots, Notifier(Settings()))
    return store, pipeline


def test_health_offline_mode():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "ok"
        assert "bedrock_live" in body


def test_simulate_pipeline_end_to_end(tmp_path):
    store, pipeline = _offline_pipeline(tmp_path)
    event, alert = pipeline.ingest(
        RawRingEvent(
            event_id="e1",
            occurred_at=datetime.now(UTC),
            scenario="package_delivery",
            image=render_frame("package_delivery"),
        )
    )

    assert event.analysis.category == AnalysisCategory.PACKAGE_DELIVERY
    assert event.analysis.offline is True
    assert alert.level == "none"
    assert event.snapshot_ref, "fixture frame should be stored as a snapshot"
    assert len(store.list_events()) == 1


def test_fall_alert_rule():
    analysis = DoorstepAnalysis(
        category=AnalysisCategory.FALL_SUSPECTED, confidence=0.9, summary="person on ground"
    )
    alert = evaluate_alert(analysis, occurred_at=datetime(2026, 10, 1, 14, 0, tzinfo=UTC))
    assert alert.level == "critical"

    low_conf = DoorstepAnalysis(
        category=AnalysisCategory.FALL_SUSPECTED, confidence=0.3, summary="unclear"
    )
    assert evaluate_alert(low_conf).level == "none"


def test_night_loitering_escalates():
    analysis = DoorstepAnalysis(
        category=AnalysisCategory.LOITERING, confidence=0.85, summary="someone pacing"
    )
    day = evaluate_alert(analysis, occurred_at=datetime(2026, 10, 1, 14, 0, tzinfo=UTC))
    night = evaluate_alert(analysis, occurred_at=datetime(2026, 10, 1, 23, 30, tzinfo=UTC))
    assert day.level == "none"
    assert night.level == "high"


def test_offline_stub_confidence_drives_alerts(tmp_path):
    """Offline stub confidence must be high enough for alert rules to evaluate
    the live way — otherwise the demo never shows the alert flow."""
    store, pipeline = _offline_pipeline(tmp_path)
    event, alert = pipeline.ingest(
        RawRingEvent(event_id="e3", occurred_at=datetime.now(UTC), scenario="fall_suspected")
    )
    assert alert.level == "critical"
    assert event.alert_level == "critical"
    assert store.list_alerts()[0].event_id == "e3"


def test_store_roundtrip(tmp_path):
    store = EventStore(str(tmp_path / "t.db"))
    analysis = DoorstepAnalysis(
        category=AnalysisCategory.VISITOR, confidence=0.8, summary="neighbour at door"
    )
    event = DoorstepEvent(
        event_id="e2",
        occurred_at=datetime.now(UTC) - timedelta(minutes=5),
        scenario="visitor",
        analysis=analysis,
    )
    store.save_event(event)
    loaded = store.list_events()
    assert loaded[0].event_id == "e2"
    assert loaded[0].analysis.category == AnalysisCategory.VISITOR


def test_webhook_signature():
    body = b'{"event_id": "x"}'
    assert verify_signature(body, None, None)  # dev mode: no secret configured
    sig = "sha256=" + __import__("hmac").new(b"s", body, __import__("hashlib").sha256).hexdigest()
    assert verify_signature(body, sig, "s")
    assert not verify_signature(body, None, "s")
    assert not verify_signature(body, "sha256=deadbeef", "s")


def test_fixture_frames_are_jpeg():
    for scenario in ("visitor", "package_delivery", "loitering", "fall_suspected", "ambient_noise"):
        frame = render_frame(scenario)
        assert frame[:2] == b"\xff\xd8", f"{scenario} frame should be a JPEG"


def test_duplicate_events_merge_within_window(tmp_path):
    """Same category inside the merge window → one entry with repeat_count, no new alert."""
    store, pipeline = _offline_pipeline(tmp_path)
    now = datetime.now(UTC)

    e1, _ = pipeline.ingest(RawRingEvent(event_id="m1", occurred_at=now, scenario="visitor"))
    e2, a2 = pipeline.ingest(
        RawRingEvent(event_id="m2", occurred_at=now + timedelta(minutes=3), scenario="visitor")
    )
    assert e2.event_id == e1.event_id
    assert e2.repeat_count == 2
    assert a2.level == "none"
    assert len(store.list_events()) == 1

    e3, _ = pipeline.ingest(
        RawRingEvent(event_id="m3", occurred_at=now + timedelta(minutes=4), scenario="package_delivery")
    )
    assert e3.event_id == "m3"
    assert e3.repeat_count == 1
    assert len(store.list_events()) == 2


def test_digest_rhythm_anomaly(tmp_path):
    store, pipeline = _offline_pipeline(tmp_path)
    vision = BedrockVision(Settings(aws_region="us-east-1"))
    vision._offline = True

    now = datetime.now(UTC)
    # yesterday: real activity; today: nothing
    yesterday = pipeline.ingest(
        RawRingEvent(
            event_id="y1",
            occurred_at=now - timedelta(hours=30),
            scenario="visitor",
        )
    )
    assert yesterday[0].event_id == "y1"

    digest = build_daily_digest(store, vision, day=now)
    assert digest.anomaly is not None
    assert "check-in" in digest.anomaly
    assert digest.offline is True

    # today: a visitor arrives → anomaly clears
    pipeline.ingest(RawRingEvent(event_id="t1", occurred_at=now, scenario="visitor"))
    digest = build_daily_digest(store, vision, day=now)
    assert digest.anomaly is None
