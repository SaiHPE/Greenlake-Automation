# ADR 0019 — The handover report is read from the array; DSCC adds what only the cloud knows, later

**Status:** PROPOSED 2026-11-16 (BL-24), waiting for the owner's yes/no ·
**Amends:** ADR 0001 (the read allowlist gains `showalert` and four System Reporter report commands) ·
**Narrows, for reports:** ADR 0006 (cloud primary) · **Keeps:** ADR 0012, ADR 0015 ·
**Research:** [2026-11-16-health-performance-reporting.md](../research/2026-11-16-health-performance-reporting.md) ·
**Spec:** [SPEC-026](../specs/SPEC-026-handover-status-and-performance.md)

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
   `srstatcpu`, `srstatport`, `srstatvv`, `srstatrcvv`. Each is read-only (alerts list; System
   Reporter queries). Live samplers (`statcpu`, `statport`, `statvv`) stay off: without `-iter`
   they never end. System Reporter writes (`setsr`, `startsr`, `stopsr`, `*sralertcrit`) stay off.
   A test pins both lists. The Console prompt gains the same five commands, since it uses this
   allowlist.
3. The tool never acknowledges, fixes or removes an alert (`setalert`, `removealert`). It may print
   those commands as text for the operator.
4. The WSAPI System Reporter path in `python-3parclient` (`getCPGStatData`) is not used: it returns
   zeros on any error.
5. DSCC is the **second** slice, for what only the cloud knows: cloud connection, call-home status
   and DSCC's overall state for this array. It ships only after one read-only probe on the lab
   workspace has shown the permissions, the system id and the regional host work. Its client
   exposes `GET`s only.
6. InfoSight is not a source until HPE publishes an API.

## Consequences

- The report works on every run and every mode that reaches the as-built, with no new input.
- The performance part is honest only if it says when the array was idle; the spec makes that a
  sentence in the document, never a silent zero.
- A section the array cannot fill (a report command refused or unknown on an older OS) is reported
  like any other failed read in the as-built (SPEC-002 R6): named in the section and the warnings.
- The cloud's view (is HPE receiving call-home data?) is missing from the first slice. The
  document says so in one line rather than implying it was checked.
- ADR 0001 gets an addendum in the build pull request naming the five commands.

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
