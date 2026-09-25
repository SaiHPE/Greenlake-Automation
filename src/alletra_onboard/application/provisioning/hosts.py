"""The provisioning host union (SPEC-003): every host the run can name, from every source that can
name one, in trust order — vCenter, the sheet's Hosts tab, the array's own host objects, the fabric
name servers as the zoning plan recorded them.

The zoning step has carried this union inline since rc.6 (`zoning_plan.build_zoning_plan`); until
SPEC-003 the provisioning step still read vCenter alone, so a Windows host declared on the sheet or
a Linux host seen only on the fabric could be zoned but never put in a host set or given an export.
"""

from __future__ import annotations

from collections import OrderedDict

from alletra_onboard.domain.discovery import DiscoveryReport, node_name_from_iqn
from alletra_onboard.domain.provisioning import DeclaredHost, ProvisionableHost, persona_for_os
from alletra_onboard.domain.shared import normalize_wwpn

# The array files every login with no host object under one nameless row (discovery.UNCLAIMED_HOST).
_NAMELESS = ""


def _short(name: str) -> str:
    return (name or "").strip().lower().split(".")[0]


def resolve_declared_hosts(
    declared_hosts: list[DeclaredHost] | None, discovery: DiscoveryReport,
) -> tuple[list[DeclaredHost], dict[str, str]]:
    """SPEC-014 R1: fill in the initiators of a sheet host typed with a name (and IP) but no WWPN/IQN.

    Looked up, in order: the server's own read over its sheet login (SPEC-014 R4); the vCenter host
    of that name or IP; the array host object of that name; an array iSCSI login from that IP; an IQN
    whose node name is the host's short name. Returns (hosts with ids filled where found, name -> how
    it was found or why not). Rows that carried ids are returned unchanged and have no entry."""
    by_vcenter: dict[str, list[str]] = {}
    for hba in discovery.host_hbas:
        by_vcenter.setdefault(hba.host_name, []).append(normalize_wwpn(hba.wwpn))
    vcenter_iqns = {i.host_name: i.iqns for i in discovery.host_identities}
    reads = {r.host_name: r for r in discovery.host_reads if not r.error}
    out: list[DeclaredHost] = []
    how: dict[str, str] = {}
    for d in declared_hosts or []:
        if d.wwpns or d.iqn:
            out.append(d)
            continue
        read = reads.get(d.name)
        if read and (read.wwpns or read.iqns):
            out.append(d.model_copy(update={"wwpns": list(read.wwpns), "iqn": read.iqns[0] if read.iqns else ""}))
            how[d.name] = f"read from the server over {read.method.upper()} ({read.address})"
            continue
        keys = {k for k in (d.name.strip().lower(), d.address.strip().lower()) if k}
        found = next((n for n in {*by_vcenter, *vcenter_iqns} if n.lower() in keys), None)
        if found:
            iqns = vcenter_iqns.get(found, [])
            out.append(d.model_copy(update={"wwpns": by_vcenter.get(found, []), "iqn": iqns[0] if iqns else ""}))
            how[d.name] = f"found in vCenter as {found}"
            continue
        ah = next((a for a in discovery.array_hosts if a.name and a.name.lower() == d.name.strip().lower()), None)
        if ah and (ah.wwpns or ah.iqns):
            out.append(d.model_copy(update={"wwpns": list(ah.wwpns), "iqn": next(iter(ah.iqns), "")}))
            how[d.name] = f"found on the array as host {ah.name}"
            continue
        by_ip = next(
            (iqn for a in discovery.array_hosts for iqn, ip in a.addresses.items() if d.address and ip == d.address.strip()),
            None,
        )
        if by_ip:
            out.append(d.model_copy(update={"iqn": by_ip}))
            how[d.name] = f"found on the array: iSCSI login from {d.address}"
            continue
        by_node = next(
            (iqn for a in discovery.array_hosts for iqn in a.iqns if _short(node_name_from_iqn(iqn)) == _short(d.name)),
            None,
        )
        if by_node:
            out.append(d.model_copy(update={"iqn": by_node}))
            how[d.name] = f"found on the array: IQN names node {node_name_from_iqn(by_node)}"
            continue
        out.append(d)
        # A vCenter that timed out was never asked, so "not in vCenter" would be a false statement.
        vcenter_read = not any(n.startswith("vCenter discovery failed") for n in discovery.notes)
        how[d.name] = (
            ("not found — not in vCenter" if vcenter_read else "not found — vCenter was not reached, so it could not be checked")
            + ", no array host of that name"
            + (f", no iSCSI login from {d.address}" if d.address else "")
            + "; add its WWPN/IQN on the Hosts tab"
        )
    return out, how


def declared_mismatches(declared_hosts: list[DeclaredHost] | None, discovery: DiscoveryReport) -> list[str]:
    """SPEC-014 R6: a WWPN/IQN typed on the sheet that the server's own read does not report — a
    plan blocker, because a mistyped initiator zones and presents to nothing."""
    reads = {r.host_name: r for r in discovery.host_reads if not r.error}
    out: list[str] = []
    for d in declared_hosts or []:
        read = reads.get(d.name)
        if read is None:
            continue
        missing = [w for w in (normalize_wwpn(x) for x in d.wwpns) if w not in read.wwpns]
        if missing:
            out.append(
                f"Host '{d.name}': sheet WWPN(s) {', '.join(missing)} not on the server — {read.address} reports "
                + (", ".join(read.wwpns) if read.wwpns else "no FC HBA")
                + ". Fix the Hosts tab."
            )
        if d.iqn and read.iqns and d.iqn not in read.iqns:
            out.append(
                f"Host '{d.name}': sheet IQN {d.iqn} is not the server's — {read.address} reports "
                f"{', '.join(read.iqns)}. Fix the Hosts tab."
            )
    return out


def union_hosts(
    discovery: DiscoveryReport,
    declared_hosts: list[DeclaredHost] | None,
    zoning_plan: dict | None = None,
) -> tuple[OrderedDict[str, ProvisionableHost], list[str]]:
    """(hosts by name, in first-seen order; notes). The first source to name an initiator owns it —
    a later source only adds initiators to a host it also names, or fills a blank OS. An initiator
    already owned by a different name is never re-claimed: the array is the arbiter of ownership and
    `ensure_host` refuses a WWN that belongs to another host. Nameless initiators (array unclaimed
    logins, fabric devices with no name) are counted for one note and offered nowhere."""
    hosts: OrderedDict[str, ProvisionableHost] = OrderedDict()
    owner: dict[str, str] = {}           # initiator (wwpn or iqn) -> host name
    attempted: dict[str, set[str]] = {}  # host name -> every initiator a source gave it
    nameless = 0

    def claim(name: str, source: str, *, wwpns=(), iqns=(), os_: str = "", persona: str | None = None) -> None:
        nonlocal nameless
        if not name:
            nameless += sum(1 for w in wwpns if w not in owner) + sum(1 for i in iqns if i not in owner)
            return
        host = hosts.get(name)
        if host is None:
            host = ProvisionableHost(name=name, source=source, os=os_, persona=persona or persona_for_os(os_))
            hosts[name] = host
        elif os_ and not host.os:
            host.os = os_
            if persona is None and host.source != "array":
                host.persona = persona_for_os(os_)
        for w in wwpns:
            w = normalize_wwpn(w)
            attempted.setdefault(name, set()).add(w)
            if owner.setdefault(w, name) == name and w not in host.wwpns:
                host.wwpns.append(w)
        for i in iqns:
            attempted.setdefault(name, set()).add(i)
            if owner.setdefault(i, name) == name and i not in host.iqns:
                host.iqns.append(i)

    # 1) vCenter — authoritative for its ESXi hosts.
    by_host: OrderedDict[str, list] = OrderedDict()
    for hba in discovery.host_hbas:
        by_host.setdefault(hba.host_name, []).append(hba)
    for name, hbas in by_host.items():
        claim(name, "vcenter", wwpns=[h.wwpn for h in hbas], os_=next((h.os for h in hbas if h.os), "") or "")

    # 2) The sheet's Hosts tab — typed by a human; rows without ids resolved from discovery.
    declared_hosts, lookup = resolve_declared_hosts(declared_hosts, discovery)
    for d in declared_hosts:
        claim(d.name, "sheet", wwpns=d.wwpns, iqns=[d.iqn] if d.iqn else [], os_=d.os)

    # 3) The array's own host objects — they exist; persona is whatever the array already has.
    for ah in discovery.array_hosts:
        if ah.name == _NAMELESS:
            claim("", "array", wwpns=list(ah.wwpns), iqns=list(ah.iqns))
            continue
        claim(ah.name, "array", wwpns=list(ah.wwpns), iqns=list(ah.iqns), persona=ah.persona or None)

    # 4) The fabric name servers, as the zoning plan recorded them (source "switch" only — its
    #    vCenter/sheet/array rows are the same hosts already claimed above).
    for fab in (zoning_plan or {}).get("fabrics", []):
        for h in fab.get("hosts", []):
            if h.get("host_source") != "switch":
                continue
            claim(h.get("host_name") or "", "switch", wwpns=[h["wwpn"]], os_=h.get("os") or "")

    notes: list[str] = []
    # A name whose every initiator belongs to another host has nothing of its own to create — most
    # often a sheet row that re-types a WWPN vCenter already attributes. Say so rather than vanish.
    for name in [n for n, h in hosts.items() if h.transport == "none"]:
        owners = sorted({owner[i] for i in attempted.get(name, set()) if i in owner})
        del hosts[name]
        if not attempted.get(name):
            notes.append(f"Host '{name}' is on the sheet with no WWPN/IQN and was {lookup.get(name, 'not found')} — not planned.")
            continue
        notes.append(
            f"Host '{name}' names only initiators that already belong to another host"
            + (f" ({', '.join(owners)})" if owners else "") + " — not planned."
        )
    if nameless:
        notes.append(
            f"{nameless} initiator(s) logged in with no host name — name them on the sheet's Hosts "
            "tab to provision them."
        )
    return hosts, notes
