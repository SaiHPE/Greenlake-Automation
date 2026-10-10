# SPEC-018 — As-built: replication and failover sections

**Status:** APPROVED 2026-10-07; **re-cut the same day** — sections in the existing one-array
document, not a pair document (ADR 0014 deferred). **R1, R3, R4 built 2026-10-10** in
`asbuilt.py` (`_add_replication_section`, `_add_failover_section`) and `documents/steps.py`
(both arrays read again with `replication.read.read_array` when the document is made; the plan,
report and result come from the run's `replication.*` events). R2 is the one sentence until
SPEC-017 fills it. 8 unit tests in `test_asbuilt_replication.py`, built on the live captures of
2026-10-09 (sync) and 2026-10-10 (periodic through the UI). **Not yet seen live:** the as-built
itself generated on the lab pair after a replication run.
**Depends on:** SPEC-016 R8 (replication facts), SPEC-017 R6 (failover record), SPEC-002 (the
provisioned sections this follows)
**Owner:** `application/documents/asbuilt.py`, `asbuilt_parse.py`

## 1. Problem

The as-built documents what this run did to this array. When the run also replicated, the document
has to say to where, what, how (mode, RPO), what state it was left in, and — when the failover test
ran — that the DR copy took over and came back. Same rule as every other section: read back from the
arrays at generation time, never copied from the plan.

## 2. Requirements

**R1 — Replication section** after *Provisioning performed*, present only when the run has a
Replication tab:
- *Partner array*: name, serial, OS (from the peer's `showsys`/`showversion`); the partnership as
  read — targets on both sides, links with status, RCIP ports and addresses per array.
- *Groups configured by this run*: per group — name, mode, RPO and period, policies, role on each
  array, volumes (primary ↔ secondary name, size, sync status, last sync time), the peer volume set.
- *Replication already present*: groups the run did not create, listed and marked as not configured
  by this run.
- The calls made with their CLI equivalents, and the removal set as **A** and **B** blocks (SPEC-016
  R7), under *To remove what this run created* like the provisioning lines.

**R2 — Failover test section** (SPEC-017 R6) when the test ran; otherwise one sentence: *The failover
test was not run in this run.*

**R3 — Read back.** R1's states come from `showrcopy` on both arrays at generation time. If the peer
cannot be read, the section says so for the peer's columns and the document is still produced.

**R4 — Unchanged otherwise.** A run without a Replication tab produces exactly today's document.

## 3. Non-goals

A two-site document (returns with ADR 0014 if it is ever taken up). HLD/LLD (BL-22/23).

## 4. Verification

Unit: a fixture run with replication facts renders both sections with the group facts and the two
removal blocks; a fixture run without the tab is byte-for-byte today's structure; the document still
opens and updates fields in Word. Live: the lab pair's as-built after the SPEC-016 and SPEC-017 runs.

## 5. Size

~150 lines in the generator, ~6 unit tests. Replication section ships in v0.17 with SPEC-016; the
failover section in v0.18 with SPEC-017.
