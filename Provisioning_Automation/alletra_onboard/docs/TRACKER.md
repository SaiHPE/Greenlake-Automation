# Pending work tracker

The ONE list of open items. `SCOPE.md` says where each of the nine areas stands; this file says what is
left, who has it, and what blocks it. The status workbook (`alletra mp init and prov status-updated.xlsx`)
is the management view — its row is in the **Sheet** column.

Rules:
- Every open item has an ID here. New work gets a new ID before it starts.
- Close an item in the same commit that finishes it: move it to *Closed* with the date and the evidence
  (commit, validation file, report). Never delete a row.
- "Done" means run live, not only tests passing (LESSONS). Built-but-not-run stays under *Test live*.

Status: `todo` · `doing` · `blocked` · `done`

## Next up (in order)

| ID | Item | Owner | Status | Sheet | Next step / notes |
|---|---|---|---|---|---|
| BL-01 | **Zoning pre-selects every array port on the host's fabric** (field request: odd host port → every odd-fabric array port) | Sai + dev | todo | B.5 | Confirm the rule, then change `recommendedSelection` in `frontend/src/steps/ZoningPlanView.tsx` (today: one port per controller node). |
| BL-02 | Docs catch-up: SCOPE.md (init, zoning, as-built are live-verified), SPEC-014 (09-28 zoning name rules), validation record for 2026-09-28, copilot-instructions | dev | todo | B.10 | After BL-01. |
| BL-03 | Record the live initialization run | Sai → dev | blocked | B.10 | Needs date, array serial, GreenLake region of the from-scratch run. |
| BL-04 | Zoning name checks, live spot-check (duplicate new alias; alias already on switch; zone name > 64) | Sai | todo | B.6 | rack13, read-only, ~5 min: type the names in step 2, see the pair under *skipped*. Paste nothing. |
| BL-05 | Demo recording | Sai | todo | B.9 | After BL-01 and BL-04. |
| BL-06 | Status workbook refresh | dev | todo | — | After each closed item. |
| BL-07 | Dependabot: 4 alerts on github.com/SaiHPE/Greenlake-Automation | dev | todo | — | Bump, full test run, push both remotes. |

## Test live (built, not yet run on hardware)

| ID | Item | Owner | Status | Sheet | Blocked by |
|---|---|---|---|---|---|
| BL-10 | Linux / HPE VME host read over SSH (SPEC-014 R4) | Sai | blocked | A.4, B.4 | A Linux login (root or passwordless sudo). Then `spec014.cmd … -LinuxHost -LinuxAddress -LinuxUser -LinuxOs`. |
| BL-11 | iSCSI export (S-9) | Sai | blocked | B.6 | An iSCSI host on rack13 (`pending.ps1 -Iscsi`). |
| BL-12 | ESXi shows the volume *Visible* after a rescan (SPEC-013) | Sai | todo | B.6 | ~10 min on rack13. |
| BL-13 | Vault / Landing Zone end to end (T-0006) | Sai | blocked | B.6 | Network path from a CRV jump box to LZ array + vCenter and VZ vCenter + switches. Substitute evidence: rack13 60/60. Optional read-only extras: VZ verify + as-built; an LZ capture replayed offline. |

## Build (not started or partial)

| ID | Item | Area | Status | Sheet | Notes |
|---|---|---|---|---|---|
| BL-20 | Replication (Remote Copy) | 5 | todo | Replication B.1 | Research done: `docs/research/2026-09-19-replication-two-arrays.md` — decisions listed there are needed before a spec. |
| BL-21 | Snapshots + schedules | 5 | todo | — | DSCC protection policies, or `createsv` / `createsched`. |
| BL-22 | HLD document | 9 | todo | — | |
| BL-23 | LLD document | 9 | todo | — | |
| BL-24 | Health / performance reporting (DSCC, Data Ops Manager, InfoSight) | 8 | todo | — | |
| BL-25 | VLAN configuration (read-only today) | 3 | todo | — | |
| BL-26 | Peer-port configuration (read-only today) | 3 | todo | — | |
| BL-27 | Migration: source-array discovery, peer setup and zoning | 2, 3 | todo | — | |
| BL-28 | Alletra MP Unified File | 6 | todo | — | Research first. |
| BL-29 | GreenLake for File (GL4F) | 7 | todo | — | Research first; gated on file API entitlements. |
| BL-30 | Tool approved as tenets | — | todo | B.11 | Management. |

## Closed

| ID | Item | Closed | Evidence |
|---|---|---|---|
| — | Initialization end to end (GreenLake → Cloud Connectivity → DSCC) on a fresh array | before 2026-09-29 | Operator-confirmed; record owed under BL-03. |
| — | Discovery (ESXi via vCenter, array, Windows over WinRM, sheet lookups), provisioning FC, verify, as-built | 2026-09-28 | rack13: session.ps1 60/60 (09-19), 59/1 with the 1 an ssh typo (09-28, fixed dde5ed5); spec014.ps1 40/0/2. |
| — | Tool-designed zone logs a host in (G-1) | 2026-09-17 | rack13. |
| — | Host-join / zoning bug sweeps (persona, OS, iSCSI host on array, alias and zone-name clashes, zone length, volume size) | 2026-09-28 | e083406, 486dfa8, ffdf900, a0cbb04. |
