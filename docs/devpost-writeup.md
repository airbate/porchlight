# Devpost Submission Write-up (draft)

> Final submission text for https://amazonappdev2026.devpost.com — Ring track + AWS Builder mini-challenge.
> ⚠️ Placeholders marked `{{...}}` are filled at submission time (links, final numbers).

## Project name
PorchLight 🏮

## Tagline (≤200 chars)
An AI guardian at the front door of your aging parents. PorchLight understands every Ring doorstep moment and keeps distant family in the loop — calm reports daily, instant alerts when it matters.

## Inspiration
In American culture, leaving the porch light on means *"I'm waiting for you to come home safe."* Millions of adult children can't leave that light on in person: more than a quarter of US adults 65+ live alone (US Census Bureau), while their families juggle worry with busy lives. Ring doorbells already watch the doorstep — but they only *notify*, they don't *understand*. A stream of "motion detected" pings isn't care; it's noise. We wanted the doorbell to tell the family what actually matters, in plain language, with the calm cadence a worried daughter actually needs.

## What it does
PorchLight turns any Ring doorbell (sandbox or device) into a 24/7 doorstep caretaker for a senior living alone:

1. **Doorstep Sense** — every Ring motion event's frame is classified by Amazon Nova (Amazon Bedrock Converse API) into `visitor`, `package delivery`, `loitering`, `suspected fall`, or `ambient noise`, with a confidence score and a one-sentence plain-language summary. Noise like branches, shadows and passing cars is filtered before it ever reaches the family.
2. **Care Digest** — every day, the family gets a short, warm, natural-language report of the day at the door ("a courier dropped a package at 10:12 — remind Dad to pick it up"), plus rhythm anomaly detection: if a normally active door goes quiet for 24+ hours, the digest itself says "worth a check-in call."
3. **Instant Alerts** — high-confidence emergencies (suspected falls, late-night loiterers) break through within seconds: a red banner in the family dashboard, an optional webhook fan-out, snapshot attached, one tap to acknowledge.

## How we built it
- **Ring integration (runtime)**: events enter through a signed webhook endpoint (`POST /events/ingest`) — the same OAuth→Bearer, HMAC-signed shape the Ring developer sandbox uses. During development, a faithful Ring-sandbox simulator service (`simulator/`) pushes signed events with synthetic doorstep frames, so the pipeline is exercised end-to-end without hardware. {{If the real test account was wired by submission: mention it and link a clip.}}
- **Amazon Bedrock**: Amazon Nova Lite via the Converse API does the multimodal frame classification (strict JSON schema, temperature 0.1, bias-to-noise prompting so we never alarm without evidence) and writes the daily digest text. Same region as ingest — home camera imagery never crosses providers.
- **AWS**: S3 stores doorstep snapshots with a {{7-day}} lifecycle for privacy minimization; presigned URLs serve them to the dashboard; EventBridge Scheduler triggers the daily digest; IAM roles are least-privilege (one model, one bucket). {{Only claim what's deployed.}}
- **App**: a FastAPI pipeline (ingest → snapshot → analysis → rules → fan-out) and a warm, mobile-first React PWA for the family: Today at the door, alert banners with one-tap acknowledgment, and a live activity feed with doorstep thumbnails.
- **Graceful degradation**: without AWS credentials the pipeline runs in a clearly-marked offline-stub mode, so the demo never breaks on stage.

## Challenges we ran into
- Ring's developer portal and the hackathon page describe testing differently ("simulator" vs. "sandbox + test accounts"), and the subscription requirement is only a footnote — we documented the whole discovery path in our Friction Log.
- Designing alert rules that are *calm by default*: threshold + quiet-hours policies so a fall alert always breaks through, but daytime loitering doesn't cry wolf.
- Making LLM output trustworthy enough for safety-adjacent use: strict JSON validation, confidence floors, and a hard bias toward "ambient noise" when the frame is ambiguous.

## Accomplishments we're proud of
- An end-to-end care loop — Ring event → AI understanding → family-friendly report/alert — running in seconds, with every stage testable offline and 12 automated tests green in CI.
- A product voice: PorchLight deliberately *doesn't* forward everything. It filters, summarizes, and only interrupts when it would interrupt a good neighbor.
- Friction Log with {{N}} concrete, reproducible platform findings (we're told internal teams actually read these — we wrote them to be usable).

## What we learned
- Multimodal classification is the easy 20%; the hard 80% is deciding what a *family* needs to feel informed but not harassed.
- The Ring platform's edge AI already classifies humans/animals/vehicles — the real opportunity for developers is the layer above it: duration, posture, rhythm, and communication.
- Building with Bedrock's Converse API made swapping and tuning models trivial; strict output schemas beat prompt-hope every time.

## What's next for PorchLight
- Real-household pilot with {{a Ring test account / a partner family}}: tune thresholds on live foot traffic.
- Care circle: multi-family sharing, neighborhood escalation ("call the neighbor 3 doors down").
- An Alexa+ skill so the family can just ask: *"Alexa, how was Mom's doorstep today?"*
- Ring Appstore submission path — caretaking is the category we built for.

## Built with
`amazon-bedrock` · `amazon-nova` · `amazon-s3` · `amazon-eventbridge` · `ring-api` · `python` · `fastapi` · `react` · `typescript` · `vite`

## Links
- Repo: https://github.com/airbate/porchlight (Apache-2.0, CI: ruff + 12 tests green)
- Video (≤3 min, English): {{YouTube URL}}
- Try it: `./scripts/dev.sh` → http://localhost:5173, then tap "Try a test event"

> Note on pre-existing work: all code in the repo was written during the hackathon window; this project started {{2026-09-11}} specifically for this event.
