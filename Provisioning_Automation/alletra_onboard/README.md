# Alletra Onboard

Local operator automation for HPE Alletra MP B10000 onboarding into HPE GreenLake and DSCC.

This is the first implementation slice from `../IMPLEMENTATION_PLAN.md`:

- FastAPI local control API
- Typer CLI
- provider-agnostic domain models
- SQLite state store with WAL
- GreenLake REST adapter contracts
- Playwright browser adapter shells for Cloudinit and DSCC Setup
- React/Vite UI starter

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
onboard status
onboard preflight --file config\arrays.example.csv
onboard preflight --file config\arrays.example.csv --live-greenlake
onboard api
```

The API binds to `127.0.0.1:8765` by default.

## Configuration

Copy `config/settings.example.toml` to `config/settings.toml` and provide secrets via environment variables:

- `GL_CLIENT_ID`
- `GL_CLIENT_SECRET`
- `GL_MEMBER_WORKSPACE_ID`

Do not commit secrets or real subscription keys.

`--live-greenlake` performs read-only checks against GreenLake: OAuth token fetch, Service Catalog provision lookup, Device Management serial lookup, and Subscription Management key lookup. Without the flag, preflight remains fully local/offline.
