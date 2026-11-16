"""The app's own replication steps on the Alletra MP -> Primera RCIP pair (BL-41). No prompts.

    python lab/rcip_pair_lab.py         (the app must be running on http://127.0.0.1:8765)

Needs the partnership `rcip_setup_lab.py setup` made (links Up both ways). CHANGES BOTH ARRAYS and
removes what it made:
1. checks the links are Up and nothing zz_rc_* is on either array; notes the Primera's own groups
2. on the Alletra rack13-ARCUS (10.132.30.121), over the app's WSAPI client: volume zz_rc_vol01
   (1 GiB thin, SSD_r6) in volume set zz_rc_vvs
3. a Custom run (replicate, failover test, as-built) from a sheet whose Replication tab names the
   Primera PRIMERA630R11U22 (10.132.30.28), one sync row zz_rc_vvs -> peer CPG SSD_r6:
   preview, link check, apply, verify until replicating, failover test, as-built
4. the run's removal sets over SSH, then the volume and set from step 2; checks nothing zz_rc_* is
   left and the Primera's own groups are as they were
Password: RCIP_PAIR_PW. Evidence in RCIP_LAB_DIR (default ~/Downloads)/rcip_pair/.
"""
import base64
import io
import json
import os
import re
import shutil
import sys
import time
import traceback
import urllib.error
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402

A_HOST, P_HOST = "10.132.30.121", "10.132.30.28"
VOL, VVSET = "zz_rc_vol01", "zz_rc_vvs"
GROUP = VVSET + "_rcg"
BASE = os.environ.get("RCIP_LAB_DIR") or os.path.join(os.path.expanduser("~"), "Downloads")
OUT = os.path.join(BASE, "rcip_pair")
CEILING_S = 20 * 60
RESULTS = []
STEP = {"n": 0}


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def evidence(name, data):
    STEP["n"] += 1
    fl.save("%02d-%s" % (STEP["n"], name), data if isinstance(data, str) else json.dumps(data, indent=2))


def api(method, path, body=None):
    req = urllib.request.Request(fl.APP + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with fl.OPENER.open(req, timeout=120) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as exc:
        return exc.code, (exc.read() or b"").decode("utf-8", "replace")


def events(run_id):
    return api("GET", "/runs/%s/events" % run_id)[1]["events"]


def step(run_id, path, done, name, body=None):
    since = len(events(run_id))
    status, resp = api("POST", "/runs/%s%s" % (run_id, path), body if body is not None else {})
    if status >= 300:
        evidence(name + "-refused.txt", "HTTP %s %s" % (status, resp))
        raise RuntimeError("POST %s -> HTTP %s: %s" % (path, status, str(resp)[:300]))
    deadline = time.time() + CEILING_S
    while time.time() < deadline:
        time.sleep(2)
        hit = [e for e in events(run_id)[since:] if e["event_type"] in tuple(done) + ("step.crashed",)]
        if hit:
            evidence(name + ".json", hit[-1])
            if hit[-1]["event_type"] == "step.crashed":
                raise RuntimeError("%s crashed: %s" % (path, hit[-1]["message"]))
            print("  %s: %s" % (hit[-1]["event_type"], hit[-1]["message"][:200]))
            return hit[-1]
    raise RuntimeError("%s: no %s within %d s" % (path, "/".join(done), CEILING_S))


def links_up(c):
    rows = [ln.split() for ln in fl.run(c, "showrcopy links").splitlines()]
    mine = [r for r in rows if len(r) >= 4 and r[0] in ("PRIMERA630R11U22", "rack13-ARCUS")]
    return sum(1 for r in mine if r[3] == "Up"), len(mine)


def leftovers(a, p):
    found = []
    for label, c in (("alletra", a), ("primera", p)):
        for cmd in ("showrcopy groups zz_rc*", "showvv zz_rc*", "showvvset zz_rc*"):
            for line in fl.run(c, cmd).splitlines():
                hit = next((x for x in line.split() if x.startswith("zz_rc")), None)
                if hit and not line.lower().startswith(("error", "no ")):
                    found.append("%s: %s (%s)" % (label, hit, cmd.split()[0]))
    return sorted(set(found))


def other_groups(c):
    out = {}
    for line in fl.run(c, "showrcopy groups").splitlines():
        t = line.split()
        if len(t) >= 5 and t[1] in ("rack13-ARCUS_PRIMERA", "rack13-ARCUS", "PRIMERA630R11U22") and not t[0].startswith("zz_rc"):
            out[t[0]] = " ".join(t[1:5])
    return out


def sweep_by_name(a, p):
    """What the removal sets do not cover (the scripts' own volume and set, or a stopped apply):
    zz_rc_* objects only, by exact name, groups first, then sets, then volumes. Returns the log lines."""
    log = []
    for label, c in (("alletra", a), ("primera", p)):
        groups = sorted({t[0] for t in (ln.split() for ln in fl.run(c, "showrcopy groups zz_rc*").splitlines())
                         if len(t) >= 5 and t[0].startswith("zz_rc") and t[1] in ("PRIMERA630R11U22", "rack13-ARCUS")})
        sets = sorted({t[1] for t in (ln.split() for ln in fl.run(c, "showvvset zz_rc*").splitlines())
                       if len(t) >= 2 and t[0].isdigit() and t[1].startswith("zz_rc")})
        vols = sorted({t[1] for t in (ln.split() for ln in fl.run(c, "showvv zz_rc*").splitlines())
                       if len(t) >= 2 and t[0].isdigit() and t[1].startswith("zz_rc")})
        cmds = [v % g for g in groups for v in ("stoprcopygroup -f %s", "removercopygroup -f %s")]
        cmds += ["removevvset -f %s" % s for s in sets] + ["removevv -f %s" % v for v in vols]
        for cmd in cmds:
            answer = fl.run(c, cmd).strip()
            log.append("(by name) [%s] $ %s\n%s" % (label, cmd, answer))
            print("  (by name) [%s] $ %s  -> %s" % (label, cmd, answer.splitlines()[-1] if answer else "(no output)"))
    return log


def compose_body(password):
    return {
        "init": {
            "gl_client_id": "not-used", "gl_client_secret": "not-used", "gl_token_url": "https://not-used",
            "serial_number": "CZ2D2K014S", "part_number": "not-used", "subscription_key": "not-used",
            "service_catalog_region_id": "ap-northeast", "dscc_region_code": "jp1",
            "mgmt_ipv4": A_HOST, "mask": "255.255.252.0", "gateway": "not-used", "dns1": "not-used",
            "ntp": "not-used", "timezone": "Asia/Kolkata",
            "contact_first_name": "Sai", "contact_last_name": "Roopesh", "contact_language": "English",
            "contact_company": "HPE", "contact_phone": "0", "contact_email": "not-used@hpe.com",
            "dscc_system_name": "rack13-ARCUS", "dscc_country": "India",
            "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab RCIP Alletra-Primera",
        },
        "targets": {
            "prov_array_host": A_HOST, "prov_array_user": "3paradm", "prov_array_password": password,
            "prov_vcenter_host": "not-used", "prov_vcenter_user": "not-used", "prov_vcenter_password": "not-used",
        },
        "volumes": [], "hostsets": [], "hosts": [],
        "replication": {
            "fields": {"peer_host": P_HOST, "peer_user": "3paradm", "peer_password": password},
            "rows": [{"vvset": VVSET, "peer_cpg": "SSD_r6", "mode": "sync"}],
        },
    }


def compose(password):
    status, resp = api("POST", "/init-sheet/compose", compose_body(password))
    if status != 200:
        raise RuntimeError("compose -> HTTP %s: %s" % (status, resp))
    with open(os.path.join(OUT, "sheet.xlsx"), "wb") as f:
        f.write(base64.b64decode(resp["content_b64"]))
    status, up = api("POST", "/init-sheet/upload", {"content_b64": resp["content_b64"]})
    if status != 200:
        raise RuntimeError("upload -> HTTP %s: %s" % (status, up))
    status, r = api("POST", "/runs/from-sheet", {"token": up["token"], "mode": "CUSTOM",
                                                  "selected_steps": ["replicate", "failover_test", "asbuilt"]})
    if status != 200:
        raise RuntimeError("from-sheet -> HTTP %s: %s" % (status, r))
    print("run " + r["run"]["run_id"])
    fl.save("run-id.txt", r["run"]["run_id"])
    return r["run"]["run_id"]


def docx_text(run_id):
    data = fl.get("/runs/%s/asbuilt/download" % run_id)
    with open(os.path.join(OUT, "asbuilt.docx"), "wb") as f:
        f.write(data)
    xml = zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode("utf-8")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", xml.replace("</w:p>", "\n")))


def run_replication(run_id):
    ev = step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "replication-preview")
    rplan, report = ev["data"].get("plan") or {}, ev["data"].get("report") or {}
    part = report.get("partnership") or {}
    check("preview: the app reads the Primera", not (report.get("peer") or {}).get("read_error"), (report.get("peer") or {}).get("read_error") or "")
    check("preview: partnership found, every link Up", bool(part) and part.get("links_primary_up") == part.get("links_primary_total") > 0
          and part.get("links_peer_up") == part.get("links_peer_total") > 0,
          "target %s / %s, links %s/%s and %s/%s" % (part.get("target_on_primary"), part.get("target_on_peer"),
                                                   part.get("links_primary_up"), part.get("links_primary_total"),
                                                   part.get("links_peer_up"), part.get("links_peer_total")))
    for f in report.get("findings", []):
        print("  finding: " + f)
    g = next((a for a in rplan.get("actions", []) if a["kind"] == "group" and a["name"] == GROUP), None)
    if not check("plan: group %s 'create', 0 blockers" % GROUP, bool(g and g["state"] == "create") and not rplan.get("blockers"),
                 "; ".join(rplan.get("blockers", []) + report.get("findings", []))[:400]):
        raise RuntimeError("replication plan is not clean")

    ev = step(run_id, "/replication/link-check", ["replication.link_checked", "replication.link_check.failed"], "link-check",
              body={"duration_s": 600})
    lc = ev["data"].get("link_check") or {}
    measured = [x for x in lc.get("results", []) if x["status"] == "measured"]
    check("link check: every link measured (checkrclink on the Alletra and the Primera)",
          ev["event_type"] == "replication.link_checked" and lc.get("results") and len(measured) == len(lc["results"]),
          ev["message"][:200])

    ev = step(run_id, "/replication/apply", ["replication.applied", "replication.apply.failed"], "replication-apply")
    res = ev["data"].get("result") or {}
    check("apply: group created, nothing failed", GROUP in res.get("groups_created", []) and not res.get("error"),
          res.get("error") or ", ".join(res.get("groups_created", [])))
    removals = (res.get("removals_a", []), res.get("removals_b", []))
    if res.get("error"):
        return removals
    ver = {}
    for attempt in range(30):
        ev = step(run_id, "/replication/verify", ["replication.verified", "replication.verify.failed"], "replication-verify-%02d" % attempt)
        ver = ev["data"].get("verification") or {}
        if ver.get("groups") and all(x["verdict"] == "replicating" for x in ver["groups"]):
            break
        time.sleep(20)
    check("verify: every group replicating, links Up", ver.get("links_ok") and ver.get("groups")
          and all(x["verdict"] == "replicating" for x in ver["groups"]),
          "; ".join("%s %s %s" % (x["group"], x["verdict"], x.get("detail", "")) for x in ver.get("groups", [])))

    ev = step(run_id, "/replication/failover-test", ["failover.completed", "failover.failed"], "failover", body={})
    rec = ev["data"].get("record") or {}
    check("failover test passed, group back to normal", rec.get("result") == "passed",
          "failover %ss, synced back %ss; %s" % (rec.get("time_to_failover_s"), rec.get("time_to_synced_s"), rec.get("error") or ev["message"][:200]))

    ev = step(run_id, "/asbuilt", ["asbuilt.generated", "asbuilt.failed"], "asbuilt")
    if ev["event_type"] == "asbuilt.generated":
        text = docx_text(run_id)
        evidence("asbuilt-text.txt", text)
        for needle in ("PRIMERA630R11U22", GROUP, "Replication configured in this run", "Failover test", "Link check"):
            check("as-built names '%s'" % needle, needle in text)
    else:
        check("as-built generated", False, ev["message"][:200])
    return removals


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    fl.OUT = OUT
    from alletra_onboard.adapters.array.wsapi_client import WsapiClient

    password = fl.lab_secret("RCIP_PAIR_PW")
    a, p = fl.ssh(A_HOST, password), fl.ssh(P_HOST, password)
    fl.banner("1. Before")
    for label, c in (("alletra", a), ("primera", p)):
        up, total = links_up(c)
        if not check("%s: RCIP links Up %d of %d" % (label, up, total), total and up == total):
            sys.exit("The partnership is not up: run rcip_setup_lab.py setup first.")
    left = leftovers(a, p)
    if left:
        sys.exit("zz_rc_* objects are already on the arrays, nothing was done:\n  " + "\n  ".join(left))
    before = other_groups(p)
    evidence("primera-groups-before.json", before)
    removals = ([], [])
    try:
        fl.banner("2. Test volume and volume set on the Alletra (the app's WSAPI client)")
        with WsapiClient(A_HOST, "3paradm", password) as w:
            check("volume %s created" % VOL, w.ensure_volume(VOL, "SSD_r6", 1024, "tpvv") == "created")
            check("volume set %s created" % VVSET, w.ensure_volume_set(VVSET, [VOL]) == "created")
        fl.banner("3. The app's replication steps")
        app_ok = api("GET", "/app/profile")[0] == 200
        if not check("the app answers on %s" % fl.APP, app_ok):
            raise RuntimeError("start the app first")
        run_id = compose(password)
        try:
            removals = run_replication(run_id)
        except Exception as exc:  # noqa: BLE001
            check("stopped: %s" % str(exc)[:300], False)
            evidence("error.txt", traceback.format_exc())
            done = [e for e in events(run_id) if e["event_type"] == "replication.applied"]
            if done:
                res = done[-1]["data"].get("result") or {}
                removals = (res.get("removals_a", []), res.get("removals_b", []))
    finally:
        fl.banner("4. Cleanup")
        a.close(), p.close()
        a, p = fl.ssh(A_HOST, password), fl.ssh(P_HOST, password)
        log = []
        for label, c, lines in (("alletra", a, removals[0]), ("primera", p, removals[1])):
            for cmd in lines:
                answer = fl.run(c, cmd).strip()
                log.append("[%s] $ %s\n%s" % (label, cmd, answer))
                print("  [%s] $ %s  -> %s" % (label, cmd, answer.splitlines()[-1] if answer else "(no output)"))
        evidence("cleanup.txt", "\n".join(log + sweep_by_name(a, p)))
        left = leftovers(a, p)
        check("no zz_rc_* object left on either array", not left, "; ".join(left))
        after = other_groups(p)
        evidence("primera-groups-after.json", after)
        check("the Primera's own groups are as they were", after == before,
              "; ".join("%s %s -> %s" % (k, before.get(k), after.get(k)) for k in sorted(set(before) | set(after)) if before.get(k) != after.get(k)))
        for label, c in (("alletra", a), ("primera", p)):
            up, total = links_up(c)
            check("%s: RCIP links still Up %d of %d" % (label, up, total), total and up == total)
        a.close(), p.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        if fl.OUT and os.path.isdir(fl.OUT):
            fails = sum(1 for r in RESULTS if r.startswith("FAIL"))
            fl.save("report.txt", "\n".join(RESULTS + ["", "%d PASS, %d FAIL" % (len(RESULTS) - fails, fails)]))
            fl.banner("%d PASS, %d FAIL. Evidence in %s" % (len(RESULTS) - fails, fails, fl.OUT))
