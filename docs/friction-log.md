# Friction Log — PorchLight

> Purpose: document real friction we hit while building with Amazon/Ring/AWS tools.
> Submitted as Product Feedback + Friction Log for the Build, Ship, Shape hackathon (worth up to +10% in judging).
> Format: date | tool | what we tried | what went wrong | suggestion.

---

## Entries

### 2026-09-11 | Devpost | Reading prize & rules pages
- **Tried:** Opening `/prizes` and `/details/prizes` on amazonappdev2026.devpost.com to get authoritative prize details.
- **Friction:** Both URLs return 404. Prize info only exists on the homepage as a visual grid; no per-track permalink to cite or share. Rules page is a single long document with no anchor links, making it hard to reference specific eligibility clauses.
- **Suggestion:** Ship canonical `/prizes` and `/rules#eligibility` anchors so participants (and AI agents!) can cite sections.

### 2026-09-11 | Hackathon docs | Finding the no-hardware path per track
- **Tried:** Determining whether a mainland-China solo dev can compete without buying Ring/Bee/Fire TV hardware.
- **Friction:** Hardware-optional paths (Ring simulator, Bee-on-Apple-Watch, Alexa+ simulated web experience) exist but are scattered across the rules text and the Build Session video; there is no single "track requirements + no-hardware path" matrix.
- **Suggestion:** Add a per-track requirements matrix to the Devpost resources tab.

<!-- Add every new entry below this line. Aim for ≥10 high-quality entries by submission. -->

## Watchlist (to fill during M0)
- [ ] Ring developer portal signup flow
- [ ] Ring simulator provisioning (access, latency, docs)
- [ ] Ring API auth (token lifecycle, scopes)
- [ ] Bedrock model access enablement (us-east-1, Nova)
- [ ] Bedrock Converse multimodal API ergonomics (image formats, limits)
- [ ] AWS credits application flow
