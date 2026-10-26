#!/usr/bin/env python3
r"""Read-only ESXi FC path probe — confirm zoning END-TO-END from the host side, no switch.

For each ESXi host it SSHes in and runs two read-only esxcli commands:

    esxcli storage san fc list        -> this host's HBA WWPNs (the initiators)
    esxcli storage core path list     -> the TARGET WWPNs the host can actually reach

If a host sees the array's target-port WWPNs as paths, zoning is working for that host (an unzoned
port would not appear). Cross-reference the target WWPNs here with the array's port WWPNs from
probe_zoning.py to confirm both fabrics are wired correctly. Read-only; requires SSH enabled on ESXi.

    python probe_esxi_paths.py <esxi-1> [<esxi-2> ...] [--user root] [--out esxi-paths.txt]

On the jump box, use the app's venv python (it already has paramiko):
    .\.venv\Scripts\python.exe scripts\discovery\probe_esxi_paths.py 10.x.x.a 10.x.x.b
"""

from __future__ import annotations

import argparse
import datetime
import getpass
import os
import re
import sys

try:
    import paramiko
except ImportError:  # pragma: no cover
    sys.exit("paramiko is required:  pip install paramiko   (or use the app's .venv python)")

_WWPN = re.compile(r"\b(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}\b")


def norm(w: str) -> str:
    return "".join(c for c in w if c in "0123456789abcdefABCDEF").upper()


def run(client, cmd: str) -> str:
    _in, out, err = client.exec_command(cmd, timeout=30)
    o = out.read().decode("utf-8", "replace").rstrip()
    e = err.read().decode("utf-8", "replace").strip()
    return o if o.strip() else (f"[stderr] {e}" if e else "")


def probe(host: str, user: str, password: str) -> tuple[str, set[str], set[str]]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    fc = run(client, "esxcli storage san fc list")
    paths = run(client, "esxcli storage core path list")
    client.close()

    # HBA (initiator) WWPNs come from the 'Port Name' lines of `san fc list`.
    initiators = {norm(m.group(0)) for line in fc.splitlines() if "port name" in line.lower()
                  for m in _WWPN.finditer(line)}
    # Target WWPNs come from the 'Target Identifier' lines of `core path list` (fc.<nodewwn>:<portwwn>).
    targets: set[str] = set()
    for line in paths.splitlines():
        if "target identifier" in line.lower():
            found = [norm(m.group(0)) for m in _WWPN.finditer(line)]
            if found:
                targets.add(found[-1])  # the port WWN is the second/last WWPN on the line
    raw = f"\n===== {host} : esxcli storage san fc list =====\n{fc}\n\n===== {host} : esxcli storage core path list =====\n{paths}"
    return raw, initiators, targets


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only ESXi FC path/zoning probe.")
    ap.add_argument("hosts", nargs="+", help="one or more ESXi host IPs")
    ap.add_argument("--user", default="root")
    ap.add_argument("--out", default="esxi-paths.txt")
    args = ap.parse_args()
    password = os.environ.get("ESXI_PASSWORD") or getpass.getpass(f"Password for {args.user}@ESXi: ")

    out = [f"# ESXi FC path probe  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"]
    summary = ["\n==================  ESXi -> array reachability (zoning end-to-end)  =================="]
    for host in args.hosts:
        try:
            raw, initiators, targets = probe(host, args.user, password)
        except Exception as exc:  # noqa: BLE001
            summary.append(f"\n{host}: FAILED — {type(exc).__name__}: {str(exc)[:120]} (is SSH enabled on this ESXi?)")
            continue
        out.append(raw)
        summary.append(f"\n{host}")
        summary.append(f"    HBA WWPNs (initiators): {sorted(initiators) or 'none'}")
        summary.append(f"    array target WWPNs seen: {len(targets)} -> {sorted(targets) or 'NONE (not zoned / no paths)'}")

    summary.append(
        "\nIf 'array target WWPNs seen' is non-empty on both HBAs, zoning + multipathing are working "
        "for that host. Match these against probe_zoning.py's array port WWPNs to confirm odd/even."
    )
    report = "\n".join(out + summary) + "\n"
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(report)
    print("\n".join(summary))
    print(f"\nFull raw output saved -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
