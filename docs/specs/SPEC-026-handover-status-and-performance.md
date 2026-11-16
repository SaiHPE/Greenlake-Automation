# SPEC-026 — Array status and performance at handover

**Status:** PROPOSED 2026-11-16 (BL-24). Not built. Needs the owner's yes on
[ADR 0019](../adr/0019-handover-report-from-the-array.md) and the read-only captures in R2 before
any parser is written.
**Research:** [2026-11-16-health-performance-reporting.md](../research/2026-11-16-health-performance-reporting.md) ·
**ADRs:** [0001](../adr/0001-post-init-verification-via-ssh-cli.md) (allowlist addendum) · 0019 ·
**Builds on:** SPEC-002 (as-built sections, failed reads), SPEC-011 (status wording), SPEC-019
(console), SPEC-020 (link latency in the as-built)
**Owner:** `adapters/array/cli_client.py` (`ALLOWED_COMMANDS`), `application/documents/handover.py`
(new: parse and summarise), `application/documents/steps.py` (reads), `application/documents/asbuilt.py`
(section), `frontend/src/steps/AsBuiltStep.tsx` (summary)
**Work packet:** [workpackets/BL-24.md](../workpackets/BL-24.md)

## 1. Problem

The as-built shows the array's `checkhealth` and inventory, but not its **alerts**, its **capacity
in use**, or any **performance** figure. A field engineer handing an array over cannot say "no open
alerts, CPU idle, ports quiet, this is the baseline" without opening a CLI session and pasting
output into the document by hand. LESSONS 24 shows the risk of doing it badly: alerts without
their timestamps sent a team after a fault repaired four days earlier.

## 2. Requirements

**R1 — Five more read commands.** `ALLOWED_COMMANDS` gains `showalert`, `srstatcpu`, `srstatport`,
`srstatvv` and `srstatrcvv`, by exact base name. `tests/unit/test_cli_allowlist.py` (new) pins
that each is allowed, and that `statcpu`, `statport`, `statvv`, `setsr`, `startsr`, `stopsr`,
`createsralertcrit`, `setalert` and `removealert` are refused. ADR 0001 gains an addendum naming
the five. The pull request says plainly that the allowlist grew.

**R2 — Captures before parsers.** A read-only script `lab/handover_capture.py` (copy
`lab/rcip_pair_capture.py`) saves, for each lab array it is pointed at, into
`tests/fixtures/handover/<array>/`: `help showalert`, `help srstatcpu`, `help srstatport`,
`help srstatvv`, `help showsys`; then each command in R3 exactly as the tool will send it; and
`showalert -d` (the form seen live in LESSONS 24). At least one capture comes from an array with
an open alert and one from an array with host I/O, if the lab has them; the README says which.
The command forms in R3 are **proposed**; where the captured help disagrees, the help wins and
this spec is corrected in the same pull request.

**R3 — The reads.** In the as-built step, after the existing reads, over the same SSH session and
credential, each with its own error capture (SPEC-002 R6):

| Key | Command (proposed form) | When |
|---|---|---|
| `alerts` | `showalert -d` | always |
| `space` | `showsys -space` | always |
| `cpu` | `srstatcpu -hires -btsecs -24h -groupby NODE -summary avg,95%,max,per_group` | always |
| `ports` | `srstatport -hires -btsecs -24h -port_type host -groupby PORT_N,PORT_S,PORT_P -summary avg,95%,max,per_group` | always |
| `volumes` | `srstatvv -hires -btsecs -24h -summary avg,95%,max` | always |
| `rcvv` | `srstatrcvv -hires -btsecs -24h -groupby GROUP_NAME -summary avg,max,per_group` | only when the workbook has a Replication tab |

`-btsecs`, `-hires`, `-groupby GROUP_NAME` and `-summary … per_group` are confirmed for
`srstatrcvv` on OS 10.5.0 (`tests/fixtures/rc_pair/help/help_srstatrcvv.txt`); the rest is
confirmed by R2. The window is the 24 hours before the read; when the array has been running for
less, System Reporter returns what it has and the section says from when.

**R4 — Alerts.** Parsed from `showalert -d` into rows: id, state, severity, time, message code,
message. The section lists every alert not in a fixed state, newest first, with a column *Before
this run* (alert time earlier than the run's creation). One verdict sentence above the table:
*"No open alerts."* or *"N open alerts; the oldest is from <date>. Alerts record an event, not the
current state: compare each with checkhealth before acting."* An alert of severity Major, Critical
or Fatal (the array's words, from the capture) adds an as-built **warning** naming it; it never
blocks the document. The tool runs no alert command other than `showalert`; the section may name
`setalert` and `removealert` as the operator's commands to acknowledge or remove one.

**R5 — Capacity.** From `showsys -space`: total, allocated, free, and data reduction where the
array prints it, in TiB with one decimal and the array's own figure beside it. The exact lines are
taken from the capture.

**R6 — Performance baseline.** Three tables, each with average, 95th percentile and maximum over
the window: per controller node CPU (% busy); per host port IOPS, throughput (MB/s) and service
time (ms); the whole array's volume IOPS, throughput and service time. Above the tables: the window
(from, to, sample interval). When the whole array's average IOPS is below 10 (`IDLE_IOPS`, a
named constant), the sentence *"The array carried almost no host I/O in this window. These figures
are an idle baseline for later comparison, not a measure of what the array can do."* No figure is
ever written as `0` for a read that failed: a failed read is named (R8).

**R7 — Remote Copy.** With a Replication tab: one row per Remote Copy group with local and remote
service time and the RPO column as System Reporter prints it, placed in the replication section
next to SPEC-020's link check paragraph. Absent otherwise.

**R8 — Failed and unknown reads.** A command refused, timed out or unknown on this OS is recorded in
`AsBuiltData.read_errors` and shown in its subsection as *"Could not read: <command> — <the array's
words>"*, plus an as-built warning, exactly like SPEC-002 R6. The other subsections still render.
A report with no rows (no host ports, nothing in the window) says so in a sentence without a warning.

**R9 — The document section.** A new Heading 1 *Array status and performance at handover*, placed
after the `checkhealth` section (matched by intent like the others), with subsections *Alerts*,
*Capacity*, *Performance baseline*, and a last line: *"This section was read from the array at
<time>. The tool did not read HPE's cloud view of this array (cloud connection, call-home)."*
HPE house-style tables (`asbuilt_docx.hpe_table`).

**R10 — Event and page.** `asbuilt.generated` data gains `handover`: `{read_at, window_from,
window_to, alerts_open, alerts_major, oldest_alert, cpu_max_pct, iops_avg, idle, read_errors}`. The
As-built step page shows, once generated, a *Status at handover* block: the alert verdict (status
indicator with colour, icon and words), the window, peak CPU, average IOPS, and the idle sentence
when `idle`. No UI string says *health* (UX-GUIDELINES §4); the word is *status*.

**R11 — Console.** Every command in R3 appears in the command log and the as-built appendix like
any other read (SPEC-019). Nothing to add: the reads go through the same client.

**R12 — Retention.** No new artifact. The figures live in the docx and the event, both already
bounded (LESSONS 9).

## 3. Non-goals

DSCC reads (cloud connection, call-home, DSCC issues, DSCC performance history): slice 2, after a
read-only probe settles the permissions, system id and regional host (research §6). Wellness events
and InfoSight. The onboard Prometheus exporter. Live samplers (`stat*`). Acknowledging, fixing or
removing alerts. A performance *test* (load generation). Per-volume or per-host performance tables.
Trends across runs. Showing alerts on the Verify page (a later slice may move the alert table
there).

## 4. Verification

Unit, all on R2's captures: the allowlist pins (R1); `showalert -d` parsed (count, fields, the
*Before this run* flag against a fixed run time, the Major warning); `showsys -space` parsed; each
`srstat*` summary parsed (avg, 95 %, max per group; the idle sentence below `IDLE_IOPS` and not
above it; the existing `srstatrcvv_hourly.txt` capture as the all-zero case); a refused or unknown
command gives the named line and a warning while the other subsections render; the docx has the
heading after `checkhealth` and no `0` where a read failed; `asbuilt.generated` carries `handover`.
Frontend: `tsc` clean.

## 5. Live-run checklist

Read-only on the array; ask the owner before running.

1. `lab/handover_capture.py` against the lab arrays: every command in R3 answers; the help files
   saved; no command refused by the array.
2. A run in *Verify only* mode on a lab array; generate the as-built from the page.
3. The console shows the five new reads, nothing else new, no write.
4. The document: the new section after `checkhealth`; the alert table matches `showalert -d` typed by
   hand in *Open terminal*; *Before this run* correct for at least one alert; the window matches the
   clock; the idle sentence present on an idle array.
5. The page: *Status at handover* shows the same counts as the document; no "health" on screen.
6. With a Replication tab, on the lab pair: the Remote Copy rows next to the link check.
7. One read made to fail (an older array or a user without the role, if the lab has one): the named
   line and a warning, the rest of the section present.
8. Validation record in `docs/validation/` with the run id, and the capture files committed.

## 5a. Size

Allowlist and tests (~30 lines), `handover.py` parsers and summary (~220), reads (~30), as-built
section (~150), event field (~15), page block (~70), capture script (~80), ~25 unit tests.
