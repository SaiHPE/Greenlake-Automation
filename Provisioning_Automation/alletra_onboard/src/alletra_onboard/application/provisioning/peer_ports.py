"""SPEC-025 (BL-26): peer ports. What this run's array says about its FC ports, which of them the
tool may set to peer mode, the plan with the command set a consultant pastes, the judgement of the
read after the paste, verify, and the zone pairs.

Read-only, and nothing here writes: the first slice of ADR 0018 prints the commands. Every parser is
pinned to real output: rack13-ARCUS, OS 10.6.0, 2026-11-16 (`tests/fixtures/peer_ports/rack13/`);
E18U31 with two FC peer ports (OS 10.5.60), D22U27 (OS 10.5.0) and VZ (OS 10.5.51), 2026-11-17
(`tests/fixtures/peer_ports/<array>/`); E18U31 and D22U27 as they were on 2026-10-07 (`rc_pair/`);
and the Primera (`rcip_pair/before/primera/`, 2026-11-03). The tool's own write (the apply) waits
for ADR 0018's live captures and the owner's yes.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.provisioning.discovery import UNCLAIMED_HOST, parse_showhost
from alletra_onboard.application.replication.read import parse_showport_roles
from alletra_onboard.domain.peer_ports import (
    PeerPortAction,
    PeerPortCheck,
    PeerPortIntent,
    PeerPortPlan,
    PeerPortResult,
    PeerPortState,
    PeerPortView,
    PortParams,
)
from alletra_onboard.domain.shared import EndpointCreds

_NSP = re.compile(r"^\d+:\d+:\d+$")
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
        if header_ok and len(p) >= 3 and _NSP.match(p[0]):
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
        if len(p) >= 3 and _NSP.match(p[0]) and p[-1] in ("allowed", "prohibited"):
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
        if len(p) >= 5 and _NSP.match(p[0]):
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
        idx = next((i for i, tok in enumerate(p) if _NSP.match(tok)), None)
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


def is_peer_port(view: PeerPortView, nsp: str) -> bool:
    """An FC port in peer mode. `showport -par` Connmode decides when it was read: Type says what is
    attached now, and live on rack13-ARCUS (2026-11-17) 0:3:1 set to peer with no SFP read mode
    `initiator`, Type `free`, Connmode `peer point` (`tests/fixtures/peer_ports/rack13_live/`). Without
    a `-par` row, Type `peer` (E18U31's linked peer ports read both)."""
    p = view.ports.get(nsp)
    if p is None or not p.is_fc:
        return False
    par = view.params.get(nsp)
    return par.connmode == "peer" if par is not None else p.type == "peer"


def is_free_fc_port(view: PeerPortView, nsp: str) -> bool:
    """SPEC-025 R3's candidate rule: a port the tool may set to peer mode. FC, Type `free`, nothing
    logged in (`showhost -d`, claimed or not), no active export (`showvlun -a`), no persistent-port
    partner in use (FailoverState empty or `none`), and `showport -c` does not call its mode change
    `prohibited`. Type alone is not enough: it says what is attached now, so a port whose host has
    gone away reads `free` (rack13 0:3:3 was `host` on 2026-11-03 and `free` on 2026-11-16).
    The view must hold the `showhost -d` and `showvlun -a` reads; `read_view` always takes them."""
    p = view.ports.get(nsp)
    return bool(
        p is not None and p.is_fc and p.type == "free" and not is_peer_port(view, nsp)
        and not view.logins.get(nsp) and not view.exports.get(nsp)
        and p.failover_state in ("", "none")
        and view.mode_change.get(nsp) != "prohibited"
    )


def free_fc_ports(view: PeerPortView) -> list[str]:
    """Every port `is_free_fc_port` accepts, in `showport` order."""
    return [nsp for nsp in view.ports if is_free_fc_port(view, nsp)]


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
                except Exception:
                    # an optional read may fail and is left out; a required one fails the read
                    if command in _REQUIRED:
                        raise
                    answers[command] = ""
    except Exception as exc:  # the step reports, the operator decides
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


# ------------------------------------------------------------------ R3: the plan

# `help controlport` (OS 10.5.0 to 10.6.0, tests/fixtures/peer_ports/): `controlport offline
# <node:slot:port>...` has no -f, and it asked "Are you sure ...? select q=quit y=yes n=no" every time on
# rack13-ARCUS (2026-11-17); `controlport rst [-m <mode>|-l|-i] [-f] <node:slot:port>...` takes -f.
OFFLINE_ASKS = ("`controlport offline` asks the array's own question (y, n or q) every time and has no option "
                "to skip it: paste the lines one at a time and answer y when it asks. Pasted as a block, the next "
                "line is taken as the answer.")


# Live on rack13-ARCUS (2026-11-17): `controlport config <mode> -ct point -f` resets the port itself and
# brings it back; the `rst` pasted right after it answered *Port 0:3:1 is being reset; please re-issue the
# command when reset is complete*. The line stays for a port left offline by a `config` that never landed.
RST_BUSY = ("If `controlport rst` answers that the port is being reset, the `config` line before it already "
            "brought the port back: read the array again; nothing more to paste for that port.")


# Live on rack13-ARCUS (2026-11-17, the second rerun): `controlport intcoal enable -f <nsp>` pasted right
# after the `config` answered the same *is being reset* and did nothing, and 0:3:1 came back with IntCoal
# `disabled`. Pasted again once the reset had ended, it went in with no answer.
INTCOAL_LAST = ("The `controlport intcoal` lines come last: the array takes one only after the port's reset has "
                "ended. If it answers that the port is being reset, wait a few seconds and paste it again until it "
                "answers nothing; `showport -par` then reads IntCoal as it did before.")


def rst_line(nsp: str) -> str:
    return f"controlport rst -f {nsp}"


def set_commands(nsp: str) -> list[str]:
    """ADR 0018: the help refuses a mode change on an online port, so offline first; `peer` takes only
    `point`. `controlport rst` joins only if the live capture shows the port stays offline."""
    return [f"controlport offline {nsp}", f"controlport config peer -ct point -f {nsp}"]


def restore_lines(nsp: str, before: PortParams) -> list[str]:
    """R5: back to the connection mode `showport -par` read before the change, and then its interrupt
    coalescing (`controlport intcoal <enable|disable> [-f] <node:slot:port>...`, every captured help):
    live on rack13-ARCUS (2026-11-17) the `config` back to host left 1:3:1's IntCoal `disabled` where it
    read `enabled` before, and this form, pasted by hand after the reset, put it back. The `rst` line
    stays on every port, so a port left offline by a hung `config` comes back."""
    lines = [f"controlport offline {nsp}", f"controlport config {before.connmode} -ct {before.conntype} -f {nsp}",
             rst_line(nsp)]
    if before.intcoal:
        lines.append(f"controlport intcoal {before.intcoal.removesuffix('d')} -f {nsp}")
    return lines


def removal_order(blocks: list[list[str]]) -> list[str]:
    """The removal set from per-port restores in the order given, every `controlport intcoal` line moved to
    the end, after every port's `config` reset (INTCOAL_LAST)."""
    lines = [line for block in blocks for line in block]
    last = [line for line in lines if line.startswith("controlport intcoal ")]
    return [line for line in lines if line not in last] + last


def _pairs_sentence(usable: list[str]) -> str:
    nodes = sorted({int(n.split(":", 1)[0]) for n in usable})
    got = (f"got {', '.join(usable)} only on node {nodes[0]}" if usable else "got no port that can be used")
    return (f"Peer ports go in pairs across nodes: name at least one port on each of two nodes ({got}), so the "
            "migration keeps a path when a node restarts.")


def _busy(view: PeerPortView, nsp: str) -> str:
    parts = []
    if view.logins.get(nsp):
        parts.append("logged in: " + ", ".join(view.logins[nsp]))
    if view.exports.get(nsp):
        parts.append("exported: " + ", ".join(view.exports[nsp]))
    return "; ".join(parts)


def pair_partner(view: PeerPortView, nsp: str) -> str:
    """The other FC port of `nsp`'s port pair, or "". `help controlport` (OS 10.5.0 to 10.6.0), *Port pair
    protection*: on a dual-port card both ports are a pair, on a quad-port card ports 1 and 2 and ports 3
    and 4, and *changing the mode of one port in a pair ... causes the other port in the pair to also
    undergo a mode change*, an online partner included, which then *is no longer online*. The help says
    this of LSI adapters; E18U31 (HPE64004-M) runs 0:3:1 in host mode beside its peer port 0:3:2, so that
    card may not enforce it, and nothing shows that rack13's HPE64004-B does not. The tool reads every FC
    card the cautious way: odd port with the next, even port with the one before."""
    try:
        node, slot, port = (int(x) for x in nsp.split(":"))
    except ValueError:
        return ""
    other = f"{node}:{slot}:{port + 1 if port % 2 else port - 1}"
    p = view.ports.get(other)
    return other if p is not None and p.is_fc else ""


def _partner_in_use(view: PeerPortView, partner: str) -> str:
    """Why the pair partner may not move with a mode change, or "" when it is free (the judgement of
    `is_free_fc_port`, worded for the sentence; LESSONS 41)."""
    p = view.ports[partner]
    if busy := _busy(view, partner):
        return f"serves hosts (Type {p.type}; {busy})"
    if p.type != "free":
        what = {"peer": "a peer port", "rcfc": "a Remote Copy port", "host": "a host port"}.get(p.type, f"Type {p.type}")
        return f"is {what}" + (f" ({p.state})" if p.state else "")
    par = view.params.get(partner)
    if par is not None and par.connmode not in ("", "host"):
        return f"is in {par.connmode} mode (showport -par), though nothing is attached now"
    if p.failover_state not in ("", "none"):
        return f"is the failover partner of {p.partner} (state {p.failover_state})"
    if view.mode_change.get(partner) == "prohibited":
        return "does not allow a mode change (showport -c)"
    return ""


def _action(nsp: str, view: PeerPortView) -> PeerPortAction:
    """SPEC-025 R3 for one row, the first rule that applies: not on the array, not FC, already peer,
    serving hosts or busy, another Type, a failover partner in use, a prohibited mode change, a pair
    partner in use (ADR 0018, amended 2026-11-17), no `showport -par` row, else create.
    `is_free_fc_port` is the same judgement on the port itself (LESSONS 41)."""
    p = view.ports.get(nsp)
    partner = pair_partner(view, nsp)
    act = PeerPortAction(nsp=nsp, state="conflict", partner=partner)
    if p is None:
        act.reason = f"{nsp} is not on this array (showport has no such port)."
    elif not p.is_fc:
        act.reason = f"{nsp} is not a Fibre Channel port (Type {p.type}, protocol {p.protocol}). Peer ports are FC ports."
    elif is_peer_port(view, nsp):
        act.state, act.reason = "exists", f"{nsp} is already a peer port."
    elif busy := _busy(view, nsp):
        act.reason = (f"{nsp} serves hosts (Type {p.type}; {busy}). The tool never takes a port from hosts: pick a "
                      "free port, or move the hosts first.")
    elif p.type != "free":
        act.reason = f"{nsp} is Type {p.type}; the tool changes only free FC ports."
    elif p.failover_state not in ("", "none"):
        act.reason = (f"{nsp} is the failover partner of {p.partner} (state {p.failover_state}); changing it removes "
                      "that path protection.")
    elif view.mode_change.get(nsp) == "prohibited":
        act.reason = f"{nsp}: the array does not allow a mode change on this port (showport -c)."
    elif partner and (why := _partner_in_use(view, partner)):
        act.reason = (f"{nsp} shares a port pair with {partner}, which {why}. A mode change on one port of a pair "
                      f"can change the other and take it offline, so the tool never sets {nsp} while {partner} is "
                      "in use: pick a port whose pair partner is free.")
    elif nsp not in view.params:
        act.reason = (f"{nsp}: showport -par gave no connection mode for this port, so the change could not be "
                      "undone. Read the array again.")
    else:
        act.state, act.reason = "create", "free, nothing logged in, no exports" + (
            f"; its pair partner {partner} is free too" if partner else "")
        act.commands, act.undo = set_commands(nsp), restore_lines(nsp, view.params[nsp])
    return act


def _fabric_by_parity(nsp: str) -> str:
    """ADR 0009's fallback: an odd card port is on the odd fabric (F1), an even one on the even (F2)."""
    return "odd fabric (F1)" if int(nsp.rsplit(":", 1)[1]) % 2 else "even fabric (F2)"


def plan_peer_ports(
    intent: PeerPortIntent, view: PeerPortView, zones: dict[str, dict[str, set[str]] | None] | None = None,
) -> PeerPortPlan:
    """R3: one action per sheet row, in sheet order. Pure. `zones` is each switch's effective zones
    (`zoning.parse_active_zones`), keyed by the switch's name, from the run's own read-only switch
    read, None for a switch that could not be read; `zones` None when the run has no switch read. The
    plan says so whenever a switch's zones were not checked."""
    plan = PeerPortPlan(actions=[_action(req.nsp, view) for req in intent.ports])
    plan.blockers = [a.reason for a in plan.actions if a.state == "conflict"]
    usable = [a.nsp for a in plan.actions if a.state in ("create", "exists")]
    if len({int(n.split(":", 1)[0]) for n in usable}) < 2:
        plan.blockers.append(_pairs_sentence(usable))
    fabrics = {_fabric_by_parity(n) for n in usable}
    if len(usable) >= 2 and len(fabrics) == 1:
        plan.notes.append(f"{' and '.join(usable)} are {'both' if len(usable) == 2 else 'all'} on the "
                          f"{fabrics.pop()} by port number; a fabric failure stops the migration.")
    if any(act.state == "create" for act in plan.actions):
        plan.notes.append(OFFLINE_ASKS)
    for act in plan.actions:
        if act.state != "create":
            continue
        p = view.ports[act.nsp]
        if p.state != "ready":
            plan.notes.append(f"{act.nsp}'s link is {p.state} (no cable or no switch port): it can be set, but zones "
                              "will not work until it is cabled.")
        if zones is None:
            plan.notes.append(f"The zones on {act.nsp}'s WWPN were not checked (no switch read): ask the SAN team "
                              "before setting it.")
            continue
        for switch, active in zones.items():
            if active is None:
                plan.notes.append(f"The zones on {act.nsp}'s WWPN were not checked on {switch} (it could not be "
                                  "read): ask the SAN team before setting it.")
                continue
            named = sorted(zone for zone, members in active.items() if p.port_wwn and p.port_wwn in members)
            if named:
                plan.notes.append(f"{act.nsp} ({p.port_wwn}) is still in zone{'s' if len(named) > 1 else ''} "
                                  f"{', '.join(named)} on {switch}: a host that is switched off may use this port. "
                                  "Ask the SAN team before setting it.")
    return plan


def command_set_text(plan: PeerPortPlan, array: str) -> str:
    """R4, first slice: the lines a consultant pastes, in sheet order, as one text for Copy and Download."""
    lines = [f"# Peer ports on {array}: paste on the array's CLI, then read the array again in the tool.",
             f"# {OFFLINE_ASKS}"]
    for act in plan.actions:
        if act.state == "create":
            lines += [f"# {act.nsp}", *act.commands]
    return "\n".join(lines) + "\n"


def removal_set_text(removals: list[str], array: str) -> str:
    """R5: the removal set as text, with its header. The tool never runs it."""
    head = [(f"# Undo the peer ports this run set on {array}. Remove the SAN team's peer-port zones and any "
             "migration that uses these ports first."),
            "# Review before pasting. The tool never runs these.",
            f"# {OFFLINE_ASKS}",
            f"# {RST_BUSY}"] + ([f"# {INTCOAL_LAST}"] if any(r.startswith("controlport intcoal ") for r in removals) else [])
    return "\n".join(head + removals) + "\n"


def planned_removals(plan: PeerPortPlan) -> list[str]:
    """Before the paste: every create's undo, last port first, so the undo exists before anything is pasted."""
    return removal_order([act.undo for act in reversed(plan.actions) if act.state == "create"])


# ------------------------------------------------------------------ R4: the read after the paste

def changed_since(plan: PeerPortPlan, before: PeerPortView, after: PeerPortView) -> bool:
    """Whether the array reads differently on any port the plan sets (Type, mode, state, connection
    mode) or on any other port's mode or Type: the read after a paste, not just a second look."""
    planned = {a.nsp for a in plan.actions if a.state == "create"}
    for nsp, b in before.ports.items():
        a = after.ports.get(nsp)
        if a is None or (a.mode, a.type) != (b.mode, b.type):
            return True
        if nsp in planned and (a.state != b.state or after.params.get(nsp) != before.params.get(nsp)):
            return True
    return False


def read_back_peer_ports(plan: PeerPortPlan, *, before: PeerPortView, after: PeerPortView) -> PeerPortResult:
    """R4: the read after the consultant's paste, judged as the apply will judge its read-back (one
    function, LESSONS 41). Each planned port must read Type peer, Connmode peer, ConnType point; every
    other port's mode and Type must be as in the read the plan was made from (LESSONS 44). The removal
    set keeps only what changed, last port first (R5): a port now peer gets its whole restore, a port
    held offline in its old mode `controlport rst` only, a port in a mode nobody planned the whole
    restore."""
    result = PeerPortResult()
    failures: list[str] = []
    blocks: list[list[str]] = []
    planned = [a for a in plan.actions if a.state == "create"]
    for act in planned:
        b, a = before.ports[act.nsp], after.ports.get(act.nsp)
        b_par, a_par = before.params.get(act.nsp), after.params.get(act.nsp)
        if a is not None and is_peer_port(after, act.nsp) and a_par is not None and (a_par.connmode, a_par.conntype) == ("peer", "point"):
            result.changed.append(act.nsp)
            result.sentences.append(f"{act.nsp} is now a peer port (port WWPN {a.port_wwn or 'not read'}).")
            blocks.append(act.undo)
            continue
        if a is None:
            failures.append(f"{act.nsp} is not in showport any more: check the array before going on.")
            blocks.append(act.undo)
            continue
        failures.append(f"{act.nsp} did not come back as a peer port (Type {a.type}, state {a.state}).")
        same_mode = a.type == b.type and (a_par is None or b_par is None
                                          or (a_par.connmode, a_par.conntype) == (b_par.connmode, b_par.conntype))
        if not same_mode:
            blocks.append(act.undo)
        elif a.state == "offline" and b.state != "offline":
            blocks.append([rst_line(act.nsp)])
    planned_nsps = {a.nsp for a in planned}
    for nsp, b in before.ports.items():
        if nsp in planned_nsps:
            continue
        a = after.ports.get(nsp)
        if a is None:
            failures.append(f"{nsp} is not in showport any more: check the array before going on.")
        elif a.mode != b.mode:
            failures.append(f"{nsp} changed as well (mode {b.mode}, now {a.mode}): check the array before going on.")
        elif a.type != b.type:
            failures.append(f"{nsp} changed as well (Type {b.type}, now {a.type}): check the array before going on.")
    result.sentences += failures
    result.error = " ".join(failures) or None
    result.removals = removal_order(list(reversed(blocks)))
    return result


# ------------------------------------------------------------------ R6: verify

def verify_peer_ports(intent: PeerPortIntent, view: PeerPortView) -> list[PeerPortCheck]:
    """R6, read-only: per sheet row, Type peer, Connmode peer (when `showport -par` was read) and the link."""
    checks = []
    for req in intent.ports:
        p = view.ports.get(req.nsp)
        par = view.params.get(req.nsp)
        if p is None:
            checks.append(PeerPortCheck(nsp=req.nsp, ok=False,
                                        sentence=f"{req.nsp} is not on this array (showport has no such port)."))
        elif not is_peer_port(view, req.nsp):
            what = f"Type {p.type}" + (f", Connmode {par.connmode}" if par is not None and par.connmode != "peer" else "")
            checks.append(PeerPortCheck(nsp=req.nsp, ok=False, sentence=f"{req.nsp} is not a peer port ({what})."))
        elif p.state != "ready":
            checks.append(PeerPortCheck(nsp=req.nsp, ok=False, sentence=(
                f"{req.nsp} is a peer port but its link is {p.state}: check the cable and the switch port.")))
        else:
            checks.append(PeerPortCheck(nsp=req.nsp, ok=True, sentence=f"{req.nsp} is a peer port, link ready."))
    return checks


# ------------------------------------------------------------------ R7: the zones

def peer_zone_pairs(intent: PeerPortIntent, view: PeerPortView) -> list[tuple[str, str]]:
    """(peer port WWPN, source array port WWPN) per sheet row and source, in sheet order. The peer
    WWPN is the one in `view`, which must be the read AFTER the change (the read after the paste, later
    the apply's read-back): a port not yet in peer mode gives no pair, since its WWPN may still change."""
    pairs = []
    for req in intent.ports:
        p = view.ports.get(req.nsp)
        if p is None or not is_peer_port(view, req.nsp) or not p.port_wwn:
            continue
        pairs += [(p.port_wwn, source) for source in req.source_wwpns]
    return pairs
