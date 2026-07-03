# Scope — HPE storage deployment automation (north star)

> This is the **north-star scope**, captured so we can prioritise and build one slice at a time. It
> is deliberately larger than what ships today. The architecture that carries it is
> [ADR 0006 — hybrid control plane](adr/0006-hybrid-control-plane.md); the language is fixed in
> [CONTEXT.md](../CONTEXT.md).

## Objective

Automate the **full lifecycle of an HPE storage deployment** — initialize → discover → connect
(zone / VLAN) → provision → replicate / DR → report → document — across **Alletra MP block** and
**file** (HPE GreenLake for File / Alletra MP Unified File), so a deployment engineer runs an
engagement **hands-off** and gets the **as-built / HLD / LLD** for free.

**Primary user:** the HPE **deployment / field / PS engineer** running a customer storage engagement
— *not* the customer's day-2 admin. (HLD/LLD/as-built, DR failover/failback, and migration are
engagement deliverables, not self-service tasks.)

## Principles

- **Discovery-driven — nothing hand-typed** ([ADR 0002](adr/0002-provisioning-driven-by-discovery.md)).
  The tool reads the environment; the operator supplies *intent*, not facts. This is the operator's
  "it must be automatic."
- **Hybrid control plane** ([ADR 0006](adr/0006-hybrid-control-plane.md)): cloud **DSCC** primary
  (multi-array), **direct WSAPI** for depth, **switch** for zoning, **host** only where unavoidable.
- **Read-only where possible; writes are preview + explicit confirm; the riskiest writes are gated**
  (zoning remediation — [ADR 0004](adr/0004-auto-remediate-san-zoning.md)).

## The lifecycle matrix

Control surface + status per cell. Legend: **✅ built** · **✔︎ confirmed buildable** (deep research
2026-07-02) · **◻︎ gap** (needs a research pass and/or teammate input before it can be specified).

| Stage | Alletra MP — **block** | GL4F / Unified File — **file** |
|---|---|---|
| **1 Initialize** | ✅ **built** — onboarding Components A→B→C→D (GreenLake register → cloudinit → DSCC Set Up → verify) | ◻︎ file init — **gap** |
| **2 Discover** | array ports + nameserver ✅ · ESXi HBAs via vCenter ✔︎ · multi-OS host discovery (Win/Linux) + **source arrays** (migration) ◻︎ | ◻︎ hosts + shares/exports — **gap** |
| **3 Connect** | FC **zoning**: verify ✅ (array-side) · Brocade remediate ✔︎ (deferred) · **Cisco MDS** ◻︎ | ◻︎ **VLAN / LAN** config — **gap** |
| **4 Provision** | host/volume/VLUN ✅ (WSAPI, Phase 2) · via **DSCC** ✔︎ · snapshots + scheduling as **protection policies** ✔︎ | ◻︎ **views · ACLs (AD) · policies · share migration** — **gap** |
| **5 Replicate / DR** | Remote Copy as **DSCC protection policies** ✔︎ · **failover/failback** + **Peer Persistence / Quorum Witness** trigger ◻︎ | ◻︎ file replication — **gap** |
| **6 Report** | health + performance via **DSCC / Data Ops Manager** telemetry ✔︎ · **InfoSight** specifics ◻︎ | ◻︎ — **gap** |
| **7 Document** | **as-built / HLD / LLD** generation ◻︎ | **as-built / HLD / LLD** ◻︎ |

## Where the tool is today

The shipping app covers the **top-left**: Alletra MP **block** — Initialize (A/B/C/D) plus partial
Discover / Zoning-verify / Provision (host·volume·VLUN over WSAPI, driven by discovery; operator
picks a *mode*). Everything else in the matrix is new. Under [ADR 0006](adr/0006-hybrid-control-plane.md)
today's direct-WSAPI provisioning becomes the "direct" tier beneath a new DSCC cloud client — nothing
already shipped is discarded.

## Phasing (north-star, built incrementally)

Build in dependency order, starting from what exists, because **automatic host discovery** is the
shared foundation under Connect / Provision / Document:

1. **Foundation:** the hybrid control-plane client (DSCC cloud + direct WSAPI abstraction) + fully
   automatic, multi-OS host discovery (block).
2. **Block depth:** DSCC-driven provision / snapshot / replication; Cisco MDS zoning; DR
   failover/failback.
3. **File (its own research + build):** the whole file column — deferred pending a targeted
   research pass on the GL4F / Unified File control plane (SMB ACL + AD, views, share migration).
4. **Report + Document:** telemetry-backed health/perf reports; as-built / HLD / LLD generation.

## Known gaps (from the deep research)

Half the matrix produced **no verified claims** and must not be assumed either way: the **file
control plane** (biggest — a whole column), **DR failover/failback + Peer Persistence/Quorum
Witness**, **Cisco MDS** zoning, **Ethernet VLAN** automation, **InfoSight** telemetry, and
**as-built/HLD/LLD** generation. Gatekeepers only teammates can answer: our **DSCC workspace
entitlements** (which cloud APIs our client is scoped for) and **file API access**.
