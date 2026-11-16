# SPEC-014 read-only lab check

- Run IDs: vcenter=0e5cdca9-b171-4b77-88dc-af43e7bb9417; No-ID ESXi sheet lookup=540ce636-4a3a-4a4c-b7af-f83f3c8ba13c; sheet-name member=82c3dc3a-8ba1-4ad0-9688-207c4ac5f7e7; Unresolved host=c2544c3b-2862-447d-ab97-66aaeb639105; No-ID array host lookup=e2edf66f-2e6a-4f6d-9ba3-b7cfe72a5c48; Short-name array host lookup=a07f3586-6c78-40e0-b0f3-775c2c09745c; Windows no-ID lookup=1e3253ec-39b2-43bd-b6a3-7ff3052e0a29; Windows server read (WinRM)=11a1d15f-e0f7-4c69-8f2d-649b6d941c47
- Result: 36 PASS, 1 FAIL, 3 SKIP

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
| Windows server read (WinRM) | PASS | Sheet host stays visible | lookup=not found — not in vCenter, no array host of that name, no iSCSI login from 10.132.30.137; add its WWPN/IQN on the Hosts tab |
| Windows server read (WinRM) | PASS | Host read carries no password field |  |
| Windows server read (WinRM) | FAIL | Host-side read succeeded | login failed for administrator@10.132.30.137 — check the Hosts tab login |
| Windows server read (WinRM) | PASS | Run detail does not echo host password |  |
| Windows server read (WinRM) | PASS | Events do not echo host password |  |
| Windows server read (WinRM) | SKIP | Typed-vs-read blocker | WinRM did not return an FC WWPN; no mismatch comparison possible |
| Linux | SKIP | Linux host login | No Linux host/address/login provided |

## Discovered host facts

| Section | Host / OS | Serial | WWPNs | IQNs | Lookup / read | Multipath |
|---|---|---|---|---|---|---|
| No-ID ESXi sheet lookup | 10.132.30.47 / esxi | CN763604C4 | 100008F1EAC03DE7, 100008F1EAC03DE8 | iqn.1998-01.com.vmware:dl380g9r11u07.grsbtelab.ap.hpecorp.net:1656314103:66 | found in vCenter as 10.132.30.47;  |  |
| Unresolved host | zz_spec014_unknown / linux |  |  |  | not found — not in vCenter, no array host of that name, no iSCSI login from 192.0.2.123; add its WWPN/IQN on the Hosts tab;  |  |
| No-ID array host lookup | HPE_VM_7f21bf6bf27da180152ea344 / vme |  |  | iqn.2024-12.com.hpe:vmenode3:42802 | found on the array as host HPE_VM_7f21bf6bf27da180152ea344;  |  |
| Short-name array host lookup | HPE_VM_7f21bf6bf27da180152ea344.spec014.local / vme |  |  | iqn.2024-12.com.hpe:vmenode3:42802 | found on the array as host HPE_VM_7f21bf6bf27da180152ea344 (short-name match);  |  |
| Windows no-ID lookup | arcus-win137 / windows |  |  |  | not found — not in vCenter, no array host of that name, no iSCSI login from 10.132.30.137; add its WWPN/IQN on the Hosts tab;  |  |
| Windows server read (WinRM) | arcus-win137 / windows |  |  |  | not found — not in vCenter, no array host of that name, no iSCSI login from 10.132.30.137; add its WWPN/IQN on the Hosts tab; WINRM read failed — login failed for administrator@10.132.30.137 — check the Hosts tab login |  |
