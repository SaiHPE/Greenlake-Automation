# SPEC-016 — The Replication step: protect volume sets over an existing partnership

**Status:** APPROVED 2026-10-07; **re-cut the same day** — v0.17 creates Remote Copy groups over
**WSAPI** on a partnership that already exists; configuring the partnership itself (RCIP ports,
targets, links) is the v0.19 release under ADR 0015 — not implemented
**ADRs:** [0015](../adr/0015-tool-configures-remote-copy-write-scoped-ssh.md) · [0001](../adr/0001-post-init-verification-via-ssh-cli.md) (reads stay read-only; untouched in v0.17)
**Depends on:** SPEC-015 (the tab, the steps)
**Research:** [2026-10-07](../research/2026-10-07-replication-document-review.md) §3–§4 — limits
and states traced to the HPE guides (ED8, Aug 2026) and the array's own `-h` output; WSAPI body
shapes from the `hpe3parclient` the tool already provisions with (`/remotecopygroups`)
**Owner:** `application/replication/` (new bounded context: `steps.py`, `read.py`, `plan.py`,
`apply.py`, `verify.py`), `adapters/array/wsapi_client.py` (remote-copy-group calls),
`domain/replication.py`, `frontend/src/steps/ReplicationStep.tsx`

## 1. Problem

The partnership between two arrays is set up once, usually at install. What repeats per engagement
is protecting the volume sets the engineer has just provisioned: a group with the right mode, period
and policies, every volume admitted with its secondary created on the right CPG, started, and
`showrcopy` checked on both arrays. By hand that is eight commands in a fixed order on the right
array, and a mistake (wrong CPG, a volume already in another group, a group never started) shows
late.

## 2. Requirements

Same five stages as provisioning — **read → check → plan → apply → verify** — and a **removal set**.
Writes go through **WSAPI**, the write plane provisioning already uses, with this run's array
credential on the primary and the tab's peer credential on the peer. No SSH write in this release.

**R1 — Read both arrays.** Over the read-only SSH client (ADR 0001) on each: `showsys`,
`showversion`, `showport -rcip`, `showrctransport -rcip` (added to the read allowlist), `showrcopy`,
`showrcopy targets`, `showrcopy links`, `showrcopy groups`, `showvvset`, `showcpg`. Over WSAPI on the
primary: `GET /remotecopy`, `GET /remotecopygroups`. Parsers are pinned to the BL-38 captures first.

**R2 — Check (blocking findings, one sentence each; nothing guessed).**
- **Partnership present, matched by address, not by name:** on each array a target whose links'
  peer addresses (`showrctransport -rcip` `PeerIPAddress`) are the other array's RCIP addresses
  (`showport -rcip` `IPAddr`), with ≥ 2 links `Up`. Target names are not trusted — on the lab pair
  E18U31's target for D22U27 is itself named `AlletraMP_E18U31` (fixtures README). The matched
  target's name is what the tool passes as `targetName`. Otherwise: *"No Remote Copy partnership
  between <A> and <B>. The tool configures partnerships from v0.19 (ADR 0015); until then it has to
  exist before this step."* The partnership is read, never created, in this release.
- Remote Copy started on both arrays (`showrcopy` system status).
- Sync rows: RTT ≤ 10 ms; async rows: ≤ 200 ms (from the tab).
- The volume set exists on the primary with ≥ 1 member; no member is already in a Remote Copy group.
- The peer CPG exists on the peer with free space ≥ the set's provisioned size.
- Group counts within the Support Matrix for that array's OS (read from `showversion`).

**R3 — Plan, exists / create / conflict (SPEC-001 pattern).** Per Protection row:
- Group absent → **create**; present with the same volume set, mode and target → **exists**;
  present with anything else → **conflict** (the tool never changes an existing group's mode, period
  or members).
- The peer volume set (`<set>_rc`): absent → create on the peer; present → exists.
- When the tab's failover test is `yes`: a row for the test volume, set and group (SPEC-015 R3).
The plan shows every create as the WSAPI call it will make **and the CLI command it is equivalent
to**, labelled **A** (primary) or **B** (peer), in execution order.

**R4 — Apply order (fixed; CLI equivalents from the ED8 guide).**

| # | Where | WSAPI | CLI equivalent |
|---|---|---|---|
| 1 | A | provisioning's own volume/VV-set calls for the test objects (if planned) | `createvv`, `createvvset` |
| 2 | A | `POST /remotecopygroups` `{name, targets:[{targetName:<B>, mode: 1 sync / 2 periodic, userCPG:<peer CPG>}], localUserCPG:<primary CPG>}` | `creatercopygroup -usr_cpg <cpgA> <B>:<cpgB> <group> <B>:sync|periodic` |
| 3 | A | `PUT /remotecopygroups/<group>` `{targets:[{targetName:<B>, syncPeriod: RPO×30, policies:{autoRecover:true, autoSynchronize:true}}]}` (`syncPeriod` async only; field names confirmed from the BL-38 `GET` — fixtures README) | `setrcopygroup period <RPO/2>m <B> <group>` · `setrcopygroup pol auto_recover|auto_synchronize <group>` |
| 4 | A | per set member: `PUT /remotecopygroups/<group>` `{action: admit, volumeName, targets:[{targetName:<B>, secVolumeName:<same name>}], volumeAutoCreation: true}` | `admitrcopyvv -createvv <vol> <group> <B>:<vol>` |
| 5 | B | create VV set `<set>_rc` with the volumes step 4 created | `createvvset <set>_rc`, `createvvset -add …` |
| 6 | A (B first if the target policy is `no_mirror_config`, read in R1) | `PUT /remotecopygroups/<group>` `{action: start}` | `startrcopygroup <group>` |

A failure at any step stops the apply, reports the step and the array's message, and the removal
set covers exactly what was created up to that point.

**R5 — Approval gate.** Nothing is written until the operator ticks *"I have reviewed this plan and
authorise configuring replication on both arrays"* and clicks *Configure replication* — the same gate
as *Create storage objects*. A plan with a conflict or a blocker cannot be applied (409).

**R6 — Verify (read-only, both arrays).** After apply and on demand (*Verify replication*):
- The target's links `Up` on both arrays.
- Each group: Status `Started`; Role `Primary` on A and `Secondary` on B — on B the group is named
  `<group>.r<A's decimal system ID>` (WSAPI `remoteGroupName`; `300gb` ↔ `300gb.r188150` in the
  fixtures), which is how the tool finds it there; Mode as planned; async
  period = RPO / 2; every volume `Synced` — `Syncing` is reported as *initial sync in progress (n of
  m volumes)* and re-checked, never failed; `Stale` / `Stopped` after a start is a failure with HPE's
  own next step (troubleshooting ED6: *start the group*; *persists → contact HPE Support*). The tool
  never retries a write in a loop.
- The peer volume set has the same volume count and sizes as the primary set.
- The `RCP_<group>` VV set the array creates on the primary is expected: reported, never a conflict,
  never a removal line of its own (`removercopygroup` owns it).
Verdict per group: **Replicating** · **Initial sync in progress** · **Not replicating (reason)**.

**R7 — Removal set (SPEC-007 pattern: CLI lines the operator pastes, in reverse dependency order).**
Exactly what this run created, as two blocks:
- **A:** `stoprcopygroup <group>` → `dismissrcopyvv -removevv <vol> <group>` per volume (removes
  the secondary volume too) → `removercopygroup <group>` → the test volume and set lines when created.
- **B:** `removevvset <set>_rc`.
Objects that existed before the run are never in it.

**R8 — Facts for the as-built (SPEC-018).** Partnership read (targets, links, RCIP ports and
addresses per array); each group (name, mode, RPO and period, policies, role per array, volumes with
sync status and last sync time); the calls made and their CLI equivalents; the removal set.

**R9 — Existing replication is respected.** Groups, targets and links the run did not create are
shown and never modified, stopped or removed. The lab pair already carries six Sync groups, one of
them a Peer Persistence group (`APP_Test`, `active_active`); every object the tool makes there is
`zz_rc_*`.

## 3. Deferred to v0.19 (ADR 0015, decision unchanged, sequenced)

Transport and partnership configured by the tool — `startrcopy`, `controlport rcip addr/gw/ping`,
`creatercopytarget`, `admitrcopylink` and their removal — over the write-scoped SSH client. Not in
v0.17 because the lab pair is already partnered, so that path cannot be proven live without
dismantling it; R2's blocker says so.

## 4. Non-goals

Peer Persistence, Active Sync, SLD, 3DC, MxN; RCFC; Quorum Witness; snapshot schedules (BL-21);
DSCC protection-policy API (dropped — its one advantage, the snapshot schedule, left with BL-21);
changing an existing group (remove and recreate); replicating from the peer back.

## 5. Verification

**Before code (BL-38) — done 2026-10-07.** Read-only capture on D22U27 and E18U31 saved to
`tests/fixtures/rc_pair/` (README there lists every fact): the SSH list in R1 plus `showrcopy -d`,
the `-h` of every Remote Copy command, **and over WSAPI** `GET /remotecopy`, `/remotecopygroups`,
`/remotecopylinks`. Confirmed: WSAPI 1.15 on both arrays serves the remote-copy-group resource; the
`policies` field names, `syncPeriod`, `remoteGroupName`, `role` 1/2, `mode` 1/2, `syncStatus` 3 =
Synced. Corrected: the partnership is matched by address (R2); the pair has **no periodic group** —
the periodic `LastSyncTime` / period output is pinned by the first live async run; `rcopy_async_test`
never existed (the capture holds the CLI and WSAPI "does not exist" responses, useful as fixtures).

**Unit** — one test per R2 check; R3 exists/create/conflict; R4 order and the `no_mirror_config`
start order; R6 verdicts from captured `showrcopy groups` (Synced / Syncing / Stale / Stopped); R7
order and "never the pre-existing objects"; CLI equivalents rendered per call.

**Live (lab pair)** — (1) read and verify the six existing groups without touching them; (2) protect
`zz_rc_test` **async** to E18U31 → *Replicating*, both arrays' `showrcopy groups` agree (the first
periodic group on this pair — its output is captured as a fixture); (3) the same **sync** if the RTT
allows; (4) removal set pasted → nothing `zz_rc_*` on either array, the six existing groups
unchanged. Runner scenario 7 (SPEC-006 §4b) automates (2) and (4).

## 6. Size

Read and parsers (~200), checks (~120), plan (~150), apply (~180), verify (~120), WSAPI client
calls (~60), UI step (~300), ~35 unit tests. **One release (v0.17)** with SPEC-015.
