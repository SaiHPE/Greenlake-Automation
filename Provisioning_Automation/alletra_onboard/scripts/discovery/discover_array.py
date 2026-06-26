#!/usr/bin/env python3
"""Read-only discovery of an HPE Alletra MP B10000 over SSH -> array-config.txt.

Runs ONLY ``show*`` commands; it never changes the array. Credentials are NOT stored in this file:
pass the host on the command line and the password via the ALLETRA_PASSWORD env var or the prompt.

    python discover_array.py <array-ip> [--user 3paradm] [--out array-config.txt]

On the jump box, use the app's venv python (it already has paramiko):
    .\.venv\Scripts\python.exe scripts\discovery\discover_array.py 10.64.154.225
"""

from __future__ import annotations

import argparse
import datetime
import getpass
import os
import sys

try:
    import paramiko
except ImportError:  # pragma: no cover
    sys.exit("paramiko is required:  pip install paramiko   (or use the app's .venv python)")

# Read-only. showportdev lines fail harmlessly if the FC port isn't fabric-synced yet (no zoning).
COMMANDS = [
    "showversion", "showsys -d", "shownet", "showwsapi",          # identity + is WSAPI enabled
    "showcpg", "showspace",                                       # pools + free capacity
    "showhost", "showhost -d", "showhostset",                     # defined hosts (likely none yet)
    "showvv", "showvvset", "showvlun -a",                         # volumes + exports (likely none yet)
    "showport", "showport -par",                                  # ALL ports incl. FC target WWPNs + state
    "showportdev ns 0:3:1", "showportdev ns 0:3:2",               # who the array SEES on each FC target
    "showportdev ns 1:3:1", "showportdev ns 1:3:2",               #   port (i.e. the zoning check)
    "showrcopy", "showtarget",                                    # replication / RC targets (none yet)
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only Alletra MP B10000 discovery (show* over SSH).")
    ap.add_argument("host", help="array management IP, e.g. 10.64.154.225")
    ap.add_argument("--user", default="3paradm")
    ap.add_argument("--out", default="array-config.txt")
    args = ap.parse_args()
    password = os.environ.get("ALLETRA_PASSWORD") or getpass.getpass(f"Password for {args.user}@{args.host}: ")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        args.host, username=args.user, password=password, timeout=15,
        look_for_keys=False, allow_agent=False,
    )
    lines = [f"# Alletra MP {args.host}  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"]
    for cmd in COMMANDS:
        _stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
        lines += [f"\n===== {cmd} =====", stdout.read().decode("utf-8", "replace").rstrip()]
        err = stderr.read().decode("utf-8", "replace").strip()
        if err:
            lines.append(f"[stderr] {err}")
    client.close()

    report = "\n".join(lines) + "\n"
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(report)
    print(report)
    print(f"\nSaved -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
