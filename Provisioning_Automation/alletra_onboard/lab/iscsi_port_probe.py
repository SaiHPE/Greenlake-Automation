"""Which lab array can serve iSCSI to this LabRAT workspace? READ-ONLY, no prompts.

    .\\.venv\\Scripts\\python.exe lab\\iscsi_port_probe.py

Changes nothing. Logs in over SSH as 3paradm (LAB_ARRAY_PW from .env) to D22U27 (10.64.122.99) and the
CRV Vault Zone array (10.64.122.140), and runs show commands and CLI help only: the iSCSI ports and
their link state, SFPs, the free ports 0:4:4 / 1:4:4, and the help for the commands that would give a
port the iSCSI role and an address. The Landing Zone array (10.64.154.225) is only pinged and its SSH
port tried (it was unreachable on 2026-10-05). From this workspace it pings the lab networks and
every iSCSI address an array reports. Everything goes in ~\\Downloads\\iscsi_port_probe.zip.
"""
import os
import re
import shutil
import socket
import subprocess
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402

ARRAYS = [("D22U27", "10.64.122.99"), ("VZ", "10.64.122.140")]
LZ = ("LZ", "10.64.154.225")
OUT = os.path.join(os.path.expanduser("~"), "Downloads", "iscsi_port_probe")
fl.OUT = OUT
READS = [
    "showsys",
    "showversion",
    "showport",
    "showport -sfp",
    "showport -i",
    "showport -par",
    "showport -iscsi",
    "showport -iscsivlans",
    "showport -rcip",
    "showport -file",
    "showiscsisession",
    "showhost -d",
]
HELP = ["help controliscsiport", "help showport"]   # read once, on D22U27
# Address -> what it is. Pings only.
TARGETS = [
    ("10.30.14.254", "gateway of the iSCSI network E18U31 used (10.30.14.0/24)"),
    ("10.54.90.70", "D22U27 file port 0:4:1"),
    ("10.54.122.92", "D22U27 RCIP port 0:4:3"),
    ("10.64.122.99", "D22U27 management"),
    ("10.64.122.140", "VZ management"),
    ("10.64.154.225", "LZ management"),
]
IPV4 = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
RESULTS = []


def note(text):
    print("      " + text)
    RESULTS.append("      " + text)


def file_name(tag, cmd):
    return "%s_%s.txt" % (tag, cmd.replace(" ", "_").replace("-", ""))


def ping(addr):
    out = subprocess.run(["ping", "-n", "2", "-w", "1500", addr], capture_output=True, text=True, timeout=30).stdout
    return "TTL=" in out.upper(), out


def tcp(addr, port):
    try:
        socket.create_connection((addr, port), timeout=5).close()
        return "open"
    except OSError as exc:
        return "no answer (%s)" % type(exc).__name__


def iscsi_rows(text):
    """`showport -iscsi` -> [(n:s:p, state, ip)]."""
    out = []
    for ln in text.splitlines():
        p = ln.split()
        if len(p) >= 3 and re.match(r"^\d+:\d+:\d+$", p[0]):
            out.append((p[0], p[1], p[2]))
    return out


def read_array(tag, host, password, extra=()):
    fl.banner("%s %s: show commands and help only" % (tag, host))
    try:
        c = fl.ssh(host, password)
    except Exception as exc:  # noqa: BLE001
        note("%s: SSH login failed: %s %s" % (tag, type(exc).__name__, exc))
        return None
    raw = {}
    try:
        for cmd in list(READS) + list(extra):
            try:
                raw[cmd] = fl.run(c, cmd)
            except Exception as exc:  # noqa: BLE001
                raw[cmd] = "ERROR %r" % exc
            fl.save(file_name(tag, cmd), "# %s\n%s" % (cmd, raw[cmd]))
    finally:
        c.close()
    name = next((ln.split()[1] for ln in raw["showsys"].splitlines() if ln.split()[:1] and ln.split()[0].startswith("0x")), "?")
    note("%s: %s, %s" % (tag, name, next((ln.strip() for ln in raw["showversion"].splitlines() if ln.startswith("Release")), "?")))
    rows = iscsi_rows(raw["showport -iscsi"])
    note("%s: %d iSCSI port(s): %s" % (tag, len(rows), "; ".join("%s %s %s" % r for r in rows) or "none"))
    for ln in raw["showport"].splitlines():
        p = ln.split()
        if p[:1] and (p[0].endswith(":4:4") or "iSCSI" in p):
            note("%s: showport  %s" % (tag, " ".join(p)))
    for ln in raw["showport -sfp"].splitlines():
        p = ln.split()
        if p[:1] and re.match(r"^\d+:4:\d+$", p[0]):
            note("%s: sfp       %s" % (tag, " ".join(p)))
    sessions = [ln for ln in raw["showiscsisession"].splitlines() if ln.strip() and not ln.startswith("No ")]
    note("%s: iSCSI sessions: %s" % (tag, len(sessions) - 1 if len(sessions) > 1 else 0))
    return rows


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    password = fl.lab_secret("LAB_ARRAY_PW")
    iscsi_ips = []
    for tag, host in ARRAYS:
        rows = read_array(tag, host, password, HELP if tag == "D22U27" else ())
        iscsi_ips += [("%s iSCSI %s (%s)" % (tag, nsp, state), ip) for nsp, state, ip in rows or [] if IPV4.match(ip) and ip != "0.0.0.0"]
    if os.path.isfile(os.path.join(OUT, "D22U27_help_controliscsiport.txt")):
        text = open(os.path.join(OUT, "D22U27_help_controliscsiport.txt"), encoding="utf-8").read()
        note("help controliscsiport: %s" % ("present" if " addr" in text else (text.strip().splitlines()[1:2] or ["(empty)"])[0][:120]))

    fl.banner("LZ %s: reachability only" % LZ[1])
    note("LZ: SSH port 22 %s" % tcp(LZ[1], 22))

    fl.banner("This workspace: which addresses answer")
    try:
        me = "%s %s" % (socket.gethostname(), socket.gethostbyname(socket.gethostname()))
    except OSError as exc:
        me = "(lookup failed: %s)" % exc
    note("this workspace: " + me)
    log = []
    for addr, what in TARGETS + [(ip, what) for what, ip in iscsi_ips]:
        ok, out = ping(addr)
        extra = ("; TCP 3260 " + tcp(addr, 3260)) if (what, addr) in {(w, i) for w, i in iscsi_ips} else ""
        note("ping %-15s %-7s %s%s" % (addr, "answers" if ok else "silent", what, extra))
        log.append("# ping %s (%s)\n%s" % (addr, what, out))
    fl.save("workspace_pings.txt", "\n".join(log))
    fl.save("workspace_route_print.txt", subprocess.run(["route", "print", "-4"], capture_output=True, text=True, timeout=30).stdout)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        if os.path.isdir(OUT):
            fl.save("script_stopped.txt", traceback.format_exc())
        raise
    finally:
        if os.path.isdir(OUT):
            fl.save("report.txt", "\n".join(RESULTS))
            fl.banner("Done. Send me %s" % shutil.make_archive(OUT, "zip", OUT))
