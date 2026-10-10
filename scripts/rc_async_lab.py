"""BL-20: the periodic (async) path through the tool's OWN modules, on the lab pair with the six
Sync groups STOPPED (`rc_option1.py stop`).

The product's R2 finding counts stopped groups too, on purpose: a periodic group started beside
stopped Sync groups could keep them from restarting, so the step refuses. This harness drops exactly
that one finding and runs the same read / check / plan / apply / verify functions the step runs
(application.replication.*); every write is the product's WSAPI code.

    python scripts\\rc_async_lab.py apply  [sheet.xlsx] [dir]   read, check, plan, APPLY (asks first), verify, capture
    python scripts\\rc_async_lab.py verify [sheet.xlsx] [dir]   verify again from the saved plan, capture again

Defaults: ~\\Downloads\\D22U27_replication_async.xlsx, ~\\Downloads\\rc_async.
"""
import json
import os
import sys
import time

from alletra_onboard.application.platform.init_sheet import parse_workbook_bytes
from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.replication.apply import apply_plan
from alletra_onboard.application.replication.plan import build_plan, check
from alletra_onboard.application.replication.read import read_array
from alletra_onboard.application.replication.verify import verify
from alletra_onboard.domain.replication import ReplicationPlan

ACTION = sys.argv[1] if len(sys.argv) > 1 else ""
SHEET = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.expanduser("~"), "Downloads", "D22U27_replication_async.xlsx")
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.expanduser("~"), "Downloads", "rc_async")
CAPTURE = ["showrcopy", "showrcopy groups", "showrcopy -d groups", "showvvset", "showvv -showcols Name,VSize_MB"]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")   # the product's sentences carry arrows; never die on a console code page


def save(name, text):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def capture(intent, stage):
    for label, creds in (("D22U27", intent.array), ("E18U31", intent.replication.peer)):
        with make_array_cli(creds) as cli:
            for cmd in CAPTURE:
                text = cli.run(cmd)
                d = os.path.join(OUT, stage, label)
                os.makedirs(d, exist_ok=True)
                with open(os.path.join(d, cmd.replace(" -", "_").replace(" ", "_").replace(",", "_") + ".txt"), "w", encoding="utf-8", newline="\n") as f:
                    f.write("# " + cmd + "\n" + text)
    print("captured -> %s" % os.path.join(OUT, stage))


def show_verification(v):
    print("\n==== Verify: links %s - %s" % ("OK" if v.links_ok else "NOT OK", v.links_detail))
    for g in v.groups:
        print("  %-18s %-16s %s" % (g.group, g.verdict.upper(), g.detail))
        if g.next_step:
            print("  %-18s next: %s" % ("", g.next_step))
    for n in v.notes:
        print("  note: " + n)
    if v.error:
        print("  error: " + v.error)


def cleanup(intent):
    """Run the saved removal set: the A lines on this array, then the B lines on the peer, over SSH
    with the sheet's credentials. Prints each array's answer."""
    import paramiko

    path = os.path.join(OUT, "removals.txt")
    if not os.path.exists(path):
        sys.exit("no %s - nothing to clean up" % path)
    sides, side = {"A": [], "B": []}, None
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("# A"):
            side = "A"
        elif line.startswith("# B"):
            side = "B"
        elif line and side:
            sides[side].append(line)
    for side, creds in (("A", intent.array), ("B", intent.replication.peer)):
        if not sides[side]:
            continue
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(creds.host, username=creds.username, password=creds.password.get_secret_value(), timeout=20,
                  allow_agent=False, look_for_keys=False)
        print("\n==== %s (%s)" % (side, creds.host))
        for cmd in sides[side]:
            _i, o, e = c.exec_command(cmd, timeout=300)
            text = (o.read() + e.read()).decode("utf-8", "replace").rstrip()
            print("$ " + cmd)
            print(text or "(no output)")
        c.close()
    capture(intent, "after_cleanup")
    print("\nCleanup done. Now: rc_option1.py start, compare, unprep.")


def main():
    if ACTION not in ("apply", "verify", "cleanup"):
        sys.exit("first argument must be apply, verify or cleanup")
    with open(SHEET, "rb") as f:
        intent = parse_workbook_bytes(f.read(), complete=True).provisioning_intent
    if intent.replication is None:
        sys.exit("the sheet has no Replication tab")
    print("Sheet: %s - rows: %s" % (SHEET, ", ".join("%s %s -> %s" % (r.vvset, r.mode, r.peer_cpg) for r in intent.replication.protections)))

    if ACTION == "cleanup":
        cleanup(intent)
        return

    if ACTION == "verify":
        with open(os.path.join(OUT, "plan.json"), encoding="utf-8") as f:
            plan = ReplicationPlan.model_validate_json(f.read())
        v = verify(intent, plan, progress=print)
        show_verification(v)
        n = 1 + sum(1 for x in os.listdir(OUT) if x.startswith("verify_") and x.endswith(".json"))
        save("verify_%d.json" % n, v.model_dump_json(indent=2))
        capture(intent, "capture_%d" % n)
        return

    a = read_array(intent.array, progress=print)
    b = read_array(intent.replication.peer, progress=print)
    report = check(a, b, intent.replication)
    if report.error:
        sys.exit("read failed: " + report.error)
    allowed = [x for x in report.findings if x.startswith("Target '") and "already carries" in x and "cannot be started there" in x]
    print("\n==== Findings (%d):" % len(report.findings))
    for x in report.findings:
        print(("  [dropped for this lab run] " if x in allowed else "  [BLOCKING] ") + x)
    plan = build_plan(report, intent.replication, intent)
    plan.blockers = [x for x in plan.blockers if x not in allowed]
    save("report.json", report.model_dump_json(indent=2))
    save("plan.json", plan.model_dump_json(indent=2))
    if plan.blockers or plan.error:
        sys.exit("\nThe plan still has blockers - nothing was written:\n  " + "\n  ".join(plan.blockers + ([plan.error] if plan.error else [])))
    print("\n==== Plan: %d to create, %d exist" % (sum(1 for x in plan.actions if x.state == "create"), sum(1 for x in plan.actions if x.state == "exists")))
    calls = sorted(((c.seq, c.where, c.cli) for x in plan.actions for c in x.calls), key=lambda t: t[0])
    for seq, where, cli in calls:
        print("  %2d  %s  %s" % (seq, where, cli))
    for n in plan.notes:
        print("  note: " + n)

    if input("\nType APPLY to write these %d calls to the arrays: " % len(calls)).strip() != "APPLY":
        sys.exit("not applied")
    started = time.strftime("%H:%M:%S")
    result = apply_plan(plan, intent, progress=print)
    save("result.json", result.model_dump_json(indent=2))
    print("\n==== Result (apply started %s):" % started)
    for o in result.outcomes:
        print("  %-13s %-20s %s  %-8s %s" % (o.kind, o.name, o.where, o.status, o.detail))
    if result.error:
        print("  ERROR: " + result.error)
    print("\n==== Removal set - A (%s):" % intent.array.host)
    print("\n".join("  " + x for x in result.removals_a) or "  (none)")
    print("==== Removal set - B (%s):" % intent.replication.peer.host)
    print("\n".join("  " + x for x in result.removals_b) or "  (none)")
    save("removals.txt", "# A %s\n%s\n# B %s\n%s\n" % (intent.array.host, "\n".join(result.removals_a), intent.replication.peer.host, "\n".join(result.removals_b)))

    v = verify(intent, plan, progress=print)
    show_verification(v)
    save("verify_1.json", v.model_dump_json(indent=2))
    capture(intent, "capture_1")
    print("\nSaved under %s. Run `verify` again in ~6 minutes (period 5 min), then paste the removal set A then B." % OUT)


if __name__ == "__main__":
    main()
