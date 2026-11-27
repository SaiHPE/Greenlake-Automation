# ADR 0033 — Opt-in Brocade Fabric OS SAN zoning apply

**Status:** accepted 2026-11-27 (owner's decision) · **Amends:** [ADR 0012](0012-no-switch-writes-the-tool-emits-a-command-set.md),
Hard Rule 1 (`AGENTS.md`), and STANDARD S6 (`docs/STANDARD.md`) · **Applies:** [ADR 0025](0025-one-rule-for-ssh-writes.md),
[ADR 0031](0031-least-privilege-in-three-stages.md), [ADR 0032](0032-typed-run-events-and-generated-frontend-types.md) ·
**Issue:** BL-66

## Context

ADR 0012 removed an undocumented, unapproved switch staging path (`cfgsave`-alone) that had shipped
without ADR approval and left Defined and Effective configurations divergent. Under ADR 0012 the
copy-paste Brocade command set became the sole zoning output.

Field engineers running end-to-end Brocade Fabric OS deployments still face manual copy-paste
friction when they own both the array and the Brocade switches during an engagement. FOS v9.2.0b1
CLI help captured on rack13 switches (`10.132.30.111` and `10.132.30.112`) on 2026-11-27 confirmed
the `-f` syntax for `cfgenable "<cfg>" -f`, and live commit/activation behaviour (zero stdin writes,
zero PTY allocation, eliminating the `cfgsave`-alone Defined/Effective divergence ADR 0012 objected
to) plus multi-channel `cfgtransabort` were live-verified on 2026-11-27 via `lab/zoning_apply_lab.py`
(21/0; [validation record](../validation/2026-11-27-bl66-brocade-zoning-apply-live.md)).

## Decision

1. **Copy-paste remains the default deliverable.** Generating the command set (`POST /zoning/render`)
   still produces the exact copy-paste block (`cfgtransshow`, additive block, separate activation
   block) for the SAN team and never touches a switch on its own.
2. **Opt-in Brocade Fabric OS apply only.** Cisco MDS fabrics remain out of scope (ADR 0004).
   When the operator reviews the rendered Brocade command set, explicitly ticks the authorisation
   box naming the configurations and switches, and clicks **Apply to switches**
   (`POST /runs/{run_id}/zoning/apply`), the backend executes the approved host-to-array and/or
   peer-port zones on the listed Brocade switches.
3. **Read-only `BrocadeClient` stays strictly read-only.** `adapters/fabric/brocade_client.py`
   keeps `ALLOWED_READ` with zero write verbs (STANDARD S6).
4. **Separate write-scoped client under ADR 0025.** `BrocadeZoneWriter`
   (`adapters/fabric/brocade_writer.py`) subclasses `BrocadeClient` and adds `write()` accepting
   **only** five exact, prompt-free FOS forms, scoped to the approved `ZoningPlanObjects`
   (`domain/plan_objects.py`):
   - `alicreate "<alias>","<wwpn>"` (alias and colon-lowercase WWPN in `objects.aliases`)
   - `zonecreate "<zone>","<m1>;<m2>"` (exact triple in `objects.zones`)
   - `cfgadd "<cfg>","<z1>[;<z2>...]"` (`cfg == objects.active_cfg`, every zone in `objects.zones`)
   - `cfgenable "<cfg>" -f` (`cfg == objects.active_cfg`, zero stdin / zero PTY)
   - `cfgtransabort` (exact literal, used only to abort our own uncommitted transaction on mid-apply failure)
   All shell metacharacters (`| & ` $ > < \n \r \ '`) and `;` outside double-quoted member lists
   are refused, as are `cfgsave`, `cfgdelete`, `cfgclear`, `cfgdisable`, `zonedelete`, `alidelete`,
   `cfgremove`, and any name outside the approved plan.
5. **Approval-gated factory and import-linter enforcement (STANDARD S2, S3).**
   - `domain/approval.py` adds `"zoning"` to `Purpose` and isolates switch credentials on
     `Approval.switches` (`switch_creds_for`), separate from `Approval.arrays`.
   - `application/provisioning/brocade_writer_factory.py` (`make_brocade_writer`) is the single
     module allowed to import `adapters/fabric/brocade_writer.py` (`S2-brocade-writer`).
   - `application/provisioning/zoning_apply.py` is the single module allowed to import
     `application/provisioning/brocade_writer_factory.py` (`S2-brocade-factory`).
   - Plans are held in memory only (`DiscoveryZoningSteps`), single-use, and invalidated on rebuild,
     re-discovery or restart.
6. **Pre-flight safety guards, pre-write undo, abort-on-failure, and read-back (ADR 0025, STANDARD S5).**
   Before sending any write on a fabric:
   - The full reverse-order removal set (`cfgremove`, `zonedelete` per zone, `alidelete` per alias,
     `cfgenable "<cfg>" -f`) is persisted in the run's `apply_in_progress` artifact.
   - `cfgtransshow` must report no outstanding zoning transaction; otherwise apply refuses with zero
     writes.
   - A fresh `cfgshow` must confirm the effective cfg still equals the planned `active_cfg` and none
     of the planned new aliases or zones already exists; otherwise apply refuses with zero writes.
   - On any error before `cfgenable`, `zoning_apply.py` attempts `cfgtransabort` (best-effort) and
     preserves the removal set on record.
   - After `cfgenable "<cfg>" -f`, a fresh `cfgshow` verifies every planned zone appears in the
     effective configuration; the per-host provisioning export gate still opens only when the
     operator runs **Check zoning again** against the array's live logins (ADR 0012).
7. **Typed events and as-built record (ADR 0032).** `domain/events.py` registers
   `zoning.apply.started`, `zoning.applied`, and `zoning.apply.failed` (`ZoningApplyData`), and
   adds defaulted `apply_plan_id` / `apply_fabrics` fields to `ZoningRenderedData`. When a run
   opts in, the as-built document (`application/documents/asbuilt_network.py`) includes a *Switch
   zoning applied* summary and *Switch removal command set*; copy-paste-only runs are unchanged.

## Gate configuration and ceiling changes (STANDARD rules 3 and 4)

This ADR authorises three import-linter contract edits (`ALLOW_CONFIG=1`):

- `pyproject.toml`: add `S2-brocade-writer` and `S2-brocade-factory` (`protected` contracts).
- `quality/imports-type-only.toml`: add `alletra_onboard.application.provisioning.brocade_writer_factory`
  to `L3-clients-only` `allowed_importers`.

Adding opt-in switch zoning apply to four already-listed files without deleting or shortening any
existing comments raises their `[file-size]` ceilings in `quality/ceilings.toml` (`ALLOW_LISTS=1`):

- `frontend/src/api.ts`: 19,955 → 20,308 (+353)
- `src/alletra_onboard/application/documents/steps.py`: 18,508 → 18,699 (+191)
- `src/alletra_onboard/application/provisioning/steps.py`: 26,635 → 27,374 (+739)
- `src/alletra_onboard/application/runs/coordinator.py`: 18,364 → 18,511 (+147)

## Consequences

- Field engineers keep the zero-risk copy-paste workflow by default and gain an audited,
  approval-gated, prompt-free Brocade apply path when they opt in.
- The per-host export gate stays array-verified (`showportdev ns` / logins on both fabrics), never
  unlocked merely by switch apply.
- Built and verified against unit/API fakes; live verification on rack13 switches runs via
  `lab/zoning_apply_lab.py`.
