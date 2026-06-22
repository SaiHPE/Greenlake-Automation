# Alletra Onboard

Operator automation for onboarding an **HPE Alletra MP B10000** into **HPE GreenLake + DSCC**.
It runs as a local web app (`onboard ui`, or the packaged `.exe`) that drives three components:

| Step | Component | What it does | How it runs |
|---|---|---|---|
| **A** | GreenLake REST | register device → assign to Data Services → add/apply subscription → verify | headless HTTP (anywhere with internet) |
| **B** | Cloud Connectivity Wizard ("cloudinit") | fill the on-array wizard, stop at Review for the operator to Submit | Playwright, **launches** its own browser at the array's `169.254.x` URL |
| **C** | DSCC "Set Up System" wizard | fill Welcome→Network→Time→Attributes→System, stop at the credential | Playwright, **attaches** to a logged-in Chrome (DSCC SSO) |
| **D** | Post-init verification *(optional)* | SSH into the initialised array, read the running config via `show*`, report per-field whether it matches what was onboarded | **read-only** SSH (paramiko); never writes |

The web app is a guided 7-step flow (Configure → Array details → GreenLake → Cloud
Connectivity → DSCC → Verify → Finish) built with **React + the HPE Design System**
(`grommet-theme-hpe`) and served by the FastAPI backend.

---

## Where it runs (the jump box does everything)

The **jump box is the primary host** and runs the whole flow (A + B + C) from the one web app:

- **A (GreenLake REST)** — needs internet + credentials (the jump box has both via the lab proxy).
- **B (cloudinit) must run on the jump box** — only it sits on the array's link-local subnet and can reach `https://169.254.x.x/cloudinit`.
- **C (DSCC)** — used to hang on the jump box ("Authenticating…"); both causes are fixed: the browser launcher now passes the proxy to Chrome, and the in-app **Sync system clock** button corrects the drift that broke the login JWT. So DSCC works on the jump box too.

So the **jump box runs the entire flow (A + B + C) from the one web app** — no second machine needed.

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
| Jump box | `C:\Users\Administrator\Downloads\alletra_onboard` (flat copy) | `jumpbox-package` | A + B + C (primary host) |
| Laptop | `C:\Users\gsairoop\Downloads\storage automation` (full clone) | `main` | C (DSCC) fallback only |

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
automatically on every push to `main` — see *Releasing* below), extract, and **double-click
`start.cmd`** (or run it from a terminal). It bypasses the PowerShell execution policy that blocks
unsigned/downloaded scripts and self-elevates (so the in-app clock-sync works), then runs the
launcher. The PowerShell-native equivalent:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start.ps1
.\start.ps1 -Proxy http://proxy.example.net:8080   # on the jump box (pass the proxy if not in env)
```
First run creates the venv, installs the package + Playwright's Chromium, then opens the web app
at `http://127.0.0.1:8765`. The built UI is in the zip, so no Node is needed. (Plain `.\start.ps1`
may be blocked by the execution policy — use `start.cmd` or the `-ExecutionPolicy Bypass` form.)

**2. Clean flat clone (just the app, no other folders).** The `jumpbox-package` branch is a
`subtree split` of only this package, with the built UI included:
```powershell
git clone -b jumpbox-package https://github.com/SaiHPE/Greenlake-Automation.git alletra-onboard
cd alletra-onboard; .\start.ps1
```

**3. Full repo (developers).** `git clone` `main`; the app is under
`Provisioning_Automation/alletra_onboard/`.

**4. Packaged `.exe` (customers — no Python, no git, no Node).** Two self-contained Windows builds
are attached to a **tagged** GitHub Release (push a `vX.Y.Z` tag → `.github/workflows/exe.yml`
builds both on a Windows runner):
- **`alletra-onboard-win64.zip`** (~60 MB) — the **slim** build; downloads Chromium (~150 MB) on
  first launch through the proxy. Use this by default.
- **`alletra-onboard-offline-win64.zip`** (~210 MB) — **bundles Chromium**; use it where the proxy
  blocks Playwright's browser CDN.

Extract the zip and **double-click `AlletraOnboard.exe`** (inside the `AlletraOnboard\` folder).
It serves the web app at `http://127.0.0.1:8765` and opens the browser. Run it **as Administrator**
for the clock-sync; the Discovery Tool is bundled (SHA256-verified). The **MSVC runtime that
Chromium needs is bundled** (shipped next to `chrome.exe`), so no separate install is required —
on an unusually stripped/corrupted Windows you may still need
[`vc_redist.x64.exe`](https://aka.ms/vs/17/release/vc_redist.x64.exe). On first launch Windows
SmartScreen may warn (the build is unsigned) — click **More info → Run anyway**. Build locally with
`scripts\build_exe.ps1` (slim) or `scripts\build_exe.ps1 -Chromium` (offline).

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
don't carry NTP). The app handles this itself: the **Prerequisites and DSCC steps show a "Sync
system clock"** control. It reads the time from an HTTPS `Date` header through the proxy (works
wherever the app has HTTPS egress), so no NTP, scripts, or scheduled tasks are needed. **Setting
the clock needs Administrator**, so launch the app elevated (`onboard ui` / `start.ps1` from an
Administrator shell, or the `.exe` as admin) for the button to work.

Credentials (`.env`) are never in git. Enter them in the web app — on upload of the Initialisation
sheet (which carries the API Client ID/Secret/token URL), or the Configure screen.

---

## Running it — on the jump box (A + B + C)

The jump box runs the **entire flow from the web app**. Full procedure from a fresh login:

#### 1. Get the latest build
```powershell
cd C:\Users\Administrator\Downloads\alletra_onboard
git fetch origin jumpbox-package
git reset --hard origin/jumpbox-package     # keeps your .env / .venv / config\arrays.csv
git log -1 --oneline                         # confirm you're on the newest commit
```
First time on a fresh machine? Install first — see **First-time setup** above, or just run
`.\start.ps1 -Proxy http://<lab-proxy>:<port>` (creates the venv + installs Chromium).

#### 2. Launch the web app — **as Administrator**
Open an **elevated** PowerShell (right-click → *Run as administrator*) so the clock-sync can set
the system time, then:
```powershell
cd C:\Users\Administrator\Downloads\alletra_onboard
.\.venv\Scripts\onboard.exe ui              # serves http://127.0.0.1:8765 and opens the browser
```
**After updating, hard-refresh the tab (`Ctrl+Shift+R`)** — an already-open tab keeps running the
old UI. (To confirm you're on the new build: step 4 shows an **Open Discovery Tool** button and a
**Fill & connect** button.)

#### 3. Walk the seven steps in the browser
1. **Configure GreenLake** — enter the API client (Client ID / Secret + the **per-workspace token
   URL**), click **Test connection** (expect Data Services *PROVISIONED* in `ap-northeast`).
2. **Array details** — **Download CSV template** and fill it (or upload your prepared
   `config\arrays.csv`) → values appear in an editable form → **Create run**.
3. **GreenLake registration** — click **Run**; the live phase log streams in. A subscription-apply
   *warning* is non-fatal (register + assign are the success criteria).
4. **Cloud Connectivity** —
   - Click **Open Discovery Tool** (launches the HPE Discovery Tool from the Desktop).
   - Find the array's serial in it and copy its **`https://169.254.x.x/cloudinit`** link (changes every boot).
   - **Paste** the link, **review the Network values** shown in the app, then **Fill & connect**.
     The automation fills the on-array wizard and submits in one motion; a guard refuses to submit
     if the management IP doesn't match (so a wrong/link-local IP is never applied). Wait for
     **"Array connected."**
5. **DSCC Setup** —
   - If the **System clock** card shows skew, click **Sync system clock** first.
   - Click **Open DSCC browser** → sign in with your HPE GreenLake account (SSO) → open **Setup**,
     find the serial, click **Set Up System**, and stay on the **Welcome** screen.
   - Back in the app, click **Run DSCC automation** (fills through to System, stops at credentials).
   - In the browser: under **System Credentials** add the array admin secret, **Continue**, review,
     **Submit**.
   - Back in the app, click **mark complete**.
6. **Verify configuration** *(optional, read-only)* — enter the array admin **username/password**
   (the DSCC System Credential, e.g. `3paradm`) and click **Verify configuration**. The app SSHes
   into the now-initialised array, runs the `show*` commands, and reports per-field whether the live
   settings (system name, mgmt IP/netmask/gateway, DNS, NTP, timezone, …) match what you onboarded.
   It writes nothing and is safe to skip; the password is used only for that SSH session and is never
   stored. *(The `show*` output parsers are calibrated against the first live array — see
   `docs/adr/0001`.)*
7. **Finish** — summary of the run.

> Two reminders: run the app **as Administrator** (for the clock-sync button), and **hard-refresh**
> the browser after every update.

### CLI

The onboarding runs entirely from the web app; the CLI is just the launcher plus a health check:

- `onboard ui` — start the web app and open the browser (operator entry point).
- `onboard api` — start the API server without opening a browser.
- `onboard check` — read-only GreenLake readiness (auth + provisioned Data Services regions).

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
   by the in-app **"Sync system clock"** button (HTTPS time-sync, since
   NTP/UDP is blocked). With the proxy flag and a synced clock, the jump box reaches the DSCC
   console, so **A + B + C all run on the jump box** from the one web app. (The clock button
   needs the app run as Administrator.)

3. **Run state does not cross machines.** Each machine has its own SQLite DB, so a web-app run
   started on the jump box (A + B) can't be continued for DSCC on the laptop — DSCC is a
   separate CLI step there. Resolved automatically once #2 lets one host do all three.

4. **The web-app path for steps 3–5 hasn't had a full live pass.** The automations are proven
   via CLI; the UI buttons (GreenLake Run, Cloud Connectivity Fill & connect) need one
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
