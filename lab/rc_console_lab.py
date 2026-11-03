"""v0.17.0 live check: the Console (SPEC-019, BL-39) and a Replication row that names a volume set
already on the array. READ-ONLY on both arrays: nothing is created, nothing is applied. No prompts.

    python lab\\rc_console_lab.py

1. restarts the app on the latest code
2. composes a replicate-only sheet: Volumes and Host sets empty, two Replication rows (a set that is
   already on D22U27, and one that is not), failover test off
3. checks the Provision preset is refused and a Custom "Replication + As-built" run is created
4. console: showsys on the array and on the peer, two refusals, the live stream, Open terminal
5. replication preview (read-only): the existing set is found, the missing one gets its sentence
6. the storage preflight (WSAPI reads), the as-built with its "Commands run on the array" appendix
7. the command log: every command above, both arrays, ssh and wsapi, no password, no write
Writes PASS/FAIL lines to report.txt; everything goes in ~\\Downloads\\rc_console.zip.
An ssh window opens near the end (Open terminal); close it.
"""
import base64
import io
import json
import os
import re
import shutil
import threading
import time
import traceback
import urllib.error
import urllib.request
import zipfile

import rc_failover_lab as fl

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "rc_console")
fl.OUT = OUT
ARRAY_PW, LAB_PW = fl.lab_secret("LAB_ARRAY_PW"), fl.lab_secret("LAB_DEFAULT_PW")
P_HOST, S_HOST = "10.64.122.99", "10.64.154.190"
MISSING = "zz_rc_no_such_set"
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


def step(run_id, path, done, name):
    since = len(api("GET", "/runs/%s/events" % run_id)[1]["events"])
    status, resp = api("POST", "/runs/%s%s" % (run_id, path), {})
    if status >= 300:
        raise RuntimeError("POST %s -> HTTP %s: %s" % (path, status, resp))
    deadline = time.time() + CEILING_S
    while time.time() < deadline:
        time.sleep(2)
        new = api("GET", "/runs/%s/events" % run_id)[1]["events"][since:]
        hit = [e for e in new if e["event_type"] in tuple(done) + ("step.crashed",)]
        if hit:
            fl.save(name + ".json", json.dumps(hit[-1], indent=2))
            print("  %s: %s" % (hit[-1]["event_type"], hit[-1]["message"][:160]))
            return hit[-1]
    raise RuntimeError("%s: no %s within %d s" % (path, "/".join(done), CEILING_S))


def existing_set(p):
    """The first volume set on D22U27 that is not the tool's own."""
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
            "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab console check",
        },
        "targets": {
            "prov_array_host": P_HOST, "prov_array_user": "3paradm", "prov_array_password": ARRAY_PW,
            "prov_vcenter_host": "10.54.154.226", "prov_vcenter_user": "administrator@vsphere.local",
            "prov_vcenter_password": LAB_PW,
        },
        "volumes": [],
        "hostsets": [],
        "replication": {
            "fields": {"peer_host": S_HOST, "peer_user": "3paradm", "peer_password": ARRAY_PW, "rtt_ms": "1",
                       "failover_test": "no"},
            "rows": [{"vvset": vvset, "peer_cpg": "SSD_r6", "mode": "sync"},
                     {"vvset": MISSING, "peer_cpg": "SSD_r6", "mode": "sync"}],
        },
    }
    status, resp = api("POST", "/init-sheet/compose", body)
    if status != 200:
        raise RuntimeError("compose -> HTTP %s: %s" % (status, resp))
    with open(os.path.join(OUT, "sheet.xlsx"), "wb") as f:
        f.write(base64.b64decode(resp["content_b64"]))
    return resp["content_b64"]


def from_sheet(sheet_b64, mode, steps=None):
    status, up = api("POST", "/init-sheet/upload", {"content_b64": sheet_b64})
    if status != 200:
        return status, up
    return api("POST", "/runs/from-sheet", {"token": up["token"], "mode": mode, "selected_steps": steps or []})


def console(run_id, command, target="array"):
    status, resp = api("POST", "/runs/%s/console" % run_id, {"command": command, "target": target})
    fl.save("console-%s-%s.txt" % (target, re.sub(r"[^A-Za-z0-9]+", "_", command)[:40]),
            "HTTP %s\n%s" % (status, json.dumps(resp, indent=2) if isinstance(resp, dict) else resp))
    return status, resp if isinstance(resp, dict) else {}


def stream_sees(run_id, command):
    """Open the console SSE stream, run `command` from another thread, wait for it on the stream."""
    seen = {"hit": False}

    def later():
        time.sleep(1.5)
        console(run_id, command)

    t = threading.Thread(target=later)
    try:
        with fl.OPENER.open(fl.APP + "/runs/%s/console/stream" % run_id, timeout=30) as r:
            t.start()
            deadline = time.time() + 25
            while time.time() < deadline:
                line = r.readline().decode("utf-8", "replace")
                if line.startswith("data:") and json.loads(line[5:]).get("command") == command:
                    seen["hit"] = True
                    break
    except Exception as exc:  # noqa: BLE001
        fl.save("stream-error.txt", repr(exc))
    if t.ident:
        t.join(timeout=30)
    return seen["hit"]


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    p = fl.ssh(P_HOST, ARRAY_PW)
    vvset = existing_set(p)
    p.close()
    if not vvset:
        check("an existing volume set on D22U27 to name on the Replication tab", False, "showvvset listed none")
        return
    print("existing set on D22U27: " + vvset)
    fl.restart_app()
    try:
        fl.banner("Sheet: Volumes and Host sets empty, Replication rows only")
        sheet = compose(vvset)
        status, resp = from_sheet(sheet, "REPLICATE")
        check("the Provision preset is refused: nothing to provision", status >= 400 and "nothing to provision" in str(resp),
              "HTTP %s %s" % (status, str(resp)[:200]))
        status, resp = from_sheet(sheet, "CUSTOM", ["replicate", "asbuilt"])
        if not check("a Custom run (Replication + As-built) is created from it", status == 200, "HTTP %s %s" % (status, str(resp)[:300])):
            return
        run_id = resp["run"]["run_id"]
        print("run " + run_id)

        fl.banner("Console")
        status, resp = api("GET", "/runs/%s/console/targets" % run_id)
        targets = resp.get("targets", {}) if isinstance(resp, dict) else {}
        check("targets: the array and the peer", targets.get("array") == "3paradm@" + P_HOST
              and targets.get("peer") == "3paradm@" + S_HOST, str(resp))
        status, r = console(run_id, "showsys")
        check("showsys on the array runs and shows D22U27", status == 200 and r.get("ok") and "D22U27" in r.get("output", ""),
              "HTTP %s %s" % (status, str(r)[:200]))
        status, r = console(run_id, "showsys", "peer")
        check("showsys on the peer runs and shows E18U31", status == 200 and r.get("ok") and "E18U31" in r.get("output", ""),
              "HTTP %s %s" % (status, str(r)[:200]))
        status, r = console(run_id, "removevv %s_x" % MISSING)
        check("removevv is refused with the sentence", status == 200 and r.get("refused") and "Open terminal" in r.get("output", ""),
              "HTTP %s %s" % (status, str(r)[:200]))
        status, r = console(run_id, "showvv; removevv x")
        check("a chained command is refused", status == 200 and r.get("refused"), "HTTP %s %s" % (status, str(r)[:200]))
        check("the live stream carries a command as it runs", stream_sees(run_id, "showdate"))

        fl.banner("Replication preview (read-only)")
        ev = step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "replication-preview")
        text = json.dumps(ev["data"])
        check("preview: the existing set '%s' is found on the array" % vvset,
              ("Volume set '%s' does not exist" % vvset) not in text and vvset in text)
        check("preview: '%s' gets 'does not exist ... Create it first'" % MISSING,
              ("Volume set '%s' does not exist on AlletraMP_D22U27. Create it first" % MISSING) in text)

        fl.banner("Storage preflight (WSAPI reads) and the as-built")
        status, objs = api("GET", "/runs/%s/storage/preflight" % run_id)
        fl.save("storage-preflight.json", json.dumps(objs, indent=2) if isinstance(objs, dict) else str(objs))
        check("storage preflight read the array over WSAPI", status == 200, "HTTP %s %s" % (status, str(objs)[:200]))
        ev = step(run_id, "/asbuilt", ["asbuilt.generated", "asbuilt.failed"], "asbuilt")
        doc = ""
        if ev["event_type"] == "asbuilt.generated":
            data = fl.get("/runs/%s/asbuilt/download" % run_id)
            with open(os.path.join(OUT, "asbuilt.docx"), "wb") as f:
                f.write(data)
            xml = zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode("utf-8")
            doc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", xml.replace("</w:p>", "\n")))
            fl.save("asbuilt-text.txt", doc)
        count = re.search(r"\d+ change\(s\) and \d+ read-only command\(s\)", doc)
        check("as-built: 'Commands run on the array', 0 changes", "Commands run on the array" in doc and "0 change(s)" in doc,
              count.group(0) if count else ev["message"][:200])

        fl.banner("Open terminal (an ssh window opens; close it)")
        status, r = api("POST", "/runs/%s/console/terminal" % run_id, {"target": "array"})
        check("Open terminal launches ssh 3paradm@%s" % P_HOST, status == 200, "HTTP %s %s" % (status, str(r)[:200]))

        fl.banner("The command log")
        status, log = api("GET", "/runs/%s/console/log" % run_id)
        entries = log.get("commands", log) if isinstance(log, dict) else log
        fl.save("commands.json", json.dumps(entries, indent=2))
        txt = fl.get("/runs/%s/console/log?format=txt" % run_id).decode("utf-8", "replace")
        fl.save("commands.txt", txt)
        entries = entries if isinstance(entries, list) else []
        targets_seen = {e.get("target") for e in entries}
        transports = {e.get("transport") for e in entries}
        commands = [e.get("command", "") for e in entries]
        check("log: %d commands, both arrays" % len(entries), P_HOST in targets_seen and S_HOST in targets_seen, ", ".join(sorted(map(str, targets_seen))))
        check("log: ssh and wsapi both recorded", {"ssh", "wsapi"} <= transports, ", ".join(sorted(map(str, transports))))
        check("log: the console commands are in it, in order",
              [c for c in commands if c in ("showsys", "showdate")] [:3] == ["showsys", "showsys", "showdate"], str([c for c in commands if c in ("showsys", "showdate")]))
        check("log: the two refusals are recorded as not ok",
              sum(1 for e in entries if not e.get("ok") and e.get("command", "").startswith(("removevv", "showvv;"))) == 2)
        check("log: the WSAPI login shows no password", any(c.startswith("POST /credentials {user, password: ********}") for c in commands))
        check("log: the WSAPI logout shows no session key", not any(re.match(r"DELETE /credentials/(?!\*)", c) for c in commands))
        everything = json.dumps(entries) + txt
        check("log: no lab password anywhere", ARRAY_PW not in everything and LAB_PW not in everything)
        check("log: no write in a read-only run", not any(e.get("write") for e in entries),
              "; ".join(c for e, c in zip(entries, commands) if e.get("write")))
        check("txt download: has showsys and the refusals", "showsys" in txt and "refused: " in txt)
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
