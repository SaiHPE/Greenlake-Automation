# Onboarding is decoupled into operator-selected modes

The operator picks a **mode** at the start of a run — *Full onboarding*, *Provision storage only*,
*Both*, *Verify only*, or *Custom* — and the wizard renders (and the service advances through) only
the steps that mode needs. The same workbook is reused; what changes is which steps run and which
sheet fields are required.

**Why.** The original flow forced a single linear path (Prerequisites → Init sheet → GreenLake →
Cloud Connectivity → DSCC → Verify). To verify or (now) provision an **already-initialised** array,
the operator had to walk the whole init chain — effectively re-running initialisation on a live array
just to reach the step they cared about. That blocks the real test/operate loop.

## Design

- A **step registry** (`StepDef{key, label, phase, kind}` in `domain/workflow.py`) is the single
  source of truth for step identity and order. `kind ∈ {init, provision, verify}`.
- `RunMode` + `RunRecord.mode` / `selected_steps` record the choice (persisted for free via the run's
  JSON payload; pre-mode rows deserialize as `FULL_ONBOARDING`).
- `enabled_steps(mode, selected)` derives the step list; `initial_phase` lands a new run on its first
  enabled step; `next_enabled_phase` makes the A→B→C auto-advance skip deselected init steps.
- **Conditional sheet validation** (`required_keys_for`): only the fields the selected steps need are
  required. A verify-only / provision-only sheet needs serial + array IP, not GreenLake creds or DSCC
  contact details.
- The frontend mirrors this: a `ModeStep` chooser, then a **mode-derived step list** (replacing the
  old static `STEPS` + `maxStep` watermark); resume maps the persisted phase to a step within that list.

## Non-negotiables kept

- **The backend stays permissive.** Step endpoints don't hard-gate on ordering (they never did); the
  mode shapes the *rendered* path and the *advance*, not a lock. This keeps the test loop flexible.
- **Backwards compatible.** Default is `FULL_ONBOARDING`, which reproduces the previous behaviour
  exactly (the existing step-transition tests are unchanged).

## Secrets-in-sheet decision (provisioning)

Provisioning needs live credentials for the array, vCenter, and both SAN switches. Unlike onboarding
(where the array admin password is entered per-run in the DSCC wizard and never stored), these are
**customer-supplied on the Provisioning tab and parsed from the workbook** — the operator's deliberate
choice, since the customer provides them and that is the only place they exist. The workbook is a
gitignored, operator-held artifact and must be treated as a secret (no commit; careful temp handling).
The intent (with passwords) is persisted only in the gitignored local state DB, the same way the
onboarding work item already preserves its subscription key.

## Considered alternatives

- **Per-step "skip" toggles with no up-front mode** — rejected: the operator wants to declare intent
  once at the start ("I'm just provisioning"), not click through skips.
- **Separate apps / entry points per slice** — rejected: one workbook, one wizard, one run model is
  simpler to ship and keeps resume/state uniform.
- **A backend hard state-machine enforcing the mode** — rejected: it would fight the deliberately
  permissive, operator-gated design and make ad-hoc re-runs during testing painful.
