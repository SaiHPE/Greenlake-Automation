"""RCIP replication between the Alletra MP and the Primera, set up by hand, with its undo (BL-41).

    python lab/rcip_setup_lab.py setup     # ports, ping, start Remote Copy, a target each way
    python lab/rcip_setup_lab.py undo      # reverses every change in the journal, newest first
    python lab/rcip_setup_lab.py undo-setup   # reverses only what setup made (keeps the hand-made entries)

CHANGES BOTH ARRAYS. Training arrays the lab gave for replication (2026-11-03):
    Alletra MP  rack13-ARCUS      10.132.30.121
    Primera     PRIMERA630R11U22  10.132.30.28
setup, in order, each change recorded in the journal before it is made and checked by reading back:
    1. Alletra RCIP address on 0:4:4 (10.93.18.11) and 1:4:4 (10.93.18.13), 255.255.254.0, MTU 1500;
       a ping from each to the Primera's RCIP ports (10.93.18.19 / .20), which the lab set up already
    2. startrcopy on the Alletra (Remote Copy was not configured there)
    3. target PRIMERA630R11U22 on the Alletra and target rack13-ARCUS on the Primera, two links each way
    4. waits for the links to come up
Not touched: the Alletra's iSCSI ports 0:4:1 / 1:4:1 (live hosts), the Primera's RCIP ports, and the
Primera's old FC target rack13-ARCUS_PRIMERA with its five stopped groups.
On any failure setup undoes what it did. undo leaves both arrays as `before/` shows them.
Password: RCIP_PAIR_PW (environment, or the app's .env). Evidence and the journal go in
RCIP_LAB_DIR (default ~/Downloads): rcip_setup_<mode>/ and rcip_setup_journal.json.
"""
import json
import os
import re
import shutil
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402

A_HOST, P_HOST = "10.132.30.121", "10.132.30.28"
A_NAME, P_NAME = "rack13-ARCUS", "PRIMERA630R11U22"
MASK = "255.255.254.0"
A_PORTS = {"0:4:4": "10.93.18.11", "1:4:4": "10.93.18.13"}      # Alletra RCIP port -> its address
P_PORTS = {"0:1:1": "10.93.18.19", "1:1:1": "10.93.18.20"}      # Primera RCIP port -> its address (set by the lab)
LINKS_A = ["0:4:4:10.93.18.19", "1:4:4:10.93.18.20"]            # Alletra port -> Primera address, node to node
LINKS_P = ["0:1:1:10.93.18.11", "1:1:1:10.93.18.13"]            # Primera port -> Alletra address
T_ON_A, T_ON_P = P_NAME, A_NAME                                  # target names: the other array's name
READS = ["showport -rcip", "showrctransport -rcip", "showrcopy", "showrcopy targets", "showrcopy links",
         "showrcopy groups", "showport"]
BASE = os.environ.get("RCIP_LAB_DIR") or os.path.join(os.path.expanduser("~"), "Downloads")
JOURNAL = os.path.join(BASE, "rcip_setup_journal.json")
RESULTS = []
LOG = []


class Stop(Exception):
    """A step's read-back did not show what the step was meant to do."""


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


class Array:
    def __init__(self, tag, host, password):
        self.tag, self.host = tag, host
        self.c = fl.ssh(host, password)

    def run(self, cmd):
        started = time.strftime("%H:%M:%S")
        out = fl.run(self.c, cmd)
        LOG.append("[%s] %s %s $ %s\n%s" % (started, self.tag, self.host, cmd, out.rstrip()))
        print("  %s $ %s\n      %s" % (self.tag, cmd, " | ".join(ln.strip() for ln in out.splitlines() if ln.strip())[:220]))
        return out

    def snapshot(self, folder):
        os.makedirs(os.path.join(fl.OUT, folder), exist_ok=True)
        for cmd in READS:
            fl.save(os.path.join(folder, "%s_%s.txt" % (self.tag, cmd.replace(" ", "_").replace("-", ""))),
                    "# %s\n%s" % (cmd, fl.run(self.c, cmd)))

    def close(self):
        self.c.close()


def load_journal():
    if os.path.isfile(JOURNAL):
        with open(JOURNAL, encoding="utf-8") as f:
            return json.load(f)
    return []


def record(journal, array, undo, what):
    """Write the undo BEFORE the change, so a crash mid-step still leaves it to run."""
    journal.append({"array": array.tag, "undo": undo, "what": what, "at": time.strftime("%Y-%m-%d %H:%M:%S")})
    with open(JOURNAL, "w", encoding="utf-8") as f:
        json.dump(journal, f, indent=1)


def rcip_rows(text):
    return {p[0]: p for p in (ln.split() for ln in text.splitlines()) if p and re.match(r"^\d+:\d+:\d+$", p[0])}


def received(ping_out):
    m = re.search(r"(\d+) received", ping_out)
    return int(m.group(1)) if m else 0


def setup(a, p, journal):
    fl.banner("1. Alletra RCIP ports")
    for nsp, ip in A_PORTS.items():
        record(journal, a, "controlport rcip delete -f %s" % nsp, "RCIP address %s on %s" % (ip, nsp))
        a.run("controlport rcip addr -f %s %s %s" % (ip, MASK, nsp))
        row = rcip_rows(a.run("showport -rcip")).get(nsp)
        if not (row and ip in row):
            # `rcip add` "configures the given network port for Remote Copy"; `addr` sets an existing interface.
            a.run("controlport rcip add -f %s %s %s" % (ip, MASK, nsp))
            row = rcip_rows(a.run("showport -rcip")).get(nsp)
        if not check("Alletra %s has RCIP address %s" % (nsp, ip), bool(row and ip in row), " ".join(row or ["not in showport -rcip"])):
            raise Stop("the RCIP address did not take on %s" % nsp)
    time.sleep(5)
    for (nsp, _ip), peer in zip(A_PORTS.items(), P_PORTS.values()):
        out = a.run("controlport rcip ping -c 3 %s %s" % (peer, nsp))
        if not check("ping from Alletra %s reaches the Primera RCIP port %s" % (nsp, peer), received(out) > 0,
                     (out.strip().splitlines() or [""])[-1][:120]):
            raise Stop("%s cannot reach %s: its cable is not on the 10.93.18.0/23 network" % (nsp, peer))

    fl.banner("2. Remote Copy on the Alletra")
    status = a.run("showrcopy")
    if "not configured" in status.lower():
        record(journal, a, "stoprcopy -f -stopgroups -clear", "startrcopy (Remote Copy was not configured)")
        a.run("startrcopy")
    elif "Started" not in status:
        record(journal, a, "stoprcopy -f", "startrcopy (Remote Copy was configured, stopped)")
        a.run("startrcopy")
    status = a.run("showrcopy")
    state = next((ln.strip() for ln in status.splitlines() if ln.startswith("Status")), status.strip()[:120])
    if not check("Remote Copy is started on the Alletra", "Started" in status, state):
        raise Stop("startrcopy did not start Remote Copy")

    fl.banner("3. A target on each array")
    for arr, name, links in ((a, T_ON_A, LINKS_A), (p, T_ON_P, LINKS_P)):
        record(journal, arr, "removercopytarget %s" % name, "target %s" % name)
        arr.run("creatercopytarget %s IP %s" % (name, " ".join(links)))
        targets = arr.run("showrcopy targets")
        if not check("%s has target %s" % (arr.tag, name), any(ln.split()[:1] == [name] for ln in targets.splitlines())):
            raise Stop("the %s refused target %s" % (arr.tag, name))

    fl.banner("4. Links")
    deadline = time.time() + 180
    while True:
        up = {}
        for arr, name in ((a, T_ON_A), (p, T_ON_P)):
            rows = [ln.split() for ln in arr.run("showrcopy links").splitlines() if ln.split()[:1] == [name]]
            up[arr.tag] = (sum(1 for r in rows if "Up" in r), len(rows))
        if all(n == total and total for n, total in up.values()) or time.time() > deadline:
            break
        time.sleep(15)
    for tag, (n, total) in up.items():
        check("%s: links Up %d of %d" % (tag, n, total), n == total and total > 0)
    for arr in (a, p):
        arr.run("showrcopy targets")
        arr.run("showrctransport -rcip")


# Entries recorded by hand after `setup` (2026-11-03): the Primera's gateway and its old FC target.
# `undo-setup` leaves them in the journal, so the arrays go back to "partnership not set up" and the
# tool can set it up again; `undo` reverses those too.
NOT_SETUP = ("controlport rcip gw", "creatercopytarget rack13-ARCUS_PRIMERA")


def undo(a, p, journal, *, setup_only=False):
    fl.banner("Undo, newest change first" + (" (only what setup made)" if setup_only else ""))
    arrays = {"alletra": a, "primera": p}
    keep = [e for e in journal if setup_only and e["undo"].startswith(NOT_SETUP)]
    for entry in reversed(journal):
        if entry in keep:
            continue
        arrays[entry["array"]].run(entry["undo"])
    with open(JOURNAL, "w", encoding="utf-8") as f:
        json.dump(keep, f, indent=1)
    rc = a.run("showrcopy")
    check("Alletra: Remote Copy is back to not configured", "not configured" in rc.lower(), rc.strip()[:120])
    left = rcip_rows(a.run("showport -rcip"))
    check("Alletra: no RCIP address on 0:4:4 / 1:4:4", not (set(A_PORTS) & set(left)), " ".join(sorted(left)))
    targets = p.run("showrcopy targets")
    check("Primera: target %s is gone" % T_ON_P, not any(ln.split()[:1] == [T_ON_P] for ln in targets.splitlines()))
    if not setup_only:
        check("Primera: the old FC target is back", "rack13-ARCUS_PRIMERA" in targets)
    check("Primera: RCIP addresses unchanged", all(ip in p.run("showport -rcip") for ip in P_PORTS.values()))


def main(mode):
    out = os.path.join(BASE, "rcip_setup_%s" % mode)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    fl.OUT = out
    password = fl.lab_secret("RCIP_PAIR_PW")
    a, p = Array("alletra", A_HOST, password), Array("primera", P_HOST, password)
    journal = load_journal()
    try:
        a.snapshot("before")
        p.snapshot("before")
        if mode in ("undo", "undo-setup"):
            if not journal:
                check("journal has changes to undo", False, JOURNAL + " is empty or missing")
                return
            undo(a, p, journal, setup_only=mode == "undo-setup")
        else:
            if journal:
                sys.exit("The journal already holds %d change(s): run `undo` first (%s)." % (len(journal), JOURNAL))
            try:
                setup(a, p, journal)
            except Exception as exc:  # noqa: BLE001 - every failure puts the arrays back
                check("setup stopped: %s" % exc, False)
                fl.save("error.txt", traceback.format_exc())
                undo(a, p, journal)
        a.snapshot("after")
        p.snapshot("after")
    finally:
        fl.save("commands.log", "\n\n".join(LOG))
        a.close()
        p.close()


if __name__ == "__main__":
    mode = (sys.argv[1:] or [""])[0]
    if mode not in ("setup", "undo", "undo-setup"):
        sys.exit(__doc__)
    try:
        main(mode)
    finally:
        if fl.OUT and os.path.isdir(fl.OUT):
            fails = sum(1 for r in RESULTS if r.startswith("FAIL"))
            fl.save("report.txt", "\n".join(RESULTS + ["", "%d PASS, %d FAIL" % (len(RESULTS) - fails, fails)]))
            fl.banner("%s: %d PASS, %d FAIL. Evidence in %s" % (mode, len(RESULTS) - fails, fails, fl.OUT))
