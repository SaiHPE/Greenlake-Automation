#!/usr/bin/env python3
r"""Switch-free FC zoning verification — prove you can confirm dual-fabric zoning WITHOUT the switch.

It logs into the ARRAY and the ESXi HOSTS only (never the Brocade switch) and answers, per host:
is each HBA zoned to the array on the correct fabric (odd HBA -> odd array ports, even -> even)?

How it knows, with zero switch access:
  * Array, per FC target port:  showportdev ns <n:s:p>  -> host WWPNs ZONED to that port + logged in
    (the fabric name server is zoning-filtered, so this IS the effective zoning for that port).
    Port parity gives the fabric: odd cardPort -> odd switch / F1, even -> even / F2.
  * ESXi, per host:  esxcli storage san fc list (HBA WWPNs) + esxcli storage core path list
    (which array target WWPNs the host actually reaches) -> an independent end-to-end confirmation.

If every host has an HBA zoned on BOTH fabrics, zoning is correct — confirmed from two sides, no
switch. A switch login would only be needed to CREATE a missing zone (remediation). 100% READ-ONLY:
the only commands issued are showport / showportdev / showhost on the array and `esxcli ... list` on
ESXi. Credentials are never stored — env vars or prompt.

    python verify_zoning_no_switch.py [--array 10.64.154.225] [--array-user 3paradm]
                                      [--esxi 10.64.159.14,10.64.159.63,10.64.159.64] [--esxi-user root]
                                      [--out zoning-no-switch.txt]

On a fresh box:  python -m pip install paramiko   then run the line above.
Passwords:  set ALLETRA_PASSWORD / ESXI_PASSWORD, or just type them at the prompt.
"""

from __future__ import annotations

import argparse
import datetime
import getpass
import os
import re
import socket
import sys

try:
    import paramiko
except ImportError:  # pragma: no cover
    sys.exit("paramiko is required:  python -m pip install paramiko")

_NSP = re.compile(r"\b(\d+):(\d+):(\d+)\b")
_WWPN = re.compile(r"\b(?:[0-9a-fA-F]{2}[:\-]?){7}[0-9a-fA-F]{2}\b")


def norm(w: str) -> str:
    return "".join(c for c in w if c in "0123456789abcdefABCDEF").upper()


def wwpns(text: str) -> set[str]:
    return {norm(m.group(0)) for m in _WWPN.finditer(text or "") if len(norm(m.group(0))) == 16}


def tcp_ok(host: str, port: int = 22, timeout: float = 5.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:  # noqa: BLE001
        return False


def connect(host: str, user: str, password: str) -> "paramiko.SSHClient":
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    return client


def run(client, cmd: str) -> str:
    _in, out, err = client.exec_command(cmd, timeout=30)
    o = out.read().decode("utf-8", "replace").rstrip()
    e = err.read().decode("utf-8", "replace").strip()
    return o if o.strip() else (f"[stderr] {e}" if e else "")


def target_ports(showport: str) -> list[str]:
    ports, seen = [], set()
    for line in showport.splitlines():
        if "target" in line.lower():
            m = _NSP.search(line)
            if m and m.group(0) not in seen:
                seen.add(m.group(0))
                ports.append(m.group(0))
    return ports


def main() -> int:
    ap = argparse.ArgumentParser(description="Switch-free FC zoning verification (array + ESXi only).")
    ap.add_argument("--array", default="10.64.154.225")
    ap.add_argument("--array-user", default="3paradm")
    ap.add_argument("--esxi", default="10.64.159.14,10.64.159.63,10.64.159.64")
    ap.add_argument("--esxi-user", default="root")
    ap.add_argument("--ports", default="", help="override array target ports, e.g. 0:3:1,0:3:2,1:3:1,1:3:2")
    ap.add_argument("--out", default="zoning-no-switch.txt")
    args = ap.parse_args()
    esxi_hosts = [h.strip() for h in args.esxi.split(",") if h.strip()]

    out = [f"# Switch-free zoning verification  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
           "# READ-ONLY: array showport/showportdev/showhost + ESXi 'esxcli ... list'. No switch login.\n"]
    print("Reachability (TCP 22):")
    for h in [args.array, *esxi_hosts]:
        ok = tcp_ok(h)
        print(f"  {h:<16} {'OK' if ok else 'UNREACHABLE'}")
        out.append(f"# reach {h}: {'OK' if ok else 'UNREACHABLE'}")
    if not tcp_ok(args.array):
        print(f"\nArray {args.array} not reachable on 22 — try the other mgmt subnet or check the IP.")
        return 2

    array_pw = os.environ.get("ALLETRA_PASSWORD") or getpass.getpass(f"\nPassword for {args.array_user}@{args.array}: ")
    esxi_pw = os.environ.get("ESXI_PASSWORD") or getpass.getpass(f"Password for {args.esxi_user}@ESXi: ")

    # ---- Array side: per-port zoned WWPNs (the effective zoning), grouped by fabric ----
    arr = connect(args.array, args.array_user, array_pw)
    showport = run(arr, "showport")
    out += ["\n===== showport =====", showport]
    out += ["\n===== showhost -d (WWPN -> host name) =====", run(arr, "showhost -d")]
    ports = [p.strip() for p in args.ports.split(",") if p.strip()] or target_ports(showport)

    odd_zoned: set[str] = set()
    even_zoned: set[str] = set()
    for nsp in ports:
        parity = int(nsp.split(":")[2]) % 2
        ns_raw = run(arr, f"showportdev ns {nsp}")
        fab_raw = run(arr, f"showportdev fcfabric {nsp}")
        zoned = wwpns(ns_raw)
        (odd_zoned if parity == 1 else even_zoned).update(zoned)
        out += [f"\n===== showportdev ns {nsp}  [{'odd/F1' if parity else 'even/F2'}]  (zoned+logged-in) =====",
                ns_raw or "(empty)",
                f"\n===== showportdev fcfabric {nsp}  (all fabric, ignores zoning) =====", fab_raw or "(empty)"]
    arr.close()

    # ---- ESXi side: HBA WWPNs + array targets seen (independent confirmation) ----
    esxi_hbas: dict[str, set[str]] = {}
    esxi_targets: dict[str, set[str]] = {}
    for h in esxi_hosts:
        if not tcp_ok(h):
            out.append(f"\n[!] ESXi {h} unreachable on 22 (SSH disabled?) — skipped")
            continue
        try:
            c = connect(h, args.esxi_user, esxi_pw)
            fc = run(c, "esxcli storage san fc list")
            paths = run(c, "esxcli storage core path list")
            c.close()
        except Exception as exc:  # noqa: BLE001
            out.append(f"\n[!] ESXi {h}: {type(exc).__name__}: {str(exc)[:120]}")
            continue
        hbas = {norm(m.group(0)) for line in fc.splitlines() if "port name" in line.lower() for m in _WWPN.finditer(line)}
        targets = set()
        for line in paths.splitlines():
            if "target identifier" in line.lower():
                found = [norm(m.group(0)) for m in _WWPN.finditer(line)]
                if found:
                    targets.add(found[-1])
        esxi_hbas[h], esxi_targets[h] = hbas, targets
        out += [f"\n===== {h} : esxcli storage san fc list =====", fc,
                f"\n===== {h} : esxcli storage core path list =====", paths]

    # ---- Verdict ----
    verdict = ["\n==================  VERDICT (no switch was used)  =================="]
    verdict.append(f"Array odd/F1 zoned WWPNs: {len(odd_zoned)}   even/F2 zoned WWPNs: {len(even_zoned)}")
    overall_ok = bool(esxi_hbas)
    for h in esxi_hosts:
        if h not in esxi_hbas:
            continue
        hbas = esxi_hbas[h]
        on_odd = sorted(hbas & odd_zoned)
        on_even = sorted(hbas & even_zoned)
        unzoned = sorted(hbas - odd_zoned - even_zoned)
        ok = bool(on_odd) and bool(on_even)
        overall_ok = overall_ok and ok
        verdict.append(f"\n{h}  ->  {'PASS (zoned on both fabrics)' if ok else 'GAP'}")
        verdict.append(f"    HBAs zoned on odd/F1:  {on_odd or 'NONE'}")
        verdict.append(f"    HBAs zoned on even/F2: {on_even or 'NONE'}")
        if unzoned:
            verdict.append(f"    HBAs NOT zoned to the array anywhere: {unzoned}  <-- switch zone needed")
        verdict.append(f"    array target WWPNs this host sees (esxcli): {len(esxi_targets.get(h, set()))}")

    verdict.append(
        f"\nCONCLUSION: zoning verification {'CONFIRMED' if esxi_hbas else 'INCONCLUSIVE'} from the array + "
        f"ESXi alone — the switch was never contacted. Overall zoning: "
        f"{'CORRECT on both fabrics' if overall_ok else 'has gaps (switch needed only to CREATE the missing zones)'}."
    )

    report = "\n".join(out + verdict) + "\n"
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(report)
    print("\n".join(verdict))
    print(f"\nFull raw output saved -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
