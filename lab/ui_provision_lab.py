"""BL-43 live check: the redesigned Provision storage screen creating real objects on D22U27, driven
by its own buttons in a headless browser. Removes everything it created at the end. No prompts.

    python lab\\ui_provision_lab.py

1. checks D22U27 has no zz_ui_* objects (stops before anything if it has)
2. restarts the app on the latest code; composes the lab sheet (ESX1, one 1 GiB volume in zz_ui_vvs,
   host set zz_ui_hs) and creates a "Provision only" run; discovery and the zoning check over the API
3. in the browser, on the Provision storage page: Build plan; Create without the tick (must be refused
   with a message and nothing sent); tick; Create; Verify paths; Continue; then Run overview and Finish
4. runs the run's own removal set over SSH and checks nothing zz_ui_* is left
Writes PASS/FAIL lines to report.txt; screenshots and evidence go in ~\\Downloads\\ui_provision.zip.
"""
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

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "ui_provision")
fl.OUT = OUT
ARRAY_PW, LAB_PW = fl.lab_secret("LAB_ARRAY_PW"), fl.lab_secret("LAB_DEFAULT_PW")
P_HOST = "10.64.122.99"
HOST = "ESX1"
VOL, VVSET, HOSTSET = "zz_ui_vol01", "zz_ui_vvs", "zz_ui_hs"
CEILING_S = 15 * 60
RESULTS = []
BAD = re.compile(r"\bundefined\b|\bNaN\b|\[object Object\]")
REMOVAL_ORDER = {"vlun": 0, "vvset": 1, "volume": 2, "hostset": 3, "host": 4}


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


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


def wait_event(run_id, since, done):
    deadline = time.time() + CEILING_S
    while time.time() < deadline:
        time.sleep(2)
        hit = [e for e in events(run_id)[since:] if e["event_type"] in tuple(done) + ("step.crashed",)]
        if hit and api("GET", "/runs/%s" % run_id)[1]["run"]["status"] != "running":
            return hit[-1]
    return None


def api_step(run_id, path, done, name):
    since = len(events(run_id))
    status, resp = api("POST", "/runs/%s%s" % (run_id, path), {})
    if status >= 300:
        raise RuntimeError("POST %s -> HTTP %s: %s" % (path, status, resp))
    ev = wait_event(run_id, since, done)
    if ev is None:
        raise RuntimeError("%s: nothing within %d min" % (path, CEILING_S // 60))
    fl.save("api-%s.json" % name, json.dumps(ev, indent=2))
    return ev


def leftovers(c):
    found = []
    for cmd in ("showvv zz_ui*", "showvvset zz_ui*", "showhostset zz_ui*", "showvlun -t -v zz_ui*"):
        for line in fl.run(c, cmd).splitlines():
            hit = next((x for x in line.split() if x.startswith(("zz_ui", "set:zz_ui"))), None)
            if hit and not line.lower().startswith(("error", "no ")):
                found.append("%s (%s)" % (hit, cmd.split()[0]))
    return sorted(set(found))


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
            "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab provisioning UI check",
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
    }
    status, resp = api("POST", "/init-sheet/compose", body)
    if status != 200:
        raise RuntimeError("compose -> HTTP %s: %s" % (status, resp))
    status, up = api("POST", "/init-sheet/upload", {"content_b64": resp["content_b64"]})
    if status != 200:
        raise RuntimeError("upload -> HTTP %s: %s" % (status, up))
    status, r = api("POST", "/runs/from-sheet", {"token": up["token"], "mode": "PROVISION_ONLY", "selected_steps": []})
    if status != 200:
        raise RuntimeError("from-sheet -> HTTP %s: %s" % (status, r))
    return r["run"]["run_id"]


def writes(run_id):
    entries = api("GET", "/runs/%s/console/log" % run_id)[1]
    entries = entries.get("commands", []) if isinstance(entries, dict) else []
    fl.save("commands.json", json.dumps(entries, indent=2))
    return [e.get("command", "") for e in entries if e.get("write")]


def browser(pw):
    try:
        return pw.chromium.launch()
    except Exception:  # noqa: BLE001 - no bundled Chromium on this box: Edge is always there on Windows
        return pw.chromium.launch(channel="msedge")


def drive(run_id):
    """The Provision storage page, pressed like an operator would. Returns the storage.applied event or None."""
    from playwright.sync_api import sync_playwright

    applied = None
    with sync_playwright() as pw:
        b = browser(pw)
        page = b.new_page(viewport={"width": 1366, "height": 768})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(fl.APP + "/")
        page.evaluate("id => localStorage.setItem('alletra.runId', id)", run_id)
        page.reload()
        page.wait_for_timeout(2500)
        rail = page.locator("nav")
        footer = page.locator("footer")

        def shot(name, full=True):
            page.wait_for_timeout(1200)
            page.screenshot(path=os.path.join(OUT, "%s.png" % name), full_page=full)
            return page.locator("body").inner_text()

        def page_ok(name, text, *phrases):
            bad = sorted(set(BAD.findall(text)))
            missing = [p for p in phrases if p.lower() not in text.lower()]
            h1 = page.locator("h1").count()
            return check("page %s" % name, h1 == 1 and not bad and not missing, "h1=%d%s%s" % (
                h1, " bad=" + ",".join(bad) if bad else "", " missing '%s'" % "', '".join(missing) if missing else ""))

        def press(label):
            footer.get_by_role("button", name=re.compile("^%s$" % re.escape(label))).first.click(timeout=10000)

        def until(text, seconds=120):
            page.get_by_text(text).first.wait_for(timeout=seconds * 1000)

        # A step not reached yet is not clickable in the rail: go on from SAN zoning like the operator
        rail.get_by_text(re.compile(r"^SAN zoning$", re.I)).first.click(timeout=10000)
        shot("00-zoning")
        footer.get_by_role("button", name=re.compile(r"^Continue with ")).first.click(timeout=10000)
        page.wait_for_timeout(1500)
        page_ok("Provision storage, no plan", shot("01-no-plan"), "Provision storage", "No plan yet")

        since = len(events(run_id))
        press("Build plan")
        ev = wait_event(run_id, since, ["storage.previewed", "storage.preview.failed"])
        fl.save("api-storage-preview.json", json.dumps(ev, indent=2))
        plan = (ev or {}).get("data", {}).get("plan") or {}
        rows = {(a["kind"], a["name"]): a["state"] for a in plan.get("actions", [])}
        mine = {k: v for k, v in rows.items() if k[1].startswith("zz_ui")}
        check("Build plan: volume, VV set, host set and export are 'create', 0 blockers",
              ev is not None and ev["event_type"] == "storage.previewed" and len(mine) == 4
              and all(v == "create" for v in mine.values()) and not plan.get("blockers"),
              "; ".join("%s %s=%s" % (k[0], k[1], v) for k, v in rows.items()) + " | " + "; ".join(plan.get("blockers", [])))
        if not ev or plan.get("blockers") or ev["event_type"] != "storage.previewed":
            b.close()
            return None
        until("Review the plan, then approve creation")
        text = shot("02-plan")
        page_ok("Provision storage, plan to review", text, "Review the plan", VOL, VVSET, HOSTSET, "I have reviewed this plan")

        before = len(events(run_id))
        press("Create storage objects")
        page.wait_for_timeout(2500)
        text = shot("03-create-without-tick", full=False)
        sent = [e["event_type"] for e in events(run_id)[before:]]
        check("Create without the tick is refused with a message, nothing sent",
              "Tick the box first" in text and not any(t.startswith("storage.apply") for t in sent) and not writes(run_id),
              "events after the click: %s" % (", ".join(sent) or "none"))

        # the refusal notice repeats the sentence, so aim at the checkbox's own label
        page.locator("label", has_text="I have reviewed this plan").first.click(timeout=10000)
        since = len(events(run_id))
        press("Create storage objects")
        for _ in range(15):
            page.wait_for_timeout(2000)
            if any(e["event_type"].startswith("storage.apply") for e in events(run_id)[since:]):
                break
        else:
            check("Create after the tick starts the apply", False, "no storage.apply event within 30 s")
            shot("04-create-not-sent")
            b.close()
            return None
        applied = wait_event(run_id, since, ["storage.applied", "storage.apply.failed"])
        fl.save("api-storage-apply.json", json.dumps(applied, indent=2))
        res = (applied or {}).get("data", {}).get("result") or {}
        failed = [o for o in res.get("outcomes", []) if o["status"] == "failed"]
        check("Create: the array created the objects, nothing failed",
              applied is not None and applied["event_type"] == "storage.applied" and not failed and not res.get("error"),
              (applied or {}).get("message", "no answer")[:200])
        if not applied or applied["event_type"] != "storage.applied":
            shot("04-create-failed")
            b.close()
            return applied
        until("What the array answered")
        text = shot("04-created")
        created = sum(1 for o in res["outcomes"] if o["status"] == "created")
        page_ok("Provision storage, created", text, "%d created" % created, "What the array answered", "Verify the paths next")
        sent = writes(run_id)
        check("every write this run sent names a zz_ui object", sent and all("zz_ui" in c for c in sent),
              "%d write(s): %s" % (len(sent), "; ".join(sent)[:400]))

        since = len(events(run_id))
        press("Verify paths")
        ev = wait_event(run_id, since, ["storage.paths.verified", "storage.paths.failed"])
        fl.save("api-paths.json", json.dumps(ev, indent=2))
        ver = (ev or {}).get("data", {}).get("verification") or {}
        ph = next((x for x in ver.get("hosts", []) if x["host"] == HOST), None)
        check("Verify paths: %s is live with 1 LUN on 2 or more paths" % HOST,
              bool(ph and ph["verdict"] == "live" and ph.get("lun_count", 0) >= 1 and (ph.get("paths_per_lun") or 0) >= 2),
              json.dumps({k: ph.get(k) for k in ("verdict", "lun_count", "paths_per_lun", "esxi_state", "detail")}) if ph else (ev or {}).get("message", "no answer"))
        page.wait_for_timeout(2000)
        text = shot("05-paths")
        page_ok("Provision storage, paths read back", text, "read back", HOST, "Continue to")
        page.set_viewport_size({"width": 1080, "height": 720})
        shot("06-paths-1080")
        page.set_viewport_size({"width": 1366, "height": 768})

        heading = page.locator("h1").first.inner_text()
        footer.get_by_role("button", name=re.compile(r"^Continue to ")).first.click(timeout=10000)
        page.wait_for_timeout(2000)
        moved = page.locator("h1").first.inner_text()
        check("Continue moves to the next step", moved != heading, "%s -> %s" % (heading, moved))
        shot("07-next-step")

        rail.get_by_text(re.compile(r"^Run overview$", re.I)).first.click(timeout=10000)
        page_ok("Run overview after provisioning", shot("08-overview"), "Documents and logs")
        rail.get_by_text(re.compile(r"^Finish$", re.I)).first.click(timeout=10000)
        page_ok("Done after provisioning", shot("09-done"), "Hand-over package")
        check("no script error in the browser", not errors, " | ".join(errors[:3]))
        b.close()
    return applied


def cleanup(applied):
    fl.banner("4. Removing what the run created")
    c = fl.ssh(P_HOST, ARRAY_PW)
    removals = ((applied or {}).get("data", {}).get("result") or {}).get("removals", [])
    lines = [r["command"] for r in sorted(removals, key=lambda r: REMOVAL_ORDER.get(r["kind"], 9))]
    log = []
    for cmd in lines:
        answer = fl.run(c, cmd).strip()
        log.append("$ %s\n%s" % (cmd, answer))
        print("  $ %s  -> %s" % (cmd, answer.splitlines()[-1] if answer else "(no output)"))
    left = leftovers(c)
    if left:
        # The run's removal set missed something (a stopped apply): the fixed names are ours, D22U27 had none before.
        extra = ["removevlun -f %s %s %s" % (VOL, t[0], t[2]) for t in
                 (line.split() for line in fl.run(c, "showvlun -t -v %s" % VOL).splitlines()) if len(t) > 2 and t[1] == VOL]
        extra += ["removevvset -f " + VVSET, "removevv -f " + VOL, "removehostset -f " + HOSTSET]
        for cmd in extra:
            answer = fl.run(c, cmd).strip()
            log.append("(fallback) $ %s\n%s" % (cmd, answer))
        left = leftovers(c)
    fl.save("cleanup.txt", "\n".join(log))
    check("the run's removal set was run (%d commands)" % len(lines), bool(lines) or applied is None)
    check("no zz_ui_* object left on D22U27", not left, "; ".join(left))
    c.close()


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    fl.banner("1. D22U27 before")
    c = fl.ssh(P_HOST, ARRAY_PW)
    left = leftovers(c)
    c.close()
    if left:
        sys.exit("zz_ui_* objects are already on D22U27, nothing was done:\n  " + "\n  ".join(left))
    fl.restart_app()

    fl.banner("2. A Provision only run: discovery and zoning check over the API")
    run_id = compose()
    print("run " + run_id)
    fl.save("run-id.txt", run_id)
    applied = None
    try:
        ev = api_step(run_id, "/discover", ["discover.completed"], "discovery")
        hosts = {h["name"]: h for h in ev["data"]["report"].get("hosts", [])}
        check("discovery: %s is in the run and identified" % HOST, bool(hosts.get(HOST, {}).get("identified")), ev["message"][:160])
        ev = api_step(run_id, "/zoning/preview", ["zoning.previewed", "zoning.proper"], "zoning-check")
        zoned = ev["data"].get("report", {}).get("zoned_hosts", [])
        if not check("zoning check: %s is zoned on both fabrics" % HOST, HOST in zoned, ", ".join(zoned) or "none"):
            return
        status, resp = api("POST", "/runs/%s/storage/builder" % run_id, {
            "host_sets": [{"name": HOSTSET, "members": [HOST]}],
            "exports": [{"source_kind": "vvset", "source_name": VVSET, "target_kind": "hostset", "target_name": HOSTSET, "lun": None}],
            "vvsets": {VVSET: [VOL]}})
        fl.save("api-builder.json", json.dumps(resp, indent=2))
        if not check("the composition is saved (host set %s with %s, export %s to it)" % (HOSTSET, HOST, VVSET), status == 200, str(resp)[:200]):
            return
        fl.banner("3. The Provision storage page, in a headless browser")
        applied = drive(run_id)
    except Exception as exc:  # noqa: BLE001
        check("stopped: %s" % str(exc).splitlines()[0][:200], False)
        fl.save("error.txt", traceback.format_exc())
        if applied is None:
            # The browser may have stopped after the apply: take the result from the run itself
            done = [e for e in events(run_id) if e["event_type"] == "storage.applied"]
            applied = done[-1] if done else None
    finally:
        cleanup(applied)


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
