# SPEC-004 — The operator can always find the next thing

**Status:** implemented 2026-09-13 (rc.9) — **pending live confirmation** (S-11, screenshots)
**Findings closed:** X-4, X-6, Z-5, P-5 (+ P-6 text), P-9
**Owner:** frontend (`ui/primitives.tsx`, `ui/StepContext.tsx`, every step), `path_verify.py` for P-9

## 1. Problem

Five things made the operator stop on 2026-09-12/13 and ask where to go or what a wall of text
said: a bare *Continue* on eight steps that names no destination (X-4); notes joined into one
paragraph with " · " (X-6); a Zoning step whose only path to *Continue* hid behind a button called
*Check zoning*, with nothing saying so (Z-5); a Compose card that fell back to *Load objects* after
apply, hiding the composition that had just been used (P-5); a path-verification line that names
fabrics by parity slot when discovery knows the switch names, and reports per host when the card
promised per LUN (P-9).

## 2. Scope

In: the shared Continue affordance, list-shaped notifications, the Zoning step's empty state, the
Compose card's lifecycle, the path-verification sentence and its fields. Out: any change to what a
step does; DS token widths (X-1), a11y attributes (X-3), empty-state copy elsewhere (X-5), the
"what changed" pattern (X-7).

## 3. Requirements

**R1 — Continue names its destination.** `StepContext` carries `nextTitle` (the next wizard step's
label, or none on the last step). A shared `ContinueButton` renders *Continue to <next step>*; on
the last step *Finish*. Every step's plain Continue uses it. Steps whose primary action is not a
plain continue keep their verb (*Create run*, *Mark DSCC complete*, *Continue with N zoned hosts*).

**R2 — Zoning says how to get to Continue.** The left action reads *Check zoning on the array* /
*Re-check zoning on the array*. Before any check has run, the step's gate reads *"Check zoning to
see which hosts can be provisioned"* with the sentence *Continue appears once at least one host is
confirmed zoned on both fabrics; build the zoning plan to read the switches and draft the command
set for the SAN team.*

**R3 — Many notes are a list.** A notification carrying more than one note renders one line per
note (a `NotesList`), never a " · "-joined paragraph. Applied to: Discovery notes, Plan notes, Plan
blockers, Check notes, path-verification notes, As-built warnings, run warnings (GreenLake, Done),
zoning render *Not included* / *Portability*. Single notes render as before.

**R4 — The composition stays in view.** The Compose card loads its objects on mount (no *Load
objects* step); after a successful apply it stays visible, read-only, showing the membership and
exports that were applied. Its intro states the real default: *with no exports composed and exactly
one host set, every volume is presented to that set at an auto LUN; with more than one host set,
exports must be composed* (P-6).

**R5 — Path verification says the numbers the customer asks.** `HostPathStatus` gains `lun_count`,
`paths_per_lun` (the minimum across the host's LUNs) and `fabric_names` (switch logical names from
discovery, in fabric order). The detail reads *3 LUN(s) · 2 HBA(s) · 4 path(s) per LUN · both
fabrics (SAN6700R13U38, SAN6700R13U40)*; when no switch names are known it falls back to the slot
labels. *Partial* names the missing fabric by switch name when known. The card's description says
what it reports: per host — LUNs, HBAs, paths per LUN, fabrics.

**R6 — Nothing else moves.** No step changes what it does, what it gates on, or what it emits.

## 4. Acceptance

Python (`tests/unit/test_path_verify_detail.py`): `test_detail_counts_luns_hbas_and_paths_per_lun`,
`test_detail_uses_switch_names_when_discovery_has_them`, `test_detail_falls_back_to_slot_labels`,
`test_partial_names_the_missing_fabric_by_switch`. Existing path-verification tests unchanged.

Frontend: `tsc --noEmit` + build. **S-11 (live, screenshots):** any step's footer (Continue names the
next step); Zoning before any check (the gate sentence); Discovery notes as a list; Provision after
apply (composition still visible, read-only); path verification detail with switch names.
