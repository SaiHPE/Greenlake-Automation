"""BL-20: free the lab target so the periodic (async) path can run through the UI, and put the six
Sync groups back afterwards. Operator's decision 2026-10-10: the six may be removed and rebuilt.

    python scripts\\rc_rebuild.py save        [dir]  read-only: record every group's definition + exports (required first)
    python scripts\\rc_rebuild.py remove      [dir]  stop + remove the six groups from their Primary side (asks REMOVE)
    python scripts\\rc_rebuild.py ui-cleanup  [dir]  run the removal set of the latest UI Replication apply (from the app)
    python scripts\\rc_rebuild.py rebuild     [dir]  recreate the six from the saved definitions, start them (asks REBUILD)
    python scripts\\rc_rebuild.py compare     [dir]  diff groups / volume sets / exports against what `save` recorded

Default dir: ~\\Downloads\\rc_rebuild. Volumes are KEPT on both arrays (removercopygroup without
-removevv), so `rebuild` re-admits the same primary and secondary volumes and the start is a full
initial copy. Primary side, target, mode, CPGs, policies and volume pairs are read from the arrays by
`save`, never assumed.
"""
import difflib
import getpass
import json
import os
import re
import sys
import time
import urllib.request

import paramiko

ACTION = sys.argv[1] if len(sys.argv) > 1 else ""
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.expanduser("~"), "Downloads", "rc_rebuild")
ARRAYS = {"D22U27": "10.64.122.99", "E18U31": "10.64.154.190"}
PASSWORDS = {}
BASE_GROUPS = ["300gb", "APP_Test", "Intern_Automation", "Intern_Automation2", "Test-RCG", "Test-RCG2"]
CAPTURE = ["showrcopy", "showrcopy groups", "showrcopy -d groups", "showrcopy targets", "showvvset",
           "showvlun -t", "showvlun", "showhost", "showhostset -summary", "showvv -showcols Name,VSize_MB,Prov,UsrCPG"]
DIFFED = ["showrcopy groups", "showvvset", "showvlun -t"]
APP = "http://127.0.0.1:8765"
POLICY_WORDS = ("auto_", "no_", "over_per_alert", "path_management", "active_active", "mt_pp")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")


def connect(host, pw):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username="3paradm", password=pw, timeout=20, allow_agent=False, look_for_keys=False)
    return c


def run(c, cmd, timeout=300):
    _i, o, e = c.exec_command(cmd, timeout=timeout)
    try:
        return (o.read() + e.read()).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001 - socket timeout: the array sent nothing for `timeout` s
        return "Error: no answer from the array within %d s (%s); the command may still be running" % (timeout, type(exc).__name__)


def fname(cmd):
    return re.sub(r"[^A-Za-z0-9]+", "_", cmd).strip("_") + ".txt"


def save_text(stage, label, cmd, text):
    d = os.path.join(OUT, stage, label)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, fname(cmd)), "w", encoding="utf-8", newline="\n") as f:
        f.write("# " + cmd + "\n" + text)


def capture(clients, stage):
    for label, c in clients.items():
        for cmd in CAPTURE:
            save_text(stage, label, cmd, run(c, cmd))
    print("captured -> %s" % os.path.join(OUT, stage))


def write(clients, label, cmd, stage):
    print("[%s] $ %s" % (label, cmd))
    text = run(clients[label], cmd)
    save_text(stage, label, cmd, text)
    print("    " + (text.strip().replace("\n", "\n    ") or "(no output)"))
    return text.strip()


def base(name):
    return re.sub(r"\.r\d+$", "", name)


def parse_groups(text):
    """`showrcopy -d groups` -> [{name, target, status, role, mode, local_cpg, remote_cpg, options, volumes}]."""
    groups, cur = [], None
    for line in text.splitlines():
        t = line.split()
        if not t or t[0] in ("Name", "LocalVV") or line.startswith("#"):
            continue
        if not line.startswith(" ") and len(t) >= 6 and t[1].isdigit():
            rest = t[6:]
            lcpg = rcpg = ""
            if len(rest) >= 2 and not any(w in rest[0] for w in POLICY_WORDS):
                lcpg, rcpg, rest = rest[0], rest[1], rest[2:]
            options = [o.strip() for o in " ".join(rest).split(",")
                       if o.strip() and not o.strip().startswith(("Last-Sync", "Period "))]
            cur = {"name": t[0], "target": t[2], "status": t[3], "role": t[4], "mode": t[5],
                   "local_cpg": lcpg, "remote_cpg": rcpg, "options": options, "volumes": []}
            groups.append(cur)
        elif line.startswith("  ") and cur is not None and len(t) >= 5:
            cur["volumes"].append({"local": t[0], "remote": t[2], "local_set": t[-2], "remote_set": t[-1]})
    return groups


def parse_sets(text):
    sets, cur = {}, None
    for line in text.splitlines():
        t = line.split()
        if not t or t[0] in ("Id", "#") or set(line.strip()) <= set("-") or "total" in t:
            continue
        if t[0].isdigit() and len(t) >= 2:
            cur = t[1]
            sets[cur] = [m for m in t[2:] if m != "--"]
        elif cur and len(t) == 1:
            sets[cur].append(t[0])
    return sets


def login():
    pw0 = os.environ.get("ARRAY_PW") or getpass.getpass("3paradm password (both arrays): ")
    clients = {}
    for label, host in ARRAYS.items():
        pw = pw0
        for _attempt in (1, 2):
            try:
                clients[label] = connect(host, pw)
                PASSWORDS[label] = pw
                break
            except paramiko.AuthenticationException:
                pw = getpass.getpass("Login failed on %s (%s) - its 3paradm password: " % (label, host))
        if label not in clients:
            sys.exit("could not log in to %s; nothing was done" % label)
    return clients


def primaries(clients):
    """{base name: (array, local name, status)} for every group whose Primary side is on either array."""
    found, others = {}, []
    for label, c in clients.items():
        for g in parse_groups(run(c, "showrcopy -d groups")):
            if g["name"].startswith("zz_rc_"):
                continue
            if base(g["name"]) not in BASE_GROUPS:
                others.append("%s: '%s' (%s, %s)" % (label, g["name"], g["status"], g["role"]))
            elif g["role"] == "Primary":
                found[base(g["name"])] = (label, g["name"], g["status"])
    return found, others


def do_save(clients):
    first = not os.path.exists(os.path.join(OUT, "groups.json"))
    capture(clients, "saved" if first else "resaved_" + time.strftime("%H%M%S"))
    defs = []
    for label, c in clients.items():
        for g in parse_groups(run(c, "showrcopy -d groups")):
            if g["role"] == "Primary" and base(g["name"]) in BASE_GROUPS:
                defs.append(dict(g, array=label))
    sets = {label: parse_sets(run(c, "showvvset")) for label, c in clients.items()}
    missing = [g for g in BASE_GROUPS if g not in {base(d["name"]) for d in defs}]
    # the first save is the one `rebuild` and `compare` use; a later save never replaces it
    path = os.path.join(OUT, "groups.json" if first else "groups_%s.json" % time.strftime("%H%M%S"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"groups": defs, "sets": sets, "saved": time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)
    print("\nSaved %d group definition(s) -> %s" % (len(defs), path))
    for d in defs:
        print("  %-18s on %s  %s %s  cpg %s/%s  [%s]  %d volume(s)%s" % (
            d["name"], d["array"], d["mode"], d["status"], d["local_cpg"] or "-", d["remote_cpg"] or "-",
            ",".join(d["options"]) or "-", len(d["volumes"]),
            "  set %s -> %s" % (d["volumes"][0]["local_set"], d["volumes"][0]["remote_set"]) if d["volumes"] and d["volumes"][0]["local_set"] != "NA" else ""))
    if missing:
        print("NOT FOUND as Primary on either array: " + ", ".join(missing))
    return defs, missing


def load_defs():
    path = os.path.join(OUT, "groups.json")
    if not os.path.exists(path):
        sys.exit("no %s - run `save` first" % path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def latest_ui_removals():
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def get(path):
        with opener.open(APP + path, timeout=30) as r:
            return json.loads(r.read())

    best = None
    for run_rec in get("/runs")["runs"]:
        for ev in get("/runs/%s/events" % run_rec["run_id"])["events"]:
            if ev["event_type"] in ("replication.applied", "replication.apply.failed") and "result" in ev.get("data", {}):
                if best is None or ev["created_at"] > best["created_at"]:
                    best = ev
    if best is None:
        sys.exit("no Replication apply found in the app's runs")
    res = best["data"]["result"]
    print("Latest UI apply: run %s at %s - %s" % (best["run_id"], best["created_at"], best["message"]))
    return res.get("removals_a", []), res.get("removals_b", [])


def parse_vlun_templates(text):
    """`showvlun -t`: Lun VVName HostName -Host_WWN/iSCSI_Name- Port Type -> [{lun, vv, host, port}]."""
    out = []
    for line in text.splitlines():
        t = line.split()
        if len(t) >= 6 and t[0].isdigit():
            out.append({"lun": t[0], "vv": t[1], "host": t[2], "port": t[4]})
    return out


def vlun_args(v):
    """The `<vv> <lun> ...` arguments shared by createvlun / removevlun for one template."""
    no = ("---", "--", "-")
    if v["host"] in no:
        return "%s %s %s" % (v["vv"], v["lun"], v["port"])                     # port presents
    if v["port"] not in no:
        return "%s %s %s %s" % (v["vv"], v["lun"], v["port"], v["host"])         # matched set
    return "%s %s %s" % (v["vv"], v["lun"], v["host"])                          # host sees / host set


def secondary_exports(clients, peer, d):
    vols = {v["remote"] for v in d["volumes"]}
    sets = {"set:" + v["remote_set"] for v in d["volumes"] if v["remote_set"] != "NA"}
    return [v for v in parse_vlun_templates(run(clients[peer], "showvlun -t")) if v["vv"] in vols | sets]


def admit_wsapi(host, pw, group, volume, target, secondary):
    """The product's own path: WSAPI addVolumeToRemoteCopyGroup with the EXISTING secondary (no
    volumeAutoCreation). WSAPI answers with an error where the CLI would sit on a prompt."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
    from alletra_onboard.adapters.array.wsapi_client import WsapiClient
    print("[%s] WSAPI addVolumeToRemoteCopyGroup %s %s -> %s:%s" % (host, group, volume, target, secondary))
    try:
        with WsapiClient(host, "3paradm", pw) as w:
            w._require().addVolumeToRemoteCopyGroup(group, volume, [{"targetName": target, "secVolumeName": secondary}])
        print("    admitted")
        return ""
    except Exception as exc:  # noqa: BLE001
        print("    Error: %s" % exc)
        return "Error: %s" % exc


PEER_OF = {"D22U27": "E18U31", "E18U31": "D22U27"}


def main():
    if ACTION == "cli":
        # python scripts\rc_rebuild.py cli <D22U27|E18U31> "<command>" ["<command>" ...] - one SSH session, answers saved
        label, cmds = sys.argv[2], sys.argv[3:]
        if label not in ARRAYS or not cmds:
            sys.exit("usage: cli D22U27|E18U31 \"<command>\" ...")
        pw = os.environ.get("ARRAY_PW") or getpass.getpass("3paradm password (%s): " % label)
        c = connect(ARRAYS[label], pw)
        for cmd in cmds:
            text = run(c, cmd)
            save_text("cli", label, cmd, text)
            print("\n[%s] $ %s\n%s" % (label, cmd, text.rstrip()))
        c.close()
        return
    if ACTION not in ("save", "remove", "ui-cleanup", "rebuild", "compare"):
        sys.exit("first argument must be save, remove, ui-cleanup, rebuild, compare or cli")
    os.makedirs(OUT, exist_ok=True)

    if ACTION == "ui-cleanup":
        a_lines, b_lines = latest_ui_removals()
        clients = login()
        capture(clients, "ui_before_cleanup")
        for label, lines in (("D22U27", a_lines), ("E18U31", b_lines)):
            for cmd in lines:
                write(clients, label, cmd, "ui_cleanup")
        for label, c in clients.items():
            print("\n==== %s $ showrcopy groups zz_rc*" % label)
            print(run(c, "showrcopy groups zz_rc*").strip() or "(none)")
        return

    clients = login()

    if ACTION == "save":
        do_save(clients)

    elif ACTION == "remove":
        if not os.path.exists(os.path.join(OUT, "groups.json")):
            sys.exit("no saved definitions - run `save` first")
        saved = {base(d["name"]): d for d in load_defs()["groups"]}
        found, others = primaries(clients)
        if others:
            sys.exit("Groups other than the six are on the arrays - nothing was removed:\n  " + "\n  ".join(others))
        todo = [g for g in BASE_GROUPS if g in found]
        unsaved = [g for g in todo if g not in saved]
        if unsaved:
            sys.exit("no saved definition for %s - nothing was removed" % ", ".join(unsaved))
        if not todo:
            sys.exit("none of the six is on the arrays - nothing to remove")
        do_save(clients)
        unexport = {}
        for g in todo:
            if "active_active" in saved[g]["options"]:
                peer = PEER_OF[found[g][0]]
                unexport[g] = (peer, secondary_exports(clients, peer, saved[g]))
        print("\nThis stops and REMOVES: %s (volumes are kept on both arrays)." % ", ".join(todo))
        for g, (peer, vl) in unexport.items():
            print("%s is Peer Persistence: the array requires its secondary unexported first. On %s:" % (g, peer))
            for v in vl:
                print("    removevlun -f " + vlun_args(v))
            if not vl:
                print("    (no template export found for the secondary - the removal may still be refused)")
        if input("Type REMOVE to continue: ").strip() != "REMOVE":
            sys.exit("not removed")
        path = os.path.join(OUT, "unexported.json")
        record = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
        failed = []
        for g in todo:
            label, name, status = found[g]
            if status == "Started":
                write(clients, label, "stoprcopygroup -f " + name, "remove")
            for v in unexport.get(g, (None, []))[1]:
                # Peer Persistence (live 2026-10-10): "Please unexport the secondary volume so the host only
                # has access to the primary volume and retry." `rebuild` exports it again.
                answer = write(clients, unexport[g][0], "removevlun -f " + vlun_args(v), "remove")
                if "Error" not in answer:
                    record.append(dict(v, array=unexport[g][0], group=g))
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(record, f, indent=2)
            answer = write(clients, label, "removercopygroup -f " + name, "remove")
            if "Error" in answer or "Failure" in answer:
                failed.append(g)
        time.sleep(3)
        for label, c in clients.items():
            print("\n==== %s $ showrcopy groups" % label)
            print(run(c, "showrcopy groups").strip())
        capture(clients, "after_remove")
        if failed:
            print("\nNOT removed: %s - see the array's answer above. Do not run the UI test yet." % ", ".join(failed))
        else:
            print("\nThe target now carries no groups. Run the UI test next.")

    elif ACTION == "rebuild":
        saved = load_defs()
        defs, sets = saved["groups"], saved["sets"]
        found, others = primaries(clients)
        live_groups = {lbl: {g["name"]: g for g in parse_groups(run(c, "showrcopy -d groups"))} for lbl, c in clients.items()}
        live = [x for x in others] + ["%s: %s" % (lbl, n) for lbl, gs in live_groups.items() for n in gs if n.startswith("zz_rc_")]
        if live:
            sys.exit("other groups are on the arrays (remove the tool's zz_rc_* first: ui-cleanup):\n  " + "\n  ".join(live))
        present = [g for g in BASE_GROUPS if g in found]
        print("Rebuilding %d group(s) saved %s.%s" % (len(defs), saved["saved"],
              "  Already present, will be completed not recreated: %s." % ", ".join(present) if present else ""))
        if input("Type REBUILD to continue: ").strip() != "REBUILD":
            sys.exit("not rebuilt")
        peer_of = {"D22U27": "E18U31", "E18U31": "D22U27"}
        for d in defs:
            label, peer, g, target = d["array"], peer_of[d["array"]], d["name"], d["target"]
            mode = "sync" if d["mode"].lower() == "sync" else "periodic"
            print("\n==== %s on %s" % (g, label))
            existing = live_groups[label].get(g)
            if existing is None:
                cpg = " -usr_cpg %s %s:%s" % (d["local_cpg"], target, d["remote_cpg"]) if d["local_cpg"] and d["remote_cpg"] else ""
                if write(clients, label, "creatercopygroup%s %s %s:%s" % (cpg, g, target, mode), "rebuild"):
                    print("    -> create refused; skipping this group")
                    continue
                admitted, have_opts, status = set(), [], ""
            else:
                # a re-run after an interrupted rebuild: finish only what is missing
                admitted = {v["local"] for v in existing["volumes"]}
                have_opts, status = existing["options"], existing["status"]
                print("    exists (%s, %d volume(s) admitted) - completing" % (status, len(admitted)))
            vols = d["volumes"]
            lset, rset = (vols[0]["local_set"], vols[0]["remote_set"]) if vols else ("NA", "NA")
            if vols and lset != "NA" and rset != "NA":
                if not admitted:
                    peer_sets = parse_sets(run(clients[peer], "showvvset"))
                    if rset not in peer_sets:
                        members = sets.get(peer, {}).get(rset) or [v["remote"] for v in vols]
                        write(clients, peer, "createvvset %s %s" % (rset, " ".join(members)), "rebuild")
                    write(clients, label, "admitrcopyvv set:%s %s %s:%s" % (lset, g, target, rset), "rebuild")
            else:
                for v in vols:
                    if v["local"] not in admitted:
                        # live 2026-10-10: the CLI admit of an existing secondary never answered; WSAPI does
                        admit_wsapi(ARRAYS[label], PASSWORDS[label], g, v["local"], target, v["remote"])
            for opt in d["options"]:
                if opt not in have_opts:
                    write(clients, label, "setrcopygroup pol %s %s" % (opt, g), "rebuild")
            if status != "Started":
                write(clients, label, "startrcopygroup " + g, "rebuild")
            else:
                print("    already Started")
        print("\n==== Peer Persistence secondary exports, back as the first save recorded them")
        for d in (x for x in defs if "active_active" in x["options"]):
            peer = PEER_OF[d["array"]]
            saved_vl = os.path.join(OUT, "saved", peer, fname("showvlun -t"))
            if not os.path.exists(saved_vl):
                print("    no saved showvlun -t for %s - export %s's secondary by hand" % (peer, d["name"]))
                continue
            vols = {v["remote"] for v in d["volumes"]} | {"set:" + v["remote_set"] for v in d["volumes"] if v["remote_set"] != "NA"}
            now = {vlun_args(v) for v in parse_vlun_templates(run(clients[peer], "showvlun -t"))}
            for v in parse_vlun_templates(open(saved_vl, encoding="utf-8").read()):
                if v["vv"] in vols and vlun_args(v) not in now:
                    write(clients, peer, "createvlun " + vlun_args(v), "rebuild")
        time.sleep(5)
        for label, c in clients.items():
            print("\n==== %s $ showrcopy groups" % label)
            print(run(c, "showrcopy groups").strip())
        capture(clients, "after_rebuild")
        print("\nInitial copies run now; check `compare` once every volume says Synced.")

    elif ACTION == "compare":
        capture(clients, "compare")
        same = True
        for label in ARRAYS:
            for cmd in DIFFED:
                paths = [os.path.join(OUT, s, label, fname(cmd)) for s in ("saved", "compare")]
                if not os.path.exists(paths[0]):
                    print("nothing saved for %s %s" % (label, cmd))
                    continue
                a, b = (open(p, encoding="utf-8").read().splitlines() for p in paths)
                diff = list(difflib.unified_diff(a, b, "saved/" + label + " " + cmd, "now", lineterm="", n=1))
                if diff:
                    same = False
                    print("\n".join(diff))
        print("\nIDENTICAL to what was saved (%s)." % ", ".join(DIFFED) if same else "\nDIFFERS from what was saved - see above.")

    for c in clients.values():
        c.close()
    print("\nSaved under", OUT)


if __name__ == "__main__":
    main()
