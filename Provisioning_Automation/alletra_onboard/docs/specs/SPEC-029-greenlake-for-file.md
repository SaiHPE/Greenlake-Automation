# SPEC-029 — GreenLake for File: the file system check (read-only, first slice)

**Status:** DEFERRED 2026-11-17 (owner's decision; proposed 2026-11-16), not built. No X10000 in
any lab, no `file-storage.*` permissions for the workspace's API client, and the File Storage API is
v1alpha1 (*"No guarantees on backward compatibility"*, HPE's versioning guide). The reasons and the
conditions to reopen are in ADR 0022 *Deferred* · **Decision:** [ADR 0022](../adr/0022-greenlake-for-file-system-type.md)
(deferred) · **Research:** [2026-11-16-greenlake-for-file.md](../research/2026-11-16-greenlake-for-file.md) ·
**Tracker:** BL-29 · **Brief:** [workpackets/BL-29.md](../workpackets/BL-29.md) · **Lab:** none yet
(needs an X10000 in a GreenLake workspace, §5)
**Owner:** `adapters/greenlake/storage_fleet.py`, `adapters/greenlake/file_storage.py`,
`application/onboarding/clients.py` (regional client), `application/filestorage/check.py`,
`domain/filestorage.py`, `cli/main.py` (`file-check`)

## 1. Problem

SCOPE area 7 has no code. The GreenLake File Storage API (v1alpha1, 2026-September) now manages
filesystems and shares on the Alletra Storage MP X10000 (devtype7), and Storage Fleet reads the
system itself. Nobody has called either from this tool, so we do not know what our API client is
allowed to read, which value joins the Devices inventory to the storage APIs, or what the answers
look like. Before any file step, sheet field or write is designed on top of them, one read-only
command proves the path end to end on a real system and captures the answers as fixtures.

The command also answers the field engineer's first question on a file system: *is it in the
workspace, assigned, subscribed and connected, and what is on it?*

## 2. Requirements

**R1 — The command.** `onboard file-check --serial <S> --region <R> [--json <file>] [--capture <dir>]`.
`<R>` is one of `us-west`, `eu-west`, `eu-central`, `ap-northeast` (the File Storage and Storage
Fleet endpoints); anything else is refused before any call with *"GreenLake file storage is served in
us-west, eu-west, eu-central and ap-northeast; <R> is not one of them."* GreenLake credentials come
from the same settings as `onboard check` (`GL_CLIENT_ID`, `GL_CLIENT_SECRET`, `GL_TOKEN_URL`);
missing ones print the same sentence as `check` and exit 2. No sheet, no run, no step in this slice.

**R2 — The regional client.** `make_regional_greenlake(settings, region)` in
`application/onboarding/clients.py` builds a `GreenLakeHttpClient` on
`https://<region>.api.greenlake.hpe.com` with the same token provider as `make_greenlake`. Two new
rate buckets, `fleet_read` and `file_read`, at the default 60 per minute (no published limit; the
value is a guess and says so in a comment).

**R3 — The reads, in this order, all GET.**
1. The token (as `check`).
2. Global: `GET /devices/v1/devices?filter=serialNumber eq '<S>'` (existing `find_by_serial`).
3. Global: `GET /service-catalog/v1/service-manager-provisions` (existing, unfiltered) and
   `GET /service-catalog/v1/per-region-service-managers` (existing) for the service's name.
4. Regional: `GET /storage-fleet/v1alpha1/devtype7-storage-systems`, every page (`limit=100`,
   `offset` until `total`).
5. Regional, for the matched system (R4): `GET /file-storage/v1alpha1/devtype7-storage-systems/<id>/filesystems`
   and `…/file-shares`, every page.

A read that fails stops only the reads that depend on it; the others still run and the report says
which were skipped and why.

**R4 — Which system is "this" one.** A Storage Fleet record matches when `<S>` equals its `id` or its
`logicalClusterSerialNumber` (case-insensitive, trimmed). The report says which field matched. No
match: a FAIL that lists every devtype7 system the client can see (`id`, `logicalClusterSerialNumber`,
`status.clusterName`), so the operator can tell a wrong serial from a missing system. More than one
match: a FAIL listing them; the command never picks one. (The join field is unconfirmed, research
§5; the live run settles it and this requirement is amended with the answer.)

**R5 — The checks.** Each has a status (PASS, WARN, FAIL, SKIPPED), one sentence saying what the API
returned, and, when not PASS, the next step.

| Check | PASS | WARN | FAIL |
|---|---|---|---|
| `token` | token fetched | — | the token endpoint's answer |
| `device` | the serial is in the workspace inventory, `deviceType` STORAGE | — | not in inventory: *add the device, or check the serial* |
| `assigned` | `assignedState` is `ASSIGNED_TO_SERVICE` | — | any other state, quoted |
| `service` | the device's `application.id` is a PROVISIONED service manager in the device's `region`; its name shown | the device's region differs from `<R>` (names both) | the application is not provisioned in that region |
| `subscription` | at least one subscription with an `endDate` in the future | ends within 90 days (date shown) | none applied, or all ended |
| `fleet_system` | one devtype7 system matched (R4) | — | none, or more than one |
| `connected` | `commonResourceAttributes.cloudState` is `CONNECTED` and `status.ready` is true | `status.ready` absent | any other `cloudState`, quoted with `errCode` and `errMessage` |
| `filesystems` | listed: count, then per filesystem `name`, `state`, `shareCount`, hard limit | a filesystem whose `state` is not `NORMAL` | the read failed |
| `shares` | listed: count, then per share `path`, `protocol`, `state`, `endPoint`, its filesystem, `accessClients` | a share whose `state` is not `ACTIVE` | the read failed |

A 401 or 403 from Storage Fleet or File Storage is a FAIL that names the permission the
documentation requires (`storage-fleet.storage-system.read`, `file-storage.file-system.read`,
`file-storage.file-share.read`) and says the workspace administrator grants it to the API client's
role. Any structured answer (401, 403, 404 with a body) means the service is reachable (LESSONS 27);
only a connection failure is *unreachable*, and that FAIL carries the proxy hint `check` prints.

**R6 — Output.** A table, one row per check, then the filesystems and shares. `--json <file>` writes
the report (the checks, the matched system, the lists) as JSON. Exit code 0 when no FAIL, 1 with any
FAIL, 2 for missing credentials or a refused region. The subscription key is never printed (`redact`).

**R7 — It changes nothing.** The service is built only from read clients; the adapters in this slice
have no method that sends POST, PUT, PATCH or DELETE. A test records every request a full check
makes and asserts each is a GET (the token request aside).

**R8 — Captures.** `--capture <dir>` writes each raw response body as
`<dir>/<nn>-<what>.json` (`02-device.json`, `04-fleet-systems-p1.json`, …) after removing
`customerId`, `tenantWorkspaceId`, `subscription[].key` and any e-mail address or phone number in
`status.supportContact`. The live run's captures go to `tests/fixtures/x10000_gl/` with a README of
the facts they show; the parsers' tests are re-pinned to them in the same pull request (rule 9). Until
then tests use payloads built from the documented schemas, and their names say *documented*.

## 3. Non-goals

Any write: device add, assignment, subscription, share create, system settings (later slices, ADR
0022 §5). A sheet field, a step in the registry, a UI page, a run (slice 2). Capacity and performance
history. devtype4 (Unified File, BL-28) — the adapter takes the device type, but this slice calls only
devtype7. The original GreenLake for File Storage product (no API). Rate limits beyond the default
bucket.

## 4. Verification

Unit and contract, all with fakes and documented payloads: the region refusal; the regional base URL;
each adapter's path, bucket and paging (two pages joined, `total` honoured); R4 with a match by `id`,
a match by `logicalClusterSerialNumber`, no match (the list printed), two matches; every R5 row in
each status it can take; a 403 naming its permission; a connection error versus a 404 with a body;
R7 (only GETs); R8 redaction (no `customerId`, no key, no e-mail in a capture); the CLI exit codes and
the JSON file. After the live run: the parsers pinned to the captures.

## 5. Live-run checklist

Before (the lab, not the tool):
- [ ] An X10000 with file enabled, connected to a GreenLake workspace in one of the four regions.
- [ ] An API client in that workspace; its role has device, subscription and service catalog read
      plus `storage-fleet.storage-system.read`, `file-storage.file-system.read`, `file-storage.file-share.read`.
- [ ] At least one filesystem and one share created by hand in the console's File Storage page; note
      their names and the share count.
- [ ] The system's serial number as the GreenLake Devices page shows it; the jump box reaches
      `global.api.greenlake.hpe.com` and `<region>.api.greenlake.hpe.com` (through the proxy if any).
- [ ] The owner has said yes to the run (AGENTS: ask before calling GreenLake).

The run:
- [ ] `onboard file-check --serial <S> --region <R> --json report.json --capture capture/` exits 0.
- [ ] Every R5 row is PASS; the filesystem and share names and counts equal the console's.
- [ ] The report says which field matched the serial (R4); write the answer into R4 and the research
      note §5.
- [ ] With the serial changed by one character: `device` FAIL with the sentence, `fleet_system` FAIL
      listing the visible systems, exit 1.
- [ ] With a role lacking `file-storage.file-system.read` (if the workspace admin can make one): the
      `filesystems` FAIL names that permission.
- [ ] The workspace's audit log shows no write by the API client during the run.
- [ ] Captures checked by eye for customer names, addresses and workspace ids, then committed under
      `tests/fixtures/x10000_gl/`; validation record `docs/validation/<date>-x10000-file-check.md`.

## 6. Size

Regional client and buckets (~25 lines), two adapters (~110), domain models (~60), check service
(~200), CLI command (~70), ~25 unit and contract tests. No frontend change.
