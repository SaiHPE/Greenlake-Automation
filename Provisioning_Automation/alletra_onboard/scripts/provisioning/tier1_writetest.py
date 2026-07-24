#!/usr/bin/env python3
# =====================================================================
# TIER-1 LIVE WRITE-VALIDATION on VZ 10.64.122.140 (throwaway zz_test_*).
# Mirrors EXACTLY what our wsapi_client emits for the plural/heterogeneous
# create path, so we prove the REAL array accepts our create sequence --
# especially persona=8 (the VMware persona fix). Pure stdlib urllib.
#
# SAFETY (fail-closed):
#   * Only ever creates/deletes objects whose name starts "zz_test".
#   * Every DELETE target is asserted to start with "zz_test" (or be a
#     VLUN whose volume does) -- a real object CANNOT be deleted.
#   * Re-verifies at runtime (never trusts a stale recon): fake WWPN not
#     in use, zz_test_* names free, CPG SSD_r6 present with room.
#   * 1 GiB THIN volume in SSD_r6 (recon: 255150 MiB free) -- negligible.
#   * Fake host WWPN AAAAAAAA00000001 (recon-confirmed unused, not logged
#     into any fabric -> isolated, no path to any real host).
#   * Default run = CREATE -> VERIFY -> TEARDOWN (leaves array pristine).
#       KEEP=1        -> create+verify, skip teardown (inspect in the UI)
#       MODE=teardown -> only tear down a prior KEEP run
#
#   run:  ARRAY_PW="..." python -u tier1_writetest.py
# =====================================================================
import json, ssl, os, sys, urllib.request, urllib.error
from pathlib import Path

ARRAY = os.environ.get("ARRAY_IP", "10.64.122.140")
USER  = os.environ.get("ARRAY_USER", "3paradm")
PW    = os.environ.get("ARRAY_PW", "3pardata")
KEEP  = os.environ.get("KEEP") == "1"
MODE  = os.environ.get("MODE", "auto").lower()          # auto | teardown
BASE  = f"https://{ARRAY}:443/api/v1"
OUT   = Path.home() / "alletra_probe_out"; OUT.mkdir(parents=True, exist_ok=True)
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

# --- the throwaway objects (the ONLY things this script may create/delete) ---
FAKE_WWPN = "AAAAAAAA00000001"
H_HOST, H_HSET, V_VOL, V_VVSET = "zz_test_host", "zz_test_hostset", "zz_test_vol", "zz_test_vvset"
CPG, SIZE_MIB, LUN = "SSD_r6", 1024, 100
PERSONA_VMWARE = 8          # WSAPI VMware persona = exactly what our fixed client emits
PREFIX = "zz_test"          # hard guard: create/delete may ONLY touch this prefix

out = []
def line(s=""):
    out.append(str(s)); print(s)

def save():
    (OUT / "tier1_writetest.txt").write_text("\n".join(out), encoding="utf-8")

def die(msg):
    line(f"\n*** ABORT: {msg}"); save(); sys.exit(1)

def call(method, path, sess=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json"); req.add_header("Accept", "application/json")
    if sess:
        req.add_header("X-HP3PAR-WSAPI-SessionKey", sess)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=40) as r:
            raw = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(raw) if raw else {}), dict(r.headers)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try: bd = json.loads(raw)
        except Exception: bd = raw
        return e.code, bd, dict(e.headers)
    except Exception as e:  # noqa: BLE001
        return None, repr(e), {}

def members(path):
    _, b, _ = call("GET", path, SESS)
    return b.get("members", []) if isinstance(b, dict) else []

def _exists(status, body):
    return status == 409 or (isinstance(body, dict) and "exist" in str(body.get("desc", "")).lower())

# --- auth --------------------------------------------------------------
st, bd, _ = call("POST", "/credentials", body={"user": USER, "password": PW})
if st not in (200, 201) or not isinstance(bd, dict) or "key" not in bd:
    die(f"WSAPI auth failed (status={st}): {bd}")
SESS = bd["key"]
line(f"WSAPI READY on {ARRAY} (auth OK).")

# --- pre-flight guards (re-verify live, never trust the recon) ---------
def preflight():
    cpg = next((c for c in members("/cpgs") if c.get("name") == CPG), None)
    if not cpg:
        die(f"CPG {CPG} not found")
    free = cpg.get("freeSpaceMiB", 0)
    if free < SIZE_MIB * 5:
        die(f"CPG {CPG} low on space: {free} MiB free")
    line(f"CPG {CPG}: {free} MiB free -- OK for a {SIZE_MIB} MiB thin volume.")
    hosts = members("/hosts")
    in_use = {str(p.get("wwn", "")).upper() for h in hosts for p in (h.get("FCPaths") or []) if p.get("wwn")}
    if FAKE_WWPN.upper() in in_use:
        die(f"fake WWPN {FAKE_WWPN} IS in use -- refuse to proceed")
    line(f"Fake WWPN {FAKE_WWPN}: confirmed NOT in use.")
    names = ({h.get("name") for h in hosts} | {x.get("name") for x in members("/hostsets")}
             | {x.get("name") for x in members("/volumesets")} | {x.get("name") for x in members("/volumes")})
    clash = [n for n in (H_HOST, H_HSET, V_VOL, V_VVSET) if n in names]
    if clash:
        die(f"name(s) already exist: {clash} -- run MODE=teardown first")
    line("Names zz_test_* : all free.")
    return len(hosts), len(members("/volumes"))

def create(path, body, what):
    nm = body.get("name", "")
    if not nm.startswith(PREFIX):
        die(f"refusing to create non-throwaway object: {nm}")
    s, b, _ = call("POST", path, SESS, body)
    if s in (200, 201):
        line(f"  created {what}: {nm}")
    elif _exists(s, b):
        line(f"  {what} already exists: {nm} (ok)")
    else:
        die(f"create {what} failed (status={s}): {b}")

def do_create():
    line("\n=== CREATE (mirrors our wsapi_client plural path) ===")
    create("/hosts", {"name": H_HOST, "FCWWNs": [FAKE_WWPN], "persona": PERSONA_VMWARE}, "host (persona=8 VMware)")
    create("/hostsets", {"name": H_HSET, "setmembers": [H_HOST]}, "host-set + member")
    create("/volumes", {"name": V_VOL, "cpg": CPG, "sizeMiB": SIZE_MIB, "tpvv": True}, "volume (1GiB thin)")
    create("/volumesets", {"name": V_VVSET, "setmembers": [V_VOL]}, "volume-set + member")
    # present the VOLUME to the HOST-SET -- the exact "set:" path apply_plan uses.
    # NB: for a host-set whose member isn't fabric-logged the array returns a
    # warning in the Location header, so we do NOT parse the key from it --
    # teardown reads the authoritative key back from GET /vluns instead.
    s, b, _ = call("POST", "/vluns", SESS, {"volumeName": V_VOL, "lun": LUN, "hostname": f"set:{H_HSET}"})
    if s in (200, 201):
        line(f"  created VLUN: {V_VOL} -> set:{H_HSET} lun {LUN}")
    elif _exists(s, b):
        line("  VLUN already exists (ok)")
    else:
        die(f"create VLUN failed (status={s}): {b}")

def do_verify():
    line("\n=== VERIFY (read-back proof) ===")
    _, h, _ = call("GET", f"/hosts/{H_HOST}", SESS)
    persona = h.get("persona") if isinstance(h, dict) else None
    wwns = [p.get("wwn") for p in (h.get("FCPaths") or [])] if isinstance(h, dict) else []
    line(f"  host {H_HOST}: persona={persona}  FCWWNs={wwns}")
    if persona == PERSONA_VMWARE:
        line("  >>> PERSONA FIX PROVEN LIVE: array stored persona=8 (VMware). <<<")
    else:
        line(f"  !!! persona mismatch: expected 8, got {persona}")
    _, v, _ = call("GET", f"/volumes/{V_VOL}", SESS)
    line(f"  volume {V_VOL}: provisioningType={v.get('provisioningType')} (expect 2=TPVV/thin) "
         f"sizeMiB={v.get('sizeMiB')} userCPG={v.get('userCPG')}")
    hs = next((x for x in members("/hostsets") if x.get("name") == H_HSET), {})
    line(f"  host-set {H_HSET}: setmembers={hs.get('setmembers')}")
    vs = next((x for x in members("/volumesets") if x.get("name") == V_VVSET), {})
    line(f"  volume-set {V_VVSET}: setmembers={vs.get('setmembers')}")
    ours = [{k: x.get(k) for k in ("volumeName", "lun", "hostname", "type")}
            for x in members("/vluns") if str(x.get("volumeName", "")).startswith(PREFIX)]
    line(f"  VLUNs for {V_VOL}: {json.dumps(ours)}")

def guard_del(name):
    if not str(name).startswith(PREFIX):
        die(f"refusing to DELETE non-throwaway object: {name}")

def _vlun_key(x):
    # build the authoritative delete key from the array's OWN reported fields
    key = f'{x.get("volumeName")},{x.get("lun")},{x.get("hostname", "")}'
    pp = x.get("portPos")
    if pp:
        key += f',{pp.get("node")}:{pp.get("slot")}:{pp.get("cardPort")}'
    return key

def do_teardown():
    line("\n=== TEARDOWN (reverse order; zz_test_* only) ===")
    # 1) VLUN(s) -- read the real key back from the array (never from a header)
    for x in members("/vluns"):
        vn = str(x.get("volumeName", ""))
        if not vn.startswith(PREFIX):
            continue
        guard_del(vn)
        key = _vlun_key(x)
        s, _, _ = call("DELETE", f"/vluns/{key}", SESS)
        line(f"  del VLUN {key}: status={s}")
    # 2) volume-set  3) volume  4) host-set  5) host
    for path, nm, what in [(f"/volumesets/{V_VVSET}", V_VVSET, "volume-set"),
                           (f"/volumes/{V_VOL}", V_VOL, "volume"),
                           (f"/hostsets/{H_HSET}", H_HSET, "host-set"),
                           (f"/hosts/{H_HOST}", H_HOST, "host")]:
        guard_del(nm)
        s, _, _ = call("DELETE", path, SESS)
        line(f"  del {what} {nm}: status={s}")

def verify_gone(orig_hosts, orig_vols):
    line("\n=== POST-TEARDOWN (confirm nothing left behind) ===")
    left = [nm for path, nm in [(f"/hosts/{H_HOST}", H_HOST), (f"/hostsets/{H_HSET}", H_HSET),
                                (f"/volumes/{V_VOL}", V_VOL), (f"/volumesets/{V_VVSET}", V_VVSET)]
            if call("GET", path, SESS)[0] == 200]
    vl = [x for x in members("/vluns") if str(x.get("volumeName", "")).startswith(PREFIX)]
    nh, nv = len(members("/hosts")), len(members("/volumes"))
    if left or vl:
        line(f"  !!! leftovers: objects={left} vluns={len(vl)} -- MANUAL CLEANUP NEEDED")
    else:
        line(f"  all zz_test_* gone. hosts {nh} (was {orig_hosts}), volumes {nv} (was {orig_vols}).")
        if nh == orig_hosts and nv == orig_vols:
            line("  >>> ARRAY RESTORED TO ORIGINAL STATE. <<<")

# --- run ---------------------------------------------------------------
if MODE == "teardown":
    do_teardown(); verify_gone(3, 85)
else:
    oh, ov = preflight()
    do_create()
    do_verify()
    if KEEP:
        line("\nKEEP=1 -> leaving zz_test_* objects for inspection. Re-run with MODE=teardown to clean up.")
    else:
        do_teardown()
        verify_gone(oh, ov)

save()
line(f"\nWROTE {OUT / 'tier1_writetest.txt'}")
