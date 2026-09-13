# SPEC-001 — The provisioning plan tells the truth

**Status:** implemented 2026-09-13 (rc.8, 18 acceptance tests green) — **pending live confirmation**
(S-0 capture, then S-1 and S-2 of the second live session)
**Findings closed:** P-1, P-11, P-12 (new, found while writing this spec), P-7
**Owner:** provisioning context (`application/provisioning/storage_provision.py`,
`adapters/array/wsapi_client.py`, `domain/provisioning.py`, `frontend/src/steps/ProvisionStep.tsx`)

## 1. Problem

The plan is the approval document: the operator ticks "I have reviewed this plan and authorise
creating these objects" against it. Today it is wrong in three ways, all seen or proven 2026-09-13:

| | What the plan says | What is true |
|---|---|---|
| P-1 | every export is *Create*, every rebuild | LUNs 0/1/2 existed; the client never reads VLUNs |
| P-11 | volume *Exists* | the name exists; size / CPG / type were never read — a 10 GiB volume satisfies a 20 GiB intent |
| P-11 | host *Exists* | the host exists but lacks WWNs; apply will *change* it (`ensure_host` → `updated`) |
| P-12 | — | `ActionOutcome.status` is `Literal["created","exists","failed"]`; the client returns `"updated"` for hosts and sets. Pydantic rejects it inside the apply loop → the broad `except` records the validation error as `result.error` and **every later object (volumes, sets, exports) is skipped** after the host was already modified. Code-proven; never seen live only because no live host has yet needed a WWN added. |

## 2. Scope

In: plan row states and reasons, attribute comparison, conflict blocking, one-read-per-type,
`updated` in results, export read-back, the Plan/Result tables and the apply gate in the UI.
Out: P-8 (identifiers in every result row), removal command set (G-5), any change to what apply
*does* on the array — `ensure_*` semantics are unchanged.

## 3. Requirements

Numbered so tests can cite them. "Read" means WSAPI GET; the plan never writes (R9).

**R1 — every row has a state and a reason.** `PlannedAction.state ∈ {create, exists, update,
conflict}`; `reason` is one sentence in the operator's vocabulary saying *why*. `exists` stays as
`state != "create"` for compatibility.

**R2 — volumes are compared, not just named.** A volume whose name exists is `exists` only when
`sizeMiB == intent.size_mib` **and** `userCPG == intent.cpg` **and** provisioning type matches
(WSAPI `provisioningType` 2 → `tpvv`, 6 → `reduce`). Any difference → `conflict`, reason names the
differing attributes with both values ("on the array: 10 GiB tpvv on SSD_r6 · intent: 20 GiB").

**R3 — hosts predict what apply will do.** Host exists and carries every intent WWN → `exists`.
Exists but lacks some → `update`, reason "adds N WWN: …". Any intent WWN owned by another host →
`conflict`, reason names the other host (apply would raise). Persona differs → not a conflict (apply
never changes persona): state as above, reason appends "persona on the array: X, intent Y — left
unchanged".

**R4 — sets predict membership changes.** Host set / VV set exists with every requested member →
`exists`; missing members → `update`, reason "adds N member(s): …". Never a conflict (additive only).

**R5 — exports are checked against the array's templates.** From one VLUN read, a template is
(volume, target ref, LUN). For a `volume` source: template to `target_ref` exists → `exists`. For a
`vvset` source: expected volumes are the intent's members of that set; all have a template to
`target_ref` → `exists`; some → `update` ("N of M member volumes already exported; apply completes
the set"); none → `create`. With an explicit LUN: a template for the same source to the same target
at a *different* LUN → `conflict` ("already exported at LUN 3, intent says 7"); a *different* volume
occupying that LUN on that target → `conflict` ("LUN 7 on set:hs is taken by volume X"). Auto LUN
matches any LUN. Host-set targets: WSAPI may report the target as `set:<name>` or as `<name>` with
`type == 5 (HOST_SET)` — both normalise to `set:<name>` in the client, so the plan sees one shape.

**R6 — conflicts block apply.** `ProvisioningPlan.blockers: list[str]` collects every conflict
reason. Apply is refused by the service and disabled in the UI while `blockers` is non-empty.
`plan.error` keeps its meaning (the plan could not be built at all).

**R7 — results carry `updated`.** `ActionOutcome.status ∈ {created, exists, updated, failed}`. An
`updated` outcome is not an error and does not stop the loop (P-12).

**R8 — created exports are read back.** After the export loop, one VLUN read. An export reported
`created` whose template is not found → `failed`, detail "the array reported created but no export
was found on read-back". Found (created or exists) → detail "LUN n" (the LUN(s) the array assigned).

**R9 — the plan reads once per object type and never writes.** Six reads at most (CPGs, hosts, host
sets, volumes, VV sets, VLUNs); zero `ensure_*` calls.

**R10 — the UI shows it.** Action column: `create` → *Create* (not started, grey), `exists` →
*Exists* (complete, green), `update` → *Update* (action required, amber), `conflict` → *Conflict*
(failed, red). Reason renders under the description. Summary: "N to create · N to update · N already
exist · N conflict(s)". Blockers render as a critical notification and disable *Create storage
objects*. Result column adds *Updated*; result detail shows the read-back LUN.

## 4. Data contract

```python
class PlannedAction(BaseModel):
    kind: ActionKind
    name: str
    description: str
    state: Literal["create", "exists", "update", "conflict"] = "create"
    reason: str = ""
    exists: bool = False            # == state != "create"
    detail: dict

class ProvisioningPlan(BaseModel):
    actions: list[PlannedAction]
    notes: list[str]
    blockers: list[str]             # R6
    error: str | None

class ActionOutcome(BaseModel):
    status: Literal["created", "exists", "updated", "failed"]   # R7
    detail: str                     # R8: "LUN 0" / read-back failure text
```

Client reads (all GET, one call each):

| method | SDK call | returns |
|---|---|---|
| `hosts()` | `getHosts` | `[ArrayHostRecord(name, persona, wwns)]` — persona by WSAPI enum → name |
| `host_sets()` | `getHostSets` | `{name: [members]}` |
| `volumes()` | `getVolumes` | `[ArrayVolumeRecord(name, size_mib, cpg, provisioning_type)]` |
| `volume_sets()` | `getVolumeSets` | `{name: [members]}` |
| `vlun_templates()` | `getVLUNs` | `[VlunTemplate(volume, target, lun)]`, target normalised to `set:<hs>` for host-set VLUNs, de-duplicated (active paths collapse onto their template) |

`*_names()` remain for the builder palette and preflight.

## 5. Acceptance tests (`tests/unit/test_plan_truth.py`)

| Test | Requirement |
|---|---|
| `test_volume_exists_only_when_size_cpg_and_type_match` | R2 |
| `test_volume_conflict_names_every_differing_attribute[size,cpg,type]` | R2, R6 |
| `test_host_update_lists_the_missing_wwns` | R3 |
| `test_host_conflict_when_a_wwn_belongs_to_another_host_blocks_apply` | R3, R6 |
| `test_host_persona_difference_is_a_reason_not_a_conflict` | R3 |
| `test_hostset_and_vvset_update_list_missing_members` | R4 |
| `test_export_exists_when_the_template_is_on_the_array` | R5 |
| `test_vvset_export_partially_present_is_update` | R5 |
| `test_export_conflicts_on_lun_taken_or_lun_changed` | R5, R6 |
| `test_export_auto_lun_matches_any_lun` | R5 |
| `test_hostset_target_normalises_both_wsapi_shapes` | R5 (client) |
| `test_plan_reads_each_object_type_once_and_never_writes` | R9 |
| `test_apply_accepts_updated_and_continues_past_it` | R7 (P-12 regression) |
| `test_apply_reads_back_created_exports_and_fails_the_missing_one` | R8 |
| `test_apply_refuses_a_plan_with_blockers` | R6 (service) |
| `test_wsapi_records_parse_the_documented_shapes` | §4 (client parsers, fixture-pinned) |

Existing tests in `test_storage_services.py` keep passing unchanged except where they asserted the
old `exists` boolean semantics for exports (P-1 made those assertions wrong).

## 6. Live confirmation

**S-0 done 2026-09-13 12:33** — `tests/fixtures/rack13_wsapi/` (raw `GET /hosts /hostsets /volumes
/volumesets /vluns`, `zz_t2_*` present). It corrected the first draft in one place: a host-set
**template** is `active: false` with `hostname: "set:<hostset>"`, while the export's **active paths**
are `active: true` with `hostname` = the *member host* and the same `type: 5`. The draft's rule
"type 5 ⇒ prefix `set:`" would therefore have invented `set:10.132.30.136` from every active path.
Templates are now the inactive records taken as-is (records without an `active` field are kept).
Also confirmed: `provisioningType` 2 = tpvv, 6 = a `{"reduce": true}` volume, 1 full, 3 snp, 7 dds;
`FCPaths` repeats a WWN once per array port (hosts de-duplicate). `test_plan_against_the_captured_
array_says_everything_exists` runs the run-2 intent against the capture: every row *Exists*, no
blockers — S-1 in miniature. **Still owed on hardware:** S-1 (through the UI) and S-2 (the 10 GiB vs
20 GiB conflict).

## 7. Non-goals and risks

- The plan compares against the intent's VV-set membership, not the array's; a set someone else
  extended will show the extra volume nowhere. Acceptable — the as-built (G-0) reports array state.
- One extra WSAPI read (VLUNs) per plan. On a large array `GET /vluns` is the biggest list on the
  box; measured cost belongs in S-1.
