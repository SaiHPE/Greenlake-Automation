# Scope — HPE storage deployment automation

> The **canonical scope and status** of the tool, in the nine areas the scope owner defined
> (2026-09-12). It replaces the earlier seven-stage lifecycle matrix. The architecture that carries
> it is [ADR 0006 — hybrid control plane](adr/0006-hybrid-control-plane.md); the language is fixed in
> [CONTEXT.md](../CONTEXT.md); the structure is in [design/HLD.md](design/HLD.md) and [STANDARD.md](STANDARD.md).
> Status here is checked against the code, not against plans. Last checked: **main (2026-11-22, post-BL-65 refactor)**.
> **Open items, owners and blockers live in [github.hpe.com issues](https://github.hpe.com/g-sai-roopesh/greenlake-automation/issues)**
> (historical log in [TRACKER.md](TRACKER.md)) — this file is the per-area summary.
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
> of both tracks recorded 2026-10-06. Landing Zone dropped (array unreachable). BL-31 (one fabric probe per
> fabric) and BL-32 (iSCSI hosts in the gate table) live 2026-10-07. **Replication** live 2026-10-09 to
> 2026-10-11 (BL-20); the **RCIP ports and partnership set up by the tool** live 2026-11-03 to 2026-11-06
> (BL-41). **2026-11-17** on rack13-ARCUS: snapshots and schedule (BL-21, 10/0, schedule fired), iSCSI
> presentation (BL-44, 17/0), iSCSI VLAN and peer-port command sets (BL-25, BL-26), handover status
> (BL-24), device trust on first contact (BL-53), Console logging (BL-54), 64 TiB volume limit (BL-55)
> and UI round 2 (BL-59) ([w1](validation/2026-11-17-rack13-live-w1.md), [w2](validation/2026-11-17-rack13-live-w2.md)).
> **2026-11-19** on rack13-ARCUS → PRIMERA630R11U22: BL-62 sync OS-version refusal before writes (12/0)
> and async end to end (38/0), BL-64 Check RC link / no performance / `showrcopy -d` volume tables (37/0),
> and BL-65 encrypted credentials and schema versions ([BL-62](validation/2026-11-19-bl62-sync-version.md),
> [BL-64](validation/2026-11-19-demo-feedback.md), [BL-65 creds](validation/2026-11-19-bl65-credentials-and-schema.md)).
> **2026-11-19 to 2026-11-21** on rack13-ARCUS + PRIMERA630R11U22: BL-65 engineering-standard
> refactor (PRs #50–#68, merged) live-verified across init walk (full 112/0, init-only 62/0 with
> restart), UI read-only (23/0), failed apply (27/0), iSCSI LUN (17/0), and RCIP sync/async (12/0,
> 38/0) ([validation/2026-11-21-bl65-refactor-live.md](validation/2026-11-21-bl65-refactor-live.md)).
> Remaining hardware-gated items are listed under *Open items and order of work* below.

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
- **SAN zoning defaults to copy-paste; opt-in Brocade apply is approval-gated** ([ADR 0012](adr/0012-no-switch-writes-the-tool-emits-a-command-set.md),
  amended by [ADR 0033](adr/0033-opt-in-brocade-zoning-apply.md)). The copy-paste Brocade command set
  stays the default deliverable; when explicitly opted in and approved on screen, the tool can apply
  and activate those exact Brocade FOS commands via `BrocadeZoneWriter` (`cfgenable "<cfg>" -f`)
  with pre-flight guards, pre-write undo and post-apply read-back. Cisco MDS remains out of scope.
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
| 2 | **Host and array discovery** | Discover ESXi, Windows and Linux hosts; collect OS, WWPN and multipathing information; discover source/Alletra array information; use host discovery as input to target configuration. | ◐ **Partial** | ✅ ESXi hosts via vCenter (HBA WWPNs, OS, serial, iSCSI IQN — live rack13 2026-09-28). ✅ Target Alletra array (ports, WWPNs, CPGs, hosts, volumes, unclaimed logins, `showport -rcip`). ✅ **Sheet hosts looked up without typed IDs** ([SPEC-014](specs/SPEC-014-agentless-hosts.md)): name + OS + IP resolved from vCenter / the array (live CRV VZ 2026-09-25, rack13 2026-09-28). ✅ **Windows host read over WinRM** — serial, FC WWPN, iSCSI IQN, OS, MPIO/MSDSM; a typed WWPN the server lacks blocks the plan (live rack13 2026-09-28). ✅ **Linux host read over SSH** (serial, WWPN, IQN, OS, `multipath -ll`) — live 2026-10-05 through Discovery on a RHEL 8.9 host (OS + IQN as a non-root user; **serial as root, live 2026-10-07**; `multipath -ll` summary — BL-36: the *not set up* case **live 2026-11-17** (the tool's own SSH client, as root, on the lab RHEL 8.9 host 10.54.159.49: `multipath -ll` exits 1, driver not loaded; [the tool's read](../tests/fixtures/linux_multipath/rhel89_lab_2026-11-17_tool_read/); the 2026-11-16 hand capture beside it shows no `/etc/multipath.conf`); the device summary **built, pending live run** (no lab Linux host has multipath and an Alletra volume) — *N Alletra/3PAR devices, M paths each*, naming a device with uneven, failed, single or no paths (at most three names), and plain sentences for multipath not set up, not readable without root, a read that timed out, or no Alletra devices yet; parser pinned to documented samples, not a lab capture, until a lab Linux host has multipath + an Alletra volume (`lab/multipath_capture.py`)). ◐ *Source* array discovery (migration, BL-27): the *Migration* tab and the *Migrate* mode are built (2026-11-17); the read of the source array waits on the 3PAR's captures, so the step is served as *not built yet*. 🟡 **The array's file side in Discovery** (BL-28, built 2026-11-17, pending live run): file service, File ports, file systems and shares, read over WSAPI v3 with GETs only. Discovery output feeds zoning + provisioning ✅. |
| 3 | **SAN and network configuration** | FC switch zoning based on discovered hosts and user inputs; VLAN configuration; peer-port configuration; migration peer setup and zoning. | ◐ **Partial** | ✅ **FC zoning (copy-paste)** + ✅ **Opt-in Brocade FOS apply (BL-66, live on rack13 SW-F1/SW-F2 2026-11-27, 21/0)** — current-connection map + operator-selected builder → emitted Brocade **command set** (`cfgsave`/`cfgenable` shown separately, default deliverable) plus opt-in, approval-gated Brocade switch apply (`alicreate` → `zonecreate` → `cfgadd` → `cfgenable "<cfg>" -f`, pre-flight `cfgtransshow`/`cfgshow` guards, pre-write undo, `cfgtransabort` on mid-apply failure, post-apply `cfgshow` Effective read-back; ADR 0033, `lab/zoning_apply_lab.py`, [validation record](validation/2026-11-27-bl66-brocade-zoning-apply-live.md)). **Brocade FOS only**; Cisco MDS out of scope (ADR 0004). Candidates are the union of vCenter + sheet + array logins + fabric name servers; **G-1 closed 2026-09-17** (a tool-designed zone, pasted as rendered, logged a host in). 2026-09-28/29, live on rack13: nothing is pre-ticked (the operator ticks every pair); an alias name the switch already defines, one new name typed for two ports, and a zone name already defined or over 64 are refused — flagged before *Generate* and listed under *Not included* after it; an installer-default name a host advertises (`HN:localhost…`, `smartstart`, `ubuntu`) is not taken as its identity. ◐ **VLAN-tagged iSCSI addresses** (BL-25, SPEC-024; **the consultant's command set live on rack13 2026-11-17**: the address added with no gateway, read back, verified and removed. Owner's decision the same day (ADR 0017 amendment): the tool never takes a port offline, so a gateway goes in a separate change-window set that names the sessions it would stop): an *iSCSI network* tab; the *Array ports* step plans them against the array and prints the `controliscsiport` lines with their undo lines; Verify and the as-built check them. The tool's own apply is not built yet (ADR 0017). ◐ Peer-port configuration: RCIP addresses on free peer ports for replication are set by the tool (SPEC-021, live 2026-11-03); migration peer ports are read only. ◐ **Peer ports for migration** (BL-26, SPEC-025; **the consultant's command set and removal set live on rack13 2026-11-17** on 0:3:1 and 1:3:1, every port view back to the baseline. Owner's decision (ADR 0018 amendment): the plan refuses a port whose card partner is in use; `controlport offline` asks for confirmation, which is fine for a hand paste; not yet seen on a cabled port): a *Peer ports* tab, the plan, the printed command set and removal set, the read after the paste, the peer zones in the zoning command set, Verify and the as-built; the tool's own port write is deferred (ADR 0018). ◻︎ Migration peer setup / zoning. |
| 4 | **Block provisioning** | Host creation; volume/LUN creation; volume sets; presentation, mapping and assignments to hosts. | ✅ **Live-verified (FC and iSCSI, one array)** | Hosts, volumes (thin/reduce, per-volume CPG), VV-sets, host-sets, exports (VLUNs) over WSAPI; read-only tier-2 **path verification**; export gated per host on verified zoning (ADR 0012). Live-proven end to end on rack13arcus 2026-09-13/14 by hand and 2026-09-15 by the session runner (SPEC-006, 38/39); plan truth (SPEC-001), removal set (SPEC-007), one credential per run (ADR 0013). Session runner 60/60 on 2026-09-19 and 2026-09-28 (and 2026-10-07 on the v0.16.1 exe); failure paths (S-3) seen live 2026-09-17. **iSCSI export (S-9) live 2026-10-05** on AlletraMP_E18U31: an iSCSI host whose IQN is logged in passes the gate without zoning, *Verify paths* reports its iSCSI paths per controller node. **iSCSI host creation (BL-44), live on AlletraMP_D22U27 2026-10-26** (run `eba8f3a7`, [validation record](validation/2026-10-26-iscsi-host-create.md)): a host with only an IQN (sheet, vCenter, a server read or an array login) is created from its iSCSI name at its OS persona; a missing IQN is added to an existing iSCSI host; an IQN owned by another host is a plan conflict. A host with both FC and iSCSI is made from FC only. Export to a host the tool created over iSCSI **live on rack13-ARCUS 2026-11-17** (BL-44 closed; [validation](validation/2026-11-17-rack13-live-w1.md)). A volume name the array refuses and a volume over its 64 TiB limit are refused on the sheet (BL-55, live 2026-11-17). A volume set name with a character the array refuses is refused on the sheet (live 2026-11-17), and a new host with a name over the array's 31 characters is a plan blocker (BL-60, closed 2026-11-17). CRV Vault Zone writes live 2026-10-05. |
| 5 | **Snapshots and replication** | Snapshot configuration; replication configuration; scheduling jobs. | ◐ **Replication live (sync + periodic, through the UI); snapshots live on rack13 (DSCC checks owed); RCFC built, pending live run** | Remote Copy groups to a peer array over an existing partnership — read, check, plan, apply over WSAPI, verify, removal set — **live-verified through the UI** on D22U27 → E18U31: sync 2026-10-09, periodic 2026-10-10 (SPEC-015/016, ADR 0015). A pair may carry a target per mode. **RCIP ports and partnership set up by the tool** (SPEC-021, BL-41): addresses, ping, `startrcopy`, a target each way, links Up, over a write-scoped SSH client — live 2026-11-03 on Alletra MP rack13-ARCUS → Primera 630, sync, then groups, failover test and as-built, 25/0, undone by the run's removal set; through the screens 2026-11-05; async (period 5 min) 27/0 the same day; the peer's side set up by the tool, a stopped apply, the link check with a gateway, mixed modes refused and a typed-confirmation failover 35/0 on 2026-11-06; the Alletra's ports behind the lab router (gateway written and read back, latency measured with ping when the array's test gives no number) 28/0 the same day, routed for the first packet only (the router redirects). A sync row from an array on OS 10.6 to a Primera 4.x or Alletra 9000 9.x peer, which the array refuses, is a plan blocker at the first read, before any write (BL-62, live 2026-11-19 on rack13-ARCUS 10.6.0 → the Primera 4.6.20; async there 38/0). The failover test passed live in sync (2026-10-10) and async (2026-10-11), SPEC-017; as-built sections generated live. The *Provision, then replicate* preset passed live with a real host (ESX1) and runner scenario 7, 32/0, 2026-10-11. ◐ **Snapshots and schedules** (BL-21, SPEC-023, ADR 0016, built 2026-11-17; **live on rack13-ARCUS, OS 10.6.0, 2026-11-17**, 10/0 after a `showsched` fix: snapshots, a schedule created and read back, verify, as-built, removal; a schedule the app made fired and was read back the same evening; owed: checks 3–4 on a DSCC-managed array, D22U27): a *Snapshots* tab and step; snapshots over WSAPI, schedules over a write-scoped SSH client (`createsched`, one tested form, ADR 0025); plan, apply, verify, removal set and the as-built section. 🟡 **Remote Copy over Fibre Channel, part A** (BL-50, SPEC-031, built 2026-11-17, pending live run): an existing FC partnership found by WWN, the 10 ms limit, groups, verify and the as-built. Setting RCFC up (part B) is deferred (ADR 0024); no FC pair is cabled in the lab. |
| 6 | **Alletra MP Unified File** | Unified File enablement/initialization; share creation; presentation; snapshot configuration. Intended extension to the initialization tool. | ◐ **Read-only slice built, pending live run** | 🟡 **First slice built 2026-11-17** (BL-28): Discovery, Verify and the as-built show the file service, File ports, file systems and shares. Research done (BL-28). The array's own WSAPI v3 is the read plane (ADR 0021, accepted 2026-11-17 for reads); the write plane waits for an amendment after a lab probe on D22U27. The read parsers are pinned to two captures ([SPEC-028](specs/SPEC-028-unified-file.md)). The first slice shows the file service, File ports, file systems and shares in Discovery, the as-built and Verify. Even when SPEC-028 is built the area stays ◐ **Partial**: enabling the file service, File port mode (it reboots the array) and file snapshots are excluded. |
| 7 | **GreenLake for File — GL4F** | Initialization; provisioning views; ACL configuration; policy configuration; share migration. | ◻︎ **Deferred (2026-11-17)** | Deferred on the owner's decision (ADR 0022, SPEC-029): no X10000 in any lab, no `file-storage.*` permissions for the workspace's API client, and the File Storage API is v1alpha1. Needs a research pass (views, SMB ACL + AD, policies, migration). Gatekeeper: file API access / workspace entitlements. |
| 8 | **Reports** | Configuration reports; hardware inventory; health-check output; health and performance reporting. | ◐ **Partial** | ✅ Configuration check vs. the sheet (Component **D**, read-only SSH). ✅ Hardware inventory (`showinventory`). ✅ `checkhealth -svc -detail` parsed into an issue table. ✅ **Status at handover** (BL-24, SPEC-026, ADR 0019, **live on rack13-ARCUS 2026-11-17**): the as-built records the array's new alerts and capacity in use, read-only. Performance figures (System Reporter) were removed on 2026-11-19 at the owner's request. ◻︎ DSCC / Data Ops Manager telemetry and InfoSight. |
| 9 | **Documentation generation** | As-built documentation; high-level design (HLD); low-level design (LLD). | ◐ **Partial** | ✅ **As-built** — read-only `show*` + `checkhealth` → the HPE Block Storage Word template (intent-matched headings, narrative fields, warnings); registered as the `asbuilt` step in every mode; the initialization sections live-proven 2026-09-13. **rc.8 adds the provisioned array** (`docs/specs/SPEC-002-asbuilt-provisioned.md`): hosts and host sets, volumes and volume sets, presentations with active paths, the SAN zoning designed in the run with its delivered command set, and the provisioning record with path verification. Generated live on every session-runner run (SPEC-006 scenario 5: verify finds no mismatch, the docx names the run); the provisioned sections were reviewed page by page on rack13 2026-10-06 (S-8, BL-33): all matched, one table label fixed. **2026-10-10 adds replication** (SPEC-018): when the workbook has a Replication tab, two more sections, read back from both arrays when the document is made: partner array and partnership (targets, links, RCIP ports), the groups this run configured (mode, RPO and period, policies, role on each side, volumes with sync state and last sync, peer volume set), replication already present, the calls made, the removal set as A and B blocks; and a Failover test section with the test's record (SPEC-017). Generated live with both sections after a replication run 2026-10-10 (BL-20), and in the BL-41 runs 2026-11-03 to 2026-11-06, with the ports and targets the tool set up. ◻︎ HLD and LLD **for a customer deployment**: not built, and not yet an issue. The tool's own HLD, LLD, engineering standard and Developer Handbook — [design/HLD.md](design/HLD.md), [design/LLD.md](design/LLD.md), [STANDARD.md](STANDARD.md) and [DEVELOPER-HANDBOOK.html](DEVELOPER-HANDBOOK.html) — are current with the refactored architecture on `main` (BL-22, BL-23, BL-65). |

## Where the tool is today

Alletra MP **block**, areas 1–4, replication and snapshots in area 5, and the block half of 8–9 live
in one operator web app with active modes (Full onboarding / Provision only / Both / Provision, then
replicate / Verify only / Custom), plus *Migrate* (served as not built yet until the source read
exists).

- **Live-verified on rack13-ARCUS + PRIMERA630R11U22** (2026-11-17 through 2026-11-21): snapshots
  and schedules on OS 10.6.0 (BL-21), handover status alerts and capacity (BL-24), iSCSI VLAN
  command set (BL-25), migration peer-port command set on uncabled ports (BL-26), iSCSI host
  creation and presentation (BL-44), per-run device trust and re-trust (BL-53, ADR 0026), Console
  logging (BL-54), 64 TiB volume limit (BL-55), UI round 2 (BL-59), sync OS-version refusal before
  writes (BL-62), Check RC link and `showrcopy -d` volume tables (BL-64), and the merged BL-65
  engineering-standard refactor (PRs #49–#68;
  [validation/2026-11-21-bl65-refactor-live.md](validation/2026-11-21-bl65-refactor-live.md)).
- **Pending lab hardware:** see *Open items and order of work* item 6 below.
- **Architecture and developer docs:** the tool's own [HLD](design/HLD.md), [LLD](design/LLD.md),
  [engineering standard](STANDARD.md) and [Developer Handbook](DEVELOPER-HANDBOOK.html) match `main`.

GreenLake for File (area 7) is deferred. The two structural gaps under ADR 0006 are unchanged: the
**DSCC cloud control plane** client (needed for cloud-driven provisioning and DSCC snapshot
policies) and the **entire file column**.

## Open items and order of work

In the order the scope owner set (2026-09-12); item-level status is in the github.hpe.com issues
(history in [TRACKER.md](TRACKER.md)).

1. **Live-test discovery, zoning and provisioning through the application** — done: session runner
   60/60 (2026-09-19, 2026-09-28), G-1 closed, zoning designer changes seen live 2026-09-29.
2. **Agentless Windows/Linux host discovery** (area 2, SPEC-014) — Windows over WinRM live
   2026-09-28; the Linux read over SSH live 2026-10-05 (BL-10 closed; serial as root 2026-10-07).
   The Linux multipath summary is owed live (BL-36).
3. **Snapshots and replication** (area 5) — replication done (TRACKER BL-20 closed 2026-10-11, v0.17.0):
   groups over WSAPI on an existing partnership, sync and periodic, the failover test in both modes,
   the as-built sections, all live on the lab pair. A Replication row may name a volume set already on
   the array. **BL-41: the tool sets up the RCIP ports and the partnership itself** (Replication
   network tab, SPEC-021): live 2026-11-03 on Alletra MP → Primera, 25/0, back to the start with the
   run's removal set (`docs/validation/2026-11-03-rcip-partnership.md`); through the screens and in async
   2026-11-05. BL-41 closed 2026-11-06 (v0.18.0).
   Snapshots (BL-21) live on rack13-ARCUS 2026-11-17 (10/0, schedule fired and read back); checks
   3–4 wait on a DSCC-managed array (D22U27).
   Field feedback 2026-10-12: the latency between the arrays is measured with `checkrclink` before
   replication and the operator decides on a latency over the limit (SPEC-020, BL-42). Live on one
   array 2026-10-12; the check, its ping fallback, the gate before configuring and the as-built
   paragraph are live on the BL-41 pair (2026-11-03 to 2026-11-06). Built, pending a live run: the
   over-the-limit path (refusal, *Continue anyway*, the accepted note) and the per-link verdict column.
   It needs a pair over 10 ms; the lab pair measures 0.02 ms (SPEC-020 addendum 2026-11-16). Closed 2026-11-17 on the owner's decision:
   the over-the-limit path stands on its unit tests until a pair over 10 ms exists.
   Research: `research/2026-09-19-replication-two-arrays.md`, `research/2026-10-07-replication-document-review.md`;
   ADR 0015; specs SPEC-015 to SPEC-018.
4. **Console** (SPEC-019, BL-39) — built in v0.17.0, live on labrat 2026-10-12: every command the tool sends
   to an array or switch, with its output, in a pane under each step and in the as-built. Expanded
   in BL-54 to cover vCenter, GreenLake and hosts (vCenter/array/switches live 2026-11-17).
5. **Engineering standard and refactor (BL-65, PRs #49–#68)** — merged and live-verified on
   rack13-ARCUS and PRIMERA630R11U22 (2026-11-19 to 2026-11-21; issue #48 remains open until the
   owner closes it). See [validation/2026-11-21-bl65-refactor-live.md](validation/2026-11-21-bl65-refactor-live.md)
   for the scope and pass counts.
6. **Hardware-gated items still open:**
   - **D22U27:** BL-21 checks 3–4 (DSCC-managed snapshot schedules) and BL-28 Unified File reads on an
     array with File ports.
   - **Cabled FC peer port:** BL-26 peer-port commands on a cabled port.
   - **3PAR 20850 R2:** BL-27 source-array captures (tab and mode are built; the read step waits on
     the captures).
   - **VME nodes / Linux host with multipath + Alletra LUN:** BL-36 Linux multipath device summary.
   - **Cabled FC array pair:** BL-50 RCFC part A live verification.
   - **Deferred:** BL-29 GreenLake for File, BL-50 part B (RCFC port setup), the tool's own
     peer-port write (BL-26), the VLAN apply (BL-25), and customer-deployment HLD/LLD generation.

## Known gaps from the deep research

Half the matrix produced **no verified claims** and must not be assumed either way: the **file
control plane** (a whole column), **DR failover/failback + Peer Persistence/Quorum Witness**,
**Cisco MDS** zoning, **Ethernet VLAN** automation, **InfoSight** telemetry, and **HLD/LLD**
generation. Gatekeepers only teammates can answer: our **DSCC workspace entitlements** (which cloud
APIs our client is scoped for) and **file API access**.
