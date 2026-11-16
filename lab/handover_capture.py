"""What a lab array says about its alerts, capacity and recent performance, before the tool reads them
for the as-built (BL-24, SPEC-026 R2). READ-ONLY, no prompts.

    .\\.venv\\Scripts\\python.exe lab\\handover_capture.py
    $env:CAPTURE_ARRAYS = "D22U27=10.64.122.99,E18U31=10.64.154.190"    # optional (PowerShell)

Changes nothing on any array. For each array in CAPTURE_ARRAYS (TAG=address, comma separated; default
D22U27=10.64.122.99) it logs in over SSH as 3paradm with LAB_ARRAY_PW from .env (CAPTURE_PW_NAME names
another .env key, e.g. RCIP_PAIR_PW for the Alletra MP + Primera pair). Only show, srstat, checkhealth
and help commands are sent: send() refuses anything else before it reaches the array, and every
command in READS is checked that way before the first login. No WSAPI, no host, no switch.
1. context: showversion, showsys, showdate
2. the CLI's own help for showalert, showsys and the four System Reporter reports
3. alerts and capacity: showalert, showalert -d, showsys -space, checkhealth -svc -detail
4. System Reporter: each report in its plain form (the array's defaults: 5-minute samples, the last
   12 hours) and in the SPEC-026 R3 form exactly as the tool will send it (24 hours, avg / 95% / max)
5. says, per array: OS, alerts by state and severity, whether System Reporter answered

Output in RCIP_LAB_DIR (default ~/Downloads): handover_capture/<TAG>/ with one file per command (first
line `# <command>`, names in READS) and _index.txt (lines and seconds per command); report.txt with the
PASS/FAIL lines; all of it zipped to handover_capture.zip. The files are named as the tests expect them
in tests/fixtures/handover/<TAG>/ (SPEC-026 R2, work packet BL-24 step 1): copy each <TAG>/ folder
there. Scrub user names before committing (alert messages and checkhealth can name the users who
logged in or changed something); no password is ever written to a file.
"""
import os
import re
import shutil
import sys
import time
import traceback
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # after the sys.path line, like the other lab scripts

ARRAYS_SPEC = os.environ.get("CAPTURE_ARRAYS") or "D22U27=10.64.122.99"
PW_NAME = os.environ.get("CAPTURE_PW_NAME") or "LAB_ARRAY_PW"
BASE = os.environ.get("RCIP_LAB_DIR") or os.path.join(os.path.expanduser("~"), "Downloads")
OUT = os.path.join(BASE, "handover_capture")
fl.OUT = OUT

# SPEC-026 R3, exactly as the tool will send them. The plain forms below are the fallback if the
# array refuses an option here; the captured help decides which one the spec keeps.
SR_CPU = "srstatcpu -hires -btsecs -24h -groupby NODE -summary avg,95%,max,per_group"
SR_PORT = ("srstatport -hires -btsecs -24h -port_type host -groupby PORT_N,PORT_S,PORT_P "
           "-summary avg,95%,max,per_group")
SR_VV = "srstatvv -hires -btsecs -24h -summary avg,95%,max"
SR_RCVV = "srstatrcvv -hires -btsecs -24h -groupby GROUP_NAME -summary avg,max,per_group"

# command -> fixture file name, in the order they are sent
READS = {
    "showversion": "showversion.txt",
    "showsys": "showsys.txt",
    "showdate": "showdate.txt",
    "help showalert": "help_showalert.txt",
    "help showsys": "help_showsys.txt",
    "help srstatcpu": "help_srstatcpu.txt",
    "help srstatport": "help_srstatport.txt",
    "help srstatvv": "help_srstatvv.txt",
    "help srstatrcvv": "help_srstatrcvv.txt",
    "showalert": "showalert.txt",
    "showalert -d": "showalert_d.txt",
    "showsys -space": "showsys_space.txt",
    "checkhealth -svc -detail": "checkhealth_svc_detail.txt",
    "srstatcpu": "srstatcpu.txt",
    SR_CPU: "srstatcpu_24h.txt",
    "srstatport": "srstatport.txt",
    SR_PORT: "srstatport_24h.txt",
    "srstatvv": "srstatvv.txt",
    SR_VV: "srstatvv_24h.txt",
    "srstatrcvv": "srstatrcvv.txt",
    SR_RCVV: "srstatrcvv_24h.txt",
}

# The only first words that may be sent: show* and srstat* (reads and System Reporter reports),
# checkhealth (inspects and reports) and help. Other check* commands stay out on purpose: some of
# them can repair what they find.
READ_PREFIXES = ("show", "srstat")
READ_WORDS = ("checkhealth", "help")
FORBIDDEN_CHARS = set(";|&`$<>[]{}\\\"'\n\r")
TAG = re.compile(r"^[A-Za-z0-9_.-]+$")
REFUSAL = re.compile(r"^(error\b|invalid\b|unknown\b|usage\b)|command not found|not (running|licensed|supported)",
                     re.IGNORECASE)
RESULTS = []


class NotARead(Exception):
    """A command that is not on this script's read list. Raised before anything is sent."""


def refusal(cmd):
    """Why send() would refuse `cmd`, or None when it is a read."""
    if FORBIDDEN_CHARS & set(cmd):
        return "it contains a shell or Tcl metacharacter"
    first = (cmd.split() or [""])[0]
    if first in READ_WORDS or first.startswith(READ_PREFIXES):
        return None
    return f"'{first}' is not a show, srstat, checkhealth or help command"


def send(c, cmd):
    """Run one read command on the open SSH session `c`."""
    why = refusal(cmd)
    if why:
        raise NotARead(f"refused before sending {cmd!r}: {why}")
    return fl.run(c, cmd)


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


def refused(text):
    """The array's own words for a refusal on the first line (LESSONS 39), or an exception we recorded."""
    return bool(REFUSAL.search(first_line(text)))


def parse_arrays(spec):
    arrays = []
    for item in spec.split(","):
        tag, sep, addr = (part.strip() for part in item.partition("="))
        if not sep or not TAG.match(tag) or not addr or tag in dict(arrays):
            sys.exit(f"CAPTURE_ARRAYS must look like D22U27=10.64.122.99[,TAG=address], each TAG once; got {spec!r}")
        arrays.append((tag, addr))
    return arrays


def alert_summary(text):
    if refused(text):
        return "refused: " + first_line(text)[:120]
    ids = re.findall(r"^\s*Id\s*:", text, re.MULTILINE)
    if not ids:
        return "no alert records; the array says: " + first_line(text)[:120]
    states = Counter(re.findall(r"^\s*State\s*:\s*(.*?)\s*$", text, re.MULTILINE))
    severities = Counter(re.findall(r"^\s*Severity\s*:\s*(.*?)\s*$", text, re.MULTILINE))
    times = sorted(re.findall(r"^\s*Time\s*:\s*(.*?)\s*$", text, re.MULTILINE))
    by_state = ", ".join(f"{k} {n}" for k, n in states.most_common()) or "?"
    by_severity = ", ".join(f"{k} {n}" for k, n in severities.most_common()) or "?"
    span = f"{times[0]} to {times[-1]}" if times else "?"
    return f"{len(ids)} alert(s); state {by_state}; severity {by_severity}; times {span}"


def sr_state(text):
    if refused(text):
        return "refused: " + first_line(text)[:120]
    rows = [ln for ln in text.splitlines() if ln.strip()]
    if len(rows) < 3:
        return "no rows: " + first_line(text)[:120]
    return f"answered, {len(rows)} line(s)"


def capture(tag, host, password):
    fl.banner(f"{tag} {host}: alerts, capacity, System Reporter (read-only)")
    fl.OUT = os.path.join(OUT, tag)
    try:
        c = fl.ssh(host, password)
    except Exception as exc:  # noqa: BLE001
        check(f"{tag} {host}: SSH login", False, f"{type(exc).__name__} {exc}")
        return None
    check(f"{tag} {host}: SSH login", True)
    raw, index = {}, []
    try:
        for cmd, name in READS.items():
            start = time.monotonic()
            try:
                raw[cmd] = send(c, cmd)
            except NotARead:
                raise
            except Exception as exc:  # noqa: BLE001 - recorded in the file and judged below
                raw[cmd] = f"ERROR {exc!r}"
            secs = time.monotonic() - start
            fl.save(name, f"# {cmd}\n{raw[cmd]}")
            lines = len(raw[cmd].splitlines())
            index.append(f"{cmd:<105} {lines:5d} lines {secs:7.1f} s")
            print(f"  {cmd[:62]:<62} {lines:5d} line(s) {secs:7.1f} s")
    finally:
        c.close()
        fl.save("_index.txt", "\n".join(index) + "\n")
    return raw


def summarise(tag, host, raw):
    fl.banner(f"{tag} {host}: what it says")
    name = next((ln.split()[1] for ln in raw["showsys"].splitlines()
                 if len(ln.split()) > 1 and ln.split()[0].startswith("0x")), "?")
    version = next((ln.strip() for ln in raw["showversion"].splitlines() if ln.startswith("Release version")),
                   first_line(raw["showversion"]))
    note(f"{tag}: {name}, {version}")
    note(f"{tag}: array clock: {first_line(raw['showdate'])[:120]}")
    for cmd in ("showalert", "showalert -d"):
        note(f"{tag}: {cmd:<13} {alert_summary(raw[cmd])}")
    reports = [cmd for cmd in READS if cmd.startswith("srstat")]
    states = {cmd: sr_state(raw[cmd]) for cmd in reports}
    for cmd in reports:
        label = cmd.split()[0] + (" (24-hour form)" if " " in cmd else " (plain)")
        note(f"{tag}: {label:<28} {states[cmd]}")
    answered = [cmd for cmd in reports if states[cmd].startswith("answered")]
    check(f"{tag}: System Reporter answered every report", len(answered) == len(reports),
          f"{len(answered)} of {len(reports)}")
    bad = [cmd for cmd in READS if refused(raw[cmd])]
    check(f"{tag}: no command refused by the array", not bad, "; ".join(bad))
    no_help = [cmd for cmd in READS if cmd.startswith("help ") and cmd.split()[1] not in raw[cmd]]
    check(f"{tag}: CLI help read for every report", not no_help, "; ".join(no_help))


def main(arrays, password):
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for tag, host in arrays:
        raw = capture(tag, host, password)
        if raw:
            summarise(tag, host, raw)


if __name__ == "__main__":
    ARRAYS = parse_arrays(ARRAYS_SPEC)
    for read in READS:
        if refusal(read):
            sys.exit(f"Not sending anything: {read!r} is refused ({refusal(read)}).")
    PASSWORD = fl.lab_secret(PW_NAME)
    try:
        main(ARRAYS, PASSWORD)
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
