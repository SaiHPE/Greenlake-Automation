# Research — GreenLake for File (SCOPE area 7, BL-29)

**Date:** 2026-11-16 · **Status:** research. The decision it led to,
[ADR 0022](../adr/0022-greenlake-for-file-system-type.md), was deferred on 2026-11-17 (owner's
decision; the reasons are there), and with it the first slice in
[SPEC-029](../specs/SPEC-029-greenlake-for-file.md) and the build brief in
[workpackets/BL-29.md](../workpackets/BL-29.md)
**Sources:** the offline GreenLake API mirror (`reference/greenlake_api_docs/greenlake/`, scraped
2026-06-07), the live GreenLake developer portal (read 2026-11-16), the code as of v0.18.0 (main
`b7006373`). Nothing was called against GreenLake, DSCC or any device.

## 1. The question, and the short answer

SCOPE area 7 asks for *initialization, provisioning views, ACL configuration, policy configuration,
share migration* on "HPE GreenLake for File (GL4F)". The questions: how such a system is onboarded
into GreenLake, how much of that the platform APIs the tool already uses can do, what needs the file
product's own API or UI, and whether this belongs in a tool built around one B10000 block array per
run.

Short answer:

- **The name covers two products, and only one has a public API.** The GreenLake API catalogue
  gained a *File Storage* service in 2026-September (§3). It manages file shares and filesystems on
  two device types: **devtype4, the Alletra MP B10000** (that is Unified File, BL-28) and
  **devtype7, the Alletra Storage MP X10000**. The original GreenLake for File Storage product, the
  one whose vocabulary SCOPE area 7 uses (*views*, *view policies*), appears nowhere in the
  catalogue: no device type, no storage tier, no endpoint (§4).
- **GreenLake onboarding is product-neutral.** Device add, the two-PATCH assignment, subscriptions
  and the service catalog do not care whether the device is block or file (§5). The tool's existing
  Component A code can carry an X10000 once three facts are confirmed (part number, how many
  inventory devices one system is, which service manager it is assigned to).
- **What the cloud API does not cover** — AD/LDAP join, SMB ACLs, quotas, protection policies,
  migration, the first network setup of the system — needs the product's own UI or API, and none of
  that is publicly documented (§6).
- **Recommendation:** treat GL4F as the X10000 reached **only through GreenLake APIs**, as a second
  *system type* in the same tool (one system per run still holds), and start with a read-only
  check: is the system in the workspace, assigned, subscribed, connected, and what filesystems and
  shares it has (§8). The VAST-based product stays out until an API for it is found (§10, Q1).

## 2. Sources

| Source | Read | Used for |
|---|---|---|
| Offline mirror: `services.md` (API catalogue) | scraped 2026-06-07 | no File Storage service in June; Object Storage and Storage Fleet present |
| Offline mirror: `services/storage-fleet/public.md`, `…/storage-systems/systemslist.md`, `…/devicetype7getstorageclusters.md` | scraped 2026-06-07 | devtype4 = B10000, devtype7 = X10000; regional base URLs; permissions; `tierType` enum; X10000 cluster fields |
| Offline mirror: `services/device-management/…/devices-v1/getdevicesv1.md`, `…/devices-v2beta1/postdevicesv2beta1.md` | scraped 2026-06-07 | device fields (`deviceType`, `assignedState`, `application`, `region`, `subscription[]`); `deviceType` enum; subscription `tier` enum |
| Live: <https://developer.greenlake.hpe.com/docs/greenlake/services/file-storage/public> | 2026-11-16 | the File Storage service, endpoints, payloads, permissions |
| Live: <https://developer.greenlake.hpe.com/docs/greenlake/services/file-storage/public/openapi/changelog> | 2026-11-16 | one entry: *2026-September, v1alpha1, initial* (`file-shares`, `filesystems`, `share-settings`) |
| Live: <https://developer.greenlake.hpe.com/docs/greenlake/services/file-storage/public/openapi/file-storage-public-v1alpha1/file-storage-api> | 2026-11-16 | the 22 operations (12 devtype4, 10 devtype7) |
| Live: <https://developer.greenlake.hpe.com/docs/greenlake/services/file-storage/public/openapi/file-storage-public-v1alpha1/file-storage-api/file-systems/devicetype7filesystemslistbysystemid> | 2026-11-16 | the X10000 filesystem record |
| Live: <https://developer.greenlake.hpe.com/docs/greenlake/services/file-storage/public/openapi/file-storage-public-v1alpha1/file-storage-api/file-shares/devicetype7fileshareslistbysystemid> | 2026-11-16 | the X10000 share record; NFS 4.1 only |
| Live: <https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public> | 2026-11-16 | unchanged from the mirror for devtype7 |
| Code: `adapters/greenlake/*`, `application/onboarding/greenlake_provision.py`, `health.py`, `domain/workflow.py`, `config.py` | main `b7006373` | what the tool already does (§5) |

Tried and **not** usable on 2026-11-16: the hpe.com product pages for GreenLake for File Storage and
the X10000 (timed out twice), the GreenLake cloud user guide on support.hpe.com (`a00120892en_us`,
client-rendered, empty to a fetcher), the developer.hpe.com search and two web search engines (no
relevant result). Every fact below that is not in the table is marked *unconfirmed* and listed in
§10.

## 3. The GreenLake File Storage API (v1alpha1, 2026-September)

The portal describes it as *"a service in Data Services Cloud Console that handles file share and
filesystem lifecycle management."*

- **Base URL is regional**, not the global one the tool uses today: `https://us-west.api.greenlake.hpe.com`,
  `eu-west`, `eu-central`, `ap-northeast`. Same bearer token (*"Authentication"* guide). The tool's
  `GreenLakeHttpClient` has one base URL (`settings.gl_base_url = https://global.api.greenlake.hpe.com`),
  so it needs a second instance per region.
- **Permissions:** `file-storage.file-share.read|create|update|delete`,
  `file-storage.file-system.read|delete`, `file-storage.file-share-setting.read`.
- **Async:** *"For asynchronous operations that return HTTP status 201 or 202, use the Location
  header"* — the pattern `GreenLakeHttpClient.poll_async` already follows. The status words these
  operations return are not documented (unconfirmed).

| Operation | devtype4 (B10000, BL-28) | devtype7 (X10000, BL-29) |
|---|---|---|
| list / get / create / update / delete share (`…/{devtype}-storage-systems/{systemId}/file-shares`) | yes | yes |
| list / get / delete filesystem (`…/filesystems`) | yes | yes |
| filesystem capacity and performance history | yes | yes |
| share settings (`…/share-settings`) | yes | no |
| create filesystem | no separate call | no separate call |

Payloads differ by device type. B10000 share create: `name`, `filesystemName`, `protocol` (example
`NFS`), `settingName`, `reduce`, `sizeInMiB`, `hostAccess[]` (`access`, `options`, `ipaddress`); on
B10000 *deleting a share "will remove the associated filesystem and share settings"*. X10000 share
create: `filesystemName` and `accessClients[].clients` (example `10.168.10.*`); update takes
`accessClients`. The X10000 share record says of `protocol`: *"For R3 only NFSV4.1 protocol is
supported"*, so on the X10000 a share is an NFS 4.1 export today; SMB, and with it SMB ACLs, is not
there.

The X10000 share record: `id`, `path` (the share has no `name`), `protocol[]`, `state` (example
`ACTIVE`), `endPoint`, `fileSystem` (an object, fields not expanded), `accessClients[]` (at most one,
*"clients (IP or hostname) that can access the NFS share"*), `ipRestricted`, `systemId`, `systemWwn`,
`customerId`, `commonResourceAttributes`, `createdAt`, `updatedAt`, `resourceUri`. Filter on
`protocol`, `state`, `generation`, `id`, `path`, `filesystemId`; default sort `path asc`.

The X10000 filesystem record: `id`, `name`, `state` (example `NORMAL`), `shareCount`,
`hardLimitInBytes`, `systemId` (*"SystemUid or serial number of the array"*), `systemWwn`,
`commonResourceAttributes` (`cloudState`, `errCode`, `errMessage`), `createdAt`, `updatedAt`,
`resourceUri`. Filter and sort on `state`, `name`, `id`, `shareCount`, `hardLimitInBytes`,
`softLimitInBytes`; `limit` up to 5000, default 100.

What it does **not** have: SMB ACLs, AD or LDAP join, user mapping, quotas beyond the hard limit,
snapshots, replication, protection policies, migration, *views* or *view policies*.

## 4. "GreenLake for File" — which product

| | The original GreenLake for File Storage | The X10000 with file |
|---|---|---|
| What SCOPE area 7 describes | yes: *views*, *policies*, *ACLs*, *share migration* are its words | partly: shares, filesystems |
| In the GreenLake API catalogue (mirror 2026-06, live 2026-11-16) | **no** device type, no `tierType`, no endpoint | **yes**: devtype7 in Storage Fleet and File Storage; `STORAGE_TIER_ALLETRA_MP_X10000` |
| Software, install, whether still sold | unconfirmed this pass (Q1) | unconfirmed (Q2) |

The `tierType` enum on `GET /storage-fleet/v1alpha1/storage-systems` lists block tiers,
`STORAGE_TIER_ALLETRA_MP_X10000` and `STORAGE_TIER_UNKNOWN`, and no file tier. If the original
product is still onboarded into GreenLake, it is not visible to the public storage APIs; at most it
would show as a `STORAGE` device in the Devices inventory. The tool cannot configure it.

## 5. What the platform calls the tool already makes can do for a file system

All of this is product-neutral in the documentation:

| Call (code) | Block today | For an X10000 |
|---|---|---|
| `POST /devices/v2beta1/devices` (`DevicesClient.add_storage_device`): `serialNumber`, `deviceType: STORAGE`, `partNumber` | yes | same call; the X10000's part number(s) unconfirmed (Q3) |
| `GET /devices/v1/devices?filter=serialNumber eq '…'` | yes | same; returns `assignedState`, `application.id`, `region`, `subscription[]` (`key`, `tier`, `endDate`) |
| Two PATCH calls: application + region, then subscription (`assign_application`, `apply_subscription`) | yes | same calls; which service manager the X10000 goes to is unconfirmed (Q4) |
| `POST /subscriptions/v1/subscriptions` + `find_by_key` | yes | same; the subscription `tier` enum has no X10000 entry (`FOUNDATION_STORAGE`, `HPE_ALLETRA_STORAGE_MP_B10000_SOFTWARE_AND_SUPPORT_SAAS`, …), unconfirmed which tier a file subscription carries |
| `GET /service-catalog/v1/service-manager-provisions` | yes, first PROVISIONED in the region | same; but see the trap below |
| 202 + `Location` polled to `SUCCEEDED`/`FAILED`/`TIMEDOUT` | yes | same for devices; for File Storage and Storage Fleet, 201/202 + `Location` is documented, the status words are not |
| Rate buckets (`default_rate_buckets`) | per family | no published limits for Storage Fleet or File Storage; use the default 60/min bucket under new names until measured |

New calls a file system needs, all documented, all read-only for the first slice:

- `GET /storage-fleet/v1alpha1/devtype7-storage-systems` (regional): per system `id`,
  `logicalClusterSerialNumber`, `commonResourceAttributes.cloudState`, and a `status` block with the
  cluster name, cluster management address, DNS, NTP, proxy and S3 data network. Permission
  `storage-fleet.storage-system.read`.
- `GET /file-storage/v1alpha1/devtype7-storage-systems/{systemId}/filesystems` and `…/file-shares`.

**Trap in the existing code:** `GreenLakeProvisioningService._discover` takes `provisions[0]` and says
so in its detail line. A workspace with Data Services in one region is fine; it is not a way to pick
the service an X10000 belongs to. The file check compares the device's own `application.id` with
the catalogue instead (LESSONS 36: "the first one" is a decision someone did not make).

**Unconfirmed identity:** which value joins the three APIs. The Devices API keys on `serialNumber`;
Storage Fleet shows `id` (example `"ASHBFY6567YGHJ"`) and `logicalClusterSerialNumber`; File Storage
says `systemId` is *"SystemUid or serial number of the array"*. An X10000 is several nodes; whether
GreenLake inventory holds one device per node or one per system is not documented (Q5). This
decides what "one system per run" means for it.

## 6. What needs the file product's own UI or API

| Need (SCOPE area 7) | X10000 through GreenLake | Original GL4F |
|---|---|---|
| Initialization: first network setup, before the system reaches GreenLake | not documented (Q6). Storage Fleet can *change* cluster management address, DNS, NTP, proxy, S3 data network after it is connected (`PUT …/devtype7-storage-systems/{systemId}`) | not documented |
| GreenLake onboarding (device, assignment, subscription) | Devices / Subscriptions / Service Catalog APIs (§5) | same APIs, if it is a `STORAGE` device (unconfirmed) |
| Provisioning: filesystems and shares | File Storage API (§3) | no public API found |
| ACL configuration (SMB ACLs, AD) | no API; X10000 shares are NFS 4.1 only (§3) | no public API found |
| Policy configuration | no API (`accessClients` is the only access control) | no public API found |
| Share migration | no API | no public API found |

## 7. How it fits a tool built for one B10000 per run

What is block-specific today, and would refuse or mislead on an X10000:

- **The sheet.** `ArrayWorkItem` requires `cloudinit_url` (must start with `https://169.254.`),
  `dscc_region_code`, `network`, `dscc_setup` — the B10000's setup wizard. ADR 0005's complete-sheet
  validation would refuse an X10000 workbook before a mode is chosen.
- **The steps.** `cloudinit`, `dscc` (the B10000 *Set Up System* wizard over CDP), `discover`,
  `zoning`, `provision`, `replicate`, `failover_test`, `verify` (SSH `show*`), `asbuilt` (the Block
  Storage Word template) all speak to a B10000 over SSH or WSAPI. Only `greenlake` is reusable.
- **The control plane.** ADR 0006 routes cloud-first, but the only cloud plane built is Component A
  on the global URL. Everything an X10000 offers is on the regional URLs.

Options:

| Option | For | Against |
|---|---|---|
| A. Out of scope | nothing new to maintain | SCOPE area 7 stays empty; the File Storage API is now public and small |
| B. A second **system type** in the same tool: the workbook says which; the registry offers file steps only for a file system | reuses GreenLake auth, http, polling, rate buckets, runs, console, packaging; one system per run still true; BL-28 shares the File Storage adapter | the sheet and registry learn a system type |
| C. A separate build profile (ADR 0007 style) | clean UI | a profile hides features, it does not add a different device; most code would be shared anyway |

**Recommended: B**, cloud-only (no SSH or REST to the X10000 itself), starting read-only. Written
as ADR 0022 (proposed).

## 8. The first slice

A read-only **file system check** for one X10000, from the CLI first (no sheet, no step), because
the API surface has never been called from this tool and LESSONS 28 says a vendor API is proven by
a live call, not a fake:

1. token; 2. device by serial (present, `assignedState`, `application.id`, `region`,
subscriptions with end dates); 3. the device's application is a PROVISIONED service manager in that
region; 4. the system in Storage Fleet devtype7 (`cloudState`); 5. its filesystems and shares.
Each a PASS / WARN / FAIL line with the next step, and `--capture` to save the raw answers for the
fixtures. Requirements in SPEC-029; steps in `workpackets/BL-29.md`.

**What the lab must have to prove it live:** an X10000 with file enabled, connected to a GreenLake
workspace in one of the four regions; an API client in that workspace whose role carries
devices, subscriptions and service-catalog read plus `storage-fleet.storage-system.read`,
`file-storage.file-system.read` and `file-storage.file-share.read`; at least one filesystem and one
share made by hand, to compare counts with the File Storage page in the console; the serial number;
a jump box with egress to the regional host. None of this exists in the lab inventory we know of
(the lab arrays in `docs/validation/` are B10000 and Primera). This is the blocker for BL-29.

## 9. How BL-29 differs from BL-28 (Alletra MP Unified File, SPEC-028)

| | BL-28 Unified File | BL-29 GreenLake for File |
|---|---|---|
| Hardware | the B10000 the tool already onboards (devtype4) | a different system, the X10000 (devtype7) |
| Onboarding | already done by the block init track; file is enabled on it | its own GreenLake onboarding; no cloudinit or DSCC wizard (Q6) |
| Run model | the same array, the same run, extra file steps | a different system type per run |
| Direct plane | WSAPI/SSH to the same array exist (whether file is reachable there is BL-28's question) | none planned; cloud only |
| File Storage API payload | `sizeInMiB`, `settingName`, `reduce`, `hostAccess`, `protocol`; share settings | `filesystemName`, `accessClients` |
| Shared | `adapters/greenlake/file_storage.py` with the device type as a parameter, the regional client, the async poll, the read models for filesystem and share | same |

Whichever branch builds first owns the shared adapter; the other reuses it. The two specs must not
define two file-share models.

## 10. Open questions for the owner

1. **Which product is "GL4F" for the field team?** If it is the original GreenLake for File Storage,
   no public API was found and the tool can do at most its GreenLake device onboarding. Is it still
   sold, and does HPE give PS an API for it?
2. Is the X10000 with file the product field engineers deploy under this scope item? Who installs it
   (HPE factory or PS)?
3. The X10000's part number(s) for `POST /devices` (the B10000's comes from the sheet).
4. Which service manager an X10000 is assigned to (Data Services, or another), and which
   subscription tier a file subscription carries.
5. One GreenLake inventory device per X10000 node, or one per system? Which field joins Devices,
   Storage Fleet (`id` / `logicalClusterSerialNumber`) and File Storage (`systemId`)?
6. How is an X10000 first set up on the network before it reaches GreenLake (a local wizard,
   factory, HPE install)? Only then can "initialization" be scoped.
7. Entitlement: can our workspace's API client be given the Storage Fleet and File Storage read
   permissions (ADR 0006 *gatekeeper*)?
8. A lab X10000, or a customer-free demo workspace with one, for the live run.
