# SPEC-014 read-only lab check

- Run IDs: vcenter=7a6dcea5-4508-4a2b-bd8b-f9c565756765; No-ID ESXi sheet lookup=e61b4c91-b289-4853-a346-31c0c7f59606; sheet-name member=bea891a0-fe93-4446-ae65-3a4d3878c8e1; Unresolved host=482c0d12-4b97-49ef-a37b-fd7a363b1708; No-ID array host lookup=4a1fe95e-d7b6-4798-8b31-12087c8a88dd; Short-name array host lookup=be5d4054-fef9-4df3-bbba-55160bfb09c4; Windows no-ID lookup=e92ded07-2a84-4f00-9c5e-343dfc3e7a51; Windows server read (WinRM)=211592b2-6641-4275-aefb-b61050e8eeaf; wrong-wwpn=1b0cab96-937d-43df-a4cc-c035f7752110
- Result: 40 PASS, 0 FAIL, 2 SKIP

| Section | Result | Check | Detail |
|---|---|---|---|
| ESXi via vCenter | PASS | Baseline discovery reached the array | ports=12 |
| ESXi via vCenter | PASS | vCenter reports host identities (SPEC-014 R2) | hosts=3 HBAs=6 |
| ESXi via vCenter | PASS | ESXi serial from vCenter |  |
| No-ID ESXi sheet lookup | PASS | Discovery reached the array | ports=12 |
| No-ID ESXi sheet lookup | PASS | Sheet host stays visible | lookup=found in vCenter as 10.132.30.47 |
| No-ID ESXi sheet lookup | PASS | Host read carries no password field |  |
| No-ID ESXi sheet lookup | PASS | Run detail does not echo host password |  |
| No-ID ESXi sheet lookup | PASS | No-ID sheet row resolved by vCenter | found in vCenter as 10.132.30.47 |
| Host-set member under a sheet name (preview only) | PASS | Sheet-name member planned under the vCenter name | Host set zz_s14_alias_hs: sheet host 'zz_s14_alias' is the same server as '10.132.30.47' and is planned under that name. |
| Host-set member under a sheet name (preview only) | PASS | Unknown member is named in the plan notes |  |
| Host-set member under a sheet name (preview only) | PASS | Host set row lists the vCenter name | 10.132.30.47 |
| Unresolved host | PASS | Discovery reached the array | ports=12 |
| Unresolved host | PASS | Sheet host stays visible | lookup=not found — not in vCenter, no array host of that name, no iSCSI login from 192.0.2.123; add its WWPN/IQN on the Hosts tab |
| Unresolved host | PASS | Host read carries no password field |  |
| Unresolved host | PASS | Run detail does not echo host password |  |
| Unresolved host | PASS | Unresolved sheet host has a discovery note |  |
| Unresolved host | PASS | Not-found wording matches vCenter state (vCenter down=False) | not found — not in vCenter, no array host of that name, no iSCSI login from 192.0.2.123; add its WWPN/IQN on the Hosts tab |
| No-ID array host lookup | PASS | Discovery reached the array | ports=12 |
| No-ID array host lookup | PASS | Sheet host stays visible | lookup=found on the array as host HPE_VM_7f21bf6bf27da180152ea344 |
| No-ID array host lookup | PASS | Host read carries no password field |  |
| No-ID array host lookup | PASS | Run detail does not echo host password |  |
| No-ID array host lookup | PASS | Array host object supplies initiators | found on the array as host HPE_VM_7f21bf6bf27da180152ea344 |
| Short-name array host lookup | PASS | Discovery reached the array | ports=12 |
| Short-name array host lookup | PASS | Sheet host stays visible | lookup=found on the array as host HPE_VM_7f21bf6bf27da180152ea344 (short-name match) |
| Short-name array host lookup | PASS | Host read carries no password field |  |
| Short-name array host lookup | PASS | Run detail does not echo host password |  |
| Short-name array host lookup | PASS | Sheet FQDN HPE_VM_7f21bf6bf27da180152ea344.spec014.local matched array host HPE_VM_7f21bf6bf27da180152ea344 | found on the array as host HPE_VM_7f21bf6bf27da180152ea344 (short-name match) |
| Windows no-ID lookup | PASS | Discovery reached the array | ports=12 |
| Windows no-ID lookup | PASS | Sheet host stays visible | lookup=not found — not in vCenter, no array host of that name, no iSCSI login from 10.132.30.137; add its WWPN/IQN on the Hosts tab |
| Windows no-ID lookup | PASS | Host read carries no password field |  |
| Windows no-ID lookup | PASS | Run detail does not echo host password |  |
| Windows no-ID lookup | SKIP | Array/initiator lookup | No lab identity for arcus-win137; it should remain visible |
| Windows server read (WinRM) | PASS | Discovery reached the array | ports=12 |
| Windows server read (WinRM) | PASS | Sheet host stays visible | lookup=read from the server over WINRM (10.132.30.137) |
| Windows server read (WinRM) | PASS | Host read carries no password field |  |
| Windows server read (WinRM) | PASS | Host-side read succeeded | winrm |
| Windows server read (WinRM) | PASS | Host-side serial returned |  |
| Windows server read (WinRM) | PASS | Host-side FC WWPN or iSCSI IQN returned |  |
| Windows server read (WinRM) | PASS | Run detail does not echo host password |  |
| Windows server read (WinRM) | PASS | Events do not echo host password |  |
| Typed-vs-read blocker (no apply) | PASS | Typed WWPN mismatch blocks the plan | Host 'arcus-win137': sheet WWPN(s) 1000000000000001 not on the server — 10.132.30.137 reports 51402EC02089CC1C, 51402EC02089CC1E. Fix the Hosts tab. |
| Linux | SKIP | Linux host login | No Linux host/address/login provided |

## Discovered host facts

| Section | Host / OS | Serial | WWPNs | IQNs | Lookup / read | Multipath |
|---|---|---|---|---|---|---|
| No-ID ESXi sheet lookup | 10.132.30.47 / esxi | CN763604C4 | 100008F1EAC03DE7, 100008F1EAC03DE8 | iqn.1998-01.com.vmware:dl380g9r11u07.grsbtelab.ap.hpecorp.net:1656314103:66 | found in vCenter as 10.132.30.47;  |  |
| Unresolved host | zz_spec014_unknown / linux |  |  |  | not found — not in vCenter, no array host of that name, no iSCSI login from 192.0.2.123; add its WWPN/IQN on the Hosts tab;  |  |
| No-ID array host lookup | HPE_VM_7f21bf6bf27da180152ea344 / vme |  |  | iqn.2024-12.com.hpe:vmenode3:42802 | found on the array as host HPE_VM_7f21bf6bf27da180152ea344;  |  |
| Short-name array host lookup | HPE_VM_7f21bf6bf27da180152ea344.spec014.local / vme |  |  | iqn.2024-12.com.hpe:vmenode3:42802 | found on the array as host HPE_VM_7f21bf6bf27da180152ea344 (short-name match);  |  |
| Windows no-ID lookup | arcus-win137 / windows |  |  |  | not found — not in vCenter, no array host of that name, no iSCSI login from 10.132.30.137; add its WWPN/IQN on the Hosts tab;  |  |
| Windows server read (WinRM) | arcus-win137 / windows | SGH640WFT7 | 51402EC02089CC1C, 51402EC02089CC1E | iqn.1991-05.com.microsoft:eljr0nb1uv.asiapacific.hpqcorp.net | read from the server over WINRM (10.132.30.137); read over WINRM from 10.132.30.137 (ELJR0NB1UV) | MPIO Installed; 3PARdata VV claimed by MSDSM; 0 Alletra/3PAR disk(s) |
