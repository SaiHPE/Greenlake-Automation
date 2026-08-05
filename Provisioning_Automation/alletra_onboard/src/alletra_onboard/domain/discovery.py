"""Discovery-context models: what a provisioning run READS about the environment at run time —
array target ports, ESXi host HBAs (via vCenter), and the array's curated host view. The input to
zoning and provisioning (ADR 0002).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from alletra_onboard.domain.shared import Fabric


class ArrayPort(BaseModel):
    node: int
    slot: int
    card_port: int
    protocol: str = "fc"    # "fc" | "iscsi"
    wwpn: str = ""          # normalized FC port WWPN ("" for iSCSI)
    address: str = ""       # iSCSI target IP ("" for FC)
    link_state: str         # ready | offline | loss_sync | ...
    # Port role. Only a 'target' port serves hosts; 'initiator'/'peer' ports carry replication or
    # migration traffic and must not be counted as host-facing capacity. The CLI (`showport`) gives
    # this as a word; the WSAPI gives it as an enum the adapter maps back to the same word.
    mode: str = ""          # target | initiator | peer | suspended | "" (unknown)
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
