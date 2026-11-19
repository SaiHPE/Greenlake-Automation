# SPEC-027 — Migration from a source array: read it, check readiness, zone the peer links

**Status:** accepted 2026-11-17 with ADR 0020 (owner's decision, with changes). **Slice 1 started
2026-11-17:** R1 (the Migration tab, parse, compose, the source password kept by the store) and R3 (the
`migrate` step, the Migrate preset, the 422 without the tab) are built, with unit tests; the step is
listed as not built yet, so a run with it is refused and the Migrate mode is greyed out. R2's read,
R4 and R5 wait for the captures (`lab/mig_pair_capture.py`, not yet run) ·
**Decision:** [ADR 0020](../adr/0020-migration-tool-prepares-hpe-imports.md) · **Research:**
[2026-11-16](../research/2026-11-16-migration-from-a-source-array.md) · **Tracker:** BL-27 · **Depends on:** SPEC-025 (BL-26, the destination's FC peer ports) · **Pattern:**
SPEC-015 (a tab and a step credential), SPEC-016 R1-R3 (read, check, plan), SPEC-010 (command set) ·
**Owner:** `domain/migration.py`, `application/migration/` (new context: `read.py`, `checks.py`,
`zoning.py`, `steps.py`), `application/platform/init_sheet.py`, `domain/workflow.py`,
`adapters/array/cli_client.py`, `frontend/src/steps/MigrationStep.tsx`

## 1. Problem

A B10000 often replaces a 3PAR, Primera or Alletra 9000. HPE moves the data with Peer Motion, run from
the B10000's UI or DSCC, over FC peer ports zoned to the source's host ports. What goes wrong in the
field happens before the import starts: the source is below the supported OS or misses a patch, a
volume sits in a Remote Copy group, a cluster is too large to move online, a peer zone lands on the wrong
fabric or uses the peer port's old WWN, the host is not zoned to the new array. The tool reads both
arrays and the fabrics already; it can find all of this and hand the SAN team the zones.

## 2. Requirements

**R1 — A new, optional tab "Migration".** Parsed only when present and non-blank; every workbook
written before this spec parses as today.

| Section | Fields | Default / rule |
|---|---|---|
| *Source array* | Management address · User · Password | Required. A read-only account is enough **for this tool** (every command in R4 runs with any role). Peer Motion itself needs a source account that can create hosts and exports; the operator gives that one to the B10000 UI or DSCC, and this tab never asks for it (ADR 0020 §1). Name, model, serial and OS are **read**, never asked. |
| *Orchestration* | Where the import runs: `array UI` / `DSCC` | `array UI`. DSCC raises the destination minimum for Primera and Alletra 9000 sources (R5 B2). |
| *Hosts to migrate* — one row per host | Host (its name **on the source array**) · Migration type (`online` / `minimally disruptive` / `offline`) · Destination CPG · Provisioning (`thin` / `reduce`) | Type **online**; provisioning **thin**. |

Refused at upload, one sentence each: source address blank or equal to the run's array; user or
password blank; no host row; the same host twice; a type or provisioning outside the list; a blank CPG.
The destination's peer ports are not on this tab (SPEC-025). Source host ports for the peer links are
not on it either: the operator ticks them on screen (R6), as in the zoning designer (nothing pre-ticked).
*Since 2026-11-19 (owner, ADR 0005): the sentence is listed at upload and on the Initialisation sheet page, and refuses the run when it is created with a step that uses this tab; it no longer stops the upload or a Full onboarding run.*

**R2 — The source is a read-only step credential (ADR 0020 §1-2).** Held by the run with the intent,
like the replication peer and the switch credentials; never in events, artifacts, logs, the as-built or
an API response. Used only through `ArrayCliClient`. No WSAPI client and no `ArrayRcCliClient` is ever
constructed with it (a unit test asserts the migration package does neither). The run's array credential
(ADR 0013) is the destination's. Every source command appears in the console (SPEC-019) under the
source's name.

**R3 — Steps and modes.** `WorkflowPhase.STORAGE_MIGRATE`; registry step `migrate` ("Migration", kind
`migrate`), served from `/app/profile`. New preset `RunMode.MIGRATE` = discover → zoning → migrate →
verify → asbuilt (Peer Motion creates the hosts and volumes on the destination, so no Provision step);
*Custom* can pick `migrate`. A run minted with `migrate` from a workbook without the tab is refused (422,
one sentence), as SPEC-015 R4.

**R4 — The read.** Over the read-only SSH client.
- Source: `showsys`, `showversion -a -b` (release, MU and the `Patches:` line), `showport`,
  `showhost -d`, `showhostset -d`, `showvv`, `showvvset`, `showvlun -a`, `showrcopy`, `showrsv -l scsi3`.
- Destination: `showsys`, `showversion`, `showport` (peer ports: Type `peer` **and** Protocol `FC`;
  an Ethernet port whose Mode reads `peer` is not one), `showtarget` (never `-rescan`), `showtarget -lun
  all`, `showcpg`, `showvv`.
- The fabric of every source port comes from the run's switch name servers, as for host ports today
  (ADR 0009 parity is the fallback, with its note).
- The read client already refuses `showtarget -rescan` (BL-46). `showrsv` joins `ALLOWED_COMMANDS`
  only after `help showrsv`, captured on each family it runs on, has been read for options that act;
  any such option goes into `_ACTION_OPTIONS` (LESSONS 46). Tests, and the pull request names the
  allowlist change.
- Parsers are pinned to captures per source family before they are written (§5). A family without a
  capture is refused with one sentence (*"The tool has not read a <family> <OS> yet …"*), never parsed
  on hope.

**R5 — Readiness check.** Blocking findings (B) stop the zoning command set and the hand-off; warnings
(W) are listed and do not. One sentence each, naming the object and the way out. The version table is
data in `domain/migration.py`, citing the matrix edition it came from.
- **B1** Source family and OS below the Peer Motion matrix for this destination OS (research §3).
- **B2** Destination OS below the matrix for the source; with `DSCC` orchestration and a Primera or
  Alletra 9000 source, below 10.4.0.
- **B3** 3PAR source missing a patch the matrix requires for its MU (`showversion` `Patches:` line).
- **B4** A named host is not on the source, or has no exported volume.
- **B5** A volume to migrate is in a Remote Copy group (out of scope here; HPE documents it separately).
- **B6** An `online` row for a host in a host set of more than 4 hosts holding SCSI-3 reservations
  (`showrsv`): *"use minimally disruptive"* (matrix note).
- **B7** A host on a persona that is not ALUA-capable, where the matrix requires ALUA (single volume
  migration; HP-UX and AIX legacy personas).
- **B8** Fewer than 2 destination peer ports `ready`, on two nodes; or more than 4 peer links planned.
- **B9** The destination CPG is missing, or its free space is below the total size of the volumes.
- **W1** Another host on the source shares a volume with a named host and is not on the tab (it is
  listed by name; HPE's tool may include it, research §10 Q5). Kept at acceptance: the storage-fleet
  API takes `set:<hostset>` as a unit to migrate, so the operator may want the whole set.
- **W2** A host's OS (from discovery) is not on the matrix: *offline is supported for it; check SPOCK*.
- **W3** A volume name already exists on the destination.
- An operator checklist (not findings, the tool cannot see them): no vVols; no Windows cluster of VMs on
  VMware moved online; RHEL clusters use network fencing; AIX ODM 3.4; a backup taken.

**R6 — Peer zoning, a command set (ADR 0012).** A designer like the zoning step's: rows are the
destination's peer ports (from SPEC-025's read), each with a dropdown of source host ports on **the same
fabric** that are target-mode host ports, `ready`, preferably on a different source node per peer port.
Nothing is pre-ticked. Each ticked pair is **one SIST zone** (one source port, one peer port). A source
port goes with one peer port only. Rendered by `render_commands` in FOS order (`cfgtransshow` first,
`cfgsave`/`cfgenable` apart). Aliases reuse `_proposed_alias` (array role, the array's serial and
`n:s:p`); the name checks of SPEC-010 R5 apply. The peer port's WWN is the one read now: a peer WWN
absent from the fabric's name server is reported as *"not logged in to the fabric: the port's WWN
changes when it becomes a peer port; cable it and read again"*.

**R7 — Host zoning to the destination.** For `online` and `minimally disruptive` rows, the hosts'
HBAs (source `showhost -d` WWNs) join the SAN Zoning step's candidates with source *migration*, and the
existing designer zones them to the destination's host ports. `offline` rows are not offered until the
import is done. Removing zones (host to source, peer zones) is not in this spec (§3, R10 later).

**R8 — Zoned and visible.** After the SAN team pastes: *Read again* shows, per peer port, whether the
source appears in `showtarget` (its node WWN, from the source's `showport`), and per host whether it is
logged in to the destination (the existing gate). The step reads *Ready for Peer Motion* only with no
blocker, every peer port seeing the source, and every online/MDM host logged in.

**R9 — Hand-off.** The tool does not create anything on the source, does not admit or import, does not
unexport (ADR 0020). The page lists what the operator enters in the B10000 UI or DSCC: source address,
hosts, volumes, migration type, CPG, provisioning, and the checklist of R5. It does not ask the engineer
to create the peer host on the source: Peer Motion is given the source credential and has no input for
a peer host, so it most likely creates it (research §10 Q3). No menu path is printed until the HPE
guide confirms it (research §10 Q1).

**R10 — Progress and result (read-only, later slice).** `showtarget -lun all` state per volume
(`discovered` → `admitted` → `importing` → `imported`), `showvv` on the destination,
`showtask -active` (added to the read allowlist then, with a test). The storage-fleet API's `GET
…/migrations` (status, percent complete, current step) could feed this instead or as well; it needs a
DSCC API client the tool does not have, so that is decided with this slice (ADR 0020 option D).
Verdict per volume: *Imported*, *Importing*, *Admitted*, *Not seen*. Path verification (SPEC-013) for
the migrated hosts. Then the removal command set: peer zones and host-to-source zones, generated only
when nothing is importing, in the order the HPE guide gives (research §10 Q4).

**R11 — As-built (later slice).** A Migration section: source (name, model, serial, OS), hosts and
volumes with sizes and type, peer links (pairs, zones), the command sets delivered, final state per
volume, when it was read.

## 3. Non-goals

Driving the import (`admitvv`, `importvv`, DSCC's wizard or its storage-fleet API, ADR 0020 option D);
any write to the source; creating the peer host on the source; configuring peer ports (SPEC-025); iSCSI
peer links; Remote Copy group migration; Nimble, Alletra 5000/6000, B10000 and non-HPE sources (OIU);
host-side actions (rescan, multipath, reboot); paired runs (ADR 0014); zone removal before R10.

## 4. Verification

**Unit**, pinned to captures: parsers per family; each R1 refusal; each R5 finding from a fixture
variant; R6 pairs (same fabric only, one source port per peer port, SIST, FOS order); the read client
accepting `showrsv -l scsi3` and refusing every acting option `help showrsv` lists (the `-rescan`
refusal is BL-46's and tested there); no write client or WSAPI client in `application/migration/`.

**Live checklist (lab pair E18U31 and the 3PAR 20850 R2; ask the owner first; ADR 0020 *Must
confirm*).** The peer ports exist and already see the source, so slice 1 and R8's visibility need no
peer-port setup, no cabling, no switch paste and no write.

| # | What | Pass |
|---|---|---|
| 0 | Destination E18U31 (DHCI_B10K, CZ2D3209YV, 10.64.154.190, OS 10.5.60, FC peer ports 0:3:2 and 1:3:2); source HPE 3PAR 20850 R2 (4UW0002142). The owner says who owns the peer ports and the 3PAR (a `Pandu_*` zone in `tests/fixtures/vz_fabric/` pairs the peer ports with another array; LESSONS 35) and gives the 3PAR's address and a read-only account | owner's answers recorded in the validation note |
| 1 | Read-only capture of both arrays by a lab script: the R4 lists, plus `help showrsv` on the 3PAR and `showport -peer` on E18U31 | files in `tests/fixtures/mig_pair/`; `showeventlog` on both arrays shows nothing from the script |
| 2 | `showversion -a -b` on the 3PAR | release, MU and patches written down. Expected (inference from fabric name fw:3313): 3.3.1 MU3, below the matrix minimum of 3.3.1 MU5 with P141, P173, P180 |
| 3 | Migration step: *Read both arrays*, one `offline` row for a host the 3PAR's owner names | page shows the 3PAR's model, serial, OS and patches, the host's volumes, and B1 if step 2 confirms 3.3.1 MU3 (B3 if it is MU5 without the patches); no B8 |
| 4 | R8 visibility, no write: `showtarget` on E18U31 | the 3PAR's node WWN 2FF70002AC07E528 on both 0:3:2 and 1:3:2 (`showport -c` already names it as their device) |
| 5 | Console | only read commands on both arrays, the 3PAR's under its own name |

The import itself waits for a source inside the matrix (ADR 0020 *Consequences*: the VZ fabric's 3PAR
8400 at fw:3321, 3PAR 7400c at fw:3315, Alletra 9060s, Primera A650s; or the Primera 630 on rack13). That
run adds: a test volume created and removed by a lab script on the source (the only source write, never
by the tool); peer zones generated by R6 and pasted by the SAN team where none exist; an offline Peer
Motion of the test volume in the B10000 UI; *Imported* (R10); and the undo, back to the step 1 capture.

## 5. Captures needed first (read-only)

First, 3PAR 20850 R2 and E18U31: the R4 lists, `help showrsv` on the 3PAR, `showport -peer` and
`showtarget -lun all` on E18U31 (BL-26's `tests/fixtures/peer_ports/E18U31/` already holds its
`showsys`, `showversion`, `showport` and `showport -peer` of 2026-11-17). Then Primera 4.6.20 and
rack13-ARCUS (now 10.6.0) with the rack13 fabrics' `nsshow`, `nscamshow`, `cfgshow`; an Alletra 9000
when one is chosen. Until a family has a capture it is refused (R4).

## 6. Size

Tab and model (~150), read and parsers (~250), checks (~200), peer-zoning designer reuse (~120), step,
API and UI (~350), ~45 unit tests. Three slices: read + readiness (§ work packet), peer and host zoning,
progress + removal + as-built.
