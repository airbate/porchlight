"""PorchLight Ring sandbox simulator — dev stand-in for the real Ring sandbox.

Pushes signed webhook events (with synthetic doorstep frames) to the
PorchLight ingest endpoint, exactly the shape the real Ring sandbox will use
after M0 wiring. Run from backend/:

    uv run uvicorn simulator.main:app --port 8322
    curl -X POST "http://127.0.0.1:8322/trigger?scenario=fall_suspected"

Env: PORCHLIGHT_INGEST_URL (default http://127.0.0.1:8000/events/ingest),
RING_WEBHOOK_SECRET (must match the backend; leave empty for unsigned dev).
"""
