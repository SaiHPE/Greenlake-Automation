# Scope — HPE storage deployment automation

> The **canonical scope and status** of the tool, in the nine areas the scope owner defined
> (2026-09-12). It replaces the earlier seven-stage lifecycle matrix. The architecture that carries
> it is [ADR 0006 — hybrid control plane](adr/0006-hybrid-control-plane.md); the language is fixed in
> [CONTEXT.md](../CONTEXT.md); the current-state module map is [ARCHITECTURE.md](ARCHITECTURE.md).
> Status here is checked against the code, not against plans. Last checked: **v0.16.0-rc.5**.

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
| 1 | **Alletra MP initialization** | Guided prerequisites; customer input template; GreenLake workspace and DSCC guidance; network/firewall requirements; time-synchronization assistance; automatic registration of array serial numbers and subscription keys; GreenLake connectivity checks; bundled discovery; initialization; instructions for remaining manual steps. | ✅ **Built** | Every sub-item exists: Prerequisites tab + downloadable firewall list (`platform/prereqs.py`); `Initialisation_sheet.xlsx` template (`platform/init_sheet.py`); Configure step with **Test connection**; **Sync system clock**; Component **A** GreenLake REST; preflight; bundled HPE Discovery Tool (SHA256-verified); Component **B** cloudinit; Component **C** DSCC Set Up System; Finish step. Ships alone as the `init-only` build profile (ADR 0007). |
| 2 | **Host and array discovery** | Discover ESXi, Windows and Linux hosts; collect OS, WWPN and multipathing information; discover source/Alletra array information; use host discovery as input to target configuration. | ◐ **Partial** | ✅ ESXi hosts via vCenter (HBA WWPNs, OS). ✅ Target Alletra array (ports, WWPNs, CPGs, hosts, volumes, unclaimed logins, `showport -rcip`). 🟡 Windows/Linux hosts inferred **array-side** (persona + IQN/WWPN) and a manual **Hosts** tab for servers vCenter cannot see. ◻︎ **Agentless host-side discovery**: log into hosts the customer lists in the sheet (not in vCenter) and read OS / WWPN / multipathing. ◻︎ Host-side multipathing. ◻︎ *Source* array discovery (migration). Discovery output feeds zoning + provisioning ✅. |
| 3 | **SAN and network configuration** | FC switch zoning based on discovered hosts and user inputs; VLAN configuration; peer-port configuration; migration peer setup and zoning. | ◐ **Partial** | 🟡 **FC zoning** — current-connection map + operator-selected builder → emitted Brocade **command set** (`cfgsave`/`cfgenable` shown separately). **Brocade FOS only**; Cisco MDS out of scope (ADR 0004). Delivered as command set by design — see Principles. Live 2026-09-12: read/design correct, but hosts outside vCenter never reached the plan; fixed (union of vCenter + sheet + array logins + fabric name servers) and the step redesigned (`docs/ux/ZONING-REDESIGN.md`) — pending live run; a tool-designed zone has not yet been applied and seen to log in. ◻︎ VLAN configuration (VLAN is only *read* from `showport -rcip`). ◻︎ Peer-port configuration (read only). ◻︎ Migration peer setup / zoning. |
| 4 | **Block provisioning** | Host creation; volume/LUN creation; volume sets; presentation, mapping and assignments to hosts. | 🟡 **Built — pending live run** | Hosts, volumes (thin/reduce, per-volume CPG), VV-sets, host-sets, exports (VLUNs) over WSAPI; read-only tier-2 **path verification**; export gated per host on verified zoning (ADR 0012). Tier-1 create was live-proven in v0.11.0; the post-2026-08-31 fixes have **not** been driven through the app on hardware. |
| 5 | **Snapshots and replication** | Snapshot configuration; replication configuration; scheduling jobs. | ◻︎ **Not started** | Zero code. Research (2026-07-02) says buildable as **DSCC protection policies** (snapshot + Remote Copy with schedule/retention); direct-array fallback is `createsv`/`createsched`. Needs a proper research pass before build. |
| 6 | **Alletra MP Unified File** | Unified File enablement/initialization; share creation; presentation; snapshot configuration. Intended extension to the initialization tool. | ◻︎ **Not started** | Needs a research pass on the file control plane. |
| 7 | **GreenLake for File — GL4F** | Initialization; provisioning views; ACL configuration; policy configuration; share migration. | ◻︎ **Not started** | Needs a research pass (views, SMB ACL + AD, policies, migration). Gatekeeper: file API access / workspace entitlements. |
| 8 | **Reports** | Configuration reports; hardware inventory; health-check output; health and performance reporting. | ◐ **Partial** | ✅ Configuration check vs. the sheet (Component **D**, read-only SSH). ✅ Hardware inventory (`showinventory`). ✅ `checkhealth -svc -detail` parsed into an issue table. ◻︎ Health/**performance** reporting (DSCC / Data Ops Manager telemetry, InfoSight). |
| 9 | **Documentation generation** | As-built documentation; high-level design (HLD); low-level design (LLD). | ◐ **Partial** | ✅ **As-built** — read-only `show*` + `checkhealth` → the HPE Block Storage Word template (intent-matched headings, narrative fields, warnings); registered as the `asbuilt` step in every mode. ◻︎ HLD. ◻︎ LLD. |

## Where the tool is today

Alletra MP **block**, areas 1–4 and the block half of 8–9, in one operator web app with five modes
(Full onboarding / Provision only / Both / Verify only / Custom). Everything in the **file** column
(6, 7) and all of **snapshots/replication** (5) is unbuilt. The two structural gaps under ADR 0006 are
unchanged: the **DSCC cloud control plane** client (needed for 5 and for cloud-driven provisioning)
and the **entire file column**.

## Open items and order of work

In the order the scope owner set (2026-09-12):

1. **Live-test discovery, zoning and provisioning through the application.** Everything since the
   [2026-08-31 live test](validation/2026-08-31-rack13arcus-live-test.md) is verified only against
   captured output. That test showed a correct parser can still leave a wrong step. Also owed from
   that test: the manual lab cleanup and the disclosure to the SAN team (see its *Owed* section).
2. **Agentless Windows/Linux host discovery** (area 2). Hosts that vCenter knows are read from
   vCenter; hosts the customer lists in the sheet that vCenter does *not* know must be logged into by
   the tool (SSH / WinRM) to read OS, WWPN/IQN and multipathing. Closes the biggest gap in area 2.
3. **Snapshots and replication** (area 5) — research first, then build, once 1 and 2 are satisfactory.
4. Then: performance reporting (8), HLD/LLD (9), VLAN / peer-port / migration (3), file column (6, 7).

## Known gaps from the deep research

Half the matrix produced **no verified claims** and must not be assumed either way: the **file
control plane** (a whole column), **DR failover/failback + Peer Persistence/Quorum Witness**,
**Cisco MDS** zoning, **Ethernet VLAN** automation, **InfoSight** telemetry, and **HLD/LLD**
generation. Gatekeepers only teammates can answer: our **DSCC workspace entitlements** (which cloud
APIs our client is scoped for) and **file API access**.
