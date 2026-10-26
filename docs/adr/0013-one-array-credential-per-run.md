# ADR 0013 — One array credential per run, held by the run

**Status:** accepted 2026-09-15 · **Finding:** X-8 (`docs/ux/FINDINGS-2026-09-13.md`) · **Spec:** SPEC-008

## Context

Two security designs were shipped side by side and never reconciled.

- ADR 0001 (post-init verification over SSH) said the array password is *"supplied per-run and never
  stored"*. Verify and As-built each render a credential form with the help text *"used for this
  session only; never stored"*.
- ADR 0005 (modes) put the array admin password on the sheet's Provisioning tab, and the run keeps the
  whole `ProvisioningIntent` — array, vCenter, both switches, passwords included — in the local state
  DB for its lifetime. Discovery, Zoning check, Provision and Path verification read it from there and
  never ask.

So in a Provision-only run the operator types the same array password three times: once into the
sheet, then into Verify, then into As-built (S-1/S-4/S-8, 2026-09-14). The two prompts claim a
guarantee ("never stored") that the run has already given up two steps earlier; and in a Full
onboarding run the credential that Verify asks for is the one the DSCC setup step *set*, from the
sheet's Initialisation tab (`dscc_setup.username` / `dscc_setup.password`), which the run also holds.

## Decision

**A run holds exactly one array credential, and every step that needs the array uses it.**

1. **Source.** The credential is whatever the sheet supplied for THE array of the run (ADR 0011's
   `array_host`): the Provisioning tab's array admin when a provisioning step is in the run;
   otherwise the Initialisation tab's DSCC system credential when its password was supplied. If
   neither is present the run holds none, and the steps that need one ask for it — once each, as
   today.
2. **Steps agree.** Verify and As-built take the run's credential by default. The request's
   `username`/`password` become optional overrides (a different admin account, a rotated password);
   with none given and none held, the API answers 409 with a sentence the UI shows verbatim.
3. **The run tells the UI.** `GET /runs/{id}` carries `array_credential: {available, source,
   username, host}` — never the password. The UI shows the credential form only when
   `available` is false, otherwise one line naming the account and the array with a way to
   override.
4. **Where it lives, and where it never goes.** With the run, in the local state DB on the jump box
   (gitignored `.alletra_onboard/state.db`, the operator's own profile), for as long as the run
   exists. Never in run events, artifacts, logs, the as-built, or any API response; `SecretStr`
   masks it in every model dump that is not the DB round-trip. This is what ADR 0005 already did;
   this ADR makes it the stated rule instead of a side effect.

## Consequences

- One password, typed once, on the sheet. Verify-only runs (no sheet Provisioning tab, no DSCC
  setup password) keep their prompt — that is the case the prompt was designed for.
- ADR 0001's *"never stored"* is superseded for runs that carry a sheet credential; the help text
  changes to say what is true: *"Using the array credential from the sheet"*.
- The session runner (SPEC-006) sends no credentials to Verify/As-built, which makes every live
  session a test of this rule.
- Rotating the array password mid-run means overriding in the step (or re-uploading the sheet as a
  new run). Acceptable: the run is one array, one sitting.
- Not decided here: encrypting the state DB at rest. The jump box is a single-operator machine on
  the customer's management network; the DB holds the same secrets as the sheet sitting next to it.
  Revisit if the tool ever runs on a shared host.
