# Lab replication pair captures — 2026-10-07 18:19 (BL-38)

Read-only output from both arrays of the lab Remote Copy pair, captured from labrat with
`ui-smoke/rc_capture.ps1` (SSH `show*`/`help` via paramiko, one `exec_command` per file so each file
starts with `# <command>`; WSAPI `GET`s via the `hpe3parclient` the tool provisions with). Nothing was
written.

| Array | Dir | System | Serial | ID (hex / dec) | OS | WSAPI | RCIP (slot 4 port 3, both nodes) | Gateway |
|---|---|---|---|---|---|---|---|---|
| D22U27 | `D22U27/` | `AlletraMP_D22U27` | CZ2D320BT1 | 0x2DEF6 / 188150 | 10.5.0 | 1.15 (build 100500043) | 0:4:3 10.54.122.92 · 1:4:3 10.54.122.93 /21 | 10.54.127.254 |
| E18U31 | `E18U31/` | `AlletraMP_E18U31` | CZ2D3209YV | 0x2DEF2 / 188146 | 10.5.0 | 1.15 (build 100500043) | 0:4:3 10.54.154.192 · 1:4:3 10.54.154.193 /21 | 10.54.159.254 |

## What the pair looks like (the facts the parsers are pinned to)

- **Partnership:** one IP target on each array, two links, all `Up`, policy `mirror_config`.
  **The target on E18U31 is named `AlletraMP_E18U31` too** (it points at D22U27's RCIP addresses) —
  so the tool matches the partnership by **link addresses** (`showrctransport -rcip` `PeerIPAddress` ↔
  the other array's `showport -rcip` `IPAddr`), never by target name.
- **Groups:** six, all **Sync**, all `Started`/`Synced`, `LastSyncTime NA`: `300gb` (auto_recover,
  auto_synchronize), `APP_Test` (+ `active_active` — a Peer Persistence group whose Primary is E18U31),
  `Intern_Automation`, `Intern_Automation2`, `Test-RCG`, `Test-RCG2`. **No periodic group exists**, so
  the periodic `LastSyncTime` / period output is pinned by the first live async run, not here.
  `rcopy_async_test` (named in earlier notes) does not exist: `showrcopy_groups_rcopy_async_test.txt`
  holds the CLI error (`Error: group matching … does not exist on the system`) and
  `wsapi/remotecopygroups_rcopy_async_test.json` the WSAPI one (404, code 187).
- **Peer-side group name** = `<group>.r<creating system's decimal ID>` (`300gb` ↔ `300gb.r188150`),
  carried in WSAPI as `remoteGroupName`. The suffix stays after a role change (`APP_Test.r188150` is
  the Primary on E18U31).
- **WSAPI `/remotecopygroups` record:** `role` 1 Primary / 2 Secondary; `targets[].mode` 1 Sync
  (2 periodic, 4 async streaming per the client docs); `targets[].state` 3 (observed on Started groups);
  `targets[].policies` = `activeActive`, `autoFailover`, `autoRecover`, `autoSynchronize`,
  `multiTargetPeerPersistence`, `overPeriodAlert`, `pathManagement`; `targets[].syncPeriod` absent on
  Sync groups; `localUserCPG` / `targets[].remoteUserCPG` (`SSD_r6` ↔ `SSD_r6`, absent on two groups);
  `volumes[].remoteVolumes[]` = `remoteVolumeName`, `remoteVolumeID`, `syncStatus` 3 (Synced),
  `volumeLastSyncTime` (ISO, +05:30) / `volumeLastSyncTimeSec`, `localVolumeSetName` /
  `remoteVolumeSetName` (`300gb` ↔ `300gb`).
- **`/remotecopy`:** `mode 2`, `status 1`, `asyncEnabled false`; links to `/remotecopygroups`,
  `/remotecopytargets` (not captured), `/remotecopylinks` (captured: one member per link, named
  `<target>_<N>_<S>_<P>`).
- **WSAPI write rules (live, 2026-10-09):** `PUT /remotecopygroups/<g>` refuses `syncPeriod` and
  `policies` in the same `targets[]` entry — HTTP 400 code 44 *"parameters cannot be present at the
  same time - policies, syncPeriod"*. Two PUTs. `POST /remotecopygroups` with `localUserCPG` in the
  body was accepted. **One mode per target:** a Periodic group on this target (six Sync groups) is
  created, configured and populated without complaint and then refused at **start** — HTTP 400 code
  236 *"Group with different modes on a single target is not supported"* (Support Matrix note 1).
  **Removal order:** the peer refuses `removevvset` on a set holding secondaries while the group
  exists (*"Set … is currently admitted to Remote Copy Group and may not be directly removed"*);
  `dismissrcopyvv -removevv` on the primary removes the secondary volume on the peer.
- **CPGs:** D22U27 `3sc`, `SSD_r6`, `test`; E18U31 `SSD_r6` only.
- **`help/`** — the array's own `-h` for every Remote Copy command (D22U27; identical OS on E18U31).
  Confirms: `creatercopygroup -usr_cpg <cpg> <target>:<cpg> <group> <target>:<mode>`;
  `admitrcopyvv -createvv [-nowwn] set:<set> <group> <target>:<sec_set>`; `setrcopygroup pol
  auto_recover|auto_synchronize`; `setrcopygroup period <n>{s|m|h|d} <target> <group>`;
  `setrcopygroup failover|recover|restore -f`; `dismissrcopyvv -removevv`; `stoprcopygroup -f`.

Pinned by `tests/unit/test_replication_read.py` (SPEC-016 R1/R2/R6) — to be written with SPEC-016.
