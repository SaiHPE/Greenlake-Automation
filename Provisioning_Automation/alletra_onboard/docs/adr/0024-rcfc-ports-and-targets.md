# ADR 0024 — Remote Copy over Fibre Channel: which writes the tool takes on

**Status:** part A accepted 2026-11-17 (owner's decision); part B deferred · **Spec:**
[SPEC-031](../specs/SPEC-031-rcfc.md) · **Tracker:** BL-50 · **Research:**
[2026-11-17-rcfc.md](../research/2026-11-17-rcfc.md) · **Fixed apart:** BL-57 (issue #33), SPEC-031 R5 ·
**Part B, if re-opened, follows:** [ADR 0025](0025-one-rule-for-ssh-writes.md) (one rule for every SSH
write) and shares the array-port client with ADR 0018 (peer ports, accepted 2026-11-17 with its port-mode write deferred) ·
**Keeps:** [ADR 0012](0012-no-switch-writes-the-tool-emits-a-command-set.md) (no switch writes), ADR 0001
(reads stay read-only), [ADR 0015](0015-tool-configures-remote-copy-write-scoped-ssh.md) unchanged while
part B is deferred

## Decision (2026-11-17)

The owner took the review's recommendation: part A now; part B later, if at all.

### Part A — accepted

The Replication step works on an RCFC partnership that already exists (SPEC-031 R1–R4, R6–R8). It adds
no write, no allowlist entry and no port-mode change. The work left:

1. **Find an existing FC partnership by WWN.** `find_partnership` matches targets by RCIP address only,
   and `parse_showport_roles` drops each FC port's WWN (it keeps one node WWN, the first FC row's).
2. **FC latency limit 10 ms, sync and async.** `RTT_LIMIT_MS` becomes a table per transport; today an
   async FC row passes at up to 200 ms.
3. **FC is not RCIP.** The link-check gate (`_gate_on_link` in `steps.py`) and the page's flag
   (`const rcip = !!report?.partnership` in `ReplicationStep.tsx`) treat every partnership as RCIP; they
   follow the partnership's transport instead.
4. **Stop sending an FC pair to the Replication network tab.** Today's "no partnership" finding tells
   the engineer to name RCIP ports on that tab, and adds *"this tool supports Remote Copy over IP only"*.

Not part A's any more: the live risk the review found in `stale_fc_targets`. It printed
`removercopytarget -cleargroups -f` for any FC target to the peer, a working one included, which would
delete the target and its groups. BL-57 (branch `feat/bl-57-fc-target-guard`, issue #33) fixes it: the
command is printed only for a failed target with no link Up and no started group; any other FC target
to the peer blocks with a sentence and no command. SPEC-031 R5 records it as done by BL-57.

Part A stays *built, pending live run* until the lab has a working RCFC pair (research §4).

### Part B — deferred

The tool does not set RCFC up. Option B below stays the design to start from; nothing of it is built,
and no form is added to any allowlist. Why:

- **Nothing can be proven in the lab.** No RCFC path is cabled. The logins on rack13's 0:3:4 and 1:3:3
  are an ESXi HBA, not the Primera; no Primera WWN is on any rack13 port; no rack13 FC port is in RCFC
  mode (research §4).
- **The command order is unknown.** The array's help gives the commands, not the order of
  `controlport rcfc init`, the zones and `creatercopytarget`.
- **Option C was judged against an outdated DSCC API** (the v1alpha1 mirror of 2026-06-07). It is
  re-done below against the live v1 API, and it is a real candidate now.
- **Nobody knows how much it would be used.** No public HPE figure for RCFC against RCIP was found. Get
  field input first (how many deployments replicate over FC, and whether their owners would let a tool
  change port modes) before spending ~550 lines (SPEC-031 §7) and a lab rebuild on part B.

Part B is re-opened only by the owner, after every item in *Before part B* below.

## Context

ADR 0015 decided that the tool configures Remote Copy layers 1–2 itself over a write-scoped SSH client,
because both ends are B10000 arrays with one CLI dialect. It scoped that client to RCIP and said
*"Not decided here: RCFC links (FC transport). Out of scope until RCIP is live."* RCIP went live on
2026-11-06 (BL-41).

RCFC needs three kinds of change, and they are not alike (research §2–§3, every form from the array's
own help):

1. **The port's connection mode.** An FC port becomes an RCFC port with `controlport config rcfc -ct
   point -f <nsp>`, and *"Controlport config mode changes are not allowed when ports are online"*, so
   `controlport offline <nsp>` comes first and possibly `controlport rst <nsp>` after. This changes a
   port's role. ADR 0015 §1 kept `controlport` to `rcip addr|gw|ping`, *"never `offline` or `config`"*,
   and SPEC-021 says *"The tool never changes a port's role."* A host port taken by mistake loses its
   hosts' paths. The peer-port work (BL-26, ADR 0018) faces the same three commands with `peer` in place
   of `rcfc`; RCFC and peer ports compete for the same free FC ports.
2. **The zones** between the two arrays' RCFC ports. A switch write; ADR 0012 already answers it: a
   command set for the SAN team.
3. **The Remote Copy objects**: `controlport rcfc init -f <nsp>`, `startrcopy`, `creatercopytarget
   <name> FC <node_WWN> <nsp>:<WWN>…`, and `admitrcopylink` / `dismissrcopylink` in their `N:S:P:WWN`
   form. Exactly the kind of command ADR 0015 put on `ArrayRcCliClient`, in the FC form.

The zones sit between 1 and 3: the target cannot see its peer until the SAN team has pasted them. So
the apply cannot run start to finish in one click; it waits for a person outside the tool.

Two facts from 2026-11-17 bear on the choice:

- The DSCC **storage-fleet** API has an FC port call and a `replication-partners` POST with an FC target
  type (research §8 read the v1alpha1 mirror; option C re-reads the live v1). ADR 0015 said DSCC had no
  layer 1–2 call; it had read only the block-storage API. Nothing was probed, and the tool has no DSCC
  write client.
- The lab has no working RCFC pair today (research §4). The first live run of any option needs the lab
  team to put two ports of each array on one fabric with zones, and the owner to say which rack13
  ports may change mode.

## Options

**A. Command set only.** The plan prints the port-mode lines, the Remote Copy lines (A and B blocks)
and the zoning command set; the engineer pastes them; the tool reads both arrays again and verifies,
then plans the groups as in part A. No new write path. It is what the owner turned down for RCIP on
2026-10-07, for a reason that holds here for item 3.

**B. The tool writes items 1 and 3, the SAN team item 2.** The design part B starts from, now under
ADR 0025's rule.

- Item 3 on `ArrayRcCliClient`, four new forms. Each is an exact whole-command form (ADR 0025 condition
  1), and the client refuses it on any port or WWN the approved plan does not name (condition 3, which
  that client meets since BL-58).

  | Form | Shape the client accepts |
  |---|---|
  | `controlport rcfc init -f <nsp>` | one port |
  | `creatercopytarget <name> FC <node WWN> <nsp>:<port WWN> …` | 16 hex digits per WWN, at least two links |
  | `admitrcopylink <name> <nsp>:<port WWN> …` | as above |
  | `dismissrcopylink <name> <nsp>:<port WWN> …` | as above |

  `controlport rcfc delete` is **not** on it: it is a removal-set line the operator pastes (SPEC-007).
- Item 1 on **the one array-port client** that ADR 0025 condition 7 shares between ADRs 0017, 0018 and
  this one: `controlport offline <nsp>`, `controlport config <mode> -ct point -f <nsp>` with `<mode>`
  limited to `peer` or `rcfc`, and `controlport rst <nsp>` only if the live run shows it is needed.
  Never `-sysreboot` (condition 4: a change that needs a reboot is not allowed). The way back to the
  old mode is a removal-set line, not a client form.
- One free-port rule and one array-to-array zone block, shared with SPEC-025 (peer ports). A port is
  offered only when it is FC, Type `free`, with no login in `showhost -d`, no export in `showvlun -a`,
  `Mode_change` `allowed` in `showport -c`, and linked. A port named by both the RCFC tab and the
  peer-port tab is refused.
- Item 2 stays a command set (ADR 0012).
- The apply runs in two phases. Phase 1: port modes, read back. Then the step stops and shows the
  zoning command set. Phase 2 starts only when a fresh read shows each RCFC port seeing its planned
  partner (the partner's port WWN in `showportdev ns <nsp>`, or the partner's node WWN in `showport -c`):
  `controlport rcfc init`, `startrcopy`, a target each way, links Up. Each phase has its own approval.

**C. DSCC storage-fleet API v1, for items 1 and 3.** Re-read on 2026-11-17 on
developer.greenlake.hpe.com (storage-fleet-latest, v1); research §8 had read the v1alpha1 mirror of
2026-06-07. Nothing was probed.

| Call | What it does |
|---|---|
| `POST /storage-fleet/v1/devtype4-storage-systems/{id}/replication-partners` | creates a replication partner: type `2` is FC, with `nodeWwn` and `replicationPartnerSystemId`; answers 202 and a task to poll |
| `PUT /storage-fleet/v1/devtype4-storage-systems/{id}/ports/{id}/fc` | an FC port's settings (item 1). The v1 page did not show the `configMode` values; v1alpha1 listed `RCFC`. To confirm. |
| `PUT /storage-fleet/v1/devtype4-storage-systems/{id}/ports/{id}/edit-rcip` | an RCIP port's settings |

For: one REST plane with tasks to poll, no new SSH write kind, no CLI prompt to handle. The tool
onboards both arrays into DSCC anyway, so the partner has a DSCC system id by the time the Replication
step runs. `edit-rcip` also undercuts ADR 0015's statement that DSCC had no RCIP setup call.
Against: the tool has no DSCC client with write scope, and the workspace roles a write needs are
unconfirmed; whether a partner that is not a B10000 (the lab's Primera) is accepted is not shown; DSCC
does not zone either, so the wait for the SAN team stays. Weighed against B when part B is re-opened,
after a read-only v1 GET of both arrays' ports and replication partners.

**D. Never set RCFC up.** Part A only: RCFC partnerships are made by hand and the tool uses them. Where
things stand while part B is deferred.

## Before part B (all of these, then the owner decides B or C)

1. The order of `controlport rcfc init`, the zones and `creatercopytarget` (CLI guide ED8, which the
   owner holds).
2. Whether `controlport config rcfc -ct point -f` brings the port back by itself, or `controlport rst`
   is needed.
3. Whether `-f` still prompts (the `TPDFORCE_OVERRIDE` question; ADR 0025 condition 6).
4. Whether the port WWN changes when the port becomes RCFC.
5. Captures: `help checkrclink` and whether it measures an FC link; `showport -rcfc`;
   `showrctransport -rcfc`; `showport -par` on an RCFC port (the value phase 1 reads back).
6. The lab: rack13's free ports 0:3:3 and 1:3:4; the Primera's RCFC ports on the same fabric, with
   zones; the owner's agreement to change those ports' mode.
7. DSCC, for option C: a read-only v1 GET of the ports and the replication partners of both arrays,
   and the workspace roles a write would need.
8. Field input on how much RCFC is used (*Part B — deferred*).

## Hard rules part B keeps

- **Rule 1, no switch writes: kept.** The zones are a command set for the SAN team in every option.
- **Rule 2, array SSH: follows ADR 0025.** Every form exact, built only inside an approved apply, bound
  to the plan's ports and WWNs, its removal line written before the write, read back after, no prompt.
  The port-mode change goes through the one array-port client shared with ADR 0018, mode `peer` or
  `rcfc` only. One free-port rule and one array-to-array zone block, shared with SPEC-025. A port named
  by both tabs is refused.
- **Rule 7, done means live:** part B stays *built, pending live run* until a lab pair exists, whatever
  the unit tests say.

## Risks

- **The wrong port taken offline drops host paths.** `controlport offline` on a port that serves a host
  cuts that host's paths at once. Guard: the free-port rule read fresh at plan time, and the client
  bound to the plan's ports.
- **A WWN change makes the zones wrong.** If a port takes a new WWN in RCFC mode (peer ports do), zones
  built from the old one never match. The command set is built from the WWNs read after phase 1.
- **The two-phase apply waits half done.** After phase 1 the ports are in RCFC mode and nothing else
  exists; the run may wait days for the SAN team, or never come back. The removal set must be complete
  and valid after phase 1 alone, and tested for a stop there and at each write (LESSONS 45).
- **The latency is the engineer's word.** For FC the round-trip time is typed, not measured, until
  `checkrclink` is known to work on FC. A link stretched over FCIP routers looks like RCFC to the array,
  so the tool cannot detect FCIP or its 120 ms async limit; it applies RCFC's 10 ms (SPEC-031 open
  question 4). This one holds for part A too.

## Consequences

- Part A changes no write path: ADR 0015, hard rule 2 and every allowlist stay as they are. Its pull
  request says *built, pending live run* and keeps the `needs live run` label.
- ADR 0015's *Context* says DSCC has no layer 1–2 call. The v1 `replication-partners` POST and
  `edit-rcip` PUT say otherwise; ADR 0015 carries a note. Its decision (RCIP over SSH) stands.
- If part B is re-opened with option B: `ArrayRcCliClient` gains the four FC forms and the array-port
  client gains the `rcfc` mode beside `peer`, each with tests pinned to the captured help and the first
  live answers (ADR 0025 condition 7), and the pull request says plainly that it adds them. With option
  C: a DSCC write client, which the tool does not have, under a decision of its own.
- The blast radius of a wrong part B apply is two FC ports per array and the Remote Copy objects
  between the two arrays. The removal set restores each port to the connection mode `showport -par`
  read before the apply (SPEC-031 R13).
