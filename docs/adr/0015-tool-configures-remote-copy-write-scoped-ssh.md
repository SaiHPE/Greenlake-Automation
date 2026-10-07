# ADR 0015 — Remote Copy is configured by the tool, over a second, write-scoped SSH client

**Status:** accepted 2026-10-07 (operator decision) · **Amends:** ADR 0001 (SSH is read-only) ·
**Keeps:** ADR 0012 (no switch writes) · **Specs:** SPEC-016, SPEC-017

## Context

Replication on a B10000 has three layers (research 2026-09-19 §2): the **transport** (RCIP ports
addressed on both arrays), the **partnership** (each array declares the other as a Remote Copy
target over ≥ 2 links) and the **protection** (a Remote Copy group over a volume set, started).

- Layer 3 has a REST control plane: the DSCC Block Storage API's `protection-policies` on an
  application set (research 2026-10-07 §5.1), and WSAPI's remote-copy-group calls as a fallback.
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

**The tool configures all three layers itself. Layers 1–2 go through a second SSH client that may
run only the Remote Copy write commands, inside the same plan → review → approve → apply → removal
flow provisioning uses. ADR 0001's read-only client is unchanged and stays the default.**

1. **Two clients, not one relaxed one.** `ArrayCliClient` (ADR 0001) keeps its read allowlist and is
   what every read uses. A new `ArrayRcCliClient` carries its own allowlist — exactly:
   `startrcopy`, `controlport rcip addr`, `controlport rcip gw`, `controlport rcip ping`,
   `creatercopytarget`, `admitrcopylink`, `dismissrcopylink`, `removercopytarget`,
   `creatercopygroup`, `setrcopygroup pol`, `setrcopygroup period`, `admitrcopyvv`,
   `startrcopygroup`, `stoprcopygroup`, `dismissrcopyvv`, `removercopygroup`, `syncrcopy`,
   `setrcopygroup switchover|failover|recover|restore|reverse` (SPEC-017 only) — and the same
   metacharacter refusal. Sub-command shape is checked, not just the first word: `controlport` is
   allowed only with `rcip addr|gw|ping`, never `offline` or `config`.
2. **Never without a plan.** The write client is constructed only inside `apply` of a plan the
   operator approved in the UI (SPEC-016 §R6), the same gate as `POST /storage/apply`. No API route
   runs a Remote Copy write directly.
3. **Every write has its undo.** Each command the apply issues appends its inverse to the run's
   removal set (SPEC-007 pattern): links → `dismissrcopylink`, target → `removercopytarget`, group
   → `stoprcopygroup` + `dismissrcopyvv -removevv` + `removercopygroup`. Objects that already
   existed are never in it.
4. **Prefer the REST path where one exists.** Layer 3 is created through the DSCC protection-policy
   API when the sheet carries GreenLake API credentials and both arrays are found in DSCC; otherwise
   through the CLI on the write-scoped client. Either way the equivalent CLI commands are **printed**
   in the plan and the as-built, so the operator can see what was done on the array.
5. **Reads stay reads.** Verification of what the apply did (`showrcopy`, `showrctransport -rcip`,
   `showport -rcip`) uses the read-only client, exactly as path verification does after provisioning.
6. **Switches are still never written.** ADR 0012 is unaffected: RCFC (Remote Copy over FC) zoning,
   if a customer wants it, is a command set for the SAN team like any other zone. v0.17 scope is
   RCIP.

## Consequences

- ADR 0001's statement "the SSH client is read-only" becomes "the *read* client is read-only; one
  write-scoped client exists for Remote Copy and is reachable only through an approved plan".
  `docs/ARCHITECTURE.md` and the project instructions change accordingly.
- The blast radius of a wrong apply is the two arrays' Remote Copy configuration — not hosts, not
  volumes, not exports (those stay on WSAPI with their own plan). The removal set bounds it to what
  the run created.
- The runner's pair scenario (SPEC-006 addendum) writes real links and groups on the lab pair
  (D22U27 ↔ E18U31) and removes them; the pair already replicates, so the tool's objects are
  `zz_rc_*` and the existing group is never touched.
- `controlport rcip ping` is in the write client although it changes nothing: it is not `show*`,
  and keeping the read client's definition exact matters more than one classification.
- Not decided here: RCFC links (FC transport). Out of scope until RCIP is live.
