# Research addendum — Replication: the 2026-10-07 document set

**Date:** 2026-10-07 · **Extends:** [2026-09-19-replication-two-arrays.md](2026-09-19-replication-two-arrays.md)
(the design options, the run model and the §8 decisions there still stand) · **Status:** research; no
code. The decisions in §6 below are what SPEC-015 needs.

## 1. The documents, graded

Eleven files were handed over in *Replication - Automation*. Three are not HPE publications and the
operator flagged them as possibly AI-written. Every claim below is traced to a document; the two
AI-looking guides are used only where an HPE guide or a live array capture agrees.

| File | What it is | Edition / date | Trust | Use |
|---|---|---|---|---|
| *Configuring and managing data replication using Remote Copy and the CLI* | HPE, procedure of record | **ED8, Aug 2026, updated for OS 10.5.0** (the 09-19 research used ED7) | authoritative | §2–§4 |
| *Getting started with data replication using Remote Copy and the CLI* | HPE, planning + concepts | ED8, Aug 2026 | authoritative | §3 |
| *Troubleshooting data replication using Remote Copy and the CLI* | HPE, failure states, `showrcopy` samples | ED6 | authoritative | §4 verification vocabulary |
| *Configuring and managing … using the on-system UI 2.6* / *Getting started … UI* / *Troubleshooting … UI* | HPE, the array's local web UI | ED7, Aug 2026 (UI 2.6) | authoritative | §5 — what the UI does and does not expose |
| *HPE Alletra Storage MP B10000 Support Matrix* | HPE (SPOCK) | OS 10.4 / 10.5 / 10.6 columns | authoritative | §3 limits |
| *HPE Alletra Storage MP B10000 architecture* (a50008302enw) | HPE technical white paper | — | background only | nothing replication-specific beyond the guides |
| `replication_sync_commands.docx` | **A capture of the array's own `<cmd> -h` help pages**: `showrcopy`, `creatercopygroup`, `admitrcopyvv`, `startrcopygroup`, `setrcopygroup`, `stoprcopygroup`, `syncrcopy`, plus `createvv`/`showvv`/`showvlun`/`createvlun`/`removevlun`/`showhostset`/`createhostset`/`removehostset`/`removevv`. The prompt `AlletraMP_D22U27 cli%` appears in it — taken on our lab array. | current OS | **high** — real CLI output | §4 exact syntax; §7 fixtures |
| `HPE_Alletra_B10000_Async_Replication_CLI_Guide.docx` | Generic "from scratch" periodic walkthrough | — | **AI-written; mostly right, three errors** (§1.1) | none beyond cross-check |
| `Types of Replication.docx` | One-page sync vs periodic summary | — | **AI-written; partly wrong** (§1.1) | none |

### 1.1 Errors in the AI-written documents (do not carry into the spec)

| Claim | Why it is wrong | Correct, with source |
|---|---|---|
| Async guide §5: `creatercopytarget … IP 0:2:1:10.10.20.20` | Slot 2 is an NVMe drive-path port on a B10000; RCIP is **slot 4, ports 3/4** on the add-on Ethernet HBA (built-in ports not supported) | Support Matrix *Maximum supported RCIP ports*; our arrays: D22U27 0:4:3/1:4:3, E18U31 0:4:3/1:4:3 (`showport -rcip`) |
| Async guide §5: one target link | Minimum is **two links from two different nodes** per target | CLI guide ED8 p.14; Support Matrix *Minimum required RC links per RC-Target 2* |
| Async guide §9: `admitrcopyvv -createvv AppVol01 …` with no CPG anywhere | `-createvv` needs the target CPG, given on the group with `creatercopygroup -usr_cpg <local> <target>:<remote>` | `creatercopygroup -h` (captured); CLI guide ED8 p.116 |
| Types doc: "Synchronous … Secondary Systems: one receives sync, the other periodic" | That describes **SLD** (three systems), not synchronous replication | Getting started ED8 *Synchronous long distance configuration* |
| Types doc: "Asynchronous … No strict latency requirements" | RCIP periodic has a **200 ms RTT** ceiling; RCFC periodic 10 ms | Support Matrix *Asynchronous Periodic → Maximum Latency* |
| Async guide: `setrcopygroup period 15m` as "RPO 15 minutes" | RPO ≈ **2 × period**; a 15 m period is a 30 m RPO | UI guide ED7 *Replication protection policies — overview*; Getting started *Recovery Point Objective* |

What the async guide gets right and the 09-19 research had not spelled out: `setrcopygroup pol
auto_synchronize` and `pol auto_recover` **before** starting the group (CLI guide ED8 p.116 marks
both as HPE-recommended), `syncrcopy <group>` for a manual sync, `srstatrcvv -hourly` for statistics.

## 2. What changed between ED7 and ED8 (CLI guide)

- **Targets per RCIP port:** 6 on OS 10.6 (4 on 10.5, 2 on 10.4). The 09-19 research said "≤ 4" —
  make it **version-dependent** and read from the Support Matrix column for the array's OS.
- **RCIP VLAN tagging** on `controlport rcip addr/gw/ping` and `creatercopytarget` (`-vlan <1–4094>`),
  with the rule "if no gateway is used with a VLAN, the partner ports must carry the same tag".
- **Gateway sequencing:** set gateways **before** bringing links up; with ≥ 2 RC links per node the
  links must be on **different subnets** from every other interface on the node.
- **Max 2 physical RCIP links per node** (was not stated in ED7's requirements list).
- `showrctransport -rcip` is the read that shows links with gateway/VLAN; `showrcopy links` shows
  link `Status Up/Down`.

## 3. Planning limits the tool must check (Support Matrix, OS 10.5 column — the lab arrays)

| Limit | Value |
|---|---|
| Replication partners per system | 4 (2 on OS 10.4) |
| RCIP ports | 2 × 10/25 GbE per node, add-on HBA only |
| Targets per RCIP port | 4 (10.5) · 6 (10.6) · 2 (10.4) |
| Links per target | ≥ 2, from two different nodes; ≤ 2 physical RCIP links per node |
| RTT, synchronous | ≤ 10 ms (RCIP, RCFC, FCIP) |
| RTT, periodic | ≤ **200 ms** RCIP · 10 ms RCFC · 120 ms FCIP |
| Minimum periodic interval | 15 s |
| Groups (2-node system) | 800 sync · 2400 periodic |
| Volumes per group | 800 sync · 1800 periodic |
| MTU | 1280–9000 |
| Firewall | TCP 5785 and 5001; no NAT |
| Transport sharing | RCIP and iSCSI cannot share a port; the RC subnet may carry other I/O if RTT holds |

The tool can read everything in the top eight rows from the two arrays (`showsys`, `showport -rcip`,
`showrctransport -rcip`, `showrcopy targets`, `showversion`). RTT it can only *ask for* (a sheet
field) or measure by `controlport rcip ping` — a write-class command (it is on the array; it changes
nothing, but it is not `show*`). Decision in §6.

## 4. The procedure of record, confirmed (ED8 + captured help)

The 09-19 §3 command list stands. Corrections and additions:

```
A, B   startrcopy
A, B   controlport rcip addr <ip> <mask> [-vlan <tag>] <N:S:P>        per RCIP port
A, B   controlport rcip gw <gw> [-vlan <tag>] <N:S:P>                 BEFORE links come up; only if subnets differ
A|B    controlport rcip ping <peer_ip> [-vlan <tag>] <N:S:P>          may need retries; fails until links admitted if 2 ports share a subnet
A      creatercopytarget <B> IP [-vlan <tag>] <N:S:P>:<B_ip> <N:S:P>:<B_ip>    ≥ 2 links, 2 nodes
B      creatercopytarget <A> IP [-vlan <tag>] <N:S:P>:<A_ip> <N:S:P>:<A_ip>
A      creatercopygroup -usr_cpg <cpgA> <B>:<cpgB> <group> <B>:periodic|sync     name ≤ 22 chars (mirror_config default)
A      setrcopygroup pol auto_synchronize <group>                     HPE-recommended
A      setrcopygroup pol auto_recover <group>                         HPE-recommended
A      setrcopygroup period <n>{s|m|h|d} <B> <group>                  periodic only; 15 s … 1 y; RPO ≈ 2×
A      admitrcopyvv -createvv set:<vvset> <group> <B>:<vvset_sec>     creates the secondary set + volumes
A      startrcopygroup <group>                                        mirrored to B (mirror_config)
verify showrcopy · showrcopy groups · showrcopy links · showrctransport -rcip · showport -rcip
undo   stoprcopygroup <group> · dismissrcopyvv -removevv set:<vvset> <group> · removercopygroup <group>
       (links/targets only if the tool created them: dismissrcopylink · removercopytarget)
```

Facts from the captured help that shape the design:

- `creatercopygroup` **also creates a VV set `RCP_<group>`** on the primary; volumes admitted to the
  group join it. The tool must expect (and the removal set must tolerate) that set.
- `admitrcopyvv -createvv` uses the **same WWN** on the secondary unless `-nowwn`; a DECO primary
  becomes a TPVV secondary when the target CPG cannot do dedup+compression.
- `startrcopygroup`: with the default **`mirror_config`** target policy the start is mirrored and the
  secondary need not be started first. Without it, "You must enter this command on the secondary
  server before entering it on the primary". The tool should read the target policy and only emit the
  one-sided start when `mirror_config` is set; otherwise it emits B first.
- Group name limit is **22** characters under `mirror_config` (31 otherwise) — a name check for the
  Names panel, like the FOS 64-character rule.
- `-createvv` and starting snapshots are mutually exclusive; the tool never uses starting snapshots.

### 4.1 Verification vocabulary (Troubleshooting ED6, real samples)

```
Remote Copy System Information
Status: Started, Normal                       ← system: Started|Stopped, Normal|…

Link Information
Target   Node  Address       Status Options        VLAN
SysB_pri 0:4:3 10.x.50.101   Up     5120KB/s tput  -       ← per link: Up|Down
receive  0:4:3 receive       Up     -              -

Group Information
Name        Target    Status   Role      Mode     Options
SysBGroup1  SysB_pri  Started  Primary   Sync             ← Status Started|Stopped|Failsafe; Role Primary|Secondary|Primary-Rev|Secondary-Rev
  LocalVV   ID    RemoteVV   ID    SyncStatus  LastSyncTime
  AB10      15642 AB10.0     16102 Synced      NA         ← Synced|Syncing|Stopped|Stale|NotSynced
```

`Synced` on every volume + group `Started` + every link `Up` = the tool's "replicating" verdict.
`Stale` after a start = "contact HPE Support" (never retry in a loop). The role table on p.34 of the
troubleshooting guide is the state machine for §5.3 (failover test): *Primary/Stopped + Secondary/Stopped
→ start*; *Primary/Failsafe + Primary-Rev/Stopped → recover or restore*; *Secondary-Rev + Primary-Rev →
restore or reverse*; *Primary-Rev + Secondary → reverse*.

## 5. The on-system UI (ED7, UI 2.6) — what it changes

1. **Protection policies on a VV set** are the UI's unit of replication: *Asynchronous* (time period,
   auto recovery, auto sync) or *Synchronous* (auto sync, auto recovery, optional High Availability =
   Active Peer Persistence / Active Sync with host proximity). Creating one **creates the Remote Copy
   group on both arrays** and names the remote set `source_vvset_name.r<source_vvset_id>`.
   The DSCC API's `protection-policies` endpoint is the same object (§5.1).
2. **Replication partner system** (+) / **Replication partner** (+): the UI's dialogs for layers 1–2.
   The guide gives no field list — only "follow the instructions on the dialog". Browser automation of
   these stays *possible, undocumented* (09-19 §4 verdict unchanged).
3. **Importing CLI-made groups:** a Remote Copy group created at the CLI is imported into the UI/DSCC
   and **becomes a virtual volume set** that must then be managed as one. So the two control planes
   are not symmetrical: CLI → UI/DSCC is a one-way conversion.
4. **Quorum Witness** is required only for Active Peer Persistence **automatic** transparent failover
   (ATF). 1-to-1 sync/periodic and manual switchover need none. E18U31's note "no quorum witness" is
   therefore not a blocker for the planned scope.

### 5.1 DSCC Block Storage API (local mirror, v1alpha1) — re-read

`POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies`

| Field | Values | Maps to CLI |
|---|---|---|
| `protectionPolicyType` | `schedule` · `sync` · `async` | — |
| `policy.remote.partnerId`, `partnerName` | from `GET …/replication-partners` | `creatercopytarget` name |
| `policy.remote.replicationType` | `sync` · `periodic` | `creatercopygroup <t>:<mode>` |
| `policy.remote.replicationPartnerUserCpg` | CPG on the partner | `-usr_cpg … <t>:<cpg>` |
| `policy.rpoSecs` | 30 – 63 072 000, even | `setrcopygroup period` (= rpoSecs / 2) |
| `policy.autoRecover`, `autoSynchronize` | bool | `setrcopygroup pol auto_recover / auto_synchronize` |
| `policy.overPeriodAlert` | bool | `setrcopygroup pol over_per_alert` |
| `policy.zeroRtoConfig` | `APP` | Active Peer Persistence (out of scope) |
| `schedules[]` | name, period + unit, expireSecs, isRemote, atTime, days | `createsched` snapshot schedules |

Companions in the same folder: `edit`, `remove`, `fix` protection policies; `getreplicationpartnersbyappsetid`;
`getreplicationpartnervolumesbyappsetid`; `getsupportedprotectiontypes`. **No endpoint creates a
replication partner** (layers 1–2) — confirmed again. `rpoSecs` minimum 30 s matches the 15 s
minimum period (RPO = 2 × period).

So layer 3 through DSCC is: find the application set (= the VV set provisioning created, by name on
the system), `POST protection-policies` with `async`/`periodic`/`rpoSecs`/partner CPG, then verify with
`showrcopy groups` over SSH on both arrays. One call replaces `creatercopygroup` + two `setrcopygroup
pol` + `setrcopygroup period` + `admitrcopyvv -createvv` + `startrcopygroup`. That is the main argument
for DSCC-first; the CLI command set stays as the fallback and as the **explanation** the as-built
prints (the operator should see what the policy did on the array).

## 6. Decisions — restated with the new evidence

The five questions in the 09-19 research §8 stand. The evidence now supports these defaults:

| # | Question | Proposed default | Why |
|---|---|---|---|
| 1 | Run model | **C** — one workbook, paired runs | unchanged; nothing in the new documents touches it |
| 2 | Default mode and period | **periodic**, period **300 s** → RPO 10 min; `sync` selectable; period never below 15 s; the sheet asks for *RPO* and the tool derives period = RPO / 2 (the field engineer thinks in RPO, every HPE guide converts) | UI/Getting-started RPO rule; Support Matrix minimum |
| 3 | Layer 3 control plane | **DSCC protection-policy API first**, CLI command set as fallback **and** as the printed explanation | §5.1: one call covers six CLI commands and carries the snapshot schedule; both lab arrays are in DSCC |
| 4 | Failover test | only on the tool's own test group by default; production groups need a typed confirmation; **manual switchover only** (`setrcopygroup switchover`) — no APP/ATF, no Quorum Witness | §5 (4); troubleshooting role table |
| 5 | Snapshot-only protection | **same tab and step** — it is `protectionPolicyType: schedule` on the same endpoint | §5.1 |
| 6 *(new)* | RTT | the sheet carries *measured RTT (ms)* as an operator-entered field; the tool refuses sync > 10 ms and periodic > 200 ms (RCIP) and prints the `controlport rcip ping` lines for the operator to run — it does **not** run them (write-class) | §3; ADR 0001 |
| 7 *(new)* | Links and targets | **read + verify + command set only** (two-sided, A and B blocks, `cfgenable`-style separation of the `startrcopygroup`); never written by the tool in v0.17 | 09-19 §4; ED8 p.21 gateway-before-links sequencing is too easy to get wrong silently |
| 8 *(new)* | `mirror_config` | the tool reads `showrcopy targets` for the target policy and emits the start order accordingly | §4 |

If you agree with the defaults, SPEC-015 (sheet + paired runs) can be written without further research.

## 7. First live action — unchanged, now with a file list

Read-only capture on **both lab arrays** (D22U27 ↔ E18U31, which already replicate: group
`rcopy_async_test`), from labrat over SSH, saved as fixtures under `tests/fixtures/rc_pair/`:

```
showsys · showversion · showport -rcip · showrctransport -rcip
showrcopy · showrcopy -d · showrcopy links · showrcopy targets · showrcopy groups
showvvset · showcpg · showsched   (snapshot schedules, if any)
```

Plus `showrcopy groups rcopy_async_test` on both sides for the Primary/Secondary pair of the same
group, and `srstatrcvv -hourly` once (statistics format). These pin the parsers for `showrcopy`
(system status, links, groups, per-volume sync status), `showrctransport -rcip` and `showport -rcip`
before any code. The 09-19 research expected the CRV LZ/VZ pair for this; LZ is dead, so the pair is
**D22U27 ↔ E18U31**. E18U31's existing group has *failed reverse tasks* — a real failure state to
capture too.
