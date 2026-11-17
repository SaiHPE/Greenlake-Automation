"""What the lab arrays show for iSCSI ports and their VLAN interfaces, before the tool adds any (BL-25,
SPEC-024). READ-ONLY, no prompts.

    .\\.venv\\Scripts\\python.exe lab\\iscsi_vlan_capture.py

Changes nothing on either array. Logs in as 3paradm with LAB_ARRAY_PW from .env to:
    E18U31  10.64.154.190   (iSCSI ports 0:4:1 to 1:4:2 were live on 2026-10-05)
    D22U27  10.64.122.99    (no iSCSI target port on 2026-10-26: the "nothing there" answers)
1. over SSH: show commands and the CLI help of the commands SPEC-024 would use or undo
2. over WSAPI: one session per array, GETs only (/ports, then /ports/<n:s:p>/iSCSIVlans/ for every
   iSCSI port), logged out at the end
3. says per iSCSI port: address, VLAN count, peer flag, the VLAN interfaces, and the hosts logged in
Everything goes in ~\\Downloads\\iscsi_vlan_capture.zip. The files are named as the fixtures the tests
expect: copy <TAG>/... to tests/fixtures/iscsi_vlan/<TAG>/ after scrubbing (no passwords, no customer
names), and write tests/fixtures/iscsi_vlan/README.md saying where and when.
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
import rc_failover_lab as fl  # noqa: E402

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "iscsi_vlan_capture")
fl.OUT = OUT
# CAPTURE_ARRAYS="TAG=address[,TAG=address]" points the capture at other arrays, e.g. rack13=10.132.30.121
ARRAYS = ([tuple(x.split("=", 1)) for x in os.environ["CAPTURE_ARRAYS"].split(",")]
          if os.environ.get("CAPTURE_ARRAYS") else [("E18U31", "10.64.154.190"), ("D22U27", "10.64.122.99")])
# Command -> fixture file name. Every one is a show command or CLI help: nothing here writes.
READS = {
    "showsys": "showsys.txt",
    "showversion": "showversion.txt",
    "shownet": "shownet.txt",
    "showport": "showport.txt",
    "showport -iscsi": "showport_iscsi.txt",
    "showport -iscsivlans": "showport_iscsivlans.txt",
    "showport -rcip": "showport_rcip.txt",
    "showport -file": "showport_file.txt",
    "showhost -d": "showhost_d.txt",
    "help controliscsiport": "help_controliscsiport.txt",
    "help showport": "help_showport.txt",
    "help controlport": "help_controlport.txt",
}
NSP = re.compile(r"^\d+:\d+:\d+$")
RESULTS = []


def note(text):
    print("      " + text)
    RESULTS.append("      " + text)


def save(tag, name, text):
    os.makedirs(os.path.join(OUT, tag, "wsapi"), exist_ok=True)
    fl.save(os.path.join(tag, name), text)


class Wsapi:
    """GET-only WSAPI session. No proxy: the arrays are on the lab management network."""

    def __init__(self, host, user, password):
        ctx = ssl.create_default_context()
        ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))
        body = json.dumps({"user": user, "password": password}).encode()
        last = None
        for base in ("https://%s/api/v1" % host, "https://%s:8080/api/v1" % host):
            req = urllib.request.Request(base + "/credentials", data=body, method="POST", headers={"Content-Type": "application/json"})
            try:
                with self.opener.open(req, timeout=30) as r:
                    self.key, self.base = json.loads(r.read())["key"], base
                    return
            except Exception as exc:  # noqa: BLE001 - try the other port, then report
                last = exc
        raise RuntimeError("WSAPI login failed on 443 and 8080: %r" % last)

    def get(self, path):
        req = urllib.request.Request(self.base + path, headers={"X-HP3PAR-WSAPI-SessionKey": self.key})
        with self.opener.open(req, timeout=60) as r:
            return json.loads(r.read())

    def close(self):
        try:
            self.opener.open(urllib.request.Request(self.base + "/credentials/" + self.key, method="DELETE"), timeout=30).close()
        except Exception:  # noqa: BLE001 - the session times out on its own
            pass


def rows(text):
    return [ln.split() for ln in (text or "").splitlines() if ln.split() and NSP.match(ln.split()[0])]


def capture_ssh(tag, host, password):
    fl.banner("%s %s: show commands and help (read-only)" % (tag, host))
    raw = {}
    try:
        c = fl.ssh(host, password)
    except Exception as exc:  # noqa: BLE001
        note("%s: SSH login failed: %s %s" % (tag, type(exc).__name__, exc))
        return None
    try:
        for cmd, name in READS.items():
            try:
                raw[cmd] = fl.run(c, cmd)
            except Exception as exc:  # noqa: BLE001
                raw[cmd] = "ERROR %r" % exc
            save(tag, name, "# %s\n%s" % (cmd, raw[cmd]))
            print("  %-24s %d line(s)" % (cmd, len(raw[cmd].splitlines())))
    finally:
        c.close()
    return raw


def capture_wsapi(tag, host, password):
    fl.banner("%s %s: WSAPI GETs" % (tag, host))
    try:
        w = Wsapi(host, "3paradm", password)
    except Exception as exc:  # noqa: BLE001
        note("%s: %s" % (tag, exc))
        return
    try:
        ports = w.get("/ports")
        save(tag, "wsapi/ports.json", json.dumps(ports, indent=1))
        for m in ports.get("members", []):
            if m.get("protocol") != 2:          # 2 = iSCSI (python-3parclient PORT_PROTO_ISCSI)
                continue
            pos = m.get("portPos") or {}
            nsp = "%s:%s:%s" % (pos.get("node"), pos.get("slot"), pos.get("cardPort"))
            flag = (m.get("iSCSIPortInfo") or {}).get("vlan")
            path = "/ports/%s/iSCSIVlans/" % nsp
            name = "wsapi/ports_%s_iscsivlans.json" % nsp.replace(":", "_")
            try:
                save(tag, name, json.dumps(w.get(path), indent=1))
                note("%s: GET %s ok (iSCSIPortInfo.vlan = %r)" % (tag, path, flag))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", "replace")
                save(tag, name, json.dumps({"http_status": exc.code, "body": body}, indent=1))
                note("%s: GET %s -> HTTP %s %s (iSCSIPortInfo.vlan = %r)" % (tag, path, exc.code, body[:120], flag))
    finally:
        w.close()


def summarize(tag, raw):
    name = next((ln.split()[1] for ln in raw["showsys"].splitlines() if ln.split()[:1] and ln.split()[0].startswith("0x")), "?")
    os_line = next((ln.strip() for ln in raw["showversion"].splitlines() if ln.startswith("Release")), "?")
    note("%s: %s, %s" % (tag, name, os_line))
    head = next((ln for ln in raw["showport -iscsi"].splitlines() if ln.startswith("N:S:P")), "(no header)")
    note("%s: showport -iscsi header: %s" % (tag, " ".join(head.split())))
    for p in rows(raw["showport -iscsi"]):
        note("%s: iSCSI %s" % (tag, " ".join(p)))
    vl = [ln for ln in raw["showport -iscsivlans"].splitlines() if ln.strip()]
    note("%s: showport -iscsivlans: %d line(s); first: %s" % (tag, len(vl), " | ".join(vl[:3])[:240]))
    helptext = raw["help controliscsiport"]
    forms = [ln.strip() for ln in helptext.splitlines() if ln.strip().startswith("controliscsiport")]
    note("%s: help controliscsiport forms: %s" % (tag, "; ".join(forms)[:600] or "none (see the file)"))
    logged = sorted({(h[1], h[-2]) for h in (ln.split() for ln in raw["showhost -d"].splitlines()) if len(h) >= 6 and NSP.match(h[-2])})
    note("%s: hosts logged in per port: %s" % (tag, "; ".join("%s on %s" % x for x in logged)[:400] or "none"))


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    password = fl.lab_secret("LAB_ARRAY_PW")
    for tag, host in ARRAYS:
        raw = capture_ssh(tag, host, password)
        capture_wsapi(tag, host, password)
        if raw:
            summarize(tag, raw)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        if os.path.isdir(OUT):
            fl.save("script_stopped.txt", traceback.format_exc())
        raise
    finally:
        if os.path.isdir(OUT):
            fl.save("report.txt", "\n".join(RESULTS))
            fl.banner("Done. Send me %s" % shutil.make_archive(OUT, "zip", OUT))
