"""The array's on-box wizard address — one implementation of what a valid one looks like.

The array answers on a LINK-LOCAL address that changes on every boot, and the HPE Discovery Tool
reports whichever family it found the array on:

    IPv4   https://169.254.239.27/cloudinit
    IPv6   https://[fe80::6095:14a0:b25d:fcb0]/cloudinit        <- rejected before 2026-08-17

REPORTED LIVE: the Discovery Tool (1.1.2) returned only an IPv6 link-local address for a new array
(serial CZ2D2K014S) and the step could not be started at all — the rule was spelled
``startswith("https://169.254.")`` in four places, so an address the vendor's own tool had just
produced was treated as invalid input.

Rules, deliberately narrow — this address reaches an unauthenticated setup wizard, so it must be
provably link-local and never a routable host:
  * IPv4 in 169.254.0.0/16, except 169.254.0.0 itself (the workbook's "not recorded yet" placeholder)
  * IPv6 in fe80::/10, bracketed, with an optional zone id (``%eth0`` / ``%12``)
  * https only, and the path defaults to ``/cloudinit`` when omitted (the Discovery Tool's Launch
    field gives the bare origin)

On the zone id: a link-local IPv6 address is ambiguous on a multi-homed host, so an interface
scope may be required to connect. RFC 6874 percent-encodes the separator inside a URI
(``[fe80::1%25eth0]``); operators paste the bare ``%`` form, so accept both and emit the encoded
one.
"""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

IPV4_LINK_LOCAL = ipaddress.ip_network("169.254.0.0/16")
IPV6_LINK_LOCAL = ipaddress.ip_network("fe80::/10")
#: The workbook carries this when no per-boot address has been recorded yet.
PLACEHOLDER_HOST = "169.254.0.0"
DEFAULT_PATH = "/cloudinit"

_ZONE = re.compile(r"%(?:25)?(?P<zone>[A-Za-z0-9._-]+)$")

EXAMPLE = "https://169.254.12.34/cloudinit or https://[fe80::1%25eth0]/cloudinit"


def _split_zone(host: str) -> tuple[str, str]:
    """('fe80::1%25eth0') -> ('fe80::1', 'eth0'); no zone -> (host, '')."""
    match = _ZONE.search(host)
    if not match:
        return host, ""
    return host[: match.start()], match.group("zone")


def normalize_cloudinit_url(raw: str | None) -> tuple[str | None, str | None]:
    """Validate and canonicalise a wizard address.

    Returns ``(url, None)`` when valid — with the ``/cloudinit`` path filled in and any IPv6 zone
    percent-encoded — or ``(None, reason)`` when not. The reason is operator-facing.
    """
    value = (raw or "").strip()
    if not value:
        return None, "Enter the array's wizard address from the Discovery Tool."
    if not value.lower().startswith("https://"):
        return None, f"The address must start with https:// — for example {EXAMPLE}."

    try:
        parts = urlsplit(value)
        host = parts.hostname or ""
    except ValueError as exc:  # malformed IPv6 literal / bad brackets
        return None, f"That is not a valid URL ({exc}). Example: {EXAMPLE}."
    if not host:
        return None, f"No address found in that URL. Example: {EXAMPLE}."

    bare, zone = _split_zone(host)
    try:
        address = ipaddress.ip_address(bare)
    except ValueError:
        return None, (
            f"'{bare}' is not an IP address. Paste the link-local address the Discovery Tool "
            f"shows, for example {EXAMPLE}."
        )

    if address.version == 4:
        if address not in IPV4_LINK_LOCAL:
            return None, (
                f"{address} is not a link-local address. The wizard answers on 169.254.x.x "
                "(IPv4) or fe80:: (IPv6) — not the array's management IP."
            )
        if str(address) == PLACEHOLDER_HOST:
            return None, (
                "169.254.0.0 is the workbook's placeholder, not a real address. Search the "
                "Discovery Tool for this serial and paste the current link."
            )
        rendered_host = str(address)
    else:
        if address not in IPV6_LINK_LOCAL:
            return None, (
                f"{address} is not a link-local address. An IPv6 wizard address starts with "
                "fe80: — not the array's management IP."
            )
        rendered_host = f"[{address}%25{zone}]" if zone else f"[{address}]"

    path = parts.path if parts.path not in ("", "/") else DEFAULT_PATH
    return f"https://{rendered_host}{path}", None


def is_valid_cloudinit_url(raw: str | None) -> bool:
    return normalize_cloudinit_url(raw)[0] is not None
