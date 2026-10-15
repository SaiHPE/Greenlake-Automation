"""Proxy normalisation on NetworkConfig.

The array's Cloud Connectivity wizard validates Proxy Server as an IPv4 or domain name and rejects
a scheme — seen live: 'Value must be valid IPv4 or domain name' on 'http://proxy.…'. Operators
naturally paste the URL form, so intake normalises it rather than letting the wizard reject it.
"""

from alletra_onboard.domain.models import NetworkConfig


def _net(**overrides) -> NetworkConfig:
    return NetworkConfig(
        mgmt_ipv4="192.0.2.40",
        mask="255.255.248.0",
        gateway="192.0.2.254",
        ntp="ntp.example.net",
        timezone="Asia/Kolkata",
        **overrides,
    )


def test_proxy_url_form_is_normalised_to_a_bare_host():
    net = _net(proxy_host="http://proxy.bgl1.global.tslabs.hpecorp.net", proxy_port=8080)
    assert net.proxy_host == "proxy.bgl1.global.tslabs.hpecorp.net"
    assert net.proxy_port == 8080


def test_proxy_embedded_port_fills_the_port_field():
    net = _net(proxy_host="https://proxy.example.net:8080/")
    assert net.proxy_host == "proxy.example.net"
    assert net.proxy_port == 8080


def test_proxy_explicit_port_wins_over_an_embedded_one():
    net = _net(proxy_host="proxy.example.net:3128", proxy_port=8080)
    assert net.proxy_host == "proxy.example.net"
    assert net.proxy_port == 8080


def test_bare_proxy_host_is_unchanged():
    net = _net(proxy_host="proxy.example.net", proxy_port=8080)
    assert net.proxy_host == "proxy.example.net"
    assert net.proxy_port == 8080


def test_no_proxy_stays_none():
    assert _net().proxy_host is None
