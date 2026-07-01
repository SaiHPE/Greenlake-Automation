#!/usr/bin/env python3
r"""Read-only Brocade FOS switch probe — understand the zoning output format. NO WRITES, EVER.

Runs a fixed, EXACT-MATCH allowlist of read-only Fabric OS commands on each switch and dumps the
output (per switch + a combined file), so we can see the real cfgshow/zoneshow/alishow format and
compare two switches (FOS version, command availability). There is no code path that can run a write
command: each command is matched against the literal allowlist below before being sent.

    python probe_switch.py 10.64.154.53 10.64.154.52 [--user PanduM] [--out switch-probe.txt]

On a fresh box:  python -m pip install paramiko   then run the line above.
Password: set BROCADE_PASSWORD, or type it at the prompt (same password is reused for all switches).
"""

from __future__ import annotations

import argparse
import datetime
import getpass
import os
import socket
import sys

try:
    import paramiko
except ImportError:  # pragma: no cover
    sys.exit("paramiko is required:  python -m pip install paramiko")

# EXACT command strings the probe may run — all read-only. Nothing else is ever sent to the switch.
# (defzone --show / zoneshow --validate are read-only inspection forms; no write variant is listed.)
READ_COMMANDS: tuple[str, ...] = (
    "version",            # FOS version — to see if two switches differ
    "switchshow",         # switch + ports + attached WWNs (who's logged into THIS switch)
    "fabricshow",         # the switches that make up this fabric
    "cfgshow",            # FULL zoning: Defined + Effective config, zones, aliases  <-- the key one
    "cfgactvshow",        # the Effective (active) config only
    "zoneshow",           # zones + members
    "alishow",            # aliases -> WWNs
    "nsshow",             # local name server (devices logged into this switch)
    "nscamshow",          # fabric-wide name server (all devices, all switches)
    "defzone --show",     # default-zone policy (read-only --show)
    "zoneshow --validate",  # read-only validation of the zone db
)


def tcp_ok(host: str, port: int = 22, timeout: float = 5.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:  # noqa: BLE001
        return False


def run_readonly(client, command: str) -> str:
    if command not in READ_COMMANDS:  # belt-and-suspenders: only the literal allowlist is runnable
        raise ValueError(f"refused: '{command}' is not in the read-only allowlist")
    _in, out, err = client.exec_command(command, timeout=45)
    o = out.read().decode("utf-8", "replace").rstrip()
    e = err.read().decode("utf-8", "replace").strip()
    return o if o.strip() else (f"[stderr] {e}" if e else "(no output)")


def probe(host: str, user: str, password: str) -> tuple[str, dict[str, str]]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    results = {cmd: run_readonly(client, cmd) for cmd in READ_COMMANDS}
    client.close()
    return host, results


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only Brocade FOS switch probe (NO writes).")
    ap.add_argument("hosts", nargs="+", help="one or more switch IPs, e.g. 10.64.154.53 10.64.154.52")
    ap.add_argument("--user", default="PanduM")
    ap.add_argument("--out", default="switch-probe.txt")
    args = ap.parse_args()
    password = os.environ.get("BROCADE_PASSWORD") or getpass.getpass(f"Password for {args.user}@<switches>: ")

    out = [f"# Brocade FOS switch probe  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
           "# READ-ONLY. Commands run: " + ", ".join(READ_COMMANDS) + "\n"]
    summary = ["================  SWITCH PROBE SUMMARY  ================"]
    for host in args.hosts:
        if not tcp_ok(host):
            summary.append(f"{host:<16} UNREACHABLE on 22")
            out.append(f"\n##### {host} : UNREACHABLE on 22 #####")
            continue
        try:
            _h, results = probe(host, args.user, password)
        except Exception as exc:  # noqa: BLE001
            summary.append(f"{host:<16} FAILED — {type(exc).__name__}: {str(exc)[:80]}")
            out.append(f"\n##### {host} : {type(exc).__name__}: {str(exc)[:120]} #####")
            continue
        ver = results.get("version", "").splitlines()
        fos = next((ln.strip() for ln in ver if "Fabric OS" in ln or "v" in ln.lower()), ver[0] if ver else "?")
        zones = results.get("cfgshow", "").lower().count("zone:")
        aliases = results.get("cfgshow", "").lower().count("alias:")
        summary.append(f"{host:<16} OK   {fos[:48]:<48}  cfgshow: ~{zones} zone lines, ~{aliases} alias lines")
        out.append(f"\n{'#' * 78}\n##### SWITCH {host} #####\n{'#' * 78}")
        for cmd in READ_COMMANDS:
            out.append(f"\n===== [{host}] {cmd} =====\n{results[cmd]}")

    report = "\n".join(out + ["\n"] + summary) + "\n"
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(report)
    print("\n".join(summary))
    print(f"\nFull raw output saved -> {args.out}  (send me this to compare the two switches' formats)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
