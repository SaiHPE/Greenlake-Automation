"""What the lab arrays say about peer ports, before the tool sets any (BL-26). READ-ONLY, no prompts.

    .\\.venv\\Scripts\\python.exe lab\\peer_port_capture.py

Changes nothing on either array. Logs in as 3paradm with LAB_ARRAY_PW from .env to:
    E18U31  10.64.154.190   has two FC peer ports (0:3:2, 1:3:2, seen 2026-10-07)
    D22U27  10.64.122.99    has none; its FC ports are host or free
1. over SSH: show commands and the CLI's own help (show*, help only; nothing on the write list)
2. over WSAPI: one session per array, GET /ports and GET /wsapiconfiguration only, logged out at the end
3. says, per FC port: mode, Type, Connmode, ConnType, logins, and what WSAPI calls it
Everything goes in ~\\Downloads\\peer_port_capture.zip. An array that does not answer is reported and
skipped (E18U31 was being replaced in October).

The files map to the fixtures tests/unit/test_peer_ports.py expects (copy them, scrubbed):
    <array>_showport_par.txt   -> tests/fixtures/peer_ports/<array>/showport_par.txt
    <array>_showport_peer.txt  -> tests/fixtures/peer_ports/<array>/showport_peer.txt
    <array>_showport_c.txt     -> tests/fixtures/peer_ports/<array>/showport_c.txt
    <array>_wsapi_ports.json   -> tests/fixtures/peer_ports/<array>/wsapi_ports.json
"""
import json
import os
import re
import shutil
import ssl
import sys
import traceback
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "peer_port_capture")
fl.OUT = OUT
# CAPTURE_ARRAYS="TAG=address[,TAG=address]" points the capture at other arrays, e.g. rack13=10.132.30.121
ARRAYS = ([tuple(x.split("=", 1)) for x in os.environ["CAPTURE_ARRAYS"].split(",")]
          if os.environ.get("CAPTURE_ARRAYS") else [("E18U31", "10.64.154.190"), ("D22U27", "10.64.122.99")])
READS = [
    "showsys", "showversion",
    "showport", "showport -par", "showport -peer", "showport -c", "showport -i", "showport -sfp",
    "showhost -d", "showvlun -a",
    "help controlport", "help showport", "help showportdev",
]
WSAPI_GETS = ["/ports", "/wsapiconfiguration"]
NSP = re.compile(r"^\d+:\d+:\d+$")
RESULTS = []


def note(text):
    print("      " + text)
    RESULTS.append("      " + text)


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def file_name(tag, cmd):
    return "%s_%s.txt" % (tag, cmd.replace(" ", "_").replace("-", "").replace(":", ""))


class Wsapi:
    """GET-only WSAPI session. No proxy: the arrays are on the lab management network."""

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


def fc_ports(showport):
    """N:S:P -> (mode, state, type) for every FC row of plain showport."""
    out = {}
    for line in showport.splitlines():
        p = line.split()
        if len(p) >= 7 and NSP.match(p[0]) and p[6] == "FC":
            out[p[0]] = (p[1], p[2], p[5])
    return out


def capture(tag, host, password):
    fl.banner("%s %s: CLI reads over SSH (show and help only)" % (tag, host))
    try:
        c = fl.ssh(host, password)
    except Exception as exc:  # noqa: BLE001
        check("%s SSH login" % tag, False, repr(exc))
        return
    raw = {}
    try:
        for cmd in READS:
            try:
                raw[cmd] = fl.run(c, cmd)
            except Exception as exc:  # noqa: BLE001
                raw[cmd] = "ERROR %r" % exc
            fl.save(file_name(tag, cmd), "# %s\n%s" % (cmd, raw[cmd]))
            note("%-22s %d line(s)" % (cmd, len(raw[cmd].splitlines())))
        ports = fc_ports(raw["showport"])
        # What is logged in on each FC port, from the switch side: only the ports that exist.
        for nsp in sorted(ports):
            cmd = "showportdev ns %s" % nsp
            try:
                raw[cmd] = fl.run(c, cmd)
            except Exception as exc:  # noqa: BLE001
                raw[cmd] = "ERROR %r" % exc
            fl.save(file_name(tag, cmd), "# %s\n%s" % (cmd, raw[cmd]))
    finally:
        c.close()

    fl.banner("%s: WSAPI reads (GET only)" % tag)
    data = {}
    try:
        w = Wsapi(host, "3paradm", password)
    except Exception as exc:  # noqa: BLE001
        check("%s WSAPI login" % tag, False, repr(exc))
        w = None
    if w:
        try:
            for path in WSAPI_GETS:
                try:
                    data[path] = w.get(path)
                    fl.save("%s_wsapi%s.json" % (tag, path.replace("/", "_")), json.dumps(data[path], indent=1))
                    note("GET %-20s ok" % path)
                except urllib.error.HTTPError as exc:
                    note("GET %-20s HTTP %s" % (path, exc.code))
        finally:
            w.close()

    fl.banner("%s: what it says" % tag)
    note("OS: " + next((ln.strip() for ln in raw["showversion"].splitlines() if ln.startswith("Release version")), "?"))
    by_wsapi = {}
    for m in (data.get("/ports") or {}).get("members", []):
        pos = m.get("portPos") or {}
        by_wsapi["%s:%s:%s" % (pos.get("node"), pos.get("slot"), pos.get("cardPort"))] = m
    par = {ln.split()[0]: ln.split()[1:3] for ln in raw["showport -par"].splitlines() if ln.split() and NSP.match(ln.split()[0])}
    logins = {}
    for line in raw["showhost -d"].splitlines():
        p = line.split()
        if len(p) >= 6 and NSP.match(p[-2]):
            logins.setdefault(p[-2], []).append(p[-3])
    for nsp, (mode, state, ptype) in sorted(fc_ports(raw["showport"]).items()):
        m = by_wsapi.get(nsp, {})
        note("%s mode %-9s state %-9s Type %-5s par %-14s logins %-2d wsapi mode %s type %s" % (
            nsp, mode, state, ptype, "/".join(par.get(nsp, ["?"])), len(logins.get(nsp, [])),
            m.get("mode"), m.get("type")))
    check("%s showport -par read" % tag, bool(par), "no N:S:P rows" if not par else "")
    check("%s controlport help read" % tag, "controlport config" in raw["help controlport"])


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    password = fl.lab_secret("LAB_ARRAY_PW")
    for tag, host in ARRAYS:
        capture(tag, host, password)


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
