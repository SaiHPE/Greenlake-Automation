"""Pure CLI output parsers shared across array contexts (STANDARD B1, L6).

Zero I/O and zero adapter imports: parses captured `show*` text into domain records or plain
dictionaries so discovery, replication, unified file, verification and documents never import
each other for parsing.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Any

from alletra_onboard.domain.discovery import EthernetPort
from alletra_onboard.domain.replication import PortRole, RcipPort

_NSP = re.compile(r"^\d+:\d+:\d+$")
_TOTAL = re.compile(r"^\s*\d+\s+total\b")
_RULE = re.compile(r"^\s*-{4,}\s*$")
_NONE_LISTED = re.compile(r"^\s*No \S.* listed\s*$", re.IGNORECASE)
_SHOWSYS_ROW = re.compile(
    r"^(?P<id>0x[0-9A-Fa-f]+)\s+(?P<name>\S+)\s+(?P<model>.*?)\s+(?P<serial>[A-Z0-9]{6,})"
    # A Primera (OS 4.6.20, 2026-11-03) prints a ClusterLED column ("Green") between Master and TotalCap.
    r"\s+(?P<nodes>\d+)\s+(?P<master>\d+)(?:\s+[A-Za-z]+)?\s+\d+\s+\d+\s+\d+\s+\d+\s*$"
)


def _clean(value: str) -> str:
    return "" if value in ("-", "--", "") else value


def _nsp_parts(token: str) -> tuple[int, int, int] | None:
    parts = token.split(":")
    if len(parts) != 3:
        return None
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None


def table_lines(text: str) -> list[str]:
    """The data lines of a CLI listing: header first; rules, totals and blank lines dropped."""
    out: list[str] = []
    for line in (text or "").splitlines():
        if not line.strip() or _RULE.match(line) or _TOTAL.match(line) or _NONE_LISTED.match(line):
            continue
        out.append(line.rstrip())
    return out


def parse_cli_sets(text: str) -> OrderedDict[str, list[str]]:
    """``showhostset`` / ``showvvset`` -> ``{set name: [members]}`` in listing order.

    Columns ``Id Name Members``; a set with several members continues on indented lines carrying
    only the member; ``--`` is an empty set; "No … listed" is no sets at all."""
    out: OrderedDict[str, list[str]] = OrderedDict()
    lines = table_lines(text)
    current: str | None = None
    for line in lines[1:]:
        toks = line.split()
        if toks[0].isdigit() and len(toks) >= 2 and not line.startswith(" " * 8):
            current = toks[1]
            members = toks[2:]
            out[current] = [] if members == ["--"] else members
        elif current is not None:
            out[current].extend(t for t in toks if t != "--")
    return out


def parse_showsys(text: str) -> dict[str, Any]:
    """`showsys` -> {id (decimal), name, model, serial}. The Model column carries spaces
    ("HPE Alletra Storage MP"), so the row is matched as a whole, not split."""
    for line in (text or "").splitlines():
        m = _SHOWSYS_ROW.match(line.strip())
        if m:
            return {
                "id": int(m.group("id"), 16),
                "name": m.group("name"),
                "model": " ".join(m.group("model").split()),
                "serial": m.group("serial"),
            }
    return {}


def parse_showversion(text: str) -> str:
    """`showversion` -> the release version string ("10.5.0")."""
    m = re.search(r"Release version\s+(\S+)", text or "")
    return m.group(1) if m else ""


def parse_showport_rcip(text: str) -> list[RcipPort]:
    """`showport -rcip`: N:S:P State HwAddr IPAddr Netmask/PrefixLen Gateway MTU Rate Duplex AutoNeg.
    "There is no specified port information" (no RCIP configured) -> []."""
    out: list[RcipPort] = []
    for line in (text or "").splitlines():
        p = line.split()
        if len(p) < 6 or not _NSP.match(p[0]):
            continue
        out.append(RcipPort(
            nsp=p[0], state=p[1], ip=_clean(p[3]), netmask=_clean(p[4]), gateway=_clean(p[5]),
            mtu=_clean(p[6]) if len(p) > 6 else "", rate=_clean(p[7]) if len(p) > 7 else "",
        ))
    return out


def parse_showport_roles(text: str) -> tuple[dict[str, PortRole], str]:
    """`showport`: N:S:P Mode State Node_WWN/IP Port_WWN/HW_Addr Type Protocol Label [Partner FailoverState]
    -> ({n:s:p: role}, the first FC row's node WWN). Columns are fixed on both lab arrays (Alletra MP OS
    10.5.55, Primera OS 4.6.20, 2026-11-03); a row with fewer than 7 columns is not a port. FC rows keep
    their node WWN and their port WWN (SPEC-031 R1): every row's, since a peer port carries a node WWN of
    its own (E18U31, 2026-11-17)."""
    roles: dict[str, PortRole] = {}
    node_wwn = ""
    for line in (text or "").splitlines():
        p = line.split()
        if len(p) < 7 or not _NSP.match(p[0]):
            continue
        role = PortRole(nsp=p[0], mode=p[1], state=p[2], type=p[5], protocol=p[6])
        if role.protocol.upper() == "FC" and re.fullmatch(r"[0-9A-Fa-f]{16}", p[3]):
            role.node_wwn = p[3].upper()
            node_wwn = node_wwn or role.node_wwn
        if role.protocol.upper() == "FC" and re.fullmatch(r"[0-9A-Fa-f]{16}", p[4]):
            role.port_wwn = p[4].upper()
        roles[p[0]] = role
    return roles, node_wwn


def parse_file_ports(showport_file: str) -> list[EthernetPort]:
    """`showport -file` -> [EthernetPort]. A separate view with its own columns:

        N:S:P  Mode  State  IPAddr/PrefixLen  IPDisable  Gateway  VLAN  MTU  Rate  Eth  Link  FailoverIPs
    """
    out: list[EthernetPort] = []
    for line in (showport_file or "").splitlines():
        p = line.split()
        if len(p) < 12 or not p[0][:1].isdigit() or ":" not in p[0]:
            continue
        nsp = _nsp_parts(p[0])
        if nsp is None:
            continue
        node, slot, card_port = nsp
        address, _, prefix = p[3].partition("/")
        out.append(EthernetPort(
            node=node, slot=slot, card_port=card_port, role="file",
            mode=p[1], link_state=p[2], address=address, prefix_len=prefix,
            ip_disabled=p[4].upper() == "Y", gateway=_clean(p[5]), vlan=p[6], mtu=p[7],
            rate=_clean(p[8]) if p[8] != "n/a" else "", eth=p[9], link=p[10],
            failover_ips=[ip for ip in p[11:] if _clean(ip)],
        ))
    return out
