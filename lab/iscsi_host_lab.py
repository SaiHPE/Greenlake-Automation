"""BL-44 live check: the app creates an iSCSI host on D22U27 from its iSCSI name, then removes it.

    .\\.venv\\Scripts\\python.exe lab\\iscsi_host_lab.py

CHANGES THE ARRAY, and removes what it made. On D22U27 (10.64.122.99) it creates host zz_is_linux
(iSCSI name of the lab Linux host 10.54.159.49, persona Generic-ALUA), host set zz_is_hs and a 1 GiB
thin volume zz_is_vol01 on SSD_r6. D22U27 has no iSCSI target port, so the export of zz_is_vol01 to
zz_is_hs is held back by the app's zoning gate and no VLUN is made. Nothing touches the Linux host.

1. checks D22U27 has no zz_is_* object and that no host carries that iSCSI name (stops if so)
2. restarts the app; a "Provision only" run from a sheet with the host typed by name, OS and IQN;
   discovery, the zoning check and the plan over the API
3. applies the plan, reads the host back over SSH and WSAPI, plans again (must say "exists")
4. runs the run's own removal set over SSH and checks nothing zz_is_* is left
Passwords come from .env (LAB_ARRAY_PW, LAB_DEFAULT_PW). Evidence in ~\\Downloads\\iscsi_host.zip.
"""
import json
import os
import re
import shutil
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402
import ui_provision_lab as ui  # noqa: E402

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "iscsi_host")
fl.OUT = OUT
P_HOST = ui.P_HOST
HOST, HOSTSET, VOL = "zz_is_linux", "zz_is_hs", "zz_is_vol01"
IQN = "iqn.1994-05.com.redhat:6e35c4a016a0"
NSP = re.compile(r"^\d+:\d+:\d+$")
RESULTS = ui.RESULTS
check = ui.check


def leftovers(c):
    found = []
    for cmd in ("showhost zz_is*", "showhostset zz_is*", "showvv zz_is*", "showvvset zz_is*", "showvlun -t -v zz_is*"):
        for line in fl.run(c, cmd).splitlines():
            hit = next((x for x in line.split() if x.startswith(("zz_is", "set:zz_is"))), None)
            if hit and not line.lower().startswith(("error", "no ")):
                found.append("%s (%s)" % (hit, cmd.split()[0]))
    return sorted(set(found))


def iqn_owner(c):
    for line in fl.run(c, "showhost -d").splitlines():
        p = line.split()
        if len(p) >= 6 and p[-3].lower() == IQN:
            return p[1]
    return None


def compose():
    sheet = {
        "init": {
            "gl_client_id": "not-used", "gl_client_secret": "not-used", "gl_token_url": "https://not-used",
            "serial_number": "CZ2D320BT1", "part_number": "not-used", "subscription_key": "not-used",
            "service_catalog_region_id": "ap-northeast", "dscc_region_code": "jp1",
            "mgmt_ipv4": P_HOST, "mask": "255.255.248.0", "gateway": "10.64.127.254", "dns1": "10.64.122.1",
            "ntp": "not-used", "timezone": "Asia/Kolkata",
            "contact_first_name": "Sai", "contact_last_name": "Roopesh", "contact_language": "English",
            "contact_company": "HPE", "contact_phone": "0", "contact_email": "not-used@hpe.com",
            "dscc_system_name": "AlletraMP_D22U27", "dscc_country": "India",
            "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab iSCSI host check",
        },
        "targets": {
            "prov_array_host": P_HOST, "prov_array_user": "3paradm", "prov_array_password": ui.ARRAY_PW,
            "prov_vcenter_host": "10.54.154.226", "prov_vcenter_user": "administrator@vsphere.local",
            "prov_vcenter_password": ui.LAB_PW,
            "prov_sw1_host": "10.64.122.146", "prov_sw1_user": "admin", "prov_sw1_password": ui.LAB_PW,
            "prov_sw2_host": "10.64.127.244", "prov_sw2_user": "admin", "prov_sw2_password": ui.LAB_PW,
        },
        "volumes": [{"name": VOL, "size_gib": "1", "provisioning_type": "tpvv", "cpg": "SSD_r6", "vvset": ""}],
        "hostsets": [{"name": HOSTSET, "members": HOST}],
        "hosts": [{"name": HOST, "os": "linux", "address": "10.54.159.49", "iqn": IQN}],
    }
    status, resp = ui.api("POST", "/init-sheet/compose", sheet)
    if status != 200:
        raise RuntimeError("compose -> HTTP %s: %s" % (status, resp))
    status, up = ui.api("POST", "/init-sheet/upload", {"content_b64": resp["content_b64"]})
    if status != 200:
        raise RuntimeError("upload -> HTTP %s: %s" % (status, up))
    status, r = ui.api("POST", "/runs/from-sheet", {"token": up["token"], "mode": "PROVISION_ONLY", "selected_steps": []})
    if status != 200:
        raise RuntimeError("from-sheet -> HTTP %s: %s" % (status, r))
    return r["run"]["run_id"]


def host_row(plan):
    return next((a for a in plan.get("actions", []) if a["kind"] == "host" and a["name"] == HOST), None)


def run(run_id):
    ev = ui.api_step(run_id, "/discover", ["discover.completed"], "discovery")
    check("discovery finished", ev["event_type"] == "discover.completed", ev["message"][:160])
    ev = ui.api_step(run_id, "/zoning/preview", ["zoning.previewed", "zoning.proper"], "zoning-check")
    report = ev["data"].get("report", {})
    check("zoning check lists %s as iSCSI, not logged in (D22U27 has no iSCSI port)" % HOST,
          report.get("iscsi_hosts", {}).get(HOST) == [], json.dumps(report.get("iscsi_hosts", {})))
    status, resp = ui.api("POST", "/runs/%s/storage/builder" % run_id, {
        "host_sets": [{"name": HOSTSET, "members": [HOST]}],
        "exports": [{"source_kind": "volume", "source_name": VOL, "target_kind": "hostset", "target_name": HOSTSET, "lun": None}],
        "vvsets": {}})
    fl.save("api-builder.json", json.dumps(resp, indent=2))
    if not check("composition saved (host set %s with %s, export %s to it)" % (HOSTSET, HOST, VOL), status == 200, str(resp)[:200]):
        return None

    ev = ui.api_step(run_id, "/storage/preview", ["storage.previewed", "storage.preview.failed"], "plan")
    plan = ev["data"].get("plan", {})
    row = host_row(plan) or {}
    check("plan: host %s to create, from its iSCSI name, persona Generic-ALUA" % HOST,
          row.get("state") == "create" and IQN in row.get("description", "") and "Generic-ALUA" in row.get("description", ""),
          row.get("description", "no host row"))
    check("plan: no blockers", not plan.get("blockers"), "; ".join(plan.get("blockers", [])))
    check("plan: the export is held back (no VLUN row) and says why",
          not [a for a in plan.get("actions", []) if a["kind"] == "vlun"]
          and any("held back" in n and HOSTSET in n for n in plan.get("notes", [])), " | ".join(plan.get("notes", []))[:300])
    if plan.get("blockers") or plan.get("error") or row.get("state") != "create":
        return None

    since = len(ui.events(run_id))
    applied = ui.api_step(run_id, "/storage/apply", ["storage.applied", "storage.apply.failed"], "apply")
    result = applied["data"].get("result", {})
    outcome = {(o["kind"], o["name"]): o for o in result.get("outcomes", [])}
    host = outcome.get(("host", HOST), {})
    check("apply: host %s created" % HOST, host.get("status") == "created", "%s %s" % (host.get("status"), host.get("detail")))
    check("apply: host set and volume created",
          outcome.get(("hostset", HOSTSET), {}).get("status") == "created" and outcome.get(("volume", VOL), {}).get("status") == "created")
    sent = [e for e in ui.writes(run_id)]
    create = [w for w in sent if w.startswith("POST /hosts ")]   # not POST /hostsets
    check("the host was made with one WSAPI call carrying the iSCSI name and no FC WWN",
          len(create) == 1 and IQN in create[0] and "FCWWNs" not in create[0], create[0][:200] if create else "none")
    check("every write named a zz_is_ object", all("zz_is_" in w for w in sent), " | ".join(sent)[:300])
    fl.save("events-after-apply.json", json.dumps(ui.events(run_id)[since:], indent=2))

    c = fl.ssh(P_HOST, ui.ARRAY_PW)
    shown = fl.run(c, "showhost -d %s" % HOST)
    persona = fl.run(c, "showhost -persona %s" % HOST)
    c.close()
    fl.save("showhost_d_after.txt", "# showhost -d %s\n%s" % (HOST, shown))
    fl.save("showhost_persona_after.txt", "# showhost -persona %s\n%s" % (HOST, persona))
    rows = [ln.split() for ln in shown.splitlines() if HOST in ln]
    check("the array lists %s with the iSCSI name, not logged in" % HOST,
          any(r[-3].lower() == IQN and not NSP.match(r[-2]) for r in rows if len(r) >= 6), shown.strip()[-200:])
    check("the array gave it persona Generic-ALUA", "Generic-ALUA" in persona, persona.strip()[-120:])

    ev = ui.api_step(run_id, "/storage/preview", ["storage.previewed", "storage.preview.failed"], "plan-again")
    again = host_row(ev["data"].get("plan", {})) or {}
    check("planning again: the host exists and carries its iSCSI name", again.get("state") == "exists",
          "%s: %s" % (again.get("state"), again.get("reason")))
    return applied


def cleanup(applied):
    fl.banner("4. Removing what the run created")
    c = fl.ssh(P_HOST, ui.ARRAY_PW)
    removals = ((applied or {}).get("data", {}).get("result") or {}).get("removals", [])
    lines = [r["command"] for r in sorted(removals, key=lambda r: ui.REMOVAL_ORDER.get(r["kind"], 9))]
    log = []
    for cmd in lines:
        answer = fl.run(c, cmd).strip()
        log.append("$ %s\n%s" % (cmd, answer))
        print("  $ %s  -> %s" % (cmd, answer.splitlines()[-1] if answer else "(no output)"))
    left = leftovers(c)
    if left:
        # The removal set missed something (a stopped apply): these fixed names are ours, D22U27 had none before.
        for cmd in ("removehostset -f " + HOSTSET, "removevv -f " + VOL, "removehost " + HOST):
            log.append("(fallback) $ %s\n%s" % (cmd, fl.run(c, cmd).strip()))
        left = leftovers(c)
    fl.save("cleanup.txt", "\n".join(log))
    check("the run's removal set was run (%d commands)" % len(lines), bool(lines) or applied is None, " | ".join(lines))
    check("no zz_is_* object left on D22U27", not left, "; ".join(left))
    c.close()


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    fl.banner("1. D22U27 before")
    c = fl.ssh(P_HOST, ui.ARRAY_PW)
    left, owner = leftovers(c), iqn_owner(c)
    c.close()
    if left:
        sys.exit("zz_is_* objects are already on D22U27, nothing was done:\n  " + "\n  ".join(left))
    if owner:
        sys.exit("The iSCSI name %s is already on host %s on D22U27, nothing was done." % (IQN, owner))
    fl.restart_app()

    fl.banner("2-3. A Provision only run: discovery, zoning check, plan, apply")
    run_id = compose()
    print("run " + run_id)
    fl.save("run-id.txt", run_id)
    applied = None
    try:
        applied = run(run_id)
    except Exception as exc:  # noqa: BLE001
        check("stopped: %s" % str(exc).splitlines()[0][:200], False)
        fl.save("error.txt", traceback.format_exc())
        done = [e for e in ui.events(run_id) if e["event_type"] == "storage.applied"]
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
