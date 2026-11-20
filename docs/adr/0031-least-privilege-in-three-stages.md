# ADR 0031 — Least privilege on customer arrays in three stages

**Status:** accepted 2026-11-20 · **Issue:** BL-65 ·
**Relates to:** [ADR 0028](0028-one-engineering-standard-enforced-by-the-gate.md) (STANDARD S2, S3, S5),
[ADR 0025](0025-one-rule-for-ssh-writes.md), [ADR 0030](0030-the-gate-fails-where-it-only-warned.md)

## Context

STANDARD S2, S3 and S5 ask for three properties on array writes: read paths hold no write methods,
writers are built only from an operator approval, and the undo of a write is stored before it
returns. An earlier single-branch implementation (`arch/step4-least-privilege`, +1,199 net production
lines) was audited and not merged: its new undo journal had no production reader and was pruned with
cached artifacts so S5 never reached an operator, and its SQLite checkpoints inside the failover
sequence could raise mid-way and leave the pair stopped with no `FailoverRecord` or recovery action.

## Decision

Deliver least privilege in three small, independently verifiable stages:

1. **Stage 1 (merged — STANDARD S2):** split `WsapiReader` (`adapters/array/wsapi_client.py`,
   reads only) from `WsapiWriter` (`adapters/array/wsapi_writer.py`, the 14 mutating calls); move
   the apply halves to `application/provisioning/apply.py` and
   `application/replication/partnership_apply.py`; place writer factories in dedicated modules
   (`application/runs/writer_clients.py`, `application/replication/clients.py`,
   `application/snapshots/clients.py`) protected by six zero-ignore import-linter contracts
   (`S2-wsapi-writer`, `S2-rc-writer`, `S2-snap-writer`, `S2-wsapi-factory`, `S2-rc-factory`,
   `S2-snap-factory`); and turn on ruff `SLF001` for `src/` so application code cannot bypass the
   reader through `_require()`.
2. **Stage 2 (this change — STANDARD S3):** introduce `domain/approval.py` (`Approval` and
   `ApprovalError`): an identity-only in-memory value carrying `run_id`, `purpose`
   (`storage | rc_groups | rc_partnership | snapshots | failover`), the reviewed plan's array
   credentials (`arrays`), and a `spent` flag, never stored or serialised. `RunCoordinator`
   (`application/runs/coordinator.py`) is the single issuer (`issue_approval`); a run remains busy
   while its approval is unspent, and `run_approved` spends the approval in the worker thread's own
   `finally` so cancelling the coroutine cannot admit a second write while the first thread still
   runs. The three writer factories (`make_wsapi_writer`, `make_rc_writer`, `make_snap_writer`)
   obtain array credentials only via `Approval.creds_for`, and each writer refuses every write once
   its approval is spent. The step services keep their in-memory `_plan` dicts, pop the held plan
   and issue the approval together after `check_approval`; storage freezes the reviewed inputs
   (`intent`, `discovery`, `reachable_hosts`, `zoning_plan`) at preview and refuses builder edits
   while a step is running. `FailoverTestRequest` requires `authorised: true` (refusing an unticked
   or empty POST with 409) instead of adding a preview route.
3. **Stage 3 (STANDARD S5):** persist the existing result model before each write (`ProvisioningResult`,
   `ReplicationResult`, `SnapshotResult`, `FailoverRecord`), exempting the in-flight record from
   pruning, and promote an orphaned record on reopen to the existing `*.apply.failed` event so
   screens and the as-built read it without a parallel journal.

## Consequences

- Stage 1 removes every write method from read-only paths and enforces that boundary at the gate
  with minimal code (+243 for stage 1).
- Stage 2 binds every array write factory and writer to a single-use, purpose- and side-scoped
  `Approval` issued only by `RunCoordinator`, closes the unticked failover POST gap and the
  builder-edit-during-preview race, and keeps `run_failover_test`'s returns-never-raises contract
  for device failures, with no ambient contextvars or slot registry.
- Adding the six `protected` import-linter contracts and ruff `SLF001` changes what the gate
  measures (STANDARD rule 4) and seeds unavoidable third-party private-attribute accesses in
  `quality/ceilings.toml` (only `python-docx` XML handles and `hpe3parclient`'s HTTP hook). The
  gate config edits covered by this ADR are: widening `S2-wsapi-client` so `wsapi_writer` can
  subclass `WsapiReader`, widening `L3-clients-only` for `application/runs/writer_clients.py`, and
  ignoring `SLF001` under `tests/**` where tests inspect client internals. Stage 2 requires no gate
  config or list additions.
- Stage 3 builds directly on these modules without adding ambient state or a second removal set.
