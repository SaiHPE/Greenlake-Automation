"""SPEC-017 in async (periodic) mode, in one go. The target carries the six lab Sync groups and the
array allows one mode per target, so (operator's decision 2026-10-11, as on 10-10) they are saved,
removed for the test, and rebuilt afterwards.

    python lab\\rc_async_failover_lab.py

1. starts the app on the latest code
2. removes the tool's zz_rc_* objects left by the last sync run (the app's own removal set)
3. saves the six groups' definitions, removes the six (volumes kept)
4. creates the source volume set and the async sheet
5. waits while the operator runs Replication, Failover test and As-built in the browser
6. collects the results; if the test left the group reversed, puts it back
7. removes the async run's objects, rebuilds the six, waits until they are Synced, compares

Asks for the 3paradm password once and for GO once. Writes to ~\\Downloads\\rc_async_failover and
zips it (the rc_rebuild record goes in the zip too).
"""
import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback

import rc_failover_lab as fl

HOME = os.path.join(os.path.expanduser("~"), "Downloads")
OUT = os.path.join(HOME, "rc_async_failover")
REBUILD_DIR = os.path.join(HOME, "rc_async_failover_rebuild")
OPTION1_DIR = os.path.join(HOME, "rc_async_failover_option1")
SHEET = os.path.join(HOME, "D22U27_replication_async.xlsx")
BASE_GROUPS = ["300gb", "APP_Test", "Intern_Automation", "Intern_Automation2", "Test-RCG", "Test-RCG2"]
SYNC_WAIT_S, POLL_S = 60 * 60, 30
fl.OUT = OUT


def child(script, *args):
    print("\n$ python %s %s" % (script, " ".join(args)))
    return subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), script), *args],
                          cwd=fl.ROOT, env=os.environ.copy(), check=False).returncode


def groups_on(c):
    """{group name: [SyncStatus of each volume]} from `showrcopy -d groups`."""
    out, cur = {}, None
    for line in fl.run(c, "showrcopy -d groups").splitlines():
        t = line.split()
        if not t or t[0] in ("Name", "LocalVV"):
            continue
        if not line.startswith(" ") and len(t) >= 6 and t[1].isdigit():
            cur = t[0]
            out[cur] = []
        elif line.startswith("  ") and cur is not None and len(t) >= 5:
            out[cur].append(t[4])
    return out


def base(name):
    return re.sub(r"\.r\d+$", "", name)


def tool_groups(p, s):
    return ["D22U27: " + g for g in groups_on(p) if g.startswith("zz_rc_")] + \
           ["E18U31: " + g for g in groups_on(s) if g.startswith("zz_rc_")]


def snapshot(p, s, stage):
    for label, c in (("D22U27", p), ("E18U31", s)):
        fl.save("%s_%s_showrcopy_d_groups.txt" % (stage, label), fl.run(c, "showrcopy -d groups"))


def remove_tool_objects(p, s, stage):
    fl.banner("Removing the tool's zz_rc_* objects (%s)" % stage)
    if fl.role_status(p, fl.GROUP)[0] and fl.role_status(s, fl.PEER_GROUP)[0]:
        fl.restore_if_needed(p, s)
    if tool_groups(p, s):
        child("rc_rebuild.py", "ui-cleanup", REBUILD_DIR)
    left = tool_groups(p, s)
    if left:
        sys.exit("These zz_rc_* groups are still on the arrays: %s\nStopping before anything else. "
                 "Send me Downloads\\rc_async_failover.zip." % ", ".join(left))
    print("No zz_rc_* group on either array.")


def wait_six_synced(p, s):
    fl.banner("Waiting until every volume of the six groups is Synced (up to %d min)" % (SYNC_WAIT_S // 60))
    deadline = time.time() + SYNC_WAIT_S
    while True:
        rows = [(g, st) for c in (p, s) for g, sts in groups_on(c).items() if base(g) in BASE_GROUPS for st in sts]
        pending = [r for r in rows if r[1] != "Synced"]
        print("  %s  %d of %d volume rows Synced" % (time.strftime("%H:%M:%S"), len(rows) - len(pending), len(rows)))
        if rows and not pending:
            return True
        if time.time() > deadline:
            print("Not all Synced after %d min." % (SYNC_WAIT_S // 60))
            return False
        time.sleep(POLL_S)


def run_ids():
    return {r["run_id"] for r in json.loads(fl.get("/runs"))["runs"]}


def collect(p, s, known):
    """Events and as-built of the run(s) started in the browser part (never an older run's test)."""
    fl.banner("Collecting the results")
    outcome = None
    for run_id in sorted(run_ids() - known):
        events = json.loads(fl.get("/runs/%s/events" % run_id))["events"]
        fl.save("events_%s.json" % run_id, json.dumps(events, indent=2))
        tests = [e for e in events if e["event_type"] in ("failover.completed", "failover.failed")]
        if tests:
            outcome = tests[-1]["event_type"]
            print("Failover test: " + tests[-1]["message"])
        try:
            with open(os.path.join(OUT, "asbuilt_%s.docx" % run_id), "wb") as f:
                f.write(fl.get("/runs/%s/asbuilt/download" % run_id))
            print("As-built saved.")
        except Exception as exc:  # noqa: BLE001
            print("No as-built for run %s (%s)." % (run_id, exc))
    if outcome is None:
        print("No failover test found in a new run.")
    for label, c, name in (("D22U27", p, fl.GROUP), ("E18U31", s, fl.PEER_GROUP)):
        fl.save("after_test_%s_showrcopy_d_groups.txt" % label, fl.run(c, "showrcopy -d groups " + name))
    return outcome


def main():
    for d in (OUT, REBUILD_DIR, OPTION1_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
    if os.path.exists(OUT + ".zip"):
        os.remove(OUT + ".zip")
    os.makedirs(OUT)
    fl.banner("This run REMOVES the six lab replication groups (300gb, APP_Test, Intern_Automation,\n"
              "Intern_Automation2, Test-RCG, Test-RCG2) for the async test, then rebuilds them.\n"
              "Their volumes stay on both arrays. The rebuild is a full first copy, so it can take a while.")
    if input("Type GO to start: ").strip() != "GO":
        sys.exit("Not started. Nothing was changed.")
    pw = os.environ.get("ARRAY_PW") or getpass.getpass("3paradm password (both arrays): ")
    os.environ["ARRAY_PW"], os.environ["RC_YES"] = pw, "1"
    p, s = fl.ssh(fl.P_HOST, pw), fl.ssh(fl.S_HOST, pw)
    snapshot(p, s, "start")

    fl.restart_app()
    remove_tool_objects(p, s, "left by the last sync run")

    fl.banner("Saving and removing the six groups")
    child("rc_rebuild.py", "save", REBUILD_DIR)
    if not os.path.exists(os.path.join(REBUILD_DIR, "groups.json")):
        sys.exit("The save did not complete. Nothing was removed.")
    child("rc_rebuild.py", "remove", REBUILD_DIR)
    still = sorted({base(g) for c in (p, s) for g in groups_on(c) if base(g) in BASE_GROUPS})
    if still:
        print("Still on the arrays: " + ", ".join(still) + ". Not running the test; rebuilding what was removed.")
    else:
        fl.banner("Preparing the source volume set and the async sheet")
        child("rc_option1.py", "prep", OPTION1_DIR)
        child("rc_sheet.py", "async", SHEET)
        known = run_ids()
        fl.banner("Your part, in the browser (http://127.0.0.1:8765)\n"
                  "   a) Start a NEW run. Upload Downloads\\D22U27_replication_async.xlsx.\n"
                  "   b) Mode: Custom. Tick Replication, Failover test and As-built.\n"
                  "   c) Replication: Preview, then Apply. Wait until it shows the groups.\n"
                  "   d) Failover test: tick the box, click Run. Wait for Passed or Failed.\n"
                  "      If it says not every volume is Synced and nothing was done, wait 2 minutes and Run again.\n"
                  "   e) As-built: Generate.\n"
                  "   Then come back here and press Enter.")
        input("Press Enter when the browser part is done... ")
        p.close(), s.close()
        p, s = fl.ssh(fl.P_HOST, pw), fl.ssh(fl.S_HOST, pw)
        outcome = collect(p, s, known)
        fl.save("outcome.txt", str(outcome))
        if outcome == "failover.failed":
            fl.diagnose(p, s)

    snapshot(p, s, "before_cleanup")
    remove_tool_objects(p, s, "the async run's")
    child("rc_option1.py", "unprep", OPTION1_DIR)
    fl.banner("Rebuilding the six groups")
    child("rc_rebuild.py", "rebuild", REBUILD_DIR)
    p.close(), s.close()
    p, s = fl.ssh(fl.P_HOST, pw), fl.ssh(fl.S_HOST, pw)
    wait_six_synced(p, s)
    child("rc_rebuild.py", "compare", REBUILD_DIR)
    snapshot(p, s, "end")
    p.close(), s.close()


def pack():
    if os.path.isdir(REBUILD_DIR):
        shutil.copytree(REBUILD_DIR, os.path.join(OUT, "rc_rebuild"), dirs_exist_ok=True)
    if os.path.isdir(OPTION1_DIR):
        shutil.copytree(OPTION1_DIR, os.path.join(OUT, "rc_option1"), dirs_exist_ok=True)
    return shutil.make_archive(OUT, "zip", OUT)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        if os.path.isdir(OUT):
            fl.save("script_stopped.txt", traceback.format_exc())
        raise
    finally:
        if os.path.isdir(OUT):
            fl.banner("Done. Send me " + pack())
