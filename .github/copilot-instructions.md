# Copilot instructions

The project's instructions for every coding agent are in **`AGENTS.md`** at the repository root.
Read it before any change; it has the hard rules, the layout, the commands and the pull request
flow. Area rules are in `.github/instructions/*.instructions.md` and apply by file path.

The rules that matter most, in short:

- The tool never writes to a SAN switch. Array SSH is read-only through an allowlist; writes go
  through WSAPI after the operator approves a plan. (ADR 0015 plans a write-scoped SSH client for
  Remote Copy links and targets; it is not built yet.)
- A run is one array. Steps and modes come from `domain/workflow.py` only.
- No secrets, customer names or customer addresses in git. Never commit `frontend/dist`.
- Tests use fakes and captured output only. "Done" means run live on lab hardware.
- Before a pull request: `.venv/bin/python scripts/check.py` (app folder) must say PASS.
- Never push to `main`, force-push, tag, release, or run lab scripts unless the user asks.
