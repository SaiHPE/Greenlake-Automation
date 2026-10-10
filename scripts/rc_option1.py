"""BL-20 option 1: pause the six Sync groups on the lab pair so a periodic (async) group can be
STARTED on the same target, then put them back and prove nothing changed.

    python scripts\\rc_option1.py baseline [dir]   read-only capture of both arrays (required first)
    python scripts\\rc_option1.py prep     [dir]   create zz_rc_vol01 (1 GiB tpvv, SSD_r6) + set zz_rc_vvs on D22U27 if missing
    python scripts\\rc_option1.py stop     [dir]   stoprcopygroup -f on the six groups, each from its Primary side
    python scripts\\rc_option1.py start    [dir]   startrcopygroup on the six, then wait until every volume is Synced
    python scripts\\rc_option1.py compare  [dir]   capture again and diff against the baseline
    python scripts\\rc_option1.py unprep   [dir]   remove zz_rc_vvs and zz_rc_vol01 on D22U27

Default dir: ~\\Downloads\\rc_option1. The Primary side of each group is read from `showrcopy groups`
at run time (APP_Test swapped sides between 2026-10-07 and 10-09), never assumed. `stop` refuses to
run without a baseline, if any of the six is not Started, or if either array carries a group other
than the six (and the tool's zz_rc_*). stoprcopygroup in sync mode keeps resync snapshots (array's
own help), so `start` is a delta resync.
"""
import difflib
import getpass
import os
import re
import sys
import time

import paramiko

ACTION = sys.argv[1] if len(sys.argv) > 1 else ""
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.expanduser("~"), "Downloads", "rc_option1")
ARRAYS = {"D22U27": "10.64.122.99", "E18U31": "10.64.154.190"}
TARGET = "AlletraMP_E18U31"          # the one target, named the same on both arrays (fixtures README)
BASE_GROUPS = ["300gb", "APP_Test", "Intern_Automation", "Intern_Automation2", "Test-RCG", "Test-RCG2"]
CAPTURE = ["showrcopy", "showrcopy groups", "showrcopy -d groups", "showvvset", "showvlun", "showvv"]
DIFFED = ["showrcopy groups", "showrcopy -d groups", "showvvset", "showvlun"]
SYNC_WAIT_S, POLL_S = 45 * 60, 20
TEST_VV, TEST_SET, TEST_CPG = "zz_rc_vol01", "zz_rc_vvs", "SSD_r6"


def connect(host, pw):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username="3paradm", password=pw, timeout=20, allow_agent=False, look_for_keys=False)
    return c


def run(c, cmd):
    _i, o, e = c.exec_command(cmd, timeout=300)
    return (o.read() + e.read()).decode("utf-8", "replace")


def fname(cmd):
    return re.sub(r"[^A-Za-z0-9]+", "_", cmd).strip("_") + ".txt"


def save(stage, label, cmd, text):
    d = os.path.join(OUT, stage, label)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, fname(cmd)), "w", encoding="utf-8", newline="\n") as f:
        f.write("# " + cmd + "\n" + text)


def write(clients, label, cmd, stage):
    print("\n[%s] $ %s" % (label, cmd))
    text = run(clients[label], cmd)
    save(stage, label, cmd, text)
    print(text.rstrip() or "(no output)")
    return text


def capture(clients, stage):
    for label, c in clients.items():
        for cmd in CAPTURE:
            save(stage, label, cmd, run(c, cmd))
    print("captured %s -> %s" % (", ".join(CAPTURE), os.path.join(OUT, stage)))


def base(name):
    return re.sub(r"\.r\d+$", "", name)   # the peer names a group <name>.r<creator's system id>


def group_rows(text):
    """`showrcopy groups` -> {group: (status, role, mode)} for rows on TARGET."""
    rows = {}
    for line in text.splitlines():
        t = line.split()
        if len(t) >= 5 and t[1] == TARGET and not line.startswith(" "):
            rows[t[0]] = (t[2], t[3], t[4])
    return rows


def volume_sync(text):
    """`showrcopy -d groups` -> [(group, volume, SyncStatus)]."""
    out, group = [], None
    for line in text.splitlines():
        t = line.split()
        if not line.startswith(" ") and len(t) >= 6 and t[2] == TARGET:
            group = t[0]
        elif line.startswith("  ") and group and len(t) >= 5 and t[0] != "LocalVV":
            out.append((group, t[0], t[4]))
    return out


def locate(clients):
    """The Primary side of each of the six, read now: {base: (array, local name, status)}; plus any
    group on either array that is not one of the six and not the tool's."""
    found, strangers = {}, []
    for label, c in clients.items():
        for name, (status, role, _mode) in group_rows(run(c, "showrcopy groups")).items():
            if base(name) not in BASE_GROUPS and not name.startswith("zz_rc_"):
                strangers.append("%s: '%s' (%s, %s)" % (label, name, status, role))
            elif role == "Primary" and base(name) in BASE_GROUPS:
                found[base(name)] = (label, name, status)
    return found, strangers


def show_groups(clients):
    for label, c in clients.items():
        print("\n==== %s $ showrcopy groups" % label)
        print(run(c, "showrcopy groups").rstrip())


def main():
    if ACTION not in ("baseline", "prep", "stop", "start", "compare", "unprep"):
        sys.exit("first argument must be baseline, prep, stop, start, compare or unprep")
    pw0 = os.environ.get("ARRAY_PW") or getpass.getpass("3paradm password (both arrays): ")
    clients = {}
    for label, host in ARRAYS.items():
        pw = pw0
        for _attempt in (1, 2):
            try:
                clients[label] = connect(host, pw)
                break
            except paramiko.AuthenticationException:
                pw = getpass.getpass("Login failed on %s (%s) - its 3paradm password: " % (label, host))
        if label not in clients:
            sys.exit("could not log in to %s; nothing was done" % label)

    if ACTION == "baseline":
        capture(clients, "baseline")
        show_groups(clients)
        found, strangers = locate(clients)
        print("\nPrimary side of each group now: " + ", ".join("%s on %s" % (g, found[g][0]) for g in BASE_GROUPS if g in found))
        if strangers:
            print("Groups that are not the six: " + "; ".join(strangers))

    elif ACTION == "prep":
        a = clients["D22U27"]
        if TEST_VV not in run(a, "showvv -showcols Name " + TEST_VV).split():
            write(clients, "D22U27", "createvv -tpvv %s %s 1g" % (TEST_CPG, TEST_VV), "prep")
        else:
            print("%s already exists on D22U27" % TEST_VV)
        if TEST_SET not in run(a, "showvvset " + TEST_SET).split():
            write(clients, "D22U27", "createvvset %s %s" % (TEST_SET, TEST_VV), "prep")
        else:
            print("%s already exists on D22U27" % TEST_SET)
        print(run(a, "showvvset " + TEST_SET).rstrip())

    elif ACTION == "unprep":
        write(clients, "D22U27", "removevvset -f " + TEST_SET, "unprep")
        write(clients, "D22U27", "removevv -f " + TEST_VV, "unprep")

    elif ACTION == "stop":
        if not os.path.isdir(os.path.join(OUT, "baseline")):
            sys.exit("no baseline under %s - run `baseline` first" % OUT)
        found, strangers = locate(clients)
        problems = list(strangers)
        for g in BASE_GROUPS:
            if g not in found:
                problems.append("no Primary side found for '%s'" % g)
            elif found[g][2] != "Started":
                problems.append("'%s' on %s is %s, not Started" % (found[g][1], found[g][0], found[g][2]))
        if problems:
            print("\n".join(problems))
            sys.exit("\nNot as expected - nothing was stopped.")
        capture(clients, "before_stop")
        for g in BASE_GROUPS:
            label, name, _status = found[g]
            write(clients, label, "stoprcopygroup -f " + name, "stop")
        time.sleep(5)
        show_groups(clients)
        print("\nThe six groups are STOPPED. Run the tool's async test now, then `start` here.")

    elif ACTION == "start":
        found, _strangers = locate(clients)
        missing = [g for g in BASE_GROUPS if g not in found]
        if missing:
            sys.exit("no Primary side found for %s - look at `showrcopy groups` by hand; nothing was started" % ", ".join(missing))
        for g in BASE_GROUPS:
            label, name, _status = found[g]
            write(clients, label, "startrcopygroup " + name, "start")
        ours = {found[g][1] for g in BASE_GROUPS}
        deadline = time.time() + SYNC_WAIT_S
        while True:
            rows = []
            for c in clients.values():
                rows += volume_sync(run(c, "showrcopy -d groups"))
            mine = [r for r in rows if r[0] in ours]
            pending = [r for r in mine if r[2] != "Synced"]
            print("%s  %d of %d volume rows Synced%s" % (
                time.strftime("%H:%M:%S"), len(mine) - len(pending), len(mine),
                "" if not pending else "  (waiting: " + ", ".join("%s/%s %s" % r for r in pending[:6]) + ")"))
            if mine and not pending:
                break
            if time.time() > deadline:
                print("Still not all Synced after %d min - look at `showrcopy -d groups` by hand." % (SYNC_WAIT_S // 60))
                break
            time.sleep(POLL_S)
        show_groups(clients)
        capture(clients, "after_start")

    elif ACTION == "compare":
        capture(clients, "compare")
        same = True
        for label in ARRAYS:
            for cmd in DIFFED:
                paths = [os.path.join(OUT, s, label, fname(cmd)) for s in ("baseline", "compare")]
                if not os.path.exists(paths[0]):
                    print("no baseline for %s %s" % (label, cmd))
                    continue
                a, b = (open(p, encoding="utf-8").read().splitlines() for p in paths)
                diff = list(difflib.unified_diff(a, b, "baseline/" + label + " " + cmd, "now", lineterm="", n=1))
                if diff:
                    same = False
                    print("\n".join(diff))
        print("\nIDENTICAL to the baseline (%s)." % ", ".join(DIFFED) if same else "\nDIFFERS from the baseline - see above.")

    for c in clients.values():
        c.close()
    print("\nSaved under", OUT)


if __name__ == "__main__":
    main()
