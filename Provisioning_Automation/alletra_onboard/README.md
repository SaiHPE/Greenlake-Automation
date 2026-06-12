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

# 1. Enter GreenLake API credentials (writes a gitignored .env)
onboard configure

# 2. Validate everything read-only (no writes)
onboard preflight --file config\arrays.csv --live-greenlake

# 3. Preview the exact GreenLake calls (still no writes)
onboard provision --file config\arrays.csv --serial <SERIAL> --dry-run

# 4. Run Component A for real: register + subscribe + assign + verify
onboard provision --file config\arrays.csv --serial <SERIAL>
```

Run `onboard` from this directory (the one containing `.env`). The local API (`onboard api`)
binds to `127.0.0.1:8765`.

## Configuration

GreenLake credentials are **personal API client** credentials (GreenLake UI:
Manage Workspace -> Personal API clients -> Create personal API client). Provide them with
`onboard configure`, or copy `config/env.example` to `.env` and fill in:

- `GL_CLIENT_ID`
- `GL_CLIENT_SECRET`
- `GL_TOKEN_URL` — the per-workspace token URL shown next to the API client. This is the
  newer `https://global.api.greenlake.hpe.com/authorization/v2/oauth2/<tid>/token` endpoint,
  **not** `sso.common.cloud.hpe.com`.
- `GL_BASE_URL` (default `https://global.api.greenlake.hpe.com`)
- `GL_MEMBER_WORKSPACE_ID`

`.env`, `config/arrays.csv`, and anything with a real subscription key are gitignored.
Only `config/arrays.example.csv` and `config/env.example` (placeholders) are committed.

## Prerequisite: provision the service in the workspace

The **assign-application** step requires the **Data Services** service to be *added to the
workspace and deployed to a region* (GreenLake UI: Manage Workspace -> Services). If
`GET /service-catalog/v1/service-manager-provisions` returns zero PROVISIONED items, the
device cannot be assigned and `onboard provision` stops at `GL_DISCOVER_SERVICE` with a
clear message. Set `service_catalog_region_id` in the CSV to the region where Data Services
is provisioned.

## Commands

- `onboard configure` — store/update GreenLake credentials in `.env`. `--show` prints current values (secret masked).
- `onboard preflight --file <csv> [--live-greenlake]` — local validation; `--live-greenlake` adds read-only GreenLake checks (token, service-catalog, device, subscription).
- `onboard provision --file <csv> [--serial <S>] [--dry-run]` — Component A pipeline: discover -> add subscription -> register device -> assign application -> apply subscription -> verify. Idempotent and resumable; every write is GET-guarded and every async operation is polled. `--dry-run` performs only the read/guard calls and prints what the live run would do.
- `onboard status` / `onboard api` — run state table / local control API.
