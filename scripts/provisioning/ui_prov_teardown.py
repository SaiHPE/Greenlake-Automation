#!/usr/bin/env python3
# =====================================================================
# TEARDOWN for the UI-driven provisioning test (throwaway zz_ui_*).
#
# The app deliberately has NO delete path, so after driving the Stage-2
# builder live (sheet -> discovery -> builder -> preview -> authorise ->
# apply) this removes what the test created. Same fail-closed rules as
# tier1_writetest.py:
#   * Only objects whose name starts "zz_ui" are ever deleted; every
#     DELETE target is asserted against the prefix first.
#   * VLUNs are matched by their volumeName ("zz_ui..." or "set:zz_ui...")
#     and deleted by the key the ARRAY reports (never a parsed header).
#   * HOSTS are NEVER deleted: the apply step ensures a host object for
#     every vCenter-discovered host under its REAL name. On VZ those
#     already exist (outcome "exists"). If apply DID create a new real
#     host, this script only LISTS hosts with zero VLUNs so you can
#     decide; remove by hand (removehost) if you want it gone.
#   * Discovery-by-listing: whatever zz_ui_* names the run created are
#     found on the array, not assumed.
#
#   run:  ARRAY_PW="..." python -u ui_prov_teardown.py
#   env:  ARRAY_IP (default 10.64.122.140 = VZ), ARRAY_USER (3paradm)
# =====================================================================
import json, ssl, os, sys, urllib.request, urllib.error
from pathlib import Path

ARRAY = os.environ.get("ARRAY_IP", "10.64.122.140")
USER  = os.environ.get("ARRAY_USER", "3paradm")
PW    = os.environ.get("ARRAY_PW", "")
BASE  = f"https://{ARRAY}:443/api/v1"
OUT   = Path.home() / "alletra_probe_out"; OUT.mkdir(parents=True, exist_ok=True)
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

PREFIX = "zz_ui"            # hard guard: delete may ONLY touch this prefix

out = []
def line(s=""):
    out.append(str(s)); print(s)

def save():
    (OUT / "ui_prov_teardown.txt").write_text("\n".join(out), encoding="utf-8")

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

def is_ours(name):
    n = str(name)
    return n.startswith(PREFIX) or n.startswith(f"set:{PREFIX}")

def guard_del(name):
    if not is_ours(name):
        die(f"refusing to DELETE non-throwaway object: {name}")

def _vlun_key(x):
    key = f'{x.get("volumeName")},{x.get("lun")},{x.get("hostname", "")}'
    pp = x.get("portPos")
    if pp:
        key += f',{pp.get("node")}:{pp.get("slot")}:{pp.get("cardPort")}'
    return key

# --- auth --------------------------------------------------------------
if not PW:
    die("set ARRAY_PW")
st, bd, _ = call("POST", "/credentials", body={"user": USER, "password": PW})
if st not in (200, 201) or not isinstance(bd, dict) or "key" not in bd:
    die(f"WSAPI auth failed (status={st}): {bd}")
SESS = bd["key"]
line(f"WSAPI READY on {ARRAY} (auth OK).")

# --- teardown (reverse creation order; zz_ui_* only) -------------------
line("\n=== TEARDOWN (VLUNs -> volume-sets -> volumes -> host-sets) ===")
for x in members("/vluns"):
    vn = str(x.get("volumeName", ""))
    if not is_ours(vn):
        continue
    guard_del(vn)
    key = _vlun_key(x)
    s, _, _ = call("DELETE", f"/vluns/{key}", SESS)
    line(f"  del VLUN {key}: status={s}")

for path, listing, what in [("/volumesets", members("/volumesets"), "volume-set"),
                            ("/volumes",    members("/volumes"),    "volume"),
                            ("/hostsets",   members("/hostsets"),   "host-set")]:
    for x in listing:
        nm = str(x.get("name", ""))
        if not nm.startswith(PREFIX):
            continue
        guard_del(nm)
        s, _, _ = call("DELETE", f"{path}/{nm}", SESS)
        line(f"  del {what} {nm}: status={s}")

# --- post-check --------------------------------------------------------
line("\n=== POST-TEARDOWN ===")
left = ([n for x in members("/volumesets") if (n := str(x.get("name", ""))).startswith(PREFIX)]
        + [n for x in members("/volumes") if (n := str(x.get("name", ""))).startswith(PREFIX)]
        + [n for x in members("/hostsets") if (n := str(x.get("name", ""))).startswith(PREFIX)])
vl = [x for x in members("/vluns") if is_ours(x.get("volumeName", ""))]
if left or vl:
    line(f"  !!! leftovers: objects={left} vluns={len(vl)} -- rerun or clean by hand")
else:
    line(f"  all {PREFIX}* gone.")

# hosts are never deleted here -- surface the inert ones for a human call
hosts = members("/hosts")
with_vluns = {str(x.get("hostname", "")) for x in members("/vluns")}
idle = [h.get("name") for h in hosts if h.get("name") not in with_vluns]
line(f"  hosts on array: {len(hosts)}; with no VLUNs (candidates IF the test created them): {idle}")
line("  (remove a test-created host by hand with `removehost <name>` if you want it gone)")

save()
line(f"\nWROTE {OUT / 'ui_prov_teardown.txt'}")
