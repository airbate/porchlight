"""Ingest pipeline: raw Ring event → Bedrock analysis → store → alert decision."""

from .alerts import evaluate_alert
from .analysis.bedrock_vision import BedrockVision
from .models import Alert, DoorstepEvent, RawRingEvent
from .store import EventStore


class Pipeline:
    def __init__(self, store: EventStore, vision: BedrockVision):
        self.store = store
        self.vision = vision

    def ingest(self, raw: RawRingEvent) -> tuple[DoorstepEvent, Alert]:
        analysis = self.vision.analyze_frame(raw.image, scenario_hint=raw.scenario)
        event = DoorstepEvent(
            event_id=raw.event_id,
            occurred_at=raw.occurred_at,
            scenario=raw.scenario,
            analysis=analysis,
        )
        self.store.save_event(event)

        alert = evaluate_alert(analysis, occurred_at=raw.occurred_at)
        if alert.level != "none":
            self.store.set_alerted(event.event_id)
            event.alerted = True
        return event, alert
