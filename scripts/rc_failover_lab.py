"""SPEC-017 lab run in one go: put the test group back to normal if a previous test left it reversed,
restart the app on the latest code, wait while the operator runs the Failover test and the As-built
in the browser, then collect everything and clean up.

    python scripts\\rc_failover_lab.py

Asks for the 3paradm password once. Writes everything to ~\\Downloads\\rc_failover and zips it.
"""
import getpass
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

import paramiko

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.expanduser("~"), "Downloads", "rc_failover")
P_HOST, S_HOST = "10.64.122.99", "10.64.154.190"
GROUP, PEER_GROUP = "zz_rc_test_rcg", "zz_rc_test_rcg.r188150"
APP = "http://127.0.0.1:8765"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")


def ssh(host, pw):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username="3paradm", password=pw, timeout=20, allow_agent=False, look_for_keys=False)
    return c


def run(c, cmd):
    _i, o, e = c.exec_command(cmd, timeout=300)
    return (o.read() + e.read()).decode("utf-8", "replace")


def role_status(c, name):
    """(role, status) of one group from `showrcopy groups <name>`, or (None, None) if absent."""
    for line in run(c, "showrcopy groups " + name).splitlines():
        t = line.split()
        if len(t) >= 5 and t[0] == name:
            return t[3], t[2]
    return None, None


def save(name, text):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def get(path):
    with OPENER.open(APP + path, timeout=30) as r:
        return r.read()


def banner(text):
    print("\n" + "=" * 70 + "\n" + text + "\n" + "=" * 70)


def wait_state(p, s, want_p, want_s, status=None, tries=60):
    for _ in range(tries):
        time.sleep(5)
        pr, ps = role_status(p, GROUP)
        sr, ss = role_status(s, PEER_GROUP)
        print("  D22U27 %s/%s   E18U31 %s/%s" % (pr, ps, sr, ss))
        if pr == want_p and sr == want_s and (status is None or (ps == status and ss == status)):
            return True
    return False


def diagnose(p, s):
    """Record how the group got here: both sides in detail, the last 3 hours of array events that name
    it, and the answer of any restore run earlier with rc_rebuild.py cli."""
    for label, c, name in (("D22U27", p, GROUP), ("E18U31", s, PEER_GROUP)):
        save("before_%s_showrcopy_d_groups.txt" % label, run(c, "showrcopy -d groups " + name))
        events = run(c, "showeventlog -min 180")
        save("before_%s_eventlog_all.txt" % label, events)
        save("before_%s_eventlog_group.txt" % label,
             "\n".join(line for line in events.splitlines() if "zz_rc_test" in line or "rcopy" in line.lower()))
    earlier = os.path.join(os.path.expanduser("~"), "Downloads", "rc_rebuild", "cli", "E18U31")
    if os.path.isdir(earlier):
        for name in os.listdir(earlier):
            if "restore" in name:
                shutil.copy(os.path.join(earlier, name), os.path.join(OUT, "earlier_" + name))


def restore_if_needed(p, s):
    banner("1. Test group state")
    pr, ps = role_status(p, GROUP)
    sr, ss = role_status(s, PEER_GROUP)
    print("D22U27 %s: %s/%s   E18U31 %s: %s/%s" % (GROUP, pr, ps, PEER_GROUP, sr, ss))
    if pr is None or sr is None:
        sys.exit("The test group is missing on one array. Stopping; send me this output.")
    if pr == "Primary" and sr == "Secondary" and ps == "Started" and ss == "Started":
        print("Normal. Nothing to restore.")
        return
    diagnose(p, s)
    if sr == "Primary-Rev":
        print("Reversed by the last test. Running on E18U31: setrcopygroup restore -f " + PEER_GROUP)
        answer = run(s, "setrcopygroup restore -f " + PEER_GROUP).strip()
        print(answer or "(no output)")
        save("restore_answer.txt", answer)
        if wait_state(p, s, "Primary", "Secondary", "Started"):
            print("Back to normal.")
            return
        sys.exit("Not back to normal after 5 minutes. Stopping; send me Downloads\\rc_failover.zip")
    if pr == "Secondary" and sr == "Primary":
        # The natural direction itself is reversed (E18U31 -> D22U27). The array's own way to swap a
        # consistent pair back: stop, `reverse` (changes natural and current direction on both), start.
        print("The group replicates the wrong way round (E18U31 is its primary). Swapping it back:")
        steps = [(s, "E18U31", "stoprcopygroup -f " + PEER_GROUP), (s, "E18U31", "setrcopygroup reverse -f " + PEER_GROUP)]
        for c, label, cmd in steps:
            answer = run(c, cmd).strip()
            print("  [%s] $ %s\n    %s" % (label, cmd, answer or "(no output)"))
            save("swap_%s.txt" % cmd.split()[0], "# " + cmd + "\n" + answer)
            if "error" in answer.lower():
                sys.exit("The array refused that. Stopping; send me Downloads\\rc_failover.zip")
        if not wait_state(p, s, "Primary", "Secondary", tries=24):
            sys.exit("The roles did not swap within 2 minutes. Stopping; send me Downloads\\rc_failover.zip")
        answer = run(p, "startrcopygroup " + GROUP).strip()
        print("  [D22U27] $ startrcopygroup %s\n    %s" % (GROUP, answer or "(no output)"))
        save("swap_startrcopygroup.txt", answer)
        if wait_state(p, s, "Primary", "Secondary", "Started"):
            print("Back to normal.")
            return
        sys.exit("Not Started on both sides after 5 minutes. Stopping; send me Downloads\\rc_failover.zip")
    sys.exit("Not a state this script knows how to fix. Stopping; send me Downloads\\rc_failover.zip")


def restart_app():
    banner("2. Restarting the app on the latest code")
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue | "
                    "ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"], check=False)
    time.sleep(2)
    flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    subprocess.Popen(["powershell", "-NoExit", "-Command", "cd '%s'; .\\.venv\\Scripts\\onboard.exe ui" % ROOT],
                     creationflags=flags, cwd=ROOT)
    for _ in range(60):
        time.sleep(2)
        try:
            get("/app/profile")
            print("App is up on " + APP)
            return
        except Exception:  # noqa: BLE001
            pass
    sys.exit("The app did not start within 2 minutes. Look at its window, then send me what it says.")


def latest_failover_run():
    best = None
    for r in json.loads(get("/runs"))["runs"]:
        events = json.loads(get("/runs/%s/events" % r["run_id"]))["events"]
        for e in events:
            if e["event_type"] in ("failover.completed", "failover.failed"):
                if best is None or e["created_at"] > best[1]:
                    best = (r["run_id"], e["created_at"], events)
    return best


def collect(p, s):
    banner("4. Collecting the results")
    found = latest_failover_run()
    if found is None:
        print("No failover test found in the app's runs.")
        return None
    run_id, _when, events = found
    save("events.json", json.dumps(events, indent=2))
    last = [e for e in events if e["event_type"] in ("failover.completed", "failover.failed")][-1]
    print("Failover test: " + last["message"])
    try:
        with open(os.path.join(OUT, "asbuilt.docx"), "wb") as f:
            f.write(get("/runs/%s/asbuilt/download" % run_id))
        print("As-built saved.")
    except Exception as exc:  # noqa: BLE001
        print("No as-built to download (%s). Generate it in the browser if you want it in the zip." % exc)
    for label, c, name in (("D22U27", p, GROUP), ("E18U31", s, PEER_GROUP)):
        save("%s_showrcopy_d_groups.txt" % label, run(c, "showrcopy -d groups " + name))
    return last["event_type"]


def child(script, *args):
    print("\n$ python %s %s" % (script, " ".join(args)))
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", script), *args], cwd=ROOT, env=os.environ.copy(), check=False)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    if os.path.exists(OUT + ".zip"):
        os.remove(OUT + ".zip")
    os.makedirs(OUT)
    pw = os.environ.get("ARRAY_PW") or getpass.getpass("3paradm password (both arrays): ")
    os.environ["ARRAY_PW"] = pw
    p, s = ssh(P_HOST, pw), ssh(S_HOST, pw)

    restore_if_needed(p, s)
    restart_app()

    banner("3. Your part, in the browser\n"
           "   a) Press Ctrl+Shift+R. The same run opens; go to the Failover test step.\n"
           "   b) Tick the box and click 'Run the failover test again'. Wait until it says Passed or Failed.\n"
           "   c) If it passed: go to As-built and click Generate.\n"
           "   Then come back here and press Enter.")
    input("Press Enter when the browser part is done... ")

    p.close(), s.close()
    p, s = ssh(P_HOST, pw), ssh(S_HOST, pw)
    outcome = collect(p, s)
    if outcome == "failover.failed":
        banner("The failover test did not pass. Nothing was cleaned up, so the state stays as the test left it.\n"
               "Send me Downloads\\rc_failover.zip.")
    else:
        banner("5. Cleaning up the test objects")
        child("rc_rebuild.py", "ui-cleanup")
        child("rc_option1.py", "unprep")
    p.close(), s.close()
    zip_path = shutil.make_archive(OUT, "zip", OUT)
    banner("Done. Send me " + zip_path)


if __name__ == "__main__":
    try:
        main()
    finally:
        if os.path.isdir(OUT) and not os.path.exists(OUT + ".zip"):
            print("Saved: " + shutil.make_archive(OUT, "zip", OUT))
