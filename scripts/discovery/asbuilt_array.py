#!/usr/bin/env python3
# =====================================================================
# READ-ONLY array pull  --  HPE Alletra MP B10000 (3PAR/Primera lineage)
# ---------------------------------------------------------------------
# One SSH session, ONLY `show*` / `checkhealth` commands. No config change
# of any kind. Two purposes in one pass:
#   * AS-BUILT   : the hardware/config/inventory + checkhealth for the doc
#   * PROVISIONING: the readiness/object reads from ADR 0010
# Dumps raw output to ~/alletra_probe_out/asbuilt_array.txt, and writes the
# array's own FC port WWPNs to ~/alletra_probe_out/array_wwpns.txt so the
# switch probe can filter to "only where the Alletra MP connects".
#
# Run (needs paramiko -- see the README):
#   python asbuilt_array.py
# Prompts for the 3paradm password (never stored). Override target:
#   set ARRAY_IP=10.64.122.140  &  set ARRAY_USER=3paradm   (Windows)
# =====================================================================
import os, sys, getpass, datetime, re
from pathlib import Path

try:
    import paramiko
except ImportError:
    sys.exit("paramiko not found -- 'pip install paramiko' (or run with the app venv python). See README.")

ARRAY = os.environ.get("ARRAY_IP", "10.64.122.140")   # VZ array
USER  = os.environ.get("ARRAY_USER", "3paradm")
OUT   = Path.home() / "alletra_probe_out"
OUT.mkdir(parents=True, exist_ok=True)
DUMP  = OUT / "asbuilt_array.txt"
WWPNS = OUT / "array_wwpns.txt"

# All read-only. AS-BUILT block feeds the doc tables; PROVISIONING block feeds ADR 0010.
COMMANDS = [
    "# ---- AS-BUILT: system / nodes / hardware / inventory ----",
    "shownode", "shownode -d", "showcage", "showcage -d",
    "showsys", "showsys -d", "shownet", "showdate",
    "showversion", "showversion -b", "showlicense",
    "showpd", "showspace", "showcpg", "showcpg -space",
    "showport", "showport -par", "showinventory",
    "# ---- AS-BUILT: health (Panduranga wants checkhealth output) ----",
    "checkhealth -svc -detail",
    "# ---- PROVISIONING readiness / objects (ADR 0010) ----",
    "showwsapi", "showhost", "showhost -d", "showhost -listpersona",
    "showhostset", "showvv", "showvvset", "showvlun -a", "showvlun -t",
    "showtarget", "showrcopy",
]


def array_port_wwpns(showport_text: str) -> list[str]:
    """FC target Port_WWN column from `showport` (col idx 4), normalized upper-hex."""
    out: list[str] = []
    for line in showport_text.splitlines():
        p = line.split()
        if len(p) >= 7 and ":" in p[0] and p[0][:1].isdigit() and p[1] == "target" and p[6] == "FC":
            w = re.sub(r"[^0-9a-fA-F]", "", p[4]).upper()
            if len(w) == 16 and w not in out:
                out.append(w)
    return out


def main():
    pw = os.environ.get("ARRAY_PW") or getpass.getpass(f"Password for {USER}@{ARRAY}: ")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ARRAY, username=USER, password=pw, timeout=30, look_for_keys=False, allow_agent=False)

    lines = [f"# ASBUILT + PROVISIONING READ-ONLY ARRAY DUMP  {datetime.datetime.now().isoformat()}",
             f"# array={ARRAY}  user={USER}"]
    showport_text = ""
    for cmd in COMMANDS:
        if cmd.startswith("#"):
            lines.append("\n" + cmd)
            continue
        lines.append(f"\n===== $ {cmd} =====")
        try:
            _i, o, e = c.exec_command(cmd, timeout=120)
            out = o.read().decode("utf-8", "replace")
            err = e.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            out, err = "", f"[error] {exc!r}"
        lines.append(out or err)
        if cmd == "showport":
            showport_text = out
        print(f"ran: {cmd}")
    c.close()

    DUMP.write_text("\n".join(lines), encoding="utf-8")
    wwpns = array_port_wwpns(showport_text)
    WWPNS.write_text("\n".join(wwpns), encoding="utf-8")
    print(f"\nWROTE  {DUMP}")
    print(f"WROTE  {WWPNS}  ({len(wwpns)} array FC port WWPNs -- used by asbuilt_switch.py)")


if __name__ == "__main__":
    main()
