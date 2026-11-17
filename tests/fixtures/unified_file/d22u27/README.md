# AlletraMP_D22U27 file side — 2026-11-17 00:16 IST (BL-28)

Read-only capture from AlletraMP_D22U27 (HPE Alletra Storage MP, CZ2D320BT1, 10.64.122.99, two
nodes, OS 10.5.0) by `lab/file_capture.py` at commit `afc2e952` (the one that sends Content-Type
on v3 GETs), run from labrat with the default `CAPTURE_ARRAYS`. SSH ran `show*` and `help` only;
WSAPI v1 and v3 had a login, GETs and a logout. Nothing was created or changed on the array: the
create and remove commands below were only asked for their help.

Scrubbed before commit:
- `/api/v1/system` `contact`: a person's name, phone and email.
- Two object names that read like a person's initials, replaced everywhere they appear (file
  system, its volume, client group, share, mount path) by the placeholders `lab_100` (a file system
  and its client group) and `Lab_test` (a share). The placeholders keep the shape of the originals
  (mixed case, underscore, digits). `fs01`, `share01`, `test1` and `testfile` are as the array has
  them.

The script redacted the login answers (body values, `Set-Cookie` values, the `Location` key). No
password, session key or cookie value is in any file. Every address is a lab address or an example
from HPE's own help text. `shownet.txt` is the same as `../../rc_pair/D22U27/shownet.txt`.

**What it shows: an array with four File ports and the file service on, holding three file systems,
three client groups and three shares.**

- `showport.txt`, `showport_file.txt`: 0:4:1, 0:4:2, 1:4:1, 1:4:2 are Type `file`, all `ready`,
  link up, 10.54.90.70/.71/.73/.74 /21, gateway 10.54.95.254, untagged, MTU 1500.
- `wsapi_v3_fileservice.json`: `isFileServiceEnabled` true; both nodes `fileserviceStatus`
  **`normal`** (the running word); each node two `portStatus` entries, configured, online, MTU 1500,
  still with no port id. `capacitySummary` has only `totalCapacity`, `usedCapacity`,
  `availableCapacity` (5855641, 256000, 5599641). They are MiB: `usedCapacity` is the sum of the
  three file systems' `vvSizeInMiB`. There is no `limitPercentage`, no share or file-system count,
  and no ransomware field: OS 10.5.0 serves WSAPI v3 **2.5.0.1463**, rack13 (10.6.0) 2.6.0.
- `wsapi_v3_filesystems.json`: `fs01` and `lab_100` (`prov` tpvv, `reduce` false, `sizeInMiB`
  102272 on a 102400 MiB volume) and `testfile` (tdvv, `reduce`/`dedupe`/`compression` true, 51072
  on 51200). Each has `sharecount` 1, `fsmaster` 0, `state` `STATE_NORMAL`, `type` XFS, and a
  `volumemembers` map naming the VV under it (same name as the file system).
- `wsapi_v3_filesharesettings.json`: client groups `test1`, `fs01`, `lab_100`, each with one
  `clientInfo` entry `{"ipaddress": "*", "access": "rw", "options": "root_squash"}`, `hostCount` 1,
  `sharecount` 1.
- `wsapi_v3_fileshares.json`: `share01` (on `fs01`, group `fs01`), `Lab_test` (`lab_100`,
  `lab_100`) and `test1` (`testfile`, group `test1`). Each has `mountpath`
  `/file/<file system>/<share>`, `protocol` `["NFS"]` (a list), `hostip` (the File port it is
  served on: 10.54.90.70 or .71), `filesystem {id, fsShortName, name}` and `sharesettings {name,
  clientInfo}` (a copy of the group's clients). No field says base or snapshot, or exported.
- Every collection is `{"version", "arraySerialNumber", "members": {<uid>: record}}`, the key equal
  to the record's `uid`, as on rack13.
- `wsapi_v3_login.json`: the same session answer as rack13 (body `key`, `sessionId`, `username`,
  `arrayPrivileges`; three cookies). The GETs again sent the key header and the cookies together.
- `wsapi_v1_wsapiconfiguration.json`: WSAPI v1 1.15.0. `wsapi_v1_system.json`:
  `licenseState.fileServices` true.
- Help: `help show`, `help create`, `help remove` list the file commands; the help of each is here
  (`help_showfileservice`, `help_showfilesystem`, `help_showfileshare`, `help_showsharesetting`,
  `help_createfilesystem`, `help_createsharesetting`, `help_createfileshare`,
  `help_removefileshare`, `help_removefilesystem`, `help_removesharesetting`). Their SYNTAX lines
  are `FILE_CLI_SYNTAX` in `domain/unified_file.py`. The File Persona names have no help, as on
  rack13.

The first labrat run of the same day (`lab/file_capture.py` before `afc2e952`) also read
AlletraMP_E18U31 (OS 10.5.60) and the VZ array (OS 10.5.51). Neither has a File port (`showport
-file`: *"There is no specified port information."*), and the ten file help texts there are
byte-for-byte the ones here. Their v3 GETs answered **400** `MISSING_MEDIA_TYPE_HEADER` because
that version of the script sent no Content-Type: that says nothing against v3 on 10.5. Those files
are not committed.

Pinned by `tests/unit/test_unified_file_read.py`.
