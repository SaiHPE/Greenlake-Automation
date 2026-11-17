"""iSCSI network models (SPEC-024): the addresses on the array's iSCSI ports. No I/O.

The read side only, for now: one row of `showport -iscsi` and one VLAN-tagged interface of
`showport -iscsivlans` (or of WSAPI `GET /ports/<n:s:p>/iSCSIVlans/`). The sheet, view, plan and
outcome models of SPEC-024 §4 come with the steps that use them (docs/workpackets/BL-25.md).
"""

from __future__ import annotations

from pydantic import BaseModel


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
    the parsers leave it out."""

    nsp: str
    vlan_id: int
    ip: str
    netmask: str
    gateway: str = ""
    mtu: str = ""
