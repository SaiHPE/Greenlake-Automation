# Discovery scripts (read-only)

Run these once per environment to capture the **current config** before building any
host / LUN / snapshot / replication / DR automation. Both are **strictly read-only**
(`show*` / `Get-*`) — they change nothing on the array, hosts, or vCenter.

No credentials are stored in these files — you pass the host and are prompted for (or
env-supply) the password.

## 1. Array — `discover_array.py` (SSH, paramiko)

```powershell
# on the jump box, use the app's venv python (it already has paramiko):
.\.venv\Scripts\python.exe scripts\discovery\discover_array.py 10.64.154.225
# (prompts for the 3paradm password; or set $env:ALLETRA_PASSWORD first)
```
Writes `array-config.txt`: WSAPI state, CPG/capacity, hosts, volumes, VLUNs, FC target
WWPNs + port state, `showportdev ns` (zoning visibility), and replication state.

## 2. ESXi via vCenter — `discover_esxi.ps1` (PowerCLI)

```powershell
Install-Module VMware.PowerCLI -Scope CurrentUser    # once
.\scripts\discovery\discover_esxi.ps1 -VCenter 10.54.154.226 -User Administrator@vsphere.local
# (prompts for the password)
```
Prints ESXi OS/version, **FC HBA WWPNs**, iSCSI IQNs, datastores, and any 3PARdata LUNs.

## Correlate / verify zoning (no switch access needed)

Match the **host WWPNs** (script 2) against the array's **`showportdev ns`** output (script 1):
if a host WWPN appears on a target port, that path is cabled + zoned. The SAN switch CLI is
only needed to *create* zones — verification is array-side.

See the provisioning runbook: `docs/runbooks/provisioning-esxi-fc.md`.
