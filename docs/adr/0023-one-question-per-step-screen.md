# Each step screen asks one question; everything else is one click away

**Status:** accepted 2026-11-17 (owner's decision), with the changes below (proposed 2026-11-16)
· **Tracker:** BL-59, *UI round 2: one question per screen* · **Spec:** [SPEC-030](../specs/SPEC-030-calmer-step-screens.md)
· **Work packet:** [`workpackets/BL-59.md`](../workpackets/BL-59.md)
· **Builds on:** BL-43's October redesign (draft 3, built 2026-10-14, closed 2026-11-17),
[ADR 0005](0005-decouple-onboarding-into-modes.md) (the step registry),
[ADR 0011](0011-bounded-context-refactor-decoupled-ux.md) (frozen API contract, no frontend test suite),
[`UX-GUIDELINES.md`](../UX-GUIDELINES.md) (the Design System rules and our calls)

## Context

BL-43's draft-3 redesign (built 2026-10-14, live on labrat 24/0 and 18/0, its replication screens
live 2026-11-05 in BL-41's runs) gave every step the Design System wizard frame. BL-43 is closed;
this round is a new item, BL-59. Since the redesign, the partnership plan (BL-41), the link check
(BL-42), iSCSI hosts (BL-44) and the console (SPEC-019) each added panels, notices and buttons to
existing screens. The audit in SPEC-030 §2 finds, on the busiest steps: up to six notices at once,
two primary buttons on one page, disabled buttons, the same action in the footer and in a panel
header, the step's state said in four places, and an estimated 70 to 120 px of real content above
the fold at 1366 x 768 once the header bands, the footer with its tick and the console bar are drawn.

The operator's complaint in October was not a missing feature. It was that a screen asked several
things at once and the answer to the current one was below the fold.

## Decision

1. **One question per screen, per state.** A step's state decides the one question on screen. The
   status line asks or answers it; the footer's one primary acts on it; the current part is the
   only open panel. Everything else (finished parts, inventories, commands, explanations, logs) is
   behind *Show*, never deleted.
2. **Parts, not pages.** A long step (Provision storage, Replication, SAN zoning) keeps its single
   registry entry. Its parts show as a parts bar; finished parts collapse to one row each with
   *Show detail* and their own "again" button; later parts are not drawn.
3. **One status signal per place.** The step header shows the state word only; counts and detail
   go in the one status line; other notices become folded notes. In the wizard the app header
   stops repeating the mode (the wizard bar carries it); it keeps the serial and the run state.
4. **The log is a panel, not a band that eats the step.** Activity and Console stay one slim bar
   with the same two buttons; opening either opens one panel with two tabs, at most 40% of the
   window high (a *Taller* / *Shorter* button changes that), and the step footer stays on screen.

## Changes on acceptance (2026-11-17)

The owner accepted the decision with these answers to SPEC-030 §7 and these changes. SPEC-030 and
the work packet carry them.

**Answers.**
- **Q1, the app header in the wizard:** drop the mode only. Keep the serial (it says which array is
  written to) and the run state.
- **Q2, skip buttons:** keep *Continue to X without Y* (SPEC-012 R2: the label says what continuing
  means). Shorten the endings only: *without replication*, not *without configuring replication*.
- **Q3, Generate command set:** stays in the page as a secondary button that is never disabled
  (slice P8a). Moving it to the footer (slice P8b) is dropped.
- **Q4, No path:** amber, not red. `path_verify.py` treats a host with no path as fine until it is
  on and zoned, and the report never blocks; red reads as "the tool failed".
- **Q5, the log panel's height:** cap it at 40% now, plus a *Taller* / *Shorter* button, not a drag
  handle. The console's terminal is 220 px high today; under a 40% cap at 768 high it gets about
  150 px, hence the button.

**Changes.**
1. **A failed apply on Provision storage** (BL-45) is its own state: *Create* stays the open part
   with the removal set showing, *Rebuild plan* stays the footer primary, and the section title
   *Undo what this run created* stays word for word.
2. **The page text the lab scripts read is frozen too**, not only the labels they press: *What the
   array answered*, *N created*, *Verify the paths next*, *Creation reported an error*, *Removal
   command set*, *Tick the box first*, the *Read-only command* field and the others SPEC-030 R10
   lists. A closed section renders nothing, so text folded away fails those checks.
   `lab/failed_apply_lab.py` joins `ui_live_lab.py` and `ui_provision_lab.py` on the list
   (`ui-smoke/` is local and git-ignored, so it is not).
3. **A test guards that text.** A pytest, run by `scripts/check.py`, finds in `frontend/src` every
   literal the lab scripts press or read, and fails naming the one that went. ADR 0011 said to
   revisit UI tests if the frontend changed a lot again; this is the small answer, a text check,
   not a frontend test suite.
4. **Discovery** opens a hosts section by itself also when a host in it has a multipath warning
   (BL-36).
5. **Result words:** when *Exists* becomes *Already there*, every sentence that names it changes
   too (*will show as Already there*). Replication keeps its link wording (*within the limit*,
   *over the limit for ...*, with the latency in ms).
6. **Slice S0 comes first:** before-screenshots at 1366 x 768 and 1080 x 720 of the Provision
   storage plan, a failed apply, the Replication plan and SAN zoning with work left, with the
   content above the fold measured. The first build slice is S5a: the log panel's cap only.

## Alternatives considered

- **Split the long steps into more registry steps** (for example *Replication network* and
  *Replication groups*). Rejected: it changes the registry, the phases and the API (ADR 0005,
  ADR 0011's frozen contract) to fix a presentation problem, and the rail would grow to 14 rows.
- **Tabs inside a step** (Plan · Result · Verify). Rejected: tabs hide where the operator is in an
  ordered flow, and the Design System reserves them for peer views, not sequence.
- **Leave the screens and shorten the copy.** Rejected: the audit shows the density comes from the
  number of blocks and buttons, not from sentence length.
- **Console as a right-hand drawer.** Rejected: array output (`showport`, `showvlun`) is wide, and a
  drawer covers the step the operator is watching.

## Consequences

- Frontend only: no API, event, backend or registry change. Every action, check, field, download
  and write confirmation stays; some move (SPEC-030 lists where). The one Python addition is the
  text test in `tests/`.
- Two shared blocks are added first (a status slot with folded notes, a log panel with tabs), and
  the existing `DoneList` and `PartsBar` are used by the long steps. Each step is then one slice
  (`docs/workpackets/BL-59.md`).
- The button labels and the page text the lab scripts press or read stay exactly as they are
  (`ui_live_lab.py`, `ui_provision_lab.py`, `failed_apply_lab.py`; SPEC-030 R10), and the text test
  in `check.py` catches a renamed one.
- `UX-GUIDELINES.md` gains the rules in the last slice (D1).
- Risk: a fact the operator needs could end up folded. Mitigation: SPEC-030 R6's default-open rule
  (a section opens by itself when it holds something to act on), the stale-discovery exception and
  the failed-apply state (change 1).
