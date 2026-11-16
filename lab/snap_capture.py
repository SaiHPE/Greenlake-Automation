"""What D22U27 holds for snapshots and schedules, before the tool creates any (BL-21). READ-ONLY, no prompts.

    .\\.venv\\Scripts\\python.exe lab\\snap_capture.py

Changes nothing on the array. Logs in to D22U27 (10.64.122.99) as 3paradm with LAB_ARRAY_PW from .env:
1. over SSH, runs show commands and the CLI's own help for the schedule and snapshot commands
2. over WSAPI, opens one session, runs GETs only (and asks for /schedules, to learn whether WSAPI has
   such a resource; any answer, 404 included, is recorded), and closes the session
3. says what it found: OS, time zone, schedules, snapshots, and whether anything named zz_sn_* is there
Everything goes in ~\\Downloads\\snap_capture.zip, under the names the fixtures use; scrub CreatedBy user
names and the /system contact before committing them. Run on rack13-ARCUS (SNAP_HOST set to its
address) on 2026-11-16: tests/fixtures/rack13_snap/.
"""
import json
import os
import shutil
import sys
import traceback
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iscsi_capture as ic  # noqa: E402 - its GET-only Wsapi session
import rc_failover_lab as fl  # noqa: E402

HOST = os.environ.get("SNAP_HOST", "10.64.122.99")
OUT = os.path.join(os.path.expanduser("~"), "Downloads", "snap_capture")
fl.OUT = OUT
PREFIX = "zz_sn_"
# command -> fixture file name
READS = {
    "showversion": "showversion.txt",
    "showdate": "showdate.txt",
    "showsched": "showsched.txt",
    "showvvset": "showvvset.txt",
    "showcpg": "showcpg.txt",
    "showvv -showcols Id,Name,Prov,Type,CopyOf,Rd,CPG,CreationTime,ExpirationTime,RetentionEndTime":
        "showvv_snapcols.txt",
    "showvv %s*" % PREFIX: "showvv_zz_sn.txt",
    "showvvset %s*" % PREFIX: "showvvset_zz_sn.txt",
    "help createsched": "help_createsched.txt",
    "help setsched": "help_setsched.txt",
    "help removesched": "help_removesched.txt",
    "help showsched": "help_showsched.txt",
    "help createsv": "help_createsv.txt",
    "help removevv": "help_removevv.txt",
}
WSAPI_GETS = {
    "/system": "wsapi_system.json",
    "/volumes": "wsapi_volumes.json",
    "/volumesets": "wsapi_volumesets.json",
    "/schedules": "wsapi_schedules_probe.json",
}
RESULTS = ic.RESULTS


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    password = fl.lab_secret("LAB_ARRAY_PW")

    fl.banner("1. CLI reads over SSH (show and help only)")
    c = fl.ssh(HOST, password)
    raw = {}
    try:
        for cmd, name in READS.items():
            try:
                raw[cmd] = fl.run(c, cmd)
            except Exception as exc:  # noqa: BLE001
                raw[cmd] = "ERROR %r" % exc
            fl.save(name, "# %s\n%s" % (cmd, raw[cmd]))
            ic.note("%-40s %d line(s)" % (cmd[:40], len(raw[cmd].splitlines())))
    finally:
        c.close()

    fl.banner("2. WSAPI reads (GET only)")
    w = ic.Wsapi(HOST, "3paradm", password)
    data = {}
    try:
        for path, name in WSAPI_GETS.items():
            try:
                data[path] = w.get(path)
                fl.save(name, json.dumps(data[path], indent=1))
                ic.note("GET %-12s ok" % path)
            except urllib.error.HTTPError as exc:
                data[path] = None
                body = exc.read().decode("utf-8", "replace")
                fl.save(name, json.dumps({"http_status": exc.code, "body": body}, indent=1))
                ic.note("GET %-12s HTTP %s %s" % (path, exc.code, body[:120]))
    finally:
        w.close()

    fl.banner("3. What it says")
    ic.note("OS: " + next((ln.strip() for ln in raw["showversion"].splitlines()
                           if ln.startswith("Release version")), "?"))
    ic.note("showdate: " + " | ".join(ln.strip() for ln in raw["showdate"].splitlines() if ln.strip())[:160])
    sched_lines = [ln for ln in raw["showsched"].splitlines() if "createsv" in ln or "compactcpg" in ln]
    ic.note("schedules: %d (createsv: %d)" % (len(sched_lines), sum("createsv" in ln for ln in sched_lines)))
    vols = (data.get("/volumes") or {}).get("members", [])
    snaps = [v for v in vols if v.get("copyType") == 3]
    ic.note("snapshots over WSAPI: %d; keys seen on them: %s" % (
        len(snaps), ", ".join(sorted({k for v in snaps for k in v}))))
    retention = sorted({k for v in snaps for k in v if "retention" in k.lower()})
    ic.note("snapshots with a retention field: %s" % (", ".join(retention) or "none"))
    ic.note("/schedules: %s" % ("answered" if data.get("/schedules") is not None else "no resource (see file)"))

    taken = [v["name"] for v in vols if v.get("name", "").startswith(PREFIX)]
    taken += [ln.split()[0] for ln in sched_lines if ln.split()[0].startswith(PREFIX)]
    ic.check("nothing named %s* on the array" % PREFIX, not taken, ", ".join(taken))
    ic.check("showsched read", "SchedName" in raw["showsched"] or "No scheduled tasks" in raw["showsched"])
    ic.check("createsched help read", "createsched" in raw["help createsched"].lower())
    ic.check("createsv help read", "createsv" in raw["help createsv"].lower())


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
