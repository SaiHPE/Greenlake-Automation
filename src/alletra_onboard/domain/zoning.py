"""Zoning-context models: the array-side zoning VERIFY report and the read-only assisted zoning
PLAN (ADR 0004 — the tool never writes to the switch).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from alletra_onboard.domain.shared import Fabric


class ExpectedZone(BaseModel):
    fabric: Fabric
    switch_host: str
    name: str               # computed zone name
    host_wwpn: str          # normalized
    array_wwpn: str         # normalized
    present: bool = False    # already in the switch's active config?


class ZoneRemediation(BaseModel):
    """The exact, additive commands to create the missing zones on one fabric (preview before apply)."""

    fabric: Fabric
    switch_host: str
    cfg_name: str           # the active config the zones are added to
    commands: list[str]     # alicreate / zonecreate / cfgadd / cfgenable (never cfgsave-alone)


class ZoningReport(BaseModel):
    expected: list[ExpectedZone] = Field(default_factory=list)
    remediations: list[ZoneRemediation] = Field(default_factory=list)
    proper: bool = False     # every expected host zoned on both fabrics, none unverified
    # Expected hosts the array could NOT confirm on EITHER fabric — could be "not zoned" OR the host
    # is simply offline/not logged in (the array can't tell the two apart). Surfaced, never silently
    # passed; confirm the host is up, or cross-check the switch/ESXi.
    unverified_hosts: list[str] = Field(default_factory=list)
    source: str = "array"    # 'array' (showportdev ns) — verification needs no switch
    notes: list[str] = Field(default_factory=list)
    error: str | None = None


class AliasedWwpn(BaseModel):
    """One WWPN in the zoning plan — a host HBA port or an array target port — with the alias(es) the
    switch already has for it (there can be several on a shared fabric) and a suggested alias to
    pre-fill (the convention-matching existing one, else empty for the operator to type). See ADR 0004."""

    wwpn: str                                   # normalized (16 hex)
    display: str                                # colon-lowercase (Brocade form)
    role: Literal["host", "array"]
    fabric: str = ""                            # "F1" | "F2" | "" (offline / on neither fabric)
    nsp: str = ""                               # array target port n:s:p ("" for a host)
    host_name: str = ""                         # owning host ("" for an array port)
    existing_aliases: list[str] = Field(default_factory=list)  # every alias the switch has for this WWPN
    suggested_alias: str = ""                   # pre-fill: the convention match, else ""


class FabricZonePlan(BaseModel):
    """The plan for one fabric: the host + array WWPNs present on it, and the SIST pairs to zone."""

    fabric: str                                 # "F1" | "F2"
    switch_host: str
    active_cfg: str = ""                        # e.g. F1_CFG (from cfgshow Effective)
    hosts: list[AliasedWwpn] = Field(default_factory=list)        # host HBA ports on this fabric
    array_ports: list[AliasedWwpn] = Field(default_factory=list)  # array target ports online on this fabric
    pairs: list[tuple[str, str]] = Field(default_factory=list)    # (host_wwpn, array_wwpn) single-init-single-target


class ZoningPlan(BaseModel):
    """The read-only assisted zoning plan (ADR 0004): per-fabric host↔array SIST pairs + aliases, for
    the operator to name and the SAN team to apply. The tool never writes to the switch."""

    fabrics: list[FabricZonePlan] = Field(default_factory=list)
    offline_hosts: list[str] = Field(default_factory=list)  # host "name (wwpn)" on no fabric -> cable+power
    notes: list[str] = Field(default_factory=list)
    error: str | None = None
