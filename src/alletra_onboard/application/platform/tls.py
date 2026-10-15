"""TLS trust for outbound HTTPS — trust what the OPERATING SYSTEM trusts, like the browser does.

httpx (and requests) verify against **certifi's** CA bundle, which contains only public roots. A
corporate network that performs TLS inspection re-signs every connection with its own root CA; IT
installs that root in the **Windows certificate store**, so Edge/Chrome work fine — but certifi has
never heard of it, and every httpx call dies with:

    [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate

which is a *trust* failure, not an authentication failure (reported live from an HPE laptop at the
GreenLake credential step). ``ssl.create_default_context()`` loads the Windows ROOT store, so this
module builds a context from the OS trust store PLUS certifi (public roots stay covered even where
the OS store is thin, e.g. a stripped container) and every outbound client uses it.

Escape hatch for a site whose root is in a file rather than the store: point ``ALLETRA_CA_BUNDLE``
(or the conventional ``SSL_CERT_FILE`` / ``REQUESTS_CA_BUNDLE``) at a PEM. Verification is never
disabled — these are cloud credentials, and a tool that silently stops checking certificates on a
network that is provably intercepting traffic would be worse than the error it replaces.
"""

from __future__ import annotations

import os
import ssl

_CA_BUNDLE_VARS = ("ALLETRA_CA_BUNDLE", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")


def ca_bundle_override() -> str | None:
    """An explicitly configured CA bundle path, if one is set and actually exists.

    MEASURED on an HPE laptop: ``SSL_CERT_FILE=C:\\Users\\...\\zscaler-root-ca.pem`` — the corporate
    root already on disk. httpx never reads that variable (it uses certifi), which is why the tool
    failed on a machine whose other tooling had been made to work.
    """
    for var in _CA_BUNDLE_VARS:
        path = (os.environ.get(var) or "").strip()
        if path and os.path.isfile(path):
            return path
    return None


def ssl_context() -> ssl.SSLContext:
    """The verification context for every outbound HTTPS call: the UNION of every trust source we
    can find — the OS store, certifi, and any explicitly configured bundle. Verification stays ON.

    A union, not a choice, on purpose. Using a configured bundle *exclusively* (the obvious reading
    of SSL_CERT_FILE) breaks every host the interceptor does NOT re-sign: a Zscaler root PEM alone
    cannot verify a genuine Amazon-issued HPE certificate, so a split-tunnel or bypassed endpoint
    would start failing the moment we "fixed" the intercepted one.
    """
    # create_default_context() calls load_default_certs(), which on Windows enumerates the ROOT
    # store — this is what picks up a corporate/TLS-inspection root that certifi cannot know about.
    context = ssl.create_default_context()
    for loader in (_load_certifi, _load_override):
        try:
            loader(context)
        except Exception:  # noqa: BLE001 - a source we cannot read must not break the others
            pass
    return context


def _load_certifi(context: ssl.SSLContext) -> None:
    import certifi

    context.load_verify_locations(cafile=certifi.where())


def _load_override(context: ssl.SSLContext) -> None:
    override = ca_bundle_override()
    if override:
        context.load_verify_locations(cafile=override)


def is_tls_trust_error(exc: BaseException) -> bool:
    """Is this failure "I could not verify the certificate", as opposed to a network or auth error?"""
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, ssl.SSLCertVerificationError):
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
