# AWS Integration — PorchLight (AWS Builder Mini-Challenge)

> This document maps every AWS service PorchLight uses, how it is integrated, and where in the code the integration lives. Written for the AWS Builder mini-challenge submission field.

## Services used

| Service | Role | Code entry point | Status |
|---------|------|------------------|--------|
| **Amazon Bedrock Runtime** | Multimodal doorstep event understanding (Nova Lite via `Converse` API) + daily digest text generation | `backend/app/analysis/bedrock_vision.py`, `backend/app/digest.py` | M1 |
| **Amazon S3** | Doorstep snapshot storage, 7-day lifecycle cleanup (privacy minimization) | `backend/app/store.py` (s3 put on ingest, optional local mode) | M2 |
| **Amazon EventBridge Scheduler** | Daily 20:00 local "Care Digest" job | `infra/` (M2, when we deploy) | M2 |
| **IAM** | Least-privilege role: bedrock:InvokeModel on one model, s3:PutObject on one bucket | `infra/` | M2 |

## Integration details

### 1. Bedrock multimodal analysis (core)

Every Ring event frame is sent to Amazon Nova Lite through the Bedrock `Converse` API with a strict JSON-schema system prompt. The model must return one of: `visitor | package_delivery | loitering | fall_suspected | ambient_noise`, a confidence score, and a one-sentence plain-language description. Structured output is validated with Pydantic before it touches the rules engine — malformed model output never reaches the alert path.

```python
# backend/app/analysis/bedrock_vision.py (excerpt)
response = bedrock.converse(
    modelId=config.bedrock_model_id,          # us.amazon.nova-lite-v1:0
    messages=[{"role": "user", "content": [
        {"image": {"format": "jpeg", "source": {"bytes": frame}}},
        {"text": "Classify this doorstep event."},
    ]}],
    system=[{"text": SYSTEM_PROMPT}],
    inferenceConfig={"temperature": 0.1, "maxTokens": 300},
)
```

### 2. Why Nova (not a hosted third-party model)

On-device-style latency budget: alerts must land within seconds of the Ring event. Nova Lite on Bedrock keeps inference inside the same AWS region as our ingest service, avoids cross-provider data transfer of home camera imagery, and its per-image pricing fits a 24/7 doorstep workload. Text generation for digests uses the same model family to keep the integration story simple.

## Deployment topology (M2)

```
Ring simulator/device ──► FastAPI ingest (Fargate or Lambda)
                              ├─► S3 (snapshots, 7-day lifecycle)
                              ├─► Bedrock Runtime (Nova Lite)
                              ├─► SQLite/DynamoDB (events)
                              └─► EventBridge Scheduler ─► digest job ─► Bedrock ─► push digest
Family PWA dashboard ──► FastAPI read APIs
```
