# SPEC-008 — One credential, a complete plan, names not "multiple"

**Status:** implemented 2026-09-15 — pending live run (the next SPEC-006 session proves R1–R4; R5/R6 are a
screenshot each)
**Findings addressed:** X-8 (array password typed three times per run), P-19 (a sheet volume with no export
vanishes from the plan), P-20 (member box reads *"multiple"*)
**Owner:** `application/runs/coordinator.py` (`array_credential`), `application/documents/steps.py`,
`api/app.py` + `api/schemas.py`, `frontend/src/steps/{VerifyStep,AsBuiltStep,ProvisioningBuilderView}.tsx`,
`application/provisioning/storage_provision.py` (`build_plan` notes)

## 1. Problem

Three small things the live sessions kept tripping on, none of which touches the array:

- The array password is on the sheet and the run keeps it (ADR 0005), yet Verify and As-built ask for
  it again with *"never stored"* — a promise already broken two steps earlier (X-8). Decision recorded
  as [ADR 0013](../adr/0013-one-array-credential-per-run.md).
- A volume listed on the sheet that no composed export presents simply does not appear in the plan
  (S-1 second plan: `zz_t2_vol03` absent, unremarked). The operator approved a plan that silently
  left a volume unpresented (P-19).
- Two members picked → the Grommet multi-select shows the word *multiple* instead of the names (P-20).

## 2. Requirements

**R1 — The run resolves its array credential** (`RunCoordinator.array_credential(run_id)`): the
Provisioning tab's array admin when the run holds a provisioning intent; else the DSCC system
credential (`dscc_setup.username` + `dscc_setup.password`) when that password is present; else none.
Returned as `ArrayCredential{available, source: 'provisioning'|'dscc_setup'|'none', username, host}` plus,
server-side only, the secret. `host` is `array_host(run_id)` (ADR 0011: one array per run).

**R2 — Verify and As-built use it.** `VerifyStepRequest.username/password` and
`AsBuiltStepRequest.username/password` are optional. Given → used as an override. Not given → the
run's credential. Neither → HTTP 409, detail *"This run holds no array credential — enter the array
admin username and password."* The credential never appears in the emitted events.

**R3 — `GET /runs/{id}` carries `array_credential`** (R1's public part, never the password), so the
UI knows before rendering whether to ask.

**R4 — The steps show what is true.** When `available`, Verify and As-built render one line —
*"Using the array credential from the sheet: 3paradm @ 10.132.30.121"* — with a *Use a different
credential* toggle that reveals the form; the action button is enabled. When not available, the form
renders as today with help text *"The run has no array credential; this one is used for this step
only and is not stored."* The old *"never stored"* text is gone.

**R5 — The plan names unpresented volumes.** After exports resolve, every `intent.volumes` entry
that no export presents — directly (`source_kind == volume`) or through a VV set it belongs to
(`source_kind == vvset`) — is listed in one note: *"1 volume is not presented by this plan: zz_t2_vol03"*
(*"N volumes are not …"*). Exports held back for reachability still count as presenting (the note is
about composition, not zoning). No note when every volume is presented, and none when the plan has
an `error`.

**R6 — Member names, not "multiple".** The host-set member select renders the chosen names joined
with ", "; with more than three, *"4 hosts: a, b, c, …"*.

## 3. Acceptance

- `tests/unit/test_credential.py`: R1 for the three sources; R2 through `DocumentSteps` with a fake
  `verify_fn` capturing the credential it received (sheet credential used; override wins; none → the
  precondition error); the `verify.completed` event data has no password.
- `tests/unit/test_api.py`: `GET /runs/{id}` has `array_credential` without a password field; `POST
  /runs/{id}/verify` with `{}` succeeds on a run made from a complete sheet and is 409 on a run without
  a credential; the existing explicit-credential test still passes.
- `tests/unit/test_plan_truth.py`: R5 — one unpresented volume → the note; all presented → no note;
  a volume presented only through its VV set → not in the note.
- Frontend: `tsc` clean; R4/R6 are screenshot items for the next live pass.
- Live: the SPEC-006 runner sends `{}` to Verify and As-built from this release on, so the next S-12
  run proves R1–R3.

## 4. Out of scope

Encrypting the state DB (ADR 0013 consequences). Prompting for the vCenter/switch credentials — they
are sheet-only and only Discovery/Zoning use them.
