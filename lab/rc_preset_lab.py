"""BL-20: the "Provision, then replicate" preset with a real host (ESX1 on D22U27), and runner
scenario 7 (SPEC-006 section 4b), in one go. No prompts.

    python lab\\rc_preset_lab.py

1. checks neither array has zz_rc_* objects
2. composes the sheet (ESX1 by name, one 1 GiB volume in zz_rc_vvs, host set zz_rc_hs, a sync
   Replication row to E18U31), starts the app, runs the preset over the app's own API:
   discover, zoning check, zoning plan (switches read-only), provision, path check, replication
   preview / apply / verify, failover test, verify, as-built
3. reruns the replication preview on a second run (everything must already exist)
4. pastes the run's own removal sets over SSH, checks nothing zz_rc_* is left and the six lab
   groups are as they were
Writes PASS/FAIL lines to report.txt; everything goes in ~\\Downloads\\rc_preset.zip.
"""
import base64
import json
import os
import re
import shutil
import sys
import time
import traceback
import urllib.error
import urllib.request

import rc_failover_lab as fl

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "rc_preset")
fl.OUT = OUT
ARRAY_PW, LAB_PW = fl.lab_secret("LAB_ARRAY_PW"), fl.lab_secret("LAB_DEFAULT_PW")
P_HOST, S_HOST = "10.64.122.99", "10.64.154.190"
HOST = "ESX1"
VOL, VVSET, HOSTSET = "zz_rc_vol01", "zz_rc_vvs", "zz_rc_hs"
GROUP = VVSET + "_rcg"
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
    """POST a step, wait for one of `done` (or step.crashed); returns the event."""
    since = len(events(run_id))
    for _ in range(30):
        status, resp = api("POST", "/runs/%s%s" % (run_id, path), body if body is not None else {})
        if status != 409 or "already running" not in str(resp):
            break
        time.sleep(2)
    if status >= 300:
        evidence(name + "-refused.txt", "HTTP %s %s" % (status, resp))
        raise RuntimeError("POST %s -> HTTP %s: %s" % (path, status, resp))
    deadline = time.time() + CEILING_S
    while time.time() < deadline:
        time.sleep(2)
        new = events(run_id)[since:]
        hit = [e for e in new if e["event_type"] in tuple(done) + ("step.crashed",)]
        if hit:
            evidence(name + ".json", hit[-1])
            if hit[-1]["event_type"] == "step.crashed":
                raise RuntimeError("%s crashed: %s" % (path, hit[-1]["message"]))
            print("  %s: %s" % (hit[-1]["event_type"], hit[-1]["message"][:160]))
            return hit[-1]
    raise RuntimeError("%s: no %s within %d s" % (path, "/".join(done), CEILING_S))


def leftovers(p, s):
    found = []
    for label, c in (("D22U27", p), ("E18U31", s)):
        for cmd in ("showrcopy groups zz_rc*", "showvv zz_rc*", "showvvset zz_rc*", "showhostset zz_rc*", "showvlun -t -v zz_rc*"):
            for line in fl.run(c, cmd).splitlines():
                t = line.split()
                hit = next((x for x in t if x.startswith("zz_rc")), None)
                if hit and not line.lower().startswith(("error", "no ")):
                    found.append("%s: %s (%s)" % (label, hit, cmd.split()[0]))
    return sorted(set(found))


def six_groups(p, s):
    """name -> 'role/status/mode' for every group that is not the tool's, on both arrays."""
    out = {}
    for label, c in (("D22U27", p), ("E18U31", s)):
        for line in fl.run(c, "showrcopy -d groups").splitlines():
            t = line.split()
            if len(t) >= 6 and t[1].isdigit() and not line.startswith(" ") and not t[0].startswith("zz_rc"):
                out["%s:%s" % (label, t[0])] = "%s/%s/%s" % (t[4], t[3], t[5])
    return out


def compose():
    body = {
        "init": {
            "gl_client_id": "not-used", "gl_client_secret": "not-used", "gl_token_url": "https://not-used",
            "serial_number": "CZ2D320BT1", "part_number": "not-used", "subscription_key": "not-used",
            "service_catalog_region_id": "ap-northeast", "dscc_region_code": "jp1",
            "mgmt_ipv4": P_HOST, "mask": "255.255.248.0", "gateway": "10.64.127.254", "dns1": "10.64.122.1",
            "ntp": "not-used", "timezone": "Asia/Kolkata",
            "contact_first_name": "Sai", "contact_last_name": "Roopesh", "contact_language": "English",
            "contact_company": "HPE", "contact_phone": "0", "contact_email": "not-used@hpe.com",
            "dscc_system_name": "AlletraMP_D22U27", "dscc_country": "India",
            "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab replication preset",
        },
        "targets": {
            "prov_array_host": P_HOST, "prov_array_user": "3paradm", "prov_array_password": ARRAY_PW,
            "prov_vcenter_host": "10.54.154.226", "prov_vcenter_user": "administrator@vsphere.local",
            "prov_vcenter_password": LAB_PW,
            # D22U27's own F1 switch runs FOS 7.0.2c and refuses the SSH client; any switch of the fabric reads it
            "prov_sw1_host": "10.64.122.146", "prov_sw1_user": "admin", "prov_sw1_password": LAB_PW,
            "prov_sw2_host": "10.64.127.244", "prov_sw2_user": "admin", "prov_sw2_password": LAB_PW,
        },
        "volumes": [{"name": VOL, "size_gib": "1", "provisioning_type": "tpvv", "cpg": "SSD_r6", "vvset": VVSET}],
        "hostsets": [{"name": HOSTSET, "members": ""}],
        "hosts": [{"name": HOST, "os": "esxi"}],
        "replication": {
            "fields": {"peer_host": S_HOST, "peer_user": "3paradm", "peer_password": ARRAY_PW, "rtt_ms": "1"},
            "rows": [{"vvset": VVSET, "peer_cpg": "SSD_r6", "mode": "sync"}],
        },
    }
    status, resp = api("POST", "/init-sheet/compose", body)
    if status != 200:
        raise RuntimeError("compose -> HTTP %s: %s" % (status, resp))
    with open(os.path.join(OUT, "sheet.xlsx"), "wb") as f:
        f.write(base64.b64decode(resp["content_b64"]))
    return resp["content_b64"]


def new_run(sheet_b64, mode, steps=None):
    status, up = api("POST", "/init-sheet/upload", {"content_b64": sheet_b64})
    if status != 200:
        raise RuntimeError("upload -> HTTP %s: %s" % (status, up))
    status, r = api("POST", "/runs/from-sheet", {"token": up["token"], "mode": mode, "selected_steps": steps or []})
    if status != 200:
        raise RuntimeError("from-sheet -> HTTP %s: %s" % (status, r))
    print("run %s (%s)" % (r["run"]["run_id"], mode))
    return r["run"]["run_id"]


def docx_text(run_id):
    import io
    import zipfile
    data = fl.get("/runs/%s/asbuilt/download" % run_id)
    with open(os.path.join(OUT, "asbuilt.docx"), "wb") as f:
        f.write(data)
    xml = zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode("utf-8")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", xml.replace("</w:p>", "\n")))


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    p, s = fl.ssh(P_HOST, ARRAY_PW), fl.ssh(S_HOST, ARRAY_PW)
    left = leftovers(p, s)
    if left:
        sys.exit("zz_rc_* objects are already on the arrays, nothing was done:\n  " + "\n  ".join(left))
    before = six_groups(p, s)
    evidence("groups-before.json", before)
    fl.restart_app()
    sheet = compose()
    storage_removals, rep_a, rep_b = [], [], []

    try:
        fl.banner("Run 1: Provision, then replicate")
        run1 = new_run(sheet, "REPLICATE")
        ev = step(run1, "/discover", ["discover.completed"], "discover")
        hosts = {h["name"]: h for h in ev["data"]["report"].get("hosts", [])}
        h = hosts.get(HOST)
        check("discovery: %s is in this run and identified" % HOST, bool(h and h.get("in_run") and h.get("identified")),
              json.dumps({k: h.get(k) for k in ("in_run", "identified", "sources", "wwpns")}) if h else "not in report.hosts")
        ev = step(run1, "/zoning/preview", ["zoning.previewed", "zoning.proper"], "zoning-check")
        zoned = ev["data"].get("report", {}).get("zoned_hosts", [])
        check("zoning check: %s is zoned on the array's ports" % HOST, HOST in zoned, ", ".join(zoned))
        try:
            ev = step(run1, "/zoning/plan", ["zoning.plan"], "zoning-plan")
            err = (ev["data"].get("plan") or {}).get("error")
            check("zoning plan read both fabrics' switches (read-only)", not err, err or "")
        except Exception as exc:  # noqa: BLE001
            check("zoning plan read both fabrics' switches (read-only)", False, str(exc))

        builder = {"host_sets": [{"name": HOSTSET, "members": [HOST]}],
                   "exports": [{"source_kind": "vvset", "source_name": VVSET, "target_kind": "hostset", "target_name": HOSTSET, "lun": None}],
                   "vvsets": {VVSET: [VOL]}}
        status, resp = api("POST", "/runs/%s/storage/builder" % run1, builder)
        evidence("builder.json", resp)
        ev = step(run1, "/storage/preview", ["storage.previewed", "storage.preview.failed"], "storage-preview")
        plan = ev["data"]["plan"]
        rows = {(a["kind"], a["name"]): a["state"] for a in plan["actions"]}
        mine = {k: v for k, v in rows.items() if k[1].startswith("zz_rc") or k[0] == "vlun"}
        check("provision plan: volume, VV set, host set and export are 'create'", mine and all(v == "create" for v in mine.values()),
              "; ".join("%s %s=%s" % (k[0], k[1], v) for k, v in mine.items()))
        check("provision plan: host %s 'exists' (it is on the array)" % HOST, rows.get(("host", HOST)) == "exists", str(rows.get(("host", HOST))))
        check("provision plan: 0 blockers", not plan["blockers"], "; ".join(plan["blockers"]))
        if plan["blockers"]:
            raise RuntimeError("provision plan has blockers")
        ev = step(run1, "/storage/apply", ["storage.applied", "storage.apply.failed"], "storage-apply")
        res = ev["data"]["result"]
        storage_removals = res.get("removals", [])
        failed = [o for o in res["outcomes"] if o["status"] == "failed"]
        check("provision apply: nothing failed", not failed and not res.get("error"), res.get("error") or "; ".join("%s %s: %s" % (o["kind"], o["name"], o["detail"]) for o in failed))
        ev = step(run1, "/storage/verify-paths", ["storage.paths.verified", "storage.paths.failed"], "paths")
        ph = next((x for x in ev["data"]["verification"]["hosts"] if x["host"] == HOST), None)
        check("paths: %s is live with the 1 LUN on >= 2 paths" % HOST, bool(ph and ph["verdict"] == "live" and ph.get("lun_count") == 1 and (ph.get("paths_per_lun") or 0) >= 2),
              json.dumps({k: ph.get(k) for k in ("verdict", "lun_count", "paths_per_lun", "detail")}) if ph else "not in report")

        ev = step(run1, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "replication-preview")
        rplan, report = ev["data"]["plan"], ev["data"]["report"]
        part = report.get("partnership") or {}
        links = (part.get("links_primary_up"), part.get("links_primary_total"), part.get("links_peer_up"), part.get("links_peer_total"))
        check("7a read: the partnership was found and every link is Up",
              bool(part) and links[0] == links[1] and links[2] == links[3] and (links[1] or 0) > 0,
              "target %s, links %s/%s and %s/%s" % ((part.get("target_on_primary"),) + links))
        check("7a read: the six lab groups are listed as already present, not planned",
              len(rplan.get("existing_groups", [])) >= 6 and not any(a["name"] in rplan["existing_groups"] for a in rplan["actions"]),
              ", ".join(rplan.get("existing_groups", [])))
        g = next((a for a in rplan["actions"] if a["kind"] == "group" and a["name"] == GROUP), None)
        check("7b plan: group %s 'create', 0 blockers" % GROUP, bool(g and g["state"] == "create") and not rplan["blockers"], "; ".join(rplan["blockers"]))
        if rplan["blockers"]:
            raise RuntimeError("replication plan has blockers")
        # SPEC-020 R4: on RCIP the apply needs the link checked first
        status, resp = api("POST", "/runs/%s/replication/apply" % run1, {})
        check("7b gate: apply refused until the link is checked", status == 409 and "Check the link first" in str(resp), "HTTP %s %s" % (status, str(resp)[:160]))
        ev = step(run1, "/replication/link-check", ["replication.link_checked", "replication.link_check.failed"], "link-check", body={"duration_s": 600})
        lc = ev["data"]["link_check"]
        worst = max((x["latency_ms"] for x in lc["results"] if x["status"] == "measured"), default=None)
        check("7b link check: every link measured, latency within the sync limit", ev["event_type"] == "replication.link_checked"
              and all(x["status"] == "measured" for x in lc["results"]) and worst is not None and worst <= 10,
              ev["message"][:160])
        ev = step(run1, "/replication/apply", ["replication.applied", "replication.apply.failed"], "replication-apply")
        rres = ev["data"]["result"]
        rep_a, rep_b = rres.get("removals_a", []), rres.get("removals_b", [])
        check("7b apply: groups created, nothing failed", GROUP in rres.get("groups_created", []) and not rres.get("error"),
              rres.get("error") or ", ".join(rres.get("groups_created", [])))
        for attempt in range(30):
            ev = step(run1, "/replication/verify", ["replication.verified", "replication.verify.failed"], "replication-verify-%d" % attempt)
            ver = ev["data"]["verification"]
            if all(x["verdict"] == "replicating" for x in ver["groups"]) or attempt == 29:
                break
            time.sleep(20)
        check("7b verify: every group replicating, links Up", ver["links_ok"] and all(x["verdict"] == "replicating" for x in ver["groups"]),
              "; ".join("%s %s %s" % (x["group"], x["verdict"], x["detail"]) for x in ver["groups"]))
        for label, c, name in (("D22U27", p, GROUP), ("E18U31", s, GROUP + ".r188150")):
            role, st = fl.role_status(c, name)
            want = "Primary" if label == "D22U27" else "Secondary"
            check("7b %s: %s is %s/Started" % (label, name, want), (role, st) == (want, "Started"), "%s/%s" % (role, st))

        fl.banner("Run 2: rerun, same sheet")
        run2 = new_run(sheet, "CUSTOM", ["replicate"])
        ev = step(run2, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "rerun-preview")
        creates = [a for a in ev["data"]["plan"]["actions"] if a["state"] == "create"]
        check("7c rerun: every row exists, 0 to create", not creates, "; ".join("%s %s" % (a["kind"], a["name"]) for a in creates))
        snap = fl.run(p, "showrcopy groups " + GROUP)
        status, resp = api("POST", "/runs/%s/replication/apply" % run2, {})
        evidence("rerun-apply.txt", "HTTP %s %s" % (status, resp))
        check("7c rerun: apply refused, nothing to create", status == 409 and "nothing to create" in str(resp), "HTTP %s %s" % (status, resp))
        check("7c rerun: showrcopy groups unchanged", fl.run(p, "showrcopy groups " + GROUP).split("\n")[:4] == snap.split("\n")[:4])

        fl.banner("Run 1: failover test, verify, as-built")
        ev = step(run1, "/replication/failover-test", ["failover.completed", "failover.failed"], "failover", body={})
        rec = ev["data"]["record"]
        check("7d failover test passed, group back to normal", rec["result"] == "passed",
              "failover %ss, synced back %ss; %s" % (rec.get("time_to_failover_s"), rec.get("time_to_synced_s"), rec.get("error") or ""))
        ev = step(run1, "/verify", ["verify.completed", "verify.failed"], "verify")
        check("verify ran", ev["event_type"] == "verify.completed", ev["message"][:160])
        ev = step(run1, "/asbuilt", ["asbuilt.generated", "asbuilt.failed"], "asbuilt")
        text = docx_text(run1)
        evidence("asbuilt-text.txt", text)
        for needle in (VOL, VVSET, HOSTSET, "Replication configured in this run", GROUP, "Failover test", "Result: Passed.",
                       "To remove what this run created", "Link check", "within HPE's limit"):
            check("7f as-built names '%s'" % needle, needle in text)
        for line in rep_a[:1] + rep_b[:1]:
            check("7f as-built carries the removal line '%s'" % line, line in text)
    except Exception as exc:  # noqa: BLE001
        check("stopped: %s" % exc, False)
        evidence("error.txt", traceback.format_exc())

    fl.banner("7g Cleanup: the runs' own removal sets over SSH")
    p.close(), s.close()
    p, s = fl.ssh(P_HOST, ARRAY_PW), fl.ssh(S_HOST, ARRAY_PW)
    log = []
    order = {"vlun": 0, "vvset": 1, "volume": 2, "hostset": 3, "host": 4}
    for label, c, lines in (("D22U27", p, rep_a), ("E18U31", s, rep_b),
                            ("D22U27", p, [r["command"] for r in sorted(storage_removals, key=lambda r: order.get(r["kind"], 9))])):
        for cmd in lines:
            answer = fl.run(c, cmd).strip()
            log.append("[%s] $ %s\n%s" % (label, cmd, answer))
            print("  [%s] $ %s  -> %s" % (label, cmd, answer.splitlines()[-1] if answer else "(no output)"))
    evidence("cleanup.txt", "\n".join(log))
    left = leftovers(p, s)
    check("7g no zz_rc_* object left on either array", not left, "; ".join(left))
    after = six_groups(p, s)
    evidence("groups-after.json", after)
    check("7g the lab's own groups are as they were", after == before,
          "; ".join("%s %s->%s" % (k, before.get(k), after.get(k)) for k in sorted(set(before) | set(after)) if before.get(k) != after.get(k)))
    p.close(), s.close()


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
            fl.save("report.txt", "\n".join(RESULTS + ["", "%d PASS, %d FAIL" % (len(RESULTS) - fails, fails)]))
            fl.banner("%d PASS, %d FAIL. Send me %s" % (len(RESULTS) - fails, fails, shutil.make_archive(OUT, "zip", OUT)))
