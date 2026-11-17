"""Peer-port models (SPEC-025, BL-26): what the array says about its FC ports. No I/O.

A peer port is an FC port in connection mode `peer`: it logs in to the fabric as an initiator so a
data migration (BL-27) can read a source array through it. Only the read side is here so far; the
sheet, plan, apply and verify models come with their work-packet steps.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PeerPortState(BaseModel):
    """One row of `showport` for one port, as the array printed it."""

    nsp: str
    mode: str = ""              # target | initiator | peer
    state: str = ""             # ready | loss_sync | offline | …
    type: str = ""              # host | free | peer | disk | rcip | cluster | … (what is attached now)
    protocol: str = ""          # FC | iSCSI | IP | NVMe | …
    node_wwn: str = ""          # FC only
    port_wwn: str = ""          # FC only: the WWPN the fabric sees
    label: str = ""             # free text; never decides what a port is (LESSONS 42)
    partner: str = ""           # Primera persistent-port partner; the Alletra MP prints no such column
    failover_state: str = ""    # Primera: none | failed_over | active | …

    @property
    def node(self) -> int:
        return int(self.nsp.split(":", 1)[0])

    @property
    def is_fc(self) -> bool:
        return self.protocol.upper() == "FC"


class PortParams(BaseModel):
    """One row of `showport -par`: the connection mode and type the removal set restores."""

    nsp: str
    connmode: str = ""          # host | disk | peer | rcfc | iscsi | …
    conntype: str = ""          # point | loop | eth


class PeerPortView(BaseModel):
    """Everything the peer-port section reads from this run's array, read-only.

    `logins` and `exports` are the one answer to "is anything using this port" for the plan and the
    verify alike (LESSONS 41).
    """

    host: str = ""
    ports: dict[str, PeerPortState] = Field(default_factory=dict)        # `showport`
    params: dict[str, PortParams] = Field(default_factory=dict)          # `showport -par`
    mode_change: dict[str, str] = Field(default_factory=dict)            # `showport -c`: allowed | prohibited
    logins: dict[str, list[str]] = Field(default_factory=dict)           # `showhost -d`, per port
    exports: dict[str, list[str]] = Field(default_factory=dict)          # `showvlun -a`, volumes per port
    peer_listing: list[PeerPortState] = Field(default_factory=list)      # `showport -peer`, for the as-built
    read_error: str = ""
