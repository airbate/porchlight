# Contributing to PorchLight

Thanks for your interest! PorchLight is being built in the open for the
[Build, Ship, Shape: Amazon Developer Hackathon](https://amazonappdev2026.devpost.com/)
(submission deadline: Oct 23, 2026). During the hackathon window the roadmap is
frozen to the milestone plan in `docs/42天里程碑.md`, so the most useful
contributions are:

- **Bug reports** — open an issue with steps to reproduce and backend logs.
- **Friction you hit** — if you try Ring's developer tooling or Bedrock and
  something hurts, tell us; we're collecting a friction log in
  `docs/friction-log.md`.
- **Small fixes** — typos, dependency bumps, test gaps. PRs welcome.

## Dev setup

```bash
cd backend && uv sync && uv run pytest     # backend + tests (no AWS creds needed)
cd frontend && npm install && npm run dev  # dashboard on :5173
```

## Ground rules

- Keep the offline-stub behavior: the demo pipeline must run without AWS
  credentials. Guard live calls behind graceful fallbacks.
- No real keys, snapshots, or personal data in commits — ever.
- Apache-2.0 in, Apache-2.0 out.
