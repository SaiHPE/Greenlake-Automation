"""Domain primitives shared across the storage contexts (discovery, zoning, provisioning):
device credentials, the fabric literal, and WWPN normalisation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, SecretStr

Fabric = Literal["odd", "even"]


def normalize_wwpn(raw: str) -> str:
    """Canonical WWPN for matching: hex only, uppercase, no separators.

    ESXi reports colon-separated lowercase (``10:00:5c:ed:…``); the array (``showhost`` /
    ``showport``) is colon-less uppercase (``10005CED…``). Normalising both to this form is what
    lets host and array WWNs be compared (see the lab calibration notes).
    """
    return "".join(c for c in raw if c in "0123456789abcdefABCDEF").upper()


def wwpn_colons(normalized: str) -> str:
    """Render a normalized WWPN back as colon-separated lowercase (Brocade/zoning display form)."""
    n = normalized.lower()
    return ":".join(n[i : i + 2] for i in range(0, len(n), 2))


class EndpointCreds(BaseModel):
    """An IP/host + username + password for a device the tool logs into (array, vCenter, switch)."""

    host: str
    username: str
    password: SecretStr
