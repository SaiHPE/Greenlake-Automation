r"""Read-only WSAPI capability probe for an HPE Alletra MP B10000.

Answers "what can WSAPI do vs what needs SSH": authenticates (POST /credentials), GETs each read-only
collection to see which exist + how many objects, then logs out. Reads config only (creates + deletes
one session). Standard library only - no extra deps, so it runs in any python.

    python probe_wsapi.py 10.64.154.225 [--user 3paradm] [--port 443]

Password via the ALLETRA_PASSWORD env var or the prompt. The WSAPI cert is self-signed, so TLS
verification is disabled (mgmt network only).
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import ssl
import sys
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


def call(method: str, url: str, *, key: str | None = None, body: dict | None = None, ctx) -> tuple[int, bytes]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if key:
        req.add_header("X-HP3PAR-WSAPI-SessionKey", key)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
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
    args = ap.parse_args()
    password = os.environ.get("ALLETRA_PASSWORD") or getpass.getpass(f"Password for {args.user}@{args.host}: ")

    base = f"https://{args.host}:{args.port}/api/v1"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    status, raw = call("POST", base + "/credentials", body={"user": args.user, "password": password}, ctx=ctx)
    if status not in (200, 201) or b"key" not in raw:
        print(f"AUTH FAILED  status={status}  {raw[:200]!r}", file=sys.stderr)
        print("Is WSAPI enabled (showwsapi) and reachable on this port?", file=sys.stderr)
        return 1
    key = json.loads(raw)["key"]
    print(f"WSAPI {base}  -  auth OK\n")
    print(f"{'collection':<20}{'status':<8}count / notes")
    print("-" * 60)
    for ep in GETS:
        st, body = call("GET", f"{base}/{ep}", key=key, ctx=ctx)
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
        flag = "" if st == 200 else "   <-- not available via WSAPI" if st in (404, 501) else ""
        print(f"{ep:<20}{st:<8}{note}{flag}")
    call("DELETE", f"{base}/credentials/{key}", key=key, ctx=ctx)
    print("\nsession closed. (Note: the fabric nameserver / zoning view - `showportdev ns` - has no")
    print("WSAPI collection, so zoning *verification* stays on SSH regardless of the above.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
