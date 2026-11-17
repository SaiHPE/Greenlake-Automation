# ADR 0021 — Unified File is read through the array's own WSAPI v3; the write plane follows a lab probe

**Status:** accepted 2026-11-17 (owner's decision) for reads (items 1 for reads, 2, 4, 5, 7); the
write plane (items 1 and 3) waits for an amendment after an approved lab probe on D22U27 (zz_fs_*:
one v3 create and its task). Proposed 2026-11-16 ·
**Research:** [2026-11-16-unified-file.md](../research/2026-11-16-unified-file.md) · **Spec:**
[SPEC-028](../specs/SPEC-028-unified-file.md) · **Tracker:** BL-28 · **Keeps:** ADR 0001 (array SSH
read-only), ADR 0006 (hybrid control plane), ADR 0013 (one array credential per run), SPEC-007 R4
(the tool never runs a removal) · **Any SSH write:** ADR 0025 (one rule for every write over the
array's SSH)

## Context

From OS 10.5 a B10000 serves NFS from its own controllers ("Unified File", research §2). Its objects
are a file service, file systems, file share settings (client groups) and file shares. Five
interfaces reach them (research §4). What the first two do on a real array comes from two read-only
captures, rack13-ARCUS on OS 10.6.0 and AlletraMP_D22U27 on 10.5.0 (*Evidence*):

- **WSAPI v3** on the array (`/api/v3/fileservice`, `/filesystems`, `/filesharesettings`,
  `/fileshares`). Both lab arrays serve all four reads on port 443 with the run's array credential.
  OS 10.5.x refuses a GET without `Content-Type: application/json`. Its
  OpenAPI also lists writes for every object, file-system snapshots and schedules, but nothing has
  been written: the share-create body (`CREATE_COMPLEX_FILE_SHARE` and its sub-actions) and how a
  write's task is named and polled are unknown (LESSONS 28). It is a new API for this tool: today's
  WSAPI client speaks v1 through `hpe3parclient` and has no file resource.
- **Array CLI over SSH.** `showport -file` shows the File ports, and Discovery already reads it.
  The CLI also shows, creates and removes file systems, client groups and shares
  (`showfilesystem`, `createfilesystem`, `createsharesetting`, `createfileshare`,
  `removefileshare`, `removefilesystem`, `removesharesetting` and the rest); their syntax is pinned
  from `help` on three arrays (D22U27, E18U31, the VZ array). `createsharesetting` always applies
  `secure`, which *"cannot be changed"*. `controlport config file` and `controlport file
  addr|gw|mtu|state` set the File ports; moving a port into or out of File mode needs `-sysreboot`
  and **reboots the array**.
- **GreenLake File Storage API** (`devtype4`, v1alpha1, since 2026-09). It can create a share only
  with a share setting that already exists (share settings are read-only there) and cannot enable
  the service. It needs a regional cloud client and workspace `file-storage.*` permissions the lab
  does not have. HPE's versioning guide says of alpha APIs: *"No guarantees on backward
  compatibility"*.
- **GreenLake Storage Fleet API**: reads the file flags and File ports; its system-settings edit
  carries an `enableFile` field its own description does not list.
- **The array UI and DSCC UI**: everything, by hand.

## Decision

Items 1 (for reads), 2, 4, 5 and 7 are accepted. Items 1 (for writes) and 3 are the write plane:
they wait for the amendment described in *Before the write plane*. Item 6 is not part of the
acceptance; nothing through SPEC-028 slice 3 needs a cloud adapter.

1. **WSAPI v3 is the read plane.** Every file read goes to the run's array over
   `https://<array>/api/v3`, logged in with the run's one array credential (ADR 0013), with
   `Content-Type: application/json` on every request. A new adapter,
   `adapters/array/wsapi_v3_client.py`, separate from the v1 client, does GET, login and logout
   only. **A read of another array is refused** (AGENTS rule 4): every v3 collection names its
   `arraySerialNumber`, and when that is missing or differs from the serial `showsys` prints, none
   of the read is shown, stored or put in the as-built, and Discovery says so in one sentence
   (SPEC-028 R2). A write slice stops on the same mismatch before its first write.
   *For writes (not yet accepted):* v3 is the proposed write plane and the write-scoped CLI is the
   fallback (*Alternatives*). The amendment chooses between them on the probe's evidence. Each write
   method is added by the slice that needs it, with a test and a sentence in the pull request
   (AGENTS, *Things an agent must not do*).
2. **Reads first.** Discovery, Verify and the as-built read the file service, file systems, client
   groups, shares and File ports. They change nothing (hard rule 3).
3. **Writes only through an approved plan** (not yet accepted). Client groups, file systems and
   shares are created by the SPEC-001 pattern: read → plan (exists / create / conflict) → the
   operator ticks the authorisation → apply in a fixed order, stop at the first failure → read back.
   An approval is withdrawn when its inputs change (lesson 6). The tool never changes or deletes an
   object it did not create in this run.
4. **Never from the tool:** putting a port in or out of File mode (`controlport config file`
   needs `-sysreboot`, which reboots the array); enabling or stopping the file service until a live
   capture shows what it disrupts; File interface addresses, gateway and MTU (WSAPI v3 has no File
   port edit; the CLI path would be a new SSH write kind, which ADR 0025 says needs its own ADR, and
   ADR 0025 condition 4 does not allow a change that needs a reboot). The tool reads these and says
   what is missing, with the array's own command or the UI page to fix it. Any hint that names
   `controlport config file` says plainly that it reboots the array.
5. **The removal set stays text** (SPEC-007 R4). It lists the objects the run created, in reverse
   order, as the array's CLI lines: `removefileshare -d -f <file system> <share>`, then
   `removefilesystem -f <file system>`, then `removesharesetting -f <client group>`. The tool does
   not run it. An object the array made on the run's behalf (see *Before the write plane*) is an
   object the run created and is listed.
6. **No cloud writes for B10000 file.** The GreenLake File Storage API's `devtype4` paths reach the
   same objects; the tool never creates, changes or deletes through them. BL-28 needs no cloud
   adapter through SPEC-028 slice 3. A later slice may *read* `devtype4` for an as-built line ("what
   GreenLake sees"). If that slice is built, BL-28 and BL-29 (deferred 2026-11-17) share only the
   regional GreenLake HTTP client and its paging, not the share models: the payloads differ
   (`devtype4` shares have a `name`, a `settingName` and `hostAccess[]`; `devtype7` shares have a
   `path`, no name, and `accessClients[]`). One run never has two planes writing the same share.
7. **NFS only.** SMB, Active Directory, LDAP and DNS for file are not in any HPE source read
   (research §2). They are out until one is.

## Before the write plane

The amendment that settles items 1 (writes) and 3 needs, in this order:

1. **An approved lab probe on D22U27**, objects named `zz_fs_*`: one v3 create and its task,
   removed by hand afterwards. It records the body the array accepts (`CREATE_COMPLEX_FILE_SHARE`
   or the separate sub-actions, research §8 Q4), how a 201 or 202 names its task and how the task
   ends (Q5), and pins both in a test (LESSONS 28).
2. **Whether a share create makes its own client group.** On D22U27 the client groups are one per
   share, each named after its share or file system. If the array makes one, it is an object the
   plan did not name, and the removal set must list it.
3. **Whether v3 can turn `secure` off.** HPE's CSI driver documents `shareSourcePorts: insecure`
   for B10000 file (research S1, read 2026-11-17); the array's CLI says `secure` *"cannot be
   changed"*. SPEC-028 R4's *secure ports* column stays only if v3 can.
4. **A lab NFS client that reaches 10.54.90.0/21**, for the mount in SPEC-028's slice 3 checklist.

## Alternatives

- **The GreenLake File Storage API.** One API for B10000 and X10000, and the async pattern the tool
  already polls. Rejected for configuring B10000 file: on `devtype4` share settings are read-only
  and `settingName` is required to create a share, so the first share on a new array cannot be made
  through it; it cannot start the file service; deleting a share also deletes its file system and
  share setting, so a removal cannot be partial; it needs regional cloud access and workspace
  permissions (`file-storage.file-share.create`) the lab does not have (ADR 0006 *gatekeepers*); it
  is v1alpha1, with *"No guarantees on backward compatibility"*. Revisit if it gains share-setting
  create.
- **The CLI over a write-scoped SSH client: the fallback for the write plane.** Not rejected. For
  it: the syntax of every create and remove is pinned from `help` on three arrays
  (`FILE_CLI_SYNTAX`), and the removal set is CLI lines already, while the v3 share-create body and
  its task polling are unknown until the probe (LESSONS 28). Against it: a second plane beside the
  v3 reads, a new SSH write kind, and `secure` that cannot be turned off. If the amendment picks
  it, it follows ADR 0025 in full: exact whole-command forms with tests for their near-misses, a
  client built only inside an approved apply and only for the plan's objects, each removal line
  written before its command is sent, a read-back after each write, `-f` on every form that asks
  for confirmation (a form that may still prompt is captured live first), and the amendment is the
  ADR that names this client kind and its forms.
- **Leave file to the array UI and only document it.** Keeps the tool small; loses the as-built and
  the repeatable share layout the scope asks for. It remains the route for everything item 4 keeps
  out of the tool.

## Consequences

- A second WSAPI client and its session. The login (`POST /api/v3/credentials`) answers with a body
  `key` and three cookies. The client sends the key as `X-HP3PAR-WSAPI-SessionKey` and the cookies
  together, as both captures did; a later two-GET probe (one GET with each) narrows it. It always
  deletes the session (`DELETE /api/v3/credentials/<key>`), also when a read fails. Every call goes
  to the command log; the password and session never do. Its readiness gate is lesson 27: any
  structured answer means alive.
- Every v3 request carries `Content-Type: application/json`, GETs included: OS 10.5.x refuses a GET
  without it (400 `MISSING_MEDIA_TYPE_HEADER`).
- Operators get a removal set they paste or click through, not one the tool runs.
- SCOPE area 6 stays *Partial* even when SPEC-028 is built: enabling the file service, File port
  mode and snapshots are excluded (item 4; snapshots go with BL-21).
- Risks:
  - **A wrong session value makes every read 401.** Discovery shows that as a note (SPEC-028 R2),
    never as a failure, and the block side is not affected.
  - **The cloud API may change under us** (v1alpha1). Only a later cloud read (item 6) depends on
    it; nothing in slices 1 to 3 does.
  - **Port mode reboots the array.** The tool never sends it (item 4), and any hint naming
    `controlport config file` says so.

## Evidence since the proposal

**rack13-ARCUS, OS 10.6.0, 2026-11-16** (read-only capture, `tests/fixtures/unified_file/rack13/`;
the facts are in SPEC-028 §8). An array with no File ports and the file service off.

- **Item 1 holds on 10.6.0.** WSAPI v3 answers on `https://<array>/api/v3` (port 443) and accepts
  the run's array credential, the same one v1 takes. All four file GETs answer 200 (server
  2.6.0.1895), even with no File ports.
- **The session.** The login answers 201 with a body `key`, a `Location` naming it, and the cookies
  `sessionToken`, `hpeWsapiSentryLineage` and `hpeWsapiSentryUsername`. The capture sent the key
  header and the cookies together, so either may be the one that counts. Logout is
  `DELETE /api/v3/credentials/<key>` (200).
- **A file CLI exists for reads.** `help show` lists `showfileservice`, `showfilesystem`,
  `showfileshare` and `showsharesetting`; the research note had said none was confirmed. Reads stay
  on v3, one source per fact.
- **Item 4 holds.** `help controlport` on 10.6.0 still requires `-sysreboot` to move a port into
  or out of File mode.

**AlletraMP_D22U27, OS 10.5.0, 2026-11-17** (read-only, `tests/fixtures/unified_file/d22u27/`;
SPEC-028 §8). Four File ports, the service on, three file systems, client groups and shares.

- **Item 1 holds on 10.5.0.** WSAPI v3 2.5.0.1463 serves all four file resources on 443 with the
  array credential, provided each GET carries `Content-Type: application/json`. Without it 10.5.x
  answers 400 `MISSING_MEDIA_TYPE_HEADER` (D22U27, E18U31 10.5.60 and VZ 10.5.51 on the day's first
  run). Those 400s were the missing header, never evidence that 10.5 lacks v3. Version 2.5.0 sends
  fewer fields than 2.6.0 (no capacity limit, counts or ransomware flags); the parsers treat those
  as optional.
- **The records are pinned.** File systems, share settings (client lists) and shares with their
  real fields, a running node's status (`normal`) and the capacity unit (MiB). Every collection's
  `arraySerialNumber` equals the serial `showsys` prints, on both arrays (item 1's refusal).
- **A file CLI exists for writes too.** `createfilesystem [-tpvv|-reduce] <name> <size>[g|G|t|T]`,
  `createsharesetting [-add <ipaddr_list>? <options for host access>] sharesetting_name`,
  `createfileshare [options] <filesystem_name> <share_name>`, and `removefileshare [options]
  <filesystem_name> <share_name>`, `removefilesystem [options] <name>`, `removesharesetting
  <sharesetting_name>`. **Item 5** gives CLI lines: share (`-d`), then file system, then client
  group, each with `-f`. The help texts are the same on E18U31 and VZ. This ADR adds none of these
  commands to an allowlist.
- **What the CLI help fixes for SPEC-028.** One share per file system; names of letters, digits,
  `.`, `-` and `_`; `secure` always applied and *"cannot be changed"* (so a *secure ports* choice on
  the sheet holds only if v3 can turn it off; see *Before the write plane*).

Still open: which session value the reads need (both captures sent the key header and the cookies;
the client sends both until the two-GET probe); every write body and its task, and whether a share
create makes its own client group (*Before the write plane*); whether `portStatus[]` follows
`showport -file`.
