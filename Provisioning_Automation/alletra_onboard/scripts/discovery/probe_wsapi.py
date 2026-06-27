r"""Read-only WSAPI capability probe for an HPE Alletra MP B10000.

Answers "what can WSAPI do vs what needs SSH": authenticates (POST /credentials), GETs each read-only
collection to see which exist + how many objects, then logs out. Reads config only (creates + deletes
one session). Standard library only - no extra deps, so it runs in any python.

    python probe_wsapi.py 10.64.154.225 [--user 3paradm] [--port 443]

The array is on the internal management network, so the request is made DIRECTLY (any HTTP(S)_PROXY
env var is bypassed - routing the array's 443 through a corporate proxy is what causes a TLS
"handshake timed out"). The WSAPI cert is self-signed, so TLS verification is disabled.
Password via the ALLETRA_PASSWORD env var or the prompt.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request

# Read-only collections to enumerate (WSAPI v1). If one 404s, that capability isn't in WSAPI.
GETS = [
    "system",            # identity + capacity
    "cpgs",              # provisioning pools
    "volumes",           # VVs (snapshots appear here too, as copyOf)
    "volumesets",        # VV sets
    "hosts",             # host definitions
    "hostsets",          # host sets
    "vluns",             # exports
    "ports",             # array ports (WWNs, state)
    "remotecopygroups",  # replication groups
    "remotecopytargets", # replication targets
    "tasks",             # async tasks
]


def make_opener(ctx: ssl.SSLContext) -> urllib.request.OpenerDirector:
    # ProxyHandler({}) disables every proxy: the array must be reached directly (an HTTP(S)_PROXY
    # env var would otherwise tunnel the request through the corporate proxy, which can't route to
    # the internal mgmt IP -> the TLS handshake times out).
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=ctx),
    )


def call(opener, method: str, url: str, *, key=None, body=None, timeout: float = 30.0) -> tuple[int, bytes]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if key:
        req.add_header("X-HP3PAR-WSAPI-SessionKey", key)
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except Exception as exc:  # noqa: BLE001 - socket/TLS issues
        return 0, str(exc).encode()


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only WSAPI capability probe.")
    ap.add_argument("host", help="array management IP, e.g. 10.64.154.225")
    ap.add_argument("--user", default="3paradm")
    ap.add_argument("--port", default="443")
    ap.add_argument("--timeout", type=float, default=45.0, help="per-request read timeout (s)")
    ap.add_argument("--retries", type=int, default=3, help="auth attempts (WSAPI may be initialising)")
    args = ap.parse_args()

    # 1) Direct TCP reachability (no proxy) - distinguishes "port blocked" from "proxy mis-route".
    try:
        with socket.create_connection((args.host, int(args.port)), timeout=8):
            print(f"TCP {args.host}:{args.port} reachable (direct).")
    except Exception as exc:  # noqa: BLE001
        print(f"TCP {args.host}:{args.port} NOT reachable directly: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("SSH (22) works but 443 doesn't -> the firewall is blocking WSAPI's port (SSH-only path).", file=sys.stderr)
        return 2

    password = os.environ.get("ALLETRA_PASSWORD") or getpass.getpass(f"Password for {args.user}@{args.host}: ")
    base = f"https://{args.host}:{args.port}/api/v1"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    opener = make_opener(ctx)

    status, raw = 0, b""
    for attempt in range(1, args.retries + 1):
        status, raw = call(opener, "POST", base + "/credentials",
                           body={"user": args.user, "password": password}, timeout=args.timeout)
        if status in (200, 201) and b"key" in raw:
            break
        print(f"  auth attempt {attempt}/{args.retries}: status={status} "
              f"{raw[:140].decode('utf-8', 'replace')}", file=sys.stderr)
        if attempt < args.retries:
            time.sleep(20)
    if status not in (200, 201) or b"key" not in raw:
        print(f"\nAUTH FAILED  status={status}  {raw[:200]!r}", file=sys.stderr)
        print("WSAPI is reachable (TCP/TLS OK) but not SERVING — a 503 'services not ready' or a hang.", file=sys.stderr)
        print("That's an ARRAY-side state, not the probe: check `checkhealth -svc -detail` (critical", file=sys.stderr)
        print("over-temp / degraded cage?) and `showwsapi -d` (System Resource Usage). Reads work over SSH.", file=sys.stderr)
        return 1
    key = json.loads(raw)["key"]
    print(f"WSAPI {base}  -  auth OK\n")
    print(f"{'collection':<20}{'status':<8}count / notes")
    print("-" * 60)
    for ep in GETS:
        st, body = call(opener, "GET", f"{base}/{ep}", key=key, timeout=args.timeout)
        note = ""
        try:
            j = json.loads(body)
            if isinstance(j, dict) and "total" in j:
                note = f"total={j['total']}"
            elif isinstance(j, dict) and "members" in j:
                note = f"members={len(j['members'])}"
            elif isinstance(j, dict):
                note = "keys=" + ",".join(list(j)[:6])
        except Exception:  # noqa: BLE001
            note = body[:60].decode("utf-8", "replace")
        flag = "   <-- not available via WSAPI" if st in (404, 501) else ""
        print(f"{ep:<20}{st:<8}{note}{flag}")
    call(opener, "DELETE", f"{base}/credentials/{key}", key=key, timeout=args.timeout)
    print("\nsession closed. (Note: the fabric nameserver / zoning view - `showportdev ns` - has no")
    print("WSAPI collection, so zoning *verification* stays on SSH regardless of the above.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
