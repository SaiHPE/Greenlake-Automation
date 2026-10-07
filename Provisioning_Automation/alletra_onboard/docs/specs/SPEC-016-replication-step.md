# SPEC-016 — The Replication step: link the arrays, protect the volume sets, verify

**Status:** APPROVED 2026-10-07 (operator decisions: the tool configures links and partnership
itself; sync and async first) — not implemented
**ADRs:** [0014](../adr/0014-paired-runs-from-one-workbook.md), [0015](../adr/0015-tool-configures-remote-copy-write-scoped-ssh.md)
**Depends on:** SPEC-015 (pair, Replication tab)
**Research:** [2026-10-07](../research/2026-10-07-replication-document-review.md) §2–§5 — every
command, limit and state below is traced there to an HPE guide (ED8, Aug 2026) or the array's own
`-h` output captured on AlletraMP_D22U27
**Owner:** `application/replication/` (new bounded context: `steps.py`, `read.py`, `plan.py`,
`apply.py`, `verify.py`), `adapters/array/rc_cli_client.py` (new, ADR 0015), `adapters/dscc/`
(protection policies), `domain/replication.py`, `frontend/src/steps/ReplicationStep.tsx`

## 1. Problem

With two arrays paired (SPEC-015) and each one discovered, zoned and provisioned, the engineer still
configures replication by hand on both arrays: RCIP addresses, targets, links, a Remote Copy group,
policies, period, admitted volumes, start — in the right order, on the right array — then checks
`showrcopy` on both. One wrong step (a gateway after the links, one link instead of two, a missing
target CPG) fails silently or late.

## 2. Requirements

The step runs on the pair. It has the same five stages as provisioning: **read → check → plan →
apply → verify**, and ends with a **removal set**.

**R1 — Read both arrays (read-only client).** For A and B: `showsys` (name, serial, nodes, OS),
`showport -rcip`, `showrctransport -rcip`, `showrcopy` (system status), `showrcopy targets`,
`showrcopy links`, `showrcopy groups`, `showvvset`, `showcpg`. All are on the read allowlist
(ADR 0001) except `showrctransport`, which is added to it. Parsers are pinned to real captures from
the lab pair (§4) before code.

**R2 — Check before planning (blocking findings, one sentence each, never guessed).**
- Each array has ≥ 2 RCIP ports usable, on 2 different nodes (from the sheet or already addressed).
- RCIP port IPs unique; not in the management subnet; not an iSCSI port. On a node with 2 RCIP links,
  each link on a subnet different from every other interface on that node (ED8).
- Ports per target and partners per system within the Support Matrix column for **that array's OS**
  (OS 10.5: 4 targets/port, 4 partners; 10.6: 6/4; 10.4: 2/2).
- Sync rows: measured RTT ≤ 10 ms. Async rows: ≤ 200 ms.
- The primary volume set exists on the primary (created by this run's provisioning or already there).
- The secondary CPG exists on the secondary and has free space ≥ the primary set's provisioned size.
- No existing Remote Copy group already holds a volume of the set (a volume belongs to one group).
- Remote Copy started on each array, or plannable (`startrcopy`).

**R3 — Plan, per layer, with *exists / create / conflict* like the provisioning plan (SPEC-001).**
1. *Transport* — per RCIP port: already addressed as the sheet says → exists; unaddressed → create
   (`controlport rcip addr`, then `gw` if a gateway is given); addressed differently → **conflict**
   (the tool never re-addresses a port in use).
2. *Partnership* — target for B on A and for A on B: present with ≥ 2 links `Up` → exists; absent →
   create (`creatercopytarget <name> IP <N:S:P>:<peer_ip> <N:S:P>:<peer_ip>` on each side); present
   with fewer links than planned → create the missing links (`admitrcopylink`).
3. *Protection* — per Replication-tab row: group absent → create; present with the same volume set,
   mode and target → exists; anything else → conflict.
The plan shows, for every *create*, the exact commands (or the DSCC call and its CLI equivalent) per
array, in execution order, labelled **A** / **B**.

**R4 — Execution order (fixed, from the CLI guide ED8).**
```
A, B  startrcopy                                                   if not started
A, B  controlport rcip addr …  ;  controlport rcip gw …            per new port; gateways BEFORE any link
A, B  controlport rcip ping <peer_ip> <N:S:P>                      per planned link; up to 3 tries, 10 s apart
A     creatercopytarget <B> IP <N:S:P>:<B_ip> <N:S:P>:<B_ip>
B     creatercopytarget <A> IP <N:S:P>:<A_ip> <N:S:P>:<A_ip>
      wait: showrcopy links on both shows every planned link Up    (≤ 120 s, then stop with the reason)
A*    protection per row — DSCC (R5) or CLI:
        creatercopygroup -usr_cpg <cpgA> <B>:<cpgB> <group> <B>:periodic|sync
        setrcopygroup pol auto_synchronize <group>    ;  setrcopygroup pol auto_recover <group>
        setrcopygroup period <RPO/2>m <B> <group>                  async only
        admitrcopyvv -createvv set:<vvset> <group> <B>:<vvset_sec>
        startrcopygroup <group>                                     secondary first only if the target
                                                                    policy is no_mirror_config (read in R1)
```
*A\** = the row's primary side (Direction). When an array's RCIP ports are on different subnets, a
ping that still fails after 3 tries stops the apply before any target is created, with the port and
the reason; nothing half-linked is left behind. When two ports share a subnet the guide says ping
fails until links are admitted, so the ping result is shown but not blocking, and the link wait
(links `Up` within 120 s) is the gate.

The test group's volume and VV set (SPEC-015 R6) are created through WSAPI before the protection
layer, as provisioning creates volumes.

**R5 — Protection through DSCC when available.** When the sheet carries GreenLake API credentials
and both arrays are found in DSCC (`devtype4-storage-systems` by serial): `POST
…/applicationsets/{id}/protection-policies` with `protectionPolicyType` `async`/`sync`,
`policy.remote.partnerId/partnerName` (from `GET …/replication-partners`),
`replicationType` `periodic`/`sync`, `replicationPartnerUserCpg`, `rpoSecs` = RPO × 60,
`autoSynchronize`, `autoRecover`; poll the async operation. Otherwise the CLI commands of R4.
Either way verification (R7) is the same SSH read.

**R6 — Approval gate.** Nothing is written until the operator ticks *"I have reviewed this plan and
authorise configuring replication on both arrays"* and clicks *Configure replication* — the same gate
as *Create storage objects*. A plan with a conflict cannot be applied (409 with the conflict).

**R7 — Verify (read-only, both arrays).** After apply, and on demand (*Verify replication*):
- Every planned link `Up` (`showrcopy links`) on both arrays.
- Each group: Status `Started`; Role `Primary` on the primary and `Secondary` on the other; Mode as
  planned; every volume's SyncStatus `Synced` — `Syncing` is reported as *initial sync in progress
  (n of m volumes)* and re-checked, never failed; `Stale` / `Stopped` after a start is a failure with
  HPE's own next step (troubleshooting ED6: *start the group*; *Stale persists → contact HPE
  Support*). The tool never retries a write in a loop.
- Async: the configured period equals RPO / 2.
- The secondary volume set exists on the secondary with the same volume count and sizes.
- The `RCP_<group>` VV set that `creatercopygroup` creates on the primary is expected: it is reported,
  never a conflict and never a separate removal line (`removercopygroup` owns it).
Verdict per group: **Replicating** · **Initial sync in progress** · **Not replicating (reason)**.

**R8 — Removal set (SPEC-007 pattern).** Exactly what this run created, in reverse dependency order,
per array: `stoprcopygroup` → `dismissrcopyvv -removevv set:<vvset> <group>` →
`removercopygroup` → `dismissrcopylink` (links the run admitted) → `removercopytarget` (targets
the run created) → the test volume and VV set on the primary (`removevvset`, `removevv`, SPEC-007
lines) → RCIP addresses are **not** removed (re-addressing a port is the network team's
call; the as-built records them). Objects that existed before the run are never in it. Shown as
two blocks, **A** and **B**.

**R9 — Facts for the as-built.** The step records: RCIP ports and addresses per array, targets and
links (with status), each group (name, mode, period/RPO, policies, role per array, volumes with sync
status), the control plane used (DSCC or CLI) and the commands issued.

**R10 — Existing replication is respected.** Groups, targets and links the run did not create are
shown (read) and never modified, stopped or removed. The lab pair already replicates
(`rcopy_async_test`); every test object is `zz_rc_*`.

## 3. Non-goals

Active Peer Persistence, Active Sync, SLD, 3DC, MxN; RCFC; Quorum Witness; snapshot schedules
(BL-21); changing a group's mode or period after creation (remove and recreate); re-addressing RCIP
ports already in use.

## 4. Verification

**Before code** — read-only capture on both lab arrays (D22U27 ↔ E18U31, already replicating),
saved to `tests/fixtures/rc_pair/`: `showsys`, `showversion`, `showport -rcip`,
`showrctransport -rcip`, `showrcopy`, `showrcopy -d`, `showrcopy links`, `showrcopy targets`,
`showrcopy groups`, `showvvset`, `showcpg`. Parsers are written against these.

**Unit** — R2 checks one test each; R3 exists/create/conflict per layer; R4 order (gateway before
links, targets on both sides, start order by target policy); the DSCC body (R5) against the API
mirror's field list; R7 verdicts from captured `showrcopy groups` (Synced / Syncing / Stale /
Stopped); R8 order and "never the pre-existing objects"; the write client refuses any command not in
ADR 0015's list and any `controlport` other than `rcip addr|gw|ping`.

**Live (lab pair)** — (1) read and verify the existing group `rcopy_async_test` without touching it;
(2) create `zz_rc_test` (1 GiB) on D22U27 and protect it **async** to E18U31 using the existing
partnership → *Replicating*; (3) same with **sync** (if the measured RTT allows); (4) removal set
pasted/applied → nothing `zz_rc_*` left on either array; (5) on a pair with no partnership (if one
becomes available) the full transport + partnership path. Runner scenario 7 (SPEC-006 addendum)
automates (2) and (4).

## 5. Size

Read + parsers (~250), checks (~150), plan (~200), apply with ordering and ping/link waits (~250),
DSCC adapter (~150), verify (~150), write client (~80), UI step (~350), as-built facts (~60), ~45
unit tests. Two releases: (a) read, check, plan, verify against the existing pair; (b) apply and
removal set.
