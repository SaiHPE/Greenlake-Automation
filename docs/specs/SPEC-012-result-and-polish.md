# SPEC-012 — Provision result and cross-cutting polish

**Status:** implemented 2026-09-15 (rc.23) — pending live screenshot (Provision Result card after an apply)
**Findings addressed:** P-8 (Result *Detail* is `—`), P-10 (*Continue* label before anything was applied),
A-4 (a one-sentence run section owns a page), X-1 (pixel widths), X-2 (two spinners), X-3 (a11y),
X-7 (Discovery and Provision halves: what changed since the last run of the step)
**Owner:** `adapters/array/wsapi_client.py` (`parse_hosts`, `parse_volumes`), `domain/provisioning.py`
(`ArrayHostRecord.id`, `ArrayVolumeRecord.id/wwn`), `application/provisioning/storage_provision.py`
(`apply_plan` read-back), `application/documents/asbuilt.py`, `frontend/src/steps/{ProvisionStep,
ProvisioningBuilderView,ZoningPlanView,ModeStep,DiscoveryStep,PrereqStep,ZoningStep}.tsx`

## 1. Problem

The register's tail: seven small things, each observed live, none needing the array to fix. The Result
table after an apply said *Created* seven times and `—` seven times where the array's own identifiers
(VV id, WWN, host id) belong — the event log and the WSAPI response had them. *Continue to Verify*
read the same whether the operator had created six objects or none. The as-built started a new page
for a one-sentence zoning section. The builder and zoning views sized boxes in pixels against a design
system that names sizes; the builder could show two spinners; thirteen data tables carried no
accessible title. And only Verify (SPEC-011) said what had changed since the previous run of the step.

## 2. Requirements

**R1 — Result rows carry the array's identifiers (P-8).** `ArrayHostRecord.id` and
`ArrayVolumeRecord.id`, `.wwn` are parsed from WSAPI (`id`, `wwn`). After the object loop `apply_plan`
reads hosts and volumes back **once each** and fills `ActionOutcome.detail`: host → *id 16 · persona
VMware · 2 WWNs*; volume → *id 101 · WWN 60002AC0…D495 · 1024 MiB tpvv on SSD_r6*; host set → *N
member(s): a, b*; VV set → *N volume(s): …*. Export rows keep the LUN read-back (SPEC-001 R8). A
failed apply keeps whatever detail it had.

**R2 — Continue says what continuing means (P-10).** Until an apply has succeeded in the run the
button reads *Continue to Verify without provisioning*; after one, *Continue to Verify*.

**R3 — Run sections share a page (A-4).** The two run sections (*SAN zoning designed in this run*,
*Provisioning performed in this run*) are marked so `_start_sections_on_new_pages` breaks before the
first of them only; the second flows on. Every other Heading 1 still starts a page.

**R4 — Sizes are tokens (X-1).** No `width="…px"` in the step views: the builder and alias rows use
`basis` tokens (`xsmall`/`small`/`medium`) with flex; the mode card's drawn radio is a
`grommet-icons` `RadioSelected`/`Radial` glyph.

**R5 — One activity indicator (X-2).** The builder shows progress on the button that is acting
(`busy`), never a free-standing spinner beside it.

**R6 — Every data table has a name (X-3).** Each `DataTable` carries an `a11yTitle` that says what
its rows are; each *TableSummary* is `role="status"` so a screen reader hears the count.

**R7 — Discovery and Provision say what changed (X-7).** Discovery: when the run holds an earlier
`discover.completed`, a notification *Since the discovery at HH:MM* lists hosts that appeared, hosts
that disappeared, and FC ports whose link state changed; nothing changed → *no change*. Provision:
when the run holds an earlier `storage.previewed`, plan rows whose state differs are tagged *was
<state>*. First runs say nothing about change.

## 3. Acceptance

- `tests/unit/test_plan_truth.py`: after apply, host/volume outcomes carry id/WWN from the fake's
  records; reads of `hosts` and `volumes` happen exactly twice (plan-time read is separate from the
  read-back); set outcomes list members. `tests/unit/test_asbuilt_provisioned.py`: only the first run
  section has `page_break_before`. Contract: `parse_hosts`/`parse_volumes` pick up `id`/`wwn` from the
  rack13 fixtures.
- Frontend: `tsc` clean; `grep 'px"' frontend/src/steps` finds nothing.
- Live: one screenshot of the Result card after an apply (identifiers in *Detail*, the Continue label).

## 4. Out of scope

Persona changes, set-member ids (the array has none), and cross-run history (G-3).
