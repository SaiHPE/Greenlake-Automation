# ADR 0025 — One rule for every write over the array's SSH

**Status:** accepted 2026-11-17 (owner's decision) · **Amends:** ADR 0001 (SSH is read-only) ·
**Generalises:** ADR 0015 (the Remote Copy write client) · **Applies to:** ADR 0015 today; ADR 0016
(snapshot schedules), ADR 0017 and 0018 (iSCSI VLANs, peer ports) and ADR 0024 part B (RCFC ports)
when they are built · **Issue:** BL-58

## Context

Hard rule 2 made the array's SSH read-only (ADR 0001) and then allowed one exception, the Remote Copy
link and target client (ADR 0015). Three later designs each asked for an exception of their own: snapshot
schedules (no WSAPI resource, `GET /schedules` answers 501 on four arrays), iSCSI VLANs (the CLI form is
captured on four OS versions, the WSAPI write is not) and port modes for peer ports and RCFC (no WSAPI
call). The reviews of 2026-11-17 asked for the rule to be decided once, so that hard rule 2 does not
wear down one exception at a time. They also found that today's Remote Copy client checks the *shape*
of a command but not that its port or target is one the approved plan names.

What went wrong before, and what this rule answers: an allowlist of names let an acting option through
(LESSONS 46, BL-46), including the CLI's Tcl quoting and command substitution; a check changed the array
and nothing noticed (LESSONS 44); a write path with no undo for its failure (LESSONS 45, BL-45).

## Decision

A command that changes the array may go over SSH only when **every** condition below holds. A WSAPI
write keeps its own path (plan, approval, apply, removal set) and is not affected.

1. **Exact forms.** Each allowed command is a whole-command pattern, not a name. Every form has a test
   that accepts it and tests that refuse its near-misses. The shared refusals apply: shell characters
   and the Tcl quoting and substitution characters `" ' { } [ ] \` (BL-46). A form that needs a quote
   at a fixed position (the quoted inner command of `createsched`) states so in its pattern, and the
   inner command is checked as an exact form of its own.
2. **Only inside an approved apply.** The write client is built by the apply of a plan the operator
   approved (the plan id the server checks, BL-52). The Console, verify, the as-built and discovery
   never get one; they keep the read client.
3. **Only on the plan's objects.** The client is built with the objects the plan names (ports, targets,
   schedules) and refuses a well-formed command on any other object.
4. **An undo before the write.** Each write has its removal line in the run's removal set, written before
   the command is sent, so a write that half-works is still covered. A form whose effect cannot be
   undone (a snapshot lock, a port change that needs a reboot) is not allowed, unless a later ADR allows
   it by name, with the plan saying so plainly and the operator ticking it as irreversible.
5. **A read-back after the write.** The apply reads the array after each write and stops if the change
   did not take, or left the array worse than it found it (LESSONS 44).
6. **No prompts.** Forms carry `-f` where the CLI asks for confirmation. A form that may still prompt is
   captured live before it is allowed.
7. **One client per kind.** Remote Copy links and targets (ADR 0015), snapshot schedules (ADR 0016) and
   array ports (one client shared by ADRs 0017, 0018 and 0024 part B, built from the (port, form family)
   pairs of the approved plan, so a VLAN apply cannot take a port offline). A new kind needs its own
   ADR naming its forms. A new form in an existing kind needs its tests and a live capture, and the pull
   request says so plainly.

Hard rule 2 in `AGENTS.md` names this rule instead of listing clients.

## Consequences

- `ArrayRcCliClient` meets condition 3 (done on BL-58): the apply builds each array's client with the
  ports, addresses and target the approved plan names on that array (`plan_objects` in
  `application/replication/partnership.py`), and `write()` refuses a well-formed command on any other
  object (*refused: port 0:4:3 is not in the approved plan*), recorded in the command log and never sent.
  A client built without the plan's objects refuses every write. Conditions 1, 2, 4, 5 and 6 it already
  met (SPEC-021).
- The reviews of 2026-11-17 judged the proposals against this rule: ADR 0016 fits once the snapshot lock
  is left out of the first slice and the removal set matches only the tool's own snapshot names (Remote
  Copy makes snapshots of the same volumes); ADR 0017 fits with `-vlan` required on every form (without
  it the port's untagged address changes); ADR 0018 and ADR 0024 part B fit through the one port client,
  after the live captures they list.
- Every new write kind costs an ADR, which is the point: the exceptions stay few and each is argued.
