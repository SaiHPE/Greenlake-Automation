"""What the Alletra MP + Primera replication pair looks like today, before anything is set up (BL-41).
READ-ONLY, no prompts.

    .\\.venv\\Scripts\\python.exe lab\\rcip_pair_capture.py

Changes nothing on either array. Logs in as 3paradm with RCIP_PAIR_PW from .env to:
    Alletra MP  rack13arcus       10.132.30.121
    Primera     PRIMERA630R11U22  10.132.30.28
1. over SSH: show commands, checkhealth, and the CLI help of every command replication setup would use
2. over WSAPI: one session per array, GETs only, logged out at the end
3. from this workspace: pings the RCIP addresses the lab planned (does anything answer on them now?)
4. says, per planned port: what it is now, its link, and which hosts, sessions or LUNs use it
Everything goes in ~\\Downloads\\rcip_pair_capture.zip. Copy that zip outside the repo folder.
"""
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import traceback
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "rcip_pair_capture")
fl.OUT = OUT
# The lab's plan (mail of 2026-11-03): port -> RCIP address, all 10.93.18.0/23, MTU 1500.
ARRAYS = [
    ("alletra", "10.132.30.121", {"0:4:1": "10.93.18.10", "0:4:2": "10.93.18.11", "1:4:1": "10.93.18.12", "1:4:2": "10.93.18.13"}),
    ("primera", "10.132.30.28", {"0:1:1": "10.93.18.19", "1:1:1": "10.93.18.20"}),
]
READS = [
    "showsys", "showsys -d", "showversion", "showlicense", "shownet", "showwsapi",
    "showport", "showport -i", "showport -par", "showport -sfp", "showport -rcip", "showport -iscsi",
    "showport -iscsivlans", "showport -file",
    "showiscsisession", "showhost -d", "showhostset -d", "showvlun -a", "showvlun -t", "showcpg",
    "showrcopy", "showrcopy -d", "showrcopy links", "showrcopy targets", "showrcopy groups", "showrctransport -rcip",
    "checkhealth",
]
HELP = ["controlport", "controliscsiport", "startrcopy", "stoprcopy", "creatercopytarget", "admitrcopylink",
        "dismissrcopylink", "removercopytarget", "checkrclink", "showrctransport"]
WSAPI_GETS = ["/system", "/ports", "/remotecopy", "/remotecopytargets", "/remotecopylinks", "/remotecopygroups"]
NSP = re.compile(r"^\d+:\d+:\d+$")
RESULTS = []


def note(text):
    print("      " + text)
    RESULTS.append("      " + text)


def file_name(tag, cmd):
    return "%s_%s.txt" % (tag, cmd.replace(" ", "_").replace("-", ""))


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


def rows(text, first_col=None):
    out = []
    for ln in (text or "").splitlines():
        p = ln.split()
        if p and NSP.match(p[0]) and (first_col is None or p[0] in first_col):
            out.append(p)
    return out


def summarize(tag, host, plan, raw):
    name = next((ln.split()[1] for ln in raw["showsys"].splitlines() if ln.split()[:1] and ln.split()[0].startswith("0x")), "?")
    os_line = next((ln.strip() for ln in raw["showversion"].splitlines() if ln.startswith("Release")), "?")
    note("%s %s: %s, %s" % (tag, host, name, os_line))
    lic = [ln.strip() for ln in raw["showlicense"].splitlines() if "remote copy" in ln.lower()]
    note("%s: Remote Copy licence: %s" % (tag, "; ".join(lic) or "NOT LISTED in showlicense"))
    wsapi = [ln.strip() for ln in raw["showwsapi"].splitlines() if ln.strip()][-1:] or ["?"]
    note("%s: WSAPI: %s" % (tag, " ".join(wsapi[0].split())[:120]))
    status = [ln.strip() for ln in raw["showrcopy"].splitlines() if ln.strip()][:3]
    note("%s: showrcopy: %s" % (tag, " | ".join(status)[:200] or "(empty)"))
    for kind in ("targets", "links", "groups"):
        lines = [" ".join(ln.split()) for ln in raw["showrcopy %s" % kind].splitlines()[2:] if ln.strip() and not ln.startswith("-")]
        note("%s: Remote Copy %s: %s" % (tag, kind, "; ".join(lines)[:300] or "none"))
    ports = {p[0]: p for p in rows(raw["showport"])}
    sfp = {p[0]: p for p in rows(raw["showport -sfp"])}
    hw = {p[0]: p for p in rows(raw["showport -i"])}
    hosts = [ln.split() for ln in raw["showhost -d"].splitlines() if len(ln.split()) >= 6]
    sessions = rows(raw["showiscsisession"])
    vluns = [ln.split() for ln in raw["showvlun -a"].splitlines() if len(ln.split()) >= 6]
    for nsp, ip in plan.items():
        p = ports.get(nsp)
        s = sfp.get(nsp)
        on_port_hosts = sorted({h[1] if h[1] != "--" else "(unnamed login)" for h in hosts if h[-2] == nsp})
        on_port_luns = [v for v in vluns if nsp in v]
        note("%s %s (plan RCIP %s): now %s | HW %s | SFP %s | %d session(s) | hosts %s | %d active LUN path(s)" % (
            tag, nsp, ip,
            " ".join(p[1:]) if p else "NOT IN showport",
            hw[nsp][-1] if nsp in hw else "?",
            " ".join(s[1:]) if s else "none",
            sum(1 for r in sessions if r[0] == nsp),
            ", ".join(on_port_hosts) or "none",
            len(on_port_luns)))
    planned_ips = set(plan.values())
    in_use = [" ".join(p) for p in rows(raw["showport"]) if len(p) > 3 and p[3] in planned_ips]
    note("%s: planned RCIP addresses already on a port of this array: %s" % (tag, "; ".join(in_use) or "none"))


def capture(tag, host, plan, password):
    fl.banner("%s %s: show commands, checkhealth, help (read-only)" % (tag, host))
    raw = {}
    try:
        c = fl.ssh(host, password)
    except Exception as exc:  # noqa: BLE001
        note("%s %s: SSH login failed: %s %s" % (tag, host, type(exc).__name__, exc))
        return None
    try:
        for cmd in READS + ["help " + h for h in HELP]:
            try:
                raw[cmd] = fl.run(c, cmd)
            except Exception as exc:  # noqa: BLE001
                raw[cmd] = "ERROR %r" % exc
            fl.save(file_name(tag, cmd), "# %s\n%s" % (cmd, raw[cmd]))
            print("  %-26s %d line(s)" % (cmd, len(raw[cmd].splitlines())))
    finally:
        c.close()

    fl.banner("%s %s: WSAPI GETs" % (tag, host))
    try:
        w = Wsapi(host, "3paradm", password)
        try:
            for path in WSAPI_GETS:
                try:
                    fl.save("%s_wsapi%s.json" % (tag, path.replace("/", "_")), json.dumps(w.get(path), indent=1))
                    print("  GET %-20s ok" % path)
                except urllib.error.HTTPError as exc:
                    note("%s: GET %s -> HTTP %s" % (tag, path, exc.code))
        finally:
            w.close()
        note("%s: WSAPI answered on %s" % (tag, w.base))
    except Exception as exc:  # noqa: BLE001
        note("%s: %s" % (tag, exc))
    return raw


def ping(addr):
    if sys.platform == "win32":
        args = ["ping", "-n", "2", "-w", "1500", addr]
    else:  # macOS: -W in milliseconds
        args = ["ping", "-c", "2", "-W", "1500", addr]
    r = subprocess.run(args, capture_output=True, text=True, timeout=30)
    out = r.stdout + r.stderr
    if "not permitted" in out.lower():
        return None, out
    return "TTL=" in out.upper(), out


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    password = fl.lab_secret("RCIP_PAIR_PW")
    raws = {tag: capture(tag, host, plan, password) for tag, host, plan in ARRAYS}

    fl.banner("From this workspace: does anything answer on the planned RCIP addresses now?")
    log = []
    for tag, _host, plan in ARRAYS:
        for nsp, ip in plan.items():
            ok, out = ping(ip)
            state = "not run (ping not allowed here)" if ok is None else ("answers" if ok else "silent")
            note("ping %-12s %-7s (planned for %s %s)" % (ip, state, tag, nsp))
            log.append("# ping %s\n%s" % (ip, out))
    fl.save("workspace_pings.txt", "\n".join(log))

    fl.banner("What each planned port is today")
    for tag, host, plan in ARRAYS:
        if raws.get(tag):
            summarize(tag, host, plan, raws[tag])


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
