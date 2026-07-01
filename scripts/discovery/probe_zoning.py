#!/usr/bin/env python3
r"""Read-only ZONING probe for an HPE Alletra MP B10000 — verify FC zoning FROM THE ARRAY, no switch.

The idea (researched): the fabric name server is zoning-filtered, so what an array target port can
SEE on the fabric *is* its effective zoning. This script makes that concrete for each FC target port:

    showportdev ns <n:s:p>        -> host WWPNs ZONED to this port AND logged in  (the zoning result)
    showportdev fcfabric <n:s:p>  -> ALL devices on the fabric from this port      (IGNORES zoning)

    gap = fcfabric - ns  ->  WWPNs physically on the fabric but NOT zoned to this port
                              (a missing zone if one of YOUR hosts is in here;
                               just other people's devices otherwise)

So you can confirm "is my host zoned to the array on the right (odd/even) fabric?" without ever
logging into the Brocade switch. It is 100% read-only — only show* / showportdev commands.

    python probe_zoning.py <array-ip> [--user 3paradm] [--ports 0:3:1,0:3:2,1:3:1,1:3:2]
                                      [--hosts 10:00:..,10:00:..] [--out zoning-probe.txt]

On the jump box, use the app's venv python (it already has paramiko):
    .\.venv\Scripts\python.exe scripts\discovery\probe_zoning.py 10.64.122.140
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

_NSP = re.compile(r"\b(\d+):(\d+):(\d+)\b")
# A WWPN with or without separators -> 16 hex.
_WWPN = re.compile(r"\b(?:[0-9a-fA-F]{2}[:\-]?){7}[0-9a-fA-F]{2}\b")


def norm(wwpn: str) -> str:
    return "".join(c for c in wwpn if c in "0123456789abcdefABCDEF").upper()


def wwpns(text: str) -> set[str]:
    return {norm(m.group(0)) for m in _WWPN.finditer(text or "") if len(norm(m.group(0))) == 16}


def run(client, cmd: str) -> str:
    _in, out, err = client.exec_command(cmd, timeout=30)
    o = out.read().decode("utf-8", "replace").rstrip()
    e = err.read().decode("utf-8", "replace").strip()
    return o if o.strip() else (f"[stderr] {e}" if e else "")


def discover_target_ports(showport: str) -> list[str]:
    """FC target ports = lines from `showport` that mention 'target' and carry an n:s:p."""
    ports: list[str] = []
    for line in showport.splitlines():
        if "target" in line.lower():
            m = _NSP.search(line)
            if m:
                ports.append(m.group(0))
    # de-dup, keep order
    seen, ordered = set(), []
    for p in ports:
        if p not in seen:
            seen.add(p)
            ordered.append(p)
    return ordered


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only array-side FC zoning probe (ns vs fcfabric).")
    ap.add_argument("host", help="array management IP, e.g. 10.64.122.140")
    ap.add_argument("--user", default="3paradm")
    ap.add_argument("--ports", default="", help="comma list of n:s:p to probe; default: auto from showport")
    ap.add_argument("--hosts", default="", help="comma list of host WWPNs you EXPECT to be zoned (any format)")
    ap.add_argument("--out", default="zoning-probe.txt")
    args = ap.parse_args()
    password = os.environ.get("ALLETRA_PASSWORD") or getpass.getpass(f"Password for {args.user}@{args.host}: ")
    expected = {norm(w) for w in args.hosts.split(",") if w.strip()}

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(args.host, username=args.user, password=password, timeout=15,
                   look_for_keys=False, allow_agent=False)

    out: list[str] = [f"# Alletra MP zoning probe  {args.host}  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"]

    showport = run(client, "showport")
    out += ["\n===== showport =====", showport]
    showhost = run(client, "showhost -d")
    out += ["\n===== showhost -d (map WWPN -> host) =====", showhost]

    ports = [p.strip() for p in args.ports.split(",") if p.strip()] or discover_target_ports(showport)
    if not ports:
        out.append("\n[!] No FC target ports auto-detected — pass --ports 0:3:1,0:3:2,1:3:1,1:3:2")

    summary = ["\n==================  ZONING SUMMARY (per array target port)  =================="]
    for nsp in ports:
        node, _slot, port = nsp.split(":")
        fabric = "odd (F1)" if int(port) % 2 == 1 else "even (F2)"
        ns_raw = run(client, f"showportdev ns {nsp}")
        fab_raw = run(client, f"showportdev fcfabric {nsp}")
        zoned = wwpns(ns_raw)
        on_fabric = wwpns(fab_raw)
        gap = on_fabric - zoned

        out += [f"\n===== showportdev ns {nsp}  (zoned + logged in) =====", ns_raw or "(empty)"]
        out += [f"\n===== showportdev fcfabric {nsp}  (all fabric, ignores zoning) =====", fab_raw or "(empty)"]

        line = [f"\nPort {nsp}  [{fabric}]   zoned(ns)={len(zoned)}  on-fabric(fcfabric)={len(on_fabric)}  gap={len(gap)}"]
        if expected:
            here = sorted(expected & zoned)
            missing = sorted(expected & gap)
            line.append(f"    expected hosts ZONED here:     {here or 'none'}")
            line.append(f"    expected hosts on fabric but NOT zoned here: {missing or 'none'}  <-- would need a zone")
        else:
            line.append(f"    zoned WWPNs: {sorted(zoned) or 'none'}")
        summary += line

    client.close()
    summary.append(
        "\nLegend: a host WWPN in ns = it is zoned to that port AND logged in (effective zoning). "
        "In fcfabric-but-not-ns = on the fabric but not zoned to this port. Compare against the "
        "odd/even rule: each host HBA should be zoned to the array's odd ports on F1 and even on F2."
    )
    report = "\n".join(out + summary) + "\n"
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(report)
    print("\n".join(summary))
    print(f"\nFull raw output saved -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
