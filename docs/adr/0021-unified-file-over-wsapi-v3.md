# ADR 0021 — Unified File is read and configured through the array's own WSAPI v3

**Status:** PROPOSED 2026-11-16 (needs the owner's yes before SPEC-028 R5 onwards is built) ·
**Research:** [2026-11-16-unified-file.md](../research/2026-11-16-unified-file.md) · **Spec:**
[SPEC-028](../specs/SPEC-028-unified-file.md) · **Tracker:** BL-28 · **Keeps:** ADR 0001 (array SSH
read-only), ADR 0006 (hybrid control plane), ADR 0013 (one array credential per run), SPEC-007 R4
(the tool never runs a removal)

## Context

From OS 10.5 a B10000 serves NFS from its own controllers ("Unified File", research §2). Its objects
are a file service, file systems, file share settings (the client list) and file shares. Five
interfaces reach them (research §4):

- **WSAPI v3** on the array (`/api/v3/fileservice`, `/filesystems`, `/filesharesettings`,
  `/fileshares`): reads and writes for every object, file-system snapshots and schedules, and the
  File port record. It is a new API for this tool: today's WSAPI client speaks v1 through
  `hpe3parclient` and has no file resource.
- **Array CLI over SSH**: `showport` shows File ports; `controlport config file` and `controlport
  file addr|gw|mtu|state` set them. Putting a port in File mode **reboots the array** (`-sysreboot`,
  *"following array reboot"*). No CLI for file systems or shares is confirmed.
- **GreenLake File Storage API** (`devtype4`, v1alpha1, since 2026-09): can create a share only with
  a share setting that already exists (share settings are read-only there), cannot enable the
  service, and needs the DSCC client the tool does not have, plus workspace permissions.
- **GreenLake Storage Fleet API**: reads the file flags and File ports; its system-settings edit
  carries an `enableFile` field its own description does not list.
- **The array UI and DSCC UI**: everything, by hand.

## Decision (proposed)

1. **WSAPI v3 is the file plane.** Every file read and write goes to the run's array over
   `https://<array>/api/v3`, logged in with the run's one array credential (ADR 0013). A new adapter,
   `adapters/array/wsapi_v3_client.py`, separate from the v1 client. Its methods are a fixed list:
   GETs first; each write method is added by the spec slice that needs it, with a test and a
   sentence in the pull request (AGENTS, *Things an agent must not do*).
2. **Reads first.** Discovery, Verify and the as-built read the file service, file systems, share
   settings, shares and File ports. They change nothing (hard rule 3).
3. **Writes only through an approved plan.** Share settings, file systems and shares are created
   by the SPEC-001 pattern: read → plan (exists / create / conflict) → the operator ticks the
   authorisation → apply in a fixed order, stop at the first failure → read back. An approval is
   withdrawn when its inputs change (lesson 6). The tool never changes or deletes an object it did
   not create in this run.
4. **Never from the tool:** putting a port in or out of File mode (it reboots the array); enabling
   or stopping the file service until a live capture shows what it disrupts; File interface
   addresses, gateway and MTU (WSAPI v3 has no File port edit; the CLI path would be a new SSH write
   path, which needs its own ADR as ADR 0015 did). The tool reads these and says what is missing,
   with the array's own command or the UI page to fix it.
5. **The removal set stays text** (SPEC-007 R4). It lists the objects the run created, in reverse
   order, as the CLI lines once `help` on the array confirms a file CLI, otherwise as the WSAPI v3
   calls and the array UI page. The tool does not run it.
6. **No cloud writes for B10000 file.** The GreenLake File Storage API's `devtype4` paths reach the
   same objects. BL-29 (GreenLake for File, ADR 0022, SPEC-029) builds the shared cloud adapter,
   `adapters/greenlake/file_storage.py`, with the device type as a parameter. BL-28 may *read*
   `devtype4` through it in a later slice (what the cloud sees, for the as-built); it never creates,
   changes or deletes through it, and BL-29 stays on `devtype7`. One run never has two planes
   writing the same share.
7. **NFS only.** SMB, Active Directory, LDAP and DNS for file are not in any HPE source read
   (research §2). They are out until one is.

## Alternatives

- **The GreenLake File Storage API** (BL-29's research reached the same API independently). One
  API for B10000 and X10000, the async pattern the tool already polls, and an adapter BL-29 will
  build anyway. Rejected for configuring B10000 file: on `devtype4` share settings are read-only and
  `settingName` is required to create a share, so the first share on a new array cannot be made
  through it; it cannot start the file service; deleting a share also deletes its file system and
  share setting, so a removal cannot be partial; it needs regional cloud access and workspace
  permissions (`file-storage.file-share.create`) the lab does not have today (ADR 0006
  *gatekeepers*); v1alpha1. Revisit if it gains share-setting create.
- **CLI over a write-scoped SSH client** (ADR 0015's pattern). Rejected: no file-system or share
  CLI is confirmed, and the port commands that are confirmed are the disruptive ones.
- **Leave file to the array UI and only document it.** Keeps the tool small; loses the as-built
  and the repeatable share layout the scope asks for. Kept as the fallback if the first capture
  shows the lab array cannot serve WSAPI v3.

## Consequences

- A second WSAPI client and its session handling (cookie session from `POST /api/v3/credentials`;
  record every call in the command log, password never). Its readiness gate is lesson 27: any
  structured answer means alive.
- The first live probe of every write body is recorded in a test (lesson 28). The `CREATE_COMPLEX_FILE_SHARE`
  envelope is not known until then.
- Operators get a removal set they paste or click through, not one the tool runs.
- If the lab array does not serve WSAPI v3, SPEC-028 stops after the read slice that works over
  `showport` and the owner decides between the cloud API and the UI.
