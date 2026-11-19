# SPEC-026 — Array status at handover (performance until 2026-11-19)

**Status:** first slice **built 2026-11-17, pending live run** (work packet steps 2 to 7: R1, R3 to
R6 and R8 to R11; R7 is a later slice). APPROVED 2026-11-17 with
[ADR 0019](../adr/0019-handover-report-from-the-array.md) (the owner's decision, with the review's
changes folded in below; proposed 2026-11-16, BL-24). The owner's answers to §2a items 8 to 10 are in
R7, R6 and R4. The R2 captures are in: rack13-ARCUS on OS 10.6.0 (2026-11-16), and D22U27, E18U31 and
VZ on OS 10.5.0, 10.5.60 and 10.5.51 (2026-11-17), with the corrected CPU and port forms (§2a). The
allowlist has the four commands; the as-built reads, parses and renders them, and the page shows the
summary, all pinned to those captures (§2b). Not yet run on an array (§5).
**Research:** [2026-11-16-health-performance-reporting.md](../research/2026-11-16-health-performance-reporting.md) ·
**ADRs:** [0001](../adr/0001-post-init-verification-via-ssh-cli.md) (allowlist addendum) · 0019 ·
**Builds on:** SPEC-002 (as-built sections, failed reads), SPEC-011 (status wording), SPEC-019
(console), SPEC-020 (link latency in the as-built)
**Owner:** `adapters/array/cli_client.py` (`ALLOWED_COMMANDS`), `application/documents/handover.py`
(new: parse and summarise), `application/documents/steps.py` (reads), `application/documents/asbuilt.py`
(section), `frontend/src/steps/AsBuiltStep.tsx` (summary)
**Work packet:** [workpackets/BL-24.md](../workpackets/BL-24.md)

## 0. The owner's decision, 2026-11-19: performance removed from the as-built

**2026-11-19: performance removed from the as-built at the owner's request** (after the customer demo of
replication over RCIP; BL-64, branch `feat/bl-64-demo-feedback`). It keeps alerts and capacity. What
changes in the requirements below, which are left as written for the record:

- **R1.** `srstatcpu`, `srstatport` and `srstatvv` leave `ALLOWED_COMMANDS` (nothing else read them; ADR
  0001 addendum 2026-11-19). `test_cli_allowlist.py` pins them as refused; its help review covers
  `showalert` only.
- **R3.** The reads are `showdate`, `showalert -d` and `showsys -space`, in that order. No System
  Reporter read is sent for the as-built.
- **R4, *Before this run*.** The array's UTC offset comes from `showdate`'s time against the moment of
  the read, to the nearest quarter hour (ADR 0019 change 5, updated). With `showdate` not read, the column
  says *unknown*, the section names the failed read and the as-built has a warning.
- **R6 and R7.** Removed: no window, no CPU, port or volume table, no performance or idle sentence, no
  Remote Copy figures.
- **R9.** The Heading 1 is *Array status at handover*, with subsections *Alerts* and *Capacity* and the
  two closing lines.
- **R10.** `handover` in `asbuilt.generated` is `{read_at, alerts_new, alerts_major, oldest_alert,
  cloud_alert, read_errors}`: `window_from`, `window_to`, `cpu_max_pct`, `iops_avg` and `idle` are gone.
  The page's *Status at handover* block shows the alert verdict, the cloud sentence and the failed-read
  count only.

The System Reporter captures stay in `tests/fixtures/handover/` for the record; their parsers and tests
were removed with the feature.

## 1. Problem

The as-built shows the array's `checkhealth` and inventory, but not its **alerts**, its **capacity
in use**, or any **performance** figure. A field engineer handing an array over cannot say "no open
alerts, CPU idle, ports quiet, this is the baseline" without opening a CLI session and pasting
output into the document by hand. LESSONS 24 shows the risk of doing it badly: alerts without
their timestamps sent a team after a fault repaired four days earlier.

## 2. Requirements

**R1 — Four more read commands.** `ALLOWED_COMMANDS` gains `showalert`, `srstatcpu`, `srstatport`
and `srstatvv`, by exact base name. `srstatrcvv` stays off until rows from a started Remote Copy
group are captured (R7; ADR 0019 change 4). `tests/unit/test_cli_allowlist.py` pins two things:

- *No option acts (LESSONS 46; in the file now, it reads only fixtures).* For `showalert`,
  `srstatcpu`, `srstatport`, `srstatvv` and `srstatrcvv`, it reads the option names from the
  captured `help_*.txt` on all four arrays and fails on any option not in its reviewed read-only
  list, where each option is marked as one that filters, windows, sorts or formats. It also checks
  AUTHORITY says "Any role in the system". No option acts, so none needs refusing in the client.
- *The allowlist (step 2).* Each of the four is allowed; `srstatrcvv`, `statcpu`, `statport`,
  `statvv`, `setsr`, `startsr`, `stopsr`, `createsralertcrit`, `setalert` and `removealert` are
  refused.

ADR 0001 gains an addendum naming the four. The pull request says plainly that the allowlist grew.

**R2 — Captures before parsers.** A read-only script `lab/handover_capture.py` (copy
`lab/rcip_pair_capture.py`) saves, for each lab array it is pointed at, into
`tests/fixtures/handover/<array>/`: `help showalert`, `help srstatcpu`, `help srstatport`,
`help srstatvv`, `help showsys`; then each command in R3 exactly as the tool will send it; and
`showalert -d` (the form seen live in LESSONS 24). At least one capture comes from an array with
an open alert and one from an array with host I/O, if the lab has them; the README says which.
The command forms in R3 are the captured ones (§2a); where a later capture's help disagrees, the
help wins and this spec is corrected in the same pull request.

**R3 — The reads.** In the as-built step, after the existing reads, over the same SSH session and
credential, each with its own error capture (SPEC-002 R6):

| Key | Command (as captured) | When |
|---|---|---|
| `alerts` | `showalert -d` | always |
| `space` | `showsys -space` | always |
| `cpu` | `srstatcpu -hires -btsecs -24h -groupby NODE -summary min,avg,5%,95%,max,per_group` | always |
| `ports` | `srstatport -hires -btsecs -24h -port_type host,iscsi -groupby PORT_N,PORT_S,PORT_P -summary avg,95%,max,per_group` | always |
| `volumes` | `srstatvv -hires -btsecs -24h -summary avg,95%,max` | always |

**Every form above answered**, none refused, each in under a second: the first `cpu` and `ports`
forms on rack13-ARCUS (OS 10.6.0, 2026-11-16), and all of them, the corrected `cpu` and `ports`
included, on D22U27, E18U31 and VZ (OS 10.5.0, 10.5.60, 10.5.51, 2026-11-17; §2a). The `cpu` and
`ports` rows above are the corrected forms, confirmed by that capture: `cpu` gained `min` and `5%`
(§2a correction 2), `ports` became `-port_type host,iscsi` (correction 3). `alerts` stays
`showalert -d`, the array's New alerts (R4; ADR 0019 change 7). `showsys -space` needs no allowlist
change (`showsys` is already on it), and neither does `showport`, which the as-built already reads
and R6 uses for the ports' state. The window is the 24 hours before the read; when the array has
been running for less, System Reporter returns what it has and the section says from when.

Not read in the first slice: `rcvv`, `srstatrcvv -hires -btsecs -24h -groupby GROUP_NAME -summary
avg,max,per_group` (R7). It answered on all four arrays, but no capture has a started group.

**R4 — New alerts.** Parsed from `showalert -d` into rows: id, state, severity, time (the latest
occurrence), first occurrence (the `Repeat Count` line, else `Time`; §2a), message code, message.
`showalert -d` lists the array's **New** alerts only; acknowledged and fixed alerts are not read
(ADR 0019 change 7), and the section calls them *New alerts*, never *open alerts*.

- *Verdict.* One sentence above the table: *"No new alerts."* or *"N new alerts; the oldest first
  occurred on <date>. Alerts record an event, not the current state: compare each with checkhealth
  before acting."*
- *Cloud connection (ADR 0019 change 3).* When a New alert has message code `0x060000a` (Major,
  *"Storage system has been disconnected from Data Services Cloud Console for more than N
  minutes"*; on rack13, D22U27 and VZ, OS 10.5.0, 10.5.51 and 10.6.0), the verdict adds *"The array
  reports it is disconnected from Data Services Cloud Console (alert <id>)."* and R9's cloud line
  says the same.
- *The table (§2a item 10, the owner's answer).* Every alert of severity Major, Critical or Fatal in
  full, newest first, with a column *Before this run*. The rest grouped by message code and
  severity, one row per group: count, first and latest occurrence, one sample message. Under the
  table: *"The full list is on the array: showalert -d."* The command log keeps 64 KB of each output
  (R11) and D22U27's list is 176 KB. On the captures: rack13 5 rows in full and 2 groups, D22U27 4
  and 1 (521 Minor task failures), VZ 8 and 3.
- *Before this run.* Yes when the alert's **first** occurrence is earlier than the run's creation
  (`Time` is the latest occurrence, §2a). Alert times carry only a zone abbreviation (`IST`). The tool
  converts them with the array's UTC offset, taken from the first System Reporter report that parsed
  (R6): its `Start Time` line prints the local time and the epoch (`2026-11-16 00:05:18 IST
  (1794767718)`: +05:30). Never from the abbreviation, and never through `zoneinfo`: the project
  ships no `tzdata`, so the Windows exe has no zone database (ADR 0019 change 5). With no System
  Reporter report read, the column says *unknown* on every row. (In a zone with daylight saving the
  offset is the one at the read; an alert first seen in the other season is an hour off, which
  changes the answer only within an hour of the run's creation.)
- *Warnings.* An alert of severity Major, Critical or Fatal (the array's words, from the capture)
  adds an as-built **warning** naming it; it never blocks the document.

The tool runs no alert command other than `showalert`; the section may name `setalert` and
`removealert` as the operator's commands to acknowledge or remove one.

**R5 — Capacity.** From `showsys -space`: total, allocated, free, and data reduction where the
array prints it, in TiB with one decimal and the array's own figure beside it. The exact lines are
taken from the capture.

**R6 — Performance.** Three short tables, each with average, 95th percentile and maximum over the
window: per controller node CPU (% busy: 100 minus Idle%; the busiest sample from the minimum Idle%,
95 % busy from the 5th percentile, §2a correction 2); per host port (FC and iSCSI) IOPS, throughput
(MB/s) and service time (ms); the whole array's volume IOPS, throughput and service time. Above the
tables: the window (from, to, sample interval), then always the sentence *"These figures are the
load seen in this window, not what the array can do."* (ADR 0019 change 2). When the host ports'
summed average IOPS is below 10 (`IDLE_IOPS`, a named constant), a second sentence: *"The array
carried almost no host I/O in this window: an idle baseline for later comparison."* At or above
`IDLE_IOPS` there is no second sentence: E18U31 at 26.3 IO/s is not idle, and its figures are still
no baseline worth quoting. (The idle rule uses the host ports, not the volumes: on rack13 the volumes
averaged 27.6 IO/s of the array's own I/O with no host I/O at all, §2a.)

*The port table (§2a item 9, the owner's answer).* One row per port that `showport` (already read by
the as-built) reports `ready`. The other ports System Reporter printed are named in one line under
the table, never dropped silently: their count, protocol, state in words and whether they carried
I/O in the window, e.g. *"4 iSCSI ports not configured, no I/O: 0:4:1, 0:4:2, 1:4:1, 1:4:2."* (VZ's,
`offline` with type `free` in `showport`). The idle sum counts every port printed.

No figure is ever written as `0` for a read that failed: a failed read is named (R8).

**R7 — Remote Copy (not in the first slice).** Built after rows from a started group are captured;
`srstatrcvv` joins the allowlist then (ADR 0019 change 4). With a Replication tab, placed in the
replication section next to SPEC-020's link check paragraph (§2a item 8, the owner's answer):
figures (local and remote IO/s and service time) only for groups `showrcopy` reports `Started`;
every other group named with its state in words, without figures; no RPO column (it prints `-`, `0`
or a date, §2a item 7, and a row means samples, not replication, item 8). Absent without a
Replication tab.

**R8 — Failed and unknown reads.** A command refused, timed out or unknown on this OS is recorded in
`AsBuiltData.read_errors` and shown in its subsection as *"Could not read: <command> — <the array's
words>"*, plus an as-built warning, exactly like SPEC-002 R6 (built with SPEC-002's own line, ``
`<command>` could not be read: <the array's words> ``, and its warning; the packet says reuse it). A
read whose text the parser cannot read (the array's refusal, or nothing) counts as failed the same way. The other subsections still render.
A report with no rows (no host ports, nothing in the window) says so in a sentence without a warning.

**R9 — The document section.** A new Heading 1 *Array status and performance at handover*, placed
after the `checkhealth` section (matched by intent like the others), with subsections *Alerts*,
*Capacity*, *Performance*, and two last lines: *"This section was read from the array at <time>."*
and the cloud line (ADR 0019 change 3):

- with a New `0x060000a` alert: *"Cloud connection: the array reports it is disconnected from Data
  Services Cloud Console (alert <id>: "<the array's message>"). The tool did not read HPE's cloud
  view of this array (call-home)."*
- without one: *"Cloud connection: the array has no New alert about it. The tool did not read HPE's
  cloud view of this array (cloud connection, call-home)."*
- with the alerts not read (R8): *"Cloud connection: unknown, the alerts could not be read. The tool
  did not read HPE's cloud view of this array (cloud connection, call-home)."*

HPE house-style tables (`asbuilt_docx.hpe_table`).

**R10 — Event and page.** `asbuilt.generated` data gains `handover`: `{read_at, window_from,
window_to, alerts_new, alerts_major, oldest_alert, cloud_alert, cpu_max_pct, iops_avg, idle,
read_errors}` (`cloud_alert`: the id of the `0x060000a` alert, or null). The As-built step page
shows, once generated, a *Status at handover* block: the alert verdict with its cloud sentence
(status indicator with colour, icon and words), the window, peak CPU, average IOPS, the performance
sentence always, and the idle sentence when `idle`. No UI string says *health* (UX-GUIDELINES §4);
the word is *status*.

**R11 — Console.** Every command in R3 appears in the command log and the as-built appendix like
any other read (SPEC-019). Nothing to add: the reads go through the same client. The log keeps the
first 64 KB of each output (`command_log.MAX_OUTPUT_BYTES`), so a long alert list is cut there: one
reason R4 points to `showalert -d` on the array.

**R12 — Retention.** No new artifact. The figures live in the docx and the event, both already
bounded (LESSONS 9).

## 2a. What the captures showed

### First capture: OS 10.6.0, 2026-11-16

`lab/handover_capture.py`, read-only, on **rack13-ARCUS, OS 10.6.0, 2026-11-16** (HPE Alletra
Storage MP B10230, two nodes; files in `tests/fixtures/handover/rack13/`, pinned by
`tests/unit/test_handover_parse.py`). Nine New alerts, no host I/O, no Remote Copy group. "Confirmed"
below means confirmed on that array, that OS and that date.

**Confirmed**

- *Commands.* All six forms then in R3 (the `srstatrcvv` one is now R7's), `showalert` and
  `checkhealth -svc -detail` answered; none refused.
  The `help` of `showalert`, `showsys` and the four `srstat*` reports says "Any role in the system".
- *Alerts (R4).* Blocks of `Key : Value` lines, one blank line between, closed by `9 alerts`. Plain
  `showalert` prints Id, State, Message Code, Time, Severity, Type, Message; `-d` adds Component,
  Tier, Maintenance, Spare_PN (hardware alerts) and, for a repeating alert, `Repeat Count: Occurred
  240 times, first at 2026-11-11 23:54:31 IST`. Time is printed in the array's zone abbreviation
  (`IST`) with no offset. Severity words seen: Critical, Major, Degraded, Informational. Without
  options `showalert` lists New alerts only (help). `checkhealth`'s Alert detail rows are the same
  nine alerts (identifier = Component, description = Message) without time or severity.
- *Capacity (R5).* `showsys -space` prints three sections: `Raw Capacity (MiB)`, `Usable Capacity
  (MiB)`, `Efficiency` (ratios). Lines are `Key : value`, nested by a two-space indent, and key
  names repeat across sections (`Total`, `Free`, `Metadata`). Raw `Total`, `Usable > Allocated`,
  `Usable > Free` equal `showsys`'s TotalCap, AllocCap, FreeCap. Usable has `Total`, `Used`, `Free`.
  Efficiency prints `Reduction 8.46` and can print a bound, not a number (`Total : >25`).
- *System Reporter (R3, R6, R7).* A `-summary` report prints `Start Time: <local> (<epoch>)`,
  `End Time: … (<epoch>)`, an optional row of dashed group headings, a `Summary <groupby…>
  <columns…>` line and one row per statistic and group. The start is the read time minus 24 hours to
  the second; the end is the last 5-minute sample. The epoch in brackets gives the window in UTC with
  no zone parsing. The array prints the statistics in its own order (Avg, Max, then 95%, with two
  decimals) whatever order `-summary` asked for. Columns: CPU `User% Sys% Idle% Intr/s CtxtSw/s`;
  ports and volumes `IO/s`, `KBytes/s`, `Svct ms`, `IOSz KBytes` (each Rd Wr Tot), `QLen`,
  `AvgBusy%`; Remote Copy `IO/s` and `KBytes/sec` (Lcl Rmt), `Svct(ms)` (Lcl Rmt), `IOSz KB` (Lcl),
  `RPO`. With no Remote Copy group the `srstatrcvv` summary has no rows and `End Time: 1970-01-01
  05:30:00 IST (0)`: epoch 0 means no sample, not a time. The plain forms (no `-summary`) print one
  row per sample (12 hours of 5-minute samples by default) and are not what the tool reads.

**Contradicted, with the correction**

1. *Idle (R6).* The whole array's volumes averaged **27.6 IO/s** (max 104.9) while the four host
   ports averaged **0.0**: `srstatvv` counts the array's own volumes. The idle rule now uses the host
   ports' summed average (R6 corrected above). The volume table stays, with the figures as printed.
2. *CPU busy (R6).* There is no Busy% column, and each column is summarised on its own: node 1's
   Max row has Idle% 92.8, the *most idle* sample. Busy average is 100 − Avg Idle% (7.8 % and
   7.5 %), but the busiest sample needs the **minimum** Idle% and the 95th percentile of busy needs the
   **5th** percentile of Idle%. Proposed form (help confirms `min` and any `<N>%`):
   `srstatcpu -hires -btsecs -24h -groupby NODE -summary min,avg,5%,95%,max,per_group`. With the
   first form the parser leaves busy max and busy 95 % unknown, never guessed. **Confirmed
   2026-11-17** on OS 10.5.0, 10.5.51 and 10.5.60, now in R3 (second capture below).
3. *Host ports (R3).* The help says `-port_type host` is "Host Fibre channel port" only; iSCSI host
   ports are `iscsi`. Proposed: `-port_type host,iscsi`. rack13's four rows are FC ports. **Confirmed
   2026-11-17**, now in R3: on E18U31 it adds four iSCSI ports that carry most of its host I/O.
   *Corrected 2026-11-17 (build):* rack13's four rows were not all FC. Its `showport` from 23:20 IST
   the same night (`tests/fixtures/peer_ports/rack13/`, BL-26) has 0:3:4 and 1:3:3 as FC host ports and
   0:4:1 and 1:4:1 as iSCSI host ports: on OS 10.6.0 `-port_type host` printed iSCSI host ports too,
   against its help. The R3 form asks for both types anyway.
4. *Alerts not fixed (R4).* `showalert -d` shows New alerts only, so Acknowledged alerts are not in
   the table. Either R4 says "New alerts", or the form becomes `showalert -all -d` (includes Fixed;
   the parser keeps State so they can be dropped). Owner's choice; capture the form first.
   **Answered 2026-11-17:** R4 says "New alerts"; the read stays `showalert -d`, `-all` is dropped.
5. *Before this run (R4).* `Time` is the latest occurrence: alert 40's Time was the capture minute,
   its first occurrence five days earlier. *Before this run* uses the first occurrence (R4 corrected).
   The alert times carry only a zone abbreviation; comparing them with the run's creation time needs
   the array's zone (`showdate` prints `(Asia/Kolkata)`). **Answered 2026-11-17:** the UTC offset
   comes from a System Reporter `Start Time` line (local time and epoch), not from the zone's name
   or abbreviation, since the project ships no `tzdata`; with no System Reporter read, *unknown* (R4).
6. *All-zero case (§4).* `tests/fixtures/rc_pair/D22U27/srstatrcvv_hourly.txt` is a time series,
   not a summary; the summary parser refuses it rather than read it as an idle array. The all-zero
   summary is rack13's `srstatport_24h.txt`; the empty one is its `srstatrcvv_24h.txt`.

### Second capture: OS 10.5.x, 2026-11-17

The same script, now also sending the corrected forms (saved as `*_24h_v2.txt`), on three lab
arrays: **D22U27** (OS 10.5.0, 525 New alerts, host I/O on FC), **E18U31** (OS 10.5.60, renamed
`DHCI_B10K`, no alert, host I/O on iSCSI) and **VZ** (OS 10.5.51, the lab's CRV Vault Zone, 31 New
alerts, two Remote Copy groups). Files in `tests/fixtures/handover/<array>/`, each with a README;
pinned by `tests/unit/test_handover_parse.py`. 0 FAIL on all three; all ten System Reporter forms
answered on each. The fourth lab array (LZ) did not answer on SSH.

**Confirmed**

- *The corrected forms.* `srstatcpu … -summary min,avg,5%,95%,max,per_group` and `srstatport …
  -port_type host,iscsi …` answered on all three. The CPU report adds `Min` and `5%` rows; the parser
  gives busy average, 95 % busy and the busiest sample per node (D22U27: 3.5, 3.5, 6.0 % on node 0).
  The rows both CPU forms print are the same figures.
- *Host and iSCSI ports.* On E18U31 `-port_type host` prints four FC ports, 2.7 IO/s together:
  *idle* by R6. `host,iscsi` adds its four ready iSCSI ports, 26.3 IO/s together: *not idle*.
  Correction 3 changes the verdict on a real array. On D22U27 (no iSCSI port) both forms print the
  same five FC ports, 44.2 IO/s together: the first capture with host I/O.
- *No alerts (R4).* An array with no alert prints exactly `no alerts`, one line, for `showalert` and
  `showalert -d` alike (E18U31, 10.5.60). The parser now accepts only that line as "no alerts"; any
  other words are an unreadable report. (Not yet seen on 10.6.0.)
- *A long alert list (R4).* D22U27's 525 alerts (4201 lines plain, 5255 with `-d`) parse in full and
  match `checkhealth`'s Alert rows one for one. VZ's 31 too.
- *Before this run (R4, item 5) again.* D22U27's alert 10 (Major, disconnected from DSCC) has a
  `Time` 13 minutes before the capture and `Occurred 2285 times, first at 2025-12-26 21:11:20 IST`.
  Without `-d` it would look new.
- *The empty Remote Copy summary.* D22U27 (six groups, none started) and E18U31 print no row and an
  `End Time` of epoch 0, as on rack13.

**OS 10.5.x and 10.6.0: what differs**

- `showalert`: the same blocks, keys and `N alerts` line. `-d` printed a `Maintenance` key only on
  rack13 (iLO alerts); `Spare_PN` and the `Repeat Count` line (before `Time`) appear on both. The
  severity `Minor` appears on 10.5.x (scheduled-task failures). On all four arrays the alerts are
  printed by `Time` (latest occurrence), oldest first, not by Id. The 10.5.x `help showalert` adds an
  example output; the options (`-n -a -f -all -d -oneline -svc -wide`) are the same.
- `showsys -space`: 10.5.x prints three more lines under Raw > Usable > Free (`VV Preallocated`,
  `CPG Preallocated`, `Unallocated`); the lines R5 reads are the same. An efficiency figure can be
  `-` (VZ `Dedup`) as well as `>25`. The 10.6.0 help adds `-block` and `-fileservice` (not used).
- `srstat*` summaries: the same layout on both. With `min` and `5%` the array prints Avg, Max, Min,
  then the percentiles group by group (`5%` and `95%` for node 0, then node 1). The 10.6.0 help adds
  the `file` port type to `srstatport` and the `AGID` group to `srstatvv`; `srstatcpu` and
  `srstatrcvv` help are identical.
- `showdate`: the same zone under two names, `Asia/Calcutta` (D22U27, E18U31) and `Asia/Kolkata` (VZ,
  rack13). The tool does not read the zone's name (item 5's answer), so both are fine.
- `checkhealth -svc -detail`: the same tables; the existing parsers read all three.

**Contradicted or new, with the correction**

7. *RPO (R7).* `srstatrcvv`'s RPO prints `-`, `0` or a date and time with a space in it (VZ
   `Recover_back`: `2026-07-20 13:11:32`). The parser split rows on spaces and refused that row. It
   now lets the last column, RPO, take the rest of the row; any other row with too many fields is
   still refused.
8. *Remote Copy rows (R7).* VZ's two groups are not started and their target has failed, yet both
   have rows: a row means System Reporter has samples, not that the group replicates. Samples come
   only when there is activity (33 in 12 hours, around a four-hourly task), so `Avg` is over those
   samples, not the 24 hours. **Answered 2026-11-17:** figures only for groups `showrcopy` reports
   `Started`, the others named with their state in words, no RPO; built after a started group is
   captured, outside the first slice (R7).
9. *iSCSI ports with no host (R6).* `-port_type iscsi` lists every iSCSI port, configured or not: VZ's
   four offline, unconfigured iSCSI ports print all-zero rows. They add nothing to the idle sum.
   **Answered 2026-11-17:** the table lists the ports `showport` reports `ready` and names the rest
   in one line (*"4 iSCSI ports not configured, no I/O"*), never dropping one silently (R6).
10. *Alert table size (R4).* R4 lists every open alert. D22U27's 525 (521 of them one Minor task
    failure repeating) would be pages of rows. Owner's choice before step 5: list all, or group by
    message code with a count and list Major and above in full. **Answered 2026-11-17:** Major,
    Critical and Fatal in full; the rest grouped by message code and severity with count, first and
    latest occurrence and one sample; a pointer to `showalert -d` on the array (R4). The command log
    keeps 64 KB of each output, and D22U27's `showalert -d` is 176 KB.

**Not captured yet:** Remote Copy rows from a started group (the lab pair's groups are not started;
LZ did not answer; needed before R7 and `srstatrcvv`); an older OS refusing a command (R8); `no
alerts` on 10.6.0; `showport` on the night of a handover capture (R6's port rule can be pinned on
E18U31's `rc_pair/E18U31/showport.txt` of 2026-10-07, where its four iSCSI ports are `ready`; VZ's
offline ones have no committed `showport`). The first-slice live run (§5) confirms the second and
third. *Update 2026-11-17 (build):* BL-26's peer-port captures took `showport` on all four arrays the
same nights (`tests/fixtures/peer_ports/<array>/showport.txt`: rack13 at 23:20 IST on 2026-11-16, the
other three on 2026-11-17). R6's port rule is pinned on them: VZ's four iSCSI ports are `offline`
with type `free` there, and the section names them in one line.

## 2b. How the first slice was built (2026-11-17)

Work packet BL-24 steps 2 to 7. Choices the requirements left open, made in the build:

- *Where.* `application/documents/handover.py` holds the reads (`READS`, the R3 forms), the parsers,
  the summary and the sentences; `asbuilt.py` renders the section (`_add_handover_section`) right after
  the `checkhealth` section, before SPEC-002's sections; `documents/steps.py` makes the reads. The
  section is left out only when the reads were not made at all (`handover_read_at` unset), which the
  as-built step never does.
- *R4.* "Newest first" is by the alert's `Time` (its latest occurrence). The grouped rows are ordered
  the same way, by each group's newest occurrence. The section names `setalert` and `removealert` as
  the operator's commands after the pointer to `showalert -d`. One warning per Major, Critical or Fatal
  alert, naming its id, severity, first occurrence and message.
- *R5.* Both the raw and the usable lines: raw total, allocated and free (equal to `showsys`'s
  columns), usable total, used and free, each in TiB with the array's MiB beside it; data reduction as
  printed (`8.46`, `>25`).
- *R6.* The performance sentence is printed whenever one System Reporter report was read: with none,
  there is no figure for it to qualify, and each report's failed-read line stands alone. Each cell
  of the port and volume tables is average / 95th percentile / maximum; MB/s is KBytes/s over 1024.
  `idle` and the host I/O figure are unknown (null), not false or 0, when the port report was not
  read or printed no port (no host port, or no sample in the window): no sample is not an idle window. A port missing from
  `showport` is named as "not listed by showport"; a port of type `free` reads "not configured".
- *R9.* The read time is printed in UTC and, when the offset is known, on the array's clock with its
  offset (`2026-11-17 00:10 on the array's clock, UTC+05:30`).
- *R10.* `window_from`, `window_to` and `read_at` are ISO times in UTC (the page shows them in the
  browser's zone); `oldest_alert` is the array's own text (`2025-12-26 21:11:20 IST`).
- *Page.* A folded section *Status at handover*, open once generated. It says "the array's status
  check" where the document says `checkhealth`: the word *health* stays off the screen.

## 3. Non-goals

DSCC reads (HPE's view of the cloud connection, call-home, DSCC issues, DSCC performance history):
slice 2, after a read-only probe settles the permissions, system id and regional host (research §6).
Remote Copy figures (R7) and `srstatrcvv`: a later slice, after a started group is captured.
Acknowledged and fixed alerts (`showalert -all`). Wellness events
and InfoSight. The onboard Prometheus exporter. Live samplers (`stat*`). Acknowledging, fixing or
removing alerts. A performance *test* (load generation). Per-volume or per-host performance tables.
Trends across runs. Showing alerts on the Verify page (a later slice may move the alert table
there).

## 4. Verification

Unit, all on R2's captures: the help review and the allowlist pins (R1); `showalert -d` parsed
(count, fields, the Major warning; E18U31's `no alerts` as an empty list; D22U27's 525 in full);
the alert table (rack13 5 rows in full and 2 groups, D22U27 4 and 1, VZ 8 and 3); the cloud
sentence and line from `0x060000a` on rack13, D22U27 and VZ, and without it on E18U31; the UTC offset
from a `Start Time` line (+05:30 on every capture) and *Before this run* against a fixed run time,
*unknown* with no System Reporter read; `showsys -space` parsed on 10.5.x and 10.6.0; each `srstat*`
summary parsed (avg, 95 %, max per group, and min and 5 % for CPU; the performance sentence on every
array and the idle sentence below `IDLE_IOPS` and not above it, with E18U31's FC-only and
FC-plus-iSCSI port forms on either side; the ready ports in the table and the rest in one line;
rack13's `srstatport_24h.txt` as the all-zero case; a time-series report such as
`rc_pair/D22U27/srstatrcvv_hourly.txt` refused, §2a); a refused or unknown command gives the named
line and a warning while the other subsections render; the docx has the heading after `checkhealth`
and no `0` where a read failed; `asbuilt.generated` carries `handover`. The Remote Copy parser tests
stay, for R7 later.
Frontend: `tsc` clean.

## 5. Live-run checklist

Read-only on the array; ask the owner before running.

1. `lab/handover_capture.py` against the lab arrays: every command in R3 answers; the help files
   saved; no command refused by the array. **Done for rack13-ARCUS, OS 10.6.0, 2026-11-16** (0 FAIL,
   8 of 8 System Reporter forms answered). **Done for D22U27, E18U31 and VZ, OS 10.5.x, 2026-11-17**
   (0 FAIL, 10 of 10 forms each, the corrected forms included; host I/O and Remote Copy rows seen).
   Still to run, for R7 only: a started Remote Copy group.
2. A run in *Verify only* mode on a lab array; generate the as-built from the page.
3. The console shows the five new reads (`showalert -d`, `showsys -space` and the three System
   Reporter reports), nothing else new, no write.
4. The document: the new section after `checkhealth`; the alert table matches `showalert -d` typed by
   hand in *Open terminal* (Major and above in full, the rest grouped); *Before this run* correct for
   at least one alert; the window matches the clock; the performance sentence present, and the idle
   sentence on an idle array; the cloud line matches the array's DSCC alert, or its absence.
5. The page: *Status at handover* shows the same counts as the document; no "health" on screen.
6. An OS 10.6.0 array with no New alert: it prints `no alerts`, and the section says *No new
   alerts*.
7. One read refused by an array on an older OS: the named line and a warning, the rest of the
   section present.
8. Validation record in `docs/validation/` with the run id, and the capture files committed.

## 5a. Size

Allowlist and tests (~30 lines, plus the help review already in), `handover.py` parsers and summary
(~250), reads (~30), as-built section (~170), event field (~15), page block (~70), capture script
(~80), ~30 unit tests.
