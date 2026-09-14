# SPEC-005 — A host set with no members is a question, not a default

**Status:** implemented 2026-09-14 (rc.10) — found live in S-1 of the second session
**Findings closed:** P-13 (new, live), P-16 (wording, new), P-14 (new, blocker pending live)
**Owner:** provisioning context (`storage_provision.py`, `domain/provisioning.py`,
`platform/init_sheet.py` header text), `ProvisioningBuilderView.tsx` copy

## 1. Problem (S-1, 2026-09-13 evening, rc.9)

The operator uploaded the run-2 sheet unchanged — its *Host sets* row `zz_t2_hs` has blank
*Members* — and built the plan. The plan said: **5 to create · 1 to update · 18 already exist**.
The one update was *Host set zz_t2_hs — 16 host(s) · adds 15 host(s)*: `.47`, `.86`,
`arcus-win137`, `zz_t2_declared`, `vmenode`, three `grp3_vmenode*` and seven `HPE_VM_*` — every
host object on the shared training array plus every ESXi host in the shared vCenter — and
`zz_t2_vol01/02` were already exported to that set. One tick and one click would have presented
this run's volumes to other teams' VME nodes.

Two things were true at once. SPEC-001 did its job: the plan said exactly what would happen and the
operator stopped. SPEC-003 made an old default dangerous: "blank members = all discovered hosts"
used to mean the vCenter inventory (already called pollution in ADR 0010); with the union it means
*every host the run can name*, including hosts that exist on the array for someone else.

Also seen: the reason for an existing iSCSI-only host read *carries all 0 WWN(s)*; the note
*Created but not yet reachable* named hosts that already exist; the default export
`zz_t2_vol03 → set:zz_t2_hs` was planned *Create* although the volume is already presented directly
to the set's member `.136` at LUN 2 (run 2 composed it that way) — a second presentation of the
same volume to the same host, which the plan did not flag.

## 2. Requirements

**R1 — Blank members block the plan.** A host set with no members (sheet *Members* blank and
nothing composed) produces a **blocker**: *"Host set X has no members — choose them in the Compose
card (or fill Members on the Host sets tab). Blank no longer means every host."* No host rows are
planned for that set; its exports are not planned. `from_simple` takes explicit `members`.

**R2 — The sheet says so.** The *Host sets* tab header reads *Members — comma-separated host
names; blank = choose in the app's Compose step*. The Compose card's membership hint reads *Pick
the members; an empty set blocks the plan.*

**R3 — Reasons fit the object.** An existing host with no FC WWNs reads *exists on the array (iSCSI
initiators; not changed by this tool)*. The reachability note reads *Not yet reachable (no login on
both fabrics): … — host objects are made or kept now; their exports wait until zoning is applied and
re-checked*, with no "Created" for hosts that exist.

**R4 — A second presentation to the same host is a conflict.** For a host-set export, a template
of the same volume to a *member host* directly (bare host name) is a conflict: *"zz_t2_vol03 is
already presented directly to member 10.132.30.136 at LUN 2 — a set export would present it a
second time; remove one or the other."* Pending live: whether the array refuses this itself
(EXISTENT_VLUN) or creates a second LUN id — either way the plan must not approve it silently.

## 3. Acceptance (`tests/unit/test_plan_truth.py`, appended)

`test_blank_host_set_members_block_the_plan_and_plan_no_hosts`,
`test_iscsi_only_existing_host_reason_and_reachability_note_wording`,
`test_set_export_conflicts_when_a_member_already_has_the_volume_directly`. Existing tests that
relied on blank-means-all now pass members explicitly (deliberate: the behaviour is removed).

## 4. Live

S-1 re-run with *Members* = `10.132.30.136` and the run-2 exports composed → every row *Exists*.
