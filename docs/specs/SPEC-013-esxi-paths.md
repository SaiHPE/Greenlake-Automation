# SPEC-013 — ESXi-side path verification (G-3)

**Status:** proposed 2026-09-17 — awaiting approval before code
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

**R3 — Per host, per exported volume: the host's own numbers.** `HostPathStatus` gains
`esxi_luns: list[EsxiLunPaths]` with `volume`, `naa`, `paths_total`, `paths_active`, `paths_dead`,
`adapters: list[str]` (vmhba names). The verdict rule extends, not replaces: `live` requires BOTH the
array's ≥2 live paths AND, when the host is in vCenter, `paths_active ≥ 2` on every exported volume;
`partial` when either side is one path; `no_path` when either side is zero. `detail` says which side
fell short: *array sees 4 paths · ESXi sees 2 active of 4 (vmhba1 dead)*.

**R4 — A rescan is the operator's, not the tool's.** ESXi caches device lists; a LUN exported a minute
ago may need *Rescan Storage*. The tool never triggers a rescan (it is a write to the host). When the
array side is live and ESXi shows the volume absent, the detail says *rescan the host's storage
adapters in vCenter, then Verify paths again* — the one actionable sentence.

**R5 — The as-built carries both sides.** The path-verification section gains the ESXi columns
(active/total paths, adapters) for hosts in vCenter; hosts not in vCenter keep the array-only row
with *ESXi view: n/a*.

**R6 — vCenter unreachable degrades, never fails.** If the read fails, every host row says *ESXi
view: not read (<one-line reason, D-11 style>)* and the array-side verdict stands alone, as today.

## 3. Non-goals

Windows/Linux MPIO (G-2's territory). Triggering rescans or any write. Datastore/VMFS facts —
the LUN being visible with active paths is the acceptance criterion; what is built on it is the
customer's.

## 4. Verification

Unit: `tests/unit/test_esxi_paths.py` — join by WWN (mixed case, `naa.` prefix), verdict matrix
(array live × ESXi 0/1/2 active), not-in-vCenter row, rescan sentence, unreachable degrade.
Contract: a `storageDeviceInfo` fixture captured from a rack13arcus ESXi host (like
`tests/fixtures/rack13_wsapi/`). Live: the runner's scenario 1 gains three assertions (`.136`:
`esxi_luns` has 2 volumes, `paths_active ≥ 2` each, adapters named).

## 5. Size

One adapter method (~40 lines), one join + verdict extension (~60), two UI rows, one docx column,
tests. One release.
