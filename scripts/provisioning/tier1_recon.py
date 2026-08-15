#!/usr/bin/env python3
# =====================================================================
# READ-ONLY recon for the tier-1 throwaway write-test (VZ 10.64.122.140).
# One auth handshake + GETs only. NO creates/deletes. It gathers exactly
# what's needed to build a SAFE throwaway create: CPG capacity, name
# collisions, and a fake host WWPN guaranteed not to clash with any real
# host. Prints a summary + writes ~/alletra_probe_out/tier1_recon.txt.
#   run:  python tier1_recon.py     (password via env, no prompt)
# =====================================================================
import json, ssl, os, sys, urllib.request, urllib.error
from pathlib import Path

ARRAY = os.environ.get("ARRAY_IP", "10.64.122.140")
USER  = os.environ.get("ARRAY_USER", "3paradm")
# This repository is PUBLIC — no credential defaults, not even the vendor default (LESSONS.md 21).
PW    = os.environ.get("ARRAY_PW") or sys.exit("Set $ARRAY_PW — credentials are never stored in this repository.")
BASE  = f"https://{ARRAY}:443/api/v1"
OUT   = Path.home() / "alletra_probe_out"; OUT.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
THROWAWAY = ["zz_test_host", "zz_test_hostset", "zz_test_vol", "zz_test_vvset"]  # names we intend to create


def call(method, path, headers=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json"); req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return None, repr(e)


def members(body):
    return body.get("members", []) if isinstance(body, dict) else []


out = []
def line(s=""):
    out.append(s); print(s)


st, bd = call("POST", "/credentials", body={"user": USER, "password": PW})
if st not in (200, 201):
    line(f"WSAPI NOT READY (status={st}) -> cannot run the write-test here. {bd}")
    (OUT / "tier1_recon.txt").write_text("\n".join(out), encoding="utf-8"); raise SystemExit
H = {"X-HP3PAR-WSAPI-SessionKey": bd["key"]}
line(f"WSAPI READY on {ARRAY} (auth OK) — write transport is up.\n")

# CPG SSD_r6 capacity
cpg = next((c for c in members(call("GET", "/cpgs", H)[1]) if c.get("name") == "SSD_r6"), None)
if cpg:
    line(f"CPG SSD_r6: freeSpaceMiB={cpg.get('freeSpaceMiB')}  rawFreeSpaceMiB={cpg.get('rawFreeSpaceMiB')}  "
         f"dedupCapable={cpg.get('dedupCapable')}  state={cpg.get('state')}")
else:
    line("CPG SSD_r6: NOT FOUND (!) — write-test would fail; check the CPG name.")

# hosts + every FC WWPN already in use
hosts = members(call("GET", "/hosts", H)[1])
in_use = sorted({str(p.get("wwn", "")).upper() for h in hosts for p in (h.get("FCPaths") or []) if p.get("wwn")})
line(f"\nHosts: {len(hosts)}  ({', '.join(h.get('name','?') for h in hosts)})")
line(f"FC WWPNs already in use ({len(in_use)}): {in_use}")

# a synthetic WWPN guaranteed NOT to clash with any real host (real ones start 10../20..)
fake = next((c for i in range(1, 99) for c in [f"AAAAAAAA{i:08X}"] if c not in in_use), None)
line(f"--> SAFE fake WWPN for the throwaway host (not in use): {fake}")

# host sets / volume sets / volumes / vluns — name collisions + LUN ids
hs = sorted(h.get("name", "") for h in members(call("GET", "/hostsets", H)[1]))
vs = sorted(v.get("name", "") for v in members(call("GET", "/volumesets", H)[1]))
vols = sorted(v.get("name", "") for v in members(call("GET", "/volumes", H)[1]))
luns = sorted({v.get("lun") for v in members(call("GET", "/vluns", H)[1]) if isinstance(v.get("lun"), int)})
line(f"\nHost sets: {hs}")
line(f"Volume sets: {vs}")
line(f"Volumes: {len(vols)} total")
line(f"VLUN LUN ids in use: {luns}  (max={max(luns) if luns else 'n/a'})")

# collision check for the names we plan to create
line("\nName-collision check (must all be FREE):")
existing = set(hosts and [h.get('name') for h in hosts]) | set(hs) | set(vs) | set(vols)
for n in THROWAWAY:
    line(f"  {n}: {'IN USE (!)' if n in existing else 'free'}")

(OUT / "tier1_recon.txt").write_text("\n".join(out), encoding="utf-8")
line(f"\nWROTE {OUT / 'tier1_recon.txt'}")
