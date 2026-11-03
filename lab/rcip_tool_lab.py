"""BL-41 live check: the tool sets up the RCIP ports and the partnership itself, then replicates over it.
No prompts. The app must be running on http://127.0.0.1:8765.

    python lab/rcip_tool_lab.py

Starts from the pair with no partnership (after `rcip_setup_lab.py undo-setup`): the Alletra rack13-ARCUS
(10.132.30.121) has Remote Copy not configured and no RCIP address on 0:4:4 / 1:4:4; the Primera
PRIMERA630R11U22 (10.132.30.28) has its RCIP ports addressed and no target for the Alletra.
CHANGES BOTH ARRAYS and removes everything with the run's own removal sets:
1. checks that starting point and that nothing zz_rc_* is on either array
2. on the Alletra, over the app's WSAPI client: volume zz_rc_vol01 (1 GiB thin, SSD_r6) in set zz_rc_vvs
3. one Custom run (replicate, failover test, as-built) from a sheet with the Replication network tab:
   preview (partnership rows only), apply (ports, ping, startrcopy, targets, links Up), preview again
   (groups), link check, apply, verify until replicating, failover test, as-built
4. pastes the run's merged removal set over SSH (A block, then B block) and checks the pair is back
   at the starting point
Password: RCIP_PAIR_PW. Evidence in RCIP_LAB_DIR (default ~/Downloads)/rcip_tool/.
"""
import base64
import json
import os
import shutil
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402
import rcip_pair_lab as pl  # noqa: E402

A_HOST, P_HOST = pl.A_HOST, pl.P_HOST
VOL, VVSET, GROUP = pl.VOL, pl.VVSET, pl.GROUP
NETWORK = [
    {"array": "this", "port": "0:4:4", "ip": "10.93.18.11", "netmask": "255.255.254.0"},
    {"array": "this", "port": "1:4:4", "ip": "10.93.18.13", "netmask": "255.255.254.0"},
    {"array": "peer", "port": "0:1:1", "ip": "10.93.18.19", "netmask": "255.255.254.0"},
    {"array": "peer", "port": "1:1:1", "ip": "10.93.18.20", "netmask": "255.255.254.0"},
]
OUT = os.path.join(pl.BASE, "rcip_tool")
check, evidence, api, step, events = pl.check, pl.evidence, pl.api, pl.step, pl.events


def starting_point(a, p):
    """(ok, detail): Remote Copy not configured on A, no RCIP on A's two ports, no target for A on P."""
    rc_a = fl.run(a, "showrcopy")
    rcip_a = fl.run(a, "showport -rcip")
    targets_p = fl.run(p, "showrcopy targets")
    rcip_p = fl.run(p, "showport -rcip")
    problems = []
    if "not configured" not in rc_a.lower():
        problems.append("Remote Copy is configured on the Alletra")
    if any(n in rcip_a for n in ("0:4:4", "1:4:4")):
        problems.append("the Alletra has an RCIP address on 0:4:4 or 1:4:4")
    if any(ln.split()[:1] == ["rack13-ARCUS"] for ln in targets_p.splitlines()):
        problems.append("the Primera has a target rack13-ARCUS")
    if not all(ip in rcip_p for ip in ("10.93.18.19", "10.93.18.20")):
        problems.append("the Primera's RCIP addresses are not 10.93.18.19 / .20")
    return not problems, "; ".join(problems)


def console_writes(run_id):
    return [c for c in api("GET", "/runs/%s/console/log" % run_id)[1]["commands"] if c.get("write")]


def compose(password):
    body = pl.compose_body(password)
    body["replication"]["network"] = NETWORK
    status, resp = api("POST", "/init-sheet/compose", body)
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
    run_id = r["run"]["run_id"]
    print("run " + run_id)
    fl.save("run-id.txt", run_id)
    return run_id


def rows(plan, *kinds):
    return [(x["kind"], x["where"], x["name"], x["state"]) for x in plan.get("actions", []) if x["kind"] in kinds]


def run_all(run_id):
    removals = []
    fl.banner("Preview 1: the partnership")
    ev = step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "preview-1")
    plan = ev["data"].get("plan") or {}
    check("preview 1: the Primera's name is read", (ev["data"].get("report") or {}).get("peer", {}).get("name") == "PRIMERA630R11U22")
    check("preview 1: ports, Remote Copy and targets planned as expected",
          rows(plan, "rcip_port", "rc_service", "target") == [
              ("rcip_port", "A", "0:4:4", "create"), ("rcip_port", "A", "1:4:4", "create"),
              ("rcip_port", "B", "0:1:1", "exists"), ("rcip_port", "B", "1:1:1", "exists"),
              ("rc_service", "A", "Remote Copy", "create"), ("rc_service", "B", "Remote Copy", "exists"),
              ("target", "A", "PRIMERA630R11U22", "create"), ("target", "B", "rack13-ARCUS", "create")],
          json.dumps(rows(plan, "rcip_port", "rc_service", "target")))
    check("preview 1: no group yet, no blocker", not rows(plan, "group") and not plan.get("blockers"),
          "; ".join(plan.get("blockers", [])))
    if plan.get("blockers"):
        raise RuntimeError("partnership plan has blockers")

    fl.banner("Apply 1: ports and partnership, over the write-scoped SSH client")
    ev = step(run_id, "/replication/apply", ["replication.applied", "replication.apply.failed"], "apply-1")
    res = ev["data"].get("result") or {}
    removals.append(res)
    kinds = [o["kind"] for o in res.get("outcomes", [])]
    check("apply 1: addresses, pings, Remote Copy, targets, links Up", not res.get("error") and kinds == [
        "rcip_port", "rcip_port", "ping", "ping", "rc_service", "target", "target", "links"],
        res.get("error") or ", ".join(kinds))
    check("apply 1: its removal set", res.get("removals_a") == [
        "removercopytarget PRIMERA630R11U22", "stoprcopy -f -stopgroups -clear",
        "controlport rcip delete -f 0:4:4", "controlport rcip delete -f 1:4:4"]
        and res.get("removals_b") == ["removercopytarget rack13-ARCUS"],
        json.dumps([res.get("removals_a"), res.get("removals_b")]))
    if res.get("error"):
        return removals
    writes = [c for c in console_writes(run_id) if c["transport"] == "ssh"]
    check("the console log names every SSH write", [c["command"] for c in writes] == [
        "controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4", "controlport rcip addr -f 10.93.18.13 255.255.254.0 1:4:4",
        "controlport rcip ping -c 3 10.93.18.19 0:4:4", "controlport rcip ping -c 3 10.93.18.20 1:4:4", "startrcopy",
        "creatercopytarget PRIMERA630R11U22 IP 0:4:4:10.93.18.19 1:4:4:10.93.18.20",
        "creatercopytarget rack13-ARCUS IP 0:1:1:10.93.18.11 1:1:1:10.93.18.13"],
        " | ".join(c["command"] for c in writes))

    fl.banner("Preview 2: the groups, over the partnership the tool made")
    ev = step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "preview-2")
    plan = ev["data"].get("plan") or {}
    part = (ev["data"].get("report") or {}).get("partnership") or {}
    check("preview 2: partnership found, 2/2 links Up each way",
          part.get("links_primary_up") == part.get("links_primary_total") == 2 and part.get("links_peer_up") == part.get("links_peer_total") == 2,
          json.dumps({k: part.get(k) for k in ("target_on_primary", "target_on_peer", "links_primary_up", "links_peer_up")}))
    check("preview 2: every partnership row exists, the group is to create, no blocker",
          all(s == "exists" for *_x, s in rows(plan, "rcip_port", "rc_service", "target"))
          and ("group", "A", GROUP, "create") in rows(plan, "group") and not plan.get("blockers"),
          "; ".join(plan.get("blockers", [])))
    if plan.get("blockers"):
        raise RuntimeError("group plan has blockers")
    status, resp = api("POST", "/runs/%s/replication/apply" % run_id, {})
    check("apply 2 is refused until the link is checked", status == 409 and "Check the link first" in str(resp),
          "HTTP %s %s" % (status, str(resp)[:160]))
    ev = step(run_id, "/replication/link-check", ["replication.link_checked", "replication.link_check.failed"], "link-check",
              body={"duration_s": 600})
    lc = ev["data"].get("link_check") or {}
    check("link check: both links measured, links still Up", ev["event_type"] == "replication.link_checked" and not lc.get("error"),
          ev["message"][:200])

    fl.banner("Apply 2: the groups")
    ev = step(run_id, "/replication/apply", ["replication.applied", "replication.apply.failed"], "apply-2")
    res = ev["data"].get("result") or {}
    removals.append(res)
    check("apply 2: groups created", GROUP in res.get("groups_created", []) and not res.get("error"),
          res.get("error") or ", ".join(res.get("groups_created", [])))
    if res.get("error"):
        return removals
    ver = {}
    for attempt in range(20):
        ev = step(run_id, "/replication/verify", ["replication.verified", "replication.verify.failed"], "verify-%02d" % attempt)
        ver = ev["data"].get("verification") or {}
        if ver.get("groups") and all(x["verdict"] == "replicating" for x in ver["groups"]):
            break
        time.sleep(15)
    check("verify: every group replicating", bool(ver.get("groups")) and all(x["verdict"] == "replicating" for x in ver["groups"]),
          "; ".join("%s %s" % (x["group"], x["verdict"]) for x in ver.get("groups", [])))
    ev = step(run_id, "/replication/failover-test", ["failover.completed", "failover.failed"], "failover", body={})
    rec = ev["data"].get("record") or {}
    check("failover test passed", rec.get("result") == "passed", ev["message"][:200])
    ev = step(run_id, "/asbuilt", ["asbuilt.generated", "asbuilt.failed"], "asbuilt")
    text = pl.docx_text(run_id) if ev["event_type"] == "asbuilt.generated" else ""
    evidence("asbuilt-text.txt", text)
    for needle in ("Replication port", "Remote Copy target", "removercopytarget PRIMERA630R11U22",
                   "controlport rcip delete -f 0:4:4", "stoprcopygroup -f " + GROUP):
        check("as-built carries '%s'" % needle, needle in text)
    check("as-built: the groups' removal lines come before the partnership's",
          text.find("stoprcopygroup -f " + GROUP) < text.find("removercopytarget PRIMERA630R11U22"))
    return removals


def merged(results, key):
    out = []
    for res in reversed(results):
        out += [line for line in res.get(key) or [] if line not in out]
    return out


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    fl.OUT = pl.OUT = OUT
    from alletra_onboard.adapters.array.wsapi_client import WsapiClient

    password = fl.lab_secret("RCIP_PAIR_PW")
    a, p = fl.ssh(A_HOST, password), fl.ssh(P_HOST, password)
    fl.banner("1. Starting point")
    ok, why = starting_point(a, p)
    if not check("the pair has no partnership yet", ok, why):
        sys.exit("Not at the starting point: " + why)
    left = pl.leftovers(a, p)
    if left:
        sys.exit("zz_rc_* objects are already on the arrays: " + "; ".join(left))
    if not check("the app answers on %s" % fl.APP, api("GET", "/app/profile")[0] == 200):
        sys.exit("start the app first")
    results = []
    try:
        fl.banner("2. Test volume and set on the Alletra")
        with WsapiClient(A_HOST, "3paradm", password) as w:
            check("volume %s created" % VOL, w.ensure_volume(VOL, "SSD_r6", 1024, "tpvv") == "created")
            check("volume set %s created" % VVSET, w.ensure_volume_set(VVSET, [VOL]) == "created")
        run_id = compose(password)
        try:
            results = run_all(run_id)
        except Exception as exc:  # noqa: BLE001
            check("stopped: %s" % str(exc)[:300], False)
            evidence("error.txt", traceback.format_exc())
            results = [e["data"].get("result") or {} for e in events(run_id)
                       if e["event_type"] in ("replication.applied", "replication.apply.failed")]
    finally:
        fl.banner("4. The run's removal set, A block then B block")
        a.close(), p.close()
        a, p = fl.ssh(A_HOST, password), fl.ssh(P_HOST, password)
        log = []
        for label, c, lines in (("alletra", a, merged(results, "removals_a")), ("primera", p, merged(results, "removals_b"))):
            for cmd in lines:
                answer = fl.run(c, cmd).strip()
                if "busy" in answer.lower():
                    time.sleep(30)
                    log.append("[%s] $ %s\n%s\n(busy: retried after 30 s)" % (label, cmd, answer))
                    answer = fl.run(c, cmd).strip()
                log.append("[%s] $ %s\n%s" % (label, cmd, answer))
                print("  [%s] $ %s  -> %s" % (label, cmd, answer.splitlines()[-1] if answer else "(no output)"))
        for cmd in ("removevvset -f " + VVSET, "removevv -f " + VOL):    # made by this script, not the run
            log.append("[alletra] $ %s\n%s" % (cmd, fl.run(a, cmd).strip()))
        evidence("cleanup.txt", "\n".join(log + pl.sweep_by_name(a, p)))
        left = pl.leftovers(a, p)
        check("no zz_rc_* object left on either array", not left, "; ".join(left))
        ok, why = starting_point(a, p)
        check("the pair is back at the starting point", ok, why)
        a.close(), p.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        if fl.OUT and os.path.isdir(fl.OUT):
            fails = sum(1 for r in pl.RESULTS if r.startswith("FAIL"))
            fl.save("report.txt", "\n".join(pl.RESULTS + ["", "%d PASS, %d FAIL" % (len(pl.RESULTS) - fails, fails)]))
            fl.banner("%d PASS, %d FAIL. Evidence in %s" % (len(pl.RESULTS) - fails, fails, fl.OUT))
