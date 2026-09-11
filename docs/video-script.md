# 3-Minute Demo Video — Script & Shot List

> Deadline: record by 10/16 (Beijing). ≤3:00 total, English VO, YouTube public/unlisted-public.
> Golden rule from the strategy doc: the first 20 seconds MUST show a real Ring event landing — not slides.
> Recording setup: two windows side by side (simulator terminal + dashboard), 1080p, cursor enlarged.

| # | Time | Shot | Voice-over (English) |
|---|------|------|---------------------|
| 1 | 0:00–0:20 | **Cold open:** cursor triggers `fall_suspected` on the simulator; cut to the dashboard as the red banner drops in with the snapshot. | "Mom lives alone. Her Ring doorbell just saw something at her front door — and this is the moment her family finds out. Not 'motion detected.' A fall, understood, explained, with a photo." |
| 2 | 0:20–0:45 | Title card "PorchLight" (porch-light animation), then dashboard overview: Today at the door + feed. | "This is PorchLight — an AI guardian at the front door of aging parents. It turns any Ring doorbell into a caretaker: it understands what happens at the doorstep, filters the noise, and tells the family what actually matters." |
| 3 | 0:45–1:20 | **Doorstep Sense:** trigger `visitor`, then `ambient_noise`; show feed entries — visitor explained in one sentence, noise dimmed/filtered. Terminal shows the Bedrock call (Nova model id visible). | "Every Ring event is analyzed by Amazon Nova on Amazon Bedrock. A visitor becomes a sentence a daughter can read in two seconds. A tree branch? Filtered — never a push notification. We bias hard toward calm: no alarm without visual evidence." |
| 4 | 1:20–1:55 | **Care Digest:** scroll the digest card; highlight the rhythm-anomaly line. Optionally show EventBridge Scheduler in AWS console (3s). | "Once a day, the family gets a digest, written in plain language: what happened, what's worth knowing. And if the door goes quiet for a whole day — PorchLight notices the rhythm change and says: worth a check-in call. Because silence can be the loudest warning." |
| 5 | 1:55–2:25 | **Instant Alerts:** replay the fall trigger in slow-mo; show the banner, snapshot, one-tap acknowledge; flash the signed webhook / HMAC line in the terminal; show alert fan-out webhook payload. | "When confidence is high — a suspected fall, or a stranger lingering at night — PorchLight breaks through in seconds: a signed webhook from the Ring event, rules engine, alert, done. One tap and the family knows someone's on it." |
| 6 | 2:25–2:45 | **Architecture slide** (10s) + repo shot: README, tests passing in CI, Apache-2.0 license. | "Under the hood: Ring events, Amazon Bedrock, S3 snapshots with a privacy lifecycle, EventBridge scheduling — twelve tests green, fully open source. It degrades gracefully, so it never breaks in front of you." |
| 7 | 2:45–3:00 | Close on the porch-light logo. | "You can't always be there. PorchLight keeps the porch light on for you." + subtitle: Built on Ring + Amazon Bedrock. |

## Shot checklist (before recording)
- [ ] Fresh db: clear events, reseed 2–3 realistic ones so the feed looks lived-in
- [ ] Dashboard at 110% zoom, light theme, browser chrome visible (feels real)
- [ ] Simulator trigger with visible `curl` or button — whichever reads better on camera
- [ ] Microphone: external, record VO separately per row, then cut
- [ ] End card: repo URL + "Built with Ring + Amazon Bedrock"
- [ ] Upload: title "PorchLight — AI doorstep care for aging parents (Amazon Developer Hackathon)", public
