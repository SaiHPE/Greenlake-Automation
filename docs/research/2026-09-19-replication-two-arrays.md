# Research — Replication (SCOPE area 5) and the two-array run

**Date:** 2026-09-19 · **Status:** research, awaiting the decisions in §8 before SPEC-015 / ADR 0014
**Sources:** the SharePoint set (§1), the local GreenLake API mirror, `python-3parclient` 4.2.14, the code
as of v0.16.0, the CRV lab sheet.

## 1. Sources — and a warning about the SharePoint folder

Many files in `GreenlakeAutomation_storage_docs_from_sharepoint/` carry the **wrong filename**
(*"Configuring… data replication using Remote (1).pdf"* is the drive-upgrade guide; *"Alletra MP
Replication_HLD.pdf"* is a Peer Motion MOP). Identify a document by its part number, never its name.
The ones this research rests on:

| Real title | Part no. | Used for |
|---|---|---|
| HPE Alletra Storage MP B10000: **Configuring and managing data replication using Remote Copy and the CLI** (118 pp, ED7) | 20-ALMPB10K-RCCF | the procedure of record (§3) |
| HPE GreenLake for Block Storage: **Configuring and managing data replication using the on-system UI 2.5** (56 pp) | 20-GRLKBLK-RCCUI-ED6 | what the array's local web UI exposes: *Replication partner systems*, *Replication partners*, per-VV-set *replication policy*, snapshot schedules |
| **Getting started** / **Troubleshooting** data replication (UI + CLI), **Recovering from disaster using Remote Copy** | RCGSUI-ED5, RCTSUI-ED4, RCTS-ED5, RCRE-ED6 | planning limits, verification, failure states, DR procedures |
| **High Level Design — HPE Alletra MP Async Replication for \<Customer\>** v1.0, 2026-03-15 (DOC-1DOC-029) | — | **a real engagement**: RCIP async periodic, ports 0:4:3 + 1:4:3, DC → DRC, one RC group, failover/switchover test and failback as deliverables, alerts as operations |
| Installing and configuring the field-/factory-integrated system | IFIC-ED15 / IFAC-ED12 | RCIP ports are slot-4 ports 3 and 4 (10/25 GbE), dedicated |
| Block Storage public API (`docs and plans/greenlake_api_docs/…/block-storage/`) | v1alpha1 | `protection-policies` CRUD on application sets, `replication-partners` GET, `remote-protection/actions` |

The GreenLake API mirror's *Initialization worksheet* (IWRKS-ED4) has **no** RCIP fields — HPE's own
worksheet does not plan replication; that is a gap our sheet fills.

## 2. What replication is on a B10000 — three layers

```
1  TRANSPORT     RCIP ports cabled and addressed on BOTH arrays (slot 4 ports 3/4; a different subnet from mgmt)
2  PARTNERSHIP   Remote Copy started, each array declares the other as a TARGET over ≥2 links from 2 nodes
3  PROTECTION    a Remote Copy GROUP over a volume set: sync or periodic (RPO ≈ 2 × period, min period 15 s),
                 secondary volumes auto-created on the peer's CPG, started; optionally snapshot schedules
```

Constraints the tool must check before it proposes anything (CLI guide §"RCIP network transport
requirements"): RCIP and iSCSI cannot share a port · unique IPs · RCIP subnet ≠ management subnet ·
≥ 2 links per target from two different nodes, ≤ 4 links per node, ≤ 4 targets per port · no NAT ·
firewall TCP **5785** and **5001** · both arrays on NTP · peer has capacity and a CPG for the secondaries.

## 3. The procedure of record (CLI guide, 1-to-1 configuration)

```
A and B   startrcopy
A and B   controlport rcip addr <ip> <netmask> <N:S:P>          per RCIP port
A and B   controlport rcip gw <gateway> <N:S:P>                 only when the sites are on different subnets
A or B    controlport rcip ping <peer_port_ip> <N:S:P>          per link
A         creatercopytarget <B_name> IP <N:S:P>:<B_port_ip> [<N:S:P>:<B_port_ip> …]
B         creatercopytarget <A_name> IP <N:S:P>:<A_port_ip> [...]
A         creatercopygroup -usr_cpg <cpgA> <B_name>:<cpgB> <group> <B_name>:periodic     (or :sync)
A         setrcopygroup period <seconds> <B_name> <group>       periodic only
A         admitrcopyvv -createvv set:<vvset> <group> <B_name>:<vvset_on_B>
A         startrcopygroup <group>
verify    showrcopy · showrcopy groups · showrctransport -rcip · showport -rcip
```

Every command above is a **write** except the four `show*`; `showrcopy` is already on the read allowlist.

## 4. Control-plane options, per layer

| Layer | Option | Evidence | Verdict |
|---|---|---|---|
| 1–2 | DSCC public API | none exists — `replication-partners` is **GET only** | ✗ |
| 1–2 | WSAPI / `hpe3parclient` | `admitRemoteCopyLinks`, `startrCopy` are **SSH** under the hood; no `creatercopytarget` at all | ✗ as an API |
| 1–2 | On-system UI (array-local web UI) via Playwright | *Replication partner systems* (+) → *Replication partner* (+) dialogs; "remote system reachable through a proxy configured on the storage system" | possible, brittle, no doc of the dialog fields |
| 1–2 | **Generated two-sided command set** (ADR 0012 pattern) | the CLI guide is explicit and short; G-1 proved the pattern works | **✓ recommended** |
| 1–2 | Tool writes over a second, write-capable SSH client | breaks ADR 0001 (SSH read-only); needs plan → approve → apply like provisioning | later, once the command set has been proven live |
| 3 | **DSCC protection policy API** `POST …/applicationsets/{id}/protection-policies` (`sync`/`async`/`schedule`, `partnerId`, `rpoSecs`, `replicationPartnerUserCpg`, schedules) | documented; needs the array in DSCC (the lab pair is) | **✓ primary** — it is the strategic control plane (ADR 0006) and carries snapshot schedules |
| 3 | WSAPI `createRemoteCopyGroup` / `addVolumeToRemoteCopyGroup` / `startRemoteCopy` | REST in `hpe3parclient` | ✓ fallback when DSCC is not available |
| 3 verify | `showrcopy`, `showrcopy groups`, `showrctransport -rcip` over the read-only SSH client | already allowlisted | ✓ |
| failover test | DSCC `POST …/remote-protection/actions` — `SWITCHOVER`, `REVERSE`, `FAILOVER`, `RECOVER`, `SYNC` | documented, per application set | ✓ for the tool's **own test group** |

## 5. The lab (CRV, from `CRV Lab_Deploymnet v1.csv`) — a live Remote Copy pair

| | Landing Zone (LZ) | Vault Zone (VZ) |
|---|---|---|
| Array | `MPB10K-E24U21-LZ`, mgmt **10.64.154.225** (nodes .223/.224) | `MPB10K-D24U21-VZ`, mgmt **10.64.122.140** (nodes .138/.139), serial `SGHD44LQLS` |
| vCenter | 10.54.154.226 (3 ESXi: 10.64.159.14/.63/.64) | 10.99.1.100 (3 ESXi: 10.99.1.1–3, `DL360G11D24U25–27`) |
| SAN | (LZ fabric not in the sheet) | VZ-SAN-F1 10.64.122.146, VZ-SAN-F2 10.64.122.145 (SN3700B) |
| RCIP | **10.222.1.x /24, GW 10.222.1.254** — already configured; the pair is already replicating | same subnet |
| DSCC | onboarded | onboarded |
| Jump box | 10.54.122.137 (VZ) — the only place that reaches the arrays; this Mac cannot |

Consequences: (1) layers 1–2 already exist here, so the tool's **read + verify** of transport and
partnership can be proven live at once, and its generated command set can be diffed against reality;
(2) any **write** test must use the tool's own objects (`zz_rc_*` volume set → new RC group) and never
touch the existing production groups; (3) the **failover test** is exercised on that test group only;
(4) credentials are in the operator's hands, never in this repo.

## 6. The run model — one sheet, two arrays: the options

The customer HLD is a **two-site design document**: one engagement, one primary, one DR array, one
deliverable. The field engineer wants to fill **one workbook**. What the code assumes today: one run
= one array = one credential (ADR 0013) = one discovery = one as-built.

| | **A. One run holding two arrays** | **B. Two independent runs, linked later** | **C. One workbook → two *paired* runs** |
|---|---|---|---|
| Sheet | one workbook, every array field doubled (or an *Array B* tab) | two workbooks, as today | **one workbook**: *Initialisation* + *Provisioning* tabs gain an **Array B** column set (blank = single-array run, unchanged); new **Replication** tab |
| Run record | `arrays: [A, B]`; every step needs "which array" | unchanged | unchanged per run + `pair_id`, `role: primary/secondary`; the pair is minted from one upload |
| Credential model | ADR 0013 becomes "one per array per run" — every step re-plumbed | unchanged | **unchanged** |
| Per-array steps (init, discover, zoning, provision, verify) | rewritten to take an array index; UI needs an A/B switch inside every step | unchanged | **unchanged** — each runs on its own run; the wizard shows a pair header with an A/B switch that just changes which run the step pages read |
| Replicate step | on the run | on A, taking B's run id as input | on the **pair** (a step whose run is A, peer resolved via `pair_id`) |
| Resume / Open another run | one entry | two unrelated entries | two entries shown as one pair |
| Runner (SPEC-006) | every scenario re-shaped | unchanged + new scenario | unchanged + new scenario |
| As-built | one two-array document | two documents | one **pair** as-built (both arrays + replication + failover record), matching the HLD's shape |
| Effort | 4–5 releases, high regression risk on a live-verified track | 1–2 releases | **2–3 releases**, the provisioning track untouched |

**Recommendation: C.** It gives the field engineer exactly what "one sheet" means — one file, both
arrays, the replication design — while leaving every live-verified step, its data model and the
credential rule alone. The two-array pairing is metadata on top of runs, not a rewrite beneath them. A
can still be reached later by folding paired runs into one record if the UI ever needs it; nothing in C
prevents that.

## 7. What v0.17 would contain (proposed, for the spec)

1. **ADR 0014 — Paired runs from one workbook.** Array B columns; `pair_id` + `role`; the pair is
   created atomically; blank B = today's behaviour. A run's credential stays its own (ADR 0013 intact).
2. **ADR 0015 — Remote Copy links are delivered as a two-sided command set**, never written (extends
   ADR 0012 to the array); the tool confirms them with `showrctransport -rcip` / `showrcopy`.
3. **SPEC-015 — Workbook + paired runs.** Sheet fields (Array B, *Replication* tab: RC target names,
   RCIP port addresses per node, netmask, gateway, per-VV-set mode `sync|periodic`, period, peer CPG,
   snapshot schedule/retention), parser, `POST /runs/from-sheet` minting the pair, wizard pair header,
   *Open another run* grouping.
4. **SPEC-016 — Replicate step (`replicate`, phase `STORAGE_REPLICATE`).**
   *Read* both arrays (RCIP ports, `showrcopy`, CPGs, capacity, the VV sets provisioning created) →
   *check* the §2 constraints → *plan* the group(s) → *command set* for layers 1–2 when links are
   missing (skipped when `showrcopy` already shows the target `ready`) → *apply* layer 3 through the DSCC
   protection-policy API (WSAPI fallback) → *verify* on both arrays (group `Started`, volumes `Synced`,
   RPO) → **removal set** for exactly what it created (SPEC-007 pattern).
5. **SPEC-017 — Failover test.** On the tool's test group (or an operator-selected group with a typed
   confirmation): `SWITCHOVER` → verify roles swapped on both arrays → `REVERSE`/failback → verify → a
   *Failover test record* in the as-built. Sync and periodic differ (periodic may lose a period; say so).
6. **SPEC-018 — As-built for the pair**: both arrays' sections, *Replication configured in this run*
   (links, targets, groups, policy), the failover test record, and the HLD's §1.6 assumptions / §1.7
   risks rendered from the run's facts.
7. **Runner scenario 7** (`session.ps1`): on the CRV pair, create `zz_rc_*` volume set on LZ →
   replicate to VZ → verify both → switchover/back → remove.

Order of work: SPEC-015 (the sheet and pairing are prerequisites) → SPEC-016 read/check/command set
**proven live against the existing CRV links** → SPEC-016 layer 3 + verify → SPEC-017 → SPEC-018.

## 8. Decisions needed before SPEC-015 is written

1. **Model C confirmed?** (one workbook, paired runs). If you want A regardless, say so; it is a
   different spec and a longer road.
2. **Default replication mode and period** on the sheet: the HLD used *async periodic*; propose
   `periodic`, period 300 s (RPO 10 min) as the default, `sync` selectable.
3. **Layer 3 primary = DSCC API.** The lab pair is onboarded, so this is testable; WSAPI as fallback
   only. Agree?
4. **Failover test default = the tool's own test group only.** Production groups need an explicit
   selection plus a typed confirmation. Agree?
5. **Snapshot-only protection** (a schedule with no peer) in the same *Replication* tab and step, or a
   separate later item?

## 9. First live action (read-only, no decisions needed)

A paste-script for the jump box that reads both CRV arrays over SSH — `showsys`, `showport -rcip`,
`showrctransport -rcip`, `showrcopy`, `showrcopy groups`, `showvvset`, `showcpg` — and saves the output
as fixtures. That pins the parsers for SPEC-016 to real captures before any code is written, exactly
as `tests/fixtures/rack13_wsapi/` did for provisioning.
