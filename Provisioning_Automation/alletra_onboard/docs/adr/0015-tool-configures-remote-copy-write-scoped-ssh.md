# ADR 0015 — Remote Copy is configured by the tool, over a second, write-scoped SSH client

**Status:** accepted 2026-10-07 (operator decision); **sequenced the same day** — § *Sequencing* ·
**Amends:** ADR 0001 (SSH is read-only) from the release that ships links and targets ·
**Keeps:** ADR 0012 (no switch writes) · **Specs:** SPEC-016, SPEC-017

## Sequencing (2026-10-07)

The `hpe3parclient` the tool already provisions with exposes the Remote Copy **group** lifecycle and
the **disaster-recovery actions** as WSAPI REST calls on `/remotecopygroups` (create, admit volume,
start, stop, remove, recover-from-disaster actions 6–11). Only links, targets and `startrcopy` run
over SSH underneath. So:

| Release | What the tool configures | Write plane | Live proof |
|---|---|---|---|
| v0.17 | Layer 3 — groups, period, policies, admitted volumes, start (SPEC-016) | **WSAPI** (existing plan → approve → apply → removal machinery) | lab pair, already partnered |
| v0.18 | Failover test — failover, recover, restore (SPEC-017) | **WSAPI** DR actions | lab pair |
| v0.19 | Layers 1–2 — RCIP addressing, targets, links, `startrcopy` | the write-scoped SSH client below | needs a pair that can be partnered from scratch |

ADR 0001 is untouched until v0.19. The decision — the tool configures all three layers itself — is
unchanged; the order follows what the lab can prove.

## Context

Replication on a B10000 has three layers (research 2026-09-19 §2): the **transport** (RCIP ports
addressed on both arrays), the **partnership** (each array declares the other as a Remote Copy
target over ≥ 2 links) and the **protection** (a Remote Copy group over a volume set, started).

- Layer 3 has a REST control plane the tool already uses: WSAPI's `/remotecopygroups` (create,
  admit, start, stop, remove, DR actions) through the `hpe3parclient` provisioning writes with. The
  DSCC Block Storage API's `protection-policies` (research 2026-10-07 §5.1) is a second REST path,
  not taken (§4).
- Layers 1–2 have **none**. `controlport rcip addr/gw`, `creatercopytarget`, `admitrcopylink` exist
  only as CLI commands over SSH; the DSCC API's `replication-partners` is GET-only, and the
  `hpe3parclient` functions for links run SSH underneath.

ADR 0001 made the tool's SSH client read-only — a fixed allowlist of `show*` commands plus
`checkhealth`, and shell metacharacters refused — and every read since (verify, as-built, discovery,
path verification) has stood on that. ADR 0012 made the tool never write to a SAN switch: it emits a
command set the SAN team pastes.

The September research proposed treating layers 1–2 like switches: a two-sided command set, never
written. The operator rejected that on 2026-10-07 with a reason that holds: **the switch rule exists
because switches are heterogeneous** — vendors, firmware trains, command dialects, and fabrics the
tool has never seen — and a pasted command set keeps the tool out of situations it cannot predict.
Both ends of a replication link are Alletra MP B10000 arrays the tool already reads and (through
WSAPI) already writes, with one CLI dialect documented in one HPE guide (ED8, Aug 2026). The reason
for the command set does not apply.

## Decision

**The tool configures all three layers itself. Layer 3 and the DR actions go over WSAPI; layers 1–2
go through a second SSH client that may run only the Remote Copy link and target commands. Both
inside the same plan → review → approve → apply → removal flow provisioning uses. ADR 0001's
read-only client is unchanged and stays the default.**

1. **Two clients, not one relaxed one.** `ArrayCliClient` (ADR 0001) keeps its read allowlist and is
   what every read uses. A new `ArrayRcCliClient` (v0.19) carries its own allowlist — exactly the
   layer 1–2 commands that have no REST equivalent: `startrcopy`, `controlport rcip addr`,
   `controlport rcip gw`, `controlport rcip ping`, `creatercopytarget`, `admitrcopylink`,
   `dismissrcopylink`, `removercopytarget` — and the same metacharacter refusal. Sub-command shape is
   checked, not just the first word: `controlport` is allowed only with `rcip addr|gw|ping`, never
   `offline` or `config`. Group and DR commands are **not** on it: they go over WSAPI (§4).
2. **Never without a plan.** The write client is constructed only inside `apply` of a plan the
   operator approved in the UI (SPEC-016 §R5), the same gate as `POST /storage/apply`. No API route
   runs a Remote Copy write directly.
3. **Every write has its undo.** Each write the apply issues appends its inverse to the run's
   removal set (SPEC-007 pattern): links → `dismissrcopylink`, target → `removercopytarget`, group
   → `stoprcopygroup` + `dismissrcopyvv -removevv` + `removercopygroup`. Objects that already
   existed are never in it.
4. **Groups and DR actions go over WSAPI.** Layer 3 (`creatercopygroup`, `setrcopygroup pol|period`,
   `admitrcopyvv`, `startrcopygroup`, `stoprcopygroup`) and the DR operations (`failover`, `recover`,
   `restore`) have REST equivalents on `/remotecopygroups`, the write plane provisioning already uses
   with its live-verified plan/approve/apply/removal flow. The CLI equivalent of every call is
   **printed** in the plan and the as-built so the operator sees what was done on the array. The DSCC
   protection-policy API is not used: its one advantage (a snapshot schedule in the same call) left
   with BL-21.
5. **Reads stay reads.** Verification of what the apply did (`showrcopy`, `showrctransport -rcip`,
   `showport -rcip`) uses the read-only client, exactly as path verification does after provisioning.
6. **Switches are still never written.** ADR 0012 is unaffected: RCFC (Remote Copy over FC) zoning,
   if a customer wants it, is a command set for the SAN team like any other zone. v0.17 scope is
   RCIP.

## Consequences

- ADR 0001's statement "the SSH client is read-only" becomes, from v0.19, "the *read* client is
  read-only; one write-scoped client exists for Remote Copy links and targets and is reachable only
  through an approved plan". `docs/ARCHITECTURE.md` and the project instructions change then.
- The blast radius of a wrong apply is the two arrays' Remote Copy configuration — not hosts, not
  volumes, not exports. The removal set bounds it to what the run created.
- The runner's replication scenario (SPEC-006 §4b) writes real groups on the lab pair
  (D22U27 ↔ E18U31) and removes them; the pair already replicates, so the tool's objects are
  `zz_rc_*` and the existing group is never touched.
- `controlport rcip ping` is in the write client although it changes nothing: it is not `show*`,
  and keeping the read client's definition exact matters more than one classification.
- Not decided here: RCFC links (FC transport). Out of scope until RCIP is live.
- The v0.19 "create partnership" path cannot be proven on the lab pair without dismantling its
  partnership; it waits for a pair that can be partnered from scratch, or the operator's decision to
  rebuild the lab one.
- Learned live 2026-10-09 (`tests/fixtures/rc_pair/second_target/`): a link — local port plus peer
  address — belongs to exactly one target (*"Link 0:4:3:10.54.154.192 appears to exist on another
  target."*). The v0.19 "second target for the other mode" therefore needs spare RCIP ports with
  addresses on at least one side; the tool must say so from `showport -rcip` before it plans one,
  and must recognise that sentence as the array's refusal.
