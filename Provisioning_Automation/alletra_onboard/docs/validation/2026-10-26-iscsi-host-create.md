# Live validation: iSCSI host creation (BL-44), D22U27, 2026-10-26

Run from the BGL LabRAT workspace (Windows Server 2025, 10.203.100.234), `jumpbox-test` at
`feat/bl-44-iscsi-hosts` c6cd24e0, app from source (`.venv\Scripts\onboard.exe ui`), driven by
`lab/iscsi_host_lab.py`. Run `eba8f3a7`, 17:47–17:49 IST. **Wrote to D22U27 and removed everything
it wrote.**

**Outcome: 14 PASS, 1 FAIL; the FAIL was the script's own check (its `POST /hosts` prefix also
matched `POST /hostsets`; fixed in the script). The app created an iSCSI host from its IQN in one
WSAPI call, the array read it back as Generic-ALUA with the IQN and no session, planning again said
*exists*, and the run's removal set left nothing behind. Host creation is live-verified; an export
to such a host over iSCSI is not, because D22U27 has no iSCSI port.**

## Environment

| | |
|---|---|
| Array | AlletraMP_D22U27 · CZ2D320BT1 · 10.64.122.99 · OS 10.5.0.43 |
| Host ports | FC 0:3:1–4, 1:3:1–4 (two `loss_sync`); no iSCSI port (`showport -iscsi`: no port information) |
| iSCSI name used | `iqn.1994-05.com.redhat:6e35c4a016a0`, the lab Linux host 10.54.159.49 (not touched) |

Sheet composed through `POST /init-sheet/compose`: Hosts tab row `zz_is_linux`, OS `linux`, address
10.54.159.49, the IQN, no login; host set `zz_is_hs` with that member; volume `zz_is_vol01` 1 GiB
tpvv on SSD_r6. Mode *Provision only*.

## What happened

| Step | Result |
|---|---|
| Discovery | 8 FC ports, 8 array hosts, no IQN on the array; vCenter login refused (the workspace's `LAB_DEFAULT_PW`), not needed here |
| Zoning check | `zz_is_linux: iSCSI, IQN not logged in on the array — exports to it are held back.` Gate empty |
| Plan | host `zz_is_linux` *create* — iSCSI, persona Generic-ALUA; host set and volume *create*; no export row; note *Not yet reachable over iSCSI …*; no blockers |
| Apply | `POST /hosts {"name": "zz_is_linux", "iSCSINames": ["iqn.1994-05…"], "persona": 2}` → 201; `POST /hostsets` → 201; `POST /volumes` → 201. Result *3 created*; host detail *id 8 · persona Generic-ALUA · 1 iSCSI name* |
| Read-back | `GET /hosts/zz_is_linux`: `iSCSIPaths[0].name` the IQN, `persona` 2, `FCPaths` empty. `showhost -d`: Port `---`, persona 2 Generic-ALUA |
| Plan again | host *exists — carries its iSCSI name*; host set and volume *exists* |
| Removal set | `removevv -f zz_is_vol01`, `removehostset -f zz_is_hs`, `removehost zz_is_linux`; no `zz_is_*` left |

The console log holds 26 commands: discovery reads over SSH, WSAPI reads, the three writes, one
`GET /hostsets/zz_is_hs` 404 (the existence check before the create), and no password.

## Found and fixed from this run

- The zoning step's sentence was the FC one (*Zoning needs 0 zone(s) … hand the command set to the
  SAN team … nothing can be provisioned*) for a run with only an iSCSI host. It now names the
  iSCSI host that is not logged in and says the hosts, sets and volumes can still be created. FC-only
  runs read as before.

## Not covered

- An export to the host and *Verify paths* over iSCSI: needs an array with an iSCSI port the host
  can reach. Planned with the LabRAT workspace as the host once the lab adds iSCSI ports.

Evidence: `tests/fixtures/d22u27_iscsi/` (`wsapi_writes_live.txt`, `wsapi_host_zz_is_linux.json`,
`showhost_d_zz_is_linux.txt`, `showhost_persona_zz_is_linux.txt`), pinned by
`tests/unit/test_iscsi_hosts.py`.
