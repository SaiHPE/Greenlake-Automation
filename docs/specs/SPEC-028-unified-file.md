# SPEC-028 — Unified File: read, check and set up NFS shares on the run's array

**Status:** PROPOSED 2026-11-16; the reads accepted 2026-11-17 with ADR 0021. R1 parsers built
and pinned to two captures (§8): rack13-ARCUS (no File ports) and D22U27 (four File ports, the
service on, three file systems, client groups and shares). Nothing reads an array yet: slice 1
(work packet steps 4–7) is next. R4–R6 (slice 2) follow slice 1's live run; R7–R12 (slice 3, the
writes) wait for ADR 0021's write-plane amendment.
**ADRs:** [0021](../adr/0021-unified-file-over-wsapi-v3.md) (accepted for reads; the write plane
waits for an amendment) · [0013](../adr/0013-one-array-credential-per-run.md) ·
[0001](../adr/0001-post-init-verification-via-ssh-cli.md) (SSH stays read-only) · ADR 0025 (any
SSH write)
**Research:** [2026-11-16-unified-file.md](../research/2026-11-16-unified-file.md)
**Tracker:** BL-28 · **Lab:** AlletraMP_D22U27 (OS 10.5.0, four File ports, service on; captured
2026-11-17) · rack13-ARCUS (OS 10.6.0, no File ports, service stopped; captured 2026-11-16)
**Owner:** `adapters/array/wsapi_v3_client.py` (new), `domain/unified_file.py` (new), `application/unified_file/`
(new bounded context: `read.py`, later `plan.py`, `apply.py`, `verify.py`, `steps.py`),
`application/provisioning/discovery.py`, `application/documents/asbuilt*.py`,
`application/platform/init_sheet.py`, `domain/workflow.py`, `frontend/src/steps/`

## 1. Problem

From OS 10.5 a B10000 serves NFS from its own controllers. An engineer who sets up block storage
with this tool sets up file shares by hand in the array UI, and the as-built says nothing about
them. Today Discovery already shows the File ports (`showport -file`), and nothing else.

The work splits in two. Reading what the array has is safe and useful on every array (R1–R3).
Creating shares is a write on a customer array: it waits for ADR 0021's write-plane amendment and
follows the plan → approve → apply pattern of provisioning (R4–R10).

## 2. Which API, and the overlap with BL-29

The tool reads B10000 file over the **array's own WSAPI v3** (ADR 0021, accepted for reads). The
write plane is v3 or, as the fallback, a write-scoped CLI client under ADR 0025; ADR 0021's
amendment chooses after the lab probe. The tool does **not** configure through the GreenLake File
Storage API, even though that API has `devtype4` (B10000) share and file-system calls and BL-29
found it too (its research §3). Checked against the OpenAPI bundle on 2026-11-16: on `devtype4`
share settings are GET-only and `settingName` is required to create a share, so the first share on
a new array cannot be made through the cloud; the file service cannot be started there; deleting a
share also deletes its file system and share setting; it needs regional cloud access and
`file-storage.*` workspace permissions the lab does not have; and it is v1alpha1 (*"No guarantees
on backward compatibility"*, HPE's versioning guide).

BL-28 needs no cloud adapter through slice 3. A later slice may *read* `devtype4` for an as-built
line "what GreenLake sees", never write. If it is built, it shares only the regional GreenLake HTTP
client and its paging with BL-29 (deferred 2026-11-17), not the share models: the payloads differ
(`devtype4` has a share `name`, `settingName` and `hostAccess[]`; `devtype7` has a `path` and
`accessClients[]`). One share is never written by two planes.

## 3. Requirements

### Reads (slice 1)

**R1 — Read the file side of the array.** Over WSAPI v3 with the run's array credential, every GET
with `Content-Type: application/json` (OS 10.5.x answers 400 `MISSING_MEDIA_TYPE_HEADER` without
it; 10.6.0 does not ask): `GET /api/v3/fileservice`, `/api/v3/filesystems`,
`/api/v3/filesharesettings`, `/api/v3/fileshares`.
Over the read-only SSH client (already allowlisted): `showversion`, `showsys`, `showport`,
`showport -file`.
The result is a `FileReport` (`domain/unified_file.py`):

| Part | Fields (from the WSAPI v3 schema) | What the captures show (§8) |
|---|---|---|
| Service | enabled (`isFileServiceEnabled`); per node: status (`fileServiceSummary[].fileserviceStatus`) and its ports (`portStatus[]`: configured, online, MTU); capacity limit % and used/available (`capacitySummary`); counts of file systems and shares | Status `normal` (running) or `stopped`. `portStatus[]`: two per node, **no port id**. `capacitySummary` is in MiB; OS 10.5.0 sends only total, used and available, 10.6.0 adds `limitPercentage` and the two counts. |
| File ports | from `showport -file`, as Discovery reads them today (`parse_file_ports`, unchanged) | D22U27: four rows. rack13-ARCUS: the no-port answer. |
| File systems | name, size MiB, data reduction (`reduce`), share count, state, owner node (`fsmaster`) | All present, plus `vvSizeInMiB` (the volume, 128 MiB over `sizeInMiB`), `prov` (`tdvv` with `reduce`, else `tpvv`) and `volumemembers` (the VV, same name). State `STATE_NORMAL`. |
| Share settings | name, clients: address, `ro`/`rw`, squash, secure port | `name`, `clientInfo[]` of `ipaddress`, `access`, `options` (`"*"`, `rw`, `root_squash`), `hostCount`, `sharecount`, `state`. **No secure-port field.** |
| Shares | name, file system, share setting, protocol, mount path, state, type (base or snapshot) | `name`, `filesystem.name`, `sharesettings.name` (with a copy of the group's clients), `protocol` `["NFS"]` (a list), `mountpath` `/file/<file system>/<share>`, `hostip` (the File port it is served on), `state`. **No base/snapshot field and no exported flag.** |

Every v3 answer is a collection: `{"version", "arraySerialNumber", "members": {<uid>: record}}`.
An empty one is `"members": {}`, a map and not a list.

**A read of another array is refused** (AGENTS rule 4; ADR 0021 item 1). Every collection names
`arraySerialNumber`, the serial `showsys` prints (both captures). When any of the four is missing
it or names another serial, none of the read is shown, stored or put in the as-built, and Discovery
says R2's sentence for it.

Each WSAPI call and SSH command goes to the command log (SPEC-019); the password and session key
never do. The parsers (`application/unified_file/read.py`) are pinned to both captures (work packet
steps 2 and 3); a record missing a field the model needs fails the whole read, never a silent skip.

**R2 — Say plainly when there is nothing to read.** One sentence each, never an error that stops
Discovery:
- OS older than 10.5: *"This array runs OS 10.4.x. File shares need OS 10.5 or later."*
- WSAPI v3 does not answer: *"The array did not answer on its file API, so only the File ports
  are shown."* (Lesson 27: any structured answer, including 401 or 404, means it answered.)
- WSAPI v3 answers 401 to the reads after a good login (the session value is wrong, a risk ADR
  0021 *Consequences* names): *"The array's file API turned down the tool's session, so only the
  File ports are shown. Block storage is not affected; send the console log to the tool team."*
- The serial does not match (R1): *"The file API at this address belongs to array <serial>, not to
  this run's array <serial>, so file details are not shown. Check the array address in the
  workbook."*
- File service off: *"The file service is off on this array. Turn it on in the array's UI before
  shares can be made."* Its ports are still listed.
- No File ports: nothing is shown (most block arrays).

Whether to show anything is decided by `showport -file` and `isFileServiceEnabled`, never by whether
v3 answers: rack13-ARCUS has no File ports and still answers all four GETs with 200, a stopped
service record and empty collections (§8). That array is the "no File ports, service off" case.

**R3 — Show it, and put it in the as-built.** Discovery's *file service ports* section becomes
*File service* with four folded parts (service, ports, file systems, shares with their clients).
The as-built gains a *File service* section after the provisioning record, read when the document
is made (the SPEC-018 pattern); absent when the array has no File ports and the service is off.
Verify configuration adds the service state and the File ports to its table, read-only.

### Configure (slice 2 after slice 1's live run; slice 3 after ADR 0021's write-plane amendment)

**R4 — A new, optional workbook tab "File".** Parsed only when present and non-blank; every
existing workbook parses as today (SPEC-015 R1 pattern).

| Section | Columns | Default / rule |
|---|---|---|
| *File service* | Expected state (on / off) | on. Checked, never changed (ADR 0021 item 4). |
| *File ports* | N:S:P · Address · Prefix length · VLAN · Gateway · MTU | Checked against `showport -file`, never written. Blank section = not checked. |
| *Client groups* (one row per client) | Group name · Client (address, CIDR or `*`) · Access (`rw`/`ro`) · Squash (`root_squash` / `no_root_squash` / `all_squash`) · Secure ports only (yes/no) | Access `rw`; squash `root_squash`; secure **yes**. A group is a WSAPI *file share setting*. The array's CLI always applies `secure` and says it *"cannot be changed"* (§8), while HPE's CSI driver documents `shareSourcePorts: insecure` for B10000 file (research S1, read 2026-11-17), so v3 may turn it off. The column stays only if the write probe shows v3 can. |
| *Shares* (one row per share) | Share name · File system · Size (GiB) · Data reduction (yes/no) · Client group | Data reduction **yes** (sent explicitly). Protocol is NFS and not a column. One share per file system: the array allows no more (§8). |

Words on the sheet and screen: *client group*, not *share setting*; *share*, *file system*.

**R5 — Validation at upload (blocking, one sentence each).**
- A share's client group is not on the tab; a client group has no client row (lesson 36: a blank
  never means everyone). `*` is accepted only when typed, and then shown as *any host that can
  reach the File ports*.
- Size under 1 GiB or over 64 TiB (research §2; *"Maximum size of filesystem is 64 TiB"*, and sizes
  round up to a multiple of 256 MiB, help createfilesystem).
- Two shares on one file system (*"Maximum of one share can be created in a filesystem"*, help
  createfileshare).
- More shares than the array allows: 32 on a two-node array, 64 on four or more (checked at step
  time, when the node count is read).
- The same share name twice; an empty name; a name with anything but letters, digits, `.`, `-` and
  `_`, or starting with `-` (help create: *"User supplied names for the create\* commands are
  limited to alphanumeric characters, period/dot, dash and underscore"*); a name over 255
  characters (the help of each create command). Mixed case is allowed (D22U27 has `Lab_test`).
- A value outside the lists above (access, squash, yes/no).

**R6 — Check (blocking findings at step time).** File service on, and every node `fileserviceStatus`
`normal`; at least one File port online per node, counted from `showport -file` (`portStatus[]`
names no port); the sheet's File ports match `showport -file` (address, prefix, VLAN, gateway, MTU),
each mismatch one row; capacity: the sum of new file systems (in MiB) fits under `availableCapacity`
and, where the array sends it (10.6.0), `limitPercentage`, and the CPG free space (`showspace` is
allowlisted); share count within R5's limit.

**R7 — Plan (SPEC-001: exists / create / conflict).** Per client group, file system and share:
absent → **create**; present and the same → **exists**; present and different (other clients,
size, file system, group) → **conflict**, never changed. The plan lists each create as the call it
will make (a WSAPI v3 call, or a CLI line if ADR 0021's amendment picks the CLI).

**R8 — Approve and apply.** Nothing is written until the operator ticks *"I have reviewed this plan
and authorise creating these file shares on the array"* and clicks *Create file shares* (the
provisioning gate). The approval is withdrawn if the tab, the read or the plan changes (lesson 6).
The apply first re-reads the array serial and stops on a mismatch (R1). Order: client groups →
file systems → shares, with the export if the share is not exported on create. The array's own help
agrees: a share setting and a file system must both exist before a share. The plane (v3, or the
write-scoped CLI under ADR 0025) and the exact bodies or forms are fixed by ADR 0021's amendment
after the first live probe (the `CREATE_COMPLEX_FILE_SHARE` sub-actions and task polling, research
§8 Q4 and Q5), and pinned in a test (lesson 28). Over v3, wait for a 202 task to finish before the
next call. Stop at the first failure, say which call and the array's message.

**R9 — Verify (read-only).** Read back: each share present, state `STATE_NORMAL`, on the planned
file system and client group, clients as planned; the file system's size and data reduction. (The
share record has no exported flag, §8: present and normal is what can be read.) Verdict per share:
**Ready** · **Not ready (reason)**. The tool does not mount the share from a host (hosts are
read-only for the tool); the step prints the mount line for the engineer to try:
`mount -t nfs4 <hostip>:<mountpath> <dir>`, both read from the share record.

**R10 — Removal set (SPEC-007, text the tool never runs).** What this run created, in reverse
order, as the array's CLI lines (ADR 0021 item 5; forms from the array's help, §8):
`removefileshare -d -f <file system> <share>`, then `removefilesystem -f <file system>`, then
`removesharesetting -f <client group>`. Without `-d` the first only unexports, and the file system
then cannot be removed (*"if fileshare is present on it will fail"*); with `-d` it is refused while
the share holds data, which the removal set says in one sentence. Objects that were there before
the run never appear. If the probe shows that a share create makes its own client group (on
D22U27 the groups are one per share, each named after its share or file system), that group is
listed too, although the plan did not name it.

**R11 — Steps and modes.** `WorkflowPhase.STORAGE_FILE`; the registry gains
`StepDef("file", "File shares", WorkflowPhase.STORAGE_FILE, "file")` after `provision` and before
`replicate`, served through `/app/profile`. A new preset `RunMode.FILE` ("File shares") =
`discover → file → verify → asbuilt`; *Custom* can pick `file`. The step needs the File tab: a run
minted for a mode that includes it from a workbook without the tab is refused with one sentence
(HTTP 422), as SPEC-015 R4 does for Replication. `BOTH` and `PROVISION_ONLY` are unchanged.

**R12 — UI (one step page, StepShell, the BL-43 parts pattern).**

```
File shares                                                     [Read again]
  1 Array file service    on · 2 nodes running · 4 ports online · 3 shares already here   (folded)
  2 Check                 0 findings | the list, one sentence each
  3 Plan                  table: Kind | Name | Action (create / exists / conflict) | Details
                          [Show 6 calls]
  4 Create                [ ] I have reviewed this plan and authorise creating these file shares
                          on the array            [Create file shares]
  5 Verify                table: Share | Mount path | Clients | Verdict ; mount line to copy
  Removal                 folded; the lines to paste or the UI steps
```

The mode card *File shares* is unavailable, with the reason, when the uploaded workbook has no File
tab (the Replication card's rule).

## 4. Non-goals

Turning the file service on or off; putting a port in or out of File mode (it reboots the array);
File port addresses, gateway, MTU, VLAN (read and checked only); SMB, Active Directory, LDAP, DNS for
file (no HPE source shows them on B10000); quotas; ransomware settings (read only); file snapshots
and schedules (with BL-21, one design for block and file); replication of file systems; the
GreenLake File Storage API for writes (ADR 0021 item 6); mounting from hosts.

## 5. Glossary (to add to `CONTEXT.md` with slice 1)

**File service**: the array's NFS service, one per array, running on each controller node.
**File port**: an Ethernet host port in File mode (`showport` Type `file`). **File system**: capacity
for shares, with data reduction. **Client group**: the list of clients that may mount a share (the
array calls it a *file share setting*). **File share**: an NFS export of a folder in a file system.
The provisional *View* entry in CONTEXT is replaced: on a B10000 the word is *share*.

## 6. Verification and live-run checklist

**Before code — the captures (read-only; the owner runs `lab/file_capture.py`).** `showversion`,
`showsys`, `showport`, `showport -file`, `shownet`, the `help` index and the help of every file
command it names; WSAPI v1 `/system` and `/wsapiconfiguration`; WSAPI v3: `POST
/api/v3/credentials`, the four GETs of R1, then the session deleted. Each array goes to
`tests/fixtures/unified_file/<TAG>/` with a README of the facts. Done for rack13-ARCUS on 2026-11-16
and D22U27 on 2026-11-17 (§8). `showlicense` and `GET /api/v3/ports` were left out: the licence flag
is in v1 `/system`, and File ports come from `showport -file` only (lesson 41).

**Unit.** Parsers on the capture; the serial refusal (R1: a missing or another serial); R2's
sentences; R5 rule per sentence; R6 findings; R7 exists/create/conflict; R8 order and
stop-at-first-failure against a stub that models the vendor's real refusals; R10 order and "never
the pre-existing objects"; registry and 422 gate (R11).

**Live, slice 1 (reads)** — on labrat, a *Verify only* and a *Provision only* run on D22U27:
- [ ] Discovery shows *File service* with the four ports, the service state, and the file systems
      and shares the array UI shows (counts and names match).
- [ ] The as-built has the *File service* section with the same content.
- [ ] The console shows only `show*` and WSAPI GETs; no password, no session key.
- [ ] A second capture after the run is identical to the first.
- [ ] On E18U31 (no File ports) nothing about file is shown.

**Live, slice 3 (writes)** — on D22U27, objects named `zz_fs_*`, with a lab Linux client that can
reach 10.54.90.0/21 (research §8 Q9):
- [ ] Plan: one client group (the client's address, `rw`, `root_squash`, secure), one file system
      (1 GiB, data reduction yes), one share. Approve, create, verify *Ready*.
- [ ] The engineer mounts the share from the client with the printed line and writes a file.
- [ ] A second plan says *exists* for all three; a changed client list is a *conflict*.
- [ ] The removal set, applied by hand, leaves no `zz_fs_*` object; a capture matches the first.
- [ ] Shares already on the array before the run are unchanged (compare the capture).

## 7. Size

Slice 1: v3 read client (~120 lines), models and parsers (~150), Discovery and as-built (~150), UI
section (~120), ~15 tests. Slice 2 (tab and check): ~250 and ~15 tests. Slice 3 (plan, apply,
verify, step, mode): ~600 and ~25 tests.

## 8. What the captures settled

**rack13-ARCUS, OS 10.6.0, 2026-11-16** (B10230, two nodes, CZ2D2K014S; read-only;
`tests/fixtures/unified_file/rack13/`, pinned by `tests/unit/test_unified_file_read.py`). An array
with no File ports.

Research §8, answered for this array:
- **Q1 Licence.** WSAPI v1 `/system` `licenseState.fileServices` is true. Whether file needs a
  licence at all is still open.
- **Q2 Service state.** Off: `isFileServiceEnabled` false, both nodes `stopped`, capacity and counts
  all zero.
- **Q3 WSAPI v3.** Served on port 443 (no 8080 needed), login accepted with the same array
  credential as v1, `X-Server-Version: 2.6.0.1895`. WSAPI v1 is 1.16.0 on this OS.
- **Q6 File CLI.** A file CLI exists for reads: `help show` lists `showfileservice`, `showfileshare`,
  `showfilesystem` and `showsharesetting`. The old 3PAR File Persona names (`showfs`, `showfpg`,
  `showvfs`, `showfshare`, `showfstore`) have no help. Create and remove commands were not asked.

Also shown:
- The v3 shape (R1): a collection with a `members` map keyed by uid; the file service record exists
  even with no File ports; `portStatus[]` lists two entries per node and **names no port**.
- The v3 session: `POST /api/v3/credentials` answers 201 with body `key`, `sessionId`, `username`,
  `arrayPrivileges`, a `Location: /api/v3/credentials/<key>` header and three cookies
  (`sessionToken`, `hpeWsapiSentryLineage`, `hpeWsapiSentryUsername`). `DELETE
  /api/v3/credentials/<key>` answers 200. The GETs carried both the key (as
  `X-HP3PAR-WSAPI-SessionKey`) and the cookies, so which one the array needs is open.
- `help controlport` on 10.6.0 still says `-sysreboot` is required to move a port into or out of
  File mode (ADR 0021 item 4 stands).

Where it contradicted the research note as first written (2026-11-16; §4 is now rewritten):
- §4 and §8 Q6 said no `show` command for the file service, file systems or shares is confirmed.
  On 10.6.0 there are four. Reads stay on v3 (one source per fact, lesson 41); the CLI matters for
  the removal set's lines (R10).
- §6 lists rack13-ARCUS at OS 10.5.55. It now runs 10.6.0; its ports are as §6 says (no File
  port; 0:4:1 and 1:4:1 iSCSI).
- §8 Q3 says the tool reaches WSAPI v1 1.15. On 10.6.0 it is 1.16.0.

**AlletraMP_D22U27, OS 10.5.0, 2026-11-17** (CZ2D320BT1, two nodes; read-only, nothing created;
`tests/fixtures/unified_file/d22u27/`, same test file). Four File ports, the service on, three file
systems, three client groups, three shares. Two object names were replaced with placeholders
before commit (the fixtures README says which).

Research §8, answered:
- **Q1 Licence.** `fileServices` is true here too. Whether file *needs* a licence is still open.
- **Q2 Service state.** On: `isFileServiceEnabled` true, both nodes `normal`, every `portStatus`
  entry configured and online at MTU 1500.
- **Q3 WSAPI v3 on 10.5.0.** Served on 443 with the array credential, `X-Server-Version:
  2.5.0.1463`, **when the GET carries `Content-Type: application/json`**. Without it OS 10.5.x
  answers 400 `{"message": {"key": "MISSING_MEDIA_TYPE_HEADER"}}`: that is what D22U27, E18U31
  (10.5.60) and VZ (10.5.51) answered on the first run of the day, before the script sent the
  header. Those 400s were the missing header, not a missing API (lesson 27: they were answers).
  Version 2.5.0 does not send `limitPercentage`, the two counts or the ransomware fields.
- **Q6 File CLI.** It has create and remove commands. Their SYNTAX lines, word for word
  (`FILE_CLI_SYNTAX` in `domain/unified_file.py`, pinned to the help):

  ```
  createfilesystem [-tpvv|-reduce] <name> <size>[g|G|t|T]
  createsharesetting [-add <ipaddr_list>? <options for host access>] sharesetting_name
  createfileshare [options] <filesystem_name> <share_name>
  removefileshare [options] <filesystem_name> <share_name>
  removefilesystem [options] <name>
  removesharesetting <sharesetting_name>
  showsharesetting [sharesetting_name]
  ```

  The ten file help texts are byte-for-byte the same on E18U31 (10.5.60) and VZ (10.5.51).

What the populated records look like (the R1 table has the fields):
- Every `members` key is the record's `uid`, on all four resources.
- `capacitySummary` is in MiB: `usedCapacity` 256000 is the sum of the three file systems'
  `vvSizeInMiB` (102400 + 102400 + 51200).
- A file system's `sizeInMiB` is 128 MiB under its volume's `vvSizeInMiB`; its VV has its name.
- A share is served on one File port (`hostip`), and its `mountpath` is
  `/file/<file system>/<share>`. It repeats its client group's `clientInfo`; the parsers read the
  clients from the group only (lesson 41), and a test checks the copies agree.
- `options` is a string; only `root_squash` has been seen.

What the help says that this spec now follows (R4, R5, R8, R10):
- Names: letters, digits, `.`, `-`, `_`, not starting with `-`, up to 255 characters.
- One share per file system. File system size in MB, rounded up to a multiple of 256 MB, at most
  64 TiB; `-reduce` (data reduction) is the default.
- A share setting and a file system must exist before a share. `createfileshare` can also take
  `-ipaddr` and `-option` itself.
- `createsharesetting` always applies `sync, wdelay, sec=sys, subtree_check, secure, hide`, which
  *"cannot be changed"*.
- Removal: `removefileshare` without `-d` only unexports; with `-d` it removes, refused while the
  share holds data. `removefilesystem` is refused while a share is on it, `removesharesetting` while
  a share uses it. Each asks for confirmation unless `-f` (`removesharesetting` lists `-f` under
  OPTIONS but not in its SYNTAX line).

Where it contradicted the research note as first written, as well as the rack13 points above:
- §4 and §8 Q6: there is a file CLI for writes too, not only reads.
- §2 (from S4): share settings carry a secure-port option. The populated record has no such field,
  and the CLI says `secure` cannot be changed.
- §6 lists E18U31 at OS 10.5.0. It now runs 10.5.60 (no File ports).
- S1 gives the path as `/file/<volume>/<share>`. The record says `/file/<file system>/<share>`; the
  file system's volume has the same name, so both read the same.

Still open:
- Which session value the GETs need. Both captures sent the key header and the cookies together;
  the slice 1 client does the same, and a later two-GET probe narrows it (ADR 0021
  *Consequences*).
- Whether the order of `portStatus[]` follows `showport -file`: on D22U27 all four entries are alike.
- The v3 write bodies (research Q4) and task polling (Q5): nothing was written. Whether a share
  create makes its own client group (R10). These wait for the lab probe (ADR 0021 *Before the
  write plane*).
- Whether v3 can make a share setting without `secure` (R4; HPE's CSI driver suggests it can), and
  what `options` looks like with more than one option.
- A snapshot share (no base/snapshot field seen), and any exported flag.
- Whether a licence is required (Q1), and a lab NFS client that reaches 10.54.90.0/21 (Q9).
