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


ActionKind = Literal["host", "hostset", "volume", "vvset", "vlun", "schedule", "snapshot"]

# What the plan predicts apply will do to one object (SPEC-001 R1). `conflict` blocks apply.
PlanState = Literal["create", "exists", "update", "conflict"]

#: SPEC-007 R3 and SPEC-023 R6: the order a removal set pastes in, top to bottom. A schedule first, so it
#: takes no more snapshots; snapshots before their base volume (`removevv` refuses a volume that still
#: has snapshots); exports, sets and members after. The one order every renderer sorts by (LESSONS 19).
REMOVAL_ORDER: dict[str, int] = {
    "schedule": 0, "snapshot": 1, "vlun": 2, "vvset": 3, "volume": 4, "hostset": 5, "host": 6,
}


class RemovalItem(BaseModel):
    """One CLI line that undoes one thing THIS apply created (SPEC-007). Text the operator pastes;
    the tool never runs it. `kind` orders the block so it can be pasted top to bottom."""

    kind: ActionKind
    name: str                 # the object; for an export "<volume> LUN <n> → <target>"
    command: str


ArrayProvisioningType = Literal["full", "tpvv", "snp", "peer", "unknown", "reduce", "dds"]


class ArrayVolumeRecord(BaseModel):
    name: str
    size_mib: int
    cpg: str
    provisioning_type: ArrayProvisioningType
    id: int | None = None          # SPEC-012 R1
    wwn: str = ""
    # SPEC-023 R3: a snapshot names its base in copy_of; times are WSAPI's ISO 8601 text, "" when unset.
    copy_of: str = ""
    read_only: bool = False
    created: str = ""
    expires: str = ""
