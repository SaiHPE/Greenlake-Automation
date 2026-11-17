# Peer-port captures (BL-26, SPEC-025)

Read-only output that the peer-port parsers are pinned to (`tests/unit/test_peer_ports.py`).

## rack13/: rack13-ARCUS, 2026-11-16 23:20 IST

| | |
|---|---|
| Array | `rack13-ARCUS`, HPE Alletra Storage MP B10230, serial CZ2D2K014S, 2 nodes, 10.132.30.121 |
| OS | 10.6.0 (Standard Support Release). It ran 10.5.55 on 2026-11-03 (`../rcip_pair/`). WSAPI 1.16.0 |
| Script | `lab/peer_port_capture.py` with `CAPTURE_ARRAYS=rack13=10.132.30.121`, run from the jump box |
| What it did | SSH `show*` and `help` only; WSAPI `GET /ports` and `GET /wsapiconfiguration` only. Nothing changed on the array |

Each `.txt` file starts with the line `# <command>`, written by the script; the rest is the array's
answer as it came. The script's `rack13_` prefix is dropped from the names. `report.txt` is the
script's own summary. Scrubbing: nothing was replaced. The only names are lab ones: the `HPE_VM_*`
VME hosts and their `iqn.2024-12.com.hpe:vmenode*` IQNs, the lab ESXi host
`DL380G10R13U25.btl.grsbtelab.ap.hpecorp.net` (also in `../rack13_fabric/`), one HPE Windows
machine's IQN in `hpqcorp.net`, and the lab volume `test_vme_shared_4`. No password, token or
customer detail.

**rack13 has no port in peer mode.** It is the "nothing in peer mode yet" case: the read before the
first change. The capture of a port in peer mode is `E18U31/` (2026-11-17, below).

| File | Command | What it shows |
|---|---|---|
| `showport.txt` | `showport` | 8 FC ports on slot 3, all mode `target`. 0:3:1, 0:3:2, 1:3:1, 1:3:2 Type `free`, `loss_sync`. 0:3:3 and 1:3:4 Type `free`, `ready`. 0:3:4 and 1:3:3 Type `host`, `ready`. No Partner or FailoverState column |
| `showport_par.txt` | `showport -par` | `N:S:P Connmode ConnType CfgRate MaxRate Class2 UniqNodeWwn VCN IntCoal TMWO`, 20 rows (no IP ports). Every FC port `host point`; NVMe drive ports `disk point`; iSCSI `host eth` |
| `showport_c.txt` | `showport -c` | Last column `Mode_change`: `allowed` on the 8 FC ports, `prohibited` on NVMe, iSCSI and IP ports. The Device column names host objects only (0:3:4's unclaimed login shows as `---`) |
| `showport_peer.txt` | `showport -peer` | *There is no specified port information.* (no peer port) |
| `showport_i.txt`, `showport_sfp.txt` | `showport -i`, `showport -sfp` | FC card HPE64004-B on both nodes. 0:3:1, 0:3:2, 1:3:1, 1:3:2 report no SFP (`-` in every column) |
| `showhost_d.txt` | `showhost -d` | 0:3:4 and 1:3:3: one unclaimed login each, 10005CED8C5312A9. The other FC ports: no login |
| `showvlun_a.txt` | `showvlun -a` | 4 active paths, all on the iSCSI ports 0:4:1 and 1:4:1. None on an FC port |
| `showportdev_ns_<nsp>.txt` | `showportdev ns <N:S:P>` | The four `loss_sync` ports: *Error: Unable to get device list on port …*. 0:3:3, 1:3:4: in a fabric, 0 devices. 0:3:4, 1:3:3: the ESXi HBA, the array's own ports, and each port's NVMe virtual port (`2034 0102 ADF2…`) |
| `wsapi_ports.json` | `GET /ports` | 28 ports. Mapped to the CLI's words they equal `showport` and `showport -par` port for port (see `parse_port_states`). Every FC port has one `virtualPorts` entry: vpi 31, protocol 6 (NVMe), node WWN `2FF70102…` |
| `wsapi_wsapiconfiguration.json` | `GET /wsapiconfiguration` | WSAPI 1.16.0, HTTPS only |
| `help_controlport.txt` | `help controlport` | `config`, `offline`, `rst`, `-f` and the `TPDFORCE_OVERRIDE` note read as on OS 10.5.55. Differences from 10.5.55 are only in the `file delete`, `rcip` (VLAN options, MTU minimum), `nvme` and `rate` text |
| `help_showport.txt` | `help showport` | `-peer`: *Displays information that is specific to the Fibre Channel ports for Data Migration*; its example peer port is `0:5:1 initiator ready 2FF70202AC000007 20510202AC000007 2Gbps` |
| `help_showportdev.txt` | `help showportdev` | `ns`, `uns`, `findport` forms |
| `showsys.txt`, `showversion.txt` | | Name, serial, OS |

## E18U31/, D22U27/, VZ/: three lab arrays, 2026-11-17

The same script, run by labrat on the three arrays it could reach (`peer_ports_<TAG>` in its
summary; LZ did not answer on SSH and was skipped). Read-only as above: SSH `show*` and `help`,
WSAPI `GET /ports` and `GET /wsapiconfiguration`. Same file names as `rack13/`, the `<TAG>_` prefix
dropped; `report.txt` is the script's summary (its `console.txt` adds only banners and was not kept).

| Folder | Array | OS, WSAPI | Peer ports |
|---|---|---|---|
| `E18U31/` | `DHCI_B10K` (named AlletraMP_E18U31 in `../rc_pair/`), serial CZ2D3209YV, 2 nodes, 10.64.154.190 | 10.5.60, WSAPI 1.15.60 | **0:3:2 and 1:3:2**, FC |
| `D22U27/` | `AlletraMP_D22U27`, serial CZ2D320BT1, 2 nodes, 10.64.122.99 | 10.5.0, WSAPI 1.15.0 | none |
| `VZ/` | `MPB10K-D24U21-VZ` (the lab's CRV Vault Zone), serial SGHD44LQLS, 2 nodes, 10.64.122.140 | 10.5.51 (kernel 10.5.0), WSAPI 1.15.0 | none |

**Scrubbing.** Two names were replaced; nothing else was edited:
- E18U31: a six-letter prefix on four host objects and their volumes reads like a customer proof of
  concept. It is `LabPoc` (`LabPoc-esxi1`, `LabPoc-NEW-RH-04`, ...) in `showhost_d.txt`,
  `showport_c.txt`, `showportdev_ns_031.txt`, `showportdev_ns_131.txt`, `showvlun_a.txt` and
  `wsapi_ports.json`. Same length, so the columns line up as captured. Older fixtures still carry the
  original (`../rc_pair/rebuild_2026-10-10/*/E18U31/showvlun_t.txt`); they were not touched here.
- D22U27: one volume name began with a person's first name; it is `testuser1_885564_553150` in
  `showvlun_a.txt`.

Kept, all lab: the `HPE_VM_*` VME hosts and `iqn.2026-10.com.hpe:hvm-host-*` IQNs, the Emulex HBAs on
`localhost.bgl1.global.tslabs.hpecorp.net`, `ESX1`, `ESX2`, the `DL380…`/`DL360…` hosts, `CRV_VZ_*`,
D22U27's hosts and test volumes (already in `../d22u27_iscsi/` and `../rc_pair/`), and the lab HPE 3PAR 20850
4UW0002142 (also in `../vz_fabric/`). No password, token or customer detail.

The help texts (`help controlport`, `help showport`, `help showportdev`) are byte for byte the same on
the three 10.5 arrays. Against rack13's 10.6.0 they differ only where `rack13/` says (`file delete`,
`rcip` VLAN options, MTU minimum 1000 not 1280, `nvme`, rate 4), plus sample output under the
`showport -rcip` example and the `showportdev sas`/DCBX options, which only 10.5 prints. The `config`, `offline`, `rst` and `-f` text is the same.

### E18U31/: the ports in peer mode

| File | What it shows |
|---|---|
| `showport.txt` | 0:3:2 and 1:3:2 `initiator ready 2FF70202AC02DEF2 20320202AC02DEF2 / 21320202AC02DEF2 peer FC`. The other FC ports read `target`, node WWN `2FF70002AC02DEF2`: 0:3:1, 0:3:4, 1:3:1, 1:3:4 Type `host` `ready`; 0:3:3, 1:3:3 Type `free` `loss_sync`. The IP ports 0:4:3, 0:4:4, 1:4:3, 1:4:4 are mode `peer`, `offline`, Type `free`. Every FC Label is `-` (the `Meow Meow` of 2026-10-07 is gone) |
| `showport_par.txt` | 20 rows. 0:3:2 and 1:3:2 `peer point` (what a removal set restores FROM); every other FC port `host point`; NVMe `disk point`; iSCSI `host eth`; no row for an IP port |
| `showport_peer.txt` | Two rows, `N:S:P Mode State Node_WWN Port_WWN Rate VPI`: 0:3:2 and 1:3:2, `initiator ready`, the same WWNs as `showport`, 32Gbps, VPI 0. The array's real output has a VPI column the help's example lacks. It lists this array's own peer ports, **not the source array's WWNs** |
| `showport_c.txt` | 0:3:2 and 1:3:2: Mode `initiator`, Device `2FF70002AC07E528` (the source array's node WWN), topology fabric, 32Gbps, Mode_change `allowed`. Every FC port `allowed`; NVMe, iSCSI and IP `prohibited` |
| `showhost_d.txt` | No login on 0:3:2 or 1:3:2. 0:3:1 and 1:3:1: the four `LabPoc-*` hosts and two unclaimed ESXi HBAs; 0:3:4 and 1:3:4: two unclaimed HBAs; the iSCSI ports: three VME hosts |
| `showvlun_a.txt` | Exports on 0:3:1, 1:3:1 and the iSCSI ports; none on a peer port or on 0:3:3, 1:3:3 |
| `showportdev_ns_032.txt`, `_132.txt` | The array's own two peer ports and one other device: `HPE_3PAR 20850_R2 - 4UW0002142`, node `2FF70002AC07E528`, ports `20320002AC07E528` / `21320002AC07E528` (its 0:3:2 and 1:3:2, host-mode WWNs). That is the migration source the peer ports see |
| `showportdev_ns_033.txt`, `_133.txt` | *Error: Unable to get device list* (no SFP in `showport_sfp.txt`) |
| `wsapi_ports.json` | 20 ports; the four IP ports in mode peer are not listed. 0:3:2 and 1:3:2: `mode` 3, `type` 6, `connectionMode` 4, `connectionType` 2, `linkState` 4, `device` `["2FF70002AC07E528"]`, `virtualPorts` empty. Every other FC port has one virtual port: vpi 31, protocol 6 (NVMe), node WWN `2FF70102AC02DEF2`, port WWN `20310102ADF2DEF2` for 0:3:1 and so on |

**The WWN question (does a port's WWN change when it becomes a peer port?).** What these files show:
a peer port carries `0202` in WWN bytes 3 and 4 (node `2FF70202…`, port `2032 0202…`), every FC port
in host mode carries `0002` (on E18U31 and on rack13, D22U27 and VZ), and the NVMe virtual ports carry
`0102`; a peer port has no NVMe virtual port. So the host-mode form of E18U31's 0:3:2 would be
`20320002AC02DEF2`, and no capture in this repository has that WWN: no capture has one port before and
after a change. The pattern points to a new WWN at the change; only the first live change proves it.

### D22U27/: OS 10.5.0, no peer port

| File | What it shows |
|---|---|
| `showport.txt` | Every FC port `target`. 0:3:1 Label `peer port`, 1:3:1 `peer 1:3:1`, 1:3:2 `Peer_port`: all three Type `host` with logins (LESSONS 42). 0:3:2 `free` `ready`; 0:3:3, 1:3:3 `free` `loss_sync`. IP: 0:4:1, 0:4:2, 1:4:1, 1:4:2 Type `file`; 0:4:3, 1:4:3 `rcip`; 0:4:4, 1:4:4 `free` `offline` |
| `showport_par.txt` | 16 rows (no iSCSI port on this array): every FC port `host point` |
| `showport_peer.txt` | *There is no specified port information.* |
| `showhost_d.txt` | 1:3:2: one unclaimed login, 1000040973C52799 (as on 2026-10-26). 0:3:2: none |
| `showportdev_ns_032.txt` | Only the array's own 0:3:2: in a fabric, nothing zoned to it |
| `wsapi_ports.json` | 18 ports: the `file` and `free` IP ports are not listed. The RCIP ports are `type` 7 |

Free FC ports by SPEC-025's rule: 0:3:2, 0:3:3, 1:3:3.

### VZ/: OS 10.5.51, no peer port

| File | What it shows |
|---|---|
| `showport.txt` | 20 ports, no NVMe drive port in the list. 0:3:1, 0:3:2, 1:3:1, 1:3:2 `host` `ready` (three `CRV_VZ_*` ESXi hosts); 0:3:3, 0:3:4, 1:3:3, 1:3:4 `free` `loss_sync` (SFP `Degraded`, TXDisable `Yes`). iSCSI 0:4:1, 0:4:2 `free` `offline`; 0:4:3, 0:4:4 `rcip` `loss_sync`; cluster ports 0:5:1, 0:5:2 |
| `showport_par.txt` | 12 rows: FC `host point`, iSCSI `host eth` |
| `showport_peer.txt` | *There is no specified port information.* |
| `wsapi_ports.json` | All 20 ports. RCIP ports `type` 7; cluster ports `linkState` 4 `ready` |

Free FC ports by SPEC-025's rule: 0:3:3, 0:3:4, 1:3:3, 1:3:4.

## rack13_live/: rack13-ARCUS, one port set to peer and back, 2026-11-17 evening

The first live change of a port's mode (BL-26 live run after the owner's decisions; record in
`docs/validation/2026-11-17-rack13-live-w2.md`, *2026-11-17 evening*). Read over SSH from the
developer's Mac with `show*` commands only, between the consultant's pastes. Each `.txt` starts with
`# <command>`; nothing was replaced (lab names only, as in `rack13/`).

| Folder or file | When | What it shows |
|---|---|---|
| `before/` | 19:24 IST, before any paste | as in `rack13/`: every slot-3 FC port `target`, Connmode `host point`; 0:3:1, 0:3:2, 1:3:1, 1:3:2 Type `free`, `loss_sync` (no SFP); 0:3:4 and 1:3:3 serve the unclaimed ESXi HBA |
| `paste_0_3_1.txt` | 19:29 | the consultant's paste of the plan's two lines for 0:3:1: `controlport offline 0:3:1` asked *Are you sure you want to run controlport offline on port 0:3:1? select q=quit y=yes n=no:*, answered `y`; `controlport config peer -ct point -f 0:3:1` answered nothing and asked nothing |
| `after_config_peer_0_3_1/` | 19:29 | 0:3:1 mode `initiator`, state `loss_sync` (not held offline: no `rst` needed), **Type still `free`** (nothing attached), Connmode `peer point`, node WWN `2FF70202AC02D495`, port WWN `20310202AC02D495` (was `…0002…`); `showport -peer` lists it. Its pair partner 0:3:2 and every other port read as before: the HPE64004-B did not move a free partner |
| `paste_removal_0_3_1.txt` | 19:33 | the removal set: `controlport offline 0:3:1` asked again (`y`); `controlport config host -ct point -f 0:3:1` answered nothing; `controlport rst -f 0:3:1` answered *controlport Error: Port 0:3:1 is being reset; please re-issue the command when reset is complete* (the `config` line's own reset) |
| `after_removal_0_3_1/` | 19:34 | slot 3 equal to `before/` in `showport`, `-par` and `-c`, WWN back to `…0002…`; `showport -peer` empty again |
| `paste_removal_both.txt` | 19:38 to 19:39 | the rerun (0:3:1 and 1:3:1 set to peer at 19:36 with the printed set, both partners unchanged) undone with the read after the paste's removal set: each `offline` asked (`y`), each `config host -ct point -f` answered nothing, each `rst -f` answered *is being reset* |
| `after_removal_both_intcoal_1_3_1/` | 19:40 | every slot-3 row as in `before/` except **1:3:1 IntCoal `disabled`** (it read `enabled` before, and 0:3:1 came back `enabled`): the `config` back to host does not always keep interrupt coalescing |
| `paste_intcoal_1_3_1.txt`, `after_intcoal_fix/` | 19:42 | `controlport intcoal enable -f 1:3:1` pasted by hand: no answer, no prompt; `showport -par` equal to `before/` again (whitespace aside: the IntCoal column widened by one space while a port read `disabled`) |
| `rerun2/` | 19:49 to 19:54 | the second rerun, to paste the removal set with its IntCoal lines end to end. `paste_removal.txt`: each `controlport intcoal enable -f`, pasted straight after its port's `config host -ct point -f`, answered *is being reset* and did nothing, as did each `rst`. `after_removal_showport_par.txt`: **0:3:1 IntCoal `disabled`** this time (1:3:1 `enabled`). `paste_intcoal_0_3_1.txt`: the same line pasted by hand a minute later, no answer; `after_fix_showport_par.txt` equals `before_showport_par.txt` |
