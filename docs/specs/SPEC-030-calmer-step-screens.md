# SPEC-030 — A calmer screen per step

**Status:** accepted 2026-11-17 with changes, design only (nothing built) · **Decision:** [ADR 0023](../adr/0023-one-question-per-step-screen.md)
(accepted 2026-11-17, owner's decision; its *Changes on acceptance* are written into this spec)
· **Tracker:** BL-59, *UI round 2: one question per screen* · **Work packet:** [`workpackets/BL-59.md`](../workpackets/BL-59.md)
· **Builds on:** BL-43's October redesign (draft 3, built 2026-10-14, closed 2026-11-17)
· **Mockup:** M16 in `frontend/mockups` (`npm run mockups`, draft 4)
**Owner:** frontend only: `frontend/src/ui/*`, `frontend/src/steps/*`, `frontend/mockups/*`. No API, event, backend or registry change.
**Rules it applies:** [`UX-GUIDELINES.md`](../UX-GUIDELINES.md) §4 (status and notifications), §5 (buttons), §6 (wizard),
§8 (collapsible child object), §14 (accessibility), taken from the Design System docs source
(design-system.hpe.design: *templates/wizard*, *components/notification*, *components/button*,
*templates/status-indicator*, *templates/empty-state*, *components/datatable*).

## 1. Problem

BL-43's draft-3 redesign (built 2026-10-14, live on labrat 24/0 read-only and 18/0 with an apply,
its replication screens live 2026-11-05 in BL-41's runs; closed 2026-11-17) fixed the frame. This
spec is its round 2, BL-59. Since then BL-41 (partnership plan), BL-42 (link check), BL-44 (iSCSI hosts) and
the console (SPEC-019) each added panels, notices and buttons to existing screens, and two parts of
draft 3 were never carried over: the `DoneList` for finished parts (built in `ui/blocks.tsx`, used
by no step) and a mockup of the zoning designer (M8 says "not mocked here"). The operator's
October complaint, "a screen asks several things at once and the answer is below the fold", is
back on the long steps.

## 2. Audit (from the code at b7006373)

Counts are the most a screen shows at once in a realistic state. "Notices" = inline
notifications (status lines, gates, info and warning boxes). Footer counts exclude the tick.
Since this audit, three items on the integration branch changed the screens: BL-36 (Discovery
marks a host's multipath warning), BL-45 (Provision storage keeps the removal set after a failed
apply) and BL-52 (the approval tick belongs to the plan on screen, by its id). The slices start
from a `main` that has them.

| Step | Panels / sections | Tables | Notices | Buttons in content | Footer | What competes |
|---|---|---|---|---|---|---|
| Prerequisites | 7 sections under 2 headings | 1 (folded) | 1–3 | 5 + 4 videos | 1–3 | A clock that is off is said 5 times: header label, status line, section summary, section button, footer primary |
| Initialisation sheet | 1 panel (12+ values) | 0 | 1–3 | file input | 2 | "Workbook read" and the credential check are two status lines |
| Mode | 6 cards + custom panel | 0 | 1–3 | ~10 ticks (Custom) | 1 | Two-sentence description |
| GreenLake registration | 1 | 0 | 1–3 | dry-run tick | 1 | calm |
| Cloud Connectivity | 2 | 0 | 1–3 (gate) | 1 | 1 | calm |
| DSCC setup | 2 (clock, browser) | 0 | 1–3 (gate) | 2 | 2 | calm |
| Discovery | up to 9 sections + legend | up to 9 | up to 6 | 1 | 3 | Hosts-in-run sections open by default (one per OS); freshness, "since the last discovery" and notes all sit above the results |
| SAN zoning | host table + 4 plan panels + command set | 2 + per-fabric blocks | up to 5 before the plan, + 2 per fabric | ~10 + a tick per pair; **Generate command set is a second, disabled primary** | 3 | The designer, the names and the command set are all open at once; the zoning pair status uses its own icon set |
| Provision storage | parts bar + 3 sections + 1 panel (Compose nests a second panel) | 3 | 2–4 | 7; **Save composition is a second, disabled primary** | 3 + tick | Builder copy says "(dropdowns)", "VV-set", "fabric-login", "to-be-created" |
| Replication | parts bar + 7 sections + 1 panel | 5 | up to 3 (12 conditions) | 6 + a **second tick** (latency) in the content; *Check the link* and *Verify replication* also sit in the footer | up to 4 + tick | Three-sentence description; *Continue to Failover test without configuring replication* is the longest label in the app |
| Failover test | 3 | 1 | 1–2 | group picker | 2 + tick | moderate |
| Verify configuration | credential + 2 sections | 2 (status can list ~195 items) | 1–3 | 0 | 2 | moderate |
| As-built document | 5 panels / lists | 0 | 1–3 | form | 2 | The empty state sits under the cover form; after generating, the cover is shown twice (form and *On the cover*) |
| Finish | docs list + 2 sections | 0 | 1–3 | 0 | header 1–2 | calm |

**Chrome, on every step:** six horizontal bands (app header, wizard bar, step identifier, content,
footer with an optional tick row and blocked-message row, console bar). The step's state appears in
four places: the app header (run state, for example *Waiting for you*), the rail, the step header
(with a detail suffix such as *Complete · 8 ports · 2 hosts in this run*) and the status line.
*About this step* opens by default on most steps and takes a third of the width at 1366 (Grommet's
`large` starts at 1081). Disabled buttons remain in the builder, the zoning view and the console.

**Vertical budget, estimated** from the theme's spacing tokens (Chrome on Windows at 1366 x 768
leaves about 640 px): app header ≈ 60, wizard bar ≈ 52, footer ≈ 64 (+ ≈ 48 with the tick row),
console bar ≈ 44, so the scroll area is ≈ 420 px (≈ 370 with a tick). Step identifier with a
two-line description ≈ 150, parts bar ≈ 64, status line ≈ 90: on Provision storage and Replication
about 70 to 120 px of content shows before scrolling. These are estimates; slice S0 measures them.

## 3. Requirements

**R1 — One question per screen.** Each step state has one question, said by the status line and
acted on by the footer primary. The content under it answers that question; everything else is
folded (R6). The per-step questions are in §4.

**R2 — One status line.** `StepShell` draws at most one status notification under the header,
picked in this order: the step's error (closable) > failed > blocked > running > waiting >
action required > complete > the empty state (when nothing has run). Every other notice becomes a
**note**: one folded line under the status line, "N notes", opening to a list (one note per line,
SPEC-004 R3). Notes are: "since the last discovery / check / plan", discovery, check and plan
notes, run warnings, the fresh-discovery time. **Exception (LESSONS 8):** a stale discovery
(over 12 hours) on a step that acts on it (SAN zoning, Provision storage) stays a visible warning
under the status line. The write gates (`gate`) and form errors stay where they are.

**R3 — One primary, in the footer; no disabled buttons.** No `primary` button inside step content
(the zoning *Generate command set* and the builder's *Save composition* stop being primary and stay
in the page as default buttons (Q3); so do the console's *Run* and its *Activity* /
*Console* toggles, which turn primary while open today). No
`disabled` on any button in a step or the console: a button that cannot act yet stays active and
says why on click (the footer's `blocked`, or an inline sentence), or is not drawn. An action is
drawn in one place only: the footer, or a part's row, never both.

**R4 — The footer holds at most three buttons.** The primary and two others. A finished part's
"do it again" (*Read both arrays again*, *Check the link again*, *Verify again*, *Rebuild plan*)
moves to that part's row (R7). Exception: after a failed apply on Provision storage, *Rebuild plan*
is the footer primary (R7a). At `large` and wider the tick sits on the footer row, left of the
buttons (as the signed-off draft-3 kit draws it); below `large` it stacks above. A step may have
two ticks (Replication's latency acceptance and its plan authorisation): both in the footer, in
that order; the blocked message names the first one not ticked and keeps today's form, *Tick the
box first: <tick text>*. **Tick wording does not change** (LESSONS 7), and a plan's tick belongs to
that plan's id (BL-52): a rebuilt plan starts unticked, and the apply sends the id only when it was
ticked.

**R5 — The header says the state, not the numbers.** The step header shows the state word only
(`stateDetail` is dropped; its counts move into the status line). A `stateLabel` override stays
only where it avoids alarm before anything happened (Prerequisites, Initialisation sheet, Mode) or
names who we wait on (*Waiting on the SAN team*); at most three words. In the wizard view the app
header drops the mode (the wizard bar already reads "<mode> on <serial>"); it keeps the serial,
which says which array is written to, and the run state (Q1). Home, Run overview and Finish are
unchanged.

**R6 — Progressive disclosure, three levels.** L1 always visible: header, status line, the current
part, the footer. L2 one click: finished parts (`DoneList` *Show detail*), inventories, result
tables, other hosts, commands, removal sets, legends (a `Section`, folded). L3 the log panel (R11).
A section opens by itself only when it holds something to act on now: a failure, a conflict, a
blocked check, a host not logged in, a host with a multipath warning (BL-36), a field to fill. A
closed section renders nothing, so no text the lab scripts read (R10) may sit inside one in the
state the script reads it; a section's title, which stays drawn, may carry it. Toggles read
"Show <thing> (N)" / "Hide <thing>"; a section header keeps aria-label "Show detail" / "Hide detail".

**R7 — Parts, not pages.** SAN zoning (new: *Check the array*, *Draft zones*, *Hand off*),
Provision storage (4 parts) and Replication (5 parts) draw: the parts bar directly under the h1
(the description moves into *About this step*); finished parts as **one** `DoneList`, one row
each: icon, one-line result, *Show detail*, the part's "again" button; the current part as the one
open `Panel` titled with the part's name (h2); later parts are not drawn. The step keeps its one
registry entry (rule 5).

**R7a — A failed apply is a state of its own** (Provision storage, BL-45). When the last apply
stopped with an error, *Create* stays the open part, not a finished row: the status line *Creation
reported an error* with the array's error and how many objects were made before it stopped, the
result table and the *Removal command set* showing without a click. The footer primary is
*Rebuild plan*; *Create storage objects* is not drawn. After *Rebuild plan*, the earlier applies'
removal set stays under the folded section *Undo what this run created* (title word for word).

**R8 — About this step is closed by default** on every step, opened by the header button; the
choice is kept for the browser session (`sessionStorage` key `alletra.about`). Descriptions are
one sentence of at most 120 characters; the rest moves into *About this step*.

**R9 — One status vocabulary.** Steps use the six state words in `ui/status.tsx`. Rows in tables
use the result words below, each drawn with `StatusIndicator` (icon + colour + word); no step
keeps its own icon map (the zoning `PairStatus` goes).

| Row of | Words (state drawn) |
|---|---|
| A check (prerequisites, readiness, link) | Passed (complete) · Review (action required) · Failed (failed) · Not checked (not started). The link check keeps its own wording: the latency in ms, *within the limit* or *over the limit for ...* |
| An endpoint | Reachable (complete) · Blocked (failed) |
| A port | Ready (complete) · the array's own word (action required) |
| A host on a fabric | Zoned (complete) · Not zoned (failed; waiting while a command set is with the SAN team) · Partly zoned (action required) · Not on fabric (not started) |
| A plan row | Create (not started) · Update (action required) · Already there (complete) · Conflict (failed) |
| A write | Created · Updated (complete) · Already there (not started) · Failed (failed) · Skipped (not started) |
| Paths | Live (complete) · Partial (action required) · No path (action required: amber; a report, never a gate, Q4) |
| A group | Replicating (complete) · Initial sync in progress (running) · Not replicating (failed) |
| A setting | Matches (complete) · Differs (action required) · Not readable (not started) |
| A failover step | Passed (complete) · Failed · Skipped |

An empty cell is `--` with `a11yTitle="No value"` (never `—` or `n/a`). This renames *Exists* /
*Existed* to *Already there*, *Done* and *OK* to *Created* / *Passed*, *Match* / *Mismatch* to
*Matches* / *Differs*, and draws *No path* amber instead of grey (`path_verify.py`: a host with no
path is fine until it is on and zoned; red would read as the tool failed). A renamed word changes
in every sentence that names it too: *objects already made will show as Already there*, *Objects
marked Already there are left alone*.

**R10 — Copy.** Plain words on screen; command names (`checkrclink`, `cfgenable`, `showvlun`) only
inside commands, the log and *About this step*. Banned on screen: *health*, *WSAPI*, *SSE*,
*n:s:p*, *VV-set* (say *volume set*), *(dropdowns)*, *to-be-created*, *fabric-login*, ADR / SPEC /
version numbers. A status line is a title of at most 8 words plus one sentence, with up to two
links (the Design System allows links, not buttons). Skip buttons keep SPEC-012 R2's *Continue to
<next step> without <work>* (Q2), with the work in a word or two: *without provisioning*, *without
replication* (today *without configuring replication*), *without the failover test*, *without
verifying*, *without the document*.

**Frozen words.** Three lab scripts drive the screens and read them: `lab/ui_live_lab.py`
(read-only), `lab/ui_provision_lab.py` and `lab/failed_apply_lab.py` (both write `zz_*` objects
and remove them). They press buttons by name and look for text in the page body, which holds only
what is drawn: a closed section's content is not there (R6). Everything below stays word for word,
drawn in the state named; a test in `check.py` guards the literals (§6). `ui-smoke/` is local and
git-ignored, so its scripts are not on the list.

| Pressed or filled (by name) | Where |
|---|---|
| *Build plan*, *Rebuild plan*, *Create storage objects*, *Verify paths* | Provision storage footer (*Rebuild plan* in the footer after a failed apply, R7a) |
| Labels starting *Continue with* / *Continue to* | SAN zoning / Provision storage footer |
| The tick starting *I have reviewed this plan* | A `label` on the Provision storage plan |
| *Undo what this run created* | Section title on Provision storage once a plan is rebuilt after an apply; clicked to open |
| *Activity* (start of the name), *Console (N commands)*, *Run*, the field named *Read-only command* | The log bar and the console prompt |
| *Runs*, *Your runs*; the rail labels, *Run overview*, *Finish* | App header menu; rail (from the registry) |

| Read on the page | Step and state |
|---|---|
| *Checked by this tool* · *Initialisation sheet* · *What do you want to do* · *Fibre Channel port* | Prerequisites · Initialisation sheet · Mode · Discovery after a run |
| One of *the array can reach* / *Fabrics* / *No host is zoned* | SAN zoning after a check |
| *plan* · *Read both arrays* · *sequence* · *Configuration* · *Cover details* | Provision storage · Replication · Failover test · Verify configuration · As-built document (also after the document is made) |
| *Documents and logs* · *Hand-over package* · *Start a new run* · *discover* | Run overview · Finish · Your runs · Discovery with Activity open |
| *No plan yet* | Provision storage before a plan |
| *Review the plan, then approve creation*, *Review the plan*, the plan's object names, *I have reviewed this plan* | Provision storage, plan to approve |
| *Tick the box first* | Create pressed without the tick (the footer's blocked message) |
| *N created*, *What the array answered*, *Verify the paths next* | Provision storage after a create |
| *read back*, the host name, *Continue to* | Provision storage after Verify paths |
| *Creation reported an error*, *N objects were created before it stopped*, *Removal command set*, each removal command | Provision storage after a failed apply (R7a) |
| *Undo what this run created* and each removal command, once opened | Provision storage, plan rebuilt after a failed apply |

Also read, but made by the backend, not the screens: the apply's error (*Stopped while creating
volume ...*) and the console's refusal (*The console runs the tool's read-only commands ...*); the
screens show them as they come. Every step page has one h1 and at least one footer button, and no
page shows *undefined*, *NaN* or *[object Object]*.

**R11 — The log panel.** The bar stays one line (last event, *Activity (N)*, *Console (N
commands)*, same names). Either button opens one panel with two tabs, *Activity* and *Commands*,
on the tab pressed; the panel is at most 40% of the window high (minimum 160 px), scrolls inside,
and the step footer stays on screen above it. A *Taller* / *Shorter* button on the panel raises the
cap to 70% and back (Q5; no drag handle): the terminal is 220 px high today and gets about 150 px
under the 40% cap at 768 high. It never opens by itself. A failed or waiting status
line may carry a link *See the commands* that opens it on *Commands*. Everything the console does
today stays (find, copy, download, open terminal, the read-only prompt, the target choice); its
*Run* and *Open terminal* stop being disabled and say why on click. Built in two slices: S5a caps
today's panels and fixes the buttons; S5b adds the tabs, *Taller* / *Shorter* and the link.

**R12 — Accessibility.** One h1; h2 for the current part and sections, h3 inside; no skipped
level. The status line sits in a `role="status"` region (`aria-live="polite"`) so a finished
action is announced; the error variant uses `role="alert"`. Every toggle is a button with
`aria-expanded`; *Show detail* names what it shows. Status is never colour alone (R9). The tabs
are Grommet `Tabs` (arrow keys move between them, Tab enters the panel). Focus does not jump when
a part finishes; it stays on the button pressed (busy then idle). Tables keep their `a11yTitle`.
Checked at 1366 x 768 and 1080 x 720, keyboard only, once per slice.

**R13 — The fold.** At 1366 x 768 and 1080 x 720, with *About this step* closed and the log
closed: the step header, the status line, the first lines of the current part and the whole
footer are visible without scrolling, on every step and state in §4.

**R14 — Nothing else moves.** No step changes what it calls, what it gates on, what it writes or
what it emits. The step list comes from `/app/profile` (rule 5); a step's state comes from
`useStepState` (no second copy). Every action, check, field, download, video and tick stays;
where one moves, the slice's brief says where. Zoning command text, removal sets and the
failover way back stay byte-identical (the SAN team and the operator paste them); the activation
block stays apart from the paste block and marked (LESSONS 31, ADR 0012).

## 4. Per-step target

Wireframes are at 1366 x 768 with the rail, *About* closed and the log closed. `[ ]` is a
default button, `[[ ]]` the primary, `( )` a tick, `▸` a folded section, `✓` a finished part row.

**Frame (every step)**
```
HPE  HPE Alletra Storage MP onboarding                                   Runs ▾
← Discovery          Provision, then replicate on DEMO000001          ✕ Cancel run
Step 5 of 9                                                  ⓘ About   ● Action required
SAN zoning
 1 Check the array ─ 2 Draft zones ─ 3 Hand off                    (parts steps only)
┌ status line: title + one sentence + time + ≤2 links ┐  ▸ 2 notes
│ current part (h2), open                                                │
✓ finished part · result                    Show detail          [Again]
▸ folded sections
──────────────────────────────────────────────────────────────────────────
( tick text )                               [ ] [ ]                [[ Primary ]]
◷ 19:40 last event                         [Activity (14)] [Console (31 commands)]
```

| Step | The question, by state | Open (L1) | Folded (L2) | Footer |
|---|---|---|---|---|
| Prerequisites | Can this workstation reach HPE? → Is the clock right? → Have you done the by-hand items? | Status line; the 3 tool checks as rows with result words | Each check's detail, the 4 by-hand sections (videos inside) | Download sheet, Continue without syncing (clock off only), primary Sync system clock or Continue |
| Initialisation sheet | Is this the right workbook? | File drop; once read, the 8 identity values (serial, product, system name, management IP, regions, country, gateway, NTP) | The device endpoints and replication ports (*Show all values*); the credential check result as a note unless it failed | Validate GreenLake credentials, primary Continue |
| Mode | What do you want to do? | Cards; Custom picker only when Custom | "This run will do" line stays | primary Create run · N steps |
| GreenLake / Cloud Connectivity / DSCC | Unchanged layout; R2, R5, R8, R10 only | | | unchanged |
| Discovery | What did it find, and is anything missing? | Status line with the counts; a list of findings, one row each: array ports, hosts in this run, other hosts, replication ports, file ports | Every table; readiness (opens when blocked); the legend (*What the columns mean*); hosts in this run open only when one is not logged in or has a multipath warning | Check readiness, Run discovery again, primary Continue |
| SAN zoning | Which hosts can reach the array? → Which pairs should be zoned? → What should the aliases be called? → Has the SAN team applied it? | Part 1: the host table. Part 2: the pair picker, then the names, with *Generate command set* in the names panel as a default button, never disabled (Q3). Part 3: the command set (3 blocks) | Fabrics and current zoning (*What the switches hold*), Export .txt inside it | As today, at most three: Build zoning plan or Rebuild plan, Check zoning on the array (or again), and Continue with N zoned hosts (primary once a host is zoned) |
| Provision storage | Who gets which volumes? → Is this the plan? → (Create) → Can the hosts see them? | The current part: Compose (one panel, no nested panel), the plan table, or path verification. After a failed apply: the Create part with its removal set (R7a) | Created objects + removal set (row of *Create*, its text keeps *What the array answered*), composition applied (row of *Compose*) | Rebuild plan on the *Review* row (footer primary after a failed apply); Continue to <next> without provisioning; primary Build plan / Create storage objects / Verify paths / Continue |
| Replication | Can the arrays see each other? → Is the link fast enough? → Is this the plan? → (Configure) → Is it replicating? | The current part: the two array cards, the latency table, the plan table (commands behind *Show N commands*), or the verify table | Finished parts in the `DoneList`; writes and removal set (row of *Configure*); *Other groups on <array> (N), never touched* | Continue to <next> without replication, at most one more, primary by part; both ticks in the footer |
| Failover test | Which group, and do you authorise the role change? | Group picker; the sequence table | The documented way back opens by itself after a failure | unchanged + tick |
| Verify configuration | Does the array match the workbook? | Status line ("3 settings differ"); the differing rows only | All settings (*Show all N*), array status (opens when new issues), the credential section | unchanged |
| As-built document | Is the document ready to send? | Before: empty state first, then the cover form. After: the file row with Download, *Check before sending* | The cover form, in a section titled *Cover details* (the lab reads the title); *On the cover* goes (the form shows the values) | unchanged |
| Finish, Home, Run overview | R9 words only | | | unchanged |

**Zoning, as mocked in M16** (state "Command set handed off"):
```
SAN zoning                                                ◷ Waiting on the SAN team
 ✓ 1 Check the array ─ ✓ 2 Draft zones ─ ● 3 Hand off
◷ Waiting on the SAN team: 2 zones for esx-demo-02 on F2. ...  since 19:40  See the commands
✓ Checked the array 19:38 · 1 of 2 hosts zoned                Show detail   [Check again]
✓ Picked 2 pairs on fabric F2                                 Show detail   [Change]
✓ Named 1 new alias · 2 reused                                Show detail
Command set for the SAN team · fabric F2            [Copy paste block] [Download .txt]
  1. Check, run alone first     cfgtransshow
  2. Paste block, additive only alicreate ... zonecreate ... cfgadd ...
 ┃3. Save and activate: the SAN team, in a window   cfgsave / cfgenable "demo_F2_cfg"
▸ What the switches hold
──────────────────────────────────────────────────────────────────────────
                                   [Continue with esx-demo-01]  [[Check zoning again]]
```
*Generate command set* stays in the page (Q3), so `ZoningPlanView` hands nothing up to the
footer and keeps its own state and its keyed remount (aliases are seeded once per plan event).
M16's *pick* and *names* states still draw *Name the aliases* and *Generate command set* as the
footer primary; slice P8a brings M16 in line before any code.

## 5. Shared blocks, built first

1. **`StepShell` status slot** (`status`, `notes`, `staleNotice` props; R2, R12) and the header
   change (R5: no `stateDetail`), *About* closed by default (R8), footer rules (R4: tick on the
   button row at `large`, `confirmations[]`, a development warning when more than two non-primary
   buttons are passed).
2. **`Disclosure`** in `ui/blocks.tsx`: an inline "Show <thing> (N)" / "Hide <thing>" toggle for
   commands and legends inside a section (R6).
3. **`DoneList`** (exists): the long steps adopt it (R7); its rows gain `aria-label` on *Show detail*.
4. **Result words** in `ui/status.tsx`: one `RESULT` table (R9) that the step maps point to.
5. **Log panel** in `ui/ConsolePane.tsx` (R11): first the 40% cap on today's panels and the
   button fixes (S5a), then the tabs, *Taller* / *Shorter* and an `openLog('commands')` on
   `StepContext` for the status line link (S5b).
6. **App header in the wizard** (R5): no mode; the serial and the run state stay (Q1).

## 6. Verification, per slice

- `npm run typecheck` (in `scripts/check.py`), and `npx tsc -p mockups --noEmit` when a mockup changes.
- **The frozen words test** (slice T1, before any step slice), run by `scripts/check.py` with the
  rest of pytest: it reads the three lab scripts (R10), collects every literal they press, fill or
  look for, and finds each in `frontend/src` (the rail labels in the step registry; the backend's
  own sentences in `src/`). A missing one fails with the literal, the script and its line. It
  proves the words exist in the source, not that they are drawn in the right state; the
  screenshots and the lab run check that. ADR 0011 said to revisit UI tests if the frontend
  changed a lot again; this text check is that revisit, not a frontend test suite.
- Sign-off before code (LESSONS 22): the owner reviews M16 and this spec; a slice that changes a
  screen not mocked gets its mockup state first.
- Screenshots through the app on the dev server (`onboard ui` + `npm run dev`) against a run made
  from the captured fixtures, at 1366 x 768 and 1080 x 720, each state named in the brief, attached
  to the pull request with the before shot (S0 takes the first set). Check R13 (the fold) on each.
- Keyboard pass (R12) and a search of the changed screens for the banned words (R10).
- Lab, on the owner's say-so after the last slice: `lab/ui_live_lab.py` (read-only), then
  `lab/ui_provision_lab.py` and `lab/failed_apply_lab.py` (they write `zz_*` objects and remove
  them). They press and read the words R10 freezes. Until then each slice is *built, pending live
  run*.

## 7. Questions for the owner, answered 2026-11-17

- **Q1** Remove the run's serial, mode and state from the app header in the wizard (R5)?
  **Answer:** the mode only. The serial stays (it says which array is written to), and so does the
  run state.
- **Q2** *Skip to <next step>* in place of *Continue to <next> without <work>* (R10)?
  **Answer:** no. Keep *Continue to X without Y* (SPEC-012 R2); shorten the endings, for example
  *without replication*.
- **Q3** Zoning's *Generate command set* as the footer primary, or in the page as a default button?
  **Answer:** in the page, as a secondary button that is never disabled (P8a). P8b is dropped.
- **Q4** *No path* after provisioning: red or amber? **Answer:** amber. `path_verify.py` treats a
  host with no path as fine until it is on and zoned and never blocks; red reads as the tool failed.
- **Q5** Is 40% of the window the right cap for the log panel, or should it be resizable?
  **Answer:** 40% now, plus a *Taller* / *Shorter* button, not a drag handle (R11).
