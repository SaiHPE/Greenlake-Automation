r"""Read-only ESXi discovery over SSH (paramiko) -> esxi-config.txt.

Runs read-only ``esxcli`` / ``vmware`` commands on each ESXi host. No PowerCLI needed - same
toolchain as discover_array.py. SSH must be enabled on the ESXi hosts (Host -> Manage -> Services).
Credentials are NOT stored here: pass the host IPs and supply the password via the ESXI_PASSWORD
env var or the prompt (assumed the same for all hosts).

    python discover_esxi_ssh.py 10.54.159.14 10.54.159.63 10.54.159.64 [--user root]

On the jump box, use the app's venv python (it already has paramiko):
    .\.venv\Scripts\python.exe scripts\discovery\discover_esxi_ssh.py 10.54.159.14 10.54.159.63 10.54.159.64
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

# All read-only (list / version).
COMMANDS = [
    "vmware -vl",                              # ESXi version + build -> array host persona
    "esxcli storage core adapter list",       # HBAs overview
    "esxcli storage san fc list",             # FC HBA WWPNs, port state, speed
    "esxcli iscsi adapter list",              # iSCSI adapters (if any)
    "esxcli storage nmp device list",         # multipath: SATP/PSP per device (round-robin ALUA?)
    "esxcli storage core device list",        # devices/LUNs with vendor + size
    "esxcli storage vmfs extent list",        # datastores
]


def run_host(host: str, user: str, password: str, out: list[str]) -> None:
    out.append(f"\n########## ESXi {host} ##########")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=15,
                       look_for_keys=False, allow_agent=False)
    except Exception as exc:  # noqa: BLE001 - report and move to the next host
        out.append(f"[connect failed] {type(exc).__name__}: {exc}  (is SSH enabled on this host?)")
        return
    for cmd in COMMANDS:
        _stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
        out.append(f"\n===== {cmd} =====")
        out.append(stdout.read().decode("utf-8", "replace").rstrip())
        err = stderr.read().decode("utf-8", "replace").strip()
        if err:
            out.append(f"[stderr] {err}")
    client.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only ESXi discovery over SSH (esxcli).")
    ap.add_argument("hosts", nargs="+", help="ESXi management IPs, e.g. 10.54.159.14 10.54.159.63")
    ap.add_argument("--user", default="root")
    ap.add_argument("--out", default="esxi-config.txt")
    args = ap.parse_args()
    password = os.environ.get("ESXI_PASSWORD") or getpass.getpass(f"Password for {args.user} on the ESXi hosts: ")

    out = [f"# ESXi discovery  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"]
    for host in args.hosts:
        run_host(host, args.user, password, out)
    report = "\n".join(out) + "\n"
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(report)
    print(report)
    print(f"\nSaved -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
