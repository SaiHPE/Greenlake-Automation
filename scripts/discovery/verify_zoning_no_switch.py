#!/usr/bin/env python3
r"""Switch-free FC zoning verification for an HPE Alletra MP B10000 — array-side, READ-ONLY.

Proves dual-fabric zoning is correct using ONLY the array (no Brocade switch, no ESXi needed).
The fabric name server is zoning-filtered, so what each array FC target port can SEE *is* its
effective zoning — and the array even prints the host name on each entry:

    showport                      -> the FC target ports that are 'ready' (skip iSCSI / loss_sync)
    showportdev ns <n:s:p>        -> the host WWPNs ZONED to that port + logged in (with host name)

Odd card-port (…:1, …:3) => odd switch / F1 ;  even (…:2, …:4) => even switch / F2. A host is
correctly zoned when it appears on BOTH fabrics. Calibrated to real B10000 output:
`showportdev ns` rows are  PtId LpID Hadr  Node_WWN  Port_WWN  ...  vp_WWN  SNN  Name  — we take the
Port_WWN (the initiator) and skip the array's own self-row (Node 2FF7… / Port == vp_WWN).

Optional cross-checks (off by default): --esxi <ips> adds the host view (esxcli), and --with-fabric
adds `showportdev fcfabric` (the WHOLE-SAN dump — large). Strictly read-only; creds via env/prompt.

    python verify_zoning_no_switch.py [--array 10.64.154.225] [--array-user 3paradm]
                                      [--esxi 10.64.159.14,10.64.159.63,10.64.159.64] [--with-fabric]

On a fresh box:  python -m pip install paramiko   then run the line above.
Password: set ALLETRA_PASSWORD, or type it at the prompt.
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

_HEX16 = re.compile(r"\b[0-9A-Fa-f]{16}\b")          # bare 16-hex WWPN (array showport / ns form)
_WWPN_COLON = re.compile(r"\b(?:[0-9A-Fa-f]{2}:){7}[0-9A-Fa-f]{2}\b")  # ESXi colon form


def norm(w: str) -> str:
    return "".join(c for c in w if c in "0123456789abcdefABCDEF").upper()


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


def target_ports(showport: str) -> list[tuple[str, str, str]]:
    """FC target ports that are READY -> [(n:s:p, fabric, array_port_wwpn)]. Skips iSCSI + loss_sync."""
    res = []
    for line in showport.splitlines():
        p = line.split()
        # columns: N:S:P  Mode  State  Node_WWN  Port_WWN  Type  Protocol  Label
        if len(p) >= 7 and ":" in p[0] and p[1] == "target" and p[2] == "ready" and "FC" in p:
            card_port = int(p[0].split(":")[2])
            fabric = "odd" if card_port % 2 == 1 else "even"
            res.append((p[0], fabric, norm(p[4])))
    return res


def parse_ns(block: str) -> list[tuple[str, str]]:
    """Parse `showportdev ns` -> [(host_name, host_port_wwpn)], excluding the array's own self-row."""
    out = []
    for line in block.splitlines():
        if not line.strip().startswith("0x"):     # data rows start with the PtId 0x......
            continue
        hexes = _HEX16.findall(line)
        if len(hexes) < 2:
            continue
        node, port = norm(hexes[0]), norm(hexes[1])
        vp = norm(hexes[2]) if len(hexes) >= 3 else ""
        if node.startswith("2FF7") or port == vp:   # the array listing its own target port — skip
            continue
        name = line.split()[-1]
        out.append((name, port))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Switch-free, array-side FC zoning verification (read-only).")
    ap.add_argument("--array", default="10.64.154.225")
    ap.add_argument("--array-user", default="3paradm")
    ap.add_argument("--ports", default="", help="override FC target ports, e.g. 0:3:1,0:3:2,1:3:1,1:3:2")
    ap.add_argument("--esxi", default="", help="optional comma list of ESXi IPs for an independent cross-check")
    ap.add_argument("--esxi-user", default="root")
    ap.add_argument("--with-fabric", action="store_true", help="also dump showportdev fcfabric (whole SAN — large)")
    ap.add_argument("--out", default="zoning-no-switch.txt")
    args = ap.parse_args()

    if not tcp_ok(args.array):
        print(f"Array {args.array} not reachable on 22 — check the IP / subnet.")
        return 2
    array_pw = os.environ.get("ALLETRA_PASSWORD") or getpass.getpass(f"Password for {args.array_user}@{args.array}: ")

    out = [f"# Switch-free zoning verification  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
           "# READ-ONLY: array showport + showportdev ns. No switch login.\n"]
    arr = connect(args.array, args.array_user, array_pw)
    showport = run(arr, "showport")
    out += ["===== showport =====", showport]

    ports = target_ports(showport)
    if args.ports:
        want = {x.strip() for x in args.ports.split(",") if x.strip()}
        ports = [(n, f, w) for (n, f, w) in ports if n in want]

    # name -> {"odd": set(wwpn), "even": set(wwpn)}
    per_host: dict[str, dict[str, set[str]]] = {}
    array_ports_by_fabric: dict[str, list[str]] = {"odd": [], "even": []}
    for nsp, fabric, arr_wwpn in ports:
        array_ports_by_fabric[fabric].append(f"{nsp} ({arr_wwpn})")
        block = run(arr, f"showportdev ns {nsp}")
        out += [f"\n===== showportdev ns {nsp}  [{fabric}/F{'1' if fabric == 'odd' else '2'}] =====", block]
        for name, wwpn in parse_ns(block):
            per_host.setdefault(name, {"odd": set(), "even": set()})[fabric].add(wwpn)
        if args.with_fabric:
            out += [f"\n===== showportdev fcfabric {nsp} (whole SAN) =====", run(arr, f"showportdev fcfabric {nsp}")]
    arr.close()

    # Optional independent ESXi cross-check (never gates the verdict).
    esxi_targets: dict[str, set[str]] = {}
    for h in [x.strip() for x in args.esxi.split(",") if x.strip()]:
        if not tcp_ok(h):
            out.append(f"\n[!] ESXi {h} unreachable on 22 — skipped")
            continue
        pw = os.environ.get("ESXI_PASSWORD") or getpass.getpass(f"Password for {args.esxi_user}@{h}: ")
        try:
            c = connect(h, args.esxi_user, pw)
            paths = run(c, "esxcli storage core path list")
            c.close()
        except Exception as exc:  # noqa: BLE001
            out.append(f"\n[!] ESXi {h}: {type(exc).__name__}: {str(exc)[:100]} (SSH on? password?)")
            continue
        tgt = set()
        for line in paths.splitlines():
            if "target identifier" in line.lower():
                m = _WWPN_COLON.findall(line)
                if m:
                    tgt.add(norm(m[-1]))
        esxi_targets[h] = tgt

    # ---- Verdict (from the array alone) ----
    v = ["\n==================  VERDICT — from the array alone, no switch  =================="]
    v.append(f"Array FC target ports (ready):  odd/F1 = {array_ports_by_fabric['odd']}   even/F2 = {array_ports_by_fabric['even']}")
    v.append(f"Hosts seen zoned to the array:  {len(per_host)}")
    all_ok = bool(per_host)
    for name in sorted(per_host):
        f = per_host[name]
        ok = bool(f["odd"]) and bool(f["even"])
        all_ok = all_ok and ok
        v.append(f"\n  {name}   ->   {'PASS (zoned on BOTH fabrics)' if ok else 'GAP'}")
        v.append(f"      odd/F1  : {sorted(f['odd'])  or 'NONE  <-- missing odd-fabric zone'}")
        v.append(f"      even/F2 : {sorted(f['even']) or 'NONE  <-- missing even-fabric zone'}")
    if esxi_targets:
        v.append("\n  ESXi cross-check (array target WWPNs each host can reach):")
        for h, t in esxi_targets.items():
            v.append(f"      {h}: {len(t)} target(s)")
    v.append(
        f"\nCONCLUSION: {'all ' + str(len(per_host)) + ' host(s) zoned on BOTH fabrics — ZONING CORRECT' if all_ok and per_host else 'zoning has GAPS'} "
        "— verified from the array alone; the switch was never contacted."
        + ("" if all_ok and per_host else "  (Switch login is needed only to CREATE the missing zones.)")
    )

    report = "\n".join(out + v) + "\n"
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(report)
    print("\n".join(v))
    print(f"\nFull raw output saved -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
