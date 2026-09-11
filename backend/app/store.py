"""SQLite event store. SQLite first; the DAO surface is narrow enough to swap
DynamoDB in behind it for the deployed demo."""

import sqlite3
import threading
from datetime import datetime

from .models import AnalysisCategory, DoorstepAnalysis, DoorstepEvent

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    event_id    TEXT PRIMARY KEY,
    occurred_at TEXT NOT NULL,
    scenario    TEXT NOT NULL,
    category    TEXT NOT NULL,
    confidence  REAL NOT NULL,
    summary     TEXT NOT NULL,
    model       TEXT NOT NULL,
    offline     INTEGER NOT NULL DEFAULT 0,
    snapshot_ref TEXT,
    alerted     INTEGER NOT NULL DEFAULT 0
);
"""


class EventStore:
    def __init__(self, path: str):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(_SCHEMA)

    def save_event(self, event: DoorstepEvent) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO events VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    event.event_id,
                    event.occurred_at.isoformat(),
                    event.scenario,
                    event.analysis.category.value,
                    event.analysis.confidence,
                    event.analysis.summary,
                    event.analysis.model,
                    int(event.analysis.offline),
                    event.snapshot_ref,
                    int(event.alerted),
                ),
            )
            self._conn.commit()

    def set_alerted(self, event_id: str) -> None:
        with self._lock:
            self._conn.execute("UPDATE events SET alerted = 1 WHERE event_id = ?", (event_id,))
            self._conn.commit()

    def list_events(self, limit: int = 100) -> list[DoorstepEvent]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM events ORDER BY occurred_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def events_between(self, start: datetime, end: datetime) -> list[DoorstepEvent]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM events WHERE occurred_at BETWEEN ? AND ? ORDER BY occurred_at",
                (start.isoformat(), end.isoformat()),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> DoorstepEvent:
        return DoorstepEvent(
            event_id=row["event_id"],
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            scenario=row["scenario"],
            analysis=DoorstepAnalysis(
                category=AnalysisCategory(row["category"]),
                confidence=row["confidence"],
                summary=row["summary"],
                model=row["model"],
                offline=bool(row["offline"]),
            ),
            snapshot_ref=row["snapshot_ref"],
            alerted=bool(row["alerted"]),
        )
