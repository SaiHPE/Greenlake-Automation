"""Diagnose an outbound TLS trust failure (the "credentials rejected" that isn't).

Read-only. Sends no credentials. Shows, for the HPE endpoints the tool uses:
  - what certificate chain is actually presented (a corporate TLS-inspection root gives itself away
    in the issuer),
  - whether certifi alone trusts it (what httpx did BEFORE the fix),
  - whether the OS trust store trusts it (what the fix uses, and what your browser uses).

Run:  python scripts\\tls_diagnose.py
"""

from __future__ import annotations

import os
import socket
import ssl
import sys

try:
    import certifi as _certifi
    _certifi_err: Exception | None = None
except ImportError as _exc:
    _certifi = None
    _certifi_err = _exc

try:
    from alletra_onboard.adapters.tls import ssl_context as _ssl_context
    _tool_err: Exception | None = None
except ImportError as _exc:
    _ssl_context = None
    _tool_err = _exc

HOSTS = [
    ("global.api.greenlake.hpe.com", 443),
    ("common.cloud.hpe.com", 443),
    ("console-jp1.data.cloud.hpe.com", 443),
]


def _name(pairs) -> str:
    """RFC4514-ish flatten of a cert name tuple, e.g. 'CN=Corp Proxy CA, O=ACME'."""
    out = []
    for rdn in pairs or ():
        for key, value in rdn:
            out.append(f"{key}={value}")
    return ", ".join(out)


def _try(ctx: ssl.SSLContext, host: str, port: int):
    """Returns (ok, detail, peer_cert_dict_or_None)."""
    try:
        with socket.create_connection((host, port), timeout=12) as raw, ctx.wrap_socket(
            raw, server_hostname=host
        ) as tls:
            return True, f"{tls.version()}", tls.getpeercert()
    except ssl.SSLCertVerificationError as exc:
        return False, f"verify failed: {exc.verify_message or exc}", None
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}", None


def _load_certifi_ctx() -> ssl.SSLContext | None:
    if _certifi is None:
        print(f"\ncertifi unavailable: {_certifi_err}")
        return None
    try:
        ctx = ssl.create_default_context(cafile=_certifi.where())
        print(f"\ncertifi bundle: {_certifi.where()}")
    except Exception as exc:  # noqa: BLE001
        print(f"\ncertifi unavailable: {exc}")
        return None
    return ctx


def _load_tool_ctx() -> ssl.SSLContext | None:
    if _ssl_context is None:
        print(f"tool context unavailable (run with PYTHONPATH=src): {_tool_err}")
        return None
    try:
        ctx = _ssl_context()
        print(f"tool context  : {len(ctx.get_ca_certs())} CA certificate(s) (OS + certifi)")
    except Exception as exc:  # noqa: BLE001 - runnable even outside the package
        print(f"tool context unavailable (run with PYTHONPATH=src): {exc}")
        return None
    return ctx


def main() -> int:
    print(f"python {sys.version.split()[0]}   platform {sys.platform}")
    for var in ("HTTPS_PROXY", "https_proxy", "ALLETRA_PROXY", "ALLETRA_CA_BUNDLE",
                "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"):
        print(f"  {var}={os.environ.get(var)!r}")

    certifi_ctx = _load_certifi_ctx()

    os_ctx = ssl.create_default_context()          # loads the Windows ROOT store
    print(f"OS trust store: {len(os_ctx.get_ca_certs())} CA certificate(s) loaded")

    tool_ctx = _load_tool_ctx()

    for host, port in HOSTS:
        print(f"\n=== {host}:{port} ===")
        # No verification: just to SEE the chain (never used by the app).
        peek = ssl._create_unverified_context()  # noqa: SLF001 - diagnostic only
        ok, detail, _ = _try(peek, host, port)
        if not ok:
            print(f"  cannot even connect: {detail}")
            continue
        with socket.create_connection((host, port), timeout=12) as raw, peek.wrap_socket(
            raw, server_hostname=host
        ) as tls:
            der = tls.getpeercert(binary_form=True)
        # The issuer shown by a SUCCESSFUL verified attempt is the informative part: on an
        # intercepted network the OS-store attempt succeeds and names the corporate CA.
        for label, ctx in (("certifi only (httpx default)", certifi_ctx),
                           ("OS trust store (browser)", os_ctx),
                           ("tool context (the fix)", tool_ctx)):
            if ctx is None:
                continue
            ok, detail, peer = _try(ctx, host, port)
            print(f"  {label:<30} {'TRUSTED' if ok else 'FAILED'}  {detail}")
            if ok and peer:
                print(f"      subject {_name(peer.get('subject'))}")
                print(f"      issuer  {_name(peer.get('issuer'))}")
        print(f"      (leaf certificate {len(der)} bytes)")

    print("\nReading:")
    print("  certifi FAILED + OS TRUSTED  -> corporate TLS inspection; the fix (OS store) solves it.")
    print("  both FAILED                  -> the inspecting root is not in the Windows store either;")
    print("                                  get the PEM from IT, set ALLETRA_CA_BUNDLE to it.")
    print("  both TRUSTED                 -> TLS is fine; the failure was something else.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
