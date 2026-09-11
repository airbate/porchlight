"""Ring event sources.

M0 GATE (docs/ring-integration.md): the exact Ring developer tooling for this
hackathon (portal, simulator, API shape) is still unverified. `FixtureSource`
lets the whole pipeline run end-to-end today; swap in `RingSimulatorSource`
once M0 confirms the real endpoints. The track requirement is a *runtime* call
against Ring API/SDK/simulator — wiring that adapter is milestone M1's first
task.
"""

import itertools
import uuid
from datetime import UTC, datetime, timedelta
from typing import Protocol

from .models import RawRingEvent

SCENARIOS = ["visitor", "package_delivery", "loitering", "fall_suspected", "ambient_noise"]


class RingEventSource(Protocol):
    def poll(self) -> list[RawRingEvent]: ...


class FixtureSource:
    """Replays synthetic doorstep events so the demo runs with zero hardware.
    Replace with RingSimulatorSource after M0 verification."""

    def __init__(self) -> None:
        self._counter = itertools.count()
        self._last_at = datetime.now(UTC)

    def poll(self) -> list[RawRingEvent]:
        scenario = SCENARIOS[next(self._counter) % len(SCENARIOS)]
        self._last_at += timedelta(minutes=7)
        return [
            RawRingEvent(
                event_id=uuid.uuid4().hex,
                occurred_at=self._last_at,
                scenario=scenario,
                metadata={"source": "fixture"},
            )
        ]


class RingSimulatorSource:
    """Polls the official Ring simulator once M0 confirms its API shape.

    TODO(M0): implement against the verified endpoints (auth, event webhook or
    polling, doorbell frame retrieval). Keep the RawRingEvent mapping here so
    nothing downstream changes.
    """

    def __init__(self, base_url: str, poll_interval_seconds: float = 2.0) -> None:
        self.base_url = base_url
        self.poll_interval_seconds = poll_interval_seconds
        raise NotImplementedError("Wire up after M0 verification — see docs/ring-integration.md")
