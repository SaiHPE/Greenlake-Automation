"""Operator-facing TLS trust failure detection and guidance.

The SSLContext builder itself lives in ``adapters/tls.py`` (STANDARD L2, L4). This module stays
free of ``ssl`` so application code can classify a trust error and explain what to do next.
"""

from __future__ import annotations

import os

_CA_BUNDLE_VARS = ("ALLETRA_CA_BUNDLE", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")


def ca_bundle_override() -> str | None:
    """An explicitly configured CA bundle path, if one is set and actually exists."""
    for var in _CA_BUNDLE_VARS:
        path = (os.environ.get(var) or "").strip()
        if path and os.path.isfile(path):
            return path
    return None


def is_tls_trust_error(exc: BaseException) -> bool:
    """Is this failure "I could not verify the certificate", as opposed to a network or auth error?"""
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if any(cls.__name__ == "SSLCertVerificationError" for cls in type(current).__mro__):
            return True
        text = str(current).upper()
        if "CERTIFICATE_VERIFY_FAILED" in text or "UNABLE TO GET LOCAL ISSUER" in text:
            return True
        current = current.__cause__ or current.__context__
    return False


def tls_trust_guidance(host: str = "the HPE cloud endpoint") -> str:
    """What the operator should actually DO about a trust failure — the error text alone reads like
    a credential problem, which sends people to re-check their client secret for an hour."""
    bundle = ca_bundle_override()
    where = f" (currently using the CA bundle at {bundle})" if bundle else ""
    return (
        f"The TLS certificate presented for {host} could not be verified against this machine's "
        f"trusted certificate authorities{where}. Your credentials were not the problem — they were "
        "never sent. This is what a network that inspects TLS traffic (Zscaler, Netskope, a "
        "corporate proxy) looks like when its root certificate is not available to the tool. "
        "Ask IT for the corporate root CA certificate (PEM/CER), then either install it in the "
        "Windows 'Trusted Root Certification Authorities' store (the tool reads that store) or set "
        "ALLETRA_CA_BUNDLE to the file's path and restart the app. If this machine reaches the "
        "internet through a proxy, also confirm the proxy setting on this screen is correct."
    )
