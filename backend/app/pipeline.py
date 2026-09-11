"""Ingest pipeline: raw Ring event → snapshot → Bedrock analysis → store → alert decision → fan-out.

Noise control: an event whose category matches a recent one (within
`merge_window_minutes`) is merged into that entry — the family sees "×N"
instead of a stream of duplicates, and merged events never re-alert.
"""

from datetime import timedelta

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
        merge_window_minutes: int = 10,
    ):
        self.store = store
        self.vision = vision
        self.snapshots = snapshots
        self.notifier = notifier
        self.merge_window = timedelta(minutes=merge_window_minutes)

    def ingest(self, raw: RawRingEvent) -> tuple[DoorstepEvent, Alert]:
        analysis = self.vision.analyze_frame(raw.image, scenario_hint=raw.scenario)

        duplicate = self.store.latest_same_category(analysis.category, raw.occurred_at - self.merge_window)
        if duplicate is not None:
            duplicate.repeat_count = self.store.bump_repeat(duplicate.event_id)
            return duplicate, Alert(level="none", reason="Merged with a recent identical event.")

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
