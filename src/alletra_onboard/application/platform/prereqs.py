"""Network prerequisites: the HPE firewall rules the customer's network team must open, plus a
live reachability check the operator can run from the jump box.

Single source of truth for the firewall list — the UI table, the downloadable ``.txt`` (which the
customer forwards to their network team), and the Initialisation-sheet "Prerequisites" tab all read
from here. ``<instance>`` is substituted with the DSCC region — confirmed codes are us1 (America),
eu1 (Europe), jp1 (Japan), uk1 (UK); HPE keeps adding regions, so any code the operator supplies is
accepted (never a closed list). Sources: HPE DSCC Security Guide (a00113337) + the "Network
requirement details for HPE Alletra Storage MP B10000".
"""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

from alletra_onboard.application.platform.proxy import ProxyResolver

# (fqdn, port, initiator, purpose). All outbound TCP 443.
FIREWALL_RULES: list[tuple[str, str, str, str]] = [
    ("console.greenlake.hpe.com", "TCP 443", "User", "HPE GreenLake"),
    ("<instance>.data.cloud.hpe.com", "TCP 443", "User / API", "DSCC instance (user + API)"),
    ("console-<instance>.data.cloud.hpe.com", "TCP 443", "User", "DSCC console"),
    ("tunnel-<instance>.data.cloud.hpe.com", "TCP 443", "Storage system, Data Orchestrator", "DSCC tunnel"),
    ("common.cloud.hpe.com", "TCP 443", "User / API", "HPE GreenLake common services"),
    ("device.cloud.hpe.com", "TCP 443", "Storage system", "Hardware device activation"),
    ("midway.ext.hpe.com", "TCP 443", "User / API", "Software device activation, RDA, InfoSight"),
    ("cosm-*.s3.*.amazonaws.com", "TCP 443", "PSG", "AWS S3 buckets"),
    ("h30689.www3.hpe.com", "TCP 443", "Storage system", "Software updates & patches"),
    ("infosight.hpe.com", "TCP 443", "User", "HPE InfoSight"),
    ("infosight.itcs.hpe.com", "TCP 443", "Storage system", "InfoSight telemetry"),
    ("infosight1.itcs.hpe.com", "TCP 443", "Storage system", "InfoSight telemetry"),
    ("api.support.hpe.com", "TCP 443", "Storage system", "HPE support API"),
]

# The connectivity button tests these (region-substituted). Wildcard hosts (cosm-*.s3.*) can't be
# resolved/connected directly, so they're intentionally excluded from the live test.
_TEST_HOSTS: tuple[str, ...] = (
    "console.greenlake.hpe.com",
    "<instance>.data.cloud.hpe.com",
    "console-<instance>.data.cloud.hpe.com",
    "tunnel-<instance>.data.cloud.hpe.com",
    "common.cloud.hpe.com",
    "device.cloud.hpe.com",
    "midway.ext.hpe.com",
)

RESERVED_IPS = (
    "16.1.8.11", "16.1.8.27", "16.1.8.43", "16.1.8.59",
    "16.1.9.11", "16.1.9.27", "16.1.9.43", "16.1.9.59",
)


def rules_for(region: str = "jp1") -> list[tuple[str, str, str, str]]:
    """The firewall rules with ``<instance>`` substituted for the DSCC region."""
    region = (region or "jp1").strip() or "jp1"
    return [(fqdn.replace("<instance>", region), port, initiator, purpose)
            for fqdn, port, initiator, purpose in FIREWALL_RULES]


def firewall_text(region: str = "jp1") -> str:
    """The downloadable plain-text firewall list to hand the customer's network team."""
    region = (region or "jp1").strip() or "jp1"
    lines = [
        "HPE Alletra Storage MP B10000 - required firewall rules",
        "=" * 56,
        "All destinations are OUTBOUND, TCP 443.",
        "Source: your storage-system management IP(s) (and the onboarding jump box).",
        f"DSCC region (<instance>): {region}",
        "",
        f"{'Destination (FQDN)':<46}{'Port':<10}Purpose",
        f"{'-' * 44:<46}{'-' * 8:<10}{'-' * 32}",
    ]
    for fqdn, port, _initiator, purpose in rules_for(region):
        lines.append(f"{fqdn:<46}{port:<10}{purpose}")
    lines += [
        "",
        "Also required:",
        "  - mDNS UDP 5353 - local array discovery (HPE Discovery app).",
        "Reserved (do NOT assign these to anything): " + ", ".join(RESERVED_IPS),
        "  (the CDM link-local range).",
        "",
        "Reference: HPE Alletra Storage MP B10000 - Network requirement details",
        "(Planning / Installing and configuring guide, sd00002405).",
    ]
    return "\n".join(lines) + "\n"


@dataclass
class ConnectivityResult:
    host: str
    port: int
    reachable: bool
    detail: str
    via: str = ""  # the proxy used ("" = tested directly)


async def _check_one(host: str, port: int, timeout: float) -> ConnectivityResult:
    try:
        future = asyncio.open_connection(host, port)
        _reader, writer = await asyncio.wait_for(future, timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:  # noqa: BLE001 - closing is best-effort
            pass
        return ConnectivityResult(host, port, True, "reachable")
    except asyncio.TimeoutError:
        return ConnectivityResult(host, port, False, "timed out - the port is filtered or blocked")
    except socket.gaierror:
        return ConnectivityResult(host, port, False, "DNS could not resolve the host")
    except OSError as exc:
        return ConnectivityResult(host, port, False, f"blocked ({type(exc).__name__})")


async def _check_via_proxy(host: str, port: int, proxy_url: str, timeout: float) -> ConnectivityResult:
    """Reachability THROUGH the proxy — an HTTP CONNECT tunnel, exactly how the tool's traffic goes."""
    parsed = urlparse(proxy_url)
    phost, pport = parsed.hostname or "", parsed.port or 8080
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(phost, pport), timeout=timeout)
    except Exception:  # noqa: BLE001
        return ConnectivityResult(host, port, False, f"proxy {phost}:{pport} not reachable", via=proxy_url)
    try:
        writer.write(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".encode())
        await writer.drain()
        line = (await asyncio.wait_for(reader.readline(), timeout=timeout)).decode("latin1", "replace").strip()
        if "407" in line:
            return ConnectivityResult(host, port, False, "proxy requires authentication (407)", via=proxy_url)
        ok = " 200 " in f" {line} " or "200 connection" in line.lower()
        return ConnectivityResult(host, port, ok, "reachable via proxy" if ok else f"proxy said: {line}", via=proxy_url)
    except Exception as exc:  # noqa: BLE001
        return ConnectivityResult(host, port, False, f"proxy error ({type(exc).__name__})", via=proxy_url)
    finally:
        writer.close()


async def check_connectivity(
    region: str = "jp1", timeout: float = 6.0, manual_proxy: str | None = None
) -> list[ConnectivityResult]:
    """Reachability to the key HPE endpoints, using the SAME path the tool will use: through the
    effective proxy (auto-detected system proxy, or the manual override) if there is one, else direct.
    So a proxy-only network no longer shows everything as blocked."""
    region = (region or "jp1").strip() or "jp1"
    hosts = [h.replace("<instance>", region) for h in _TEST_HOSTS]
    resolver = ProxyResolver(manual_proxy)

    async def _check(host: str) -> ConnectivityResult:
        proxy = resolver.for_url(f"https://{host}")
        return await (_check_via_proxy(host, 443, proxy, timeout) if proxy else _check_one(host, 443, timeout))

    return list(await asyncio.gather(*[_check(h) for h in hosts]))
