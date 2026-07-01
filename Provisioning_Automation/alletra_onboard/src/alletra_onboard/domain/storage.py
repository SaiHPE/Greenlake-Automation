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
    wwpn: str               # normalized
    link_state: str
    fabric: Fabric          # by port parity: card_port odd -> odd fabric, even -> even fabric

    @property
    def label(self) -> str:
        return f"{self.node}:{self.slot}:{self.card_port}"


class HostHba(BaseModel):
    host_name: str
    wwpn: str               # normalized
    model: str | None = None
    os: str | None = None
    fabric: Fabric | None = None  # set from which switch nameserver the WWPN logs into


class NameserverEntry(BaseModel):
    """Who is logged into the fabric, from `nsshow` / array `showportdev ns` — the live truth."""

    fabric: Fabric
    switch_host: str
    wwpn: str               # normalized — a logged-in initiator/target WWPN
    is_array_port: bool = False


class DiscoveryReport(BaseModel):
    array_ports: list[ArrayPort] = Field(default_factory=list)
    host_hbas: list[HostHba] = Field(default_factory=list)
    nameserver: list[NameserverEntry] = Field(default_factory=list)
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
