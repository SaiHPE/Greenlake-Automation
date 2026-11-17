"""What a migration pair looks like before the Migration step reads it (BL-27, SPEC-027 R4). READ-ONLY,
no prompts.

    $env:MIG_SOURCE_HOST = "<the 3PAR's management address>"   # PowerShell; nothing has a default
    $env:MIG_SOURCE_USER = "<its read-only account>"
    $env:MIG_DEST_HOST   = "<E18U31's management address>"
    $env:MIG_DEST_USER   = "<E18U31's account>"
    .\\.venv\\Scripts\\python.exe lab\\mig_pair_capture.py

Changes nothing on either array. The passwords come from MIG_SOURCE_PW and MIG_DEST_PW, in the
environment or the app's .env (never in this script). MIG_SOURCE_TAG and MIG_DEST_TAG name the two
folders (default 3par and e18u31; the Primera 630 + rack13-ARCUS pair is captured the same way later).

Like rcip_pair_capture.py, it logs in to each array over SSH itself and sends each command as it is
written below: nothing goes through the tool's read client, so `help showrsv` and `showrsv -l scsi3`
are captured although `showrsv` is not on the tool's allowlist yet (it joins only after its help has
been read, SPEC-027 R4). Before the first login, send() checks every command: only show* and help, no
shell or Tcl metacharacter, and never `showtarget -rescan`. No WSAPI, no host, no switch.
1. source (3PAR 20850 R2): showsys, showversion -a -b, showport, showhost -d, showhostset -d, showvv,
   showvvset, showvlun -a, showrcopy, help showrsv, showrsv -l scsi3
2. destination (E18U31): showsys, showversion, showport, showport -c, showport -peer, showtarget,
   showtarget -lun all, showcpg, showvv
3. says: each array's name, model, serial and OS; the source's patches; the destination's FC peer
   ports; on which of them showtarget lists the source's node WWN

Output in RCIP_LAB_DIR (default ~/Downloads): mig_pair_capture/<tag>/ with one file per command (first
line `# <command>`), named as tests/fixtures/mig_pair/<tag>/ expects them, and _index.txt (lines and
seconds per command); report.txt with the PASS/FAIL lines; all of it zipped to mig_pair_capture.zip.
Copy each <tag>/ folder to tests/fixtures/mig_pair/ after scrubbing it: host and user names that look
like a customer's or a colleague's (lab names are fine), any email address (lab-user@example.com). No
password is ever written to a file. Afterwards, `showeventlog` on both arrays should show nothing from
this script.
"""
import os
import re
import shutil
import sys
import time
import traceback

import paramiko

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # after the sys.path line, like the other lab scripts

BASE = os.environ.get("RCIP_LAB_DIR") or os.path.join(os.path.expanduser("~"), "Downloads")
OUT = os.path.join(BASE, "mig_pair_capture")
fl.OUT = OUT

# SPEC-027 R4 and work packet BL-27, in the order they are sent. `help showrsv` comes before
# `showrsv -l scsi3`, so the help is on file even if the array refuses the read.
SOURCE_READS = [
    "showsys", "showversion -a -b", "showport", "showhost -d", "showhostset -d", "showvv", "showvvset",
    "showvlun -a", "showrcopy", "help showrsv", "showrsv -l scsi3",
]
DEST_READS = [
    "showsys", "showversion", "showport", "showport -c", "showport -peer", "showtarget", "showtarget -lun all",
    "showcpg", "showvv",
]

FORBIDDEN_CHARS = set(";|&`$<>[]{}\\\"'\n\r")
ACTING_OPTIONS = {"showtarget": {"-rescan"}}
NSP = re.compile(r"^\d+:\d+:\d+$")
WWN = re.compile(r"^[0-9A-Fa-f]{16}$")
TAG = re.compile(r"^[A-Za-z0-9_.-]+$")
SYS_ID = re.compile(r"^(0x[0-9A-Fa-f]+|\d+)$")
REFUSAL = re.compile(r"^(error\b|invalid\b|unknown\b|usage\b)|command not found|not (running|licensed|supported)",
                     re.IGNORECASE)
RESULTS = []


class NotARead(Exception):
    """A command this script will not send. Raised before anything is sent."""


def refusal(cmd):
    """Why send() would refuse `cmd`, or None when it is a read."""
    if FORBIDDEN_CHARS & set(cmd):
        return "it contains a shell or Tcl metacharacter"
    words = cmd.split()
    first = (words or [""])[0]
    if first != "help" and not first.startswith("show"):
        return f"'{first}' is not a show or help command"
    acting = ACTING_OPTIONS.get(first, set()) & {w.lower() for w in words[1:]}
    if acting:
        return f"{', '.join(sorted(acting))} makes '{first}' act"
    return None


def setting(name, example):
    value = (os.environ.get(name) or "").strip()
    if not value:
        sys.exit(f'{name} is not set. Set it first (PowerShell: $env:{name} = "{example}") and run again.')
    return value


def ssh(host, user, pw):
    """fl.ssh with the user named: the source's read-only account is not 3paradm."""
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username=user, password=pw, timeout=20, allow_agent=False, look_for_keys=False)
    return c


def send(c, cmd):
    why = refusal(cmd)
    if why:
        raise NotARead(f"refused before sending {cmd!r}: {why}")
    return fl.run(c, cmd)


def file_name(cmd):
    return cmd.replace(" ", "_").replace("-", "") + ".txt"


def note(text):
    print("      " + text)
    RESULTS.append("      " + text)


def check(what, ok, detail=""):
    line = ("PASS" if ok else "FAIL") + "  " + what + ((" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def first_line(text):
    return next((ln.strip() for ln in (text or "").splitlines() if ln.strip()), "(empty)")


def capture(tag, host, user, password, reads):
    fl.banner(f"{tag} {host}: show and help commands over SSH (read-only)")
    fl.OUT = os.path.join(OUT, tag)
    try:
        c = ssh(host, user, password)
    except Exception as exc:  # noqa: BLE001
        check(f"{tag} {host}: SSH login as {user}", False, f"{type(exc).__name__} {exc}")
        return None
    check(f"{tag} {host}: SSH login as {user}", True)
    raw, index = {}, []
    try:
        for cmd in reads:
            start = time.monotonic()
            try:
                raw[cmd] = send(c, cmd)
            except NotARead:
                raise
            except Exception as exc:  # noqa: BLE001 - recorded in the file and judged below
                raw[cmd] = f"ERROR {exc!r}"
            secs = time.monotonic() - start
            fl.save(file_name(cmd), f"# {cmd}\n{raw[cmd]}")
            lines = len(raw[cmd].splitlines())
            index.append(f"{cmd:<24} {lines:5d} lines {secs:7.1f} s")
            print(f"  {cmd:<24} {lines:5d} line(s) {secs:7.1f} s")
    finally:
        c.close()
        fl.save("_index.txt", "\n".join(index) + "\n")
    bad = [cmd for cmd in reads if REFUSAL.search(first_line(raw[cmd])) or raw[cmd].startswith("ERROR ")]
    check(f"{tag}: no command refused by the array", not bad, "; ".join(f"{cmd}: {first_line(raw[cmd])[:80]}" for cmd in bad))
    return raw


def port_rows(showport):
    """N:S:P -> the columns of plain showport (Mode, State, Node_WWN, Port_WWN, Type, Protocol, ...)."""
    return {p[0]: p for p in (ln.split() for ln in showport.splitlines()) if len(p) >= 7 and NSP.match(p[0])}


def identity(tag, raw, version_cmd):
    # showsys: ID (decimal on a 3PAR, 0x... on an Alletra MP), Name, Model (may hold spaces), then Serial
    # and six number columns.
    rows = [p for p in (ln.split() for ln in raw["showsys"].splitlines()) if len(p) >= 10 and SYS_ID.match(p[0])]
    if rows:
        r = rows[0]
        note(f"{tag}: showsys: name {r[1]}, model {' '.join(r[2:-7])}, serial {r[-7]}")
    else:
        note(f"{tag}: showsys: {first_line(raw['showsys'])[:120]}")
    text = raw[version_cmd]
    for label in ("Release version", "Patches") if "-b" in version_cmd else ("Release version",):
        line = next((ln.strip() for ln in text.splitlines() if ln.strip().startswith(label)), None)
        note(f"{tag}: {version_cmd}: {line or label + ' line not found'}")


def summarise(src_tag, src, dst_tag, dst):
    fl.banner("What the pair says")
    if src:
        identity(src_tag, src, "showversion -a -b")
        check(f"{src_tag}: help showrsv read", "showrsv" in src["help showrsv"].lower(), first_line(src["help showrsv"])[:80])
    if dst:
        identity(dst_tag, dst, "showversion")
        peers = {nsp: p for nsp, p in port_rows(dst["showport"]).items() if p[5].lower() == "peer" and p[6] == "FC"}
        for nsp, p in sorted(peers.items()):
            note(f"{dst_tag}: FC peer port {nsp}: mode {p[1]}, state {p[2]}, port WWN {p[4]}")
        check(f"{dst_tag}: FC peer ports (Type peer, Protocol FC) on two nodes",
              len({nsp.split(':')[0] for nsp, p in peers.items() if p[2] == 'ready'}) >= 2,
              ", ".join(f"{nsp} {p[2]}" for nsp, p in sorted(peers.items())) or "none")
    if src and dst:
        node_wwns = {p[3].upper() for p in port_rows(src["showport"]).values() if WWN.match(p[3])}
        seen = sorted({ln.split()[0] for ln in dst["showtarget"].splitlines()
                       if ln.split()[:1] and NSP.match(ln.split()[0]) and node_wwns & {w.upper() for w in ln.split()}})
        note(f"{src_tag}: node WWN(s) from showport: {', '.join(sorted(node_wwns)) or 'none'}")
        check(f"{dst_tag}: showtarget lists the source on its peer ports", bool(seen), ", ".join(seen) or "not listed")


def prepare():
    """Everything that can stop the script, before anything is written or sent: (tag, host, user, pw, reads)
    for the source, then the destination."""
    arrays = [
        ("source", os.environ.get("MIG_SOURCE_TAG") or "3par", "MIG_SOURCE", SOURCE_READS),
        ("destination", os.environ.get("MIG_DEST_TAG") or "e18u31", "MIG_DEST", DEST_READS),
    ]
    for _role, tag, _prefix, _reads in arrays:
        if not TAG.match(tag):
            sys.exit(f"A folder tag must be letters, digits, '.', '_' or '-'; got {tag!r}")
    if arrays[0][1] == arrays[1][1]:
        sys.exit("MIG_SOURCE_TAG and MIG_DEST_TAG name the same folder.")
    for cmd in SOURCE_READS + DEST_READS:
        if refusal(cmd):
            sys.exit(f"Not sending anything: {cmd!r} is refused ({refusal(cmd)}).")
    targets = []
    for role, tag, prefix, reads in arrays:
        host = setting(prefix + "_HOST", f"<the {role} array's management address>")
        user = setting(prefix + "_USER", f"<the {role} array's user>")
        targets.append((tag, host, user, fl.lab_secret(prefix + "_PW"), reads))
    if targets[0][1] == targets[1][1]:
        sys.exit("MIG_SOURCE_HOST and MIG_DEST_HOST are the same address; the source is the array the data moves from.")
    return targets


def main(targets):
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    raws = [capture(*t) for t in targets]
    summarise(targets[0][0], raws[0], targets[1][0], raws[1])


if __name__ == "__main__":
    TARGETS = prepare()
    try:
        main(TARGETS)
    except BaseException:
        fl.OUT = OUT
        if os.path.isdir(OUT):
            fl.save("script_stopped.txt", traceback.format_exc())
        raise
    finally:
        fl.OUT = OUT
        if os.path.isdir(OUT):
            fails = sum(1 for r in RESULTS if r.startswith("FAIL"))
            fl.save("report.txt", "\n".join([*RESULTS, "", f"{fails} FAIL"]))
            fl.banner(f"Done, {fails} FAIL. Send me {shutil.make_archive(OUT, 'zip', OUT)}")
