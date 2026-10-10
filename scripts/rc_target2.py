"""BL-20 option 0: a SECOND Remote Copy target between D22U27 and E18U31 over the SAME RCIP ports
and peer addresses, so a periodic (async) group has a target of its own (the array refused the
start on the Sync target: code 236 "Group with different modes on a single target is not supported").

    python scripts\\rc_target2.py create [output folder]   -> creates both sides, shows targets/links
    python scripts\\rc_target2.py remove [output folder]   -> removes both sides

Writes exactly one `creatercopytarget` per array (or one `removercopytarget`). Never `-cleargroups`;
a target in use by any group cannot be removed, so the six existing Sync groups are never at risk.
If E18U31 refuses after D22U27 accepted, the D22U27 target is removed again so the pair is left as found.
"""
import getpass
import os
import re
import sys
import time

import paramiko

MODE = sys.argv[1] if len(sys.argv) > 1 else "create"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.expanduser("~"), "Downloads", "rc_target2")
D22, E18 = ("D22U27", "10.64.122.99"), ("E18U31", "10.64.154.190")
#: (array, new target name, creatercopytarget links: local port -> peer RCIP address)
SIDES = [
    (D22, "AlletraMP_E18U31_async", "0:4:3:10.54.154.192 1:4:3:10.54.154.193"),
    (E18, "AlletraMP_D22U27_async", "0:4:3:10.54.122.92 1:4:3:10.54.122.93"),
]
SHOW = ["showrcopy targets", "showrcopy links", "showrctransport -rcip"]


def connect(host, pw):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username="3paradm", password=pw, timeout=20, allow_agent=False, look_for_keys=False)
    return c


def run(c, cmd):
    _i, o, e = c.exec_command(cmd, timeout=120)
    return (o.read() + e.read()).decode("utf-8", "replace")


def save(label, stage, cmd, text):
    d = os.path.join(OUT, label)
    os.makedirs(d, exist_ok=True)
    name = stage + "_" + re.sub(r"[^A-Za-z0-9]+", "_", cmd).strip("_") + ".txt"
    with open(os.path.join(d, name), "w", encoding="utf-8", newline="\n") as f:
        f.write("# " + cmd + "\n" + text)


def refused(text):
    # creatercopytarget / removercopytarget are silent on success; any sentence is a refusal
    # (live 2026-10-09: "Link 0:4:3:10.54.154.192 appears to exist on another target.").
    return bool(text.strip())


def show(clients, stage):
    for (label, _host), _name, _links in SIDES:
        print("\n==== %s after %s" % (label, stage))
        for cmd in SHOW:
            text = run(clients[label], cmd)
            save(label, stage, cmd, text)
            print("$ " + cmd)
            print(text.rstrip())


def write(clients, label, cmd, stage):
    print("\n[%s] $ %s" % (label, cmd))
    text = run(clients[label], cmd)
    save(label, stage, cmd, text)
    print(text.rstrip() or "(no output = accepted)")
    return text


def main():
    if MODE not in ("create", "remove"):
        sys.exit("first argument must be create or remove")
    pw0 = os.environ.get("ARRAY_PW") or getpass.getpass("3paradm password (both arrays): ")
    clients = {}
    for (label, host), _name, _links in SIDES:
        pw = pw0
        for _attempt in (1, 2):
            try:
                clients[label] = connect(host, pw)
                break
            except paramiko.AuthenticationException:
                pw = getpass.getpass("Login failed on %s (%s) - its 3paradm password: " % (label, host))
        if label not in clients:
            sys.exit("could not log in to %s; nothing was written" % label)

    show(clients, "before")

    if MODE == "remove":
        for (label, _host), name, _links in SIDES:
            write(clients, label, "removercopytarget " + name, "remove")
        show(clients, "remove")
        print("\nSaved under", OUT)
        return

    done = []
    for (label, _host), name, links in SIDES:
        text = write(clients, label, "creatercopytarget %s IP %s" % (name, links), "create")
        if refused(text):
            print("\nREFUSED on %s - stopping." % label)
            for prev_label, prev_name in done:
                write(clients, prev_label, "removercopytarget " + prev_name, "rollback")
            show(clients, "rollback" if done else "refused")
            print("\nSaved under", OUT)
            return
        done.append((label, name))

    print("\nBoth targets created; waiting 20 s for the links to come up...")
    time.sleep(20)
    show(clients, "create")
    for c in clients.values():
        c.close()
    print("\nSaved under", OUT)


if __name__ == "__main__":
    main()
