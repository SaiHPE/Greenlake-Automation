# Copilot instructions

The project's instructions for every coding agent are in **`AGENTS.md`** at the repository root.
Read it before any change; it has the hard rules, the layout, the commands and the pull request
flow. Area rules are in `.github/instructions/*.instructions.md` and apply by file path.

The rules that matter most, in short:

- The tool never writes to a SAN switch. Array SSH is read-only through an allowlist; writes go
  through WSAPI after the operator approves a plan. An SSH write follows ADR 0025: exact tested forms,
  built only inside an approved apply, only on the plan's objects, undo written first, read back after.
  Today the SSH write clients are ADR 0015's `ArrayRcCliClient` (Remote Copy ports and targets) and
  ADR 0016's `ArraySnapCliClient` (snapshot schedules, one `createsched -f` form).
- A run is one array. Steps and modes come from `domain/workflow.py` only.
- No secrets, customer names or customer addresses in git. Never commit `frontend/dist`.
- Tests use fakes and captured output only. "Done" means run live on lab hardware.
- Before a pull request: `.venv/bin/python scripts/check.py` (app folder) must say PASS.
- Never push to `main`, force-push, tag, release, or run lab scripts unless the user asks.
