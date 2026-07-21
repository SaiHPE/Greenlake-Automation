#!/usr/bin/env python3
# =====================================================================
# READ-ONLY switch pull  --  Brocade FOS (HPE SN3600B / SN6700B)
# ---------------------------------------------------------------------
# Logs into BOTH fabric switches and runs ONLY read-only show commands
# (switchshow / fabricshow / ipaddrshow / chassisshow / nsshow / version).
# NEVER runs a config/zoning write. For the as-built "which Alletra MP
# port is on which switch + switch port" table (Panduranga's scope: only
# where the Alletra MP connects, not the whole fabric).
#
# If ~/alletra_probe_out/array_wwpns.txt exists (written by asbuilt_array.py),
# it also prints a FILTERED "Alletra MP attached ports" section per switch.
# Dumps to ~/alletra_probe_out/asbuilt_switch.txt.
#
# Run (needs paramiko):  python asbuilt_switch.py
# Prompts once for the switch password (default user PanduM). Override:
#   set SWITCH_USER=PanduM  &  set SWITCH_PW=...   (Windows)
# =====================================================================
import os, sys, getpass, datetime, re
from pathlib import Path

try:
    import paramiko
except ImportError:
    sys.exit("paramiko not found -- 'pip install paramiko' (or run with the app venv python). See README.")

# name, ip  -- edit here if the Alletra MP is on different switches.
SWITCHES = [
    ("SN3600_E21U38_F1", os.environ.get("SWITCH_F1", "10.64.154.53")),
    ("SN3600_E21U36_F2", os.environ.get("SWITCH_F2", "10.64.154.52")),
]
USER = os.environ.get("SWITCH_USER", "PanduM")
OUT  = Path.home() / "alletra_probe_out"
OUT.mkdir(parents=True, exist_ok=True)
DUMP = OUT / "asbuilt_switch.txt"
WWPNS = OUT / "array_wwpns.txt"

# All read-only Brocade FOS commands. switchshow is the key one (port index + attached WWPN + the
# effective zoning cfg name in its header). nsshow = LOCAL nameserver only (bounded); we deliberately
# do NOT run nscamshow/cfgshow (fabric-wide, hundreds of zones on a shared prod fabric).
COMMANDS = ["switchshow", "fabricshow", "ipaddrshow", "chassisshow", "switchname", "version", "nsshow"]


def _norm(s: str) -> str:
    return re.sub(r"[^0-9a-fA-F]", "", s).upper()


def load_array_wwpns() -> list[str]:
    if WWPNS.exists():
        return [_norm(w) for w in WWPNS.read_text(encoding="utf-8").split() if _norm(w)]
    return []


def filter_ports(switchshow: str, array_wwpns: list[str]) -> list[str]:
    """switchshow lines whose attached WWPN is one of the Alletra MP's ports."""
    hits = []
    for line in switchshow.splitlines():
        norm = _norm(line)
        if any(w and w in norm for w in array_wwpns):
            hits.append(line.rstrip())
    return hits


def main():
    pw = os.environ.get("SWITCH_PW") or getpass.getpass(f"Password for {USER}@both switches: ")
    array_wwpns = load_array_wwpns()
    lines = [f"# ASBUILT READ-ONLY SWITCH DUMP  {datetime.datetime.now().isoformat()}",
             f"# user={USER}  array_wwpns_loaded={len(array_wwpns)} "
             f"({'run asbuilt_array.py first for the filtered view' if not array_wwpns else 'filtering ON'})"]

    for name, ip in SWITCHES:
        lines.append(f"\n\n########## SWITCH {name}  ({ip}) ##########")
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            c.connect(ip, username=USER, password=pw, timeout=30, look_for_keys=False, allow_agent=False)
        except Exception as exc:  # noqa: BLE001
            lines.append(f"[connect error] {exc!r}")
            print(f"{name}: connect FAILED ({exc!r})")
            continue
        switchshow = ""
        for cmd in COMMANDS:
            lines.append(f"\n===== [{name}] $ {cmd} =====")
            try:
                _i, o, e = c.exec_command(cmd, timeout=60)
                out = o.read().decode("utf-8", "replace")
                err = e.read().decode("utf-8", "replace")
            except Exception as exc:  # noqa: BLE001
                out, err = "", f"[error] {exc!r}"
            lines.append(out or err)
            if cmd == "switchshow":
                switchshow = out
            print(f"{name}: ran {cmd}")
        c.close()
        if array_wwpns:
            hits = filter_ports(switchshow, array_wwpns)
            lines.append(f"\n----- [{name}] ALLETRA MP ATTACHED PORTS (filtered) -----")
            lines.append("\n".join(hits) if hits else "(no Alletra MP WWPN found on this switch)")

    DUMP.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWROTE  {DUMP}")


if __name__ == "__main__":
    main()
