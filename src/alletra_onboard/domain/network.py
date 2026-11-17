"""iSCSI network models (SPEC-024 §4): VLAN-tagged addresses on the array's iSCSI ports. No I/O.

The sheet's rows (`IscsiVlanRequest`), what the read found on one array (`PortNetworkView`: each
port's role, untagged address and VLAN interfaces), the plan (`IscsiNetworkPlan`), what an apply
did (`IscsiVlanOutcome`, the later slice of ADR 0017) and what Verify compares (`IscsiVlanCheck`).
A port's role comes from `PortRole` only (SPEC-021's `parse_showport_roles`), shared with SPEC-025.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from alletra_onboard.domain.replication import PortRole


class IscsiVlanRequest(BaseModel):
    """One row of the workbook's *iSCSI network* tab (R1): one VLAN interface on one iSCSI port."""

    nsp: str
    vlan_id: int
    ip: str
    netmask: str
    gateway: str = ""


class IscsiPortAddress(BaseModel):
    """One row of `showport -iscsi`: the port's untagged (base) address. "" when the port has none."""

    nsp: str
    ip: str = ""
    netmask: str = ""
    gateway: str = ""
    peer_enabled: bool = False
    # The VLANs (or, on older output, VLAN) column exactly as printed. On rack13-ARCUS (OS 10.6.0)
    # and E18U31 (OS 10.5.0 and 10.5.60) it is 1 on a port with an address and 0 on one without
    # (VZ, OS 10.5.51), matching the rows `showport -iscsivlans` lists for the port; a capture with a
    # tagged interface will say whether it counts tagged ones. The older layout prints Y. Display
    # only; never plan on it.
    vlans: str = ""


class IscsiVlanInterface(BaseModel):
    """A VLAN-tagged address on an iSCSI port. The untagged address is not one: it is the port's
    `IscsiPortAddress`. The CLI lists it as VLAN `untagged` and WSAPI, on OS 10.5.60, as `vlanTag` 0;
    the parsers leave it out. No `state`: `showport -iscsivlans` has no State column (R7 takes it
    from `showport`)."""

    nsp: str
    vlan_id: int
    ip: str
    netmask: str
    gateway: str = ""
    mtu: str = ""


class PortNetworkView(BaseModel):
    """What the read (R2) found on ONE array, read-only."""

    name: str = ""
    mgmt_ip: str = ""
    mgmt_netmask: str = ""
    roles: dict[str, PortRole] = Field(default_factory=dict)
    iscsi_ports: list[IscsiPortAddress] = Field(default_factory=list)
    vlans: list[IscsiVlanInterface] = Field(default_factory=list)
    # Addresses the array already uses elsewhere: address -> "RCIP port 0:4:3" / "file port 0:4:1".
    other_addresses: dict[str, str] = Field(default_factory=dict)


class IscsiVlanAction(BaseModel):
    """One sheet row, judged against the read (R3)."""

    nsp: str
    vlan_id: int
    state: Literal["create", "exists", "conflict"]
    reason: str = ""
    # The array's own lines, each with -vlan: the addr line, then the gw line when the row has one.
    cli: str = ""


class IscsiNetworkPlan(BaseModel):
    array: str = ""
    actions: list[IscsiVlanAction] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    # One sentence per port for the network team (R3). Never a switch command.
    switch_handoff: list[str] = Field(default_factory=list)


class IscsiVlanOutcome(BaseModel):
    """What an apply did for one create (R4, the later slice). `failed`: sent, then refused or not
    seen in the read-back; its removal line stays (R5)."""

    nsp: str
    vlan_id: int
    status: Literal["created", "exists", "failed"]
    detail: str = ""


class IscsiVlanCheck(BaseModel):
    """One sheet row compared with `showport -iscsivlans` by the Verify step (R6). Read-only."""

    nsp: str
    vlan_id: int
    status: Literal["present", "missing", "different"]
    # For `different`: one "field: array value, sheet value" entry per field that differs.
    differences: list[str] = Field(default_factory=list)
