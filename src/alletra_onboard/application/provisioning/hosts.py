"""The provisioning host union (SPEC-003): every host the run can name, from every source that can
name one, in trust order — vCenter, the sheet's Hosts tab, the array's own host objects, the fabric
name servers as the zoning plan recorded them.

The zoning step has carried this union inline since rc.6 (`zoning_plan.build_zoning_plan`); until
SPEC-003 the provisioning step still read vCenter alone, so a Windows host declared on the sheet or
a Linux host seen only on the fabric could be zoned but never put in a host set or given an export.
"""

from __future__ import annotations

from collections import OrderedDict

from alletra_onboard.domain.discovery import DiscoveryReport
from alletra_onboard.domain.provisioning import DeclaredHost, ProvisionableHost, persona_for_os
from alletra_onboard.domain.shared import normalize_wwpn

# The array files every login with no host object under one nameless row (discovery.UNCLAIMED_HOST).
_NAMELESS = ""


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

    # 2) The sheet's Hosts tab — servers nothing can see yet, typed by a human.
    for d in declared_hosts or []:
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
