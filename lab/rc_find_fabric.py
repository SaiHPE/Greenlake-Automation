"""BL-20, read-only: find the vCenter and the two FC switches that D22U27's host ESX1 uses, so the
"Provision, then replicate" preset and runner scenario 7 can run with a real host.

    python lab\\rc_find_fabric.py

Reads the 3paradm password and the lab password for vCenter and switches from the app's .env
(LAB_ARRAY_PW, LAB_DEFAULT_PW). Every login is
read-only: array `show*` over SSH, the switch through the tool's own allowlisted Brocade client
(switchshow, fabricshow, nsshow), vCenter through the tool's own client (HBA list). Writes
~\\Downloads\\rc_find_fabric.zip with every answer and summary.txt.
"""
import os
import re
import shutil
import socket
import sys
import traceback

import paramiko

import rc_failover_lab as fl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from alletra_onboard.adapters.fabric.brocade_client import BrocadeClient  # noqa: E402
from alletra_onboard.adapters.vcenter.vcenter_client import VCenterClient  # noqa: E402

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "rc_find_fabric")
ARRAY = "10.64.122.99"
SWITCHES = ["10.64.122.145", "10.64.122.146"]           # the VZ pair, same /24 as D22U27
EXTRA_SWITCHES = sys.argv[1:]                            # any switch IP typed after the script name
VCENTERS = ["10.99.1.100", "10.54.154.226"]              # the VZ and LZ vCenters
HOSTS = {"ESX1": [], "ESX2": []}
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")
SUMMARY = []


def say(text):
    print(text)
    SUMMARY.append(text)


def save(name, text):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, re.sub(r"[^A-Za-z0-9_.-]+", "_", name)), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def wwn(text):
    return re.sub(r"[^0-9a-f]", "", text.lower())


def array_side(pw):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ARRAY, username="3paradm", password=pw, timeout=20, allow_agent=False, look_for_keys=False)

    def run(cmd):
        _i, o, e = c.exec_command(cmd, timeout=120)
        text = (o.read() + e.read()).decode("utf-8", "replace")
        save("array_" + cmd + ".txt", "# " + cmd + "\n" + text)
        return text

    ports = []
    for line in run("showport").splitlines():
        t = line.split()
        if len(t) >= 7 and re.fullmatch(r"\d+:\d+:\d+", t[0]) and t[1] == "target" and t[2] == "ready" and t[6] == "FC":
            ports.append((t[0], wwn(t[4])))
    say("D22U27 FC host ports ready: " + ", ".join("%s (%s)" % p for p in ports))
    targets = set()
    for port, _w in ports:
        sw = None
        for line in run("showportdev fcfabric " + port).splitlines():
            m = re.match(r"Logical Name:\s+(\S+)", line)
            if m:
                sw = m.group(1)
            t = line.split()
            if sw and "F-Port" in t and len(t) >= 2 and wwn(t[-2]) in {w for _p, w in ports}:
                targets.add(sw)
    say("Switches D22U27's ports log in to (from showportdev): " + ", ".join(sorted(targets)))
    for name in HOSTS:
        for line in run("showhost -d " + name).splitlines():
            for tok in line.split():
                if re.fullmatch(r"[0-9A-Fa-f]{16}", tok):
                    HOSTS[name].append(wwn(tok))
        HOSTS[name] = sorted(set(HOSTS[name]))
        say("%s WWPNs on D22U27: %s" % (name, ", ".join(HOSTS[name]) or "none"))
    c.close()
    return ports, targets


def by_dns(names):
    """The lab names switches like SW6505_D21U36_F1; try that and the dash form in DNS."""
    found = []
    for name in names:
        for guess in (name, name.replace("_", "-"), name.lower().replace("_", "-")):
            try:
                ip = socket.gethostbyname(guess)
            except OSError:
                continue
            say("DNS: %s -> %s" % (guess, ip))
            found.append(ip)
            break
        else:
            say("DNS: no address for %s" % name)
    return found


def switch_side(pw, ports, targets):
    seen, todo, found = set(), list(SWITCHES) + EXTRA_SWITCHES + by_dns(sorted(targets)), []
    while todo:
        ip = todo.pop(0)
        if ip in seen:
            continue
        seen.add(ip)
        try:
            with BrocadeClient(ip, "admin", pw) as sw:
                texts = {cmd: sw.read(cmd) for cmd in ("switchshow", "fabricshow", "nsshow")}
        except Exception as exc:  # noqa: BLE001
            say("switch %s: no read (%s)" % (ip, exc))
            continue
        for cmd, text in texts.items():
            save("switch_%s_%s.txt" % (ip, cmd), text)
        ns = wwn(texts["nsshow"])
        name = next((line.split(":", 1)[1].strip() for line in texts["switchshow"].splitlines() if line.startswith("switchName")), "?")
        mine = [p for p, w in ports if w and w in ns]
        hosts = [h for h, ws in HOSTS.items() if any(w in ns for w in ws)]
        say("switch %s (%s): D22U27 ports in its name server: %s; hosts: %s" % (ip, name, ", ".join(mine) or "none", ", ".join(hosts) or "none"))
        if mine:
            found.append(ip)
        for line in texts["fabricshow"].splitlines():
            named = re.search(r'"([^"]+)"', line)
            ip_m = re.search(r"\b(\d+\.\d+\.\d+\.\d+)\b", line)
            if named and ip_m and named.group(1) in targets:
                say("fabricshow on %s: %s is %s" % (ip, named.group(1), ip_m.group(1)))
                if ip_m.group(1) not in seen:
                    todo.append(ip_m.group(1))
    say("Switches that carry D22U27: " + (", ".join(found) or "none found"))


def vcenter_side(pw):
    for ip in VCENTERS:
        try:
            with VCenterClient(ip, "administrator@vsphere.local", pw) as vc:
                hbas = vc.host_fc_hbas()
        except Exception as exc:  # noqa: BLE001
            say("vCenter %s: no read (%s)" % (ip, exc))
            continue
        save("vcenter_%s_hbas.txt" % ip, "\n".join("%s %s %s" % (h.host_name, h.wwpn, h.os or "") for h in hbas))
        by_wwpn = {wwn(h.wwpn): h.host_name for h in hbas}
        for name, ws in HOSTS.items():
            match = sorted({by_wwpn[w] for w in ws if w in by_wwpn})
            say("vCenter %s: %s is %s" % (ip, name, ", ".join(match) or "not here"))
        say("vCenter %s: %d FC HBA ports on %d hosts" % (ip, len(hbas), len({h.host_name for h in hbas})))


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    apw = os.environ.get("ARRAY_PW") or fl.lab_secret("LAB_ARRAY_PW")
    lpw = os.environ.get("LAB_PW") or fl.lab_secret("LAB_DEFAULT_PW")
    say("paramiko " + paramiko.__version__)
    ports, targets = array_side(apw)
    switch_side(lpw, ports, targets)
    vcenter_side(lpw)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        save("script_stopped.txt", traceback.format_exc())
        raise
    finally:
        save("summary.txt", "\n".join(SUMMARY))
        print("\nDone. Send me " + shutil.make_archive(OUT, "zip", OUT))
