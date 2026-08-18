"""The array wizard address — IPv4 *and* IPv6 link-local.

REPORTED LIVE 2026-08-17: the HPE Discovery Tool (1.1.2) found a new array (serial CZ2D2K014S) on
IPv6 only and returned https://[fe80::6095:14a0:b25d:fcb0]. The rule was spelled
``startswith("https://169.254.")`` in four separate places, so the Cloud Connectivity step could
not be started at all with an address the vendor's own tool had just produced.
"""

from __future__ import annotations

import pytest

from alletra_onboard.domain.cloudinit_url import is_valid_cloudinit_url, normalize_cloudinit_url

LIVE_IPV6 = "https://[fe80::6095:14a0:b25d:fcb0]"


def test_the_reported_ipv6_address_is_accepted_and_gets_the_path():
    url, reason = normalize_cloudinit_url(LIVE_IPV6)
    assert reason is None
    assert url == "https://[fe80::6095:14a0:b25d:fcb0]/cloudinit"


def test_ipv6_with_the_path_already_present_is_unchanged():
    url, reason = normalize_cloudinit_url(f"{LIVE_IPV6}/cloudinit")
    assert reason is None and url == "https://[fe80::6095:14a0:b25d:fcb0]/cloudinit"


@pytest.mark.parametrize("raw,expected_zone", [
    ("https://[fe80::1%eth0]/cloudinit", "eth0"),      # operators paste the bare % form
    ("https://[fe80::1%25eth0]/cloudinit", "eth0"),    # RFC 6874 encoded form
    ("https://[fe80::1%12]/cloudinit", "12"),          # Windows numeric scope id
])
def test_ipv6_zone_is_preserved_and_percent_encoded(raw, expected_zone):
    """A link-local address is ambiguous on a multi-homed host, so the interface scope must
    survive — and RFC 6874 requires the separator encoded as %25 inside a URI."""
    url, reason = normalize_cloudinit_url(raw)
    assert reason is None
    assert url == f"https://[fe80::1%25{expected_zone}]/cloudinit"


def test_ipv4_link_local_still_works():
    url, reason = normalize_cloudinit_url("https://169.254.239.27/cloudinit")
    assert reason is None and url == "https://169.254.239.27/cloudinit"
    url, reason = normalize_cloudinit_url("https://169.254.239.27")     # bare origin from the tool
    assert reason is None and url == "https://169.254.239.27/cloudinit"


def test_the_workbook_placeholder_is_still_refused():
    url, reason = normalize_cloudinit_url("https://169.254.0.0/cloudinit")
    assert url is None and "placeholder" in reason


@pytest.mark.parametrize("raw,needle", [
    ("https://10.132.30.121/cloudinit", "link-local"),        # the array's MANAGEMENT ip
    ("https://[2001:db8::1]/cloudinit", "link-local"),        # routable IPv6
    ("http://169.254.1.2/cloudinit", "https"),                # the wizard is https
    ("https://array.example.com/cloudinit", "not an IP"),
    ("", "Discovery Tool"),
    (None, "Discovery Tool"),
])
def test_refusals_say_why(raw, needle):
    """This address reaches an UNAUTHENTICATED setup wizard, so it must be provably link-local —
    never a routable host that happens to answer."""
    url, reason = normalize_cloudinit_url(raw)
    assert url is None
    assert needle.lower() in reason.lower()


def test_is_valid_matches_normalize():
    assert is_valid_cloudinit_url(LIVE_IPV6)
    assert not is_valid_cloudinit_url("https://10.132.30.121/cloudinit")


def test_link_local_ipv6_never_goes_through_a_proxy():
    """A proxy has no route to an address that only means anything on this cable."""
    from alletra_onboard.application.platform import proxy

    resolver = proxy.ProxyResolver(manual="corp:8080")
    assert resolver.for_url("https://[fe80::6095:14a0:b25d:fcb0]/cloudinit") is None
    assert resolver.for_url("https://[fe80::1%25eth0]/cloudinit") is None
    assert resolver.for_url("https://169.254.1.2/cloudinit") is None
    assert resolver.for_url("https://common.cloud.hpe.com") == "http://corp:8080"
