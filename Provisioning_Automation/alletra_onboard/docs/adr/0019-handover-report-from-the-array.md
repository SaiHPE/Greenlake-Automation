# ADR 0019 — The handover report is read from the array; DSCC adds what only the cloud knows, later

**Status:** accepted 2026-11-17 (owner's decision), with the changes below ·
**Proposed:** 2026-11-16 (BL-24) ·
**Amends:** ADR 0001 (the read allowlist gains `showalert`, `srstatcpu`, `srstatport` and `srstatvv`) ·
**Corrects:** ADR 0006 ("DSCC telemetry" listed as build-ready, verified: change 6) ·
**Narrows, for reports:** ADR 0006 (cloud primary) · **Keeps:** ADR 0012, ADR 0015 ·
**Research:** [2026-11-16-health-performance-reporting.md](../research/2026-11-16-health-performance-reporting.md) ·
**Spec:** [SPEC-026](../specs/SPEC-026-handover-status-and-performance.md) ·
**Work packet:** [BL-24](../workpackets/BL-24.md)

**Built 2026-11-17, pending live run** (work packet BL-24 steps 2 to 7): the four commands on the
allowlist with their tests and the ADR 0001 addendum; the as-built section and the page summary from
the array over the read-only client. Decision 5 (DSCC) and Remote Copy figures are later slices.

**2026-11-19: performance removed from the as-built at the owner's request** (after the customer demo,
BL-64). The section is *Array status at handover*: alerts and capacity only. No System Reporter read is
sent for the as-built; `srstatcpu`, `srstatport` and `srstatvv` left the allowlist (ADR 0001 addendum of
the same date), since nothing else read them. The page's block and the `handover` event data drop the
window, CPU, host I/O and idle fields. Change 5 now takes the array's UTC offset from `showdate` (already
on the allowlist) against the moment of the read, to the nearest quarter hour, still never from the
zone's name. Decision 2's System Reporter part, change 2, the idle baseline and the performance
consequences below are history.

## Changes on acceptance (owner, 2026-11-17)

The owner accepted the decision with the changes a review recommended. They are folded into the
sections below and into SPEC-026.

1. **No option of the five commands acts.** In the captured `help` of `showalert`, `srstatcpu`,
   `srstatport`, `srstatvv` and `srstatrcvv` on all four lab arrays (OS 10.5.0, 10.5.51, 10.5.60,
   10.6.0), every option filters, windows, sorts or formats, and AUTHORITY is "Any role in the
   system". Pinned as LESSONS 46 (BL-46) asks: `tests/unit/test_cli_allowlist.py` reads the option
   names from each `help_*.txt` and fails on any option not in its reviewed read-only list. It reads
   the fixtures only.
2. **The performance warning is always printed:** *"These figures are the load seen in this window,
   not what the array can do."* The idle sentence is added only below `IDLE_IOPS`. E18U31 is not idle
   at 26 IO/s, and its figures are still no baseline worth quoting.
3. **The array reports its own cloud connection.** rack13, D22U27 and VZ each carry the Major alert
   *"Storage system has been disconnected from Data Services Cloud Console for more than N
   minutes"* (message code `0x060000a`, on OS 10.5.0, 10.5.51 and 10.6.0). The first slice puts it in
   the alert verdict sentence and in the section's cloud line (SPEC-026 R4, R9).
4. **`srstatrcvv` and the Remote Copy rows (SPEC-026 R7) are out of the first slice.** `srstatrcvv`
   stays off the allowlist until rows from a started group are captured: no capture has one.
5. **Time zone from the array's own figures.** The project ships no `tzdata`, so `zoneinfo` fails in
   the Windows exe. The array's UTC offset comes from a System Reporter `Start Time` line, which
   prints the local time and the epoch (`2026-11-16 00:05:18 IST (1794767718)` is +05:30), never from
   the abbreviation `IST`. With no System Reporter read, *Before this run* says unknown.
   *Since 2026-11-19 (no System Reporter read):* from `showdate`'s time against the moment of the read,
   to the nearest quarter hour; with no `showdate`, *Before this run* says unknown.
6. **This ADR corrects ADR 0006,** whose Consequences list "DSCC telemetry" as build-ready
   (verified). That came from documentation; the tool has never called a DSCC telemetry endpoint
   (research §1, §2.3). Slice 2 makes the first call, after a read-only probe.
7. **Alerts are the array's New alerts.** The read stays `showalert -d`; `showalert -all -d` is
   dropped. SPEC-026 R4 says "New alerts".

## Context

SCOPE area 8 asks for status and performance reporting. Four sources exist (research §2): the
array over SSH (alerts and System Reporter history), the array's WSAPI and onboard Prometheus
exporter, DSCC's Storage Fleet, Block Storage and Data Services REST APIs, and InfoSight.

- The array is the only source the tool has already used live, needs no new credential, works with
  no internet, and keeps performance history from the moment it started. `srstatrcvv` was captured
  on OS 10.5.0 (BL-38 fixtures).
- DSCC has documented `GET` endpoints for overall state, call-home status, performance and capacity
  history and active issues, but none has ever been called by the tool. It needs Data Services read
  permissions on the user behind the API client (unconfirmed), a regional host built from a region
  the Verify-only mode does not know, and its performance series have an undocumented inner shape.
  At handover it holds at most a few hours of history.
- InfoSight has no public API for this array (research §2.4).
- At handover the array usually has no host workload. Any performance figure is an idle baseline.

ADR 0006 routes *report* to the cloud where entitled. Nobody has confirmed the entitlement, and
the one thing a handover document must not do is depend on a source we cannot prove at the customer
site.

## Decision

1. The first handover report is read **from the array, over the read-only SSH client**, inside the
   existing **as-built** step: a new document section *Array status and performance at handover*
   and a short summary on the As-built step page. No new step; the step registry is unchanged.
2. The read allowlist (`ALLOWED_COMMANDS`, ADR 0001) gains, by exact base name: `showalert`,
   `srstatcpu`, `srstatport`, `srstatvv`. Each is read-only (alerts list; System Reporter queries),
   and a test reads their captured `help` to show that no option acts (change 1). `srstatrcvv` joins
   only after a started Remote Copy group is captured (change 4). Live samplers (`statcpu`,
   `statport`, `statvv`) stay off: without `-iter` they never end. System Reporter writes (`setsr`,
   `startsr`, `stopsr`, `*sralertcrit`) stay off. A test pins both lists. The Console prompt gains
   the same four commands, since it uses this allowlist.
3. The tool never acknowledges, fixes or removes an alert (`setalert`, `removealert`). It may print
   those commands as text for the operator.
4. The WSAPI System Reporter path in `python-3parclient` (`getCPGStatData`) is not used: it returns
   zeros on any error.
5. DSCC is the **second** slice, for what only the cloud knows: HPE's view of the cloud connection,
   call-home status and DSCC's overall state for this array. It ships only after one read-only probe
   on the lab workspace has shown the permissions, the system id and the regional host work. Its
   client exposes `GET`s only.
6. InfoSight is not a source until HPE publishes an API.

## Consequences

- The report works on every run and every mode that reaches the as-built, with no new input.
- The performance part always says its figures are the load seen in the window, not what the array
  can do, and adds the idle sentence when the host ports were idle (change 2); never a silent zero.
- A section the array cannot fill (a report command refused or unknown on an older OS) is reported
  like any other failed read in the as-built (SPEC-002 R6): named in the section and the warnings.
- The cloud's view (is HPE receiving call-home data?) is missing from the first slice. The array's
  own alert about its cloud connection is shown (change 3); the document says in one line that the
  cloud's view was not read, rather than implying it was checked.
- *Before this run* needs one System Reporter read for the array's UTC offset (change 5).
- Remote Copy figures in the as-built wait for a capture of a started group (change 4).
- ADR 0001 gets an addendum in the build pull request naming the four commands.

## Considered options

- **DSCC first** (ADR 0006's default for reports): rejected for slice 1 on the unconfirmed
  permissions, region and series shape, and the empty history at handover. Kept as slice 2.
- **A new *Handover report* step:** rejected; it would read the same array the as-built step reads
  seconds later, and add a page and a registry entry for one document section.
- **Part of Verify configuration:** rejected for slice 1; Verify compares with the sheet and its
  page is the place to act on `checkhealth`. The alert list could join it later.
- **Live samplers (`statvv -iter 1` and friends):** rejected; one sample is noise, and an
  `-iter`-less command would hang the SSH read. System Reporter already summarises.
- **The onboard Prometheus exporter:** rejected as a requirement; it is off unless the customer
  enables it (a configuration change the tool will not make), has no history and no capacity.
- **`showalert -all -d`** (acknowledged and fixed alerts too): dropped on acceptance (change 7).
- **The array's zone through `zoneinfo`** (`showdate` prints `Asia/Kolkata` or `Asia/Calcutta`):
  rejected; it needs `tzdata`, which the Windows exe does not carry (change 5).
