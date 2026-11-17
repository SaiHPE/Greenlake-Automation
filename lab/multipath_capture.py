"""The real `multipath -ll` of a lab Linux host, to replace the documented samples (BL-36). READ-ONLY.

    .\\.venv\\Scripts\\python.exe lab\\multipath_capture.py

Changes nothing, on the host or on any array. Logs in to the lab Linux host over SSH with the app's own
read-only client (LINUX_HOST, default 10.54.159.49; LINUX_USER, default root; the password from .env,
LAB_DEFAULT_PW, or the .env name given in LINUX_PW_NAME) and runs only these fixed commands:
`multipath -ll`, `sudo -n multipath -ll`, `cat /sys/module/dm_multipath/initstate`, `hostname`.
1. saves what each printed, with its exit code
2. saves the app's own summary sentence for that output
For a useful capture the host needs multipath set up and an Alletra volume presented on two fabrics.
Scrub the files (no customer names or addresses), then save the listing under
tests/fixtures/linux_multipath/ (its README says how). Everything goes in ~\\Downloads\\multipath_capture.zip.
"""
import os
import shutil
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402

sys.path.insert(0, os.path.join(fl.ROOT, "src"))
from alletra_onboard.adapters.hosts import linux_ssh  # noqa: E402

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "multipath_capture")
fl.OUT = OUT
HOST = os.environ.get("LINUX_HOST", "10.54.159.49")
USER = os.environ.get("LINUX_USER", "root")
KEYS = ["hostname", "multipath", "multipath_sudo", "dm_multipath"]
RESULTS = []


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    password = fl.lab_secret(os.environ.get("LINUX_PW_NAME", "LAB_DEFAULT_PW"))

    fl.banner("1. Fixed reads over SSH as %s@%s" % (USER, HOST))
    with linux_ssh.LinuxHostClient(HOST, USER, password) as client:
        for key in KEYS:
            status, out = client.run(key)
            fl.save("%s.txt" % key, "# %s\n# exit %s\n%s" % (linux_ssh.COMMANDS[key], status, out))
            RESULTS.append("      %-15s exit %s, %d line(s)" % (key, status, len(out.splitlines())))
            print(RESULTS[-1])
        read = linux_ssh.read_linux_host(client, HOST, HOST)

    fl.banner("2. The app's summary")
    fl.save("summary.txt", "state: %s\nmultipath: %s\nnotes: %s\n" % (read.multipath_state, read.multipath, read.notes))
    RESULTS.append("      state %s: multipath: %s" % (read.multipath_state, read.multipath))
    print(RESULTS[-1])
    # not_set_up is a definite answer too (no driver, nothing to list), so "permitted" is all the first check says;
    # a read that timed out says nothing either way.
    check("the read was permitted (root, or sudo without a password)", read.multipath_state not in ("not_permitted", "timed_out", ""),
          "state " + (read.multipath_state or "none"))
    check("multipath is set up and lists Alletra/3PAR devices", read.multipath_state in ("ok", "uneven", "degraded"),
          "state " + (read.multipath_state or "none"))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        if os.path.isdir(OUT):
            fl.save("script_stopped.txt", traceback.format_exc())
        raise
    finally:
        if os.path.isdir(OUT):
            fails = sum(1 for r in RESULTS if r.startswith("FAIL"))
            fl.save("report.txt", "\n".join(RESULTS + ["", "%d FAIL" % fails]))
            fl.banner("Done, %d FAIL. Send me %s" % (fails, shutil.make_archive(OUT, "zip", OUT)))
