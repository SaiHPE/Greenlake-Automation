# SPEC-028 — Unified File: read, check and set up NFS shares on the run's array

**Status:** PROPOSED 2026-11-16; nothing built. R1–R3 can be built once the first capture is in
(work packet BL-28); R4 onward wait for ADR 0021 to be accepted.
**ADRs:** [0021](../adr/0021-unified-file-over-wsapi-v3.md) (proposed) · [0013](../adr/0013-one-array-credential-per-run.md) ·
[0001](../adr/0001-post-init-verification-via-ssh-cli.md) (SSH stays read-only)
**Research:** [2026-11-16-unified-file.md](../research/2026-11-16-unified-file.md)
**Tracker:** BL-28 · **Lab:** AlletraMP_D22U27 (OS 10.5.0, four File ports up)
**Owner:** `adapters/array/wsapi_v3_client.py` (new), `domain/unified_file.py` (new), `application/unified_file/`
(new bounded context: `read.py`, later `plan.py`, `apply.py`, `verify.py`, `steps.py`),
`application/provisioning/discovery.py`, `application/documents/asbuilt*.py`,
`application/platform/init_sheet.py`, `domain/workflow.py`, `frontend/src/steps/`

## 1. Problem

From OS 10.5 a B10000 serves NFS from its own controllers. An engineer who sets up block storage
with this tool sets up file shares by hand in the array UI, and the as-built says nothing about
them. Today Discovery already shows the File ports (`showport -file`), and nothing else.

The work splits in two. Reading what the array has is safe and useful on every array (R1–R3).
Creating shares is a write on a customer array: it waits for the decision (ADR 0021) and follows
the plan → approve → apply pattern of provisioning (R4–R10).

## 2. Which API, and the overlap with BL-29

The tool configures B10000 file over the **array's own WSAPI v3** (ADR 0021). It does **not**
configure through the GreenLake File Storage API, even though that API has `devtype4` (B10000)
share and file-system calls and BL-29 found it too (its research §3). Checked against the OpenAPI
bundle on 2026-11-16: on `devtype4` share settings are GET-only and `settingName` is required to
create a share, so the first share on a new array cannot be made through the cloud; the file
service cannot be started there; deleting a share also deletes its file system and share setting;
and it needs regional cloud access and `file-storage.*` workspace permissions the lab does not have.

The shared adapter is **`adapters/greenlake/file_storage.py`** (BL-29's name, device type as a
parameter, built by whichever branch comes first; BL-29 is first, read-only). BL-28 uses it only
to *read* `devtype4` in a later slice, for an as-built line "what GreenLake sees", never to write.
BL-29 stays on `devtype7` (X10000). One share is never written by two planes.

## 3. Requirements

### Reads (slice 1)

**R1 — Read the file side of the array.** Over WSAPI v3 with the run's array credential:
`GET /api/v3/fileservice`, `/api/v3/filesystems`, `/api/v3/filesharesettings`, `/api/v3/fileshares`.
Over the read-only SSH client (already allowlisted): `showversion`, `showport`, `showport -file`.
The result is a `FileReport` (`domain/unified_file.py`):

| Part | Fields (from the WSAPI v3 schema; the first capture decides which are present on 10.5.0) |
|---|---|
| Service | enabled (`isFileServiceEnabled`); per node: status (`fileServiceSummary[].fileserviceStatus`) and its ports (`portStatus[]`: configured, online, MTU); capacity limit % and used/available (`capacitySummary`); counts of file systems and shares |
| File ports | from `showport -file`, as Discovery reads them today (`parse_file_ports`, unchanged) |
| File systems | name, size MiB, data reduction (`reduce`), share count, state, owner node (`fsmaster`) |
| Share settings | name, clients: address, `ro`/`rw`, squash, secure port |
| Shares | name, file system, share setting, protocol, mount path, state, type (base or snapshot) |

Each WSAPI call and SSH command goes to the command log (SPEC-019); the password and session key
never do. Parsers are pinned to the D22U27 capture before any other code (work packet step 2).

**R2 — Say plainly when there is nothing to read.** One sentence each, never an error that stops
Discovery:
- OS older than 10.5: *"This array runs OS 10.4.x. File shares need OS 10.5 or later."*
- WSAPI v3 does not answer: *"The array did not answer on its file API, so only the File ports
  are shown."* (Lesson 27: any structured answer, including 401 or 404, means it answered.)
- File service off: *"The file service is off on this array. Turn it on in the array's UI before
  shares can be made."* Its ports are still listed.
- No File ports: nothing is shown (most block arrays).

**R3 — Show it, and put it in the as-built.** Discovery's *file service ports* section becomes
*File service* with four folded parts (service, ports, file systems, shares with their clients).
The as-built gains a *File service* section after the provisioning record, read when the document
is made (the SPEC-018 pattern); absent when the array has no File ports and the service is off.
Verify configuration adds the service state and the File ports to its table, read-only.

### Configure (slices 2 and 3, after ADR 0021 is accepted)

**R4 — A new, optional workbook tab "File".** Parsed only when present and non-blank; every
existing workbook parses as today (SPEC-015 R1 pattern).

| Section | Columns | Default / rule |
|---|---|---|
| *File service* | Expected state (on / off) | on. Checked, never changed (ADR 0021 item 4). |
| *File ports* | N:S:P · Address · Prefix length · VLAN · Gateway · MTU | Checked against `showport -file`, never written. Blank section = not checked. |
| *Client groups* (one row per client) | Group name · Client (address, CIDR or `*`) · Access (`rw`/`ro`) · Squash (`root_squash` / `no_root_squash` / `all_squash`) · Secure ports only (yes/no) | Access `rw`; squash `root_squash`; secure **yes**. A group is a WSAPI *file share setting*. |
| *Shares* (one row per share) | Share name · File system · Size (GiB) · Data reduction (yes/no) · Client group | Data reduction **yes** (sent explicitly). Protocol is NFS and not a column. |

Words on the sheet and screen: *client group*, not *share setting*; *share*, *file system*.

**R5 — Validation at upload (blocking, one sentence each).**
- A share's client group is not on the tab; a client group has no client row (lesson 36: a blank
  never means everyone). `*` is accepted only when typed, and then shown as *any host that can
  reach the File ports*.
- Size under 1 GiB or over 64 TiB (research §2).
- More shares than the array allows: 32 on a two-node array, 64 on four or more (checked at step
  time, when the node count is read).
- The same share name twice; an empty share or file system name, or one with a space. The array's
  own name rule is *unconfirmed*; the first refused create pins it as a sentence here.
- A value outside the lists above (access, squash, yes/no).

**R6 — Check (blocking findings at step time).** File service on, and every node `fileserviceStatus`
running; at least one File port online per node; the sheet's File ports match `showport -file`
(address, prefix, VLAN, gateway, MTU), each mismatch one row; capacity: the sum of new shares fits
under the service's limit and the CPG free space (`showspace` is allowlisted); share count within
R5's limit.

**R7 — Plan (SPEC-001: exists / create / conflict).** Per client group, file system and share:
absent → **create**; present and the same → **exists**; present and different (other clients,
size, file system, group) → **conflict**, never changed. The plan lists each create as the WSAPI
v3 call it will make.

**R8 — Approve and apply.** Nothing is written until the operator ticks *"I have reviewed this plan
and authorise creating these file shares on the array"* and clicks *Create file shares* (the
provisioning gate). The approval is withdrawn if the tab, the read or the plan changes (lesson 6).
Order: client groups (`POST /api/v3/filesharesettings`) → file systems → shares, with the export if
the share is not exported on create. The exact body of the file system and share create (the
`CREATE_COMPLEX_FILE_SHARE` sub-actions, research §8 Q4) is fixed by the first live probe and
pinned in a test (lesson 28). Wait for a 202 task to finish before the next call. Stop at the first
failure, say which call and the array's message.

**R9 — Verify (read-only).** Read back: each share present, state normal, exported, on the planned
file system and client group, clients as planned; the file system's size and data reduction. Verdict
per share: **Ready** · **Not ready (reason)**. The tool does not mount the share from a host (hosts
are read-only for the tool); the step prints the mount line for the engineer to try:
`mount -t nfs4 <File port address>:<mount path> <dir>` with the mount path read from the share.

**R10 — Removal set (SPEC-007, text the tool never runs).** What this run created, in reverse
order: shares, then file systems, then client groups. Shown as the array's CLI lines once a capture
confirms them, otherwise as the WSAPI v3 calls and the array UI page (ADR 0021 item 5). Objects that
were there before the run never appear.

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

**Before code — the first capture (read-only, on D22U27; the owner runs it).** `showversion`,
`showport`, `showport -file`, `help` (the command index, to find any file `show` command),
`showlicense`; WSAPI v3: `POST /api/v3/credentials`, the four GETs of R1, `GET /api/v3/ports`, then
the session deleted. Saved to `tests/fixtures/d22u27_file/` with a README of the facts. Answers
research §8 Q1–Q3 and Q6.

**Unit.** Parsers on the capture; R2's four sentences; R5 rule per sentence; R6 findings; R7
exists/create/conflict; R8 order and stop-at-first-failure against a stub that models the vendor's
real refusals; R10 order and "never the pre-existing objects"; registry and 422 gate (R11).

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
