"""BL-45 and BL-46 live check: a provisioning apply that fails half-way keeps the commands to undo what
it made, and the Console refuses `showtarget -rescan`. Removes everything it created at the end. No
prompts. Needs both fixes: run it from a branch that has BL-45 and BL-46.

    python lab\\failed_apply_lab.py                     (jump box: D22U27 and ESX1, lab passwords from .env)
    FA_SHEET=<workbook> FA_HOST=<host> python lab/failed_apply_lab.py
                                     (anywhere the array is reachable, the app already running: the array,
                                      vCenter, switches and their passwords come from that initialisation
                                      workbook, read by the app's parser and never printed; FA_HOST is a
                                      host that already exists on the array)

1. checks the array has no zz_bl45_* objects (stops before anything if it has)
2. restarts the app on the latest code (Windows only); composes a Provision only run: host set
   zz_bl45_hs (the host: when the array does not have it yet the apply makes it, and its removal set
   must remove it again) and two thin volumes in zz_bl45_vvs: zz_bl45_vol01 (1 GiB) and zz_bl45_vol02 (1 PiB, which
   no array accepts, so the apply stops there). No export, so no host ever sees a volume.
3. in the browser, on the Provision storage page: Build plan, tick, Create. Expects the apply to stop
   at zz_bl45_vol02 with the host set and zz_bl45_vol01 made, and a removal set of exactly those two.
   Screenshots of the failed state at 1366 and 1080 wide. Then Rebuild plan: the made objects read
   Exists, the run's removal set is still on the page, and the approval tick is clear.
4. in the Console pane: types `showtarget -rescan` (must be refused, nothing sent to the array); over
   the API, `showtarget` still runs and the refusal is in the command log
5. the as-built: the provisioning section carries the error and the removal lines
6. runs the failed apply's own removal set over SSH and checks nothing zz_bl45_* is left
Writes PASS/FAIL lines to report.txt; screenshots and evidence go in ~\\Downloads\\failed_apply.zip.
"""
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

BASE = os.environ.get("RCIP_LAB_DIR") or os.path.join(os.path.expanduser("~"), "Downloads")
OUT = os.path.join(BASE, "failed_apply")
fl.OUT = OUT


def sheet_targets(path):
    """The array, vCenter and switches with their passwords, from an initialisation workbook read by the
    app's own parser. The passwords go to the local app only; nothing here prints them."""
    from alletra_onboard.application.platform.init_sheet import parse_workbook_bytes
    from alletra_onboard.domain.workflow import RunMode

    with open(path, "rb") as f:
        parsed = parse_workbook_bytes(f.read(), mode=RunMode.PROVISION_ONLY)
    intent, net = parsed.provisioning_intent, parsed.work_item.network
    targets = {}
    for prefix, creds in (("prov_array", intent.array), ("prov_vcenter", intent.vcenter),
                          ("prov_sw1", intent.switch_f1), ("prov_sw2", intent.switch_f2)):
        targets.update({prefix + "_host": creds.host, prefix + "_user": creds.username,
                        prefix + "_password": creds.password.get_secret_value()})
    network = {"mask": net.mask, "gateway": net.gateway, "dns1": (net.dns or ["not-used"])[0], "ntp": net.ntp,
               "timezone": net.timezone}
    return parsed.work_item.serial_number, network, targets


if os.environ.get("FA_SHEET"):
    SERIAL, NETWORK, TARGETS = sheet_targets(os.environ["FA_SHEET"])
else:
    _array_pw, _lab_pw = fl.lab_secret("LAB_ARRAY_PW"), fl.lab_secret("LAB_DEFAULT_PW")
    SERIAL = "CZ2D320BT1"
    NETWORK = {"mask": "255.255.248.0", "gateway": "10.64.127.254", "dns1": "10.64.122.1", "ntp": "not-used",
               "timezone": "Asia/Kolkata"}
    TARGETS = {
        "prov_array_host": "10.64.122.99", "prov_array_user": "3paradm", "prov_array_password": _array_pw,
        "prov_vcenter_host": "10.54.154.226", "prov_vcenter_user": "administrator@vsphere.local",
        "prov_vcenter_password": _lab_pw,
        # D22U27's own F1 switch runs FOS 7.0.2c and refuses the SSH client; any switch of the fabric reads it
        "prov_sw1_host": "10.64.122.146", "prov_sw1_user": "admin", "prov_sw1_password": _lab_pw,
        "prov_sw2_host": "10.64.127.244", "prov_sw2_user": "admin", "prov_sw2_password": _lab_pw,
    }
P_HOST, ARRAY_PW = TARGETS["prov_array_host"], TARGETS["prov_array_password"]
HOST = os.environ.get("FA_HOST") or "ESX1"
PREFIX = "zz_bl45"
VOL1, VOL2, VVSET, HOSTSET = PREFIX + "_vol01", PREFIX + "_vol02", PREFIX + "_vvs", PREFIX + "_hs"
TOO_BIG_GIB = 1024 * 1024          # 1 PiB thin: above any array's volume size limit
# What the apply makes before it stops, and its undo in paste order. The host joins both when the plan
# says the array does not have it yet (rack13, 2026-11-16: it did not).
EXPECTED_MADE = ["hostset " + HOSTSET, "volume " + VOL1]
EXPECTED_REMOVALS = ["removevv -f " + VOL1, "removehostset -f " + HOSTSET]
CEILING_S = 15 * 60
RESULTS = []
BAD = re.compile(r"\bundefined\b|\bNaN\b|\[object Object\]")
REMOVAL_ORDER = {"vlun": 0, "vvset": 1, "volume": 2, "hostset": 3, "host": 4}
REFUSED_START = "The console runs the tool's read-only commands"


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


def api_step(run_id, path, done, name, body=None):
    since = len(events(run_id))
    status, resp = api("POST", "/runs/%s%s" % (run_id, path), body or {})
    if status >= 300:
        raise RuntimeError("POST %s -> HTTP %s: %s" % (path, status, resp))
    ev = wait_event(run_id, since, done)
    if ev is None:
        raise RuntimeError("%s: nothing within %d min" % (path, CEILING_S // 60))
    fl.save("api-%s.json" % name, json.dumps(ev, indent=2))
    return ev


def made_host():
    """The plan said the array did not have the host, so the run made it and the cleanup removes it."""
    return ("host " + HOST) in EXPECTED_MADE


def leftovers(c):
    def ours(x):
        return x.startswith((PREFIX, "set:" + PREFIX))

    reads = [(cmd % PREFIX, ours) for cmd in ("showvv %s*", "showvvset %s*", "showhostset %s*", "showvlun -t -v %s*")]
    if made_host():
        reads.append(("showhost " + HOST, lambda x: x == HOST))
    found = []
    for cmd, mine in reads:
        for line in fl.run(c, cmd).splitlines():
            hit = next((x for x in line.split() if mine(x)), None)
            if hit and not line.lower().startswith(("error", "no ")):
                found.append("%s (%s)" % (hit, cmd.split()[0]))
    return sorted(set(found))


def compose():
    body = {
        "init": {
            "gl_client_id": "not-used", "gl_client_secret": "not-used", "gl_token_url": "https://not-used",
            "serial_number": SERIAL, "part_number": "not-used", "subscription_key": "not-used",
            "service_catalog_region_id": "ap-northeast", "dscc_region_code": "jp1", "mgmt_ipv4": P_HOST, **NETWORK,
            "contact_first_name": "Sai", "contact_last_name": "Roopesh", "contact_language": "English",
            "contact_company": "HPE", "contact_phone": "0", "contact_email": "not-used@hpe.com",
            "dscc_system_name": "lab-array", "dscc_country": "India",
            "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab failed apply check",
        },
        "targets": TARGETS,
        "volumes": [{"name": VOL1, "size_gib": "1", "provisioning_type": "tpvv", "cpg": "SSD_r6", "vvset": VVSET},
                    {"name": VOL2, "size_gib": str(TOO_BIG_GIB), "provisioning_type": "tpvv", "cpg": "SSD_r6", "vvset": VVSET}],
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


def command_log(run_id):
    entries = api("GET", "/runs/%s/console/log" % run_id)[1]
    entries = entries.get("commands", []) if isinstance(entries, dict) else []
    fl.save("commands.json", json.dumps(entries, indent=2))
    return entries


def browser(pw):
    try:
        return pw.chromium.launch()
    except Exception:  # noqa: BLE001 - no bundled Chromium: Edge is always there on Windows, Chrome usually elsewhere
        return pw.chromium.launch(channel="msedge" if os.name == "nt" else "chrome")


def drive(run_id):
    """The Provision storage page and the Console pane, pressed like an operator would.
    Returns the storage.apply.failed (or storage.applied) event, or None."""
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

        def tick_label():
            # the refusal notice repeats the sentence, so aim at the checkbox's own label
            return page.locator("label", has_text="I have reviewed this plan").first

        # A reopened run makes every step clickable in the rail. Provision storage is opened from there:
        # zoning offers "Continue with" only when a host is zoned, and this check exports nothing.
        rail.get_by_text(re.compile(r"^Provision storage$", re.I)).first.click(timeout=10000)
        page.wait_for_timeout(1500)
        shot("01-no-plan")

        since = len(events(run_id))
        press("Build plan")
        ev = wait_event(run_id, since, ["storage.previewed", "storage.preview.failed"])
        fl.save("api-storage-preview.json", json.dumps(ev, indent=2))
        plan = (ev or {}).get("data", {}).get("plan") or {}
        rows = {(a["kind"], a["name"]): a["state"] for a in plan.get("actions", [])}
        mine = {k: v for k, v in rows.items() if k[1].startswith(PREFIX)}
        check("Build plan: host set, two volumes and the VV set are 'create', 0 blockers",
              ev is not None and ev["event_type"] == "storage.previewed" and len(mine) == 4
              and all(v == "create" for v in mine.values()) and not plan.get("blockers"),
              "; ".join("%s %s=%s" % (k[0], k[1], v) for k, v in rows.items()) + " | " + "; ".join(plan.get("blockers", [])))
        if not ev or plan.get("blockers") or ev["event_type"] != "storage.previewed":
            b.close()
            return None
        if rows.get(("host", HOST)) == "create":
            EXPECTED_MADE.insert(0, "host " + HOST)
            EXPECTED_REMOVALS.append("removehost " + HOST)
        print("  the plan %s %s, so the apply should make: %s" % (
            "creates" if rows.get(("host", HOST)) == "create" else "keeps", HOST, ", ".join(EXPECTED_MADE)))
        until("Review the plan, then approve creation")
        shot("02-plan")

        tick_label().click(timeout=10000)
        since = len(events(run_id))
        press("Create storage objects")
        applied = wait_event(run_id, since, ["storage.applied", "storage.apply.failed"])
        fl.save("api-storage-apply.json", json.dumps(applied, indent=2))
        res = (applied or {}).get("data", {}).get("result") or {}
        made = sorted("%s %s" % (o["kind"], o["name"]) for o in res.get("outcomes", []) if o["status"] == "created")
        removals = [r["command"] for r in res.get("removals", [])]
        check("Create: the apply stopped, as planned (event storage.apply.failed)",
              applied is not None and applied["event_type"] == "storage.apply.failed", (applied or {}).get("message", "no answer")[:240])
        if not applied or applied["event_type"] != "storage.apply.failed":
            shot("03-did-not-fail")
            b.close()
            return applied
        check("the error names the object it stopped at (%s)" % VOL2,
              (res.get("error") or "").startswith("Stopped while creating volume %s: " % VOL2), (res.get("error") or "")[:240])
        check("what was made before it stopped is what the plan said (%s)" % ", ".join(EXPECTED_MADE),
              made == sorted(EXPECTED_MADE), ", ".join(made) or "none")
        check("the failed apply's removal set is exactly that, in paste order",
              removals == EXPECTED_REMOVALS, " | ".join(removals) or "empty")
        sent = [e.get("command", "") for e in command_log(run_id) if e.get("write")]
        ours = (PREFIX, '"%s"' % HOST) if made_host() else (PREFIX,)
        check("every write this run sent names a %s object%s" % (PREFIX, " or the new host " + HOST if len(ours) > 1 else ""),
              sent and all(any(name in c for name in ours) for c in sent), "%d write(s): %s" % (len(sent), "; ".join(sent)[:400]))

        until("Creation reported an error")
        text = shot("03-failed-1366")
        page_ok("Provision storage, failed apply", text, "Creation reported an error", "Stopped while creating volume " + VOL2,
                "%d objects were created before it stopped" % len(EXPECTED_MADE), "Removal command set", *EXPECTED_REMOVALS)
        check("the footer offers Rebuild plan, not Create",
              footer.get_by_role("button", name=re.compile(r"^Rebuild plan$")).count() == 1
              and footer.get_by_role("button", name=re.compile(r"^Create storage objects$")).count() == 0)
        page.set_viewport_size({"width": 1080, "height": 720})
        shot("04-failed-1080")
        page.set_viewport_size({"width": 1366, "height": 768})

        since = len(events(run_id))
        press("Rebuild plan")
        ev = wait_event(run_id, since, ["storage.previewed", "storage.preview.failed"])
        fl.save("api-storage-preview-2.json", json.dumps(ev, indent=2))
        plan = (ev or {}).get("data", {}).get("plan") or {}
        rows = {(a["kind"], a["name"]): a["state"] for a in plan.get("actions", [])}
        check("Rebuild plan: what the failed apply made now reads Exists, the rest Create",
              rows.get(("hostset", HOSTSET)) == "exists" and rows.get(("volume", VOL1)) == "exists"
              and rows.get(("volume", VOL2)) == "create",
              "; ".join("%s %s=%s" % (k[0], k[1], v) for k, v in rows.items() if k[1].startswith(PREFIX)))
        until("Undo what this run created")
        check("the approval tick is clear on the new plan", not tick_label().locator("input[type=checkbox]").first.is_checked())
        page.get_by_text("Undo what this run created").first.click(timeout=10000)
        text = shot("05-rebuilt-undo-open")
        page_ok("Provision storage, plan rebuilt after the failure", text, "Undo what this run created", *EXPECTED_REMOVALS)

        # BL-46: the Console prompt, typed like an operator would
        page.get_by_role("button", name=re.compile(r"Console \(\d+ command")).first.click(timeout=10000)
        before = len(command_log(run_id))
        box = page.get_by_label("Read-only command").first
        box.fill("showtarget -rescan")
        page.get_by_role("button", name=re.compile(r"^Run$")).first.click(timeout=10000)
        page.wait_for_timeout(3000)
        text = shot("06-console-rescan-refused", full=False)
        check("Console: `showtarget -rescan` is refused on screen", REFUSED_START in text)
        new = command_log(run_id)[before:]
        check("Console: the refusal is in the command log and nothing reached the array",
              len(new) == 1 and new[0].get("ok") is False and "showtarget -rescan" in new[0].get("result", "")
              and new[0].get("result", "").endswith("(console)"),
              json.dumps([{k: e.get(k) for k in ("command", "ok", "result")} for e in new])[:400])
        check("no script error in the browser", not errors, " | ".join(errors[:3]))
        b.close()
    return applied


def console_api(run_id):
    status, r = api("POST", "/runs/%s/console" % run_id, {"command": "showtarget -rescan", "target": "array"})
    fl.save("console-showtarget-rescan.json", json.dumps(r, indent=2) if isinstance(r, dict) else str(r))
    check("Console API: `showtarget -rescan` refused", status == 200 and isinstance(r, dict) and r.get("refused") is True, str(r)[:200])
    status, r = api("POST", "/runs/%s/console" % run_id, {"command": "showtarget", "target": "array"})
    fl.save("console-showtarget.json", json.dumps(r, indent=2) if isinstance(r, dict) else str(r))
    check("Console API: `showtarget` still runs", status == 200 and isinstance(r, dict) and r.get("ok") is True
          and r.get("refused") is False, str(r)[:200])


def asbuilt(run_id):
    ev = api_step(run_id, "/asbuilt", ["asbuilt.generated", "asbuilt.failed"], "asbuilt")
    doc = ""
    if ev["event_type"] == "asbuilt.generated":
        data = fl.get("/runs/%s/asbuilt/download" % run_id)
        with open(os.path.join(OUT, "asbuilt.docx"), "wb") as f:
            f.write(data)
        xml = zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode("utf-8")
        doc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", xml.replace("</w:p>", "\n")))
        fl.save("asbuilt-text.txt", doc)
    check("as-built: the provisioning section carries the error and the removal lines",
          "Provisioning stopped with an error" in doc and all(cmd in doc for cmd in EXPECTED_REMOVALS),
          ev["message"][:200])


def cleanup(applied):
    fl.banner("6. Removing what the run created")
    c = fl.ssh(P_HOST, ARRAY_PW)
    removals = ((applied or {}).get("data", {}).get("result") or {}).get("removals", [])
    lines = [r["command"] for r in sorted(removals, key=lambda r: REMOVAL_ORDER.get(r["kind"], 9))]
    log = []
    for cmd in lines:
        answer = fl.run(c, cmd).strip()
        log.append("$ %s\n%s" % (cmd, answer))
        print("  $ %s  -> %s" % (cmd, answer.splitlines()[-1] if answer else "(no output)"))
    left = leftovers(c)
    ours = "%s_*%s" % (PREFIX, " or host " + HOST if made_host() else "")
    check("the failed apply's own removal set left nothing %s on the array" % ours, bool(lines) and not left, "; ".join(left))
    if left:
        # The fixed names are ours and the array had none before: remove them in dependency order,
        # the host last and only when this run made it.
        fallback = ["removevvset -f " + VVSET, "removevv -f " + VOL2, "removevv -f " + VOL1, "removehostset -f " + HOSTSET]
        if made_host():
            fallback.append("removehost " + HOST)
        for cmd in fallback:
            answer = fl.run(c, cmd).strip()
            log.append("(fallback) $ %s\n%s" % (cmd, answer))
        left = leftovers(c)
    fl.save("cleanup.txt", "\n".join(log))
    check("no %s object left on the array" % ours, not left, "; ".join(left))
    c.close()


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    fl.banner("1. The array before (%s)" % P_HOST)
    c = fl.ssh(P_HOST, ARRAY_PW)
    left = leftovers(c)
    c.close()
    if left:
        sys.exit("%s_* objects are already on the array, nothing was done:\n  %s" % (PREFIX, "\n  ".join(left)))
    if os.name == "nt":
        fl.restart_app()
    else:
        fl.get("/app/profile")      # the app must already be running on this machine

    fl.banner("2. A Provision only run: discovery and zoning check over the API")
    run_id = compose()
    print("run " + run_id)
    fl.save("run-id.txt", run_id)
    applied = None
    try:
        ev = api_step(run_id, "/discover", ["discover.completed"], "discovery")
        hosts = {h["name"]: h for h in ev["data"]["report"].get("hosts", [])}
        check("discovery: %s is in the run and identified" % HOST, bool(hosts.get(HOST, {}).get("identified")), ev["message"][:160])
        api_step(run_id, "/zoning/preview", ["zoning.previewed", "zoning.proper"], "zoning-check")
        status, resp = api("POST", "/runs/%s/storage/builder" % run_id, {
            "host_sets": [{"name": HOSTSET, "members": [HOST]}], "exports": [], "vvsets": {VVSET: [VOL1, VOL2]}})
        fl.save("api-builder.json", json.dumps(resp, indent=2))
        if not check("the composition is saved (host set %s with %s, no export)" % (HOSTSET, HOST), status == 200, str(resp)[:200]):
            return
        fl.banner("3-4. The Provision storage page and the Console, in a headless browser")
        applied = drive(run_id)
        fl.banner("4. The Console over the API")
        console_api(run_id)
        fl.banner("5. The as-built")
        asbuilt(run_id)
    except Exception as exc:  # noqa: BLE001
        check("stopped: %s" % str(exc).splitlines()[0][:200], False)
        fl.save("error.txt", traceback.format_exc())
        if applied is None:
            done = [e for e in events(run_id) if e["event_type"] in ("storage.applied", "storage.apply.failed")]
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
