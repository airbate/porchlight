"""Alert fan-out: critical/high alerts must reach the family even with the
dashboard closed. Log always; optional outbound webhook (e.g. a push or email
bridge) when configured."""

import logging

import httpx

from .config import Settings
from .models import Alert, DoorstepEvent

logger = logging.getLogger(__name__)


class Notifier:
    def __init__(self, settings: Settings):
        self._url = settings.alert_webhook_url

    def dispatch(self, event: DoorstepEvent, alert: Alert) -> None:
        logger.warning(
            "ALERT [%s] event=%s scenario=%s — %s",
            alert.level, event.event_id, event.scenario, alert.reason,
        )
        if not self._url:
            return
        payload = {
            "level": alert.level,
            "reason": alert.reason,
            "event_id": event.event_id,
            "occurred_at": event.occurred_at.isoformat(),
            "summary": event.analysis.summary,
        }
        try:
            resp = httpx.post(self._url, json=payload, timeout=5.0)
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001 — fan-out must never break ingest
            logger.error("Alert webhook delivery failed: %s", exc)
