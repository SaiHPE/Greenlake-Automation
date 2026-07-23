"""Domain models for storage provisioning (Phase 2).

These are the contracts the WSAPI/vCenter/Brocade adapters fill and the discovery / zoning /
provision services produce. Kept in their own module (distinct from the onboarding models) because
storage provisioning is a separate subdomain — see docs/adr/0002-0004 and the FC provisioning runbook.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, SecretStr

Fabric = Literal["odd", "even"]
ProvisioningType = Literal["tpvv", "reduce"]


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


# Host persona is DERIVED from the discovered host OS (discovery is vCenter/ESXi today → VMware default).
# We return the persona NAME here and let the WSAPI adapter map it to the array's persona id, because the
# two numbering schemes differ and it is a trap: the CLI `showhost -listpersona` calls VMware "11", but
# the WSAPI enum that `createHost` needs calls VMware 8 (verified against the hpe3parclient constants AND
# a live Alletra MP whose VMware ESXi hosts reported WSAPI persona 8). Passing the CLI number to createHost
# would create ESXi hosts with the *Windows* persona. Resolving by name keeps the two from ever mixing.
PersonaName = Literal["VMware", "WindowsServer", "Generic-ALUA"]


def persona_for_os(os: str | None) -> PersonaName:
    """Map a host OS string (e.g. from vCenter) to its host persona NAME. Defaults to VMware."""
    s = (os or "").lower()
    if "vmware" in s or "esxi" in s:
        return "VMware"
    if "windows" in s:
        return "WindowsServer"
    if any(k in s for k in ("linux", "rhel", "red hat", "ubuntu", "suse", "centos", "oracle", "debian")):
        return "Generic-ALUA"
    return "VMware"  # default: the tool discovers ESXi hosts today


# ------------------------------------------------------------------ provisioning intent (the sheet)

class EndpointCreds(BaseModel):
    """An IP/host + username + password for a device the tool logs into (array, vCenter, switch)."""

    host: str
    username: str
    password: SecretStr


class VolumeSpec(BaseModel):
    """A compact volume request: <name_prefix>NN for count volumes of size_gib each."""

    name_prefix: str
    size_gib: int
    count: int = 1

    def names(self) -> list[str]:
        if self.count <= 1:
            return [self.name_prefix]
        width = max(2, len(str(self.count)))
        return [f"{self.name_prefix}{i:0{width}d}" for i in range(1, self.count + 1)]


class ProvisioningIntent(BaseModel):
    """What the operator supplies on the Provisioning tab to drive a provisioning run."""

    host_set_name: str
    array: EndpointCreds          # mgmt IP + admin (e.g. 3paradm) + password
    vcenter: EndpointCreds        # vCenter for read-only ESXi HBA discovery
    switch_f1: EndpointCreds      # odd fabric (F1)
    switch_f2: EndpointCreds      # even fabric (F2)
    cpg: str = "SSD_r6"
    provisioning_type: ProvisioningType = "tpvv"
    volume: VolumeSpec
    vvset_name: str | None = None


# ------------------------------------------------------------------ discovery

class ArrayPort(BaseModel):
    node: int
    slot: int
    card_port: int
    protocol: str = "fc"    # "fc" | "iscsi"
    wwpn: str = ""          # normalized FC port WWPN ("" for iSCSI)
    address: str = ""       # iSCSI target IP ("" for FC)
    link_state: str         # ready | offline | loss_sync | ...
    # FC only. Derived from the switch this port attaches to (showportdev fcfabric) when it is
    # 'ready' and resolvable; otherwise falls back to card-port parity (odd card_port -> odd fabric,
    # even -> even). See docs/adr/0009.
    fabric: Fabric | None = None
    fabric_switch: str = ""  # the switch/fabric-entry name from showportdev fcfabric ("" if unknown)
    usage: str = ""          # showport Label token: "RCFC"/"Peer" = replication/peer port, NOT a host target

    @property
    def label(self) -> str:
        return f"{self.node}:{self.slot}:{self.card_port}"

    @property
    def identifier(self) -> str:
        """WWPN for FC, target IP for iSCSI — the port's addressable id for display."""
        return self.wwpn if self.protocol == "fc" else self.address


class HostHba(BaseModel):
    host_name: str
    wwpn: str               # normalized
    model: str | None = None
    os: str | None = None
    fabric: Fabric | None = None  # set from which array fabric the WWPN logs into (via showhost)


class ArrayHost(BaseModel):
    """A host the ARRAY knows (from `showhost -d`) — the authoritative, curated host view (real hosts
    only, never storage ports). Each FC WWPN maps to the array ports (n:s:p) it is logged into; an
    empty port list means the WWPN is configured on the array but NOT logged in (not zoned / offline)."""

    name: str
    persona: str = ""                                      # VMware | WindowsServer | Generic-ALUA | ...
    wwpns: dict[str, list[str]] = Field(default_factory=dict)  # normalized WWPN -> [n:s:p logged in]


class DiscoveryReport(BaseModel):
    array_ports: list[ArrayPort] = Field(default_factory=list)
    host_hbas: list[HostHba] = Field(default_factory=list)
    array_hosts: list[ArrayHost] = Field(default_factory=list)  # from showhost -d (zoning source)
    notes: list[str] = Field(default_factory=list)
    error: str | None = None


# ------------------------------------------------------------------ zoning

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


# ------------------------------------------------------------------ zoning plan (assisted builder)

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


# ------------------------------------------------------------------ provisioning plan + result

ActionKind = Literal["host", "hostset", "volume", "vvset", "vlun"]


class PlannedAction(BaseModel):
    kind: ActionKind
    name: str
    description: str         # human-readable preview line
    exists: bool = False     # idempotency: already present on the array?
    detail: dict = Field(default_factory=dict)


class ProvisioningPlan(BaseModel):
    actions: list[PlannedAction] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    error: str | None = None


class ActionOutcome(BaseModel):
    kind: ActionKind
    name: str
    status: Literal["created", "exists", "failed"]
    detail: str = ""


class ProvisioningResult(BaseModel):
    outcomes: list[ActionOutcome] = Field(default_factory=list)
    error: str | None = None


# ------------------------------------------------------------------ tier-2 path verification (ADR 0010)

PathVerdict = Literal["live", "partial", "no_path"]


class VolumePath(BaseModel):
    """One ACTIVE VLUN path from `showvlun -a`: a volume live to a host over one HBA WWPN + array port."""

    lun: int
    volume: str
    host: str
    host_wwpn: str          # normalized
    port: str               # array port n:s:p
    status: str             # active | nonopt (ALUA active-optimized / non-optimized) | ...


class HostPathStatus(BaseModel):
    """Per host: does the exported LUN actually reach it, and over how many fabrics? Read-only, never
    a gate — a `no_path` host is fine (the export exists and activates once the host is on + zoned)."""

    host: str
    verdict: PathVerdict
    hbas_with_paths: int                                   # distinct host WWPNs carrying a live path
    fabrics: list[str] = Field(default_factory=list)       # fabrics (odd/even) with live paths
    live_volumes: list[str] = Field(default_factory=list)  # target volumes with >=1 active path here
    dead_volumes: list[str] = Field(default_factory=list)  # target volumes exported but with NO path
    detail: str = ""


class PathVerification(BaseModel):
    hosts: list[HostPathStatus] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    error: str | None = None
