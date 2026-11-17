# iSCSI port and VLAN captures (BL-25, SPEC-024)

One folder per array, named by the capture's TAG. Each was written by `lab/iscsi_vlan_capture.py`,
which is read-only: show commands and CLI help over SSH, GETs over WSAPI, nothing changed. Every file
starts with the command that made it (`# showport -iscsi`); `report.txt` is the script's own summary.

## rack13/ — rack13-ARCUS, 2026-11-16 about 23:19 IST

HPE Alletra Storage MP B10230, serial CZ2D2K014S, management 10.132.30.121, **OS 10.6.0**
(`showversion`; the same array was OS 10.5.55 in `../../rack13_array/`, 2026-09-13). Run from the jump
box with `CAPTURE_ARRAYS=rack13=10.132.30.121`. No password, token or customer name is in the files;
the host names are the lab's own (`HPE_VM_*`, one HPE lab Windows initiator).

What the files settle:

| File | What it shows |
|---|---|
| `showport_iscsi.txt` | Layout `N:S:P State IPAddr Netmask/PrefixLen Gateway TPGT MTU Rate iSNS_Addr iSNS_Port STGT VLANs Peer_Enabled`. 0:4:1 and 1:4:1 ready on 10.93.18.10 and .12, 255.255.254.0, gateway 10.93.18.1, VLANs 1, Peer_Enabled N. 0:4:2 and 1:4:2 offline, `0.0.0.0` everywhere, VLANs 0 |
| `showport_iscsivlans.txt` | Layout `N:S:P VLAN IPAddr Netmask/PrefixLen Gateway MTU TPGT STGT iSNS_Addr iSNS_Port` (no State column). One row per port **with** an address, VLAN `untagged`, the same values as `showport -iscsi`. No port has a tagged interface, so no tagged row exists here |
| `help_controliscsiport.txt` | `addr <IP_address> <netmask\|prefix_len> [-vlan <vlan_tag>] [-f] <node:slot:port>`, `gw <gw_address> [-vlan <vlan_tag>] [-f] <node:slot:port>`, `delete [-vlan <vlan_tag>] [-f] <node:slot:port>`, `allowpeer`, the discovery and session forms; tag 1 to 4094 (0 to 4094 for initiator commands, 0 meaning untagged). Its example `controliscsiport delete -f 1:1:1` deletes the port's whole configuration: a delete without `-vlan` removes the untagged address |
| `help_showport.txt` | `-iscsivlans` "Displays information about VLANs on iSCSI ports"; NOTES: an address shown with `*` means the port has more than one address configured with VLANs |
| `help_controlport.txt` | On OS 10.6.0 `controlport rcip add/addr/delete/gw/mtu/ping/state` take `-vlan` (OS 10.5's help, `../rc_pair/help/`, did not); `controlport file delete` no longer lists `-vlan`. No iSCSI form: iSCSI addresses are `controliscsiport` only |
| `wsapi/ports_<n_s_p>_iscsivlans.json` | `GET /ports/<n:s:p>/iSCSIVlans/` answers on all four iSCSI ports with `{"iSCSIVlans": [], "total": 0, "links": [...]}`: its own envelope, not `members`, and empty even on 0:4:1 and 1:4:1, which carry an untagged address |
| `wsapi/ports.json` | `GET /ports`: every port, FC and NVMe included, carries `iSCSIVlans: []`; the iSCSI ports carry `iSCSIPortInfo` (`IPAddr`, `netmask`, `gateway`, `mtu`, `tpgt`, `stgt`, `iSNSPort`, `iSNSAddr`, `rate`, `vlan`) with `vlan` 0 on all four |
| `showport.txt` | Roles: 0:4:1 and 1:4:1 `target ready host iSCSI`, 0:4:2 and 1:4:2 `target offline free iSCSI`, 0:4:3/0:4:4/1:4:3/1:4:4 `peer offline free IP`, FC 0:3:x/1:3:x |
| `showhost_d.txt` | Two `HPE_VM_*` iSCSI hosts logged in on 0:4:1 and 1:4:1 from 10.132.28.10 and .11, and one unclaimed Windows initiator on 1:4:1 |
| `showport_rcip.txt`, `showport_file.txt` | No RCIP and no file port configured (prose answer) |
| `shownet.txt`, `showsys.txt`, `showversion.txt` | Management 10.132.30.121/255.255.240.0; name rack13-ARCUS; OS 10.6.0 |

## D22U27/, VZ/, E18U31/ — three OS 10.5 arrays, 2026-11-17

Run from the jump box by the lab runner, one capture per array, the same script and the same files
as rack13 (`report.txt` is each run's summary). No password, token or customer name is in the
files. The host names are the lab's own: `ESX1`, `ESX2`, `DL380*`, `winhost_CDS`, `Host1-zerto` on
D22U27; `CRV_VZ_DL360G11D24U2*` on VZ (the lab's CRV Vault Zone); `HPE_VM_*` and `TPIPoc-*` on
E18U31. None of the three has a tagged interface either.

**D22U27/** — AlletraMP_D22U27, serial CZ2D320BT1, management 10.64.122.99, **OS 10.5.0**. No iSCSI
port at all.

| File | What it shows |
|---|---|
| `showport.txt` | Slot 4 is 0:4:1/0:4:2/1:4:1/1:4:2 `target ready file IP`, 0:4:3/1:4:3 `peer ready rcip IP`, 0:4:4/1:4:4 `peer offline free IP`. No iSCSI port |
| `showport_iscsi.txt`, `showport_iscsivlans.txt` | Two different prose answers: *"There is no specified port information."* and *"no ports listed"*. Both parse as `[]` |
| `showport_file.txt`, `showport_rcip.txt` | The four file ports (10.54.90.70 to .74/21, VLAN `untagged`) and the two RCIP ports (10.54.122.92 and .93, 255.255.248.0, gateway 10.54.127.254) |
| `wsapi/ports.json` | `GET /ports` only (no iSCSI port, so no per-port GET): 18 members, the file ports and the free IP ports left out, and no `iSCSIVlans` field on any port |

**VZ/** — MPB10K-D24U21-VZ, serial SGHD44LQLS, management 10.64.122.140, **OS 10.5.51**. Four iSCSI
ports, all offline.

| File | What it shows |
|---|---|
| `showport.txt` | 0:4:1, 0:4:2, 1:4:1, 1:4:2 `target offline free iSCSI`; 0:4:3 to 1:4:4 `peer loss_sync rcip IP`; 0:5:x/1:5:x `cluster` ports |
| `showport_iscsi.txt` | The `VLANs Peer_Enabled` layout; `0.0.0.0` everywhere, MTU 1500, VLANs 0, Peer_Enabled N |
| `showport_iscsivlans.txt` | *"no ports listed"*, the same words as D22U27 with no iSCSI port: the view lists addresses, not ports |
| `showport_rcip.txt` | 10.222.1.5 to .8, 255.255.255.0, no gateway, all `loss_sync` |
| `wsapi/ports_<n_s_p>_iscsivlans.json` | `{"iSCSIVlans": [], "total": 0, "links": [...]}` on all four ports |
| `wsapi/ports.json` | `iSCSIPortInfo` `0.0.0.0`, MTU 1500, `vlan` 0 on the four iSCSI ports; no `iSCSIVlans` field on any port |

**E18U31/** — the array of `../rc_pair/E18U31/` (same serial, CZ2D3209YV), now named **DHCI_B10K**,
management 10.64.154.190, **OS 10.5.60**. Four ready iSCSI ports, MTU 9000.

| File | What it shows |
|---|---|
| `showport.txt` | 0:4:1, 0:4:2, 1:4:1, 1:4:2 `target ready host iSCSI`; 0:4:3 to 1:4:4 `peer offline free IP` (no RCIP any more); 0:3:2/1:3:2 `initiator ready peer FC` |
| `showport_iscsi.txt` | 0:4:1 10.1.1.2 and 1:4:1 10.1.1.3 on 10.1.1.0/24, 0:4:2 20.1.1.2 and 1:4:2 20.1.1.3 on 20.1.1.0/24; gateway `0.0.0.0` (none), MTU 9000, VLANs 1, Peer_Enabled N |
| `showport_iscsivlans.txt` | rack13's layout; the four untagged addresses (MTU 9000), no tagged row |
| `showhost_d.txt` | Three `HPE_VM_*` iSCSI hosts logged in on all four ports, from 10.1.1.4 to .6 and 20.1.1.4 to .6; four `TPIPoc-*` FC hosts |
| `wsapi/ports_<n_s_p>_iscsivlans.json` | **Unlike rack13 (OS 10.6.0)**: one record per port, the untagged address, `vlanTag` 0, `total` 1. Fields `IPAddr`, `netmask`, `gateway`, `vlanTag`, `mtu`, `stgt`, `tpgt`, `iSNSAddr`, `iSNSPort`: the first real record in hand |
| `wsapi/ports.json` | The same record in each iSCSI port's `iSCSIVlans` (`[]` on the other ports); `iSCSIPortInfo.vlan` 0 on all four |
| `showport_rcip.txt`, `showport_file.txt` | Prose: no RCIP and no file port configured |

**OS 10.5 help, the same on all three** (`help_*.txt` are byte for byte equal across 10.5.0, 10.5.51
and 10.5.60):

| File | What it shows |
|---|---|
| `help_controliscsiport.txt` | The same `addr`, `gw` and `delete` forms with `[-vlan <vlan_tag>]` as OS 10.6.0, and the same example `controliscsiport delete -f 1:1:1`. The tag is "(1 to 4094)"; 10.6.0's initiator range (0 to 4094), `-skip_rescan` and `-vlan` on `discovery show` and `session show` are not there |
| `help_controlport.txt` | Equal to `../rc_pair/help/help_controlport.txt`. `controlport rcip` takes no `-vlan` on any form (10.6.0's does); `file` and `nvme` do |
| `help_showport.txt` | `-iscsivlans` and the `*` note as on 10.6.0 |

Owed: the same capture while a port carries a tagged interface, saved as `tagged/` (the live
confirmation before the apply is built, ADR 0017 and SPEC-024 §6; rack13-ARCUS is the candidate). It
pins the tagged row of `showport -iscsivlans`, the values of a tagged WSAPI iSCSIVlans record, and the
`*` that `showport -iscsi` puts after a starred address; the three tests that need it stay strict
xfail until then.

Pinned by `tests/unit/test_iscsi_vlans.py`.
