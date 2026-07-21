# As-built + provisioning read-only probe suite

Three **strictly read-only** probes that pull everything we need to (a) build the as-built
documentation tables and (b) confirm provisioning readiness (ADR 0010). Nothing here ever writes to
the array or the switch — array side is `show*` / `checkhealth` only; switch side is
`switchshow` / `fabricshow` / `ipaddrshow` / `chassisshow` / `nsshow` / `version` only (no zoning/config
command is ever issued).

All three prompt for the password (never stored) and write their output to **`~/alletra_probe_out/`**
(`C:\Users\<you>\alletra_probe_out\` on Windows).

## Targets (edit at the top of each script, or set env vars)

| Probe | Default target | Creds |
|---|---|---|
| `asbuilt_array.py` | array `10.64.122.140` | `3paradm` / (prompt) |
| `asbuilt_wsapi.py` | array `10.64.122.140` | `3paradm` / (prompt) |
| `asbuilt_switch.py` | `10.64.154.53` (F1) + `10.64.154.52` (F2) | `PanduM` / (prompt) |

## On the jump server

```powershell
# 1) get the scripts
cd C:\Users\gsairoop\Documents\Greenlake-Automation      # your repo clone root
git fetch origin
git checkout probe/asbuilt-lab-reads
git pull origin probe/asbuilt-lab-reads

cd Provisioning_Automation\alletra_onboard\scripts\discovery

# 2) paramiko is needed for the two SSH probes. If 'import paramiko' fails:
pip install paramiko
# ...or run everything with the app venv python if you have it:
#   & "C:\...\alletra_onboard\.venv\Scripts\python.exe" asbuilt_array.py

# 3) run in this order (array first -- it writes array_wwpns.txt that the switch probe filters on)
python asbuilt_array.py      # -> ~/alletra_probe_out/asbuilt_array.txt  (+ array_wwpns.txt)
python asbuilt_wsapi.py      # -> ~/alletra_probe_out/asbuilt_wsapi.txt
python asbuilt_switch.py     # -> ~/alletra_probe_out/asbuilt_switch.txt
```

## Then send back

The three files from `~/alletra_probe_out/`:
`asbuilt_array.txt`, `asbuilt_wsapi.txt`, `asbuilt_switch.txt`.

From those I format the as-built tables (array config + checkhealth + the Alletra-MP-port→switch+port
mapping) and confirm provisioning readiness (`showhost -d` = who's on+zoned; CPG `SSD_r6` capacity;
WSAPI ready), then build + release.

## Notes

- `asbuilt_switch.py` reads `array_wwpns.txt` (written by `asbuilt_array.py`) and prints a filtered
  **"Alletra MP attached ports"** section per switch — the exact "which switch port" mapping. If the
  array's WWPNs don't appear on either switch, the VZ array is on a **different fabric** than the LZ
  switches (`10.64.154.x`) — which the dump will make obvious.
- The jump server (`10.54.122.137`) must route to **both** the array subnet (`10.64.122.x`) and the
  switch subnet (`10.64.154.x`).
