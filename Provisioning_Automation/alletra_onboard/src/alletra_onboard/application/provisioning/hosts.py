"""The provisioning host union (SPEC-003): every host the run can name, from every source that can
name one, in trust order — vCenter, the sheet's Hosts tab, the array's own host objects, the fabric
name servers as the zoning plan recorded them.

The zoning step has carried this union inline since rc.6 (`zoning_plan.build_zoning_plan`); until
SPEC-003 the provisioning step still read vCenter alone, so a Windows host declared on the sheet or
a Linux host seen only on the fabric could be zoned but never put in a host set or given an export.
"""

from __future__ import annotations

import ipaddress
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field

from alletra_onboard.domain.discovery import (
    ArrayHost,
    DiscoveryReport,
    HostRead,
    node_name_from_iqn,
)
from alletra_onboard.domain.provisioning import (
    DeclaredHost,
    HostSource,
    ProvisionableHost,
    persona_for_os,
)
from alletra_onboard.domain.shared import normalize_wwpn

# The array files every login with no host object under one nameless row (discovery.UNCLAIMED_HOST).
_NAMELESS = ""


def _short(name: str) -> str:
    return (name or "").strip().lower().split(".")[0]


def _short_key(name: str) -> str:
    """The short name to compare, or "" for an IP address ("10.9.9.9" is not host "10")."""
    try:
        ipaddress.ip_address((name or "").strip())
        return ""
    except ValueError:
        return _short(name)


def _ambiguous(short: str, where: str, names: list[str]) -> str:
    return (
        f"not found uniquely — short name '{short}' fits {len(names)} {where} ({', '.join(names)}); "
        "type the full name or its WWPN/IQN on the Hosts tab"
    )


@dataclass(frozen=True)
class _LookupHit:
    source_name: str
    text: str
    wwpns: tuple[str, ...] = ()
    iqn: str = ""
    os_: str = ""
    ambiguous: bool = False


@dataclass(frozen=True)
class _DiscoveryIndex:
    by_vcenter: dict[str, list[str]]
    vcenter_iqns: dict[str, list[str]]
    reads: dict[str, HostRead]
    iqn_owner: dict[str, str]
    known_owner: dict[str, str]
    array_hosts: list[ArrayHost]
    vcenter_read: bool

    @classmethod
    def build(cls, discovery: DiscoveryReport) -> _DiscoveryIndex:
        by_vcenter: dict[str, list[str]] = {}
        for hba in discovery.host_hbas:
            by_vcenter.setdefault(hba.host_name, []).append(normalize_wwpn(hba.wwpn))
        vcenter_iqns = {i.host_name: i.iqns for i in discovery.host_identities}
        reads = {r.host_name: r for r in discovery.host_reads if not r.error}
        iqn_owner = {iqn: a.name for a in discovery.array_hosts for iqn in a.iqns}
        # Who already names an initiator: vCenter first, then an array host object (never the nameless bucket).
        known_owner = {i: a.name for a in discovery.array_hosts if a.name for i in (*a.wwpns, *a.iqns)}
        known_owner.update({w: name for name, ws in by_vcenter.items() for w in ws})
        # A vCenter that timed out was never asked, so "not in vCenter" would be a false statement.
        vcenter_read = not any(n.startswith("vCenter discovery failed") for n in discovery.notes)
        return cls(
            by_vcenter=by_vcenter,
            vcenter_iqns=vcenter_iqns,
            reads=reads,
            iqn_owner=iqn_owner,
            known_owner=known_owner,
            array_hosts=list(discovery.array_hosts),
            vcenter_read=vcenter_read,
        )

    @property
    def vcenter_names(self) -> set[str]:
        return {*self.by_vcenter, *self.vcenter_iqns}


def _match_host_read(d: DeclaredHost, idx: _DiscoveryIndex) -> _LookupHit | None:
    read = idx.reads.get(d.name)
    if not (read and (read.wwpns or read.iqns)):
        return None
    owner = next((idx.known_owner[i] for i in (*read.wwpns, *read.iqns) if i in idx.known_owner), "")
    return _LookupHit(
        source_name=owner,
        text=f"read from the server over {read.method.upper()} ({read.address})",
        wwpns=tuple(read.wwpns),
        iqn=read.iqns[0] if read.iqns else "",
        os_=read.os,
    )


def _match_vcenter_exact(d: DeclaredHost, idx: _DiscoveryIndex) -> _LookupHit | None:
    keys = {k for k in (d.name.strip().lower(), d.address.strip().lower()) if k}
    found = next((n for n in idx.vcenter_names if n.lower() in keys), None)
    if not found:
        return None
    iqns = idx.vcenter_iqns.get(found, [])
    return _LookupHit(found, f"found in vCenter as {found}", tuple(idx.by_vcenter.get(found, [])), iqns[0] if iqns else "")


def _match_array_exact(d: DeclaredHost, idx: _DiscoveryIndex) -> _LookupHit | None:
    target = d.name.strip().lower()
    ah = next((a for a in idx.array_hosts if a.name and a.name.lower() == target), None)
    if not (ah and (ah.wwpns or ah.iqns)):
        return None
    return _LookupHit(ah.name, f"found on the array as host {ah.name}", tuple(ah.wwpns), next(iter(ah.iqns), ""))


def _match_array_ip(d: DeclaredHost, idx: _DiscoveryIndex) -> _LookupHit | None:
    if not d.address:
        return None
    addr = d.address.strip()
    by_ip = next((iqn for a in idx.array_hosts for iqn, ip in a.addresses.items() if ip == addr), None)
    if not by_ip:
        return None
    return _LookupHit(idx.iqn_owner.get(by_ip, ""), f"found on the array: iSCSI login from {d.address}", iqn=by_ip)


def _match_vcenter_short(d: DeclaredHost, idx: _DiscoveryIndex) -> _LookupHit | None:
    short = _short_key(d.name)
    matches = sorted(n for n in idx.vcenter_names if short and _short_key(n) == short)
    if len(matches) > 1:
        return _LookupHit("", _ambiguous(short, "vCenter hosts", matches), ambiguous=True)
    if not matches:
        return None
    name = matches[0]
    iqns = idx.vcenter_iqns.get(name, [])
    return _LookupHit(
        name, f"found in vCenter as {name} (short-name match)",
        tuple(idx.by_vcenter.get(name, [])), iqns[0] if iqns else "",
    )


def _match_array_short(d: DeclaredHost, idx: _DiscoveryIndex) -> _LookupHit | None:
    short = _short_key(d.name)
    matches = [a for a in idx.array_hosts if a.name and short and _short_key(a.name) == short and (a.wwpns or a.iqns)]
    if len(matches) > 1:
        return _LookupHit("", _ambiguous(short, "array hosts", sorted(a.name for a in matches)), ambiguous=True)
    if not matches:
        return None
    ah = matches[0]
    return _LookupHit(
        ah.name, f"found on the array as host {ah.name} (short-name match)",
        tuple(ah.wwpns), next(iter(ah.iqns), ""),
    )


def _match_iqn_node_short(d: DeclaredHost, idx: _DiscoveryIndex) -> _LookupHit | None:
    short = _short_key(d.name)
    matches = sorted(i for i in idx.iqn_owner if short and _short(node_name_from_iqn(i)) == short)
    if len(matches) > 1:
        return _LookupHit("", _ambiguous(short, "array IQNs", matches), ambiguous=True)
    if not matches:
        return None
    iqn = matches[0]
    return _LookupHit(idx.iqn_owner[iqn], f"found on the array: IQN names node {node_name_from_iqn(iqn)}", iqn=iqn)


# Ordered resolution table (SPEC-014 R1): first matching rule wins.
_LOOKUP_RULES: tuple[Callable[[DeclaredHost, _DiscoveryIndex], _LookupHit | None], ...] = (
    _match_host_read,
    _match_vcenter_exact,
    _match_array_exact,
    _match_array_ip,
    _match_vcenter_short,
    _match_array_short,
    _match_iqn_node_short,
)


def _not_found_reason(d: DeclaredHost, vcenter_read: bool) -> str:
    vc = "not found — not in vCenter" if vcenter_read else "not found — vCenter was not reached, so it could not be checked"
    ip = f", no iSCSI login from {d.address}" if d.address else ""
    return f"{vc}, no array host of that name{ip}; add its WWPN/IQN on the Hosts tab"


def _apply_hit(d: DeclaredHost, hit: _LookupHit, *, canonical_names: bool) -> DeclaredHost:
    update: dict[str, object] = {"wwpns": list(hit.wwpns), "iqn": hit.iqn}
    if canonical_names and hit.source_name:  # an unclaimed login has no name of its own
        update["name"] = hit.source_name
    if hit.os_ and not d.os:
        update["os"] = hit.os_
    return d.model_copy(update=update)


def resolve_declared_hosts(
    declared_hosts: list[DeclaredHost] | None, discovery: DiscoveryReport, *, canonical_names: bool = False,
) -> tuple[list[DeclaredHost], dict[str, str]]:
    """SPEC-014 R1: fill in the initiators of a sheet host typed with a name (and IP) but no WWPN/IQN.

    Looked up, in order: the server's own read over its sheet login (SPEC-014 R4); the vCenter host
    of that name or IP; the array host object of that name; an array iSCSI login from that IP; then
    by short name (esx01 = esx01.lab.local) the vCenter host, the array host object, an IQN's node
    name. A short name that fits more than one host is refused, not guessed. Returns (hosts with
    ids filled where found, sheet name -> how it was found or why not). Rows that carried ids are
    returned unchanged and have no entry.

    `canonical_names` renames a found row to the name its source already uses, for the planners:
    the array refuses a second host object for a WWN it has (`ensure_host`), and vCenter's name
    already owns those initiators in the union."""
    idx = _DiscoveryIndex.build(discovery)
    out: list[DeclaredHost] = []
    how: dict[str, str] = {}
    for d in declared_hosts or []:
        if d.wwpns or d.iqn:
            out.append(d)
            continue
        hit = next((found for rule in _LOOKUP_RULES if (found := rule(d, idx)) is not None), None)
        if hit is None:
            out.append(d)
            how[d.name] = _not_found_reason(d, idx.vcenter_read)
        elif hit.ambiguous:
            out.append(d)
            how[d.name] = hit.text
        else:
            out.append(_apply_hit(d, hit, canonical_names=canonical_names))
            how[d.name] = hit.text
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
        if d.iqn and read.iqns and d.iqn.lower() not in {i.lower() for i in read.iqns}:   # IQNs are case-insensitive
            out.append(
                f"Host '{d.name}': sheet IQN {d.iqn} is not the server's — {read.address} reports "
                f"{', '.join(read.iqns)}. Fix the Hosts tab."
            )
    return out


@dataclass(frozen=True)
class _HostSighting:
    """One source's view of a host to merge into the provisioning host union."""

    name: str
    source: HostSource
    wwpns: tuple[str, ...] = ()
    iqns: tuple[str, ...] = ()
    os_: str = ""
    persona: str | None = None


@dataclass
class _HostUnion:
    hosts: OrderedDict[str, ProvisionableHost] = field(default_factory=OrderedDict)
    owner: dict[str, str] = field(default_factory=dict)          # initiator (wwpn or iqn) -> host name
    attempted: dict[str, set[str]] = field(default_factory=dict)  # host name -> every initiator a source gave it
    nameless: int = 0

    def claim(self, entry: _HostSighting) -> None:
        if not entry.name:
            self.nameless += (
                sum(1 for w in entry.wwpns if w not in self.owner)
                + sum(1 for i in entry.iqns if i not in self.owner)
            )
            return
        host = self._ensure_host(entry)
        self._claim_initiators(entry.name, (normalize_wwpn(w) for w in entry.wwpns), host.wwpns)
        self._claim_initiators(entry.name, entry.iqns, host.iqns)

    def _ensure_host(self, entry: _HostSighting) -> ProvisionableHost:
        host = self.hosts.get(entry.name)
        if host is None:
            host = ProvisionableHost(
                name=entry.name, source=entry.source, os=entry.os_,
                persona=entry.persona or persona_for_os(entry.os_),
            )
            self.hosts[entry.name] = host
        if entry.source == "array":
            host.on_array = True
        elif entry.os_ and not host.os:
            host.os = entry.os_
            if entry.persona is None and host.source != "array":
                host.persona = persona_for_os(entry.os_)
        return host

    def _claim_initiators(self, name: str, items, target: list[str]) -> None:
        for init in items:
            self.attempted.setdefault(name, set()).add(init)
            if self.owner.setdefault(init, name) == name and init not in target:
                target.append(init)


def _vcenter_sightings(discovery: DiscoveryReport) -> list[_HostSighting]:
    # 1) vCenter — authoritative for its ESXi hosts.
    by_host: OrderedDict[str, list] = OrderedDict()
    for hba in discovery.host_hbas:
        by_host.setdefault(hba.host_name, []).append(hba)
    return [
        _HostSighting(
            name=name, source="vcenter",
            wwpns=tuple(h.wwpn for h in hbas),
            os_=next((h.os for h in hbas if h.os), "") or "",
        )
        for name, hbas in by_host.items()
    ]


def _array_sightings(discovery: DiscoveryReport) -> list[_HostSighting]:
    # 3) The array's own host objects — they exist; persona is whatever the array already has.
    return [
        _HostSighting(
            name="" if ah.name == _NAMELESS else ah.name,
            source="array",
            wwpns=tuple(ah.wwpns),
            iqns=tuple(ah.iqns),
            persona=None if ah.name == _NAMELESS else (ah.persona or None),
        )
        for ah in discovery.array_hosts
    ]


def _switch_sightings(zoning_plan: dict | None) -> list[_HostSighting]:
    # 4) The fabric name servers, as the zoning plan recorded them (source "switch" only — its
    #    vCenter/sheet/array rows are the same hosts already claimed above).
    return [
        _HostSighting(
            name=h.get("host_name") or "", source="switch",
            wwpns=(h["wwpn"],), os_=h.get("os") or "",
        )
        for fab in (zoning_plan or {}).get("fabrics", [])
        for h in fab.get("hosts", [])
        if h.get("host_source") == "switch"
    ]


def _prune_empty_hosts(
    union: _HostUnion, sheet_names: set[str], lookup: dict[str, str], alias_of: dict[str, str],
) -> list[str]:
    """A name whose every initiator belongs to another host has nothing of its own to create — most
    often a sheet row that re-types a WWPN vCenter already attributes. Say so rather than vanish."""
    notes: list[str] = []
    for name in [n for n, h in union.hosts.items() if h.transport == "none"]:
        owners = sorted({union.owner[i] for i in union.attempted.get(name, set()) if i in union.owner})
        del union.hosts[name]
        if not union.attempted.get(name):
            notes.append(f"Host '{name}' is on the sheet with no WWPN/IQN and was {lookup.get(name, 'not found')} — not planned.")
        elif name in sheet_names and len(owners) == 1:
            alias_of[name] = owners[0]
            notes.append(f"Host '{name}' has only initiators that belong to '{owners[0]}' — treated as another name for it.")
        else:
            notes.append(
                f"Host '{name}' names only initiators that already belong to another host"
                + (f" ({', '.join(owners)})" if owners else "") + " — not planned."
            )
    return notes


def _attach_aliases(hosts: OrderedDict[str, ProvisionableHost], alias_of: dict[str, str]) -> None:
    """The sheet's own name for a host planned under another, so Host-sets members typed with it still land."""
    for alias, target in alias_of.items():
        seen = {alias}
        while target not in hosts and target in alias_of and target not in seen:
            seen.add(target)
            target = alias_of[target]
        if alias not in hosts and target in hosts and alias not in hosts[target].aliases:
            hosts[target].aliases.append(alias)


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
    union = _HostUnion()
    # 2) The sheet's Hosts tab — typed by a human; rows without ids resolved from discovery.
    typed = list(declared_hosts or [])
    resolved, lookup = resolve_declared_hosts(typed, discovery, canonical_names=True)
    alias_of = {t.name: d.name for t, d in zip(typed, resolved) if t.name != d.name}
    sheet_names = {t.name for t in typed} | {d.name for d in resolved}
    sheet_sightings = [
        _HostSighting(name=d.name, source="sheet", wwpns=tuple(d.wwpns), iqns=(d.iqn,) if d.iqn else (), os_=d.os)
        for d in resolved
    ]

    for batch in (_vcenter_sightings(discovery), sheet_sightings, _array_sightings(discovery), _switch_sightings(zoning_plan)):
        for entry in batch:
            union.claim(entry)

    notes = _prune_empty_hosts(union, sheet_names, lookup, alias_of)
    _attach_aliases(union.hosts, alias_of)
    if union.nameless:
        notes.append(
            f"{union.nameless} initiator(s) logged in with no host name — name them on the sheet's Hosts "
            "tab to provision them."
        )
    return union.hosts, notes


def host_fabric_logins(discovery: DiscoveryReport, zoning_plan: dict | None) -> dict[str, list[set[str]]]:
    """host name -> [fabric labels seen by the array side, fabric labels seen by the switch side].
    Kept as two sets because the two sides label fabrics differently (odd/even vs F1/F2); the count
    that matters is the larger of the two, never their union."""
    array_side: dict[str, set[str]] = {}
    for hba in discovery.host_hbas:
        if hba.fabric:
            array_side.setdefault(hba.host_name, set()).add(hba.fabric)
    port_fabric: dict[str, str] = {p.label: p.fabric for p in discovery.array_ports if p.fabric}
    for ah in discovery.array_hosts:
        for ports in list(ah.wwpns.values()) + list(ah.iqns.values()):
            for port in ports:
                if port in port_fabric:
                    array_side.setdefault(ah.name, set()).add(port_fabric[port])
    switch_side: dict[str, set[str]] = {}
    for fab in (zoning_plan or {}).get("fabrics", []):
        for h in fab.get("hosts", []):
            if h.get("host_name") and h.get("fabric"):
                switch_side.setdefault(h["host_name"], set()).add(h["fabric"])
    return {n: [array_side.get(n, set()), switch_side.get(n, set())] for n in set(array_side) | set(switch_side)}
