# D22U27 iSCSI host captures — 2026-10-26 (BL-44)

Read-only capture from AlletraMP_D22U27 (10.64.122.99, CZ2D320BT1, OS 10.5.0.43) by
`lab/iscsi_capture.py`, run from the BGL LabRAT workspace. Show commands and CLI help over SSH, GETs
over WSAPI; nothing was changed on the array. `GET /system` is left out: it carries a person's contact.

What they settled for iSCSI host creation:

- `wsapi_hostpersonas.json`: WSAPI persona ids Generic-ALUA 2, VMware 8, WindowsServer 11 — the ids
  `_WSAPI_PERSONA` sends. The CLI numbers differ (`showhost_listpersona.txt`: VMware 11,
  WindowsServer 15); never send a CLI number to WSAPI.
- `wsapi_hosts.json`: 8 hosts, every one FC or empty; each record has `iSCSIPaths` (empty here).
  The shape of a filled `iSCSIPaths` entry (`name`, `IPAddr`, `hostSpeed`) is in
  `../rack13_wsapi/hosts.json`. No host on either array has both FC and iSCSI paths.
- `help_createhost.txt`: `createhost -iscsi <hostname> <iscsi_name>` takes an IQN the array has never
  seen; `-add` adds a WWN or IQN to an existing host; host names up to 31 characters.
- `help_removehost.txt`: `removehost <hostname>` removes the whole host and refuses one that still
  has an export (so the removal set removes exports first).
- `showport_iscsi.txt`, `showiscsisession.txt`: D22U27 has no iSCSI target port and no session, so
  an iSCSI host made here has no path; its exports are held back by the zoning gate.

The live run of `lab/iscsi_host_lab.py` the same day (run `eba8f3a7`, 17:47 IST) added:

- `wsapi_writes_live.txt`: the three writes from the run's console log; the array answered
  `POST /hosts {"name", "iSCSINames": [IQN], "persona": 2}` with HTTP 201.
- `wsapi_host_zz_is_linux.json`: `GET /hosts/zz_is_linux` right after, the record of a host the tool
  made: `iSCSIPaths[0].name` is the IQN, `IPAddr` a placeholder (`f6ff:ffff:…`), `persona` 2.
- `showhost_d_zz_is_linux.txt`, `showhost_persona_zz_is_linux.txt`: the CLI's view of it, Port `---`
  (not logged in), persona 2 Generic-ALUA. All three objects were removed by the run's removal set.

Pinned by `tests/unit/test_iscsi_hosts.py`.
