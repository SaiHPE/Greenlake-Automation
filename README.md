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

## Repositories, branches and machines

**One home: [github.hpe.com/g-sai-roopesh/greenlake-automation](https://github.hpe.com/g-sai-roopesh/greenlake-automation)**
(HPE GitHub Enterprise, private). The git remote is `origin`. All code, pull requests and releases
live there. The lab jump boxes cannot reach it, so **live lab runs only** go through a public
github.com repo, [SaiHPE/Greenlake-Automation](https://github.com/SaiHPE/Greenlake-Automation), which
carries the `jumpbox-test` branch and nothing else that matters: no releases, Actions off, never
push `main` or tags there. It is public so jump boxes fetch with no login: never put a password,
token or customer data in anything you push there.

| Branch | What is in it | Who pushes it |
|---|---|---|
| `main` | the full repo (the app is under `Provisioning_Automation/alletra_onboard/`) | the owner (Sai), by merging pull requests |
| `feat/bl-NN-short-name` | one issue (`BL-NN`), branched from `main` | the developer working on it |
| `jumpbox-package` | the app folder only, at the branch root (`git subtree split` of `main`), for anyone who clones just the app (*Getting the app*, option 2) | the owner, after every merge to `main` |
| `jumpbox-test` (github.com only) | the app folder from any commit, for a live lab run; scratch, force-pushed | the developer with the lab booked, with `scripts/push_jumpbox_test.sh` |

| Machine | Folder | Pulls | Used for |
|---|---|---|---|
| Developer laptop | your clone of the full repo | `main` + your branch | code, tests, the UI dev server, mockups |
| labrat jump box (Windows, 10.203.101.230) | `%USERPROFILE%\Downloads\alletra_onboard` | `jumpbox-test` from github.com | live runs against the lab arrays |
| rack13arcus jump box (Windows) | the same layout | the same | live runs (onboarding, CRV) |
| A Windows laptop on the HPE VPN | a full clone | the release tag | building and publishing the `.exe` release |

**The lab jump boxes cannot reach github.hpe.com**, hence github.com for lab runs and a laptop on
the HPE VPN for the `.exe` release. **The built UI (`frontend/dist`) is committed**, so jump boxes
need no Node.

### One-time setup

**Developer laptop.** Install git, Python 3.12, Node 20 and the GitHub CLI (`gh`), then:
```bash
gh auth login --hostname github.hpe.com        # browser login with your HPE account
gh auth setup-git --hostname github.hpe.com    # plain git uses the same login
git clone https://github.hpe.com/g-sai-roopesh/greenlake-automation.git
cd greenlake-automation
git config core.hooksPath .githooks                # refuses commits that touch frontend/dist or carry a token
cd Provisioning_Automation/alletra_onboard
python -m venv .venv && .venv/bin/pip install -e .[dev]    # Windows: .venv\Scripts\pip
cd frontend && npm ci
```
Line endings are fixed by `.gitattributes`: every clone, Mac or Windows, gets the same bytes and a
clean `git status`.

**Lab runs** (once per developer who runs on the lab): a github.com account added as a
collaborator on `SaiHPE/Greenlake-Automation` (ask the owner), then on the laptop:
```bash
gh auth login --hostname github.com && gh auth setup-git --hostname github.com
```

**Jump box** (once per machine, in PowerShell). Its clone fetches from the public github.com repo,
no login needed. The lab passwords go in the app's `.env`, which is never committed and survives
every fetch; the lab scripts read them from there, so they never prompt and no password is in git:
```powershell
cd $env:USERPROFILE\Downloads\alletra_onboard
git remote set-url origin https://github.com/SaiHPE/Greenlake-Automation.git
Add-Content .env "`nLAB_ARRAY_PW=<the lab arrays' 3paradm password>"
Add-Content .env "LAB_DEFAULT_PW=<the lab vCenter and switch password>"
```

### Day to day: developers

1. `git switch main && git pull`, then `git switch -c feat/bl-NN-short-name`.
2. Change the code. Before pushing, from the app folder: `.venv/bin/python scripts/check.py`
   (Windows: `.venv\Scripts\python scripts\check.py`). It runs the tests, ruff, the TypeScript
   check and the branch rules below, and ends with a block to paste into the pull request. There is
   no CI on github.hpe.com, so this is the check the reviewer relies on.
3. UI changes: edit `frontend/src` only. **Never commit `frontend/dist`**: the owner rebuilds it
   after each merge, and `scripts/push_jumpbox_test.sh` builds it for lab runs. The hook and
   `check.py` both refuse a branch that changes it.
4. `git push -u origin feat/bl-NN-short-name` and open a pull request into `main` on github.hpe.com.
   Write `Closes #N` in the description; squash-merging closes the issue.

A feature verified only against captured output is *built, pending live run*, not done. Say so in
the pull request and the tracker.

### A live run on a jump box

1. Book the lab with the team first: only one person at a time. Two runs collide on the app's
   port (8765) and on the same arrays.
2. Commit your work, then from anywhere in the full repo (Git Bash on Windows):
   ```bash
   Provisioning_Automation/alletra_onboard/scripts/push_jumpbox_test.sh
   ```
   It pushes exactly your committed `HEAD` to `jumpbox-test` on github.com. It never checks out,
   resets or commits anything in your clone.
3. On the jump box, one paste (change the script name):
   ```powershell
   cd $env:USERPROFILE\Downloads\alletra_onboard; git fetch origin jumpbox-test; git reset --hard origin/jumpbox-test; .\.venv\Scripts\python.exe lab\ui_live_lab.py
   ```
   `.env` and `.venv` are kept. Each lab script writes `~\Downloads\<name>.zip`; that zip is the
   result to read. If git asks `Unlink of file … failed (y/n)`, answer **`n`** and run the
   `reset --hard` again; if it still errors, `Get-Process git | Stop-Process -Force` and retry.
4. When done, leave the jump box on released code: run the push script from an up-to-date `main`,
   then the same paste without the last command.

The lab scripts are in `lab/` (never in the release zip). Each one says
at the top what it reads or changes, and the ones that create objects use a fixed `zz_*` prefix and
remove everything with that prefix at the end. Read a script before running it against an array.

### Reviewing and merging: the owner

`main` is protected on github.hpe.com (ruleset *main: pull requests only*): no force-push, no
deletion, and every change arrives by pull request with the code owner's approval
(`.github/CODEOWNERS`). Only squash merge is allowed, so each pull request lands as one commit
titled after the pull request, and its branch is deleted. The owner (repository admin) can bypass,
which is how `after_merge.sh` pushes the rebuilt `frontend/dist`.

1. Read the pull request: the template's check block must say PASS, and the live-run box must be
   honest. To try it locally: `gh pr checkout <number>`, then `scripts/check.py`.
2. Approve, then *Squash and merge*. Edit the commit title if it does not read `BL-NN: …`.
3. On your laptop, once after one or more merges:
   ```bash
   Provisioning_Automation/alletra_onboard/scripts/after_merge.sh          # --lab also updates jumpbox-test
   ```
   It updates `main`, rebuilds `frontend/dist` and pushes it if it changed, refreshes
   `jumpbox-package`, and refreshes the `latest` release zip (`--no-release` skips that). It needs
   `git subtree` (Git for Windows has it; on macOS use Homebrew git), Node 20, `gh` and PowerShell 7.

---

## Getting the app onto a machine

Three ways, easiest first. The full repo is deeply nested; you don't need to navigate it.

**1. Release zip (operators — no git, no Node).** Download **`alletra-onboard-latest.zip`** from
the [latest release on github.hpe.com](https://github.hpe.com/g-sai-roopesh/greenlake-automation/releases/latest) —
extract, and **double-click `start.cmd`** (or run it from a terminal). It bypasses the PowerShell
execution policy that blocks
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
are attached to a **tagged** release on github.hpe.com, built on a Windows laptop on the HPE VPN
with `scripts\publish_release.ps1 -Tag vX.Y.Z -BuildExe` (see *Releasing*):
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

Releases are built by the owner on their own machines and uploaded to github.hpe.com with
**`scripts\publish_release.ps1`**. Actions cannot do it: GitHub Enterprise disables Actions for
repositories owned by a person (`g-sai-roopesh`), and an enterprise policy locks that setting. The
workflows in `.github/workflows/` stay in the repo for the day it moves into an organisation; until
then they never run.

| What | Built where | Command |
|---|---|---|
| Rolling `latest` zip (`alletra-onboard-latest.zip`, for operators) | any machine with Node 20, `gh` and PowerShell 7, after every merge that touches the app | `pwsh scripts/publish_release.ps1` |
| Tagged release `vX.Y.Z` with the three `.exe` zips | a Windows laptop on the HPE VPN (PyInstaller builds for the OS it runs on; the lab jump boxes cannot reach github.hpe.com) | `.\scripts\publish_release.ps1 -Tag vX.Y.Z -BuildExe` |

**A tagged release, step by step:**

1. Bump the version in `pyproject.toml`, `src/alletra_onboard/__init__.py` and
   `frontend/package.json` in a pull request, and merge it.
2. On the owner's laptop: `scripts/after_merge.sh` (*Reviewing and merging*, above), then tag the
   same `main` commit and push the tag:
   ```bash
   git tag vX.Y.Z && git push origin vX.Y.Z      # a tag with '-' (v0.18.0-rc.1) is a pre-release
   ```
3. On a Windows laptop on the HPE VPN, with Python 3.12 and `gh` signed in to github.hpe.com:
   ```powershell
   git fetch origin --tags; git checkout vX.Y.Z
   cd Provisioning_Automation\alletra_onboard
   .\scripts\publish_release.ps1 -Tag vX.Y.Z -BuildExe
   git checkout main
   ```
   The script refuses unless the tag is on github.hpe.com and the checkout holds exactly the tagged
   code. It builds the slim, offline and init-only `.exe`, runs each one's self-test and the serve
   smoke test (it boots the app with a system proxy set), and attaches the zips and their `.sha256`
   to the tag's release. Expect it to take a while: the offline build bundles Chromium.
   No Windows laptop? Build on labrat after the push script sends it the tagged `main` (run
   `scripts\build_exe.ps1`, `-Chromium` and `-Profile init-only`, each followed by
   `dist\AlletraOnboard\AlletraOnboard.exe selftest`), copy the three `dist\*.zip` and `.sha256` to
   the laptop clone's `dist\` (Remote Desktop clipboard), check out the tag there and run
   `pwsh scripts/publish_release.ps1 -Tag vX.Y.Z` (no `-BuildExe`).
4. Record the release in `docs/TRACKER.md` (*Closed* table).

The rolling `latest` release is refreshed in place (assets replaced, never deleted and recreated),
so `/releases/latest` never points at nothing. To build the zip without publishing (needs Node):
```powershell
.\scripts\build_release.ps1     # -> release\alletra-onboard-<version>.zip + .sha256
```
The zip excludes `node_modules`, `.venv`, tests, `lab/` and captures — just `src/`, the prebuilt
`frontend/dist/`, `config/arrays.example.csv`, the operator scripts and `start.ps1`.

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
On a lab jump box: the push script and paste in *A live run on a jump box*. On a machine that reaches
github.hpe.com:
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

#### 3. Work through the run in the browser
The rail on the left lists every step; the mode decides which ones a run has (the list comes from
the app's step registry, so it is always current).

1. **Prepare.** *Prerequisites* (the GreenLake connection, the proxy, the workstation clock, and the
   workspace and DSCC set-up in GreenLake), then
   *Initialisation sheet* (download the template, fill it for **one** array, upload it; it carries
   the GreenLake client, the array and target credentials, hosts, volumes and replication rows),
   then *Mode*: Full onboarding, Provision only, Both, Provision then replicate, Verify only, or
   Custom.
2. **Onboarding** (Full onboarding and Both) is steps 3 to 5.
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
6. **Storage steps** (Provision only, Both, Provision then replicate): *Discovery* reads the array,
   vCenter, hosts and both fabrics; *SAN Zoning* checks zoning and writes the Brocade command set
   for the SAN team (the tool never writes to a switch); *Provision storage* shows the plan and
   creates hosts, sets, volumes and exports only after you tick the confirmation; *Replication* and
   *Failover test* set up Remote Copy to the peer named on the sheet and prove a failover and back.
7. **Verify configuration** and **As-built document** — read-only: the array's settings against
   what was onboarded, its status check, and the Word document for the hand-over. **Finish**
   collects the documents and the run's timeline.

> Two reminders: run the app **as Administrator** (for the clock-sync button), and **hard-refresh**
> the browser after every update.

### CLI

The onboarding runs entirely from the web app; the CLI is just the launcher plus a health check:

- `onboard ui` — start the web app and open the browser (operator entry point).
- `onboard api` — start the API server without opening a browser.
- `onboard check` — read-only GreenLake readiness (auth + provisioned Data Services regions).

### The self-checking live session (`session.ps1`)

Every zip carries `session.ps1` next to the exe ([SPEC-006](docs/specs/SPEC-006-session-runner.md)).
With the app running, in PowerShell:

```powershell
.\session.cmd -BaseSheet C:\path\to\Initialisation_sheet.xlsx
```

(`session.cmd` runs `session.ps1` with the execution policy bypassed — the zip's files carry the
"downloaded from the internet" mark, which RemoteSigned blocks; `Unblock-File .\session.ps1` is the
alternative. The sheet may stay open in Excel.)

It asks for the array, vCenter and switch passwords, refuses an array that already has `zz_s6_*`
objects, then drives six scenarios over the app's own API against a clean array — create, rerun,
size conflict, blank host-set members, verify + as-built, and cleanup by the tool's own removal
set ([SPEC-007](docs/specs/SPEC-007-removal-set.md)) pasted over SSH (one more password prompt).
It writes `session-<stamp>\report.md` (PASS/FAIL per check) and keeps every response, WSAPI read,
the docx and the SSH transcript in that folder; exit code 1 on any FAIL. Send the folder back.
It never writes to a switch and never issues a CLI command the tool did not generate.

**Run history** lives in `%LOCALAPPDATA%\AlletraOnboard\` (from rc.28), so a new zip in a new folder
keeps every earlier run; the console banner prints the folder. An older `.alletra_onboard\state.db`
beside the exe is still used when present. *Runs, Your runs* (top right) lists every run, grouped by who has to act next.

---

## Sheet fields that are easy to get wrong

The initialisation sheet replaced the older `arrays.csv` (its template is still served for scripts;
`config/arrays.example.csv`). In either:

- **The part number must be the product SKU** (e.g. `S0B84A`), **not** the box FRU/assembly number
  (`R7C75-…`); the FRU returns `HPE_GL_ERROR_NOT_FOUND`.
- **The subscription key** is the GreenLake activation key (from the activation email's
  attachment), **not** the EON order number and **not** the AutoPass on-array `.dat` license keys.
- **The cloudinit URL** changes on every boot: paste the fresh `169.254.x` URL in the app.

---

## Status and open items

What is built and what is proven on hardware, area by area: **[docs/SCOPE.md](docs/SCOPE.md)**.
Open work: the [issues on github.hpe.com](https://github.hpe.com/g-sai-roopesh/greenlake-automation/issues).
The incident→rule register: [docs/LESSONS.md](docs/LESSONS.md). Evidence from lab runs:
[docs/validation/](docs/validation/).

Two things that are scope, not gaps: **the tool never writes to a SAN switch** (ADR 0012; zoning
is a command set for the SAN team), and **the DSCC system credential is entered by the operator**
in the wizard (the tool never handles it).

---

## Development (workstation only)

```powershell
.\.venv\Scripts\python.exe scripts\check.py      # tests, ruff, TypeScript and branch rules in one go
.\.venv\Scripts\python.exe -m pytest -q          # backend tests only
cd frontend; npm ci; npm run build               # build the UI locally (never commit frontend/dist)
```
`onboard api` binds `127.0.0.1:8765`; the Vite dev server (`npm run dev`) runs on `:5173` and
the API allows it via CORS.
