#!/usr/bin/env python3
# =====================================================================
# RECON for the BGL provisioning test target (sheet: bgl_labs).
# Read-only by default. Pure stdlib -- copy to the jump box and run.
#
# Answers, for the array named in the sheet's Provisioning tab:
#   1. Is WSAPI ENABLED?  (unauthenticated GET /api reports the version;
#      connection-refused => not started -- fix on the array CLI:
#      ssh 3paradm@<array>  ->  showwsapi  ->  startwsapi)
#   2. Do the creds work (POST /credentials)?
#   3. System identity (GET /system): name / model / serial / OS.
#   4. CPGs + free space -- and is the sheet's CPG (SSD_r6) present?
#   5. Existing hosts / host sets / volumes / volume sets, and whether
#      the sheet's names (CRV_LZ_Prod, CRV_LZ_Prod_set, ESX_Cluster_LZ)
#      clash with anything already on the array.
#   6. FC ports: target-mode ports and their link state.
#   7. SSH (port 22) reachable + banner -- discovery needs it.
#   8. vCenter reachable + creds + the ESXi host list (the apply step
#      REFUSES to run if discovery finds zero hosts, so this is the gate).
#   9. WRITE=1 only: proves empirically whether THIS array accepts the
#      exact create bodies the app will send -- including the open
#      question: a 1 GiB "reduce" volume ({"tdvv":true,"compression":
#      true}), which the lineage may reject below 16 GiB. Throwaway
#      zz_recon_* names, deleted immediately, prefix-guarded.
#
#   run:  ARRAY_PW="..." VC_PW="..." python -u recon_bgl.py
#   env:  ARRAY_IP (10.64.186.90)  ARRAY_USER (3paradm)
#         VC_IP (10.55.234.169)    VC_USER (Administrator@vsphere.local)
#         WRITE=1  -> include the create/delete probe (off by default)
# =====================================================================
import json, os, socket, ssl, sys, urllib.request, urllib.error
from base64 import b64encode
from pathlib import Path

ARRAY   = os.environ.get("ARRAY_IP", "10.64.186.90")
A_USER  = os.environ.get("ARRAY_USER", "3paradm")
A_PW    = os.environ.get("ARRAY_PW", "")
VC      = os.environ.get("VC_IP", "10.55.234.169")
VC_USER = os.environ.get("VC_USER", "Administrator@vsphere.local")
VC_PW   = os.environ.get("VC_PW", "")
WRITE   = os.environ.get("WRITE") == "1"

SHEET_CPG   = "SSD_r6"
SHEET_NAMES = ("CRV_LZ_Prod", "CRV_LZ_Prod_set", "ESX_Cluster_LZ")
PREFIX      = "zz_recon"          # WRITE probe may only create/delete this

OUT = Path.home() / "alletra_probe_out"; OUT.mkdir(parents=True, exist_ok=True)
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

out = []
def line(s=""):
    out.append(str(s)); print(s)

def save():
    (OUT / "recon_bgl.txt").write_text("\n".join(out), encoding="utf-8")

def http(method, url, body=None, headers=None, timeout=15):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json"); req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try: bd = json.loads(raw)
        except Exception: bd = raw
        return e.code, bd
    except Exception as e:  # noqa: BLE001
        return None, repr(e)

def tcp(host, port, timeout=5, read_banner=False):
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            if read_banner:
                s.settimeout(timeout)
                try:
                    return True, s.recv(80).decode("ascii", "replace").strip()
                except Exception:  # noqa: BLE001
                    return True, ""
            return True, ""
    except Exception as e:  # noqa: BLE001
        return False, repr(e)

# ---------------------------------------------------------------- 1. network
line(f"=== ARRAY {ARRAY} -- network ===")
ok443, _ = tcp(ARRAY, 443)
ok22, banner = tcp(ARRAY, 22, read_banner=True)
ok8080, _ = tcp(ARRAY, 8080)
line(f"  tcp 443 (WSAPI): {'OPEN' if ok443 else 'CLOSED/UNREACHABLE'}")
line(f"  tcp 22  (SSH for discovery): {'OPEN  ' + banner if ok22 else 'CLOSED/UNREACHABLE'}")
line(f"  tcp 8080: {'open (unexpected extra listener)' if ok8080 else 'closed (fine; WSAPI lives on 443 here)'}")

# ---------------------------------------------------------------- 2. wsapi enabled?
line(f"\n=== ARRAY {ARRAY} -- is WSAPI enabled? ===")
BASE = f"https://{ARRAY}:443/api/v1"
st, bd = http("GET", f"https://{ARRAY}:443/api")
if st == 200 and isinstance(bd, dict):
    line(f"  WSAPI ENABLED. version={bd.get('major')}.{bd.get('minor')}.{bd.get('revision')} build={bd.get('build')}")
else:
    line(f"  WSAPI NOT RESPONDING on 443 (GET /api -> {st}: {bd})")
    line("  -> ssh 3paradm@" + ARRAY + " ; run: showwsapi   (if disabled: startwsapi ; https: setwsapi -https enable)")
    save(); sys.exit(0 if not ok443 else 1)

# ---------------------------------------------------------------- 3. auth + identity
SESS = None
if not A_PW:
    line("  ARRAY_PW not set -> skipping authenticated checks.")
else:
    st, bd = http("POST", f"{BASE}/credentials", body={"user": A_USER, "password": A_PW})
    if st in (200, 201) and isinstance(bd, dict) and "key" in bd:
        SESS = bd["key"]
        line(f"  auth OK as {A_USER}.")
    else:
        line(f"  AUTH FAILED (status={st}): {bd}")

def get(path):
    st_, bd_ = http("GET", BASE + path, headers={"X-HP3PAR-WSAPI-SessionKey": SESS})
    return bd_ if st_ == 200 else {}

def mem(path):
    b = get(path)
    return b.get("members", []) if isinstance(b, dict) else []

if SESS:
    sysinfo = get("/system")
    line(f"\n=== SYSTEM ===")
    line(f"  name={sysinfo.get('name')}  model={sysinfo.get('model')}  serial={sysinfo.get('serialNumber')}")
    line(f"  os={sysinfo.get('systemVersion')}  totalCapacityMiB={sysinfo.get('totalCapacityMiB')}")

    # ------------------------------------------------------------ 4. CPGs
    line("\n=== CPGs (sheet expects '" + SHEET_CPG + "') ===")
    cpgs = mem("/cpgs")
    if not cpgs:
        line("  NO CPGs returned!")
    for c in cpgs:
        nm = c.get("name")
        free = (c.get("UsrUsage") or {}).get("totalMiB")  # fallback fields vary by version
        line(f"  {nm}   freeSpaceMiB={c.get('freeSpaceMiB')}  (usr totalMiB={free})")
    names = {c.get("name") for c in cpgs}
    line(f"  sheet CPG '{SHEET_CPG}': {'PRESENT' if SHEET_CPG in names else 'MISSING -- fix the sheet CPG to one of the above'}")

    # ------------------------------------------------------------ 5. existing objects + clashes
    hosts, hsets = mem("/hosts"), mem("/hostsets")
    vols, vsets = mem("/volumes"), mem("/volumesets")
    line("\n=== EXISTING OBJECTS ===")
    line(f"  hosts={len(hosts)}  host-sets={len(hsets)}  volumes={len(vols)}  volume-sets={len(vsets)}")
    for h in hosts:
        wwns = [p.get("wwn") for p in (h.get("FCPaths") or [])]
        line(f"    host {h.get('name')}  persona={h.get('persona')}  wwns={wwns}")
    everything = ({h.get("name") for h in hosts} | {x.get("name") for x in hsets}
                  | {x.get("name") for x in vols} | {x.get("name") for x in vsets})
    clash = [n for n in SHEET_NAMES if n in everything]
    line(f"  sheet-name clashes: {clash if clash else 'none -- all three names are free'}")

    # ------------------------------------------------------------ 6. FC ports
    line("\n=== FC PORTS (target mode) ===")
    for p in mem("/ports"):
        if p.get("protocol") != 1:      # 1 = FC
            continue
        pos = p.get("portPos") or {}
        nsp = f"{pos.get('node')}:{pos.get('slot')}:{pos.get('cardPort')}"
        line(f"  {nsp}  mode={p.get('mode')} (2=target)  linkState={p.get('linkState')} (4=ready)  wwn={p.get('portWWN')}")

    # ------------------------------------------------------------ 9. WRITE probe (opt-in)
    if WRITE:
        line("\n=== WRITE PROBE (zz_recon_*, created then deleted) ===")
        test_cpg = SHEET_CPG if SHEET_CPG in names else (sorted(names)[0] if names else None)
        if not test_cpg:
            line("  no CPG available -- skipping")
        else:
            def guard(nm):
                if not nm.startswith(PREFIX):
                    line(f"  *** refusing to touch non-throwaway name {nm}"); save(); sys.exit(1)

            def try_create(nm, size_mib, body_extra, what):
                guard(nm)
                body = {"name": nm, "cpg": test_cpg, "sizeMiB": size_mib}
                body.update(body_extra)
                s2, b2 = http("POST", f"{BASE}/volumes", body=body,
                              headers={"X-HP3PAR-WSAPI-SessionKey": SESS})
                if s2 in (200, 201):
                    line(f"  {what} {size_mib} MiB: ACCEPTED")
                    guard(nm)
                    http("DELETE", f"{BASE}/volumes/{nm}", headers={"X-HP3PAR-WSAPI-SessionKey": SESS})
                    line(f"    (deleted {nm})")
                    return True
                line(f"  {what} {size_mib} MiB: REJECTED (status={s2}) {b2}")
                return False

            # exactly what the app sends for the sheet's row: 1 GiB reduce
            ok = try_create("zz_recon_reduce", 1024, {"tdvv": True, "compression": True},
                            "reduce (tdvv+compression) -- the sheet's row as-is:")
            if not ok:
                try_create("zz_recon_reduce", 16384, {"tdvv": True, "compression": True},
                           "reduce at 16 GiB (min-size check):")
            try_create("zz_recon_thin", 1024, {"tpvv": True}, "thin (tpvv):")
    else:
        line("\n(WRITE probe skipped -- rerun with WRITE=1 to empirically test the 1 GiB reduce create)")

# ---------------------------------------------------------------- 8. vCenter
line(f"\n=== VCENTER {VC} ===")
okv, err = tcp(VC, 443)
line(f"  tcp 443: {'OPEN' if okv else 'CLOSED/UNREACHABLE ' + err}")
if okv and VC_PW:
    basic = "Basic " + b64encode(f"{VC_USER}:{VC_PW}".encode()).decode()
    token = None
    st, bd = http("POST", f"https://{VC}/api/session", body=None, headers={"Authorization": basic})
    if st in (200, 201) and isinstance(bd, str):
        token = bd
    else:
        st, bd = http("POST", f"https://{VC}/rest/com/vmware/cis/session", body=None, headers={"Authorization": basic})
        if st in (200, 201) and isinstance(bd, dict):
            token = bd.get("value")
    if not token:
        line(f"  vCenter AUTH FAILED (status={st}): {bd}")
    else:
        line(f"  auth OK as {VC_USER}.")
        st, hostsv = http("GET", f"https://{VC}/api/vcenter/host", headers={"vmware-api-session-id": token})
        if st != 200:
            st, wrapped = http("GET", f"https://{VC}/rest/vcenter/host", headers={"vmware-api-session-id": token})
            hostsv = wrapped.get("value", []) if st == 200 and isinstance(wrapped, dict) else []
        if isinstance(hostsv, list) and hostsv:
            line(f"  ESXi hosts vCenter reports ({len(hostsv)}) -- discovery's raw material:")
            for h in hostsv:
                line(f"    {h.get('name')}  connection={h.get('connection_state')}  power={h.get('power_state')}")
        else:
            line(f"  NO ESXi hosts returned ({st}) -- the apply step will REFUSE with zero discovered hosts")
elif okv:
    line("  VC_PW not set -> skipping vCenter auth + host list.")

save()
line(f"\nWROTE {OUT / 'recon_bgl.txt'}")
