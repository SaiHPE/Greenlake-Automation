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


# 3PAR / Primera / Alletra MP host persona IDs (see `showhost -listpersona`). We only CREATE hosts we
# discover, and discovery is vCenter/ESXi today, so VMware(11) is the default — but the persona is
# DERIVED from the host OS so a Windows/Linux host gets the right one instead of a hardcoded 11.
PERSONA_NAMES: dict[int, str] = {1: "Generic", 2: "Generic-ALUA", 11: "VMware", 15: "WindowsServer"}


def persona_for_os(os: str | None) -> int:
    """Map a host OS string (e.g. from vCenter) to its array host persona id. Defaults to VMware."""
    s = (os or "").lower()
    if "vmware" in s or "esxi" in s:
        return 11  # VMware
    if "windows" in s:
        return 15  # WindowsServer
    if any(k in s for k in ("linux", "rhel", "red hat", "ubuntu", "suse", "centos", "oracle", "debian")):
        return 2   # Generic-ALUA
    return 11      # default: the tool discovers ESXi hosts today


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
