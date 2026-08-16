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


class NsDevice(BaseModel):
    """One device from the fabric name server (`nsshow` local / `nscamshow` remote) — the ONLY view
    that sees unzoned-but-online devices, and richer than we first assumed. Measured on live VZ
    switches (tests/fixtures/vz_fabric): NodeSymb carries the HOST's own name and OS
    (``HN:DL360G11D24U25 OS:VMware ESXi 8.0.3``), an array port's PortSymb carries its serial and
    n:s:p (``SGHD44LQLS - 0:3:1 - HPE64004-B``), and Device type classifies initiator vs target
    outright — so the zoning builder can identify hosts from the switch alone, without vCenter
    (which on a vault network is routinely unreachable, and names hosts by IP anyway).

    TRAP the model exists to make unmissable: every FC-NVMe-capable array port registers TWICE —
    the physical FCP entry plus an ``NPIV Target`` shadow with its own WWPN. Zones must pair
    physical ports only; use the ``is_physical_*`` properties, never bare membership."""

    wwpn: str                   # normalized (16 hex)
    device_type: str = ""       # raw: "Physical Initiator" | "Physical Target" | "NPIV Target" | ...
    port_symb: str = ""
    node_symb: str = ""
    permanent_wwpn: str = ""    # an NPIV entry points at its physical port here (normalized)
    host_name: str = ""         # from NodeSymb "HN:<name>" ("" when not advertised)
    os: str = ""                # from NodeSymb "OS:<text>"
    array_serial: str = ""      # from an array port's PortSymb ("" for hosts)
    array_nsp: str = ""         # n:s:p from the same ("" for hosts)

    @property
    def is_npiv(self) -> bool:
        return "npiv" in self.device_type.lower()

    @property
    def is_physical_initiator(self) -> bool:
        return "initiator" in self.device_type.lower() and not self.is_npiv

    @property
    def is_physical_target(self) -> bool:
        return "target" in self.device_type.lower() and not self.is_npiv


class AliasedWwpn(BaseModel):
    """One WWPN in the zoning plan — a host HBA port or an array target port — with the alias(es) the
    switch already has for it (there can be several on a shared fabric) and a suggested alias to
    pre-fill (the convention-matching existing one, else empty for the operator to type). See ADR 0004."""

    wwpn: str                                   # normalized (16 hex)
    display: str                                # colon-lowercase (Brocade form)
    role: Literal["host", "array"]
    fabric: str = ""                            # "F1" | "F2" | "" (offline / on neither fabric)
    nsp: str = ""                               # array target port n:s:p ("" for a host)
    host_name: str = ""                         # owning host ("" for an array port, or a host that
    #                                             advertises no name — QLogic HBAs publish no HN:)
    host_source: str = ""                       # "vcenter" | "switch" — where the host identity came
    #                                             from ("switch" = the declared switch's local NS,
    #                                             used when vCenter reports nothing)
    existing_aliases: list[str] = Field(default_factory=list)  # every alias the switch has for this WWPN
    suggested_alias: str = ""                   # pre-fill: the convention match, else ""
    caution: str = ""                           # non-empty = select knowingly (e.g. an RCFC/Peer-labelled
    #                                             array port: usually replication, but proven live to
    #                                             carry host logins — flagged, never hard-dropped)


class FabricZonePlan(BaseModel):
    """The plan for one fabric: the host + array WWPNs present on it, and the SIST pairs to zone.

    `pairs` is every CANDIDATE (host, array) pair; `already_zoned` is the subset the fabric's
    effective configuration already permits (both WWPNs share a zone). The DELTA — what the
    command preview may create — is pairs minus already_zoned. On a fully-zoned bed (VZ) that
    delta is empty and the preview must emit NOTHING: proposing zones that already exist against
    a production config is the failure mode this field exists to prevent (ADR 0004)."""

    fabric: str                                 # "F1" | "F2"
    switch_host: str
    active_cfg: str = ""                        # e.g. F1_CFG (from cfgshow Effective)
    hosts: list[AliasedWwpn] = Field(default_factory=list)        # host HBA ports on this fabric
    array_ports: list[AliasedWwpn] = Field(default_factory=list)  # array target ports online on this fabric
    pairs: list[tuple[str, str]] = Field(default_factory=list)    # (host_wwpn, array_wwpn) single-init-single-target
    already_zoned: list[tuple[str, str]] = Field(default_factory=list)  # subset of pairs the active cfg covers


class ZoningPlan(BaseModel):
    """The read-only assisted zoning plan (ADR 0004): per-fabric host↔array SIST pairs + aliases, for
    the operator to name and the SAN team to apply. The tool never writes to the switch."""

    fabrics: list[FabricZonePlan] = Field(default_factory=list)
    offline_hosts: list[str] = Field(default_factory=list)  # host "name (wwpn)" on no fabric -> cable+power
    notes: list[str] = Field(default_factory=list)
    error: str | None = None


class FabricStageResult(BaseModel):
    """What staging did to ONE fabric switch: the additive commands executed and committed to the
    DEFINED config (cfgsave), the read-back verification, and the manual activation hand-off. The
    tool never runs `cfgenable`; `handoff` is the command a human runs during a maintenance window."""

    fabric: str                                  # "F1" | "F2"
    switch_host: str = ""
    staged: list[str] = Field(default_factory=list)   # commands the switch accepted (committed)
    skipped: list[str] = Field(default_factory=list)  # selected pairs that could not render (no alias)
    verified: bool = False                       # cfgshow re-read: zones in DEFINED, effective cfg unchanged
    handoff: str = ""                            # e.g. 'cfgenable F1_CFG' — for the human, never run
    error: str | None = None


class ZoningStageResult(BaseModel):
    """The staged-write outcome across both fabrics, plus the Broadcom defined≠effective warning that
    must be shown until a human activates (the divergence is documented to yield different effective
    zoning across switches on a zone merge or HA failover)."""

    fabrics: list[FabricStageResult] = Field(default_factory=list)
    warning: str = ""
