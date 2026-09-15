# SPEC-010 — The zoning page reads in FOS order

**Status:** implemented 2026-09-15 (rc.21) — pending live screenshot (Zoning plan page with one selected pair)
**Findings addressed:** Z-1 (designer legend implicit), Z-3 (validator flags but does not offer a name),
Z-4 (`cfgtransshow` is a sentence, not the first line; activation order)
**Owner:** `application/provisioning/zoning_plan.py` (`render_commands`, `fos_name_suggestion`),
`frontend/src/steps/ZoningPlanView.tsx`

## 1. Problem

The zoning page was redesigned in rc.6 (panels A–F) and has been through two rounds of live
screenshots. Three small things stayed open. The designer shows an already-zoned pair as a green tick
and a proposed pair as a checkbox with nothing saying so. The alias field tells the operator a name is
*Letters, digits and _ only* and leaves the fix to them. And the FOS procedure — `cfgtransshow`, then
the additive paste, then `cfgsave`, then `cfgenable` — is delivered with its first step as a sentence
beside a button rather than as the first command line, so the one copy of the procedure the SAN team
receives (the `.txt`) starts at step two.

## 2. Requirements

**R1 — `cfgtransshow` is the first line.** `render_commands` emits `cfgtransshow` as the first
command for every fabric that has anything to render; the rendered list is therefore the FOS order
end to end: `cfgtransshow` → `alicreate…` → `zonecreate…` → `cfgadd…` → `cfgsave` → `cfgenable <cfg>`.
The as-built prints the same list (it already prints `commands[fabric]`).

**R2 — Three blocks on screen, one procedure in the file.** The UI renders the list as *1. Check*
(`cfgtransshow`, with the expected reply *"There is no outstanding zoning transaction"* — stop if it
says otherwise), *2. Paste block* (additive, Copy), *3. Save and activate — SAN team, in a window*
(`cfgsave`, `cfgenable`). *Copy paste block* copies block 2 with the `#` header; block 1 has its own
Copy. *Download .txt* carries all three in order with `# ---` separators. The header comment's
"Run cfgtransshow first" sentence goes: the line itself is there.

**R3 — A rejected alias comes with a corrected one.** `fos_name_suggestion(name)` folds every run of
characters FOS rejects to `_`, strips leading/trailing `_`, prefixes `a` when the result would start
with something other than a letter or digit (or be empty), and truncates to 64. The render refusal
reads *"alias 'win host 1' for … contains ' ' — try 'win_host_1'"*. The UI mirrors it: beside a
critical alias check, a *Use win_host_1* button fills the field. Only offered when the suggestion is
valid and differs from what was typed.

**R4 — The designer carries its legend.** One line under the *Design new zones* description:
*✓ already zoned (read from the array; never recreated) · ☑ selected — a new zone will be created ·
☐ available, not selected · ⚠ caution — see the port's note.* Same glyphs the rows use.

## 3. Acceptance

- `tests/unit/test_zoning_plan.py`: the rack13 exact-list test starts with `cfgtransshow`; empty
  selections still render `[]` (no `cfgtransshow` without work); `fos_name_suggestion` on
  `"win host 1"`, `"-lead"`, `""`, a 70-character name, a valid name (unchanged); the refusal text
  carries *try '…'*.
- Frontend: `tsc` clean. Live: one screenshot of the plan page with a pair selected (designer legend,
  alias row with a suggestion after typing a space, the three command blocks).

## 4. Out of scope

Applying anything to a switch (ADR 0012; G-1 stays with the training team). Per-host `#` comment lines
inside the paste block (Z-2 remainder, P).
