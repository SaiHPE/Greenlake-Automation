"""BL-44 live check, the whole way: the app creates an iSCSI host from its iSCSI name, presents a LUN to
it and reads the path back. Removes everything it created at the end. No prompts.

    IS_SHEET=<workbook> IS_IQN=<iqn> [IS_PORT=1:4:1] python lab/iscsi_lun_lab.py

The array, vCenter and switches with their passwords come from the initialisation workbook, read by the
app's parser and never printed; the app must already be running (on Windows the script restarts it).
IS_IQN is a server's iSCSI name that is logged in to the array and that no array host owns yet; IS_PORT
is the array port it is logged in on (read from `showiscsisession` when not given).

CHANGES THE ARRAY, and removes what it made: host zz_is_eljr (that iSCSI name, OS windows, so persona
WindowsServer), host set zz_is_hs, a 1 GiB thin volume zz_is_vol01 in zz_is_vvs, and the export of
zz_is_vvs to zz_is_hs. The server sees a new disk while the LUN is presented; nothing is done on it.

1. checks the array has no zz_is_* object, that no host owns the iSCSI name and that it is logged in
   (stops before anything if not)
2. a Provision only run from a composed sheet; discovery, the zoning check (the host logged in over
   iSCSI: exports allowed), the composition, the plan: only zz_is_* creates, the host from its iSCSI
   name with persona WindowsServer, the export to the host set (stops if the plan holds anything else)
3. applies the plan with its id, reads the host and the VLUN back over SSH, plans again (all there)
4. Verify paths: the host's LUN live over the iSCSI port it is logged in on (one node only reads Partial)
5. the as-built: the provisioning section names the host, its iSCSI name and the volume
6. runs the run's own removal set over SSH and checks nothing zz_is_* is left and the name is unclaimed
Writes PASS/FAIL lines to report.txt; evidence goes in ~/Downloads/iscsi_lun.zip.
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

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "iscsi_lun")
fl.OUT = OUT
SERIAL, NETWORK, TARGETS = fl.sheet_targets(os.environ["IS_SHEET"])
P_HOST, ARRAY_PW = TARGETS["prov_array_host"], TARGETS["prov_array_password"]
IQN = os.environ["IS_IQN"].strip().lower()
PREFIX = "zz_is"
HOST, HOSTSET, VOL, VVSET = PREFIX + "_eljr", PREFIX + "_hs", PREFIX + "_vol01", PREFIX + "_vvs"
CEILING_S = 15 * 60
RESULTS = []
REMOVAL_ORDER = {"vlun": 0, "vvset": 1, "volume": 2, "hostset": 3, "host": 4}
NSP = re.compile(r"^\d+:\d+:\d+$")


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def note(what):
    line = "NOTE  " + what
    print(line)
    RESULTS.append(line)


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


def api_step(run_id, path, done, name, body=None):
    since = len(events(run_id))
    status, resp = api("POST", "/runs/%s%s" % (run_id, path), body if body is not None else {})
    if status >= 300:
        raise RuntimeError("POST %s -> HTTP %s: %s" % (path, status, resp))
    deadline = time.time() + CEILING_S
    while time.time() < deadline:
        time.sleep(2)
        hit = [e for e in events(run_id)[since:] if e["event_type"] in tuple(done) + ("step.crashed",)]
        if hit and api("GET", "/runs/%s" % run_id)[1]["run"]["status"] != "running":
            fl.save("api-%s.json" % name, json.dumps(hit[-1], indent=2))
            return hit[-1]
    raise RuntimeError("%s: nothing within %d min" % (path, CEILING_S // 60))


def writes(run_id):
    entries = api("GET", "/runs/%s/console/log" % run_id)[1]
    entries = entries.get("commands", []) if isinstance(entries, dict) else []
    fl.save("commands.json", json.dumps(entries, indent=2))
    return [e.get("command", "") for e in entries if e.get("write")]


def leftovers(c):
    found = []
    for cmd in ("showhost %s*", "showhostset %s*", "showvv %s*", "showvvset %s*", "showvlun -t -v %s*"):
        for line in fl.run(c, cmd % PREFIX).splitlines():
            hit = next((x for x in line.split() if x.startswith((PREFIX, "set:" + PREFIX))), None)
            if hit and not line.lower().startswith(("error", "no ")):
                found.append("%s (%s)" % (hit, cmd.split()[0]))
    return sorted(set(found))


def iqn_owner(c):
    """The named array host that carries the iSCSI name, '' when the name is logged in unclaimed, None when absent."""
    owner = None
    for line in fl.run(c, "showhost -d").splitlines():
        p = line.split()
        if IQN in (t.lower() for t in p):
            owner = p[1] if len(p) > 1 and p[0].isdigit() else ""
            if owner:
                return owner
    return owner


def iqn_ports(c):
    return sorted({p[0] for p in (ln.split() for ln in fl.run(c, "showiscsisession").splitlines())
                   if len(p) > 5 and NSP.match(p[0]) and p[5].lower() == IQN})


def compose():
    body = {
        "init": {
            "gl_client_id": "not-used", "gl_client_secret": "not-used", "gl_token_url": "https://not-used",
            "serial_number": SERIAL, "part_number": "not-used", "subscription_key": "not-used",
            "service_catalog_region_id": "ap-northeast", "dscc_region_code": "jp1", "mgmt_ipv4": P_HOST, **NETWORK,
            "contact_first_name": "Lab", "contact_last_name": "User", "contact_language": "English",
            "contact_company": "HPE", "contact_phone": "0", "contact_email": "not-used@hpe.com",
            "dscc_system_name": "lab-array", "dscc_country": "India",
            "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab iSCSI LUN check",
        },
        "targets": TARGETS,
        "volumes": [{"name": VOL, "size_gib": "1", "provisioning_type": "tpvv", "cpg": "SSD_r6", "vvset": VVSET}],
        "hostsets": [{"name": HOSTSET, "members": HOST}],
        "hosts": [{"name": HOST, "os": "windows", "iqn": IQN}],
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


def rows_of(plan):
    return [(a["kind"], a["name"], a["state"], a.get("description", "")) for a in plan.get("actions", [])]


def run(run_id, port):
    ev = api_step(run_id, "/discover", ["discover.completed"], "discovery")
    check("discovery finished", ev["event_type"] == "discover.completed", ev["message"][:160])
    ev = api_step(run_id, "/zoning/preview", ["zoning.previewed", "zoning.proper"], "zoning-check")
    report = ev["data"].get("report", {})
    check("zoning check: %s is iSCSI, logged in on %s, exports allowed" % (HOST, port),
          port in report.get("iscsi_hosts", {}).get(HOST, []) and HOST in report.get("zoned_hosts", []),
          "iscsi_hosts=%s zoned=%s" % (json.dumps(report.get("iscsi_hosts", {})), report.get("zoned_hosts")))
    status, resp = api("POST", "/runs/%s/storage/builder" % run_id, {
        "host_sets": [{"name": HOSTSET, "members": [HOST]}],
        "exports": [{"source_kind": "vvset", "source_name": VVSET, "target_kind": "hostset", "target_name": HOSTSET, "lun": None}],
        "vvsets": {VVSET: [VOL]}})
    fl.save("api-builder.json", json.dumps(resp, indent=2))
    if not check("composition saved (host set %s with %s, export %s to it)" % (HOSTSET, HOST, VVSET), status == 200, str(resp)[:200]):
        return None

    ev = api_step(run_id, "/storage/preview", ["storage.previewed", "storage.preview.failed"], "plan")
    plan = ev["data"].get("plan", {})
    rows = rows_of(plan)
    seen = "; ".join("%s %s=%s" % r[:3] for r in rows)
    others = [r for r in rows if not (r[1].startswith(PREFIX) and r[2] == "create")]
    kinds = sorted(r[0] for r in rows)
    ok = check("plan: only zz_is_* creates (host, host set, volume, volume set, export), no blockers",
               not others and kinds == ["host", "hostset", "vlun", "volume", "vvset"] and not plan.get("blockers")
               and not plan.get("error"), seen + " | " + "; ".join(plan.get("blockers", [])) + (plan.get("error") or ""))
    host = next((r for r in rows if r[0] == "host"), None)
    check("plan: host %s made from its iSCSI name, persona WindowsServer" % HOST,
          bool(host) and IQN in host[3].lower() and "WindowsServer" in host[3], host[3] if host else "no host row")
    fl.save("plan-notes.txt", "\n".join(plan.get("notes", [])))
    if not ok:
        note("the plan holds something other than zz_is_* creates: stopped before any write")
        return None

    applied = api_step(run_id, "/storage/apply", ["storage.applied", "storage.apply.failed"], "apply",
                       body={"approved_plan": plan.get("plan_id")})
    result = applied["data"].get("result", {})
    outcomes = {(o["kind"], o["name"]): o for o in result.get("outcomes", [])}
    check("apply: every object created, no error", applied["event_type"] == "storage.applied" and not result.get("error")
          and outcomes and all(o["status"] == "created" for o in outcomes.values()),
          applied["message"][:200] + " | " + "; ".join("%s %s=%s" % (k[0], k[1], o["status"]) for k, o in outcomes.items()))
    sent = writes(run_id)
    fl.save("writes.txt", "\n".join(sent))
    create = [w for w in sent if w.startswith("POST /hosts ")]
    check("the host was made with one WSAPI call carrying the iSCSI name, persona 11 (WindowsServer), no FC WWN",
          len(create) == 1 and IQN in create[0].lower() and "FCWWNs" not in create[0] and re.search(r'"persona":\s*11\b', create[0]),
          re.sub(r"\s+", " ", create[0])[:240] if create else "none")
    check("every write named a zz_is_ object", bool(sent) and all(PREFIX + "_" in w for w in sent),
          re.sub(r"\s+", " ", " | ".join(sent))[:500])

    c = fl.ssh(P_HOST, ARRAY_PW)
    shown = fl.run(c, "showhost -d %s" % HOST)
    persona = fl.run(c, "showhost -persona %s" % HOST)
    vluns = fl.run(c, "showvlun -a -v %s" % VOL)
    templates = fl.run(c, "showvlun -t -v %s" % VOL)
    c.close()
    fl.save("readback.txt", "# showhost -d %s\n%s\n# showhost -persona %s\n%s\n# showvlun -a -v %s\n%s\n# showvlun -t -v %s\n%s"
            % (HOST, shown, HOST, persona, VOL, vluns, VOL, templates))
    check("the array lists %s with the iSCSI name, logged in on %s" % (HOST, port),
          any(HOST in ln and IQN in ln.lower() and port in ln for ln in shown.splitlines()), shown.strip()[-240:])
    check("the array gave it persona WindowsServer", "WindowsServer" in persona, persona.strip()[-160:])
    # `showvlun -a` lists the live paths; its Status is the ALUA state: active, or nonopt for a path
    # through the node that does not own the volume (rack13, 2026-11-17: 1:4:1 read nonopt).
    live = [ln.split() for ln in vluns.splitlines() if VOL in ln and HOST in ln and port in ln]
    check("the VLUN is live for %s over %s" % (HOST, port),
          bool(live) and live[0][-2].lower() in ("active", "nonopt"), vluns.strip()[-300:])
    if live:
        note("showvlun -a status of the path over %s: %s" % (port, live[0][-2]))

    ev = api_step(run_id, "/storage/preview", ["storage.previewed", "storage.preview.failed"], "plan-again")
    again = rows_of(ev["data"].get("plan", {}))
    check("planning again: every row is already there", bool(again) and all(r[2] == "exists" for r in again),
          "; ".join("%s %s=%s" % r[:3] for r in again))

    ev = api_step(run_id, "/storage/verify-paths", ["storage.paths.verified", "storage.paths.failed"], "paths")
    ver = ev["data"].get("verification") or {}
    ph = next((h for h in ver.get("hosts", []) if h["host"] == HOST), None)
    seen = json.dumps({k: ph.get(k) for k in ("verdict", "lun_count", "paths_per_lun", "hbas_with_paths", "detail")}) if ph else ev["message"]
    check("Verify paths: %s has its LUN live over iSCSI on %s" % (HOST, port),
          bool(ph) and ph["verdict"] in ("live", "partial") and ph.get("lun_count", 0) >= 1 and port in ph.get("detail", ""), seen)
    if ph:
        note("Verify paths verdict for %s: %s (%s)" % (HOST, ph["verdict"], ph.get("detail", "")))
    return applied


def winrm_read():
    """A read over WinRM of what the server sees, only when the workbook holds a login for it."""
    from alletra_onboard.application.platform.init_sheet import parse_workbook_bytes
    from alletra_onboard.domain.workflow import RunMode

    with open(os.environ["IS_SHEET"], "rb") as f:
        hosts = parse_workbook_bytes(f.read(), mode=RunMode.PROVISION_ONLY).provisioning_intent.declared_hosts
    login = next((h for h in hosts if h.iqn.lower() == IQN and h.username and h.password), None)
    if login is None:
        note("no read on the server: the workbook holds no login for the host with that iSCSI name")


def asbuilt(run_id):
    ev = api_step(run_id, "/asbuilt", ["asbuilt.generated", "asbuilt.failed"], "asbuilt")
    doc = ""
    if ev["event_type"] == "asbuilt.generated":
        data = fl.get("/runs/%s/asbuilt/download" % run_id)
        with open(os.path.join(OUT, "asbuilt.docx"), "wb") as f:
            f.write(data)
        xml = zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode("utf-8")
        doc = re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", " ", xml.replace("</w:p>", "\n")))
        fl.save("asbuilt-text.txt", doc)
    check("as-built: it names the host, its iSCSI name, the host set, the volume and the volume set",
          all(x in doc.lower() for x in (HOST, IQN, HOSTSET, VOL, VVSET)), ev["message"][:200])


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
    if left:
        # The removal set missed something (a stopped apply): these fixed names are ours, the array had none before.
        for t in (ln.split() for ln in fl.run(c, "showvlun -t -v %s" % VOL).splitlines()):
            if len(t) > 2 and t[1] == VOL:
                log.append("(fallback) $ removevlun -f %s %s %s\n%s" % (VOL, t[0], t[2], fl.run(c, "removevlun -f %s %s %s" % (VOL, t[0], t[2]))))
        for cmd in ("removevvset -f " + VVSET, "removevv -f " + VOL, "removehostset -f " + HOSTSET, "removehost " + HOST):
            log.append("(fallback) $ %s\n%s" % (cmd, fl.run(c, cmd).strip()))
        left = leftovers(c)
    owner = iqn_owner(c)
    fl.save("cleanup.txt", "\n".join(log))
    check("the run's removal set was run (%d commands)" % len(lines), bool(lines) or applied is None, " | ".join(lines))
    check("no zz_is_* object left on the array", not left, "; ".join(left))
    check("the iSCSI name is unclaimed again", not owner, "owned by %s" % owner if owner else "")
    c.close()


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    fl.banner("1. The array before (%s)" % P_HOST)
    c = fl.ssh(P_HOST, ARRAY_PW)
    left, owner, ports = leftovers(c), iqn_owner(c), iqn_ports(c)
    fl.save("before.txt", "# showiscsisession\n%s" % fl.run(c, "showiscsisession"))
    c.close()
    if left:
        sys.exit("%s_* objects are already on the array, nothing was done:\n  %s" % (PREFIX, "\n  ".join(left)))
    if owner:
        sys.exit("The iSCSI name is already on host %s, nothing was done." % owner)
    port = os.environ.get("IS_PORT") or (ports[0] if ports else "")
    if port not in ports:
        sys.exit("The iSCSI name is not logged in on %s (sessions on: %s), nothing was done." % (port or "any port", ", ".join(ports) or "none"))
    print("logged in on %s; unclaimed" % ", ".join(ports))
    if os.name == "nt":
        fl.restart_app()
    else:
        fl.get("/app/profile")      # the app must already be running on this machine

    fl.banner("2-5. A Provision only run: discovery, zoning check, plan, apply, paths, as-built")
    run_id = compose()
    print("run " + run_id)
    fl.save("run-id.txt", run_id)
    applied = None
    try:
        applied = run(run_id, port)
        if applied:
            winrm_read()
            asbuilt(run_id)
    except Exception as exc:  # noqa: BLE001
        check("stopped: %s" % str(exc).splitlines()[0][:200], False)
        fl.save("error.txt", traceback.format_exc())
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
            passes = sum(1 for r in RESULTS if r.startswith("PASS"))
            fails = sum(1 for r in RESULTS if r.startswith("FAIL"))
            fl.save("report.txt", "\n".join(RESULTS + ["", "%d PASS, %d FAIL" % (passes, fails)]))
            fl.banner("%d PASS, %d FAIL. Send me %s" % (passes, fails, shutil.make_archive(OUT, "zip", OUT)))
