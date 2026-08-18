"""Outbound TLS trust — verify against the OS store, and never call a trust failure an auth failure.

Reported live from an HPE laptop at the GreenLake credential step:
    ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] ... unable to get local issuer certificate
shown as "GreenLake credentials were rejected". The credentials were never sent: httpx verifies
against certifi's public-root bundle, so a corporate TLS-inspection root that Edge trusts (it lives
in the Windows store) is invisible to the tool.
"""

from __future__ import annotations

import ssl

from alletra_onboard.application.platform.tls import (
    ca_bundle_override,
    is_tls_trust_error,
    ssl_context,
    tls_trust_guidance,
)


def _clear(monkeypatch):
    for var in ("ALLETRA_CA_BUNDLE", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"):
        monkeypatch.delenv(var, raising=False)


def test_context_verifies_and_carries_ca_certificates(monkeypatch):
    _clear(monkeypatch)
    ctx = ssl_context()
    assert ctx.verify_mode == ssl.CERT_REQUIRED       # verification is never disabled
    assert ctx.check_hostname is True
    assert len(ctx.get_ca_certs()) > 0                 # OS store and/or certifi actually loaded


def test_explicit_ca_bundle_wins(monkeypatch, tmp_path):
    """A site whose root lives in a file, not the store: ALLETRA_CA_BUNDLE points at it."""
    import certifi

    _clear(monkeypatch)
    bundle = tmp_path / "corp.pem"
    bundle.write_bytes(open(certifi.where(), "rb").read())   # a real, loadable PEM
    monkeypatch.setenv("ALLETRA_CA_BUNDLE", str(bundle))
    assert ca_bundle_override() == str(bundle)
    assert ssl_context().verify_mode == ssl.CERT_REQUIRED


def test_a_nonexistent_bundle_path_is_ignored_not_fatal(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.setenv("SSL_CERT_FILE", str(tmp_path / "nope.pem"))
    assert ca_bundle_override() is None
    assert ssl_context().verify_mode == ssl.CERT_REQUIRED    # falls back to the OS store


def test_is_tls_trust_error_sees_through_the_wrapping():
    """httpx wraps the SSLError in a ConnectError; the classifier must follow the chain."""
    verify = ssl.SSLCertVerificationError(
        "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate"
    )
    assert is_tls_trust_error(verify)

    try:
        try:
            raise verify
        except ssl.SSLCertVerificationError as inner:
            raise ConnectionError("connection failed") from inner
    except ConnectionError as wrapped:
        assert is_tls_trust_error(wrapped)              # found via __cause__

    # And the exact text httpx surfaces, even when the type is a plain Exception.
    assert is_tls_trust_error(Exception(
        "ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: "
        "unable to get local issuer certificate (_ssl.c:1010)"
    ))


def test_is_tls_trust_error_does_not_claim_ordinary_failures():
    assert not is_tls_trust_error(Exception("401 Unauthorized"))
    assert not is_tls_trust_error(Exception("ConnectTimeout"))
    assert not is_tls_trust_error(Exception("getaddrinfo failed"))


def test_guidance_names_the_remedy_not_the_credentials():
    text = tls_trust_guidance("the HPE GreenLake API")
    assert "were not the problem" in text and "never" in text
    assert "ALLETRA_CA_BUNDLE" in text and "Trusted Root" in text


async def test_greenlake_check_reports_trust_failure_separately(monkeypatch):
    """The health check must not label a trust failure as rejected credentials."""
    from alletra_onboard.application.onboarding import health
    from alletra_onboard.config import Settings

    class _Boom:
        def __init__(self):
            self.service_catalog = self
            self.http = self

        async def per_region_service_managers(self):
            raise ConnectionError(
                "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: "
                "unable to get local issuer certificate (_ssl.c:1010)"
            )

    monkeypatch.setattr(health, "missing_credentials", lambda settings: [])
    monkeypatch.setattr(health, "make_greenlake", lambda settings: _Boom())
    report = await health.greenlake_check(Settings())
    assert report.ok is False and report.tls_trust_failure is True
    assert "certificate" in (report.error or "").lower()
    assert "were not the problem" in (report.error or "")


async def test_greenlake_check_leaves_other_failures_alone(monkeypatch):
    from alletra_onboard.application.onboarding import health
    from alletra_onboard.config import Settings

    class _Boom:
        def __init__(self):
            self.service_catalog = self
            self.http = self

        async def per_region_service_managers(self):
            raise RuntimeError("401 Unauthorized")

    monkeypatch.setattr(health, "missing_credentials", lambda settings: [])
    monkeypatch.setattr(health, "make_greenlake", lambda settings: _Boom())
    report = await health.greenlake_check(Settings())
    assert report.ok is False and report.tls_trust_failure is False
    assert "401" in (report.error or "")
