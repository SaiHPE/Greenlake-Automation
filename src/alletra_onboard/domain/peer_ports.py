"""Peer-port models (SPEC-025, BL-26): what the array says about its FC ports. No I/O.

A peer port is an FC port in connection mode `peer`: it logs in to the fabric as an initiator so a
data migration (BL-27) can read a source array through it. The sheet's rows (`PeerPortIntent`), what
the read found (`PeerPortView`), the plan (`PeerPortPlan`), the judgement of the read after the paste
(`PeerPortResult`) and what Verify says (`PeerPortCheck`).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PeerPortRequest(BaseModel):
    """One row of the workbook's *Peer ports* tab (R1): an FC port of this array to set to peer mode,
    and the source array's port WWPNs to zone to it (normalised, 16 hex digits)."""

    nsp: str
    source_wwpns: list[str] = Field(default_factory=list)

    @property
    def node(self) -> int:
        return int(self.nsp.split(":", 1)[0])


class PeerPortIntent(BaseModel):
    ports: list[PeerPortRequest] = Field(default_factory=list[PeerPortRequest])


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
    # enabled | disabled | "" (n/a). A mode change can reset it: live on rack13-ARCUS (2026-11-17) 1:3:1
    # came back from peer to host with IntCoal `disabled`, read `enabled` before.
    intcoal: str = ""


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
    peer_listing: list[PeerPortState] = Field(default_factory=list[PeerPortState])  # `showport -peer`, for the as-built
    read_error: str = ""


class PeerPortAction(BaseModel):
    """One sheet row judged against the read (R3). `commands` are the lines that set the port (printed
    for a consultant in the first slice); `undo` restores the connection mode `showport -par` read."""

    nsp: str
    state: Literal["create", "exists", "conflict"]
    reason: str = ""
    commands: list[str] = Field(default_factory=list)
    undo: list[str] = Field(default_factory=list)
    # The other port of its card's port pair (ports 1-2, 3-4): a mode change on one can change the other
    # (`help controlport`, port pair protection). "" when the array has no such FC port.
    partner: str = ""


class PeerPortPlan(BaseModel):
    actions: list[PeerPortAction] = Field(default_factory=list[PeerPortAction])
    blockers: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class PeerPortResult(BaseModel):
    """The read after the paste (and later the apply's read-back), judged (R4). `removals` is the undo
    of what changed, last port first (R5); `sentences` say per port what the read shows."""

    changed: list[str] = Field(default_factory=list)
    removals: list[str] = Field(default_factory=list)
    error: str | None = None
    sentences: list[str] = Field(default_factory=list)


class PeerPortCheck(BaseModel):
    """One planned port as Verify reads it (R6). Read-only."""

    nsp: str
    ok: bool
    sentence: str
