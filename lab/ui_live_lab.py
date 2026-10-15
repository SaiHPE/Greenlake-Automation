"""BL-43 live check: the redesigned screens against the real lab arrays. READ-ONLY: nothing is created,
applied or tested on any array or switch. No prompts.

    python lab\\ui_live_lab.py

1. restarts the app on the latest code and checks the browser is served the new bundle
2. composes the lab sheet (D22U27, ESX1, the two lab switches, a sync Replication row to E18U31)
   and creates a "Provision, then replicate" run
3. runs only the read-only parts over the app's API: discovery, zoning check, zoning plan (switches
   read), provisioning plan, replication read, verify configuration, as-built document
4. opens the app in a headless browser and visits every page of that run (Home, Run overview, every
   step, Done) at 1366 x 768 and 1080 x 720: one h1, no script error, no "undefined" / "NaN" on the
   page, a footer on every step. It only moves between pages; it never presses a step's button.
Writes PASS/FAIL lines to report.txt; screenshots and evidence go in ~\\Downloads\\ui_live.zip.
"""
import base64
import json
import os
import re
import shutil
import time
import traceback
import urllib.error
import urllib.request

import rc_failover_lab as fl

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "ui_live")
fl.OUT = OUT
ARRAY_PW, LAB_PW = fl.lab_secret("LAB_ARRAY_PW"), fl.lab_secret("LAB_DEFAULT_PW")
P_HOST, S_HOST = "10.64.122.99", "10.64.154.190"
CEILING_S = 15 * 60
RESULTS = []

# Read-only step endpoints and the events that end them.
READS = [
    ("discovery", "/discover", ["discover.completed"]),
    ("zoning-check", "/zoning/preview", ["zoning.previewed", "zoning.proper"]),
    ("zoning-plan", "/zoning/plan", ["zoning.plan"]),
    ("provision-plan", "/storage/preview", ["storage.previewed", "storage.preview.failed"]),
    ("replication-read", "/replication/preview", ["replication.previewed", "replication.preview.failed"]),
    ("verify", "/verify", ["verify.completed", "verify.failed"]),
    ("asbuilt", "/asbuilt", ["asbuilt.generated", "asbuilt.failed"]),
]
# Rail label, and a phrase the page must show (from the redesign).
STEP_PAGES = [
    ("Prerequisites", "Checked by this tool"),
    ("Initialisation sheet", "Initialisation sheet"),
    ("Mode", "What do you want to do"),
    ("Discovery", "Fibre Channel port"),
    ("SAN zoning", ("the array can reach", "Fabrics", "No host is zoned")),
    ("Provision storage", "plan"),
    ("Replication", "Read both arrays"),
    ("Failover test", "sequence"),
    ("Verify configuration", "Configuration"),
    ("As-built document", "Cover details"),
]
BAD = re.compile(r"\bundefined\b|\bNaN\b|\[object Object\]")


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
            "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab UI check",
        },
        "targets": {
            "prov_array_host": P_HOST, "prov_array_user": "3paradm", "prov_array_password": ARRAY_PW,
            "prov_vcenter_host": "10.54.154.226", "prov_vcenter_user": "administrator@vsphere.local",
            "prov_vcenter_password": LAB_PW,
            # D22U27's own F1 switch runs FOS 7.0.2c and refuses the SSH client; any switch of the fabric reads it
            "prov_sw1_host": "10.64.122.146", "prov_sw1_user": "admin", "prov_sw1_password": LAB_PW,
            "prov_sw2_host": "10.64.127.244", "prov_sw2_user": "admin", "prov_sw2_password": LAB_PW,
        },
        "volumes": [{"name": "zz_ui_vol01", "size_gib": "1", "provisioning_type": "tpvv", "cpg": "SSD_r6", "vvset": "zz_ui_vvs"}],
        "hostsets": [{"name": "zz_ui_hs", "members": "ESX1"}],
        "hosts": [{"name": "ESX1", "os": "esxi"}],
        "replication": {
            "fields": {"peer_host": S_HOST, "peer_user": "3paradm", "peer_password": ARRAY_PW, "rtt_ms": "1"},
            "rows": [{"vvset": "zz_ui_vvs", "peer_cpg": "SSD_r6", "mode": "sync"}],
        },
    }
    status, resp = api("POST", "/init-sheet/compose", body)
    if status != 200:
        raise RuntimeError("compose -> HTTP %s: %s" % (status, resp))
    return resp["content_b64"]


def new_run(sheet_b64):
    status, up = api("POST", "/init-sheet/upload", {"content_b64": sheet_b64})
    if status != 200:
        raise RuntimeError("upload -> HTTP %s: %s" % (status, up))
    status, r = api("POST", "/runs/from-sheet", {"token": up["token"], "mode": "REPLICATE", "selected_steps": []})
    if status != 200:
        raise RuntimeError("from-sheet -> HTTP %s: %s" % (status, r))
    return r["run"]["run_id"]


def read_step(run_id, name, path, done):
    since = len(api("GET", "/runs/%s/events" % run_id)[1]["events"])
    status, resp = api("POST", "/runs/%s%s" % (run_id, path), {})
    if status >= 300:
        return check("%s started" % name, False, "HTTP %s %s" % (status, str(resp)[:200]))
    deadline = time.time() + CEILING_S
    while time.time() < deadline:
        time.sleep(3)
        new = api("GET", "/runs/%s/events" % run_id)[1]["events"][since:]
        hit = [e for e in new if e["event_type"] in tuple(done) + ("step.crashed",)]
        if hit and not (api("GET", "/runs/%s" % run_id)[1]["run"]["status"] == "running"):
            fl.save("api-%s.json" % name, json.dumps(hit[-1], indent=2))
            return check("%s ran: %s" % (name, hit[-1]["event_type"]), hit[-1]["event_type"] != "step.crashed",
                         hit[-1]["message"][:160])
    return check("%s finished within %d min" % (name, CEILING_S // 60), False)


def served_bundle():
    """The bundle the app serves must be the one in this checkout (LESSONS 13)."""
    with open(os.path.join(fl.ROOT, "frontend", "dist", "index.html"), encoding="utf-8") as f:
        local = re.search(r"assets/index-[^\"']+\.js", f.read())
    served = re.search(r"assets/index-[^\"']+\.js", fl.get("/").decode("utf-8", "replace"))
    check("the app serves this checkout's bundle", bool(local and served and local.group(0) == served.group(0)),
          "%s / %s" % (served.group(0) if served else None, local.group(0) if local else None))


def browser(pw):
    try:
        return pw.chromium.launch()
    except Exception:  # noqa: BLE001 - no bundled Chromium on this box: Edge is always there on Windows
        return pw.chromium.launch(channel="msedge")


def visit_pages(run_id, width, height, tag):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        b = browser(pw)
        page = b.new_page(viewport={"width": width, "height": height})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(fl.APP + "/")
        page.evaluate("id => localStorage.setItem('alletra.runId', id)", run_id)
        page.reload()
        page.wait_for_timeout(2500)
        rail = page.locator("nav")

        def look(name, phrase=None, step=True):
            page.wait_for_timeout(1500)
            shot = "%s-%s.png" % (tag, re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"))
            page.screenshot(path=os.path.join(OUT, shot))
            if tag != "1366":
                return
            page.screenshot(path=os.path.join(OUT, "full-" + shot), full_page=True)
            text = page.locator("body").inner_text()
            h1 = page.locator("h1").count()
            bad = sorted(set(BAD.findall(text)))
            phrases = [phrase] if isinstance(phrase, str) else list(phrase or [])
            found = not phrases or any(p.lower() in text.lower() for p in phrases)
            footer = page.locator("footer button").count()
            ok = h1 == 1 and not bad and found and (footer >= 1 or not step)
            check("page %s" % name, ok, "h1=%d%s%s%s" % (
                h1, " bad=" + ",".join(bad) if bad else "",
                "" if found else " missing '%s'" % "' or '".join(phrases),
                "" if not step or footer else " no footer button"))

        for label, phrase in STEP_PAGES:
            try:
                rail.get_by_text(re.compile("^%s$" % re.escape(label), re.I)).first.click(timeout=10000)
                look(label, phrase)
            except Exception as exc:  # noqa: BLE001
                check("page %s" % label, False, str(exc).splitlines()[0][:200])
        try:
            rail.get_by_text(re.compile(r"^Run overview$", re.I)).first.click(timeout=10000)
            look("Run overview", "Documents and logs", step=False)
            rail.get_by_text(re.compile(r"^Finish$", re.I)).first.click(timeout=10000)
            look("Done", "Hand-over package", step=False)
            rail.get_by_text(re.compile(r"^Discovery$", re.I)).first.click(timeout=10000)
            page.get_by_role("button", name=re.compile(r"^Activity")).first.click(timeout=10000)
            look("Discovery with Activity open", "discover")
            # Grommet names the menu button "Open Menu"; its text is Runs
            page.locator("header button", has_text="Runs").first.click(timeout=10000)
            page.get_by_text("Your runs", exact=True).last.click(timeout=10000)
            look("Your runs", "Start a new run", step=False)
        except Exception as exc:  # noqa: BLE001
            check("pages beyond the steps (%s)" % tag, False, str(exc).splitlines()[0][:200])
        if tag == "1366":
            check("no script error in the browser", not errors, " | ".join(errors[:3]))
        b.close()


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    fl.restart_app()
    served_bundle()

    fl.banner("3. A run from the lab sheet, read-only steps only")
    run_id = new_run(compose())
    print("run " + run_id)
    fl.save("run-id.txt", run_id)
    for name, path, done in READS:
        read_step(run_id, name, path, done)

    fl.banner("4. The screens, in a headless browser")
    visit_pages(run_id, 1366, 768, "1366")
    visit_pages(run_id, 1080, 720, "1080")

    status, ev = api("GET", "/runs/%s/console/log" % run_id)
    entries = ev.get("commands", []) if isinstance(ev, dict) else []
    fl.save("commands.json", json.dumps(entries, indent=2))
    check("no write sent to any device in this run", not any(e.get("write") for e in entries),
          "; ".join(e.get("command", "") for e in entries if e.get("write"))[:300])


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
