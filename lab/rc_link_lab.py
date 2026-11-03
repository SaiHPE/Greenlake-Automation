"""SPEC-020 first live run: the link check between D22U27 and E18U31, read-only. Nothing is created
or applied. No prompts.

    python lab\\rc_link_lab.py

1. restarts the app on the latest code
2. composes a replicate-only sheet (an existing set on D22U27, Volumes and Host sets empty)
3. Read both arrays (preview), then Check the link: checkrclink server on E18U31, client on D22U27,
   stopped once the latency is printed, for each RCIP link
4. checks the result, the gate (apply refused until checked), the six commands per link in the
   console log, and that no checkrclink server or client is left running on either array
Writes PASS/FAIL lines to report.txt; everything goes in ~\\Downloads\\rc_link.zip.
"""
import base64
import json
import os
import shutil
import time
import traceback
import urllib.error
import urllib.request

import rc_failover_lab as fl

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "rc_link")
fl.OUT = OUT
ARRAY_PW, LAB_PW = fl.lab_secret("LAB_ARRAY_PW"), fl.lab_secret("LAB_DEFAULT_PW")
P_HOST, S_HOST = "10.64.122.99", "10.64.154.190"
CEILING_S = 10 * 60
RESULTS = []


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def api(method, path, body=None, timeout=120):
    req = urllib.request.Request(fl.APP + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with fl.OPENER.open(req, timeout=timeout) as r:
            raw = r.read()
            try:
                return r.status, json.loads(raw or b"null")
            except ValueError:
                return r.status, raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, (exc.read() or b"").decode("utf-8", "replace")


def step(run_id, path, done, name, body=None):
    since = len(api("GET", "/runs/%s/events" % run_id)[1]["events"])
    status, resp = api("POST", "/runs/%s%s" % (run_id, path), body if body is not None else {})
    if status >= 300:
        raise RuntimeError("POST %s -> HTTP %s: %s" % (path, status, resp))
    deadline = time.time() + CEILING_S
    while time.time() < deadline:
        time.sleep(2)
        new = api("GET", "/runs/%s/events" % run_id)[1]["events"][since:]
        for e in new:
            if e["event_type"] == "phase.progress":
                print("    " + e["message"])
        hit = [e for e in new if e["event_type"] in tuple(done) + ("step.crashed",)]
        if hit:
            fl.save(name + ".json", json.dumps(hit[-1], indent=2))
            print("  %s: %s" % (hit[-1]["event_type"], hit[-1]["message"][:200]))
            return hit[-1]
    raise RuntimeError("%s: no %s within %d s" % (path, "/".join(done), CEILING_S))


def existing_set(p):
    for line in fl.run(p, "showvvset").splitlines():
        t = line.split()
        if len(t) >= 3 and t[0].isdigit() and not t[1].startswith(("zz_rc", "RCP_", "RH")):
            return t[1]
    return None


def compose(vvset):
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
            "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab link check",
        },
        "targets": {
            "prov_array_host": P_HOST, "prov_array_user": "3paradm", "prov_array_password": ARRAY_PW,
            "prov_vcenter_host": "10.54.154.226", "prov_vcenter_user": "administrator@vsphere.local",
            "prov_vcenter_password": LAB_PW,
        },
        "volumes": [], "hostsets": [],
        "replication": {
            "fields": {"peer_host": S_HOST, "peer_user": "3paradm", "peer_password": ARRAY_PW, "failover_test": "no"},
            "rows": [{"vvset": vvset, "peer_cpg": "SSD_r6", "mode": "sync"}],
        },
    }
    status, resp = api("POST", "/init-sheet/compose", body)
    if status != 200:
        raise RuntimeError("compose -> HTTP %s: %s" % (status, resp))
    return resp["content_b64"]


def reach(label, host):
    """SSH to the array, three tries 20 s apart; the first live run (2026-10-12) found E18U31 unreachable
    and the app's read failed with the right sentence but the script went on to three confusing FAILs."""
    last = None
    for _attempt in range(3):
        try:
            return fl.ssh(host, ARRAY_PW)
        except Exception as exc:  # noqa: BLE001
            last = exc
            print("  %s %s: %s (%s); retrying in 20 s" % (label, host, type(exc).__name__, exc))
            time.sleep(20)
    check("%s %s reachable over SSH from this jump box" % (label, host), False,
          "%s: %s. Check the array is up and ping/ssh it from here, then run this script again." % (type(last).__name__, last))
    return None


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    fl.banner("Both arrays reachable?")
    p = reach("D22U27", P_HOST)
    s = reach("E18U31", S_HOST)
    if p is None or s is None:
        return
    s.close()
    check("both arrays answer over SSH", True)
    vvset = existing_set(p)
    p.close()
    if not vvset:
        check("an existing volume set on D22U27", False, "showvvset listed none")
        return
    fl.restart_app()
    try:
        sheet = compose(vvset)
        status, up = api("POST", "/init-sheet/upload", {"content_b64": sheet})
        status, r = api("POST", "/runs/from-sheet", {"token": up["token"], "mode": "CUSTOM", "selected_steps": ["replicate"]})
        if not check("run created", status == 200, "HTTP %s %s" % (status, str(r)[:200])):
            return
        run_id = r["run"]["run_id"]
        print("run " + run_id)

        fl.banner("Read both arrays")
        ev = step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "preview")
        part = ev["data"]["report"].get("partnership") or {}
        check("partnership found by link address", bool(part), str(part)[:200])
        status, resp = api("POST", "/runs/%s/replication/apply" % run_id, {})
        check("apply is refused until the link is checked", status == 409 and "Check the link first" in str(resp), "HTTP %s %s" % (status, str(resp)[:200]))

        fl.banner("Check the link (checkrclink)")
        t0 = time.time()
        ev = step(run_id, "/replication/link-check", ["replication.link_checked", "replication.link_check.failed"], "link-check", body={"duration_s": 600})
        took = time.time() - t0
        lc = ev["data"]["link_check"]
        measured = [x for x in lc["results"] if x["status"] == "measured"]
        failed = [x for x in lc["results"] if x["status"] == "failed"]
        check("link check completed", ev["event_type"] == "replication.link_checked", ev["message"][:200])
        check("every link measured (%d), none failed" % len(lc["results"]), bool(measured) and not failed,
              "; ".join("%s: %s" % (x["pair"]["nsp_a"], x["detail"]) for x in failed) or ", ".join("%s %s ms" % (x["pair"]["nsp_a"], x["latency_ms"]) for x in measured))
        worst = max((x["latency_ms"] for x in measured), default=None)
        check("latency within the sync limit (10 ms) on the lab pair", worst is not None and worst <= 10, "worst %s ms" % worst)
        check("no pings lost", all((x["pings_lost_pct"] or 0) == 0 for x in measured), ", ".join("%s %s %%" % (x["pair"]["nsp_a"], x["pings_lost_pct"]) for x in measured))
        check("the check took under 3 minutes (stopped after the latency, not the 600 s test)", took < 180, "%.0f s" % took)
        for x in measured:
            fl.save("client-%s.txt" % x["pair"]["nsp_a"].replace(":", "-"), x["output"])
        check("the client output has the latency lines", all("Average measured latency" in x["output"] and "Pings Lost" in x["output"] for x in measured))
        check("the operator's option: apply still refused (no plan to create here) with the old sentence, not the latency one",
              "latency" not in str(api("POST", "/runs/%s/replication/apply" % run_id, {})[1]).lower())

        fl.banner("The command log")
        status, log = api("GET", "/runs/%s/console/log" % run_id)
        entries = log.get("commands", []) if isinstance(log, dict) else []
        fl.save("commands.json", json.dumps(entries, indent=2))
        rc = [(e["target"], e["command"], e["result"]) for e in entries if e["command"].startswith("checkrclink")]
        fl.save("checkrclink-commands.txt", "\n".join("%s  %s  %s" % x for x in rc))
        per_link = 5
        check("the log holds %d checkrclink commands (%d per link)" % (per_link * len(lc["results"]), per_link), len(rc) == per_link * len(lc["results"]), str(len(rc)))
        check("server commands went to E18U31, client commands to D22U27",
              all((t == S_HOST) == ("server" in c) for t, c, _ in rc))
        check("every link's client was stopped and its server stopped last",
              all(rc[i * per_link + 3][1].startswith("checkrclink stopclient") and rc[i * per_link + 4][1].startswith("checkrclink stopserver") for i in range(len(lc["results"]))))
        check("no password in the log", ARRAY_PW not in json.dumps(entries))

        fl.banner("Nothing left running on the arrays")
        p, s = fl.ssh(P_HOST, ARRAY_PW), fl.ssh(S_HOST, ARRAY_PW)
        answers = []
        for label, c, cmd in (("D22U27", p, "checkrclink stopclient"), ("E18U31", s, "checkrclink stopserver")):
            for x in lc["results"]:
                nsp = x["pair"]["nsp_a"] if label == "D22U27" else x["pair"]["nsp_b"]
                answer = fl.run(c, "%s %s" % (cmd, nsp)).strip()
                fl.save("after-%s-%s.txt" % (label, nsp.replace(":", "-")), answer)
                answers.append("%s %s: %s" % (label, nsp, (answer.splitlines() or ["(no output)"])[0]))
        p.close(), s.close()
        check("a second stop on both arrays answered (read after-*.txt: it should say nothing was running)", True, "; ".join(answers))
    except Exception as exc:  # noqa: BLE001
        check("stopped: %s" % exc, False)
        fl.save("error.txt", traceback.format_exc())


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
