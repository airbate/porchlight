"""Ingest pipeline: raw Ring event → snapshot → Bedrock analysis → store → alert decision → fan-out."""

from .alerts import evaluate_alert
from .analysis.bedrock_vision import BedrockVision
from .models import Alert, DoorstepEvent, RawRingEvent
from .notifiers import Notifier
from .snapshots import SnapshotStore
from .store import EventStore


class Pipeline:
    def __init__(
        self,
        store: EventStore,
        vision: BedrockVision,
        snapshots: SnapshotStore,
        notifier: Notifier,
    ):
        self.store = store
        self.vision = vision
        self.snapshots = snapshots
        self.notifier = notifier

    def ingest(self, raw: RawRingEvent) -> tuple[DoorstepEvent, Alert]:
        analysis = self.vision.analyze_frame(raw.image, scenario_hint=raw.scenario)
        event = DoorstepEvent(
            event_id=raw.event_id,
            occurred_at=raw.occurred_at,
            scenario=raw.scenario,
            analysis=analysis,
        )
        if raw.image:
            event.snapshot_ref = self.snapshots.save(event.event_id, raw.image)

        alert = evaluate_alert(analysis, occurred_at=raw.occurred_at)
        if alert.level != "none":
            event.alert_level = alert.level
            event.alert_reason = alert.reason
            self.notifier.dispatch(event, alert)

        self.store.save_event(event)
        return event, alert
