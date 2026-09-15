# SPEC-011 — Verify says what to look at

**Status:** implemented 2026-09-15 (rc.22) — pending live screenshot (Verify page on rack13arcus, one
status row expanded)
**Findings addressed:** V-1 (status summary rows are not actionable; detail rows never reach the UI),
V-2 (footnote examples that match none of the rows), V-3 ("health" wording), V-4 (two visibly
different strings called *Match*), V-5 (*Not readable* footnote with no such row); X-7's Verify half
(nothing says what changed since the last check)
**Owner:** `domain/models.py` (`FieldCheck.match`, `HealthIssue.details`), `application/documents/verification.py`,
`frontend/src/steps/VerifyStep.tsx`

## 1. Problem

The live Verify page (S-8, 2026-09-14) showed *vlun — Hosts not connected to a port — 4* and
*Port — Degraded or failed SFPs — 2*. Which four hosts? Which two ports? The array said, in the
Detail table of the same command; the tool parsed those rows for the as-built and threw them away
for the screen. Under the table a footnote promised guidance — *"for example replication links, iLO,
cage or security"* — that matched none of the five rows. *Support contact* compared
`prabhu.barrow@hpe.com` with `Prabhu Barrow Selvaraj, 9632988119, prabhu.barrow@hpe.com` and called
it *Match*, correctly, without saying the rule was *contains*. And the *Not readable* footnote printed
when nothing was not readable.

## 2. Requirements

**R1 — The array's detail rows reach the screen.** `HealthIssue.details: list[HealthDetail]`
(`identifier`, `description`, `resolution`) — the Detail-table rows whose Component matches the
summary row, attached by `_health_issues`. The UI renders each status row with an expander; expanded,
it lists the identifiers with the array's own description and resolution. Rows with no detail rows
say so (*the array gave no detail for this component*).

**R2 — Guidance is the array's, not ours.** The generic footnote and its examples are gone. In their
place: *"Each component here needs attention outside this tool. Expand a row for the identifiers the
array names and the resolution it states."* Nothing about replication links, iLO or cages unless the
array said so.

**R3 — The row says how it matched.** `FieldCheck.match: 'exact' | 'contains' | 'includes'` set by
`_exact`, `_contains`, `_set`. A passing *contains* row reads *Match · contains the expected value*; a
passing *includes* row (DNS servers) *Match · every expected value present*; exact rows stay *Match*.

**R4 — Footnotes only when they apply.** The *Not readable* sentence renders only when at least one
row is not readable.

**R5 — What changed since the last check.** When the run holds an earlier `verify.completed`, the
status card marks each summary row *new* (component + summary not in the earlier report), *cleared*
(present before, gone now — listed in a line under the table) or unchanged, and the card's description
says *compared with the check at HH:MM*. The first check says nothing about change.

**R6 — Wording.** No new UI string says *health*; the card stays *Array status*. Code identifiers
(`health_issues`, `checkhealth`) are not renamed: `checkhealth` is the command's name, and
`health_issues` is load-bearing in the event payload and the as-built.

## 3. Acceptance

- `tests/unit/test_verification.py`: detail rows attach to their component (Alert 1, Security 1;
  RC none); a detail row's component with no summary row is not invented; `match` per rule.
- Frontend: `tsc` clean. Live: one screenshot with a status row expanded and *Support contact* showing
  the *contains* note.

## 4. Out of scope

Naming the four hosts behind *vlun — Hosts not connected to a port* when the array's Detail table
does not (it names identifiers where it has them; the tool adds none). A baseline across runs (R5 is
within one run; cross-run history is G-3's territory).
