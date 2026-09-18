# SPEC-013 — ESXi-side path verification (G-3)

**Status:** implemented 2026-09-18 (rc.28) — pending live (runner scenario 1 asserts the read; a
rescanned host for the *ok* state)
**Findings addressed:** G-3 (verification stops at the array; the 12 paths the customer cares about are
the ones ESXi sees)
**Owner:** `adapters/vcenter/vcenter_client.py` (one new read), `application/provisioning/path_verify.py`,
`domain/provisioning.py` (`HostPathStatus`), `frontend/src/steps/ProvisionStep.tsx` (path panel),
`application/documents/asbuilt.py` (path section)

## 1. Problem

Tier-2 path verification (`showvlun -a`) proves the ARRAY sees the host's initiators on the exported
LUNs. It cannot prove the host sees the LUN: a datastore that never appears, a path in *dead* state, or
a LUN mounted through one HBA only are invisible from the array side. The customer's acceptance test
is `esxcli storage core path list` on the ESXi host — the tool should read the same facts, read-only,
through the vCenter session it already holds.

## 2. Requirements

**R1 — One read, read-only, via the existing vCenter session.** `VCenterClient.host_paths()` reads
`HostSystem.configManager.storageSystem.storageDeviceInfo` — `scsiLun[]` (canonical name
`naa.<wwn>`, operationalState) and `multipathInfo.lun[].path[]` (adapter, state, pathState) — per
ESXi host the run discovered. No `esxcli`, no SSH to the host, nothing written. A host that is not in
vCenter (sheet-declared, array-only) is reported *not checked — not an ESXi host in this vCenter*.

**R2 — Joined on the volume WWN, never the name.** The array's `ArrayVolumeRecord.wwn`
(`60002AC0…`) is the ESXi `naa.` canonical name lower-cased; the join is on that. A volume the array
exported that ESXi has no `naa.` for is *not seen by the host* — the finding the customer would
otherwise make on day two.

**R3 — Per host, per exported volume: the host's own numbers, as a SECOND column.** `HostPathStatus`
gains `esxi_state` (*ok* = every exported volume visible with ≥2 active paths and no dead path;
*degraded* = visible, one active path or a dead path; *absent* = at least one exported volume has no
device on the host; *not_in_vcenter*; *not_read*; *not_checked*), `esxi_luns: list[EsxiLunPaths]`
(`volume`, `naa`, `present`, `paths_total`, `paths_active`, `paths_dead`, `adapters`) and `esxi_note`
(one sentence: *ESXi sees 2 volume(s) · 4 active of 4 path(s) per LUN · vmhba1, vmhba2*).
**The array-side `verdict` is never changed by the ESXi view** — revised from the proposal on
implementation: a LUN exported seconds ago is invisible to ESXi until a storage rescan, so folding the
host view into the verdict would make every fresh export read *no_path* (and fail the runner's
scenario 1 every time). Two columns, two truths: *Array view* and *ESXi view*.

**R4 — A rescan is the operator's, not the tool's.** ESXi caches device lists; a LUN exported a minute
ago may need *Rescan Storage*. The tool never triggers a rescan (it is a write to the host). When a
volume is *absent* the note says *rescan the host's storage adapters in vCenter, then Verify paths
again* — the one actionable sentence.

**R5 — The as-built carries both sides.** The path-verification table gains an *ESXi view* column
(the same sentence); hosts not in vCenter read *n/a — not an ESXi host in this vCenter*.

**R6 — vCenter unreachable degrades, never fails.** If the volume WWNs (WSAPI) or the host devices
(vCenter) cannot be read, every row says *ESXi view: not read (<one-line reason>)* and the array-side
verdict stands alone, as before.

## 3. Non-goals

Windows/Linux MPIO (G-2's territory). Triggering rescans or any write. Datastore/VMFS facts —
the LUN being visible with active paths is the acceptance criterion; what is built on it is the
customer's.

## 4. Verification

Unit: `tests/unit/test_esxi_paths.py` — `parse_storage_device` over duck-typed fakes (paths per
`naa.`, adapters named, local `mpx.` disks dropped, upper-case canonical names), join by WWN, the
ok / degraded / absent / not_in_vcenter / not_read states, the rescan sentence, a volume without a
WWN named rather than guessed. Live: the runner's scenario 1 asserts the read happened (`esxi_state`
in ok/degraded/absent, both volumes listed by `naa.60002ac0…`); the *ok* state needs a host that has
been rescanned after the export — owed live.

## 5. Size

As built: one adapter read + pure parser (~50 lines), one join (~80), a domain model, one UI column,
one docx column, 7 unit tests, 2 runner assertions. One release (rc.28).
