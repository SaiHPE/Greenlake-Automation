"""Provisioning-context models: the intent (what the customer wants created), the Stage-2 builder
palette/composition, the tier-1 plan + result, and tier-2 path verification (ADR 0010).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from alletra_onboard.domain.shared import EndpointCreds

ProvisioningType = Literal["tpvv", "reduce"]

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

class VolumeRequest(BaseModel):
    """One volume to create — its OWN name, size, provisioning type, CPG, and optional VV-set membership.
    Heterogeneous by design: a run creates a LIST of these, not N identical copies (ADR 0010)."""

    name: str
    size_gib: int
    provisioning_type: ProvisioningType = "tpvv"
    cpg: str = "SSD_r6"
    vvset: str | None = None       # optional VV-set to add this volume to

    @property
    def size_mib(self) -> int:
        return self.size_gib * 1024


class HostSetRequest(BaseModel):
    """A host set to create + its SELECTED members (host names). Empty members => all discovered hosts
    (the cluster). A run may create one or more host sets (ADR 0010)."""

    name: str
    members: list[str] = Field(default_factory=list)


ExportSourceKind = Literal["volume", "vvset"]
ExportTargetKind = Literal["host", "hostset"]


class ExportRequest(BaseModel):
    """One presentation (VLUN): a source (a volume or a VV-set) exported to a target (a host or a
    host-set) at an explicit LUN, or auto-assigned. Composed by the operator's dropdown builder over
    discovered + to-be-created objects (ADR 0010). When a run supplies NO exports, provisioning falls
    back to the Stage-1 default (every volume -> every host set, auto LUN)."""

    source_kind: ExportSourceKind
    source_name: str
    target_kind: ExportTargetKind
    target_name: str
    lun: int | None = None          # None = let the array auto-assign

    @property
    def source_ref(self) -> str:
        """The WSAPI volumeName token: a bare volume name, or 'set:<vvset>' for a VV-set."""
        return self.source_name if self.source_kind == "volume" else f"set:{self.source_name}"

    @property
    def target_ref(self) -> str:
        """The WSAPI hostname token: a bare host name, or 'set:<hostset>' for a host-set."""
        return self.target_name if self.target_kind == "host" else f"set:{self.target_name}"


class ProvisioningIntent(BaseModel):
    """What drives a provisioning run: reach (creds) + a plural/heterogeneous set of objects to create —
    many volumes (each with its own attributes), one or more host sets with selected members, and the
    presentations (exports) that wire them together. See ADR 0010."""

    array: EndpointCreds          # mgmt IP + admin (e.g. 3paradm) + password
    vcenter: EndpointCreds        # vCenter for read-only ESXi HBA discovery
    switch_f1: EndpointCreds      # odd fabric (F1)
    switch_f2: EndpointCreds      # even fabric (F2)
    volumes: list[VolumeRequest] = Field(default_factory=list)
    host_sets: list[HostSetRequest] = Field(default_factory=list)
    exports: list[ExportRequest] = Field(default_factory=list)  # empty => default each-volume->each-host-set

    @classmethod
    def from_simple(
        cls,
        *,
        array: EndpointCreds,
        vcenter: EndpointCreds,
        switch_f1: EndpointCreds,
        switch_f2: EndpointCreds,
        host_set_name: str,
        name_prefix: str,
        size_gib: int,
        count: int = 1,
        provisioning_type: ProvisioningType = "tpvv",
        cpg: str = "SSD_r6",
        vvset: str | None = None,
    ) -> "ProvisioningIntent":
        """Bulk shortcut: expand <prefix>NN + count into N identical volumes in one all-members host set —
        the current flat-sheet case. The row-table sheet (Stage 2) will build the plural form directly."""
        if count <= 1:
            names = [name_prefix]
        else:
            width = max(2, len(str(count)))
            names = [f"{name_prefix}{i:0{width}d}" for i in range(1, count + 1)]
        return cls(
            array=array, vcenter=vcenter, switch_f1=switch_f1, switch_f2=switch_f2,
            volumes=[
                VolumeRequest(name=n, size_gib=size_gib, provisioning_type=provisioning_type, cpg=cpg, vvset=vvset)
                for n in names
            ],
            host_sets=[HostSetRequest(name=host_set_name, members=[])],
        )


# ------------------------------------------------------------------ provisioning builder (ADR 0010 Stage 2)

class DiscoveredHostBrief(BaseModel):
    """A discovered ESXi host offered in the host-set membership dropdown, with a short fabric-login
    status so a half-zoned host isn't picked blind (ADR 0010)."""

    name: str
    status: str                                       # e.g. "2 HBAs - both fabrics" / "not logged in"
    wwpns: list[str] = Field(default_factory=list)     # normalized


class ProvisioningObjects(BaseModel):
    """The dropdown 'palette': objects already on the array (read over WSAPI) + the ones this run will
    create (from the sheet intent) + discovered hosts, plus the host sets / exports already composed so
    the builder can resume. `array_error` is set (and the existing_* lists empty) if the array read
    failed — the palette is still usable with the to-be-created + discovered objects."""

    existing_cpgs: list[str] = Field(default_factory=list)
    existing_hosts: list[str] = Field(default_factory=list)
    existing_host_sets: list[str] = Field(default_factory=list)
    existing_volumes: list[str] = Field(default_factory=list)
    existing_volume_sets: list[str] = Field(default_factory=list)
    array_error: str | None = None
    new_volumes: list[str] = Field(default_factory=list)
    new_host_sets: list[str] = Field(default_factory=list)
    new_vvsets: list[str] = Field(default_factory=list)
    discovered_hosts: list[DiscoveredHostBrief] = Field(default_factory=list)
    host_sets: list[HostSetRequest] = Field(default_factory=list)   # currently composed
    exports: list[ExportRequest] = Field(default_factory=list)      # currently composed


class ProvisioningBuilder(BaseModel):
    """What the operator composed in the dropdown builder — host-set membership, VV-set membership
    (vvset name -> member volume names), and the exports. Saved onto the run's ProvisioningIntent.
    When `vvsets` is non-empty it is authoritative (a volume not listed in any set is un-set)."""

    host_sets: list[HostSetRequest] = Field(default_factory=list)
    exports: list[ExportRequest] = Field(default_factory=list)
    vvsets: dict[str, list[str]] = Field(default_factory=dict)


class ProvisioningComposition(BaseModel):
    """Echo of the composed relationships after saving them onto the intent (for the UI to confirm)."""

    host_sets: list[HostSetRequest] = Field(default_factory=list)
    exports: list[ExportRequest] = Field(default_factory=list)
    volumes: list[VolumeRequest] = Field(default_factory=list)


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
