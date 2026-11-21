# AGENTS.md

Instructions for people and coding agents (GitHub Copilot, Codex, Claude Code, Cursor) working in
this repository. Read this first. Area rules live in `.github/instructions/`; the step-by-step guide
for new people is `CONTRIBUTING.md`.

## What this is

`alletra_onboard`: a local web app that deploys an **HPE Alletra Storage MP B10000** array for HPE
field engineers. It onboards the array into HPE GreenLake and DSCC, then discovers hosts and
fabrics, writes a SAN-zoning command set, provisions block storage, sets up Remote Copy, verifies
the result and writes the as-built document. FastAPI backend (127.0.0.1:8765), React + Grommet
(HPE Design System) frontend, Typer CLI, shipped as a zip and a Windows `.exe`. It runs from a
Windows jump box next to the array. **A run is one array.**

Everything lives under `Provisioning_Automation/alletra_onboard/` (called "the app folder" below).

## Read before changing anything

| Question | File (in the app folder) |
|---|---|
| What is in scope, what is built, what is live-verified | `docs/SCOPE.md` |
| Open work | github.hpe.com issues (one per item, `BL-NN` titles); history in `docs/TRACKER.md` |
| How the code is laid out | `docs/design/HLD.md`, `docs/design/LLD.md`, `docs/STANDARD.md`; the full guide for new developers is `docs/DEVELOPER-HANDBOOK.html` (open it in a browser) |
| Domain words (array, run, fabric, VV set, ...) | `CONTEXT.md` |
| Why things are the way they are | `docs/adr/` and `docs/specs/` |
| Mistakes we already made, and the rule each one left | `docs/LESSONS.md` (read before touching wizards, state or a refactor) |
| How the UI must look and read | `docs/UX-GUIDELINES.md` |
| GreenLake API reference (offline mirror) | `reference/greenlake_api_docs/greenlake/` (repo root; start at `services.md` and `guides.md`) |

## Hard rules

1. **Never write to a SAN switch** (ADR 0012). Zoning is a copy-paste Brocade command set for the
   SAN team; `cfgenable` is shown separately. Do not add a switch write path.
2. **Array SSH is read-only, and every write over it follows one rule** (ADR 0025). Every read goes
   through the allowlist in `adapters/array/cli_client.py` (`ALLOWED_COMMANDS`; acting options, shell
   and Tcl quoting characters refused). A write over SSH needs: exact command forms each with a test,
   a client built only inside the apply of an approved plan, only on the objects that plan names, its
   removal line written before the command, a read-back after it, and no prompts. One client per kind,
   each kind argued in its own ADR; today there are two: ADR 0015's `ArrayRcCliClient` (RCIP
   addresses, `startrcopy`, Remote Copy targets) and ADR 0016's `ArraySnapCliClient` (one form:
   `createsched -f` of a `createsv -f` with an expiry and no lock). WSAPI writes also run only after
   the operator approved a plan on screen. The link check runs `checkrclink` (and, when it prints no
   latency number, an RCIP ping) through a separate diagnostic allowlist.
3. **Verification, as-built and discovery never change anything** on an array, host, vCenter or
   switch.
4. **One array per run.** Refuse a workbook that names two.
5. **Steps and modes come from the step registry** in `domain/workflow.py`; the UI renders it from
   `/app/profile`. Never hardcode a step list elsewhere.
6. **Secrets never enter git**: GreenLake client credentials, array, vCenter and switch passwords
   live in `.env` or the uploaded initialisation sheet. Lab passwords live in the jump box `.env`
   (`LAB_ARRAY_PW`, `LAB_DEFAULT_PW`). No customer names or customer addresses in fixtures,
   screenshots or docs.
7. **"Done" means run live on lab hardware.** Passing tests against captured output is *built,
   pending live run*: say so in the pull request, and keep the issue's `needs live run` label.
8. **Never commit `frontend/dist`.** It is rebuilt from `frontend/src` after each merge. A hook,
   `scripts/check.py` and review all refuse it.
9. **Tests use fakes and real captures only**: no live GreenLake, array, vCenter or switch call in
   the test suite. Parsers are pinned to captured command output in `tests/fixtures/`.

## Layout (app folder)

```
src/alletra_onboard/   domain/ (no I/O), application/ (per-context services + service.py),
                       adapters/ (one package per outside system), api/ (FastAPI), cli/ (Typer)
frontend/src/          React + Grommet UI (steps/, ui/, api.ts, useRunEvents.ts)
tests/                 unit/, contract/, fixtures/ (captured device output)
lab/                   scripts that drive the app against lab arrays (see lab/README.md)
scripts/               check.py, push_jumpbox_test.sh, after_merge.sh, release/packaging scripts
```

See `docs/design/HLD.md` (section 5) for the component diagram and `[tool.importlinter]` in
`pyproject.toml` for the enforced import boundaries.

## Commands (from the app folder)

```bash
python -m venv .venv && .venv/bin/pip install -e .[dev]   # Windows: .venv\Scripts\pip
cd frontend && npm ci && cd ..
.venv/bin/python scripts/check.py        # the pre-pull-request gate: tests, ruff, tsc, UI tests, branch rules
                                         # and the checks of docs/STANDARD.md: deps, lint, complexity, fitness,
                                         # vulture, pyright, ui-lint, knip. Known violations are listed in
                                         # quality/ceilings.toml; fix the code, never add to a list
.venv/bin/python scripts/fitness.py --tighten   # after a fix: lowers the ceilings, drops entries that are gone
scripts/install_hooks.sh                 # once per clone: commit hook, and a push hook that runs check.py
.venv/bin/python -m pytest -q            # tests only
.venv/bin/python -m ruff check .         # ruff alone (pinned in pyproject.toml); prints the listed offenders too
cd frontend && npm run typecheck         # TypeScript
cd frontend && npm test                  # frontend unit tests (vitest, pure logic, no browser)
.venv/bin/onboard ui                     # run the app (http://127.0.0.1:8765)
cd frontend && npm run dev               # UI dev server on :5173 against the running backend
cd frontend && npm run mockups           # design mockups on :5175
```

## Making a change

1. Work from an issue. Branch from an up-to-date `main`: `feat/bl-NN-short-name`.
2. Keep the change to that one item. Update the docs that describe the behaviour you changed
   (`SCOPE.md`, an ADR or spec if it is a decision, `README.md` for operator steps).
3. Run `scripts/check.py` until it says PASS. There is no CI on github.hpe.com; this is the gate.
4. Push and open a pull request on github.hpe.com. Fill in the template, paste the check block,
   write `Closes #N`. The owner reviews and squash-merges; the title becomes the commit, so make it
   `BL-NN: what changes, in plain words`.
5. Lab runs: `scripts/push_jumpbox_test.sh` sends your committed branch to the jump box (README,
   *A live run on a jump box*). Ask before running anything against lab hardware.

## Things an agent must not do

- Push to `main`, force-push, delete branches, create tags or publish releases.
- Commit `frontend/dist`, `.env`, workbooks, generated documents or anything under `archive/`.
- Run lab scripts, or call an array, switch, vCenter or GreenLake, without the user asking.
- Add a command to an allowlist, or a write path, without a test and without saying so plainly.
- Bypass checks (`--no-verify`, skipping `check.py`) or weaken a test to make it pass.
- Set `ALLOW_LISTS=1`, `ALLOW_CONFIG=1` or `ALLOW_DIST=1` for `check.py` unless the owner asked for
  that change. The check prints a WARN line when one was used; say why in the pull request.

## Domain facts that are easy to get wrong

- **GreenLake device assignment is two PATCH calls**: application + region first, subscription
  second. One call with both is rejected.
- Service catalog: the id is `serviceManager.id` (nested), not `application_id`; the filter field is
  `status` but the response field is `provisionStatus`.
- GreenLake writes return `202 + Location`: always poll to `SUCCEEDED` / `FAILED` / `TIMEDOUT`.
- Rate limits: one token bucket per endpoint family; sleep **outside** the lock.
- DSCC region codes differ from GreenLake region ids (`ap-northeast` is `jp1`, `us-west` is `us1`,
  `eu-central` is `eu1`, `eu-west` is `uk1`).
- The array's setup wizard URL must be link-local: `https://169.254.x.x` or a bracketed `fe80::`
  address (`domain/cloudinit_url.py`). A `fail-prov-*` error there is a
  GreenLake state problem (device or subscription), not a network one: fix GreenLake, do not retry.
- The DSCC browser attaches over CDP to `localhost:9222` only; the operator signs in by hand. The
  tool never handles DSCC passwords or MFA.
- Browser selectors live in `adapters/browser/locators.py`; use role, label or visible text, never
  CSS classes.
- Shipped `.ps1` files must be pure ASCII (Windows PowerShell 5.1 reads them as ANSI).
- Run event evolution (ADR 0032): a field added to an event payload in `domain/events.py` gets a
  default; a payload field or event type is never renamed or given a new meaning (a new meaning gets
  a new event type).
- Initialisation routes (`/app/profile`, `/init-sheet/upload`, `/runs/from-sheet`) keep their
  existing runtime serialisation (ADR 0032): document OpenAPI changes with
  `responses={200: {"model": ...}}` only, never add or change `response_model=`.

## Writing style (UI text, docs, commit and pull request messages)

Plain English, short sentences, no internal jargon on screen (no ADR, SPEC or version numbers in
operator messages). Say what happened, what it means and what to do next. Comments say only what
the code cannot.
