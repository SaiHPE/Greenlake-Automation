"""Discovery-context models: what a provisioning run READS about the environment at run time —
array target ports, ESXi host HBAs (via vCenter), and the array's curated host view. The input to
zoning and provisioning (ADR 0002).
"""

from __future__ import annotations

from typing import Literal

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


#: The OS buckets the host tables group by. "unknown" is a real answer, not a failure: an FC host
#: whose HBA registers no OS string, or an iSCSI host with an unrecognised IQN prefix, genuinely
#: cannot be classified from the wire and must not be guessed into a bucket.
HostOs = Literal["esxi", "windows", "linux", "vme", "unknown"]

#: iSCSI naming authorities, from the IQN's reversed-domain part. This is the ONLY OS signal
#: available for an iSCSI host: the array reports no OS, and an iSCSI initiator never performs an FC
#: login so the switch name server cannot see it either. Measured on rack13arcus:
#:   iqn.1991-05.com.microsoft:win-tn3n7rujk3v   -> Windows (hostname embedded)
#:   iqn.2024-12.com.hpe:hvm3:50796              -> HPE VME, node hvm3
_IQN_OS: tuple[tuple[str, HostOs], ...] = (
    ("com.microsoft", "windows"),
    ("com.vmware", "esxi"),
    ("com.hpe", "vme"),
    ("org.open-iscsi", "linux"),
    ("com.redhat", "linux"),
    ("com.oracle", "linux"),
    ("org.debian", "linux"),
    ("com.suse", "linux"),
    ("com.ubuntu", "linux"),
)


def os_from_iqn(iqn: str) -> HostOs:
    """The OS an IQN's naming authority implies, or 'unknown'.

    A convention, not a guarantee — an administrator may set any initiator name they like. It is
    used to GROUP hosts for display, never to choose a persona or gate an action.
    """
    low = (iqn or "").lower()
    for authority, os_name in _IQN_OS:
        if authority in low:
            return os_name
    return "unknown"


def os_from_switch_string(os_text: str) -> HostOs:
    """The OS a fabric name-server `OS:` string implies. FC only — an iSCSI host is never here."""
    low = (os_text or "").lower()
    if "vmware" in low or "esx" in low:
        return "esxi"
    if "windows" in low or "microsoft" in low:
        return "windows"
    if any(k in low for k in ("linux", "rhel", "red hat", "suse", "ubuntu", "debian", "centos")):
        return "linux"
    return "unknown"


def node_name_from_iqn(iqn: str) -> str:
    """The host part an IQN carries after its colon, when it has one.

    Worth extracting because the array's own name for an iSCSI host can be useless: HPE VME hosts
    register as `HPE_VM_07dc508b8e41df1fcf6ab266` on the array while their IQN says
    `iqn.2024-12.com.hpe:hvm3:50796` — `hvm3` is the node an operator would recognise. Likewise
    `iqn.1991-05.com.microsoft:win-tn3n7rujk3v` carries the Windows machine name.
    """
    _, _, tail = (iqn or "").partition(":")
    return tail.split(":")[0] if tail else ""


class DiscoveredHost(BaseModel):
    """One physical server, assembled from every source that can see it.

    The join key is always an initiator id (WWPN or IQN), never a name: the same server is called
    different things by vCenter, by the fabric name server, by the array's host object and by the
    sheet, and those namespaces do not intersect (measured across three arrays — an exact-name join
    reported no_path for every pre-existing host).

    A host may hold both transports. HPE does not support exporting the same volume over both, so
    the two are kept as separate lists rather than merged into one 'initiators' field.
    """

    name: str
    os: HostOs = "unknown"
    address: str = ""                  # management/iSCSI IP where a source reports one
    wwpns: list[str] = Field(default_factory=list)      # FC, normalized
    iqns: list[str] = Field(default_factory=list)       # iSCSI
    fabrics: list[str] = Field(default_factory=list)    # fabrics its WWPNs are logged into
    logged_in: bool = False            # the array can currently see at least one of its initiators
    array_host_name: str = ""          # what the array's own host object calls it ("" = unclaimed)
    sources: list[str] = Field(default_factory=list)    # vcenter | array | switch | sheet

    @property
    def transports(self) -> list[str]:
        return [t for t, present in (("fc", bool(self.wwpns)), ("iscsi", bool(self.iqns))) if present]


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
    # iSCSI initiators the array sees for this host, IQN -> [n:s:p]. Same shape as `wwpns` but a
    # different cardinality underneath: a host has one IQN presented over many sessions, where it has
    # one WWPN per HBA port. Kept separate because an IQN cannot be zoned and must never reach the
    # fabric lookup.
    iqns: dict[str, list[str]] = Field(default_factory=dict)
    # IQN -> the initiator's IP. PER INITIATOR, not per host: `showhost` files every unclaimed login
    # under one nameless row, so a single ArrayHost can carry initiators belonging to several
    # different machines. A single `address` field gave the first one's IP to all of them.
    addresses: dict[str, str] = Field(default_factory=dict)


class DiscoveryReport(BaseModel):
    # Host-facing target ports only (FC + iSCSI). Everything downstream treats this as "ports that
    # can serve a host", so replication and file ports are deliberately NOT in here.
    array_ports: list[ArrayPort] = Field(default_factory=list)
    replication_ports: list[EthernetPort] = Field(default_factory=list)  # RCIP (showport / -rcip)
    file_ports: list[EthernetPort] = Field(default_factory=list)         # file services (showport -file)
    host_hbas: list[HostHba] = Field(default_factory=list)
    array_hosts: list[ArrayHost] = Field(default_factory=list)  # from showhost -d (zoning source)
    # Every server any source can see, joined on initiator id and grouped by OS for display.
    hosts: list[DiscoveredHost] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    error: str | None = None
