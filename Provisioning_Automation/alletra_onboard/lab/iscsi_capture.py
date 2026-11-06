"""What D22U27 holds for iSCSI hosts, before the tool creates them (BL-44). READ-ONLY, no prompts.

    .\\.venv\\Scripts\\python.exe lab\\iscsi_capture.py

Changes nothing on the array. Logs in to D22U27 (10.64.122.99) as 3paradm with LAB_ARRAY_PW from .env:
1. over SSH, runs show commands and the CLI's own help for createhost and removehost
2. over WSAPI, opens one session, runs GETs only, and closes the session
3. says what it found: OS, iSCSI target ports and sessions, hosts that carry an IQN, persona ids,
   and whether anything named zz_is_* is already there
Everything goes in ~\\Downloads\\iscsi_capture.zip.
"""
import json
import os
import shutil
import ssl
import sys
import traceback
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402

HOST = "10.64.122.99"
OUT = os.path.join(os.path.expanduser("~"), "Downloads", "iscsi_capture")
fl.OUT = OUT
PREFIX = "zz_is_"
LINUX_IQN = "iqn.1994-05.com.redhat:6e35c4a016a0"   # the lab Linux host 10.54.159.49, read 2026-10-05
READS = [
    "showversion",
    "showport",
    "showport -iscsi",
    "showiscsisession",
    "showhost -d",
    "showhost -persona",
    "showhost -listpersona",
    "showhostset -d",
    "help createhost",
    "help removehost",
    "showhost %s*" % PREFIX,
    "showhostset %s*" % PREFIX,
    "showvv %s*" % PREFIX,
    "showvvset %s*" % PREFIX,
]
WSAPI_GETS = ["/system", "/hosts", "/hostpersonas", "/ports", "/hostsets", "/volumesets"]
RESULTS = []


def note(text):
    print("      " + text)
    RESULTS.append("      " + text)


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def file_name(cmd):
    return cmd.replace(" ", "_").replace("-", "").replace("*", "STAR") + ".txt"


class Wsapi:
    """GET-only WSAPI session. No proxy: the array is on the lab management network."""

    def __init__(self, host, user, password):
        ctx = ssl.create_default_context()
        ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
        self.base = "https://%s/api/v1" % host
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))
        body = json.dumps({"user": user, "password": password}).encode()
        req = urllib.request.Request(self.base + "/credentials", data=body, method="POST",
                                     headers={"Content-Type": "application/json"})
        with self.opener.open(req, timeout=30) as r:
            self.key = json.loads(r.read())["key"]

    def get(self, path):
        req = urllib.request.Request(self.base + path, headers={"X-HP3PAR-WSAPI-SessionKey": self.key})
        with self.opener.open(req, timeout=60) as r:
            return json.loads(r.read())

    def close(self):
        req = urllib.request.Request(self.base + "/credentials/" + self.key, method="DELETE")
        try:
            self.opener.open(req, timeout=30).close()
        except Exception:  # noqa: BLE001 - the session times out on its own
            pass


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    password = fl.lab_secret("LAB_ARRAY_PW")

    fl.banner("1. CLI reads over SSH (show and help only)")
    c = fl.ssh(HOST, password)
    raw = {}
    try:
        for cmd in READS:
            try:
                raw[cmd] = fl.run(c, cmd)
            except Exception as exc:  # noqa: BLE001
                raw[cmd] = "ERROR %r" % exc
            fl.save(file_name(cmd), "# %s\n%s" % (cmd, raw[cmd]))
            note("%-28s %d line(s)" % (cmd, len(raw[cmd].splitlines())))
    finally:
        c.close()

    fl.banner("2. WSAPI reads (GET only)")
    w = Wsapi(HOST, "3paradm", password)
    data = {}
    try:
        for path in WSAPI_GETS:
            try:
                data[path] = w.get(path)
                fl.save("wsapi%s.json" % path.replace("/", "_"), json.dumps(data[path], indent=1))
                note("GET %-14s ok" % path)
            except urllib.error.HTTPError as exc:
                data[path] = None
                note("GET %-14s HTTP %s" % (path, exc.code))
    finally:
        w.close()

    fl.banner("3. What it says")
    note("OS: " + next((ln.strip() for ln in raw["showversion"].splitlines() if ln.startswith("Release version")), "?"))
    ports = (data.get("/ports") or {}).get("members", [])
    iscsi_ports = [p for p in ports if p.get("protocol") == 2]
    note("iSCSI ports over WSAPI (protocol 2): %d %s" % (len(iscsi_ports), ", ".join(
        "%s:%s:%s mode %s link %s" % (p["portPos"]["node"], p["portPos"]["slot"], p["portPos"]["cardPort"],
                                      p.get("mode"), p.get("linkState")) for p in iscsi_ports)))
    note("showport -iscsi: " + (raw["showport -iscsi"].strip().splitlines() or ["(empty)"])[0][:120])
    note("showiscsisession: " + (raw["showiscsisession"].strip().splitlines() or ["(empty)"])[0][:120])

    hosts = (data.get("/hosts") or {}).get("members", [])
    with_iqn = [h for h in hosts if h.get("iSCSIPaths")]
    both = [h["name"] for h in hosts if h.get("iSCSIPaths") and h.get("FCPaths")]
    note("hosts: %d, with an IQN: %d (%s), with FC and iSCSI both: %d %s" % (
        len(hosts), len(with_iqn), ", ".join(h["name"] for h in with_iqn), len(both), ", ".join(both)))
    note("host record keys: %s" % ", ".join(sorted({k for h in hosts for k in h})))
    owner = next((h["name"] for h in hosts for p in h.get("iSCSIPaths") or [] if p.get("name", "").lower() == LINUX_IQN), None)
    note("lab Linux IQN %s: %s" % (LINUX_IQN, "on host " + owner if owner else "on no host"))

    personas = (data.get("/hostpersonas") or {}).get("members", [])
    note("WSAPI personas: " + ", ".join("%s=%s" % (p.get("name"), p.get("wsapiAssignedId")) for p in personas))

    taken = sorted(
        ["host " + h["name"] for h in hosts if h.get("name", "").startswith(PREFIX)]
        + ["host set " + s["name"] for s in (data.get("/hostsets") or {}).get("members", []) if s.get("name", "").startswith(PREFIX)]
        + ["volume set " + s["name"] for s in (data.get("/volumesets") or {}).get("members", []) if s.get("name", "").startswith(PREFIX)]
    )
    vv_lines = [ln for ln in raw["showvv %s*" % PREFIX].splitlines() if ln.split()[1:2] and ln.split()[1].startswith(PREFIX)]
    check("nothing named %s* on the array" % PREFIX, not taken and not vv_lines, "; ".join(taken + vv_lines))
    check("WSAPI host list read", bool(hosts))
    check("createhost help read", "createhost" in raw["help createhost"].lower())


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
