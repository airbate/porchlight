# PorchLight 🏮

> An AI guardian at the front door of your aging parents.

PorchLight turns any Ring doorbell into a 24/7 caretaker for seniors living alone. It understands every doorstep moment — visitors, package deliveries, unusual loitering, fall-like postures — filters out the noise, and keeps distant family in the loop with a plain-language **daily care report** plus **instant alerts** when something looks wrong.

Built for the [Build, Ship, Shape: Amazon Developer Hackathon](https://amazonappdev2026.devpost.com/) — **Ring track + AWS Builder mini-challenge**.

## Why "PorchLight"

In American culture, leaving the porch light on means *"I'm waiting for you to come home safe."* PorchLight is that light, kept on by AI when you can't be there yourself.

## How it works

```
Ring sandbox / device ──signed webhook──► Ingest API (HMAC-verified)
        │                                      │
  (dev: simulator/                        1. snapshot → S3 / local
   stands in until                            2. Amazon Bedrock (Nova Lite, multimodal)
   M0 wiring)                                    → visitor / package / loitering /
                                                   fall_suspected / ambient_noise
                                               3. rules engine (confidence + quiet hours)
                                                      │
                              Family PWA ◄──alerts────┴── daily Care Digest (EventBridge)
```

- **Doorstep Sense** — every Ring event frame is classified by Amazon Nova via the Bedrock `Converse` API; noise (branches, shadows, passing cars) is filtered before it ever reaches the family.
- **Care Digest** — a natural-language report of the day at the door, plus rhythm anomaly detection (e.g., no real door activity for 24h → "worth a check-in call").
- **Instant Alerts** — high-confidence emergencies (suspected fall, late-night loiterer) reach designated family members in seconds: dashboard banner, optional webhook fan-out, snapshot attached, one tap to acknowledge.

## Repository layout

```
backend/     FastAPI ingest + Bedrock analysis + rules engine (Python 3.12+, uv)
  app/         pipeline, HMAC webhook verification, snapshot store, notifiers
  simulator/   dev stand-in for the Ring sandbox: pushes signed events w/ frames
  tests/       12 automated tests (pipeline, HMAC, snapshots, alerts, digest)
frontend/    Family dashboard PWA (React + Vite + TypeScript)
docs/        Research, brief, milestones, friction log, submission drafts (部分中文)
scripts/     dev launcher
```

## Run the demo

```bash
./scripts/dev.sh             # backend on :8000, dashboard on :5173
```

Open http://127.0.0.1:5173 and tap **"Try a test event"** — trigger a visitor, a
package, a suspected fall. Or drive the signed-webhook path exactly like the real
sandbox will:

```bash
cd backend
RING_WEBHOOK_SECRET=dev-secret uv run uvicorn app.main:app --port 8000
PORCHLIGHT_INGEST_URL=http://127.0.0.1:8000/events/ingest \
RING_WEBHOOK_SECRET=dev-secret uv run uvicorn simulator.main:app --port 8322
curl -X POST "http://127.0.0.1:8322/trigger?scenario=fall_suspected"
```

Without AWS credentials the backend runs in a clearly-marked **offline-stub mode**
so the demo never breaks; add credentials + enable the Nova model to go live:

```bash
cp .env.example .env         # then edit: AWS_REGION, BEDROCK_MODEL_ID, RING_WEBHOOK_SECRET, ...
```

## Tests

```bash
cd backend && uv run pytest        # 12 tests: pipeline, HMAC, snapshots, alerts, digest
cd frontend && npm install && npm run build   # typecheck + production build
```

## Documentation

| Doc | Content |
|-----|---------|
| `docs/主办方深度研究.md` | Sponsor business-line strategy & judge psychology → winning tactics (zh) |
| `docs/立项文档.md` | Project brief: value prop, features, architecture, win mapping (zh) |
| `docs/42天里程碑.md` | 42-day milestone plan M0→M3 (zh) |
| `docs/ring-integration.md` | Ring tooling verification checklist (M0 gate) |
| `docs/aws-integration.md` | AWS services map for the AWS Builder mini-challenge |
| `docs/devpost-writeup.md` | Submission text draft (en) |
| `docs/video-script.md` | 3-minute demo video script & shot list |
| `docs/product-feedback.md` | Product feedback + feature requests drafts (en) |
| `docs/friction-log.md` | Real friction we hit with Amazon/AWS tooling (+10% score) |

## License

Apache-2.0 — see [LICENSE](LICENSE).
