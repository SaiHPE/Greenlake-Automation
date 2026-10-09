# Scope — HPE storage deployment automation

> The **canonical scope and status** of the tool, in the nine areas the scope owner defined
> (2026-09-12). It replaces the earlier seven-stage lifecycle matrix. The architecture that carries
> it is [ADR 0006 — hybrid control plane](adr/0006-hybrid-control-plane.md); the language is fixed in
> [CONTEXT.md](../CONTEXT.md); the current-state module map is [ARCHITECTURE.md](ARCHITECTURE.md).
> Status here is checked against the code, not against plans. Last checked: **v0.16.1 + main** (2026-10-07).
> **Open items, owners and blockers live in [TRACKER.md](TRACKER.md)** — this file is the per-area summary.
>
> **Live-proven:** the **init track** was run from scratch on a factory-fresh array (operator-confirmed
> 2026-09-29). The **provisioning track** (discover → zoning check → plan →
> apply → path verification → verify → as-built) runs end to end on rack13arcus under the session
> runner (SPEC-006): 60/60 on 2026-09-19 and 2026-09-28, and **60/60 on 2026-10-07 against the packaged
> v0.16.1 exe**. **G-1 closed 2026-09-17**: a tool-generated zone,
> pasted as rendered, logged a host into the array. S-3 (failure paths) and S-5 (resume) seen live
> 2026-09-17. SPEC-014 (sheet hosts without typed IDs; ESXi serial/IQN; Windows over WinRM) live on
> rack13 2026-09-28 (40/0/2). The zoning designer's 2026-09-29 changes (nothing pre-ticked, name
> clashes flagged before and after *Generate*, installer-default host names ignored) seen live the same
> day. Record: [validation/2026-09-29-rack13arcus-live-test-3.md](validation/2026-09-29-rack13arcus-live-test-3.md).
> 2026-10-05/07: **iSCSI export (S-9) live** on AlletraMP_E18U31; **CRV Vault Zone** read-only and writes
> live; SPEC-013 *Visible* after a rescan live; Linux read over SSH live (as root: serial). Canned demos
> of both tracks recorded 2026-10-06. Landing Zone dropped (array unreachable). Still owed live: TRACKER
> *Test live* (BL-31, BL-32, BL-36).

## Objective

Automate the **full lifecycle of an HPE storage deployment** — initialize → discover → connect
(zone / VLAN) → provision → protect (snapshot / replicate) → report → document — across **Alletra MP
block**, **Alletra MP Unified File** and **HPE GreenLake for File (GL4F)**, so a deployment engineer
runs an engagement **hands-off** and gets the **as-built / HLD / LLD** for free.

**Primary user:** the HPE **deployment / field / PS engineer** running a customer storage engagement
— *not* the customer's day-2 admin.

## Principles

- **Discovery-driven — nothing hand-typed** ([ADR 0002](adr/0002-provisioning-driven-by-discovery.md)).
  The tool reads the environment; the operator supplies *intent*, not facts.
- **Hybrid control plane** ([ADR 0006](adr/0006-hybrid-control-plane.md)): cloud **DSCC** primary
  (multi-array), **direct WSAPI/SSH** for depth, **switch read-only**, **host** only where unavoidable.
- **Read-only where possible; writes are preview + explicit confirm.**
- **The tool never writes to a SAN switch** ([ADR 0012](adr/0012-no-switch-writes-the-tool-emits-a-command-set.md)).
  It emits the exact command set for *that* switch, which a consultant copy-pastes. This is
  deliberate scope: we do not take on switch-vendor intricacies. "FC switch zoning" in the scope table
  below is **delivered** in this form.
- **Validate live** ([LESSONS.md](LESSONS.md)). A feature verified only against captured command
  output is not done; it is *built — pending live run*.

## Status legend

| Mark | Meaning |
|---|---|
| ✅ **Built** | shipped and driven through the application against real hardware |
| 🟡 **Built — pending live run** | code complete and unit-tested against real captured output, but not yet driven through the app on hardware since the change |
| ◐ **Partial** | some sub-items built, others not |
| ◻︎ **Not started** | no code; may still need a research pass |

## The nine scope areas

| # | Area | Scope (as defined) | Status | Detail |
|---|---|---|---|---|
| 1 | **Alletra MP initialization** | Guided prerequisites; customer input template; GreenLake workspace and DSCC guidance; network/firewall requirements; time-synchronization assistance; automatic registration of array serial numbers and subscription keys; GreenLake connectivity checks; bundled discovery; initialization; instructions for remaining manual steps. | ✅ **Built — live-verified** | Every sub-item exists: Prerequisites tab + downloadable firewall list (`platform/prereqs.py`); `Initialisation_sheet.xlsx` template (`platform/init_sheet.py`); Configure step with **Test connection**; **Sync system clock**; Component **A** GreenLake REST; preflight; bundled HPE Discovery Tool (SHA256-verified); Component **B** cloudinit; Component **C** DSCC Set Up System; Finish step. Ships alone as the `init-only` build profile (ADR 0007). Run from scratch on a factory-fresh array (operator-confirmed 2026-09-29). |
| 2 | **Host and array discovery** | Discover ESXi, Windows and Linux hosts; collect OS, WWPN and multipathing information; discover source/Alletra array information; use host discovery as input to target configuration. | ◐ **Partial** | ✅ ESXi hosts via vCenter (HBA WWPNs, OS, serial, iSCSI IQN — live rack13 2026-09-28). ✅ Target Alletra array (ports, WWPNs, CPGs, hosts, volumes, unclaimed logins, `showport -rcip`). ✅ **Sheet hosts looked up without typed IDs** ([SPEC-014](specs/SPEC-014-agentless-hosts.md)): name + OS + IP resolved from vCenter / the array (live CRV VZ 2026-09-25, rack13 2026-09-28). ✅ **Windows host read over WinRM** — serial, FC WWPN, iSCSI IQN, OS, MPIO/MSDSM; a typed WWPN the server lacks blocks the plan (live rack13 2026-09-28). ✅ **Linux host read over SSH** (serial, WWPN, IQN, OS, `multipath -ll`) — live 2026-10-05 through Discovery on a RHEL 8.9 host (OS + IQN as a non-root user; **serial as root, live 2026-10-07**; `multipath -ll` summary owed live — BL-36, no lab Linux host has multipath + an Alletra volume). ◻︎ *Source* array discovery (migration). Discovery output feeds zoning + provisioning ✅. |
| 3 | **SAN and network configuration** | FC switch zoning based on discovered hosts and user inputs; VLAN configuration; peer-port configuration; migration peer setup and zoning. | ◐ **Partial** | ✅ **FC zoning** — current-connection map + operator-selected builder → emitted Brocade **command set** (`cfgsave`/`cfgenable` shown separately). **Brocade FOS only**; Cisco MDS out of scope (ADR 0004). Delivered as command set by design — see Principles. Candidates are the union of vCenter + sheet + array logins + fabric name servers; **G-1 closed 2026-09-17** (a tool-designed zone, pasted as rendered, logged a host in). 2026-09-28/29, live on rack13: nothing is pre-ticked (the operator ticks every pair); an alias name the switch already defines, one new name typed for two ports, and a zone name already defined or over 64 are refused — flagged before *Generate* and listed under *Not included* after it; an installer-default name a host advertises (`HN:localhost…`, `smartstart`, `ubuntu`) is not taken as its identity. ◻︎ VLAN configuration (VLAN is only *read* from `showport -rcip`). ◻︎ Peer-port configuration (read only). ◻︎ Migration peer setup / zoning. |
| 4 | **Block provisioning** | Host creation; volume/LUN creation; volume sets; presentation, mapping and assignments to hosts. | ✅ **Live-verified (FC and iSCSI, one array)** | Hosts, volumes (thin/reduce, per-volume CPG), VV-sets, host-sets, exports (VLUNs) over WSAPI; read-only tier-2 **path verification**; export gated per host on verified zoning (ADR 0012). Live-proven end to end on rack13arcus 2026-09-13/14 by hand and 2026-09-15 by the session runner (SPEC-006, 38/39); plan truth (SPEC-001), removal set (SPEC-007), one credential per run (ADR 0013). Session runner 60/60 on 2026-09-19 and 2026-09-28 (and 2026-10-07 on the v0.16.1 exe); failure paths (S-3) seen live 2026-09-17. **iSCSI export (S-9) live 2026-10-05** on AlletraMP_E18U31: an iSCSI host whose IQN is logged in passes the gate without zoning, *Verify paths* reports its iSCSI paths per controller node. CRV Vault Zone writes live 2026-10-05. |
| 5 | **Snapshots and replication** | Snapshot configuration; replication configuration; scheduling jobs. | ◐ **Replication live (sync + periodic); snapshots not started** | Remote Copy groups to a peer array over an existing partnership — read, check, plan, apply over WSAPI, verify, removal set — **live-verified 2026-10-09** on D22U27 → E18U31 (sync through the UI; periodic through the same modules with the lab's Sync groups paused; SPEC-015/016, ADR 0015). A pair may carry a target per mode. Owed: periodic through the UI (needs a target of its own), failover test (SPEC-017, v0.18), links/targets configured by the tool (v0.19). Snapshots (BL-21): DSCC protection policies or `createsv`/`createsched`. |
| 6 | **Alletra MP Unified File** | Unified File enablement/initialization; share creation; presentation; snapshot configuration. Intended extension to the initialization tool. | ◻︎ **Not started** | Needs a research pass on the file control plane. |
| 7 | **GreenLake for File — GL4F** | Initialization; provisioning views; ACL configuration; policy configuration; share migration. | ◻︎ **Not started** | Needs a research pass (views, SMB ACL + AD, policies, migration). Gatekeeper: file API access / workspace entitlements. |
| 8 | **Reports** | Configuration reports; hardware inventory; health-check output; health and performance reporting. | ◐ **Partial** | ✅ Configuration check vs. the sheet (Component **D**, read-only SSH). ✅ Hardware inventory (`showinventory`). ✅ `checkhealth -svc -detail` parsed into an issue table. ◻︎ Health/**performance** reporting (DSCC / Data Ops Manager telemetry, InfoSight). |
| 9 | **Documentation generation** | As-built documentation; high-level design (HLD); low-level design (LLD). | ◐ **Partial** | ✅ **As-built** — read-only `show*` + `checkhealth` → the HPE Block Storage Word template (intent-matched headings, narrative fields, warnings); registered as the `asbuilt` step in every mode; the initialization sections live-proven 2026-09-13. **rc.8 adds the provisioned array** (`docs/specs/SPEC-002-asbuilt-provisioned.md`): hosts and host sets, volumes and volume sets, presentations with active paths, the SAN zoning designed in the run with its delivered command set, and the provisioning record with path verification. Generated live on every session-runner run (SPEC-006 scenario 5: verify finds no mismatch, the docx names the run); a page-by-page review of the provisioned sections (S-8) is still owed. ◻︎ HLD. ◻︎ LLD. |

## Where the tool is today

Alletra MP **block**, areas 1–4 and the block half of 8–9, in one operator web app with five modes
(Full onboarding / Provision only / Both / Verify only / Custom). Everything in the **file** column
(6, 7) and all of **snapshots/replication** (5) is unbuilt. The two structural gaps under ADR 0006 are
unchanged: the **DSCC cloud control plane** client (needed for 5 and for cloud-driven provisioning)
and the **entire file column**.

## Open items and order of work

In the order the scope owner set (2026-09-12); item-level status is in [TRACKER.md](TRACKER.md).

1. **Live-test discovery, zoning and provisioning through the application** — done: session runner
   60/60 (2026-09-19, 2026-09-28), G-1 closed, zoning designer changes seen live 2026-09-29.
2. **Agentless Windows/Linux host discovery** (area 2, SPEC-014) — Windows over WinRM live
   2026-09-28; the Linux read over SSH is built and waits on a Linux login (TRACKER BL-10).
3. **Snapshots and replication** (area 5) — next. Replication research done
   (`research/2026-09-19-replication-two-arrays.md`, `research/2026-10-07-replication-document-review.md`);
   decisions taken 2026-10-07 (ADR 0015; ADR 0014 paired runs deferred); specs approved and re-cut for
   delivery: SPEC-015 (Replication tab on the one-array workbook), SPEC-016 (groups over WSAPI on an
   existing partnership — v0.17), SPEC-017 (failover test — v0.18), SPEC-018 (as-built sections); links
   and targets configured by the tool in v0.19. Sync and async first; snapshots (BL-21) after.
4. Then: performance reporting (8), HLD/LLD (9), VLAN / peer-port / migration (3), file column (6, 7).

## Known gaps from the deep research

Half the matrix produced **no verified claims** and must not be assumed either way: the **file
control plane** (a whole column), **DR failover/failback + Peer Persistence/Quorum Witness**,
**Cisco MDS** zoning, **Ethernet VLAN** automation, **InfoSight** telemetry, and **HLD/LLD**
generation. Gatekeepers only teammates can answer: our **DSCC workspace entitlements** (which cloud
APIs our client is scoped for) and **file API access**.
