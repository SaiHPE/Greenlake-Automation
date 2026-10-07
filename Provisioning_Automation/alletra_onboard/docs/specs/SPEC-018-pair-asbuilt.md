# SPEC-018 — As-built for a replicated pair

**Status:** APPROVED 2026-10-07 — not implemented
**Depends on:** SPEC-016 (replication facts), SPEC-017 (failover record), SPEC-002 (provisioned
sections), ADR 0014 (pair)
**Owner:** `application/documents/asbuilt.py`, `asbuilt_parse.py`, `steps.py`

## 1. Problem

The customer design for a two-site deployment is one document; the tool's as-built is one document
per run, i.e. per array. A pair needs one as-built that covers both arrays and the replication
between them, in the same template and with the same rule as today: every array fact read back from
the array, never copied from the plan.

## 2. Requirements

**R1 — One document for the pair.** The As-built step on a paired run generates one docx for the
pair (file name `<A system>_<B system>_asbuilt.docx`). A single-array run is unchanged.

**R2 — Both arrays, same sections.** The existing sections (configuration table, inventory,
checkhealth, hosts and host sets, volumes and volume sets, presentations, zoning designed, provisioning
performed — SPEC-002) appear once per array under *Primary site — <name>* and *DR site — <name>*
headings, each read from its own array with its own run's credential.

**R3 — Replication configured in this run.** A section after both arrays: RCIP ports and addresses per
array; targets and links with status; per group — name, mode, RPO and period, policies, role on each
array, volumes (primary ↔ secondary name, size, sync status, last sync time); the control plane used
(DSCC or CLI) and the commands issued (R9 of SPEC-016); the removal set (A and B blocks).
Pre-existing replication objects are listed under *Replication already present* and marked as not
configured by this run.

**R4 — Failover test.** SPEC-017 R6's section, when the test ran; otherwise *The failover test was not
run in this run*.

**R5 — Read back, not planned.** R3's states come from `showrcopy` read at generation time, like the
provisioned sections read `showvv` / `showvlun`. If one array cannot be read, its sections say so and
the document is still produced with the other.

## 3. Non-goals

HLD/LLD generation (BL-22/23). Customer-specific narrative beyond the existing sheet fields.

## 4. Verification

Unit: a pair as-built from fixture runs contains both site headings, the replication section with the
group facts, the failover table, and still opens/updates fields in Word; a single-array as-built is
byte-for-byte the same structure as today. Live: the lab pair's as-built after SPEC-016/017 runs.

## 5. Size

~250 lines in the generator, ~10 unit tests. Ships with SPEC-017.
