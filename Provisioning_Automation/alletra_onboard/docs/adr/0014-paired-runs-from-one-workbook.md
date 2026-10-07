# ADR 0014 — Two arrays from one workbook: paired runs

**Status:** accepted 2026-10-07 (operator decision) · **Research:**
[2026-09-19-replication-two-arrays.md](../research/2026-09-19-replication-two-arrays.md) §6,
[2026-10-07-replication-document-review.md](../research/2026-10-07-replication-document-review.md) ·
**Specs:** SPEC-015 (workbook + pairing), SPEC-016 (Replicate step), SPEC-017 (failover test),
SPEC-018 (pair as-built)

## Context

Replication is a relationship between two arrays. Everything the tool does today assumes one: one
workbook names one array (it refuses two), one run holds one array credential (ADR 0013), one
discovery, one zoning check, one provisioning plan, one as-built. All of it is live-verified and
covered by the session runner; rewriting it to carry an array index would put a proven track at risk
for a feature that only the last step needs.

The field engineer's expectation is unchanged by that: **one workbook** for the engagement, both
arrays in it, the replication design in it, one as-built out. The customer design we have seen (an
HLD for a two-site async deployment) is one document for one primary and one DR array.

Three models were compared in the September research: one run holding two arrays (every step
re-plumbed), two unrelated runs linked afterwards (two workbooks, two as-builts), or one workbook
that mints two **paired** runs.

## Decision

**One workbook may name two arrays. Uploading it creates two runs, paired. Each run is still one
array with one credential; the pair is metadata on top.**

1. **The workbook.** The *Initialisation* and *Provisioning* tabs gain an **Array B** column set
   next to today's fields. Blank Array B = a single-array workbook, parsed exactly as today. A new
   **Replication** tab describes what is replicated between A and B (SPEC-015).
2. **Two runs, one pair.** `POST /runs/from-sheet` on a two-array workbook creates run A
   (`role: primary`) and run B (`role: secondary`) atomically, sharing a `pair_id`. Each run holds
   its own array's credential, discovery, zoning report, plan, result and as-built, as today. The
   per-array steps (init, discover, zoning, provision, verify) **do not change**.
3. **Pair-level steps** (`replicate`, `failover_test`) belong to the pair: they are recorded on run
   A and resolve run B through `pair_id`. They read both arrays with both runs' credentials.
4. **The UI shows one pair.** A pair header with an **A / B switch** above the per-array steps;
   the switch changes which run the step pages read. *Open another run* lists a pair as one entry.
   The step list comes from the step registry as today, with the pair-level steps appended when the
   run has a pair.
5. **Modes.** A new preset **Replicate** (discover → zoning → provision → **replicate** →
   **failover_test** → verify → asbuilt, on both arrays) joins the registry; *Custom* can pick the
   pair-level steps when the run has a pair. Pair-level steps are refused on a run without a pair.

## Consequences

- The provisioning track, its data model and ADR 0013 are untouched. Pairing is additive: a run
  with no `pair_id` behaves exactly as v0.16.
- Two credentials exist in the pair, one per run — not "one credential per run" bent into "two per
  run". The Replicate step takes both runs' credentials from their runs; it never asks.
- Discovery, zoning and provisioning run per array, so a pair run costs two of each. The operator
  switches A / B; nothing runs on B behind the operator's back except the pair-level steps, which
  say so.
- Folding paired runs into one record later (if the UI ever needs a true two-array view) stays
  possible: nothing here prevents it, and the pair id is the join key.
- The session runner gains a pair scenario; every single-array scenario is unchanged and keeps
  guarding that promise.

## Rejected

- *One run holding two arrays* — 4–5 releases of rewrite across live-verified steps, and an A/B
  switch inside every step page.
- *Two unrelated runs* — two workbooks and two as-builts for one engagement; the field engineer's
  "one sheet" expectation is the whole point.
