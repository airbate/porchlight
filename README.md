# PorchLight 🏮

> An AI guardian at the front door of your aging parents.

PorchLight turns any Ring doorbell into a 24/7 caretaker for seniors living alone. It understands every doorstep moment — visitors, package deliveries, unusual loitering, fall-like postures — filters out the noise, and keeps distant family in the loop with a plain-language **daily care report** plus **instant alerts** when something looks wrong.

Built for the [Build, Ship, Shape: Amazon Developer Hackathon](https://amazonappdev2026.devpost.com/) — **Ring track + AWS Builder mini-challenge**.

## Why "PorchLight"

In American culture, leaving the porch light on means *"I'm waiting for you to come home safe."* PorchLight is that light, kept on by AI when you can't be there yourself.

## How it works

```
Ring simulator/device ──► Ingest API ──► Amazon Bedrock (Nova Lite, multimodal)
                              │                 │ structured JSON: visitor / package /
                              │                 │ loitering / fall_suspected / ambient_noise
                              ▼                 ▼
                          S3 snapshots    Rules engine (confidence + quiet hours)
                                                │
                          Family PWA ◄──────────┴── daily Care Digest (EventBridge Scheduler)
```

- **Doorstep Sense** — every Ring event frame is classified by Amazon Nova via the Bedrock `Converse` API; noise (branches, shadows, passing cars) is filtered before it ever reaches the family.
- **Care Digest** — a natural-language report of the day at the door, plus rhythm anomaly detection (e.g., no one left the house for 24h).
- **Instant Alerts** — high-confidence emergencies (suspected fall, late-night loiterer) reach designated family members in seconds, with snapshot + AI summary + one-tap actions.

## Repository layout

```
backend/    FastAPI ingest + Bedrock analysis + rules engine (Python 3.12+, uv)
frontend/   Family dashboard PWA (React + Vite + TypeScript)
docs/       Project brief, milestones, friction log, AWS integration map (部分中文)
```

## Quick start

### Backend

```bash
cd backend
uv sync                      # creates .venv from uv.lock
uv run uvicorn app.main:app --reload
# → http://127.0.0.1:8000/docs  (GET /health, GET /events, POST /dev/simulate)
```

Without AWS credentials the backend runs in **offline mode**: Bedrock calls return a graceful stub so the demo never breaks. Set AWS credentials + enable Nova model access to go live:

```bash
cp .env.example .env         # then edit: AWS_REGION, BEDROCK_MODEL_ID, ...
```

### Frontend

```bash
cd frontend
npm install && npm run dev   # → http://127.0.0.1:5173 (Node 20+; Bun works too)
```

### Both at once

```bash
./scripts/dev.sh
```

### Tests

```bash
cd backend && uv run pytest
```

## Documentation

| Doc | Content |
|-----|---------|
| `docs/立项文档.md` | Project brief: value prop, features, architecture, win mapping (zh) |
| `docs/42天里程碑.md` | 42-day milestone plan M0→M3 (zh) |
| `docs/ring-integration.md` | Ring tooling verification checklist (M0 gate) |
| `docs/aws-integration.md` | AWS services map for the AWS Builder mini-challenge |
| `docs/friction-log.md` | Real friction we hit with Amazon/AWS tooling (+10% score) |

## License

Apache-2.0 — see [LICENSE](LICENSE).
