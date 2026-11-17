# rack13-ARCUS file side — 2026-11-16 23:27 IST (BL-28)

Read-only capture from rack13-ARCUS (HPE Alletra Storage MP B10230, CZ2D2K014S, 10.132.30.121,
two nodes, OS 10.6.0) by `lab/file_capture.py` with `CAPTURE_ARRAYS=rack13=10.132.30.121`. SSH ran
`show*` and `help` only; WSAPI v1 and v3 had a login, GETs and a logout. Nothing was changed on the
array. Scrubbed before commit: the person named in `/api/v1/system` `contact`. The script itself
redacted the login answers (body values, `Set-Cookie` values, the `Location` key). No password,
session key or cookie value is in any file (`test_unified_file_read.py` checks the cookies and keys).

**What it shows: an array with no File ports. Its WSAPI v3 file resources answer anyway, and are
empty.**

- `showport_file.txt`: *"There is no specified port information."* `showport.txt` has no port of
  Type `file`: 0:4:1 and 1:4:1 are iSCSI, 0:4:2 and 1:4:2 free iSCSI, 0:4:3-4 and 1:4:3-4 free IP.
- `wsapi_v3_fileservice.json`: HTTP 200. One member, keyed by its `uid`. `isFileServiceEnabled`
  false; each node's `fileserviceStatus` is `stopped`; each node lists two `portStatus` entries
  (`isFilePortConfigured` false, `isFilePortOnline` false, `mtu` 0) **with no port id**;
  `capacitySummary` all zero (so the unit is not shown); `displayname.default` is *"File Service on
  2FF70002AC02D495"*, the system WWN that `showport` prints as the FC Node_WWN.
- `wsapi_v3_filesystems.json`, `wsapi_v3_filesharesettings.json`, `wsapi_v3_fileshares.json`:
  HTTP 200, `{"version", "arraySerialNumber", "members": {}}`. An empty collection is an empty
  **map**, not a list. No member of these three has been seen yet, so their fields are not pinned.
- Every v3 answer carries `X-Server-Version: 2.6.0.1895` (the OpenAPI 2.6.0 the research read) and
  `arraySerialNumber` `CZ2D2K014S`, the serial `showsys` prints.
- `wsapi_v3_login.json`: `POST /api/v3/credentials` on port 443, HTTP 201. Body fields `key`,
  `sessionId`, `username`, `arrayPrivileges`; header `Location: /api/v3/credentials/<key>`; three
  cookies, `sessionToken`, `hpeWsapiSentryLineage`, `hpeWsapiSentryUsername`. The GETs sent both
  the body `key` (as `X-HP3PAR-WSAPI-SessionKey`) and the cookies, so which one the array needs is
  still open. `wsapi_v3_logout.json`: `DELETE /api/v3/credentials/<key>` answered 200, empty body.
- `wsapi_v1_wsapiconfiguration.json`: WSAPI v1 1.16.0, HTTPS on 443, HTTP off.
  `wsapi_v1_system.json`: `licenseState.fileServices` is true.
- `help_show.txt` lists four file show commands: `showfileservice`, `showfileshare`,
  `showfilesystem`, `showsharesetting`. The first three have their help here (`help_showfile*.txt`);
  `help showsharesetting` was not asked. The old 3PAR File Persona names (`showfs`, `showfpg`,
  `showvfs`, `showfshare`, `showfstore`) answer *"No help for …"*. `help -sub` is not a form of help
  (*"No help for -sub"*); `help help` is the same index as `help`.
- `help_controlport.txt`: on 10.6.0, as on 10.5.x, `-sysreboot` *"is required only when switching out
  of or into File mode"*.
- `report.txt`, `_index.txt`: the script's own summary. Its counts read *"?"* because it expected
  `members` to be a list; the bodies above are the answer (all zero).

Not here: an array **with** File ports and a running service. That is AlletraMP_D22U27 (OS 10.5.0,
four File ports), in `../d22u27/` (2026-11-17). OS 10.6.0 answered the v3 GETs without a
Content-Type header; OS 10.5.x refuses them with 400 `MISSING_MEDIA_TYPE_HEADER`.

Pinned by `tests/unit/test_unified_file_read.py`.
