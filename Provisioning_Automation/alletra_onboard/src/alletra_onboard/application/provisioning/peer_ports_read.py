"""SPEC-025 (BL-26): peer-port array reads and parsers.

Read-only: `read_view` is the only I/O; every `parse_*` function and `build_view` are pure.
Every parser is pinned to real output: rack13-ARCUS, OS 10.6.0, 2026-11-16
(`tests/fixtures/peer_ports/rack13/`); E18U31 with two FC peer ports (OS 10.5.60), D22U27
(OS 10.5.0) and VZ (OS 10.5.51), 2026-11-17 (`tests/fixtures/peer_ports/<array>/`); E18U31 and
D22U27 as they were on 2026-10-07 (`rc_pair/`); and the Primera (`rcip_pair/before/primera/`,
2026-11-03). Planning, read-back, verify and zone pairs live beside this in `peer_ports.py`.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.provisioning.discovery import UNCLAIMED_HOST, parse_showhost
from alletra_onboard.domain.array_parse import NSP, parse_showport_roles
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.peer_ports import (
    PeerPortState,
    PeerPortView,
    PortParams,
)
from alletra_onboard.domain.shared import EndpointCreds

_WWN = re.compile(r"^[0-9A-Fa-f]{16}$")
# `showport -par` on rack13-ARCUS (OS 10.6.0) and in the CLI's own help:
# N:S:P Connmode ConnType CfgRate MaxRate Class2 UniqNodeWwn VCN IntCoal TMWO
_PAR_HEADER = ["N:S:P", "Connmode", "ConnType"]

#: The reads `read_view` makes, in order. All are `showport`, `showhost` and `showvlun` forms, so the
#: read-only client's allowlist does not change.
READS = ("showport", "showport -par", "showport -c", "showhost -d", "showvlun -a", "showport -peer")
#: Without these the view cannot say whether a port is free or what to restore, so a failed one
#: fails the whole read. `showport -c` and `showport -peer` only add detail.
_REQUIRED = ("showport", "showport -par", "showhost -d", "showvlun -a")


def _dash(text: str) -> str:
    return "" if text in ("-", "--", "---") else text


def parse_showport_ports(text: str) -> dict[str, PeerPortState]:
    """`showport` -> {n:s:p: state}. Mode, state, Type, protocol and node WWN come from
    `parse_showport_roles`, the one reader of a port's role (LESSONS 41); this adds the port WWN, the
    Label, and on a Primera the Partner and FailoverState columns (the last two, when the header has
    them; the Alletra MP prints neither). The Label may hold spaces (`Meow Meow` on E18U31)."""
    roles, _node_wwn = parse_showport_roles(text)
    partner_cols = False
    out: dict[str, PeerPortState] = {}
    for line in (text or "").splitlines():
        p = line.split()
        if p and p[0] == "N:S:P":
            partner_cols = p[-2:] == ["Partner", "FailoverState"]
            continue
        role = roles.get(p[0]) if p else None
        if role is None:
            continue
        tail = p[7:]
        partner = failover = ""
        if partner_cols and len(tail) >= 3:
            tail, partner, failover = tail[:-2], _dash(tail[-2]), _dash(tail[-1])
        fc = role.protocol.upper() == "FC"
        out[role.nsp] = PeerPortState(
            nsp=role.nsp, mode=role.mode, state=role.state, type=role.type, protocol=role.protocol,
            node_wwn=role.node_wwn, port_wwn=p[4].upper() if fc and _WWN.match(p[4]) else "",
            label=_dash(" ".join(tail)), partner=partner, failover_state=failover,
        )
    return out


def parse_showport_par(text: str) -> dict[str, PortParams]:
    """`showport -par` -> {n:s:p: (Connmode, ConnType)}: what the removal set restores. Columns are
    fixed and the first three are read by position. Output with any other header reads as nothing,
    so the plan blocks on a missing read rather than restoring from a column it misread."""
    out: dict[str, PortParams] = {}
    header_ok, intcoal_at = False, None
    for line in (text or "").splitlines():
        p = line.split()
        if p and p[0] == "N:S:P":
            header_ok = p[:3] == _PAR_HEADER
            intcoal_at = p.index("IntCoal") if "IntCoal" in p else None
            continue
        if header_ok and len(p) >= 3 and NSP.match(p[0]):
            intcoal = p[intcoal_at] if intcoal_at is not None and len(p) > intcoal_at else ""
            out[p[0]] = PortParams(nsp=p[0], connmode=p[1], conntype=p[2],
                                   intcoal=intcoal if intcoal in ("enabled", "disabled") else "")
    return out


def parse_showport_c(text: str) -> dict[str, str]:
    """`showport -c` -> {n:s:p: Mode_change} (`allowed` | `prohibited`, the last column). A port with
    more than one device prints the extra devices on lines of their own with no N:S:P. The Device
    column names host objects only: on rack13 the unclaimed login on 0:3:4 shows as `---`, so it
    never replaces `showhost -d` for "is anything logged in"."""
    out: dict[str, str] = {}
    for line in (text or "").splitlines():
        p = line.split()
        if len(p) >= 3 and NSP.match(p[0]) and p[-1] in ("allowed", "prohibited"):
            out[p[0]] = p[-1]
    return out


def parse_showport_peer(text: str) -> list[PeerPortState]:
    """`showport -peer` -> one row per peer port, virtual ones included. The first five columns are
    read: N:S:P Mode State Node_WWN Port_WWN. The CLI's help shows `Rate` after them; the array
    itself (E18U31, OS 10.5.60) also prints `VPI`. The rows are this array's own peer ports, never
    the source array they reach. An array with none answers *There is no specified port
    information.* (rack13, D22U27, VZ), which reads as an empty list."""
    out: list[PeerPortState] = []
    for line in (text or "").splitlines():
        p = line.split()
        if len(p) >= 5 and NSP.match(p[0]):
            out.append(PeerPortState(
                nsp=p[0], mode=p[1], state=p[2],
                node_wwn=p[3].upper() if _WWN.match(p[3]) else "",
                port_wwn=p[4].upper() if _WWN.match(p[4]) else "",
            ))
    return out


def _logins_by_port(showhost_d: str) -> dict[str, list[str]]:
    """`showhost -d` -> {n:s:p: [who is logged in]}: a host object by its name, an unclaimed login
    (`-- --`) as *an unnamed initiator <WWPN or IQN>*. Only real logins (Port is an N:S:P) count."""
    out: dict[str, list[str]] = {}
    for host in parse_showhost(showhost_d):
        for initiator, ports in [*host.wwpns.items(), *host.iqns.items()]:
            who = host.name if host.name != UNCLAIMED_HOST else f"an unnamed initiator {initiator}"
            for port in ports:
                names = out.setdefault(port, [])
                if who not in names:
                    names.append(who)
    return out


def _exports_by_port(showvlun_a: str) -> dict[str, list[str]]:
    """`showvlun -a` -> {n:s:p: [exported volume]}. Rows are anchored on the N:S:P token like
    `path_verify.parse_showvlun_active`, but every active row counts whatever the initiator: that
    parser leaves NVMe rows out because path verify does not check them, and an NVMe export still
    makes a port busy."""
    out: dict[str, list[str]] = {}
    for line in (showvlun_a or "").splitlines():
        p = line.split()
        if len(p) < 7 or not p[0].isdigit():
            continue
        idx = next((i for i, tok in enumerate(p) if NSP.match(tok)), None)
        if idx is None or idx < 4:
            continue
        volume = " ".join(p[1:idx - 2])
        names = out.setdefault(p[idx], [])
        if volume not in names:
            names.append(volume)
    return out


def build_view(
    showport: str, showhost_d: str = "", showvlun_a: str = "", showport_par: str = "",
    showport_c: str = "", showport_peer: str = "",
) -> PeerPortView:
    """The view from the array's answers. Pure: `read_view` is the only I/O."""
    return PeerPortView(
        ports=parse_showport_ports(showport),
        params=parse_showport_par(showport_par),
        mode_change=parse_showport_c(showport_c),
        logins=_logins_by_port(showhost_d),
        exports=_exports_by_port(showvlun_a),
        peer_listing=parse_showport_peer(showport_peer),
    )


def read_view(
    creds: EndpointCreds, *, array_cli_factory: Callable = make_array_cli,
) -> PeerPortView:
    """One SSH session on the read-only client (ADR 0001), the reads in `READS`. A failed login, or a
    required read that fails or answers `Error`, is the view's `read_error` and the view is empty:
    a half read could make a busy port look free."""
    answers: dict[str, str] = {}
    try:
        with array_cli_factory(creds) as cli:
            for command in READS:
                try:
                    answers[command] = cli.run(command)
                except DeviceError:
                    if command in _REQUIRED:
                        raise
                    answers[command] = ""
    except DeviceError as exc:
        return PeerPortView(host=creds.host, read_error=f"Could not read {creds.host}: {exc}")
    for command in READS:
        first = answers[command].strip().splitlines()[0] if answers[command].strip() else ""
        if first.lower().startswith("error"):
            if command in _REQUIRED:
                return PeerPortView(host=creds.host,
                                    read_error=f"Could not read {creds.host}: '{command}' answered: {first}")
            answers[command] = ""
    view = build_view(
        answers["showport"], showhost_d=answers["showhost -d"], showvlun_a=answers["showvlun -a"],
        showport_par=answers["showport -par"], showport_c=answers["showport -c"],
        showport_peer=answers["showport -peer"],
    )
    view.host = creds.host
    return view
