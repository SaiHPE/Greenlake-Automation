# ADR 0022 — GreenLake for File is a second system type in the same tool, reached only through GreenLake APIs

**Status:** DEFERRED 2026-11-17 (owner's decision; proposed 2026-11-16). Nothing below is to be
built until the conditions in *Deferred* hold ·
**Research:** [2026-11-16-greenlake-for-file.md](../research/2026-11-16-greenlake-for-file.md) ·
**Spec:** [SPEC-029](../specs/SPEC-029-greenlake-for-file.md) · **Tracker:** BL-29 ·
**Builds on:** ADR 0005 (modes and the step registry), ADR 0006 (hybrid control plane, cloud first),
ADR 0007 (build profiles) · **Neighbour:** BL-28 / SPEC-028 (Unified File on the B10000)

## Deferred

The owner deferred this decision on 2026-11-17, as a review recommended. The reasons:

- **No X10000 in any lab**, so no slice could be run live (AGENTS rule 7) or pinned to a capture
  (rule 9).
- **No `file-storage.*` permissions** for the workspace's API client, so not even the read-only
  first slice (SPEC-029) can call the API.
- **The File Storage API is v1alpha1.** HPE's versioning guide says of alpha APIs: *"No guarantees
  on backward compatibility"*
  (developer.greenlake.hpe.com/docs/greenlake/guides/public/standards/versioning_basics, read
  2026-11-17).
- **Decision 1 ("GL4F = X10000") changes SCOPE area 7** without the field team agreeing. Which
  product the field team means, and whether the X10000 is the one they deploy, are research §10 Q1
  and Q2; both are unanswered.
- **The system type (decision 2) reaches the core**: `ArrayWorkItem`, sheet validation and the step
  registry would all change, with no live proof possible.

**Reopen when** all three hold: the field team confirms the product; an X10000 is connected to a
GreenLake workspace we may use; and the workspace's API client has the `file-storage.*` read
permissions. On reopening, item 6 follows ADR 0021 item 6: the two file items share the regional
HTTP client and paging only, not the share models (the devtype4 and devtype7 payloads differ).

SCOPE area 7 stays *Not started*.

## Context

SCOPE area 7 asks the tool to initialise and provision *HPE GreenLake for File*. The research found:

- The GreenLake API catalogue has, since 2026-September, a **File Storage** service (v1alpha1,
  regional base URLs, 201/202 + `Location`) for two device types: devtype4, the Alletra MP B10000
  (Unified File, BL-28), and **devtype7, the Alletra Storage MP X10000**. Storage Fleet reads and
  settings for devtype7 have been there since at least 2026-06.
- The original GreenLake for File Storage product, whose words (*views*, *view policies*) SCOPE
  area 7 uses, has no device type, storage tier or endpoint in the catalogue.
- GreenLake device onboarding (device add, the two PATCH calls, subscriptions, service catalog) is
  product-neutral and already built (Component A).
- The tool is built around one B10000 per run (AGENTS rule 4). Its sheet requires the B10000's
  setup-wizard fields; every step but *GreenLake registration* talks to a B10000 over SSH or WSAPI.

## Decision (proposed 2026-11-16, deferred 2026-11-17)

1. **"GreenLake for File" in this tool means a file system the GreenLake File Storage API manages
   as devtype7 (the X10000).** The original product is out of scope until a supported API for it is
   found; the tool will not drive its UI.
2. **Same tool, a second system type.** The workbook states the system type (`block` for the
   B10000, the default, or `file` for the X10000). The run carries it. **One system per run** still
   holds: an X10000 is one system however many nodes or serials it has; a workbook naming two
   systems is refused as today.
3. **Steps still come from the step registry.** File steps get their own `kind` (`file`); the
   registry offers a step only for the system types it applies to. A file run never shows
   *Cloud Connectivity*, *DSCC Setup*, *Discovery*, *SAN Zoning*, *Provision storage*,
   *Replication* or the SSH *Verify*. *GreenLake registration* is shared, behind a device-neutral
   work item. No step list is hardcoded in the UI.
4. **Cloud plane only.** Every file call goes through GreenLake (Devices, Subscriptions, Service
   Catalog, Storage Fleet, File Storage) with the workspace's API client. No SSH, REST or browser
   session to the X10000 itself, so no new allowlist.
5. **Read-only first.** The first slice only reads (SPEC-029). File Storage writes (share create,
   update, delete) are a new write path: they come later, each behind the plan → approve → apply gate
   with a removal set, and that release says so plainly and amends this ADR.
6. **One File Storage adapter for both file items.** `adapters/greenlake/file_storage.py` takes the
   device type (`devtype4` or `devtype7`) as a parameter; BL-28 and BL-29 share it and its read
   models. The regional GreenLake client is shared with Storage Fleet.

## Why

- A separate tool or fork (rejected in ADR 0005 and 0007 for the same reason) would duplicate the
  GreenLake auth, token refresh, polling, rate buckets, proxy and TLS handling, runs, console and
  packaging, which are most of the work and all already proven live.
- A build profile chooses what one artifact *hides*; it does not describe a different device. A
  field engineer with both products would need two downloads.
- Leaving area 7 out entirely ignores that the API is now public and small (22 operations).
- Cloud-only keeps rule 2's promise intact (no new device write path) and matches ADR 0006.

## Considered options

| Option | Verdict |
|---|---|
| Out of scope | rejected for the X10000; **kept** for the original product (no API) |
| New mode in the B10000 run (file steps after block steps) | rejected: that is BL-28's shape; an X10000 is a different system, so it would break one-system-per-run |
| Separate build profile or separate app | rejected (above) |
| **Second system type, registry-driven, cloud-only** | proposed |

## Consequences

- `ArrayWorkItem` splits into what every GreenLake device needs (serial, part number, subscription
  key, region, tags) and the B10000's setup-wizard fields; the sheet's complete-superset rule
  (ADR 0005 revision) becomes "complete for its system type".
- `StepDef` gains the system types it applies to; `/app/profile` serves it; `mode_steps()` is per
  system type.
- A regional GreenLake HTTP client next to the global one (`https://{region}.api.greenlake.hpe.com`).
- The workspace API client needs Storage Fleet and File Storage read permissions; that is an
  entitlement request, not code (ADR 0006 *gatekeeper*).
- Nothing about the block track changes. The default system type is `block`, and every existing
  workbook parses as before.
- "Done" for any file slice needs an X10000 connected to a GreenLake workspace we may use. The lab
  has none today.
