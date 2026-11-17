# Research — Migration onto the B10000 from a 3PAR, Primera or Alletra 9000 (BL-27)

**Date:** 2026-11-16, updated 2026-11-17 at acceptance (§1, §4, §5, §7, §8, §10) · **Status:** research;
no code. The decisions in §9 feed [ADR 0020](../adr/0020-migration-tool-prepares-hpe-imports.md)
(accepted 2026-11-17 with changes) and
[SPEC-027](../specs/SPEC-027-migration-source-array.md) · **Tracker:** BL-27 · **Related:** BL-26 /
SPEC-025 (destination peer ports, specified in parallel), SPEC-015/016 (the replication peer as a second,
step-scoped credential), ADR 0012, 0013, 0014

## 1. Sources, graded

The SharePoint download (`GreenlakeAutomation_storage_docs_from_sharepoint/`) mislabels files again
(the 2026-09-19 note warned about this). Identify each by its title page and part number:

| File name says | It really is | Part no. / date | Trust | Used for |
|---|---|---|---|---|
| *HPE GreenLake for Block Storage Peer Motion Data Migration Support Matrix* | the SPOCK Peer Motion matrix ("BLUE = new from 10.5.6") | SPOCK, no part no.; current edition lists destination 10.5.6 | authoritative | §3 |
| *…Migrating data from HPE 3PAR to HPE Alletra Storage MP B10000…* (sd00002432) | **the RHEL implementation guide**, not a migration guide | 20-ALMPB10K-RHIG-ED12, May 2026 | n/a | nothing |
| *…from HPE Nimble Storage to … B10000* (sd00004844) | **Migrating data from VMAX** with the Online Import Utility (OIU) | 20-GRLKBLK-VMAXMP-ED1, Jul 2024 | authoritative for OIU | §4 (peer-port and zoning procedure on a B10000 destination) |
| *…from VMAX…* (sd00004731) | Migrating data from NetApp (OIU) | 20-GRLKBLK-NetappMP-ED1, Jul 2024 | authoritative for OIU | cross-check of §4 |
| *HPE Alletra MP Command Line Interface reference guide* | B10000 CLI reference | 20-ALMPB10K-CIR105-ED7, Dec 2025 | authoritative | §4, §5, §7 |
| *HPE 3PAR / Primera / Alletra 9000 CLI reference* | source-side CLI references | P29135-002a (Nov 2024), 20-PRI600-CIRQR-ED1 (Aug 2024, quick reference only), 20-ALL9000-CIR96-ED8 (Sep 2025) | authoritative | §7 |
| *Alletra MP Peer motion MOP.pdf* = *Alletra MP Replication_HLD.pdf* = *IBK-peer motion-MOP document.docx* | one field method-of-procedure, 3PAR 8400 → Alletra MP, customer and engineer names blanked or present | field document, undated | field practice; not HPE-published | §6 (what engineers actually do) |
| *PRIMARY DIRECT MIGRATION METHOD OVERVIEW.docx* | field notes for XIV/VMAX → Primera by hand (`admitvv` / `importvv`) | undated | field practice, **third-party sources** | §5 only, as evidence the CLI primitives exist |
| `reference/greenlake_api_docs/…/block-storage/` (repo) | DSCC Block Storage public API mirror, v1alpha1 | — | authoritative for what it lists | §5: **no migration resource** |
| `storage-fleet-api.yaml` on developer.greenlake.hpe.com (read 2026-11-17; not in the repo mirror) | DSCC storage-fleet public API, v1alpha1, spec version 1.4.0 | — | authoritative, alpha | §5: **migration partners and migrations** (ADR 0020 option D) |

Public pages (read 2026-11-16): SPOCK is where the matrix lives (`https://spock.hpe.com`, *Software →
Array SW: HPE GreenLake for Block Storage → Data Migration Technologies*, the path the VMAX guide gives
on its p.8). The HPE-to-HPE Peer Motion user guide for the B10000 (UI and DSCC procedure) was **not**
in the download and is the most important document still missing (§10 Q1).

## 2. The migration paths HPE documents onto a B10000

| Path | Sources | Driven from | Evidence |
|---|---|---|---|
| **Peer Motion** (data migration over FC peer ports; iSCSI from 10.5.0) | 3PAR, Primera, Alletra 9000, Nimble/Alletra 5000/6000, B10000 | **the array's own UI ("HPE GreenLake for Block Storage UI") or DSCC** | matrix p.2 *"supported by the HPE GreenLake for Block Storage UI and DSCC"*; *Supported UI* column on every table |
| Online Import Utility (OIU) | VMAX, NetApp, other non-HPE | a Windows utility (`addsource`, `createmigration`, …) over SMI-S | OIU guides (VMAX, NetApp) |
| By hand on the destination CLI: `admitvv` + `importvv` | any source that exports LUNs to the peer ports | destination CLI | B10000 CLI ED7 p.56, p.219-221; PDM field notes |
| Host-based (LVM mirror, Storage vMotion) | anything | the host | general practice; not specific to HPE docs |

The legacy *Peer Motion Utility* (3PAR to 3PAR, 3PAR to Primera) is not listed as a supported UI for a
B10000 destination in the matrix. **For a 3PAR, Primera or Alletra 9000 source the recommended path is
Peer Motion orchestrated from the B10000's UI or DSCC.**

## 3. Support matrix: Peer Motion onto the B10000 (SPOCK, edition with 10.5.6)

| Source | Models | Source OS (minimum, with later MUs/patches) | Destination OS | Protocol | Notes that bite |
|---|---|---|---|---|---|
| 3PAR | 7000, 7000c, 8000, 9000, 10000, 20000, 20000 R2 | **3.2.2 MU6, 3.3.1 MU5, 3.3.2 MU1**, each with patches installed first: 3.2.2 MU6 P122, P138, P154, P165 · 3.3.1 MU5 P141, P173, P180 · 3.3.2 MU1 P10 | 10.3.0, 10.4.0, 10.4.2, 10.4.5, 10.4.8, 10.5.0, 10.5.6 (AIX/HP-UX from 10.4.0) | FC | RC groups via Peer Motion from 10.4.0 (not HP-UX, AIX); multilink (max 4 links = 2 peer link pairs) from 10.3.0 |
| 3PAR | same | same | 10.5.0, 10.5.6 | **iSCSI** | no Windows clusters, no RC groups, no CHAP, one peer link per node, no tagged VLAN on the peer port |
| Primera | C/A630, C/A650, C/A670 | **4.4, 4.5, 4.6** (AIX/HP-UX 4.5, 4.6) | 10.3.0 … 10.5.6; **10.4.0 minimum when DSCC orchestrates** | FC | RC groups via Peer Motion from 10.5.0 |
| Alletra 9000 | 9060, 9080 | **9.4, 9.5, 9.6** (AIX/HP-UX 9.5, 9.6) | 10.3.0 … 10.5.6; 10.4.0 minimum with DSCC | FC | RC group migration not supported |
| B10000 | 10020 … 10260 | 10.5.0, 10.5.6 | 10.5.0, 10.5.6 | FC | migration of RC volumes not supported |

Host side (all HPE sources): Windows Server 2016/2019/2022 (MPIO, Failover Cluster, Hyper-V), RHEL 7.9,
8.10, 9.5, SLES 12 SP5 / 15 SP6, Oracle Linux 8.10 (standalone), vSphere 6.5, 6.7, 7.0U3, 8.0U3 (RDM and
VMDK), AIX 7.2 TL5 / 7.3 TL0-2 (ODM 3.4; ODM 3.5 not supported), HP-UX 11i v3. Notes common to the
tables:

- SCSI-3 persistent-reservation clusters: **at most 4 nodes online**; larger, use Minimally Disruptive
  Migration (MDM). Without persistent reservations, larger clusters can go online.
- Windows clusters built from VMs on VMware: MDM only. RHEL clusters: network fencing only.
- **VMware vVols are not supported.** Migration of Remote Copy volumes is not supported (B10000 source).
- Single volume migration needs an **ALUA-capable persona**; HP-UX and AIX volumes on legacy personas
  must be moved to ALUA first.
- **Offline** migration is supported for every cluster technology on SPOCK, with hosts shut down and the
  volumes un-exported throughout. Unlisted clusters: MDM, after `showrsv -l scsi3` on the source shows
  no SCSI-3 reservation.

The lab's destination runs **10.5.55** (rack13-ARCUS) and 10.5.51 (CRV VZ). The matrix lists 10.5.0
and 10.5.6 "and all subsequent applicable MUs and patches". Whether 10.5.5x counts is **unconfirmed**
(§10 Q2).

## 4. How the arrays connect: peer ports and peer zoning

From the B10000 CLI reference (ED7) and the OIU guide's destination procedure (the destination side is
the same array and the same commands whatever the source):

- A **peer port** is an FC port in connection mode `peer`, point-to-point only:
  `controlport offline <n:s:p>` then `controlport config peer -ct point <n:s:p>` (CLI p.93-102,
  OIU p.17). `-virt_ports <n>` adds up to 8 virtual peer ports. Mode changes are refused on an online port.
- `showport` lists it as Type **`peer`** ("FC port used for data migration", Connmode `peer`);
  `showport -peer` shows the peer-port detail. **Trap:** on Ethernet ports the *Mode* column also reads
  `peer` (our captures: rack13-ARCUS 0:4:3/0:4:4 `peer offline … free IP`). A data-migration peer port is
  Type `peer` **and** Protocol `FC`; the RCIP code already keys on `IP` + mode `peer` (`PortRole`).
- **The port's WWN changes when it becomes a peer port** (OIU p.17). Zoning must use the WWN read after
  the change, never one from an earlier discovery.
- Choose **two unused ports on partner nodes** as peer ports; on the source choose **two host ports on
  different controllers**; **zone one source host port to one peer port, a separate zone per
  interconnection** (OIU p.17). The matrix caps multilink at **4 links (2 peer link pairs)**.
- The source is correctly zoned when it appears as a target on both peer ports: `showtarget` on the
  destination (`Port`, `Node_WWN`, `Port_WWN`, *reported_as_scsi_target*). `showtarget -lun all` lists
  the LUNs the source exports to the peer ports, each with a **State**: `--`, `discovered`, `admitted`,
  `importing`, `imported` (CLI p.528-531).
- `showtarget -rescan` **rescans the peer ports**. It changes no configuration but it is an action. The
  read client allowed it because it checked only the first word; BL-46 now refuses it (LESSONS 46).
- The source must present the volumes to the destination as if the destination were a host (a host on
  the source holding the peer ports' WWNs). For non-HPE sources the guides say persona *Linux*/ALUA
  (OIU p.18; PDM notes). **For a 3PAR/Primera source the persona and who creates that host (the B10000
  UI/DSCC, or the engineer) are unconfirmed** (§10 Q3).

## 5. The import itself: who drives it

| Option | What it takes | Evidence | Verdict |
|---|---|---|---|
| The B10000 UI or DSCC (Peer Motion) | the operator in a browser; the UI holds the source credential and does the source-side work | matrix *Supported UI* | **the supported path** |
| DSCC public API | a migration resource | the Block Storage API mirror (v1alpha1) has none. **The storage-fleet API (v1alpha1, 1.4.0, read 2026-11-17) has one**: `POST …/devtype4-storage-systems/{id}/migration-partners` (source address, user, password, family `3PAR/PRIMERA/ALLETRA-9K`, `FC` or `iSCSI`); GETs of the source's hosts, host sets, volumes, VLUNs, ports, Remote Copy groups; `POST …/migrations` (hosts or `set:<hostset>`, CPG, `tpvv`/`reduce`, minimally disruptive, pause; actions resume, revert, retry); `GET …/migrations` (status, percent, step) | the likely future way; not now (alpha, needs a write-scoped DSCC API client, entitlement unknown): ADR 0020 option D |
| Destination CLI `admitvv <vv>:<WWN>` + `importvv [-tpvv/-reduce] [-snap] [-nocons] [-pri] [-jobid] [-notask] [-clrsrc] <cpg> <vv/set:>` | a write-scoped SSH client on the destination **and** writes on the source (create the peer host, export to it, unexport from the production host) | CLI ED7 p.56, p.219-221 (`-clrsrc` even deletes the source volume, its snapshots and sets) | possible, not the supported orchestration; rejected for now (ADR 0020) |
| Playwright on DSCC's migration wizard | stable selectors for a wizard nobody here has captured | ADR 0006: the DSCC browser is attach-only, the operator signs in | rejected: brittle, and the wizard is the operator's decision point |

The import changes customer data paths on two arrays and the host at once. The field MOP's back-out
plan says what failure costs: *"the host loses access to its volumes, and an outage would occur"*, 4 to
5 hours to roll back. HPE's tools hold the import's own pre-checks; the tool's job is to get the
engagement to the point where those checks pass first time, and to prove the result afterwards.

## 6. Host side and the cutover

Migration types (OIU p.11-12; the matrix uses the same three): **online** (no host I/O disruption; the
host must already be zoned to the destination), **minimally disruptive** (I/O stops while the host and
multipath are reconfigured; host zoned to the destination), **offline** (host down, volumes un-exported
for the whole run; no host zoning to the destination needed until afterwards).

What the field MOP (3PAR 8400 → Alletra MP) does, in order: check peer ports and peer zoning; **zone the
hosts to the destination's host ports**; present a test LUN and check `multipath -ll`; present the source
volumes to the destination; start Peer Motion until it offers *Pause*; rescan the host and see the new
paths; check I/O on old and new paths; **un-present the volumes on the source but do not unzone the host
from the source**; resume; wait for the import (22 h estimated); check the application; clean up. The
PDM notes (third-party sources) instead **remove the host-to-source zones before the import**. The two
disagree, and the B10000 Peer Motion guide is what decides (§10 Q4). Both agree the **peer zones stay
until every volume is imported** (OIU p.16 says the same).

Host requirements the tool can see or cannot see:

| Requirement | Can the tool see it? |
|---|---|
| Host OS and version on the matrix | yes: vCenter, WinRM, Linux SSH discovery (SPEC-014) and the source's `showhost -d` OS column |
| Cluster size with SCSI-3 reservations (> 4 nodes ⇒ not online) | partly: `showrsv -l scsi3` on the source + host-set membership |
| ALUA-capable persona on the source | yes: `showhost -d` persona |
| Remote Copy on the volumes | yes: `showrcopy` on the source |
| vVols, Windows-on-VMware clusters, RHEL fencing type, ODM version | no: an operator checklist item, never a guess |

## 7. What the tool would read on the source (read-only)

All confirmed in the 3PAR (P29135-002a), Alletra 9000 (ED8) and B10000 (ED7) CLI references; authority
*Any role in the system* where stated. The Primera reference in the download is the quick reference
only; its command list includes them except `showvlun`, which our Primera captures must confirm.

| Command | Why | On `ALLOWED_COMMANDS` today |
|---|---|---|
| `showsys`, `showversion` (3PAR prints a `Patches:` line) | family, model, serial, OS, patches vs §3 | yes |
| `showport` | source host ports: mode, state, type, port WWN, node | yes |
| `showhost -d`, `showhostset -d` | hosts, WWNs, persona, OS; clusters | yes |
| `showvv`, `showvvset` | volumes, sizes, provisioning, sets | yes |
| `showvlun -a` | which volumes each host sees, at which LUN | yes |
| `showrcopy` | volumes in Remote Copy groups | yes |
| `showrsv -l scsi3 [-host <h>]` | SCSI-3 reservations (matrix: unlisted clusters, cluster size) | **no**: add after reading `help showrsv` for acting options, with a test (LESSONS 46) |
| destination: `showport -peer`, `showtarget`, `showtarget -lun all` | peer ports; source visible on them; per-LUN import state | yes (`showport`, `showtarget`) |
| destination: `showtask -active` | import tasks (`import_vv` task type, CLI ED7 p.534 *showtask*) | **no**: add later, with a test |

The source is never read over WSAPI: no WSAPI session means no write path exists for it at all, and a
3.2.2 source's WSAPI version is untested here.

## 8. The lab

| | Destination | Source |
|---|---|---|
| Array | rack13-ARCUS, CZ2D2K014S, 10.132.30.121, OS 10.5.55 | PRIMERA630R11U22, SGH339NK4C, 10.132.30.28, OS 4.6.20 (supported source, §3) |
| FC today (`tests/fixtures/rcip_pair/before/*/showport.txt`, 2026-11-03) | 0:3:3, 0:3:4, 1:3:3, 1:3:4 host `ready`; **0:3:1, 0:3:2, 1:3:1, 1:3:2 free, `loss_sync`** (no link) | 1:3:1, 1:3:3 host `ready`; 0:3:1, 0:3:3 `failed_over` (persistent ports); 0:3:2, 1:3:2 initiator, label RCFC |
| Fabric | rack13 Brocade fabrics (`tests/fixtures/rack13_fabric/`): this array's 0:3:3/0:3:4/1:3:3/1:3:4 | the same fabrics carry the Primera's 20:32/21:32 (F1) and 21:31 (F2); old zones `rcfc1`/`rcfc2` pair them with this array |

Both arrays share the two rack13 fabrics, so the pair can carry peer zones. What is missing: **a cabled
spare FC port on each node of rack13-ARCUS** to become a peer port (or the owner's decision to convert
two host ports), a capture of the Primera's host, volume and VLUN state, and §10 Q2. rack13-ARCUS has
since moved to 10.6.0 (BL-26 capture, 2026-11-16).

**The first live pair (2026-11-17, at acceptance): E18U31 and the 3PAR 20850 R2.** No setup is needed.

| | Destination | Source |
|---|---|---|
| Array | E18U31: DHCI_B10K, CZ2D3209YV, 10.64.154.190, OS 10.5.60 | HPE 3PAR 20850 R2, 4UW0002142, address not yet known |
| Peer link | FC peer ports 0:3:2 and 1:3:2, `initiator ready`, 32 Gbps; `showport -c` names device 2FF70002AC07E528 on both | its host ports 0:3:2 (20320002AC07E528) and 1:3:2 (21320002AC07E528), seen by `showportdev ns` on the two peer ports |
| Fabric | the VZ fabric; all four ports log in to one fabric (F2 in the 2026-08 capture) | same |
| OS against §3 | 10.5.6 is listed; a SPOCK edition naming 10.5.60 to be confirmed | fabric name fw:3313 suggests 3.3.1 MU3, below 3.3.1 MU5 + P141, P173, P180 (inference until `showversion -a -b`) |

Source: BL-26's captures (`tests/fixtures/peer_ports/E18U31/` on that branch) and
`tests/fixtures/vz_fabric/`. The same fabric capture holds peer zones from earlier work: `…_Zone17` and
`…_Zone18` pair the 3PAR's 0:3:2 and 1:3:2 with E18U31's peer WWNs, and `Pandu_774796_480683` pairs the
peer WWNs with another array (WWN prefix 50:06:0e:80). This project did not make these zones: ask
who owns the peer ports before using them (LESSONS 35). Other sources on the VZ fabric for a real import later: 3PAR 8400 fw:3321, 3PAR 7400c
fw:3315, Alletra 9060s (fw:9410 to fw:9570), Primera A650 (fw:4530, fw:4650).

## 9. Decisions this research proposes

1. **The tool prepares and proves; HPE's Peer Motion (B10000 UI or DSCC) imports** (ADR 0020).
2. **The source is a read-only step credential**, like the replication peer (SPEC-015 R1): read over
   the read-only SSH client only, never WSAPI, never a write client. ADR 0013 (one array credential, the
   destination's) and rule 4 hold: the run deploys one array; the source is refused if it is that array.
   ADR 0014 stays deferred: nothing is configured on the source, so there is no second run to pair.
3. **Peer zoning and host zoning are command sets** (ADR 0012), one zone per source port ↔ peer port
   pair, the operator ticking every pair. Removal zones come only after the import, in a later slice.
4. **Destination peer ports are SPEC-025's** (BL-26). BL-27 reads them and zones them.
5. **FC only first**, sources 3PAR / Primera / Alletra 9000.
6. **The read client refuses `showtarget -rescan`** (done, BL-46); `showrsv` joins the read allowlist
   after its help has been read for acting options.

## 10. Open questions

Answers recorded at acceptance (2026-11-17) are in italics.

1. Where is the current HPE Peer Motion user guide for a B10000 destination (UI and DSCC), and does it
   say who creates the peer host on the source, with which persona? *Open.*
2. Is a destination on 10.5.5x (lab: 10.5.55, 10.5.51) inside the matrix's "10.5.0 … and later MUs"?
   *Open; for the first pair the question is a SPOCK edition that names 10.5.60.*
3. Does the B10000 UI or DSCC create the peer host and the exports on the source itself, given the
   source credential, or must the engineer do it first? *Likely Peer Motion: the storage-fleet API takes
   the source credential, has no input for a peer host, and lists "peer hosts" on the partner. The tool
   does not ask the engineer to create it. The account's role and the persona are still to confirm.*
4. Cutover: unzone the host from the source before the import (PDM notes) or after (field MOP)? Per
   migration type? *Open. The API's `pauseMigration` (pause right before the data transfer) fits the
   field MOP's method.*
5. Does Peer Motion pull in every host that shares a volume with a selected host (OIU does)? *Open;
   keep W1. The API accepts `set:<hostset>` as the unit to migrate.*
6. Is a Peer Motion licence needed on a 3PAR or Primera source? *Open.*
7. Can the lab cable 0:3:1 and 1:3:1 on rack13-ARCUS to the rack13 fabrics, and may a test volume
   (`zz_mig_*`) be created on the Primera by a lab script for the live run? *No longer needed: the first
   pair (E18U31 and the 3PAR) needs no cabling and no test volume. A real import later asks the same of
   the source the owner picks.*
8. Is there a 3PAR (3.3.1 MU5 or later) in any lab, for the 3PAR parsers and the patch check? *Yes, the
   HPE 3PAR 20850 R2 (4UW0002142), probably 3.3.1 MU3 (below the matrix): it gives the parsers and a
   version blocker. 3.3.1 MU5 or later: see §8 for candidates.*
