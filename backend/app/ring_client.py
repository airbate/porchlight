"""Ring integration boundary.

M0 GATE (docs/ring-integration.md): the hackathon's Ring sandbox access is
being verified. Today the receiving side is fully real — the Ring sandbox (or
our dev simulator standing in for it) POSTs signed JSON webhooks to
`POST /events/ingest`, and `verify_signature` enforces the shared-secret HMAC
the same way production will. `RingSandboxPoller` is the polling alternative
for sandbox shapes that don't push; its endpoints stay configurable so M0
findings land in config, not code.

Track requirement: a *runtime* call against Ring API/SDK/simulator — the
webhook receiver is that runtime boundary; `FixtureSource` is test-only.
"""

import hashlib
import hmac
import itertools
import uuid
from datetime import UTC, datetime, timedelta
from typing import Protocol

import httpx

from .models import RawRingEvent

SCENARIOS = ["visitor", "package_delivery", "loitering", "fall_suspected", "ambient_noise"]


def sign_body(body: bytes, secret: str) -> str:
    """Mirror of what a Ring-shaped webhook sender does — used by the dev simulator."""
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def verify_signature(body: bytes, header_value: str | None, secret: str | None) -> bool:
    """Verify an inbound webhook HMAC (sha256 hex, optional `sha256=` prefix).

    With no secret configured (local dev only) everything is accepted;
    with a secret configured, a missing or wrong signature is rejected.
    """
    if secret is None:
        return True
    if not header_value:
        return False
    sig = header_value.strip().removeprefix("sha256=").strip()
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)


class RingEventSource(Protocol):
    def poll(self) -> list[RawRingEvent]: ...


class FixtureSource:
    """Test-only replay of synthetic events. Never used by the live service."""

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


class RingSandboxPoller:
    """Polls the Ring sandbox for recent events when webhooks aren't available.

    TODO(M0): confirm the sandbox's real event-list and frame endpoints; they
    arrive as config (base_url + bearer token), so wiring lands in .env.
    """

    def __init__(
        self,
        base_url: str,
        bearer_token: str,
        events_path: str = "/events",
        poll_interval_seconds: float = 2.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.events_path = events_path
        self.poll_interval_seconds = poll_interval_seconds

    def poll(self) -> list[RawRingEvent]:
        resp = httpx.get(
            f"{self.base_url}{self.events_path}",
            headers={"Authorization": f"Bearer {self.bearer_token}"},
            timeout=10.0,
        )
        resp.raise_for_status()
        # TODO(M0): map the verified payload shape onto RawRingEvent here.
        raise NotImplementedError("Payload mapping lands after M0 verification")
