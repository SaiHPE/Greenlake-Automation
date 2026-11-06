"""BL-41 in-scope paths not yet run live, on the Alletra MP rack13-ARCUS (10.132.30.121) -> Primera
PRIMERA630R11U22 (10.132.30.28) pair. No prompts. The app must be running on http://127.0.0.1:8765.

    python lab/rcip_scope_lab.py

Starts where `rcip_tool_lab.py` ends (no partnership; the Primera's RCIP ports addressed, its gateway as
the lab set it, Remote Copy started, no target). CHANGES BOTH ARRAYS and puts them back:
1. mixed:   a sync row and an async row with the Replication network tab -> refused at the first read
2. half:    this array's ports on another network -> addresses set, ping fails, the run stops; its
            removal set is pasted
3. gateway: the Primera's gateway left on -> the link check must report the links it broke and the way
            back; that way back is run, then the removal set
4. peer:    the Primera's Remote Copy stopped and its RCIP addresses removed (journaled), so the tool sets
            the peer's addresses and starts Remote Copy there; groups, verify; then a second run of the
            same sheet runs the failover test on a group it did not create (refused, then typed back);
            the removal set, then the Primera's addresses, gateway and Remote Copy restored
Password: RCIP_PAIR_PW. Evidence in RCIP_LAB_DIR (default ~/Downloads)/rcip_scope/. Journal: the
rcip_setup_lab.py journal in RCIP_LAB_DIR (entries tagged scope-peer).
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
import rcip_tool_lab as tl  # noqa: E402

A_HOST, P_HOST = pl.A_HOST, pl.P_HOST
OUT = os.path.join(pl.BASE, "rcip_scope")
JOURNAL = os.path.join(pl.BASE, "rcip_setup_journal.json")
P_PORTS = ("0:1:1", "1:1:1")
GROUP = pl.GROUP
check, api, step = pl.check, pl.api, pl.step
OTHER_NET = [
    {"array": "this", "port": "0:4:4", "ip": "192.0.2.11", "netmask": "255.255.255.0"},
    {"array": "this", "port": "1:4:4", "ip": "192.0.2.13", "netmask": "255.255.255.0"},
    *tl.NETWORK[2:],
]


def run_from_sheet(password, name, rows=None, network=tl.NETWORK, steps=("replicate",)):
    body = pl.compose_body(password)
    body["replication"]["network"] = network
    if rows is not None:
        body["replication"]["rows"] = rows
    status, resp = api("POST", "/init-sheet/compose", body)
    if status != 200:
        raise RuntimeError("compose -> HTTP %s: %s" % (status, resp))
    status, up = api("POST", "/init-sheet/upload", {"content_b64": resp["content_b64"]})
    if status != 200:
        raise RuntimeError("upload -> HTTP %s: %s" % (status, up))
    status, r = api("POST", "/runs/from-sheet", {"token": up["token"], "mode": "CUSTOM", "selected_steps": list(steps)})
    if status != 200:
        raise RuntimeError("from-sheet -> HTTP %s: %s" % (status, r))
    run_id = r["run"]["run_id"]
    print("  run %s: %s" % (name, run_id))
    with open(os.path.join(OUT, "%s-sheet.xlsx" % name), "wb") as f:
        f.write(base64.b64decode(resp["content_b64"]))
    return run_id


def applies(run_id):
    return [e["data"].get("result") or {} for e in pl.events(run_id)
            if e["event_type"] in ("replication.applied", "replication.apply.failed")]


def paste(password, results, name):
    """The run's merged removal set, A block then B block, as the operator pastes it."""
    a, p = fl.ssh(A_HOST, password), fl.ssh(P_HOST, password)
    log, errors = [], []
    for label, c, lines in (("alletra", a, tl.merged(results, "removals_a")), ("primera", p, tl.merged(results, "removals_b"))):
        for cmd in lines:
            answer = fl.run(c, cmd).strip()
            if "busy" in answer.lower():
                time.sleep(30)
                answer = fl.run(c, cmd).strip()
            if answer.lower().startswith("error"):
                errors.append("%s: %s -> %s" % (label, cmd, answer.splitlines()[0]))
            log.append("[%s] $ %s\n%s" % (label, cmd, answer))
    pl.evidence("%s-removal-set.txt" % name, "\n".join(log))
    a.close(), p.close()
    return errors


def primera_rcip(p):
    """{n:s:p: (ip, netmask, gateway)} for the Primera's two RCIP ports, as showport -rcip lists them."""
    out = {}
    for line in fl.run(p, "showport -rcip").splitlines():
        t = line.split()
        if len(t) >= 6 and t[0] in P_PORTS:
            out[t[0]] = (t[3], t[4], t[5])
    return out


def back_at_start(password, name):
    a, p = fl.ssh(A_HOST, password), fl.ssh(P_HOST, password)
    ok, why = tl.starting_point(a, p)
    groups = [g for g in pl.leftovers(a, p) if "showrcopy" in g]
    a.close(), p.close()
    return check("%s: the pair is back at the start" % name, ok and not groups, why + "; ".join(groups))


# ------------------------------------------------------------------ 1. mixed modes

def mixed(password):
    fl.banner("1. A sync row and an async row with the Replication network tab")
    rows = [{"vvset": pl.VVSET, "peer_cpg": "SSD_r6", "mode": "sync"},
            {"vvset": "zz_rc_vvs2", "peer_cpg": "SSD_r6", "mode": "async", "rpo_minutes": "10"}]
    run_id = run_from_sheet(password, "mixed", rows=rows)
    ev = step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "mixed-preview")
    blockers = (ev["data"].get("plan") or {}).get("blockers", [])
    check("mixed: refused at the first read, with the reason",
          any("mixes sync and async rows, and the partnership the tool sets up" in b for b in blockers), " | ".join(blockers)[:400])
    status, resp = api("POST", "/runs/%s/replication/apply" % run_id, {})
    check("mixed: configure is refused", status == 409, "HTTP %s %s" % (status, str(resp)[:160]))
    check("mixed: nothing was written", not tl.console_writes(run_id))


# ------------------------------------------------------------------ 2. a stopped apply

def half(password):
    fl.banner("2. This array's ports on another network: the ping fails and the run stops")
    run_id = run_from_sheet(password, "half", network=OTHER_NET)
    try:
        ev = step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "half-preview")
        plan = ev["data"].get("plan") or {}
        check("half: planned without a blocker", not plan.get("blockers"), " | ".join(plan.get("blockers", []))[:300])
        if plan.get("blockers"):
            return
        ev = step(run_id, "/replication/apply", ["replication.applied", "replication.apply.failed"], "half-apply")
        res = ev["data"].get("result") or {}
        check("half: stopped at the ping, nothing after the addresses",
              ev["event_type"] == "replication.apply.failed" and "ping from 0:4:4 to 10.93.18.19" in (res.get("error") or "")
              and "nothing after the addresses was done" in (res.get("error") or ""), (res.get("error") or "")[:300])
        check("half: the removal set is exactly the two addresses",
              res.get("removals_a") == ["controlport rcip delete -f 0:4:4", "controlport rcip delete -f 1:4:4"]
              and res.get("removals_b") == [], json.dumps([res.get("removals_a"), res.get("removals_b")]))
        writes = [c["command"] for c in tl.console_writes(run_id)]
        check("half: no startrcopy, no target written", not any(w.startswith(("startrcopy", "creatercopytarget")) for w in writes),
              " | ".join(writes))
    finally:
        errors = paste(password, applies(run_id), "half")
        check("half: the removal set ran without an error", not errors, "; ".join(errors))
        back_at_start(password, "half")


# ------------------------------------------------------------------ 3. the gateway

def gateway(password):
    fl.banner("3. The Primera's gateway left on: the link check must catch the links it breaks")
    p = fl.ssh(P_HOST, password)
    gws = {nsp: v[2] for nsp, v in primera_rcip(p).items()}
    p.close()
    if not check("gateway: the Primera's ports have the lab's gateway", set(gws.values()) == {"10.93.18.1"}, json.dumps(gws)):
        return
    run_id = run_from_sheet(password, "gateway")
    try:
        step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "gateway-preview-1")
        ev = step(run_id, "/replication/apply", ["replication.applied", "replication.apply.failed"], "gateway-apply-1")
        if not check("gateway: partnership set up, links Up", ev["event_type"] == "replication.applied", ev["message"][:200]):
            return
        step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "gateway-preview-2")
        ev = step(run_id, "/replication/link-check", ["replication.link_checked", "replication.link_check.failed"], "gateway-link-check",
                  body={"duration_s": 600})
        lc = ev["data"].get("link_check") or {}
        details = " | ".join(r.get("detail", "") for r in lc.get("results", []))
        check("gateway: the check names the gateway before it runs", any("10.93.18.1" in n for n in lc.get("notes", [])),
              " | ".join(lc.get("notes", []))[:300])
        check("gateway: no latency, the answers went through 10.93.18.1",
              all(r.get("status") == "failed" for r in lc.get("results", [])) and "routed its answers through gateway 10.93.18.1" in details,
              details[:400])
        check("gateway: the links it broke are an error with the way back",
              "these Remote Copy links are Down, and they were Up before it" in (lc.get("error") or "")
              and "controlport rcip state down -f" in (lc.get("error") or ""), (lc.get("error") or "")[:400])
        status, resp = api("POST", "/runs/%s/replication/apply" % run_id, {})
        check("gateway: configure is refused", status == 409, "HTTP %s %s" % (status, str(resp)[:200]))
        fl.banner("3b. The way back the tool printed: state down / up on the Primera's ports")
        p = fl.ssh(P_HOST, password)
        log = []
        for nsp in P_PORTS:
            for cmd in ("controlport rcip state down -f %s" % nsp, "controlport rcip state up -f %s" % nsp):
                log.append("$ %s\n%s" % (cmd, fl.run(p, cmd).strip()))
        pl.evidence("gateway-way-back.txt", "\n".join(log))
        a = fl.ssh(A_HOST, password)
        for _ in range(18):
            ups = [pl.links_up(a), pl.links_up(p)]
            if all(n == t == 2 for n, t in ups):
                break
            time.sleep(10)
        check("gateway: after the way back every link is Up again", all(n == t == 2 for n, t in ups), json.dumps(ups))
        a.close(), p.close()
    finally:
        errors = paste(password, applies(run_id), "gateway")
        check("gateway: the removal set ran without an error", not errors, "; ".join(errors))
        back_at_start(password, "gateway")


# ------------------------------------------------------------------ 4. the peer's side, and the failover choice

def journal_add(entries):
    journal = json.load(open(JOURNAL)) if os.path.exists(JOURNAL) else []
    journal += entries
    with open(JOURNAL, "w", encoding="utf-8") as f:
        json.dump(journal, f, indent=1)


def restore_primera(password, before):
    """Puts back the Primera's addresses, gateway and Remote Copy from `before`; idempotent."""
    p = fl.ssh(P_HOST, password)
    log = []
    now = primera_rcip(p)
    for nsp, (ip, mask, gw) in before.items():
        if now.get(nsp, ("",))[0] != ip:
            log.append("$ controlport rcip addr -f %s %s %s\n%s" % (ip, mask, nsp, fl.run(p, "controlport rcip addr -f %s %s %s" % (ip, mask, nsp)).strip()))
        if gw not in ("-", "") and now.get(nsp, ("", "", ""))[2] != gw:
            log.append("$ controlport rcip gw -f %s %s\n%s" % (gw, nsp, fl.run(p, "controlport rcip gw -f %s %s" % (gw, nsp)).strip()))
    if "started" not in fl.run(p, "showrcopy").lower():
        log.append("$ startrcopy\n%s" % fl.run(p, "startrcopy").strip())
    after = primera_rcip(p)
    started = "started" in fl.run(p, "showrcopy").lower()
    pl.evidence("peer-primera-restored.txt", "\n".join(log))
    p.close()
    ok = check("peer: the Primera's addresses, gateway and Remote Copy are back", after == before and started,
               "%s started=%s" % (json.dumps(after), started))
    if ok:
        journal = json.load(open(JOURNAL))
        with open(JOURNAL, "w", encoding="utf-8") as f:
            json.dump([e for e in journal if e.get("what", "").startswith("scope-peer") is False], f, indent=1)


def peer(password):
    fl.banner("4. The tool sets the peer's addresses and starts Remote Copy on it")
    from alletra_onboard.application.replication.read import parse_showrcopy

    p = fl.ssh(P_HOST, password)
    rc = parse_showrcopy(fl.run(p, "showrcopy"))
    before = primera_rcip(p)
    if not check("peer: the Primera has no target and no group, so stopping its Remote Copy loses nothing",
                 not rc["targets"] and not rc["groups"] and rc["status"] == "Started" and len(before) == 2,
                 "status %s, targets %s, groups %s" % (rc["status"], [t.name for t in rc["targets"]], [g.name for g in rc["groups"]])):
        p.close()
        return
    at = time.strftime("%Y-%m-%d %H:%M:%S")
    entries = [{"array": "primera", "undo": "startrcopy", "what": "scope-peer: Remote Copy stopped", "at": at}]
    for nsp in P_PORTS:
        ip, mask, gw = before[nsp]
        entries.append({"array": "primera", "undo": "controlport rcip gw -f %s %s" % (gw, nsp), "what": "scope-peer: gateway", "at": at})
        entries.append({"array": "primera", "undo": "controlport rcip addr -f %s %s %s" % (ip, mask, nsp), "what": "scope-peer: address", "at": at})
    journal_add(entries)
    pl.evidence("peer-primera-before.json", {"rcip": before, "status": rc["status"]})
    log = ["$ stoprcopy -f -stopgroups -clear\n" + fl.run(p, "stoprcopy -f -stopgroups -clear").strip()]
    for nsp in P_PORTS:
        log.append("$ controlport rcip delete -f %s\n%s" % (nsp, fl.run(p, "controlport rcip delete -f %s" % nsp).strip()))
    pl.evidence("peer-primera-cleared.txt", "\n".join(log + ["$ showrcopy\n" + fl.run(p, "showrcopy"), "$ showport -rcip\n" + fl.run(p, "showport -rcip")]))
    cleared = not primera_rcip(p) or all(v[0] in ("-", "0.0.0.0") for v in primera_rcip(p).values())
    check("peer: the Primera now has no RCIP address and no Remote Copy",
          cleared and "not configured" in fl.run(p, "showrcopy").lower(), json.dumps(primera_rcip(p)))
    p.close()
    run_id = second = None
    try:
        run_id = run_from_sheet(password, "peer")
        ev = step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "peer-preview-1")
        plan = ev["data"].get("plan") or {}
        rows = tl.rows(plan, "rcip_port", "rc_service", "target")
        check("peer: both sides' ports, Remote Copy on both and both targets to create, no blocker",
              rows == [("rcip_port", "A", "0:4:4", "create"), ("rcip_port", "A", "1:4:4", "create"),
                       ("rcip_port", "B", "0:1:1", "create"), ("rcip_port", "B", "1:1:1", "create"),
                       ("rc_service", "A", "Remote Copy", "create"), ("rc_service", "B", "Remote Copy", "create"),
                       ("target", "A", "PRIMERA630R11U22", "create"), ("target", "B", "rack13-ARCUS", "create")]
              and not plan.get("blockers"), json.dumps(rows) + " " + " | ".join(plan.get("blockers", []))[:300])
        if plan.get("blockers"):
            return
        ev = step(run_id, "/replication/apply", ["replication.applied", "replication.apply.failed"], "peer-apply-1")
        res = ev["data"].get("result") or {}
        kinds = [o["kind"] + o["where"] for o in res.get("outcomes", [])]
        check("peer: 4 addresses, 2 pings, Remote Copy started on both, 2 targets, links Up",
              not res.get("error") and kinds == ["rcip_portA", "rcip_portA", "rcip_portB", "rcip_portB", "pingA", "pingA",
                                                 "rc_serviceA", "rc_serviceB", "targetA", "targetB", "linksA"],
              res.get("error") or ", ".join(kinds))
        check("peer: the B block undoes the peer's side too",
              res.get("removals_b") == ["removercopytarget rack13-ARCUS", "stoprcopy -f -stopgroups -clear",
                                        "controlport rcip delete -f 0:1:1", "controlport rcip delete -f 1:1:1"],
              json.dumps(res.get("removals_b")))
        if res.get("error"):
            return
        step(run_id, "/replication/preview", ["replication.previewed", "replication.preview.failed"], "peer-preview-2")
        step(run_id, "/replication/link-check", ["replication.link_checked", "replication.link_check.failed"], "peer-link-check",
             body={"duration_s": 600})
        ev = step(run_id, "/replication/apply", ["replication.applied", "replication.apply.failed"], "peer-apply-2")
        res = ev["data"].get("result") or {}
        if not check("peer: groups created", GROUP in res.get("groups_created", []), res.get("error") or ""):
            return
        for attempt in range(20):
            ev = step(run_id, "/replication/verify", ["replication.verified", "replication.verify.failed"], "peer-verify-%02d" % attempt)
            ver = ev["data"].get("verification") or {}
            if ver.get("groups") and all(x["verdict"] == "replicating" for x in ver["groups"]):
                break
            time.sleep(15)
        check("peer: every group replicating", all(x["verdict"] == "replicating" for x in ver.get("groups", [])) and ver.get("groups"),
              "; ".join("%s %s" % (x["group"], x["verdict"]) for x in ver.get("groups", [])))

        fl.banner("4b. A second run of the same sheet: the failover test on a group it did not create")
        second = run_from_sheet(password, "failover", steps=("failover_test",))
        status, resp = api("POST", "/runs/%s/replication/failover-test" % second, {"group": GROUP})
        check("failover: refused without the name typed back",
              status == 409 and "was not created by this run" in str(resp), "HTTP %s %s" % (status, str(resp)[:200]))
        ev = step(second, "/replication/failover-test", ["failover.completed", "failover.failed"], "failover-typed",
                  body={"group": GROUP, "confirm": GROUP})
        rec = ev["data"].get("record") or {}
        check("failover: with the name typed back it ran on %s and passed" % GROUP,
              rec.get("result") == "passed" and rec.get("group") == GROUP, ev["message"][:200])
    finally:
        errors = paste(password, applies(run_id), "peer") if run_id else []
        check("peer: the removal set ran without an error", not errors, "; ".join(errors))
        p = fl.ssh(P_HOST, password)
        pl.evidence("peer-primera-after-removal.txt", "$ showrcopy\n" + fl.run(p, "showrcopy") + "\n$ showport -rcip\n" + fl.run(p, "showport -rcip"))
        p.close()
        restore_primera(password, before)
        back_at_start(password, "peer")


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    fl.OUT = pl.OUT = OUT
    from alletra_onboard.adapters.array.wsapi_client import WsapiClient

    password = fl.lab_secret("RCIP_PAIR_PW")
    if not check("the app answers on %s" % fl.APP, api("GET", "/app/profile")[0] == 200):
        sys.exit("start the app first")
    a, p = fl.ssh(A_HOST, password), fl.ssh(P_HOST, password)
    ok, why = tl.starting_point(a, p)
    left = pl.leftovers(a, p)
    a.close(), p.close()
    if not check("the pair has no partnership and nothing zz_rc_*", ok and not left, why + "; ".join(left)):
        sys.exit("Not at the starting point")
    try:
        with WsapiClient(A_HOST, "3paradm", password) as w:
            check("volume %s and set %s created" % (pl.VOL, pl.VVSET),
                  w.ensure_volume(pl.VOL, "SSD_r6", 1024, "tpvv") == "created" and w.ensure_volume_set(pl.VVSET, [pl.VOL]) == "created")
        for scenario in (mixed, half, gateway, peer):
            try:
                scenario(password)
            except Exception as exc:  # noqa: BLE001 - the next scenario still runs; its own cleanup ran
                check("%s stopped: %s" % (scenario.__name__, str(exc)[:300]), False)
                pl.evidence("%s-error.txt" % scenario.__name__, traceback.format_exc())
    finally:
        fl.banner("Cleanup: the scripts' own volume and set, anything zz_rc_* left")
        a, p = fl.ssh(A_HOST, password), fl.ssh(P_HOST, password)
        pl.evidence("cleanup.txt", "\n".join(pl.sweep_by_name(a, p)))
        left = pl.leftovers(a, p)
        check("no zz_rc_* object left on either array", not left, "; ".join(left))
        ok, why = tl.starting_point(a, p)
        check("the pair is back at the start", ok, why)
        a.close(), p.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        if fl.OUT and os.path.isdir(fl.OUT):
            fails = sum(1 for r in pl.RESULTS if r.startswith("FAIL"))
            fl.save("report.txt", "\n".join(pl.RESULTS + ["", "%d PASS, %d FAIL" % (len(pl.RESULTS) - fails, fails)]))
            fl.banner("%d PASS, %d FAIL. Evidence in %s" % (len(pl.RESULTS) - fails, fails, fl.OUT))
