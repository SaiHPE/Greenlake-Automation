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
    # `showport` Type — the ROLE the array itself assigns: host | free | disk | cluster | file | rcip.
    # This is machine state and is the only trustworthy classifier. Measured across three arrays.
    port_type: str = ""
    # `showport` Label — FREE TEXT an operator typed, never an enum. On AlletraMP_D22U27 three
    # host-serving FC ports carry "peer port", "peer 1:3:1" and "Peer_port": three spellings of the
    # same idea on one array, on ports whose Type is `host`. Display only; never classify on it.
    usage: str = ""

    @property
    def label(self) -> str:
        return f"{self.node}:{self.slot}:{self.card_port}"

    @property
    def identifier(self) -> str:
        """WWPN for FC, target IP for iSCSI — the port's addressable id for display."""
        return self.wwpn if self.protocol == "fc" else self.address


class EthernetPort(BaseModel):
    """A non-host-facing ethernet data port: FILE services or RCIP replication.

    Kept apart from ArrayPort on purpose. `array_ports` means "ports that can serve a host", and
    everything downstream (zoning candidates, fabric resolution, path verification) assumes that.
    Mixing replication and file ports into that list would put them in the zoning dropdowns, which is
    the one hazard the port filters have always existed to prevent.

    `role` is the array's own `showport` Type: "file" or "rcip". A slot-4 port that is capable but
    not yet configured reports Type `free`, and is listed here as available rather than omitted —
    "0:4:4 is an unconfigured RCIP port" is the planning answer, and Type alone cannot give it.
    """

    node: int
    slot: int
    card_port: int
    role: str                    # file | rcip | free (capable, not yet configured)
    mode: str = ""               # target (file) | peer (rcip)
    link_state: str = ""         # ready | offline | loss_sync | ...
    address: str = ""            # IPv4 ("" when unconfigured)
    prefix_len: str = ""         # from showport -file "IPAddr/PrefixLen"
    netmask: str = ""            # from showport -rcip, which gives a dotted mask not a prefix
    ip_disabled: bool = False
    gateway: str = ""            # "-" in the CLI means unset, normalised to ""
    vlan: str = ""               # "untagged" or a tag id (file only)
    mtu: str = ""
    rate: str = ""               # "n/a" on a down link
    eth: str = ""                # eth6 / eth7 / eth8 (file only)
    link: str = ""               # up | down (file only)
    duplex: str = ""             # rcip only
    autoneg: str = ""            # rcip only
    failover_ips: list[str] = Field(default_factory=list)

    @property
    def label(self) -> str:
        return f"{self.node}:{self.slot}:{self.card_port}"


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
    # Host-facing target ports only (FC + iSCSI). Everything downstream treats this as "ports that
    # can serve a host", so replication and file ports are deliberately NOT in here.
    array_ports: list[ArrayPort] = Field(default_factory=list)
    replication_ports: list[EthernetPort] = Field(default_factory=list)  # RCIP (showport / -rcip)
    file_ports: list[EthernetPort] = Field(default_factory=list)         # file services (showport -file)
    host_hbas: list[HostHba] = Field(default_factory=list)
    array_hosts: list[ArrayHost] = Field(default_factory=list)  # from showhost -d (zoning source)
    notes: list[str] = Field(default_factory=list)
    error: str | None = None
