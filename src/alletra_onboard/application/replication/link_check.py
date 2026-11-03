"""SPEC-020: the latency between the two arrays, measured with `checkrclink` before replication.

R1 pairs every outbound RCIP link of A toward B with B's port; R2 runs the array's own link test
on each pair (server on B, client on A, read until the latency is printed, stop both); R3 is the
result. Nothing here changes either array's configuration on purpose; the test server does add a
host route on B, and the links are read again afterwards in case it was left behind (live
2026-11-03, Primera OS 4.6.20: `stopserver` kept the route and every RCIP link went Down).
"""

from __future__ import annotations

import ipaddress
import re
import time
from collections.abc import Callable
from datetime import UTC, datetime

from alletra_onboard.adapters.array.cli_client import ArrayCliError
from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.replication.read import parse_showrcopy
from alletra_onboard.domain.replication import (
    LINK_CHECK_TIME_DEFAULT,
    LinkCheck,
    LinkCheckResult,
    LinkPair,
    RcipPort,
    ReplicationIntent,
    ReplicationReport,
)
from alletra_onboard.domain.shared import EndpointCreds

#: The client prints these before its throughput test starts (screenshot 2026-10-12).
LATENCY_RE = re.compile(r"Average measured latency:\s*([\d.]+)\s*ms")
LOST_RE = re.compile(r"Pings Lost:\s*([\d.]+)\s*%")
#: The server's route to A's address: "Adding route: 10.93.18.11 -> 10.93.18.1" (a gateway) or "-> eth12".
ROUTE_RE = re.compile(r"Adding route:\s*(\S+)\s*->\s*(\S+)")
#: Read the client's output until this line, then stop it (R2 step 3).
UNTIL = r"Pings Lost:\s*[\d.]+\s*%"
#: How long the latency phase may take before the pair counts as failed.
LATENCY_WAIT_S = 120.0
#: After the stops: how long a link that was Up before may take to come back before it counts as broken.
LINKS_SETTLE_S = 60.0
LINKS_POLL_S = 10.0

FC_ONLY = "The link check measures RCIP links; this pair replicates over fibre channel."


def plan_pairs(report: ReplicationReport) -> tuple[list[LinkPair], list[str]]:
    """R1: (pairs to check, pairs not checkable with the reason) from the preview's read."""
    p = report.partnership
    if p is None:
        return [], ["No Remote Copy partnership between the arrays was found; nothing to measure."]
    targets = set(p.target_by_mode.values()) or {p.target_on_primary}
    ip_a = {port.nsp: port.ip for port in report.primary.rcip_ports if port.ip}
    nsp_b = {port.ip: port.nsp for port in report.peer.rcip_ports if port.ip}
    pairs: list[LinkPair] = []
    unchecked: list[str] = []
    for link in report.primary.links:
        if link.inbound or link.target not in targets:
            continue
        a_ip = ip_a.get(link.nsp)
        b_nsp = nsp_b.get(link.address)
        if not a_ip:
            unchecked.append(f"A {link.nsp} → {link.address}: port {link.nsp} has no RCIP address on A (showport -rcip).")
        elif not b_nsp:
            unchecked.append(f"A {link.nsp} → {link.address}: no RCIP port on B carries {link.address}.")
        else:
            pairs.append(LinkPair(nsp_a=link.nsp, ip_a=a_ip, nsp_b=b_nsp, ip_b=link.address))
    if not pairs and not unchecked:
        unchecked.append(FC_ONLY if not report.primary.rcip_ports else
                         f"Target '{p.target_on_primary}' on A has no outbound link.")
    return pairs, unchecked


def parse_client_output(text: str) -> tuple[float | None, float | None]:
    """(latency ms, pings lost %) from the client's output, either None when not printed."""
    latency = LATENCY_RE.search(text)
    lost = LOST_RE.search(text)
    return (float(latency.group(1)) if latency else None, float(lost.group(1)) if lost else None)


def same_network(port: RcipPort, address: str) -> bool:
    """`address` is on `port`'s own IPv4 network (from its netmask), so no gateway is needed to reach it."""
    try:
        net = ipaddress.ip_network(f"{port.ip}/{port.netmask}", strict=False)
        return ipaddress.ip_address(address) in net
    except ValueError:
        return False


def gateway_notes(report: ReplicationReport, pairs: list[LinkPair]) -> list[str]:
    """B's RCIP gateway on a port whose peer address is on the same network: checkrclink's server routes
    the test through that gateway anyway (live 2026-11-03), and a gateway that cannot reach A fails it."""
    b_port = {p.nsp: p for p in report.peer.rcip_ports}
    b_name = report.peer.name or "B"
    notes = []
    for pair in pairs:
        port = b_port.get(pair.nsp_b)
        if port and port.gateway not in ("", "-", "0.0.0.0") and same_network(port, pair.ip_a):
            notes.append(f"{b_name} {pair.nsp_b} has gateway {port.gateway}, although {pair.ip_a} is on the port's own "
                         "network. The link test is sent through that gateway; if the gateway cannot reach the other "
                         "array, the test reports 100 % pings lost.")
    return notes


def run_link_check(
    array: EndpointCreds,
    replication: ReplicationIntent,
    report: ReplicationReport,
    *,
    duration_s: int = LINK_CHECK_TIME_DEFAULT,
    cli_factory: Callable = make_array_cli,
    progress: Callable[[str], None] | None = None,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
    sleep: Callable[[float], None] = time.sleep,
) -> LinkCheck:
    """R2 on every pair, in order; the stops run whatever happened before them. Then the links are read
    again on both arrays: a link that was Up before and stays Down is an error, never a pass."""
    say = progress or (lambda _m: None)
    pairs, unchecked = plan_pairs(report)
    check = LinkCheck(at=now().isoformat(timespec="seconds"), duration_s=duration_s, unchecked=unchecked,
                      modes=sorted({row.mode for row in replication.protections}))
    if not pairs:
        check.error = unchecked[0] if unchecked else "No link to check."
        return check
    check.notes.extend(gateway_notes(report, pairs))
    a_name = report.primary.name or "A"
    b_name = report.peer.name or "B"
    try:
        with cli_factory(replication.peer) as b_cli, cli_factory(array) as a_cli:
            for pair in pairs:
                check.results.append(_check_pair(pair, a_cli, b_cli, a_name, b_name, duration_s, say, report))
            say("Reading the Remote Copy links again on both arrays")
            broken = _links_still_down(report, a_cli, b_cli, sleep)
            if broken:
                check.error = _broken_links_error(broken, report, pairs)
    except ArrayCliError as exc:
        check.error = str(exc)
    return check


def _up_links(cli, side_links) -> set[tuple[str, str, str]]:
    """(target, n:s:p, address) of the outbound links `cli`'s array reports Up now."""
    now = {(link.target, link.nsp, link.address) for link in parse_showrcopy(cli.run("showrcopy links"))["links"]
           if link.up and not link.inbound}
    return {key for key in side_links if key in now}


def _links_still_down(report: ReplicationReport, a_cli, b_cli, sleep) -> list[str]:
    """Links that were Up in the preview's read and are not Up again within LINKS_SETTLE_S."""
    sides = [(report.primary.name or "A", a_cli, {(x.target, x.nsp, x.address) for x in report.primary.links if x.up and not x.inbound}),
             (report.peer.name or "B", b_cli, {(x.target, x.nsp, x.address) for x in report.peer.links if x.up and not x.inbound})]
    waited = 0.0
    while True:
        down = [f"{name} {nsp} → {addr}" for name, cli, before in sides for (_t, nsp, addr) in sorted(before - _up_links(cli, before))]
        if not down or waited >= LINKS_SETTLE_S:
            return down
        sleep(LINKS_POLL_S)
        waited += LINKS_POLL_S


def _broken_links_error(broken: list[str], report: ReplicationReport, pairs: list[LinkPair]) -> str:
    b_name = report.peer.name or "B"
    ports = ", ".join(sorted({p.nsp_b for p in pairs}))
    return (f"After the link check these Remote Copy links are Down, and they were Up before it: {'; '.join(broken)}. "
            f"The test server on {b_name} added a route to the other array and stopping it did not remove the route. "
            f"On {b_name}, for each of {ports}, run `controlport rcip state down -f <port>` and then "
            "`controlport rcip state up -f <port>` (the port keeps its address), wait for the links to show Up, then "
            "check again. Replication was not configured.")


def _check_pair(pair: LinkPair, a_cli, b_cli, a_name: str, b_name: str, duration_s: int, say,
                report: ReplicationReport | None = None) -> LinkCheckResult:
    result = LinkCheckResult(pair=pair)
    route_via = ""
    try:
        # a server left by an interrupted check runs for 48 h; a stop with nothing running is harmless
        _quiet(b_cli, f"checkrclink stopserver {pair.nsp_b}")
        say(f"Starting the test server on {b_name} {pair.nsp_b}")
        server = b_cli.run_diagnostic(f"checkrclink startserver {pair.nsp_b} {pair.ip_a}")
        if _is_error(server):
            raise ArrayCliError(f"{b_name} refused the test server on {pair.nsp_b}: {server.strip().splitlines()[0]}")
        route = ROUTE_RE.search(server)
        if route and re.match(r"^\d+\.\d+\.\d+\.\d+$", route.group(2)):
            route_via = route.group(2)
        say(f"Measuring latency {a_name} {pair.nsp_a} → {pair.ip_b} …")
        out = a_cli.run_diagnostic(f"checkrclink startclient {pair.nsp_a} {pair.ip_b} {duration_s}",
                                   until=UNTIL, timeout=LATENCY_WAIT_S)
        result.output = out
        if _is_error(out):
            raise ArrayCliError(f"{a_name} refused the test client on {pair.nsp_a}: {out.strip().splitlines()[0]}")
        result.latency_ms, result.pings_lost_pct = parse_client_output(out)
        if result.latency_ms is None and result.pings_lost_pct is not None and result.pings_lost_pct >= 100:
            why = (f"No reply: {a_name} {pair.nsp_a} sent the test to {pair.ip_b} and every ping was lost.")
            if route_via:
                why += (f" {b_name} routed its answers through gateway {route_via}"
                        + (f", although {pair.ip_a} is on the port's own network" if _same_net_b(report, pair) else "")
                        + f"; if that gateway cannot reach {a_name}, clear it on {pair.nsp_b} "
                          "(`controlport rcip gw` is not needed when both arrays are on one network) and check again.")
            raise ArrayCliError(why)
        if result.latency_ms is None:
            raise ArrayCliError(f"The client on {a_name} {pair.nsp_a} printed no latency within {LATENCY_WAIT_S:g} s.")
    except ArrayCliError as exc:
        result.status, result.detail = "failed", str(exc)
    finally:
        say(f"Stopping the client on {a_name}")
        _quiet(a_cli, f"checkrclink stopclient {pair.nsp_a}")
        say(f"Stopping the server on {b_name}")
        _quiet(b_cli, f"checkrclink stopserver {pair.nsp_b}")
    return result


def _same_net_b(report: ReplicationReport | None, pair: LinkPair) -> bool:
    port = next((p for p in report.peer.rcip_ports if p.nsp == pair.nsp_b), None) if report else None
    return bool(port and same_network(port, pair.ip_a))


def _quiet(cli, command: str) -> None:
    try:
        cli.run_diagnostic(command)
    except ArrayCliError:
        pass


def _is_error(text: str) -> bool:
    return text.lstrip().lower().startswith("error")
