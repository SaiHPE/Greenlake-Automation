"""Read-only look at the three lab arrays to decide how async replication can be tested (BL-20):
is VZ alive, does it have RCIP ports, do the replication networks route to each other (one
`controlport rcip ping` each way -- ICMP only, changes nothing), are the spare x:4:4 ports cabled.

    python scripts\\rc_options.py <output folder>

Asks for the 3paradm password once (tried on all three arrays; asks again per array if refused).
"""
import getpass
import os
import re
import sys

import paramiko

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.expanduser("~"), "Downloads", "rc_options")
ARRAYS = [("D22U27", "10.64.122.99"), ("E18U31", "10.64.154.190"), ("VZ", "10.64.122.140")]
READS = ["showsys", "showversion", "shownet", "showport", "showport -rcip", "showrctransport -rcip",
         "showrcopy targets", "showrcopy links", "showcpg", "showvvset"]


def connect(host, pw):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username="3paradm", password=pw, timeout=20, allow_agent=False, look_for_keys=False)
    return c


def run(c, cmd):
    _i, o, e = c.exec_command(cmd, timeout=120)
    return (o.read() + e.read()).decode("utf-8", "replace")


def save(label, cmd, text):
    d = os.path.join(OUT, label)
    os.makedirs(d, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9]+", "_", cmd).strip("_") + ".txt"
    with open(os.path.join(d, name), "w", encoding="utf-8", newline="\n") as f:
        f.write("# " + cmd + "\n" + text)


def main():
    pw0 = os.environ.get("ARRAY_PW") or getpass.getpass("3paradm password (tried on all three arrays): ")
    clients, rcip = {}, {}
    for label, host in ARRAYS:
        pw = pw0
        for _attempt in (1, 2):
            try:
                clients[label] = connect(host, pw)
                break
            except paramiko.AuthenticationException:
                pw = getpass.getpass("Login failed on %s (%s) - its 3paradm password: " % (label, host))
            except Exception as exc:  # noqa: BLE001
                print("%s (%s): NOT REACHABLE - %s %s" % (label, host, type(exc).__name__, exc))
                break
        c = clients.get(label)
        if c is None:
            continue
        print("\n==== %s (%s)" % (label, host))
        for cmd in READS:
            text = run(c, cmd)
            save(label, cmd, text)
            if cmd in ("showsys", "showport -rcip", "showrctransport -rcip", "showrcopy targets"):
                print("$ " + cmd)
                print(text.rstrip())
            if cmd == "showport":
                print("$ showport (slot 4 only)")
                print("\n".join(line for line in text.splitlines() if re.match(r"^[01]:4:\d", line)))
        rcip[label] = re.findall(r"^\d:\d:\d\s+\S+\s+\S+\s+(\d+\.\d+\.\d+\.\d+)", run(c, "showport -rcip"), re.M)

    def ping(src, dst_ip, port="0:4:3"):
        c = clients.get(src)
        if c is None or not dst_ip:
            return
        cmd = "controlport rcip ping -c 3 %s %s" % (dst_ip, port)
        text = run(c, cmd)
        save(src, cmd, text)
        print("\n[%s] $ %s\n%s" % (src, cmd, text.rstrip()))

    vz = rcip.get("VZ", [])
    d22 = rcip.get("D22U27", [])
    e18 = rcip.get("E18U31", [])
    print("\n==== RCIP addresses: D22U27 %s | E18U31 %s | VZ %s" % (d22, e18, vz))
    if vz:
        ping("D22U27", vz[0])
        ping("E18U31", vz[0])
        if d22:
            ping("VZ", d22[0])
        if e18:
            ping("VZ", e18[0])
    else:
        print("VZ has no configured RCIP port (or was not reachable) - nothing to ping.")
    for c in clients.values():
        c.close()
    print("\nSaved under", OUT)


if __name__ == "__main__":
    main()
