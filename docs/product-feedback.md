# Product Feedback (submission draft)

> Devpost requires feedback for every tool/API/SDK used. One block per tool; keep concrete and reproducible.
> ✍️ Fill the "after M0/M2 real usage" sections honestly before submitting.

## Ring developer platform / sandbox
- **What we built with it:** signed webhook ingest of doorstep motion events with frames, mapped onto our care pipeline.
- **What's great:** the Appstore framing (build → certify → roll out) gives a real commercial path; webhook events with built-in human/animal/vehicle classification save every developer from rebuilding detection; the Ring MCP server for IDEs is a genuinely modern touch.
- **What to change:** (1) the words "simulator" (hackathon page) vs "sandbox/test accounts" (portal) should converge — we lost time discovering they weren't the same thing; (2) surface the subscription requirement at registration, not in a page footnote; (3) portal root was intermittently slow/unreachable during our window and `/docs` 404'd — one canonical "start here" page would fix the whole discovery journey. *(update after M0 real usage)*
- **Would we use again:** yes — the caretaking/appstore angle is exactly where third-party devs add value. (confirm post-M0)

## Amazon Bedrock (Converse API + Nova Lite)
- **What we built with it:** multimodal doorstep frame classification with strict JSON output; daily digest text generation.
- **What's great:** one API shape for multimodal and text; inference config is simple; model id swap means tuning cost/quality is a config change; same-region inference keeps home camera imagery in one trust boundary.
- **What to change:** model-access enablement is an extra console step every new developer trips on — a "grant me Nova in one click" flow would help hackathons; JSON-mode responses occasionally wrapped in markdown fences (we strip defensively). *(update after M2 tuning)*
- **Would we use again:** yes, without hesitation.

## Amazon S3 (snapshots + presigned URLs)
- **What we built with it:** doorstep snapshot storage, lifecycle-based privacy cleanup, presigned GET for the dashboard.
- **What's great:** presigned URLs are the perfect privacy pattern for camera imagery — the backend never proxies bytes.
- **What to change:** lifecycle rules are console-buried; an example policy in docs for "keep N days then delete" would save the classic misconfiguration. *(confirm during M2 deploy)*
- **Would we use again:** yes.

## Amazon EventBridge Scheduler (daily digest)
- **What we built with it:** daily Care Digest job trigger. *(mark exact usage after M2 deploy; local dev used in-process scheduling)*
- **What to change:** naming overlap between EventBridge rules and EventBridge Scheduler confused us initially; docs could separate "event buses" from "cron-as-a-service" more clearly.

## Devpost (platform)
- **What's great:** friction-log-as-bonus is a brilliant incentive; track priority categories published upfront helped us aim.
- **What to change:** `/prizes` and `/details/prizes` 404 (prize info only in homepage grid); judges and concrete resource links appear late; a per-track "requirements + no-hardware path" matrix would remove the #1 source of participant anxiety.

## Feature Requests (optional submission section)
1. **Ring:** expose per-event frame bundles (before/during/after) via webhook payloads — care use-cases need the seconds around a trigger.
2. **Ring sandbox:** a time-travel API (replay yesterday's traffic) for testing consumer logic without waiting for real motion.
3. **Bedrock:** first-class JSON-schema-constrained output for Nova models (function-calling style), removing defensive parsing.
4. **Devpost:** per-track submission checklists generated from the rules, so teams can self-audit before the deadline.
