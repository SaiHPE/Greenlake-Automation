"""Approved-plan object scopes for write-scoped SSH clients (ADR 0025 condition 3, STANDARD L3).

Defined in domain so both the application planners/appliers and the write-scoped SSH adapters can
name the exact object-scope value without application code importing the writer module directly.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RcPlanObjects:
    """What the approved plan names on one array: the only objects that array's write client may act on
    (ADR 0025 condition 3). `startrcopy` names nothing and needs only a bound client."""

    ports: frozenset[str] = frozenset()             # this array's RCIP ports, N:S:P
    addresses: frozenset[str] = frozenset()         # addresses set on those ports: RCIP address, gateway
    peer_addresses: frozenset[str] = frozenset()    # the other array's RCIP addresses: pinged, linked to
    targets: frozenset[str] = frozenset()           # Remote Copy targets on this array


@dataclass(frozen=True)
class SnapPlanObjects:
    """What the approved plan creates: the only schedules this client may write (ADR 0025 condition 3)."""

    schedules: frozenset[tuple[str, str]] = frozenset()    # (schedule name, source_ref) of the plan's creates


@dataclass(frozen=True)
class ZoningPlanObjects:
    """What the approved zoning plan creates on one Brocade fabric switch (ADR 0025 condition 3, ADR 0033)."""

    active_cfg: str
    aliases: tuple[tuple[str, str], ...] = ()          # (alias_name, normalized_wwpn) pairs to alicreate
    zones: tuple[tuple[str, str, str], ...] = ()       # (zone_name, member1, member2) triples to zonecreate
