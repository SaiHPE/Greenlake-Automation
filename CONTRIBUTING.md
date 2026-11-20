# Contributing

Welcome. This page takes you from a new laptop to your first merged pull request. It is the one
guide for people joining the team; everything else is linked from here.

**What we build.** `alletra_onboard`, a local web app HPE field engineers run on a Windows jump
box to deploy an **HPE Alletra Storage MP B10000**: onboarding into GreenLake and DSCC, host and
fabric discovery, a SAN-zoning command set, block provisioning, Remote Copy with a failover test,
verification and the as-built document. Backend FastAPI (Python), frontend React with the HPE
Design System (Grommet). The code is in `Provisioning_Automation/alletra_onboard/`, called *the app
folder* below.

## 1. Read these first (an hour, in this order)

1. [`AGENTS.md`](AGENTS.md): the rules, the folder layout and the commands. Short; read all of it.
2. [`docs/SCOPE.md`](Provisioning_Automation/alletra_onboard/docs/SCOPE.md): the nine areas of the
   product, what is built and what is proven on hardware.
3. [`CONTEXT.md`](Provisioning_Automation/alletra_onboard/CONTEXT.md): the words we use (array,
   run, fabric, VV set, export, ...).
4. [`docs/LESSONS.md`](Provisioning_Automation/alletra_onboard/docs/LESSONS.md): the mistakes we
   already made and the rule each one left. Most of the rules on this page come from it.
5. The [issues](https://github.hpe.com/g-sai-roopesh/greenlake-automation/issues): the open work.

## 2. Access you need

Ask the owner (Sai) for each of these on your first day.

| What | Why |
|---|---|
| Collaborator on [github.hpe.com/g-sai-roopesh/greenlake-automation](https://github.hpe.com/g-sai-roopesh/greenlake-automation) | The code, the issues, pull requests and releases |
| HPE VPN on your laptop | github.hpe.com is only reachable on it |
| A github.com account, collaborator on `SaiHPE/Greenlake-Automation` | Only if you will run code on the lab: the lab jump boxes cannot reach github.hpe.com, so lab runs go through that repo |
| Remote Desktop access to the lab jump box (labrat) | Only for lab runs |

## 3. One-time setup

Install git, Python 3.12 or newer, Node 20.19 or newer, the GitHub CLI (`gh`), and on Windows Git
Bash (comes with Git for Windows). Then:

```bash
gh auth login --hostname github.hpe.com && gh auth setup-git --hostname github.hpe.com
git clone https://github.hpe.com/g-sai-roopesh/greenlake-automation.git
cd greenlake-automation/Provisioning_Automation/alletra_onboard
python -m venv .venv
.venv/bin/pip install -e ".[dev]"            # Windows: .venv\Scripts\pip install -e ".[dev]"
cd frontend && npm ci && cd ..
scripts/install_hooks.sh                     # turns on the commit and push hooks (section 6)
.venv/bin/python scripts/check.py            # must end with PASS
```

On Windows run `scripts/install_hooks.sh` from Git Bash. The push hook runs the check with the
`.venv` above, so create it before your first push.

The two install lines bring every tool the check runs, at pinned versions: ruff, import-linter and
vulture with `pip install -e ".[dev]"`; pyright, eslint and knip with `npm ci`. In a checkout you
already have, run both again after pulling. If `npm ci` stops with
`UNABLE_TO_GET_ISSUER_CERT_LOCALLY` on the HPE network, run it as `NODE_USE_SYSTEM_CA=1 npm ci`.

On a Windows laptop use `.venv\Scripts\python` wherever this page says `.venv/bin/python`.

**Certificate errors on an HPE laptop** (pip or npm cannot verify a certificate): HPE's network
inspects TLS. On macOS, export the trusted roots once and point the tools at them:

```bash
security find-certificate -a -p /Library/Keychains/System.keychain \
  /System/Library/Keychains/SystemRootCertificates.keychain > ~/hpe-ca.pem
export PIP_CERT=~/hpe-ca.pem NODE_EXTRA_CA_CERTS=~/hpe-ca.pem
```

**Run the app:** `.venv/bin/onboard ui` serves it on http://127.0.0.1:8765. For UI work, keep that
running and start `npm run dev` in `frontend/` (http://127.0.0.1:5173, hot reload). Design mockups:
`npm run mockups` (http://127.0.0.1:5175). Without lab access the app runs, but every step that
talks to an array, switch, vCenter or GreenLake will report that it cannot reach it; the test suite
is how you exercise that code offline.

## 4. How work flows

1. **Pick an issue.** Labels say the area (`area/replication`, `area/docs`, ...) and the state
   (`build`, `needs live run`, `blocked`, `in progress`). Assign yourself, and say in the issue what
   you plan to do before a large change. No issue for your idea? Open one; its title starts with
   the next free `BL-NN` (see `docs/TRACKER.md`).
2. **Branch** from an up-to-date `main`: `git switch main && git pull && git switch -c
   feat/bl-NN-short-name`. One issue per branch.
3. **Make the change** (section 5). Commit as often as you like; the merge squashes them.
4. **Run the check** (section 6) until it says PASS.
5. **Push and open a pull request** (section 7).
6. **Review.** The owner reviews every pull request. Answer each comment; a push after approval
   needs approval again.
7. **Merge.** The owner squash-merges: the pull request title becomes the one commit on `main`,
   the branch is deleted, and `Closes #N` closes the issue.
8. **Live run** if the change reaches hardware (section 8). Until it has run on the lab, the issue
   keeps `needs live run`.

You cannot push to `main`; github.hpe.com refuses it. Everything arrives through a pull request.

## 5. Making the change

**The hard rules, and why.**

| Rule | Why |
|---|---|
| Never write to a SAN switch. Zoning is a command set the SAN team pastes. | A wrong zone takes a customer's production hosts off their storage. The tool proposes; people with change control apply. (ADR 0012) |
| Array SSH is read-only, through an allowlist. Writes go through WSAPI after the operator approves a plan on screen. Remote Copy groups and the failover test use WSAPI too. (ADR 0001; ADR 0015's one write-scoped SSH client sets up Remote Copy ports, targets and links, behind the same approval) | Everything the tool does to an array must be something the operator saw and agreed to. |
| Discovery, verification and the as-built never change anything. | They are run on live customer systems to report, not to fix. |
| One array per run. | Credentials, plans and documents belong to one array; mixing them is how the wrong array gets changed. |
| Steps and modes come only from `domain/workflow.py`. | The UI renders the registry; a second list drifts from it (it happened). |
| No secrets, customer names or customer addresses in git, fixtures or screenshots. Lab addresses are fine. | The repo is shared, and `jumpbox-test` is pushed to a public github.com repo. |
| Tests never call real systems; parsers are pinned to real captured output in `tests/fixtures/`. | The suite must run anywhere, and device output never matches the documentation exactly. |
| "Done" means it ran on lab hardware. | Most of our bugs passed every test and failed on a real array. |
| Never commit `frontend/dist`. | It is built from `frontend/src` after each merge; committed by hand, it conflicts in every pull request. |

**Also update** the docs that describe what you changed: `docs/SCOPE.md` if an area's status
moves, `README.md` (app folder) for operator steps, an ADR in `docs/adr/` for a decision, a spec in
`docs/specs/` for a new feature's requirements.

**UI changes** follow [`docs/UX-GUIDELINES.md`](Provisioning_Automation/alletra_onboard/docs/UX-GUIDELINES.md):
plain operator language, no ADR, SPEC or version numbers on screen, one heading per page, and a
confirmation tick before anything that writes to an array. Attach screenshots at 1366 x 768.

**Coding agents** (Copilot, Codex, Claude Code, Cursor) read `AGENTS.md` and the rules in
`.github/instructions/` on their own. You are still the author: read what they produce, and run the
check yourself.

## 6. The check, and the hooks

There is no CI on github.hpe.com (Actions is turned off for this repository), so one command is the
gate. From the app folder:

```bash
.venv/bin/python scripts/check.py           # --quick skips the tests for a fast re-run
```

| Line | What it checks | If it fails |
|---|---|---|
| tests | the whole pytest suite; a test that reaches the network fails | fix the code, or the test if behaviour changed on purpose (say so in the pull request) |
| deps | the import rules of `docs/STANDARD.md` (import-linter) | the contract it prints says which rule and what to do |
| lint, complexity | ruff with the pinned version, compared per function with `quality/ceilings.toml` | fix the function the NEW or WORSE line names; delete the line a STALE one names |
| fitness | long files may not grow, a file may not gain a `type: ignore`, `noqa` or `eslint-disable`, documents name only code that exists, Markdown stays in today's folders, a new lesson names its test | each line says what to do |
| vulture, knip | dead code in `src` and in `frontend/` | delete it or use it |
| pyright | backend type errors per file | fix the types in the file it names |
| types | `npm run typecheck` in `frontend/` | fix the TypeScript error |
| mockups | the design mockups' TypeScript (`tsc -p mockups --noEmit` in `frontend/`) | fix the error in `frontend/mockups` |
| ui-lint | `npm run lint` in `frontend/` (eslint) | fix the error; never add to `eslint-suppressions.json` |
| ui-tests | the frontend unit tests (`npm test` in `frontend/`) | fix the code, or the test if behaviour changed on purpose |
| dist | nothing under `frontend/dist` changed on your branch | it prints the command that drops those changes |
| secrets | no token, private key or lab password in the lines you added | remove it, and tell the owner if it was ever pushed |
| lists | no known violation is added to a list or raised on your branch | fix the code and take the line back out; the owner alone lets one through (`ALLOW_LISTS=1`) |
| config | the gate's scripts and the tools' settings (ruff, pyright, eslint, tsc, knip, the import contracts) are unchanged on your branch | take the change back out; a rule change is its own pull request with an ADR, and the owner lets it through (`ALLOW_CONFIG=1`) |
| ignored | (warning) files under `src/`, `tests/` or `frontend/src/` that `.gitignore` hides | see section 9 |

The rules behind these lines are in `docs/STANDARD.md` (app folder). Violations that existed when a
check was added are listed, in `quality/ceilings.toml`, in the import contracts and in
`frontend/eslint-suppressions.json`. The lists only get shorter: fix the code rather than add a
line, and after a fix run `.venv/bin/python scripts/fitness.py --tighten`. When you move or rename
listed code, take its entry along with `scripts/fitness.py --move 'OLD KEY' 'NEW KEY'`.

It ends with a block to paste into the pull request.

The **commit hook** (`.githooks/pre-commit`, on after the setup step) refuses a commit that touches
`frontend/dist` or contains something that looks like a GitHub token or private key.

The **push hook** (`.githooks/pre-push`) runs the check before every push of your branch and refuses
the push unless it says PASS. It skips pushes with nothing to check: deleting a branch, pushing only
tags, commits the remote already has, the `jumpbox-package` and `jumpbox-test` branches, and commits
that change only `frontend/dist` (the owner's `after_merge.sh`). It checks the branch you have
checked out, so push from that branch. In a second worktree without its own `.venv`, point it at
one: `CHECK_PYTHON=/path/to/.venv/bin/python git push`.

Do not bypass either hook with `--no-verify`. It breaks the project rule (the check must say PASS
before a pull request), and the reviewer has no other gate.

## 7. The pull request

Push your branch and open the pull request on github.hpe.com (`gh pr create` works too). The
template asks for:

- **Title** `BL-NN: what changes, in plain words`. It becomes the commit message on `main`.
- **What and why**, and `Closes #N`.
- **The check block**, pasted.
- **Live run**: tick one. *Run live* (script, jump box, date, result), *not run live yet* (built,
  pending live run), or *not needed* (nothing reaches hardware).
- **The checklist**: no `frontend/dist`, screenshots for UI, allowlist changes tested, docs updated,
  no secrets or customer data.

Keep pull requests small: one issue, reviewable in one sitting. A draft pull request is a good way
to ask early whether you are on the right track.

## 8. Running on the lab

Only when the change reaches an array, switch, vCenter, host or GreenLake, and only after you have
booked the lab with the team: one person at a time, because runs collide on the same arrays and the
app's port.

1. **Once per jump box** (PowerShell, in the jump box's app folder): put the lab passwords in
   `.env`; the lab scripts read them from there and never prompt.
   ```powershell
   cd $env:USERPROFILE\Downloads\alletra_onboard
   Add-Content .env "`nLAB_ARRAY_PW=<the lab arrays' 3paradm password>"
   Add-Content .env "LAB_DEFAULT_PW=<the lab vCenter and switch password>"
   ```
2. **Once per laptop:** `gh auth login --hostname github.com && gh auth setup-git --hostname github.com`.
3. **Each run:** commit, then from the repo root (Git Bash on Windows):
   ```bash
   Provisioning_Automation/alletra_onboard/scripts/push_jumpbox_test.sh
   ```
   It sends your committed code, with `frontend/dist` built from your `frontend/src`, to
   `jumpbox-test` on github.com. It never changes your branch.
4. **On the jump box,** one paste (pick the script from [`lab/README.md`](Provisioning_Automation/alletra_onboard/lab/README.md)):
   ```powershell
   cd $env:USERPROFILE\Downloads\alletra_onboard; git fetch origin jumpbox-test; git reset --hard origin/jumpbox-test; .\.venv\Scripts\python.exe lab\ui_live_lab.py
   ```
   Each script writes `~\Downloads\<name>.zip` with PASS/FAIL lines and the evidence. Put the
   result in the pull request.
5. **When you finish,** put the jump box back on released code: run the push script from an
   up-to-date `main`, then the same paste without the last command.

Read a lab script's header before running it: it says what it changes. Scripts that create objects
name them `zz_...` and remove them at the end. A new lab script follows the rules in `lab/README.md`.

## 9. Things that will trip you up

- **Git ignores your new file.** The root `.gitignore` ignores whole file types everywhere
  (`*.json`, `*.txt`, `*.csv`, `*.yaml`, `*.html`, `*.docx`, ...) because lab dumps once leaked
  passwords. If your file is clean, add an exception for its folder in the same pull request.
  `check.py` lists such files.
- **`frontend/dist`.** Never commit it; if it shows as changed after `npm run build`, run
  `git checkout -- Provisioning_Automation/alletra_onboard/frontend/dist`.
- **The lab jump boxes cannot reach github.hpe.com.** That is why lab runs go through github.com
  and the `.exe` release is built on a laptop on the VPN.
- **github.com is public.** Anything in a commit you send with the push script is visible to
  anyone. The hook and `check.py` catch tokens and lab passwords; customer data is on you.
- **Windows PowerShell 5.1** reads `.ps1` files as ANSI. Shipped `.ps1` files must be pure ASCII:
  no smart quotes, no dashes other than `-`.
- **Line endings** are fixed by `.gitattributes`. If `git status` ever shows many files changed
  that you did not touch, stop and ask before committing.

## 10. Owner tasks (for reference)

Reviewing and merging, `scripts/after_merge.sh` (rebuilds `frontend/dist`, refreshes
`jumpbox-package` and the `latest` release zip) and tagged releases are the owner's. They are
described in the app folder's [README](Provisioning_Automation/alletra_onboard/README.md), sections
*Reviewing and merging* and *Releasing*.

## 11. Where things are

| Need | Where |
|---|---|
| Rules, layout, commands | [`AGENTS.md`](AGENTS.md) |
| Running, releasing, the jump boxes | [app README](Provisioning_Automation/alletra_onboard/README.md) |
| What is built and proven | `docs/SCOPE.md` |
| Why a decision was made | `docs/adr/`, `docs/specs/` |
| How the code fits together | `docs/DEVELOPER-HANDBOOK.html` (open in a browser; the one-stop guide), then `docs/design/HLD.md` and `docs/STANDARD.md` |
| Evidence from past lab runs | `docs/validation/` |
| GreenLake API reference, offline | `reference/greenlake_api_docs/greenlake/` (repo root) |
| Old plans and tools | `archive/` (read only) |

## 12. Getting help

Ask in the issue you are working on, so the answer stays with the work. For anything about access,
the lab schedule or priorities, ask the owner directly.
