# Alletra Onboard

Operator automation for deploying an **HPE Alletra MP B10000**: onboarding into **HPE GreenLake +
DSCC**, then discovery, SAN-zoning command sets, block provisioning, verification and the as-built
document. **Scope and current status per area: [docs/SCOPE.md](docs/SCOPE.md).** It runs as a
local web app (`onboard ui`, or the packaged `.exe`). The onboarding slice drives three components:

| Step | Component | What it does | How it runs |
|---|---|---|---|
| **A** | GreenLake REST | register device → assign to Data Services → add/apply subscription → verify | headless HTTP (anywhere with internet) |
| **B** | Cloud Connectivity Wizard ("cloudinit") | fill the on-array wizard, stop at Review for the operator to Submit | Playwright, **launches** its own browser at the array's `169.254.x` URL |
| **C** | DSCC "Set Up System" wizard | fill Welcome→Network→Time→Attributes→System, stop at the credential | Playwright, **attaches** to a logged-in Chrome (DSCC SSO) |
| **D** | Post-init verification *(optional)* | SSH into the initialised array: per-field config check vs. what was onboarded, **plus** the `checkhealth` issue summary + inventory | **read-only** SSH (paramiko); never writes |

The web app is a guided step flow built with **React + the HPE Design System** (`grommet-theme-hpe`)
and served by the FastAPI backend. The operator picks a **mode** (Full onboarding / Provision only /
Both / Verify only / Custom), which selects the steps: GreenLake → Cloud Connectivity → DSCC →
Discovery → SAN Zoning → Provision storage → Verify → As-built. The `init-only` build profile ships
only the onboarding steps as the "Alletra MP Initialization" accelerator.

---

## Where it runs (the jump box does everything)

The **jump box is the primary host** and runs the whole flow (A + B + C) from the one web app:

- **A (GreenLake REST)** — needs internet + credentials (the jump box has both via the lab proxy).
- **B (cloudinit) must run on the jump box** — only it sits on the array's link-local subnet and can reach `https://169.254.x.x/cloudinit`.
- **C (DSCC)** — used to hang on the jump box ("Authenticating…"); both causes are fixed: the browser launcher now passes the proxy to Chrome, and the in-app **Sync system clock** button corrects the drift that broke the login JWT. So DSCC works on the jump box too.

So the **jump box runs the entire flow (A + B + C) from the one web app** — no second machine needed.

---

## Repositories & machines

GitHub (HPE Enterprise): **`github.hpe.com/g-sai-roopesh/greenlake-automation`** (`origin`). The
earlier `github.com/SaiHPE/Greenlake-Automation` is no longer reachable and is kept only as the
`github-com` remote on the dev workstation. There are **two branches** that matter:

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

**Dev workstation → GitHub** (after changing the package). Push `main`, refresh the subtree branch
so the jump box can pull it, then publish the release zip (Actions cannot do it — see *Releasing*):

```powershell
# from the repo root, after committing to main
git push origin main
git branch -D jumpbox-package
git subtree split --prefix=Provisioning_Automation/alletra_onboard -b jumpbox-package
git push -f origin jumpbox-package
cd Provisioning_Automation\alletra_onboard; .\scripts\publish_release.ps1     # refresh /releases/latest
```
Do this **every time** a push to `main` touches the package, or the jump box will lag.
If a UI source file changed, run `npm run build` in `frontend/` and commit the new `frontend/dist`
**before** pushing (`publish_release.ps1` rebuilds it for the zip regardless).

Authentication on the workstation is the GitHub CLI: `gh auth login --hostname github.hpe.com`
once, then `gh auth setup-git --hostname github.hpe.com` so plain `git push` uses the same token.

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
the [latest release](https://github.hpe.com/g-sai-roopesh/greenlake-automation/releases/latest)
(refreshed on every release — see *Releasing* below), extract, and **double-click
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
git clone -b jumpbox-package https://github.hpe.com/g-sai-roopesh/greenlake-automation.git alletra-onboard
cd alletra-onboard; .\start.ps1
```

**3. Full repo (developers).** `git clone` `main`; the app is under
`Provisioning_Automation/alletra_onboard/`.

**4. Packaged `.exe` (customers — no Python, no git, no Node).** Three self-contained Windows builds
are attached to a **tagged** GitHub Release (built on Windows with
`scripts\publish_release.ps1 -Tag vX.Y.Z -BuildExe`, or by `.github/workflows/exe.yml` once a
self-hosted Windows runner exists):
- **`alletra-onboard-win64.zip`** (~60 MB) — the **slim** build. It **drives an already-installed
  Chrome/Edge** (which almost every Windows box has) — no download. Only if *no* branded browser is
  present does it download Chromium (~150 MB) on first launch. Use this by default. (Force a choice
  with `ALLETRA_BROWSER_CHANNEL=chrome|msedge|chromium`.)
- **`alletra-onboard-offline-win64.zip`** (~210 MB) — **bundles Chromium**; use it on a locked-down
  box with **no** Chrome/Edge installed *and* no route to Playwright's browser CDN.

Extract the zip and **double-click `AlletraOnboard.exe`** (inside the `AlletraOnboard\` folder).
It serves the web app at `http://127.0.0.1:8765` and opens the browser. Run it **as Administrator**
for the clock-sync; the Discovery Tool is bundled (SHA256-verified). The **MSVC runtime that
Chromium needs is bundled** (shipped next to `chrome.exe`), so no separate install is required —
on an unusually stripped/corrupted Windows you may still need
[`vc_redist.x64.exe`](https://aka.ms/vs/17/release/vc_redist.x64.exe). On first launch Windows
SmartScreen may warn (the build is unsigned) — click **More info → Run anyway**. Build locally with
`scripts\build_exe.ps1` (slim) or `scripts\build_exe.ps1 -Chromium` (offline).

### Releasing

One script does it, from any machine with `git`, Node and the GitHub CLI signed in to
`github.hpe.com`: **`scripts\publish_release.ps1`**. It reads the host/owner/repo from the `origin`
remote, so the same script targets whichever GitHub the clone came from.

```powershell
cd Provisioning_Automation\alletra_onboard
.\scripts\publish_release.ps1                          # build the zip, refresh the rolling `latest` release
.\scripts\publish_release.ps1 -Tag v0.16.0-rc.6 -BuildExe   # Windows only: build the 3 .exe zips, upload to the tag
```
The rolling **`latest`** release is refreshed in place (assets clobbered, never deleted and
recreated), so `/releases/latest` never points at nothing. A tag containing `-` (an `rc`) is
published as a **pre-release**.

**Why not GitHub Actions?** `.github/workflows/release.yml` and `exe.yml` do exactly the above, but
`github.hpe.com` is GitHub Enterprise Server: there are no GitHub-hosted runners, and as of
2026-09-12 Actions is disabled by enterprise policy for this user-owned repository (enabling it
via the API returns 204 and stays `false`; no runner packages are offered). The workflows are kept
current and target `[self-hosted, windows, x64]`; the day a runner can be registered (Settings →
Actions → Runners, on a Windows box with Node 20, Python 3.12 and `gh`), they take over untouched.

To build the zip without publishing (needs Node):
```powershell
.\scripts\build_release.ps1     # -> release\alletra-onboard-<version>.zip + .sha256
```
The zip excludes `node_modules`, `.venv`, tests, and captures — just `src/`, the prebuilt
`frontend/dist/`, `config/arrays.example.csv`, the scripts, and `start.ps1` (~210 KB). Bump the
version in `pyproject.toml` (and `src/alletra_onboard/__init__.py`, `frontend/package.json`) to
change the versioned asset name.

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
6. **Verify config & health** *(optional, read-only)* — enter the array admin **username/password**
   (the DSCC System Credential, e.g. `3paradm`) and click **Verify config & health**. The app SSHes
   into the now-initialised array and reports two things: (a) **configuration** — per-field whether the
   live settings (system name, mgmt IP/netmask/gateway, DNS, NTP, timezone, …) match what you onboarded;
   and (b) **array health** — the `checkhealth -svc -detail` issue summary (cage/iLO/CDM/RC/security…)
   plus inventory/capacity (`showinventory`, `showcpg`, `showpd`). It writes nothing and is safe to
   skip; the password is used only for that SSH session and is never stored. *(The output parsers are
   calibrated against the live array — see `docs/adr/0001`.)*
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

## Status and open items

The per-area status table and the order of work live in **[docs/SCOPE.md](docs/SCOPE.md)**; the
incident→rule register is [docs/LESSONS.md](docs/LESSONS.md); the latest hardware run is
[docs/validation/2026-08-31-rack13arcus-live-test.md](docs/validation/2026-08-31-rack13arcus-live-test.md).
In short (as of v0.16.0-rc.5):

1. **Live run owed.** Discovery, zoning and provisioning fixes since 2026-08-31 are verified only
   against captured command output — the current build has not been driven through the app on
   hardware. That is the first thing to do. The lab cleanup and SAN-team disclosure from that
   test are also still owed (see its *Owed* section).

2. **Windows/Linux hosts not in vCenter** are only inferred array-side or typed into the Hosts
   tab. Agentless log-in discovery (OS / WWPN / multipathing) is the next feature.

3. **Snapshots and replication** are not started; research before build.

4. **Subscription key for the target lab array is unresolved.** The factory activation produced
   AutoPass on-array licenses + an EON order number — **not** a GreenLake "Storage Central"
   subscription. Until one is obtained, the apply-subscription phase warns (non-fatal; register +
   assign still succeed). **Action:** get/confirm the array's own GreenLake subscription key.

5. **DSCC credential entry is manual by design.** The "Create Secret" modal was never reliably
   captured, and the array admin password is sensitive, so the operator enters it in the wizard.

6. **The tool never writes to a SAN switch** (ADR 0012). Zoning is delivered as a copy-paste
   command set for the consultant; this is scope, not a gap.

---

## Development (workstation only)

```powershell
.\.venv\Scripts\python.exe -m pytest -q          # backend tests
.\.venv\Scripts\python.exe -m ruff check src tests
cd frontend; npm install; npm run build          # rebuild the UI (commit frontend/dist)
```
`onboard api` binds `127.0.0.1:8765`; the Vite dev server (`npm run dev`) runs on `:5173` and
the API allows it via CORS.
