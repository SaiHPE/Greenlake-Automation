"""Pure WSAPI v1 response parsers for the Alletra MP B10000 (zero HTTP or SDK I/O).

Separated from `wsapi_client.py` so response parsing and enum mappings can be tested and reused
without importing `hpe3parclient` or opening a transport.
"""

from __future__ import annotations

from alletra_onboard.domain.network import IscsiVlanInterface
from alletra_onboard.domain.peer_ports import PeerPortState, PortParams
from alletra_onboard.domain.provisioning import ArrayHostRecord, VlunTemplate
from alletra_onboard.domain.shared import (
    ArrayProvisioningType,
    ArrayVolumeRecord,
    normalize_wwpn,
)

# WSAPI host-persona ids, resolved by NAME. The values are hpe3parclient's HOST_PERSONA_* constants —
# the array's WSAPI persona enum: VMware=8, WindowsServer=11, Generic-ALUA=2. Verified 2026-07-22 against
# the SDK constants AND a live Alletra MP (GET /hosts reported persona 8 for its VMware ESXi hosts). This
# is the WSAPI enum, NOT the CLI `showhost -listpersona` numbering where VMware=11 — passing the CLI number
# to createHost would create ESXi hosts with the *Windows* persona (11 == WindowsServer here). Resolving by
# name means the two numberings can never be confused again.
_WSAPI_PERSONA: dict[str, int] = {"VMware": 8, "WindowsServer": 11, "Generic-ALUA": 2}

# WSAPI port enums -> the CLI (`showport`) vocabulary that ArrayPort documents. Only values we have
# actually observed are mapped; anything else falls through as its own string rather than being
# guessed at or dropped.
#
# PROVEN by running both interfaces against the same array (4UW0004497, OS 10.5.60.36) and matching
# them port for port: the six ports `showport` calls `target` are exactly the six the WSAPI reports
# as mode=2, the two it calls `initiator` are exactly mode=3, and every port it calls `ready` is
# linkState=4. The IP/peer ports (`peer`, protocol IP) come back as protocol=4/mode=4 and are
# filtered out before this mapping applies.
#
# The rest was matched the same way on rack13-ARCUS (CZ2D2K014S, OS 10.6.0, 2026-11-16): `GET /ports`
# against `showport` and `showport -par`, all 28 ports (tests/fixtures/peer_ports/rack13/). linkState 12
# is the cluster ports' `link_idle_for_reset`; type -1 is `cluster`; connectionType 99 is the iSCSI
# ports' `eth`.
#
# The FC peer port, matched the same way on E18U31 (DHCI_B10K, OS 10.5.60, 2026-11-17,
# tests/fixtures/peer_ports/E18U31/): 0:3:2 and 1:3:2, `initiator` and Type `peer` in `showport`,
# `peer point` in `showport -par`, are mode 3, type 6, connectionMode 4. Type 7 is the `rcip` IP ports
# of D22U27 (OS 10.5.0) and VZ (OS 10.5.51). python-3parclient also names type 5 rcfc and 8 iscsi;
# no capture has shown either, so they stay unmapped.
_PORT_LINK_STATE: dict[object, str] = {4: "ready", 5: "loss_sync", 10: "offline", 12: "link_idle_for_reset"}
_PORT_MODE: dict[object, str] = {1: "suspended", 2: "target", 3: "initiator", 4: "peer"}
_PORT_TYPE: dict[object, str] = {1: "host", 2: "disk", 3: "free", 6: "peer", 7: "rcip", -1: "cluster"}
_PORT_PROTOCOL: dict[object, str] = {1: "FC", 2: "iSCSI", 4: "IP", 6: "NVMe"}
_PORT_CONN_MODE: dict[object, str] = {1: "disk", 2: "host", 4: "peer"}
_PORT_CONN_TYPE: dict[object, str] = {2: "point", 99: "eth"}

# WSAPI persona id -> name (the inverse of _WSAPI_PERSONA) for reading hosts back.
_PERSONA_NAME: dict[int, str] = {v: k for k, v in _WSAPI_PERSONA.items()}

# WSAPI volume `provisioningType` enum. 6 (TDVV) is what a `{"reduce": True}` create reads back as on
# the Alletra MP (observed live, see ensure_volume) — so 6 IS "reduce" in this tool's vocabulary.
_PROVISIONING_TYPE: dict[object, ArrayProvisioningType] = {
    1: "full", 2: "tpvv", 3: "snp", 4: "peer", 5: "unknown", 6: "reduce", 7: "dds",
}


def _members(body) -> list[dict]:
    """python-3parclient get* returns {'total':N,'members':[...]} (or sometimes a bare list)."""
    if isinstance(body, dict):
        return body.get("members", []) or []
    if isinstance(body, list):
        return body
    return []


def _word(table: dict[object, str], value: object) -> str:
    return table.get(value, "" if value is None else str(value))


def _iscsi_names(host: dict) -> list[str]:
    out: list[str] = []
    for p in host.get("iSCSIPaths") or []:
        iqn = str(p.get("name", "")).strip()
        if iqn and iqn.lower() not in {i.lower() for i in out}:
            out.append(iqn)
    return out


def _names(body: object) -> list[str]:
    return [m.get("name", "") for m in _members(body)]


def parse_hosts(body: object) -> list[ArrayHostRecord]:
    """getHosts -> records. Persona by name (unknown ids pass through as their number); FC WWNs
    de-duplicated — `FCPaths` carries one entry per (WWN, array port), so a dual-fabric HBA appears
    twice (rack13arcus capture, 2026-09-13). iSCSI names come from `iSCSIPaths[].name`, de-duplicated
    case-insensitively (rack13arcus 2026-09-13, D22U27 2026-10-26)."""
    out: list[ArrayHostRecord] = []
    for m in _members(body):
        name = m.get("name", "")
        if not name:
            continue
        persona_id = m.get("persona")
        wwns: list[str] = []
        for p in m.get("FCPaths") or []:
            w = normalize_wwpn(str(p.get("wwn", "")))
            if len(w) == 16 and w not in wwns:
                wwns.append(w)
        persona = (
            _PERSONA_NAME.get(persona_id, str(persona_id))
            if isinstance(persona_id, int)
            else (str(persona_id) if persona_id is not None else "")
        )
        out.append(ArrayHostRecord(
            name=name,
            persona=persona,
            wwns=wwns,
            iqns=_iscsi_names(m),
            id=int(m["id"]) if str(m.get("id", "")).isdigit() else None,
        ))
    return out


def parse_port_states(body: object) -> tuple[dict[str, PeerPortState], dict[str, PortParams]]:
    """getPorts -> ({n:s:p: state}, {n:s:p: params}) in the words `showport` and `showport -par`
    print, so a WSAPI read and a CLI read of one array compare equal (rack13-ARCUS, 2026-11-16). An
    unknown enum value passes through as its number. WWNs are kept for FC ports only: for an NVMe
    port the WSAPI puts its IP address in `nodeWWN`. A port without `connectionMode` (the IP ports)
    has no params, as `showport -par` lists none for it. On OS 10.5 (E18U31, D22U27, 2026-11-17)
    `GET /ports` leaves out the IP ports of Type `free` and `file`, so it is not a full port list there;
    OS 10.6.0 (rack13) lists every port."""
    states: dict[str, PeerPortState] = {}
    params: dict[str, PortParams] = {}
    for m in _members(body):
        pos = m.get("portPos") or {}
        if not pos:
            continue
        nsp = f"{pos.get('node')}:{pos.get('slot')}:{pos.get('cardPort')}"
        protocol = _word(_PORT_PROTOCOL, m.get("protocol"))
        fc = protocol == "FC"
        states[nsp] = PeerPortState(
            nsp=nsp,
            mode=_word(_PORT_MODE, m.get("mode")),
            state=_word(_PORT_LINK_STATE, m.get("linkState")),
            type=_word(_PORT_TYPE, m.get("type")),
            protocol=protocol,
            node_wwn=normalize_wwpn(str(m.get("nodeWWN") or "")) if fc else "",
            port_wwn=normalize_wwpn(str(m.get("portWWN") or "")) if fc else "",
            label=str(m.get("label") or ""),
        )
        if m.get("connectionMode") is not None:
            params[nsp] = PortParams(nsp=nsp, connmode=_word(_PORT_CONN_MODE, m.get("connectionMode")),
                                     conntype=_word(_PORT_CONN_TYPE, m.get("connectionType")))
    return states, params


def parse_volumes(body: object) -> list[ArrayVolumeRecord]:
    out: list[ArrayVolumeRecord] = []
    for m in _members(body):
        name = m.get("name", "")
        if not name:
            continue
        out.append(ArrayVolumeRecord(
            name=name,
            size_mib=int(m.get("sizeMiB") or 0),
            cpg=str(m.get("userCPG") or ""),
            provisioning_type=_PROVISIONING_TYPE.get(m.get("provisioningType"), "unknown"),
            id=int(m["id"]) if str(m.get("id", "")).isdigit() else None,
            wwn=str(m.get("wwn") or "").upper(),
            copy_of=str(m.get("copyOf") or ""),
            read_only=bool(m.get("readOnly")),
            created=str(m.get("creationTime8601") or ""),
            expires=str(m.get("expirationTime8601") or ""),
        ))
    return out


def parse_sets(body: object) -> dict[str, list[str]]:
    """getHostSets / getVolumeSets -> {name: members}. A set with no `setmembers` is present and empty."""
    return {m["name"]: list(m.get("setmembers") or []) for m in _members(body) if m.get("name")}


def parse_vlun_templates(body: object) -> list[VlunTemplate]:
    """getVLUNs -> the presentation templates: (volume, target, lun), target exactly as the array
    names it (`set:<hostset>` for a host-set export, a bare host name otherwise).

    PINNED to the rack13arcus capture (tests/fixtures/rack13_wsapi/vluns.json, 2026-09-13): the
    array returns two kinds of record. Templates have `active: false` and carry the target as
    written (`hostname: "set:zz_t2_hs"`, `type: 5`). Active paths have `active: true` and carry the
    MEMBER host (`hostname: "10.132.30.136"`, still `type: 5`) plus `remoteName` / `portPos`. So a
    template is an inactive record taken as-is — never "type 5 ⇒ prefix set:", which the first
    draft did from the documentation and which would have invented `set:10.132.30.136` from every
    active path. Records with no `active` field (unknown firmware) are kept, de-duplicated."""
    seen: dict[tuple[str, str, int], VlunTemplate] = {}
    for m in _members(body):
        if m.get("active") is True:
            continue
        volume, target, lun = m.get("volumeName"), m.get("hostname"), m.get("lun")
        if not volume or not target or lun is None:
            continue
        key = (str(volume), str(target), int(lun))
        if key not in seen:
            seen[key] = VlunTemplate(volume=key[0], target=key[1], lun=key[2])
    return list(seen.values())


def parse_iscsi_vlans_wsapi(nsp: str, body: object) -> list[IscsiVlanInterface]:
    """`GET /ports/<n:s:p>/iSCSIVlans/` -> the port's VLAN-tagged addresses.

    PINNED to tests/fixtures/iscsi_vlan/: the answer is `{"iSCSIVlans": [...], "total": N, "links":
    [...]}`, not the `members` envelope of the other collections, so `_members` would read every
    answer as empty. Whether the untagged address is in the list depends on the OS: rack13-ARCUS
    (OS 10.6.0, 2026-11-16) left it out, E18U31 (OS 10.5.60, 2026-11-17) lists it as a record with
    `vlanTag` 0. Tag 0 is the port's base address, not a VLAN interface, so it is left out here as
    `parse_iscsi_vlans` leaves out the CLI's `untagged` row.

    The field names are those of E18U31's real untagged records (`IPAddr`, `netmask`, `gateway`,
    `vlanTag`, `mtu`, `stgt`, `tpgt`, `iSNSAddr`, `iSNSPort`); no tagged record is captured yet. A
    record without `vlanTag`, `IPAddr` or `netmask`, or with a tag outside 0 to 4094, is refused
    rather than read as blanks (LESSONS 28)."""
    if not isinstance(body, dict) or "iSCSIVlans" not in body:
        raise ValueError(f"WSAPI iSCSIVlans answer for {nsp} has no iSCSIVlans list: {str(body)[:200]}")
    out: list[IscsiVlanInterface] = []
    for rec in body["iSCSIVlans"] or []:
        missing = [k for k in ("vlanTag", "IPAddr", "netmask") if not isinstance(rec, dict) or k not in rec]
        if missing:
            raise ValueError(f"WSAPI iSCSIVlans record for {nsp} has no {', '.join(missing)}: {str(rec)[:200]}")
        tag = str(rec["vlanTag"])
        if not (tag.isdigit() and int(tag) <= 4094):
            raise ValueError(f"WSAPI iSCSIVlans record for {nsp} has vlanTag {tag}, "
                             "neither a tag from 1 to 4094 nor 0 (untagged)")
        if int(tag) == 0:
            continue
        gateway = str(rec.get("gateway") or "")
        out.append(IscsiVlanInterface(
            nsp=nsp, vlan_id=int(tag), ip=str(rec["IPAddr"]), netmask=str(rec["netmask"]),
            gateway="" if gateway == "0.0.0.0" else gateway, mtu=str(rec.get("mtu") or ""),
        ))
    return out
