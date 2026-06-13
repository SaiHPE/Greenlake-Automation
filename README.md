# Alletra Onboard

Operator automation for onboarding an **HPE Alletra MP B10000** into **HPE GreenLake + DSCC**.
It runs as a local web app (`onboard ui`) and as a CLI (`onboard …`). Both drive the same
three components:

| Step | Component | What it does | How it runs |
|---|---|---|---|
| **A** | GreenLake REST | register device → assign to Data Services → add/apply subscription → verify | headless HTTP (anywhere with internet) |
| **B** | Cloud Connectivity Wizard ("cloudinit") | fill the on-array wizard, stop at Review for the operator to Submit | Playwright, **launches** its own browser at the array's `169.254.x` URL |
| **C** | DSCC "Set Up System" wizard | fill Welcome→Network→Time→Attributes→System, stop at the credential | Playwright, **attaches** to a logged-in Chrome (DSCC SSO) |

The web app is a guided 6-step flow (Configure → Array details → GreenLake → Cloud
Connectivity → DSCC → Finish) built with **React + the HPE Design System** (`grommet-theme-hpe`)
and served by the FastAPI backend.

---

## ⚠️ Two-machine reality (read this first)

The work is currently split across two machines because no single one can do everything:

- **B (cloudinit) must run on the jump box** — only it sits on the array's link-local subnet and can reach `https://169.254.x.x/cloudinit`.
- **C (DSCC) currently runs on the laptop** — DSCC SSO would hang on the jump box behind the lab proxy. A fix is in place (the launcher now applies the proxy automatically) but is **not yet confirmed on the jump box**; until then, do DSCC on the laptop.
- **A (GreenLake REST) runs anywhere** with internet + credentials.

So today: **jump box does A + B**, **laptop does C**. The run state is a per-machine SQLite
DB, so the DSCC step on the laptop is a separate CLI step, not a continuation of the jump
box's run. Once DSCC-on-jump-box is confirmed working, the whole flow collapses onto one host.

---

## Repositories & machines

GitHub: `github.com/SaiHPE/Greenlake-Automation`. There are **two branches** that matter:

| Branch | Contents | Used by |
|---|---|---|
| `main` | the **full repo** (`Provisioning_Automation/alletra_onboard/…` + other dirs) | the dev workstation, the **laptop** |
| `jumpbox-package` | a **`git subtree split`** of just `Provisioning_Automation/alletra_onboard`, so the package sits at the branch **root** | the **jump box** (which has the package as a flat folder, not a full clone) |

| Machine | Path | Pulls from | Role |
|---|---|---|---|
| Dev workstation | `…\Documents\Greenlake-Automation` (full clone) | `main` | builds/commits; has Node for the frontend |
| Jump box | `C:\Users\Administrator\Downloads\alletra_onboard` (flat copy) | `jumpbox-package` | A + B |
| Laptop | `C:\Users\gsairoop\Downloads\storage automation` (full clone) | `main` | C (DSCC) |

**The built UI (`frontend/dist`) is committed to git**, so neither the jump box nor the laptop
needs Node — they just pull and run.

### Syncing (the important part)

**Dev workstation → GitHub** (after changing the package). Push `main`, then refresh the
subtree branch so the jump box can pull it:

```powershell
# from the repo root, after committing to main
git push origin main
git branch -D jumpbox-package
git subtree split --prefix=Provisioning_Automation/alletra_onboard -b jumpbox-package
git push -f origin jumpbox-package
```
Do this **every time** a push to `main` touches the package, or the jump box will lag.
If a UI source file changed, run `npm run build` in `frontend/` (PowerShell) and commit the
new `frontend/dist` **before** pushing.

**Jump box ← GitHub** (flat copy, `jumpbox-package` branch):
```powershell
cd C:\Users\Administrator\Downloads\alletra_onboard
git fetch origin jumpbox-package
git reset --hard origin/jumpbox-package
git log -1 --oneline
```
Preserves untracked `.env` / `.venv` / `config\arrays.csv`. If git prompts
`Unlink of file … failed (y/n)` after the fetch, answer **`n`** — the fetch already landed;
just run the `reset --hard`. If the reset itself errors, `Get-Process git | Stop-Process -Force`
then retry.

**Laptop ← GitHub** (full clone, `main`):
```powershell
cd "C:\Users\gsairoop\Downloads\storage automation"
git fetch origin
git reset --hard origin/main
git log -1 --oneline
```

---

## Getting the app onto a machine

Three ways, easiest first. The full repo is deeply nested; you don't need to navigate it.

**1. Release zip (operators — no git, no Node).** Download **`alletra-onboard-latest.zip`** from
the [latest release](https://github.com/SaiHPE/Greenlake-Automation/releases/latest) (rebuilt
automatically on every push to `main` — see *Releasing* below), extract, and run:
```powershell
.\start.ps1                                  # first run sets up the venv; then launches the UI
.\start.ps1 -Proxy http://proxy.example.net:8080   # on the jump box (behind a proxy)
```
`start.ps1` creates the venv, installs the package + Playwright's Chromium on first run, then
opens the web app at `http://127.0.0.1:8765`. The built UI is in the zip, so no Node is needed.

**2. Clean flat clone (just the app, no other folders).** The `jumpbox-package` branch is a
`subtree split` of only this package, with the built UI included:
```powershell
git clone -b jumpbox-package https://github.com/SaiHPE/Greenlake-Automation.git alletra-onboard
cd alletra-onboard; .\start.ps1
```

**3. Full repo (developers).** `git clone` `main`; the app is under
`Provisioning_Automation/alletra_onboard/`.

### Releasing (automated)

Every push/merge to `main` that touches the app runs **`.github/workflows/release.yml`** on a
Windows runner: it builds the UI, runs `scripts/build_release.ps1`, and refreshes a single
rolling **`latest`** GitHub Release with `alletra-onboard-latest.zip` (+ a versioned copy and
SHA256). So `/releases/latest` is always the newest `main` build — nothing manual to do.

To build the zip locally (dev workstation, needs Node):
```powershell
.\scripts\build_release.ps1     # -> release\alletra-onboard-<version>.zip + .sha256
```
The zip excludes `node_modules`, `.venv`, tests, and captures — just `src/`, the prebuilt
`frontend/dist/`, `config/arrays.example.csv`, the scripts, and `start.ps1` (~210 KB). Bump the
version in `pyproject.toml` to change the versioned asset name.

---

## First-time setup (manual — `start.ps1` does this for you)

```powershell
# from the package dir (the one with pyproject.toml)
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
# Component B (jump box) launches a browser, so it needs Playwright's Chromium:
.\.venv\Scripts\python.exe -m playwright install chromium
```
The jump box has a helper: `.\scripts\setup_jumpbox.ps1 -Proxy http://<lab-proxy>:<port>`
(creates the venv, installs, runs `onboard check`). The jump box also needs the **VC++ x64
Redistributable** (else greenlet fails to import) and a persisted proxy
(`setx HTTPS_PROXY http://<lab-proxy>:<port>`).

**Clock skew & DSCC sign-in.** DSCC login fails with `iat is in the future` if the host clock
has drifted, and NTP can't always fix it (UDP 123 is firewalled in locked environments; proxies
don't carry NTP). The app handles this itself: the **DSCC step shows a "Sync system clock"
button** when it detects skew, and there's a CLI equivalent **`onboard sync-clock`**. Both read
the time from an HTTPS `Date` header through the proxy (works wherever the app has HTTPS egress),
so no NTP, scripts, or scheduled tasks are needed. **Setting the clock needs Administrator**, so
launch the app elevated (`onboard ui` / `start.ps1` from an Administrator shell) for the button
to work.

Credentials (`.env`) are never in git. Enter them with `onboard configure` (or in the web
app's Configure screen). DSCC (C) does **not** need GreenLake credentials.

---

## Running it

### Web app (recommended) — on the jump box for A + B

```powershell
cd C:\Users\Administrator\Downloads\alletra_onboard
.\.venv\Scripts\onboard.exe ui          # starts the server + opens http://127.0.0.1:8765
```
1. **Configure GreenLake** — enter the API client (Client ID/Secret + per-workspace token URL), **Test connection**.
2. **Array details** — **Download CSV template**, fill it, **upload** → values land in an editable form → **Create run**.
3. **GreenLake registration** — **Run** (live phase log streams in). A subscription-apply warning is non-fatal.
4. **Cloud Connectivity** — get the `169.254.x` URL from the Discovery Tool, **paste it**, **Launch & Fill** → review the values in the browser → **Submit yourself**.
5. **DSCC Setup** — (see two-machine note) on the jump box only once DSCC auth is confirmed there; otherwise use the laptop CLI below.

### CLI — DSCC on the laptop (proven path)

```powershell
cd "C:\Users\gsairoop\Downloads\storage automation\Provisioning_Automation\alletra_onboard"
# 1) open a logged-in DSCC browser (auto-applies the proxy if HTTPS_PROXY is set)
.\.venv\Scripts\onboard.exe browser --url https://console-jp1.data.cloud.hpe.com
#    -> log into DSCC, open Setup -> <serial> -> Set Up System, stay on Welcome
# 2) fill the wizard up to the System credential, then stop
.\.venv\Scripts\onboard.exe dscc --file config\arrays.csv --serial <SERIAL> --attach http://localhost:9222
#    -> in the browser: add the credential, Continue, review, Submit
```

### All CLI commands

- `onboard ui` — start the web app and open the browser.
- `onboard configure [--show]` — store/inspect GreenLake credentials in `.env`.
- `onboard check` — read-only GreenLake readiness (auth + provisioned Data Services regions).
- `onboard preflight --file <csv> [--live-greenlake]` — validate a work item.
- `onboard provision --file <csv> --serial <S> [--dry-run]` — Component A.
- `onboard cloudinit --file <csv> --serial <S> [--attach <cdp>]` — Component B.
- `onboard dscc --file <csv> --serial <S> --attach <cdp>` — Component C.
- `onboard browser [--url <u>] [--no-proxy]` — launch a CDP debug Chrome (applies `HTTPS_PROXY` unless `--no-proxy`).
- `onboard api` / `onboard status` — raw API server / run table.

---

## `arrays.csv`

One row per array. Gitignored (`config/arrays.example.csv` is the committed template). Columns:

```
serial_number, part_number, subscription_key, service_catalog_region_id, dscc_region_code,
cloudinit_url, mgmt_ipv4, mask, gateway, dns (semicolon-separated), ntp, timezone,
proxy_host, proxy_port, dscc_system_name, dscc_country, contact_first_name, contact_last_name,
contact_language, contact_company, contact_phone, contact_email, secret_name, secret_username,
secret_password, blueprint_name, apply_blueprint
```

Gotchas:
- **`part_number` must be the product SKU** (e.g. `S0B84A`), **not** the box FRU/assembly number (`R7C75-…`) — the FRU returns `HPE_GL_ERROR_NOT_FOUND`.
- **`subscription_key`** is the GreenLake activation key (from the activation email's attachment), **not** the EON order number and **not** the AutoPass on-array `.dat` license keys.
- **`cloudinit_url`** is a placeholder; paste the fresh `169.254.x` URL per boot in the UI.
- **`secret_password`** is unused by automation (the operator enters the DSCC credential by hand); leave it blank.

---

## Current issues to solve

1. **Subscription key for the target array is unresolved.** The factory activation produced
   AutoPass on-array licenses (the 28-key `.dat`) + an EON order number — **not** a GreenLake
   "Storage Central" (SKU `R7N52AAE`) subscription. The only subscription in the workspace was
   issued against a *different* serial. Until a valid GreenLake subscription for the target
   array is obtained, the apply-subscription phase warns (non-fatal; register + assign still
   succeed). **Action:** get/confirm the array's own GreenLake subscription key from HPE.

2. **DSCC on the jump box — resolved (single host).** The "Authenticating…" hang had two
   causes, both fixed: (a) Chrome ignores `HTTPS_PROXY`, so the launcher passes `--proxy-server`
   automatically; (b) host **clock drift** failed the login JWT (`iat is in the future`) — fixed
   by the in-app **"Sync system clock"** button / `onboard sync-clock` (HTTPS time-sync, since
   NTP/UDP is blocked). With the proxy flag and a synced clock, the jump box reaches the DSCC
   console, so **A + B + C all run on the jump box** from the one web app. (The clock button
   needs the app run as Administrator.)

3. **Run state does not cross machines.** Each machine has its own SQLite DB, so a web-app run
   started on the jump box (A + B) can't be continued for DSCC on the laptop — DSCC is a
   separate CLI step there. Resolved automatically once #2 lets one host do all three.

4. **The web-app path for steps 3–5 hasn't had a full live pass.** The automations are proven
   via CLI; the UI buttons (GreenLake Run, Cloud Connectivity Launch & Fill) need one
   end-to-end run on the jump box against the real array.

5. **DSCC credential entry is manual by design.** The "Create Secret" modal was never reliably
   captured, and the array admin password is sensitive, so the operator enters it in the
   wizard. Could be automated later if the modal selectors are captured.

6. **Packaging — done for v1.** Self-contained **release zip + one-click `start.ps1`**, and a
   GitHub Actions workflow auto-refreshes the rolling **`latest`** release on every push to
   `main`. A signed `.exe` (PyInstaller, like the SAP automation framework) is a later option —
   heavier, bundles Chromium.

---

## Development (workstation only)

```powershell
.\.venv\Scripts\python.exe -m pytest -q          # backend tests
.\.venv\Scripts\python.exe -m ruff check src tests
cd frontend; npm install; npm run build          # rebuild the UI (commit frontend/dist)
```
`onboard api` binds `127.0.0.1:8765`; the Vite dev server (`npm run dev`) runs on `:5173` and
the API allows it via CORS.
