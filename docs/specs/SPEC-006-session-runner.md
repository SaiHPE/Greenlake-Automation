# SPEC-006 — The session runs itself

**Status:** implemented 2026-09-14 (rc.14; rc.15 fixes the 5.1 encoding failure, LESSONS 38) — **pending its own first live run** (S-12)
**Findings addressed:** G-4 (breadth and failure evidence), the operator's cost of a live session
(11 screenshots, 6 pasted scripts, ~3 hours on 2026-09-14)
**Owner:** `scripts/session.ps1` (ships inside every release zip next to the exe), `api/app.py`
`POST /init-sheet/compose`, `platform/init_sheet.py` `compose_workbook_bytes`

## 1. Problem

Everything the operator did on 2026-09-14 that was not *looking at a screen* was mechanical: click
Discover, click Check, pick members, add export rows, click Build, tick, click Create, click Verify
paths, download the docx, paste a `show*` script, paste a cleanup script. The judgements that found
P-21 — "the plan said Exists, the result said Created", "6 LUNs for 4 volumes" — are comparisons a
script makes better than a person. The looking (labels, layout, wording) is the smaller part and
still needs a person, but once per release, not once per step.

## 2. Scope

In: one PowerShell 5.1 script that drives the exe over its own HTTP API, checks the array over
WSAPI, runs a fixed set of scenarios against a **clean** array, asserts every outcome, cleans up
with the tool's own removal set (SPEC-007), and writes a report plus an evidence folder. A small
server endpoint that fills a workbook from JSON, so the script never writes xlsx itself.
Out: UX judgement (stays a screenshot pass), the init track (needs a factory-fresh array), zoning
apply (G-1, needs a switch write by a human), iSCSI (S-9).

## 3. Requirements

**R1 — One command, three passwords, one report.** `.\session.ps1 -BaseSheet <the operator's
working Initialisation_sheet.xlsx>` — prompts for the array password (used for both the sheet and
WSAPI checks), the vCenter password and the switch password; everything else comes from the base
sheet. Writes `session-<stamp>\report.md` (one PASS/FAIL line per assertion, a summary, the exe
version) and keeps every API response, every WSAPI read and the docx in that folder. Exit code 1
on any FAIL.

**R2 — Refuses a dirty array.** Before anything, WSAPI reads hosts / host sets / volumes / VV sets /
VLUNs; if any object name begins with the runner's prefix (`zz_s6_`) it stops and prints the
SPEC-007-shaped removal lines for them. Records the five counts as the baseline.

**R3 — Sheets from JSON, server-side.** `POST /init-sheet/compose` takes `{base_b64, init, targets,
volumes, hostsets, hosts}`; with `base_b64` it loads that workbook, otherwise the template; fills the
key/value tabs given and **replaces** each row table given (existing data rows cleared first);
returns `{content_b64}`. The runner composes every scenario sheet from the operator's base sheet
and the scenario's rows, so credentials and init fields are never typed into the script.

**R4 — Scenarios, in order, each a run of its own** (Provision only):

| # | Scenario | Asserts |
|---|---|---|
| 1 | **Create** — `zz_s6_vol01` (1 GiB tpvv), `zz_s6_vol02` (1 GiB reduce) in `zz_s6_vvs`; host set `zz_s6_hs` = the base sheet's first vCenter host that Discovery reports logged in on both fabrics; export `zz_s6_vvs → zz_s6_hs` | discovery has ≥1 host on both fabrics · zoning check puts that host in `zoned_hosts` · plan: every `zz_s6_*` row `create`, the host row `exists`, 0 blockers · apply: **every planned `create` is `created`, every `exists` is `exists`, no `failed`** · read-back detail names two LUNs · WSAPI: exactly two new templates, both to `set:zz_s6_hs` · path verification: host `live`, `lun_count == 2`, `paths_per_lun ≥ 2` · removal set has 6 lines in R3 order |
| 2 | **Rerun** — same sheet, new run | plan: every row `exists`, 0 to create, 0 blockers · apply: every outcome `exists`, **WSAPI template count unchanged** (P-21) · removal set empty |
| 3 | **Conflict** — same sheet, `zz_s6_vol01` at 2 GiB | plan: that row `conflict`, `blockers` non-empty · `POST /storage/apply` is refused (HTTP 4xx) · WSAPI unchanged |
| 4 | **Blank members** — same sheet, `zz_s6_hs` members blank, nothing composed | plan: blocker names the set, no `host` rows, no `vlun` rows (SPEC-005) |
| 5 | **Documents** — on run 1: verify, as-built | verify: no mismatch · docx text contains `zz_s6_vol01`, `zz_s6_vvs`, `host set zz_s6_hs`, `To remove what this run created`, the two `removevlun` lines, and **not** "did not include the SAN zoning step" (A-3) |
| 6 | **Cleanup** — paste run 1's removal set over SSH (one password prompt), then WSAPI | the six lines accepted · counts equal the R2 baseline · no `zz_s6_*` left |

**R5 — Waiting is by state, not by sleep.** After each POST the runner polls `GET /runs/{id}` until
`status` leaves `running` (1 s interval, 300 s ceiling) and then reads the latest event of the type
it needs from `GET /runs/{id}/events`. A timeout is a FAIL with the last status.

**R6 — Evidence is kept whole.** Every response body is written as `NN-<step>.json`; every WSAPI
read as `wsapi-<what>-<when>.json`; the docx as `asbuilt.docx`; the SSH transcript as
`cleanup.txt`. The report links them. This folder is what the operator sends back — the same
material fixtures were pinned from on 2026-09-13/14, gathered without a human.

**R7 — Nothing the runner does is new capability.** It uses only endpoints the UI uses, WSAPI GETs,
and — for cleanup only — the tool's own removal lines over SSH. It never writes to a switch, never
issues a CLI command the tool did not generate.

## 4. Acceptance

Python (`tests/unit/test_init_sheet.py`): `test_compose_replaces_row_tables_and_fills_kv_on_a_base_workbook`,
`test_compose_from_template_when_no_base`. Contract (`tests/unit/test_api.py`, Windows CI):
`POST /init-sheet/compose` round-trips through `parse_workbook_bytes`.
PowerShell: `session.ps1` parses under `[Parser]::ParseFile`; **S-12** is its first live run — the
operator runs it once against rack13arcus and sends the folder.

## 5. Limits, stated

- The runner tests what it is told to expect; the assertions are today's register turned into
  code. A new class of defect still needs a person the first time.
- Scenario 1 needs one vCenter host logged in on both fabrics (as `.136` is). On an array with
  none, the runner stops after Discovery with a clear message rather than inventing a host.
- The SSH cleanup prompts for the array password once (the CLI has no token login). Everything
  else is non-interactive after the three prompts at start.
