# Copilot instructions

The project's instructions for every coding agent are in **`AGENTS.md`** at the repository root.
Read it before any change; it has the hard rules, the layout, the commands and the pull request
flow. Area rules are in `.github/instructions/*.instructions.md` and apply by file path.

The rules that matter most, in short:

- SAN zoning defaults to a copy-paste Brocade command set and `BrocadeClient` stays read-only;
  opt-in Brocade FOS switch apply follows ADR 0033 and ADR 0025 via `BrocadeZoneWriter` only
  (approval-gated, 5 exact prompt-free forms, pre-flight guards, pre-write undo, read-back). Array
  SSH is read-only through an allowlist; array writes go through WSAPI after operator approval, or
  via an ADR 0025 write-scoped SSH client: ADR 0015's `ArrayRcCliClient` (Remote Copy ports and
  targets) and ADR 0016's `ArraySnapCliClient` (snapshot schedules, one `createsched -f` form).
- A run is one array. Steps and modes come from `domain/workflow.py` only.
- No secrets, customer names or customer addresses in git. Never commit `frontend/dist`.
- Tests use fakes and captured output only. "Done" means run live on lab hardware.
- Before a pull request: `.venv/bin/python scripts/check.py` (app folder) must say PASS.
- Never push to `main`, force-push, tag, release, or run lab scripts unless the user asks.
