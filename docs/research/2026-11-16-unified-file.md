# Research — Alletra MP Unified File (SCOPE area 6, BL-28)

**Date:** 2026-11-16 · **Status:** research; no code. The decision is ADR 0021 (proposed), the
behaviour is SPEC-028, the first slice is `docs/workpackets/BL-28.md`.
**Sources:** §1. Every fact below names its source. Anything no source confirms is marked
*unconfirmed* and listed in §8.

## 1. Sources

| # | Source | What it is | Read |
|---|---|---|---|
| S1 | HPE CSI Driver docs, *HPE Alletra Storage MP B10000 File Service* CSP page, https://scod.hpedev.io/csi_driver/container_storage_provider/hpe_alletra_storage_mp_b10000_file_service/index.html | HPE's own Kubernetes driver documentation for the B10000 file service | 2026-11-16 |
| S2 | HPE CSI Driver release notes v3.0.0 (2025-07-28), https://github.com/hpe-storage/csi-driver/blob/master/release-notes/v3.0.0.md, and the release table at https://scod.hpedev.io/csi_driver/index.html | when the driver gained B10000 file | 2026-11-16 |
| S3 | HPE Developer, *HPE Alletra* platform page, https://developer.hpe.com/platform/hpe-alletra/home/ | protocol table per product; link to the WSAPI v3 guide and spec | 2026-11-16 |
| S4 | **WSAPI v3 OpenAPI**, `openapi_wsapiv3_2.6.0_en-US.json` (title *WS-APIv3 Documentation*, version *v3 2.6.0 (2026-11-04 22:59:51 UTC)*), served by https://developer.hpe.com/ws/api-spec | the array's own REST API, version 3 | 2026-11-16 |
| S5 | GreenLake **File Storage** API v1alpha1, https://developer.greenlake.hpe.com/docs/greenlake/services/file-storage/public and its OpenAPI bundle (`file-storage-api.yaml`, version 1.0.0); changelog *2026-September: initial v1alpha1* | the cloud API for file on B10000 (`devtype4`) and X10000 (`devtype7`) | 2026-11-16 |
| S6 | GreenLake **Storage Fleet** API v1alpha1, the offline mirror `reference/greenlake_api_docs/greenlake/services/storage-fleet/` (scraped 2026-06-07) and the live bundle `storage-fleet-api.yaml` | system, system-settings and port records for B10000, with file fields | 2026-11-16 |
| S7 | The array's own `help controlport`, captured on our lab arrays: `tests/fixtures/rc_pair/help/help_controlport.txt` (AlletraMP_D22U27, OS 10.5.0, BL-38) and `tests/fixtures/rcip_pair/help/alletra_help_controlport.txt` (rack13-ARCUS, OS 10.5.55, BL-41) | the CLI that sets File ports | captured 2026-10-07 and 2026-11-03 |
| S8 | `showport` captured on the lab arrays: `tests/fixtures/rc_pair/D22U27/showport.txt`, `tests/fixtures/rc_pair/E18U31/showport.txt`, `tests/fixtures/rcip_pair/before/alletra/showport.txt` | which lab array has File ports | captured 2026-10-07, 2026-11-03 |
| S9 | The tool's own `showport -file` reader: `parse_file_ports` in `application/provisioning/discovery.py` (commits b5a736dd and f7ebac85, 2026-09-04) and its tests in `tests/unit/test_storage_services.py` (`_SHOWPORT_FILE`, two arrays; `_D22U27_FILE`) | File ports are already read and shown in Discovery | in the code since v0.13 |

Not reachable on 2026-11-16: the WSAPI v3 developer guide (https://www.hpe.com/support/AlletraMP-B10000-WSAPIV3-devguide,
timed out), the WSAPI v3 FAQ (https://www.hpe.com/psnow/doc/a00148521enw, timed out) and the HPE
Community post *Introducing HPE Alletra Storage MP B10000 File Service with HPE CSI Driver for
Kubernetes 3.0.0* (403). No HPE user guide for B10000 file was read. That is the biggest gap in this
note (§8).

## 2. What "Unified File" is on a B10000

An NFS file service that runs on the block array itself, on the same controller nodes and capacity,
served out of Ethernet host ports switched to *File* mode. It is not a separate product or cluster.

| Fact | Source |
|---|---|
| *"HPE Alletra Storage MP B10000 from OS version 10.5 and later offer an NFS file service."* The array *"needs to be running OS 10.5 or later."* | S1 |
| The CSI driver's 3.0.0 notes say *"Support for Unified File in Alletra MP B10000 Release 5"* (CON-3153). "Unified File" is HPE's own name for it. | S2 |
| The B10000's protocols are listed as *"NVME, Fibre Channel, iSCSI, File"*. | S3 |
| Objects: a **file service** (one per array), **file systems** (capacity, data reduction, snapshots and schedules), **file share settings** (the client list: address, `ro`/`rw`, squash, secure port), **file shares** (a name in a file system, with a setting and a protocol). | S4 paths `/api/v3/fileservice`, `/filesystems`, `/filesharesettings`, `/fileshares` |
| Protocol: `NFS` is the only value of the share `protocol` enum in WSAPI v3. The cloud API says *"Currently, only the NFSv4 protocol is supported."* | S4 `fileshares.CreateFileShare.protocol`; S5 `ArcusShareCreateRequest.protocol` |
| A share's path on the array is `/file/<volume>/<share>`. | S1 |
| Limits (from the CSI page): *"Maximum 64 File Service shares for four or more array nodes, 32 for a two node system"*; *"Maximum 64TiB capacity per file share."* The cloud API caps a share at 67108864 MiB (64 TiB) and takes at least 1024 MiB. | S1; S5 `sizeInMiB` |
| The file service keeps a capacity limit: `spaceLimitPercentage` (*"Maximum provisioned capacity limit"*) on start, `limitPercentage` in the read. | S4 `fileservice.StartFileService`, `fileservice.SystemCapacitySummary` |
| Ransomware detection is a file-service and file-system option (enable, disable, clear alert). | S4 `fileservice_uid_Request`, `filesystems_uid_Request` |

Not found in any source read: **SMB**, **Active Directory**, **LDAP for file users**, **DNS for the
file service**, **licensing**, quotas. WSAPI v3 has an `/api/v3/sr/fssmb` System Reporter path
(S4), which hints that an SMB statistic exists, but the share `protocol` enum has only `NFS`. The
`/api/v3/ldap` resource in S4 has no file field; it is not shown to be the file service's directory.
All of this is *unconfirmed* (§8).

## 3. File ports and networking

| Fact | Source |
|---|---|
| A port is put in File mode with `controlport config file <node:slot:port>`. *"Controlport config file command changes the port from iSCSI or NVMe to File on all nodes in the array following array reboot."* `-sysreboot` *"Causes reboot of the array. This option is required only when switching out of or into File mode."* *"Controlport config mode changes are not allowed when ports are online."* | S7 |
| A File interface is addressed with `controlport file addr [-f] <ip_addr> <prefix_len> [-vlan <vlan_tag>] <node:slot:port>` (one IPv4 address per interface; the interface must be offline first). `controlport file gw` sets **one gateway common to all File interfaces** (all offline first). `controlport file mtu` takes 1280–9000 (default 1500). `controlport file state {up|down}`, `controlport file ping`, `controlport file delete`. | S7 |
| WSAPI v3 reads a File port: `port.Port.fileData` = `failoverIPs`, `ipDisabled`, `linkState`, `prefixLength`, `vlanId`. WSAPI v3 has edit actions for iSCSI, NVMe and RCIP ports but **none for File ports**, and its `CONFIG_PORT` action converts *"to either NVMe/TCP or iSCSI"* only. | S4 `port.PortFile`, `port.Configure_port_protocol` |
| The file service reports, per node, `fileserviceStatus` and per port `isFilePortConfigured`, `isFilePortOnline`, `mtu`. | S4 `fileservice.FileServiceSummary`, `fileservice.PortStatus` |
| `showport -file` prints `N:S:P Mode State IPAddr/PrefixLen IPDisable Gateway VLAN MTU Rate Eth Link FailoverIPs`. The tool already parses it and shows a *file service ports* section in Discovery. On D22U27: `0:4:1 … 10.54.90.70/21 N 10.54.95.254 untagged 1500 10Gbps eth6 up -`. A down port's address shows up as the `FailoverIPs` of its partner. File and iSCSI are alternatives on x:4:1 / x:4:2 (`showport -iscsi` on D22U27: *"There is no specified port information"*). | S9 |
| The cloud has `PUT …/ports/{id}/edit-file` (`ipAddress`) and `POST …/ports/{id}/ping-file`, *"supported from OS version 10.5.0 and later"*, and reads `fileData` and port type `PORT_TYPE_FS`. | S6 |
| Clients need *"IP ports configured on the array that are reachable from the Kubernetes compute nodes"* (the same holds for any NFS client). | S1 |

So the File network is a property of the ports, set once at install. Switching a port into File mode
reboots the whole array: the tool must never do that (ADR 0021).

## 4. Interfaces, side by side

| Interface | Reads | Writes | Fit for this tool |
|---|---|---|---|
| **WSAPI v3** on the array (`https://<array>/api/v3`, session from `POST /api/v3/credentials`) | file service, file systems, share settings, shares, File ports, tasks | start/stop file service; create/modify/delete file systems; create/modify/delete share settings; shares through the `CREATE_COMPLEX_FILE_SHARE` / `MODIFY_COMPLEX_FILE_SHARE` sub-actions (`CREATE_FILE_SYSTEM`, `CREATE_FILE_SHARE_SETTINGS`, `CREATE_FILE_SHARE`, `ADD_SNAP_SCHEDULE`, `EXPORT_FILE_SHARE`, `UNEXPORT_FILE_SHARE`, …); delete a share; file-system snapshots and schedules | **Best.** Direct plane, the run's own array credential, no cloud entitlement. New for the tool: today's client speaks WSAPI v1 through `hpe3parclient` (`adapters/array/wsapi_client.py`). |
| **Array CLI over SSH** | `showport` and `showport -file` show File ports, already read by Discovery (S8, S9). No `show` command for the file service, file systems or shares is confirmed. | `controlport config file` / `controlport file …` (S7). No CLI for file systems or shares is confirmed. | Reads of ports only. Writes are out: ADR 0001 keeps SSH read-only, and the only write path (ADR 0015) is scoped to Remote Copy. |
| **GreenLake File Storage API** (cloud, `devtype4`) | shares, file systems, share settings, capacity and performance history | create a share (needs an **existing** share setting: `settingName` is required and share settings are GET-only), update hosts or size, delete a share (*"removes the associated filesystem and share settings"*), delete a file system; 202 + `Location` task | Not for a greenfield setup: it cannot create a share setting or enable the service. Needs the DSCC client the tool does not have (ADR 0006) and the workspace permissions `file-storage.file-share.*`. v1alpha1. |
| **GreenLake Storage Fleet API** (cloud, `devtype4`) | `fileServiceInfo` (`isFileCapable`, `isFileEnabled`, capacity), system-settings `isFileEnabled`, `fileData` on ports | system-settings `enableFile {enable, fileServiceId}`; File port `edit-file` / `ping-file` | Same cloud gap. The edit's own description lists the setting kinds it accepts and `enableFile` is not among them: *unconfirmed* which one is right. |
| **The array UI** and **DSCC / Data Ops Manager UI** | everything | everything | The operator's own route. The CSI page reads a share's `referenceUid` *"from URL in the web UI of the array while viewing the file share"* (S1). |
| **HPE CSI Driver** File Service CSP | — | NFS shares as Kubernetes volumes | Not ours: Kubernetes only. Useful as HPE's own description of the service and its limits. |

## 5. Snapshots

WSAPI v3 has file-system snapshots and schedules: `Create_FileSnapshot`, `Add/Modify/Suspend/Resume/
Remove_File_System_Schedule`, `Restore_File_System_Snapshot`, `Set_File_System_Snapshot_Online/Offline`
(S4 `filesystems_uid_Request`) and `ADD_SNAP_SCHEDULE` inside a share create (schedule name, cron-like
`scheduleParams`, `expireSecs`, `retainSecs`, `namePattern`). The CSI driver does not use them
(*"Snapshots and clones are not yet implemented"*, S1). SCOPE area 6 lists "snapshot configuration";
it belongs with BL-21 (snapshots) so that block and file schedules are one design.

## 6. The lab

| Array | OS | File ports | Source |
|---|---|---|---|
| AlletraMP_D22U27 | 10.5.0 | **0:4:1, 0:4:2, 1:4:1, 1:4:2 in File mode** (`Type file`, `Protocol IP`), each with an address (10.54.90.70/.71/.73/.74), `ready` | S8 `rc_pair/D22U27/showport.txt` |
| AlletraMP_E18U31 | 10.5.0 | none: the same four ports are iSCSI | S8 |
| rack13-ARCUS | 10.5.55 | none: 0:4:1/1:4:1 are iSCSI, 0:4:2/1:4:2 free iSCSI, 0:4:3-4/1:4:3-4 free IP (before BL-41 used 0:4:4/1:4:4 for RCIP) | S8 |

D22U27 is the lab array for this work. Its `showport` lists all four File ports `ready`; the
`showport -file` rows pinned in the tests (S9, two of the four) are `up` on 10.54.90.0/21 with
gateway 10.54.95.254. That its ports are addressed suggests someone set the file
service up there, but no capture shows the service state, a file system or a share: that is the
first read-only capture (SPEC-028 §5). D22U27 is also the replication lab array; a file share there
does not touch Remote Copy (different ports), but the booking has to say so. No lab Linux host is
known to reach 10.54.90.x for an NFS mount: *unconfirmed*.

## 7. The overlap with BL-29 (GreenLake for File)

| | BL-28 Unified File (this note) | BL-29 GreenLake for File (SPEC-029) |
|---|---|---|
| What | The NFS file service **inside the B10000 the run already targets** (`devtype4`) | A different system: BL-29 treats GL4F as the **X10000** (`devtype7`) reached through GreenLake only; the original GreenLake for File Storage product (views, view policies) has no public API (its research §4) |
| Array | the run's one array (ADR 0013), its admin credential | not the run's B10000; a second system type per run (ADR 0022, proposed) |
| Plane | the array's WSAPI v3 (direct) | cloud only |
| Shared ground | The GreenLake **File Storage** API (S5) serves both B10000 (`devtype4`) and X10000 (`devtype7`). BL-29's research (branch `feat/bl-29-gl4f-spec`, `docs/research/2026-11-16-greenlake-for-file.md` §3, §9) found the same API; its operation list, payloads and *"will remove the associated filesystem and share settings"* agree with the OpenAPI bundle read here. It proposes one adapter for both, `adapters/greenlake/file_storage.py`, device type as a parameter, built by whichever branch comes first. |
| This note's answer | BL-28 configures over WSAPI v3, not that API: on `devtype4` share settings are GET-only and `settingName` is required, so a greenfield share cannot be made through it, and the service cannot be started (§4). BL-28 may read `devtype4` through the shared adapter later (what the cloud sees); BL-29 stays on `devtype7`. ADR 0021 item 6. |

## 8. Unconfirmed — open questions for the owner and the first capture

1. **Licence.** Does Unified File need a licence or a subscription tier on the B10000? No source read says. (Owner, or `showlicense` on D22U27.)
2. **Is the file service enabled on D22U27, and with what?** Read `GET /api/v3/fileservice` (first capture).
3. **Does the lab array serve WSAPI v3, and which version?** The tool reaches WSAPI v1 1.15 on both lab arrays (BL-38). Fields marked *"Available since v2.6.0"* or *v2.7.0* in S4 may be missing on OS 10.5.0. (First capture.)
4. **The envelope of a share create.** S4 lists `CREATE_FILE_SHARE` as *"a subaction to CREATE_COMPLEX_FILE_SHARE"*, and its conventions describe batches as `{"batch": …, "ordered": true, "operations": [...]}` posted to `/api/v3/provisioning`, but the provisioning request schema does not list the file batch and `POST /api/v3/fileshares` takes the sub-actions directly. Which body the array accepts is a live probe (lesson 28).
5. **Task polling.** WSAPI v3 writes answer 201 or 202; S4 has `/api/v3/tasks/{uid}`. How a 202 names its task is not shown.
6. **CLI for file objects.** No `show` command for file systems or shares is confirmed. `help` on D22U27 (read-only) answers it; until then the removal set cannot be CLI lines (ADR 0021).
7. **SMB, Active Directory, LDAP, DNS for file.** Not in any source read. Out of scope until an HPE document says they exist on B10000.
8. **Enabling the service.** What `START_FS_SERVICE` needs first (File ports? a reboot?) and what it disrupts. Not in scope for the first slices.
9. **A client for the live run**: a lab Linux host that can reach D22U27's File addresses.
10. **The cloud contradiction** in S6 (`enableFile` in the edit body, absent from the edit's own list). Not needed if ADR 0021 is accepted.
