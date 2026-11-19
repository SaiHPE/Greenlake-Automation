# Lab scripts

Scripts that drive the app against the real lab arrays, run on a lab jump box after
`scripts/push_jumpbox_test.sh` (README, *A live run on a jump box*). They are not part of the app,
the release zip or the lint gate. Each one says at the top what it reads and what it changes.

**Before running one:** book the lab, read its header, and put the lab passwords in the jump box's
`.env` once (`LAB_ARRAY_PW`, `LAB_DEFAULT_PW`; read by `rc_failover_lab.lab_secret()`). Never write a
password into a script. Results go to `~\Downloads\<name>.zip`.

**Writing a new one:** copy the closest script below, import `rc_failover_lab as fl` for SSH, the
app API and saving evidence, keep it free of prompts, give everything it creates a `zz_<initials>_`
prefix, and remove all of it at the end.

| Script | What it checks | Changes the arrays? |
|---|---|---|
| `ui_live_lab.py` | Every page of the app at 1366 and 1080 wide, on a run with real discovery, zoning, plans, verify and as-built (BL-43) | No |
| `ui_provision_lab.py` | The Provision storage page creates objects through its own buttons, then removes them (BL-43). `UI_SHEET` + `UI_HOST` run it from any machine that reaches the array; a host zoned on one fabric only has its export held back and checked as such | Yes, `zz_ui_*` (and the host, when the array did not have it) on D22U27 or the workbook's array, removed at the end |
| `rc_peer_ready.py` | Whether the peer array can be the replication partner of D22U27 | No |
| `rcip_pair_capture.py` | The Alletra MP 10.132.30.121 + Primera 10.132.30.28 pair before replication setup: planned RCIP ports today (role, link, hosts on them), licences, Remote Copy state, CLI help of the setup commands (BL-41) | No |
| `rcip_setup_lab.py` | `setup`: RCIP addresses on the Alletra (0:4:4/1:4:4), ping, startrcopy, a target each way, links Up; `undo`: reverses every change from its journal; `undo-setup`: reverses only the partnership, so the tool can set it up again (BL-41) | Yes, both arrays; `undo` restores them |
| `rcip_pair_lab.py` | The app's Replication steps (preview, link check, apply, verify, failover test, as-built) on the Alletra MP -> Primera pair, then its removal sets (BL-41) | Yes, `zz_rc_*` on both arrays, removed at the end |
| `rcip_tool_lab.py` | From a pair with no partnership (after `rcip_setup_lab.py undo-setup`): the tool sets up the RCIP ports and the partnership from the Replication network tab, then groups, link check, verify (each group's `showrcopy -d` settings and volumes, the raw reads saved), failover test, as-built (no performance, no `srstat*` read); pastes the run's merged removal set and checks the pair is back at the start; `RCIP_MODE=async` for a periodic row, RPO 10 min; `RCIP_NET=routed` puts this array's ports on a /28 behind the lab router 10.93.18.1 (BL-41). Sync when this array's OS refuses sync to the peer's (rack13 on 10.6 to the Primera's 4.x, BL-62): expects the one blocker at the first read, the apply refused and no write by the run; only its own `zz_rc_vol01` / `zz_rc_vvs` are made and removed | Yes, both arrays; removed at the end |
| `rcip_scope_lab.py` | The in-scope paths beyond the happy path, on the Alletra MP -> Primera pair: mixed sync/async rows refused before any write; a stopped apply (ping fails) and its removal set; the link check with the Primera's gateway on (must report the links it broke) and the way back; the peer's addresses and Remote Copy set up by the tool; the failover test on a group the run did not create (typed confirmation) (BL-41) | Yes, both arrays; the Primera's own settings journaled and restored |
| `failed_apply_lab.py` | A 1 PiB volume, a volume name with a `+` and a volume set name with a `+` upload, are listed by the upload, and refuse a Provision only run with that sentence, so no run is made (BL-55, help createvv, BL-60); a provisioning apply that stops half-way (a volume set name of 256 characters: the tool does not check a set name's length, the array is expected to refuse it; not yet seen live) keeps the commands to undo what it made, on the page, after a rebuild and in the as-built; the Console refuses `showtarget -rescan` (BL-45, BL-46). `FA_SHEET` + `FA_HOST` run it from any machine that reaches the array | Yes, `zz_bl45_*` (and the host, when the array did not have it) on D22U27 or the workbook's array, removed at the end |
| `iscsi_capture.py` | What D22U27 holds for iSCSI hosts: ports, sessions, hosts with an IQN, personas, `createhost` help (BL-44) | No |
| `iscsi_host_lab.py` | The app creates an iSCSI host from its IQN (lab Linux host), plans again, then removes it (BL-44) | Yes, `zz_is_*` on D22U27, removed at the end |
| `iscsi_lun_lab.py` | `IS_SHEET` + `IS_IQN`: the app creates an iSCSI host from the IQN of a server logged in to the array (persona from its OS), presents a 1 GiB LUN to its host set, reads it back, verifies the path, writes the as-built, then runs the run's removal set (BL-44) | Yes, `zz_is_*` on the workbook's array, removed at the end; the server sees the LUN while it is presented, nothing is done on it |
| `iscsi_port_probe.py` | Which lab array (D22U27, the CRV VZ array; LZ pinged only) has iSCSI ports with a link, and which lab networks this workspace reaches (BL-44) | No |
| `multipath_capture.py` | What `multipath -ll` prints on the lab Linux host (as the login, and through `sudo -n`), with exit codes, and the app's one-line summary of it; the capture that replaces the documented samples in `tests/fixtures/linux_multipath/` (BL-36) | No (nothing on the host either) |
| `snap_capture.py` | What D22U27 holds for snapshots and schedules: `showsched`, snapshot columns of `showvv`, the time zone, the help of `createsched`, `createsv`, `removesched`, `setsched`, `showsched`, `removevv`; WSAPI volumes and sets, and whether `GET /schedules` exists (BL-21, SPEC-023). Also `help createvv`, for the largest volume the array creates (BL-55) | No |
| `handover_capture.py` | What each array in `CAPTURE_ARRAYS` (default D22U27) says about its alerts (`showalert`, `showalert -d`), capacity (`showsys -space`), `checkhealth`, and 24 hours of System Reporter (`srstatcpu`, `srstatport`, `srstatvv`, `srstatrcvv`, plain and in the as-built's own form), plus their CLI help; sends only show, srstat, checkhealth and help commands, files named for `tests/fixtures/handover/<TAG>/` (BL-24) | No |
| `iscsi_vlan_capture.py` | What E18U31 and D22U27 show for iSCSI ports and their VLAN interfaces (`showport -iscsi`, `showport -iscsivlans`, `help controliscsiport`, WSAPI `/ports/<n:s:p>/iSCSIVlans/`), named as the fixtures SPEC-024's tests expect (BL-25) | No |
| `peer_port_capture.py` | FC ports on E18U31 (has peer ports) and D22U27: `showport -par`, `-peer`, `-c`, logins per port, WSAPI `GET /ports`, `controlport` help; the fixtures the peer-port tests wait for (BL-26, not yet run) | No |
| `mig_pair_capture.py` | A migration pair before the Migration step reads it: on the source (the lab's 3PAR 20850 R2) `showsys`, `showversion -a -b`, ports, hosts and host sets, volumes and sets, exports, Remote Copy, `help showrsv`, `showrsv -l scsi3`; on the destination (E18U31) its ports, peer ports, `showtarget`, `showtarget -lun all`, CPGs and volumes. Show and help commands only, sent over its own SSH session (like `rcip_pair_capture.py`, not through the tool's read client); addresses, users and passwords from `MIG_SOURCE_*` / `MIG_DEST_*`; files named for `tests/fixtures/mig_pair/{3par,e18u31}/` (BL-27, not yet run) | No |
| `file_capture.py` | What D22U27 (or `CAPTURE_ARRAYS`) holds for Unified File: File ports (`showport -file`), the CLI's help index and any file commands in it, WSAPI v1 `/system` and `/wsapiconfiguration`, and the WSAPI v3 file service, file systems, share settings and shares with every HTTP status, 404 included (BL-28) | No |
| `rc_find_fabric.py` | Which vCenter and FC switches a lab host uses | No |
| `rc_console_lab.py` | The command console and its refusal of write commands (SPEC-019) | No |
| `rc_link_lab.py` | The replication link check between the pair (SPEC-020) | No |
| `rc_link_solo_lab.py` | The link check's real output on one array, server and client on its two RCIP ports | No |
| `rc_preset_lab.py` | The "Provision, then replicate" preset end to end with a real host | Yes, `zz_rc_*` on both arrays, removed at the end |
| `rc_async_lab.py` | Periodic (async) replication through the app's own modules | Yes, see its header |
| `rc_failover_lab.py` | The failover test (SPEC-017); also the shared helper module every script imports | Yes, the test group |
| `rc_async_failover_lab.py` | The failover test in periodic mode | Yes, see its header |
| `rc_option1.py`, `rc_rebuild.py`, `rc_sheet.py` | Helpers the failover scripts call: pause and restore the lab's Sync groups, compose the test sheet | Yes, run by the scripts above |
| `spec014.ps1` / `spec014.cmd` | Agentless host discovery (SPEC-014) from one workbook | No |

`archive/` keeps one-off explorations from the replication work (BL-20). They are not maintained.
