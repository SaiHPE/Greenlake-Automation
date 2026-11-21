#!/usr/bin/env python3
# =====================================================================
# READ-ONLY WSAPI probe  --  Alletra MP B10000 (ADR 0010 readiness)
# ---------------------------------------------------------------------
# Confirms the WSAPI write transport is reachable + READY (the 503/code-68
# "services not ready" gate) and reads capacity/objects. ONE auth handshake
# (POST /credentials -> a session token that self-expires; not a config
# change) + GET calls only. No dependencies -- Python 3 standard library.
# Dumps to ~/alletra_probe_out/asbuilt_wsapi.txt.
#
# Run:  python asbuilt_wsapi.py     (prompts for the 3paradm password)
# =====================================================================
import json, ssl, os, getpass, urllib.request, urllib.error, datetime
from pathlib import Path

ARRAY = os.environ.get("ARRAY_IP", "10.64.122.140")   # VZ array
USER  = os.environ.get("ARRAY_USER", "3paradm")
OUT   = Path.home() / "alletra_probe_out"
OUT.mkdir(parents=True, exist_ok=True)
DUMP  = OUT / "asbuilt_wsapi.txt"
BASE  = f"https://{ARRAY}:443/api/v1"

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE          # self-signed array cert


def call(method, path, headers=None, body=None):
    # Structural read-only guard: only GET, plus the single login handshake (POST /credentials, which
    # just mints a self-expiring session token — not a config write). Any other verb is refused.
    if not (method == "GET" or (method == "POST" and path == "/credentials")):
        raise RuntimeError(f"REFUSED — not a read-only WSAPI call: {method} {path}")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return None, f"ERROR: {e!r}"


def main():
    pw = os.environ.get("ARRAY_PW") or getpass.getpass(f"Password for {USER}@{ARRAY}: ")
    lines = [f"# WSAPI READ-ONLY DUMP  {datetime.datetime.now().isoformat()}",
             f"# array={ARRAY}  user={USER}  base={BASE}"]

    def log(t):
        lines.append(t); print(t[:160])

    st, bd = call("POST", "/credentials", body={"user": USER, "password": pw})
    if st not in (200, 201):
        log(f"\nAUTH/READINESS status={st}\n{bd}")
        log("# (HTTP 503 + errorCode 68 == 'system services not ready' -- not ready for writes yet)")
        DUMP.write_text("\n".join(lines), encoding="utf-8"); print(f"\nWROTE {DUMP}"); return
    key = json.loads(bd).get("key")
    log("AUTH OK -- WSAPI reachable + ready (session token obtained)\n")
    H = {"X-HP3PAR-WSAPI-SessionKey": key}

    for label, path in [
        ("SYSTEM", "/system"), ("WSAPI-CONFIG", "/wsapiconfiguration"), ("CAPACITY", "/capacity"),
        ("CPGS", "/cpgs"), ("PORTS", "/ports"), ("HOSTS", "/hosts"), ("HOSTSETS", "/hostsets"),
        ("VOLUMES", "/volumes"), ("VOLUMESETS", "/volumesets"), ("VLUNS", "/vluns"),
    ]:
        st, bd = call("GET", path, headers=H)
        log(f"\n===== {label}  GET {path}  ->  HTTP {st} =====")
        try:
            log(json.dumps(json.loads(bd), indent=2))
        except Exception:  # noqa: BLE001
            log(bd)

    DUMP.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWROTE  {DUMP}")


if __name__ == "__main__":
    main()
