from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.alerts import evaluate_alert
from app.analysis.bedrock_vision import BedrockVision
from app.config import Settings
from app.main import app
from app.models import AnalysisCategory, DoorstepAnalysis, DoorstepEvent, RawRingEvent
from app.pipeline import Pipeline
from app.store import EventStore


def test_health_offline_mode():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "ok"
        assert "bedrock_live" in body


def test_simulate_pipeline_end_to_end(tmp_path):
    store = EventStore(str(tmp_path / "t.db"))
    vision = BedrockVision(Settings(aws_region="us-east-1"))
    # force offline stub path so the test never touches AWS
    vision._offline = True

    pipeline = Pipeline(store, vision)
    event, alert = pipeline.ingest(
        RawRingEvent(event_id="e1", occurred_at=datetime.now(UTC), scenario="package_delivery")
    )

    assert event.analysis.category == AnalysisCategory.PACKAGE_DELIVERY
    assert event.analysis.offline is True
    assert alert.level == "none"
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
