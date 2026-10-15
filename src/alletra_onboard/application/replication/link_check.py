"""SPEC-020: the latency between the two arrays, measured with `checkrclink` before replication.

R1 pairs every outbound RCIP link of A toward B with B's port; R2 runs the array's own link test
on each pair (server on B, client on A, read until the latency is printed, stop both); R3 is the
result. Nothing here changes either array's configuration.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import UTC, datetime

from alletra_onboard.adapters.array.cli_client import ArrayCliError
from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.domain.replication import (
    LINK_CHECK_TIME_DEFAULT,
    LinkCheck,
    LinkCheckResult,
    LinkPair,
    ReplicationIntent,
    ReplicationReport,
)
from alletra_onboard.domain.shared import EndpointCreds

#: The client prints these before its throughput test starts (screenshot 2026-10-12).
LATENCY_RE = re.compile(r"Average measured latency:\s*([\d.]+)\s*ms")
LOST_RE = re.compile(r"Pings Lost:\s*([\d.]+)\s*%")
#: Read the client's output until this line, then stop it (R2 step 3).
UNTIL = r"Pings Lost:\s*[\d.]+\s*%"
#: How long the latency phase may take before the pair counts as failed.
LATENCY_WAIT_S = 120.0

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


def run_link_check(
    array: EndpointCreds,
    replication: ReplicationIntent,
    report: ReplicationReport,
    *,
    duration_s: int = LINK_CHECK_TIME_DEFAULT,
    cli_factory: Callable = make_array_cli,
    progress: Callable[[str], None] | None = None,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> LinkCheck:
    """R2 on every pair, in order; the stops run whatever happened before them."""
    say = progress or (lambda _m: None)
    pairs, unchecked = plan_pairs(report)
    check = LinkCheck(at=now().isoformat(timespec="seconds"), duration_s=duration_s, unchecked=unchecked,
                      modes=sorted({row.mode for row in replication.protections}))
    if not pairs:
        check.error = unchecked[0] if unchecked else "No link to check."
        return check
    a_name = report.primary.name or "A"
    b_name = report.peer.name or "B"
    try:
        with cli_factory(replication.peer) as b_cli, cli_factory(array) as a_cli:
            for pair in pairs:
                check.results.append(_check_pair(pair, a_cli, b_cli, a_name, b_name, duration_s, say))
    except ArrayCliError as exc:
        check.error = str(exc)
    return check


def _check_pair(pair: LinkPair, a_cli, b_cli, a_name: str, b_name: str, duration_s: int, say) -> LinkCheckResult:
    result = LinkCheckResult(pair=pair)
    try:
        # a server left by an interrupted check runs for 48 h; a stop with nothing running is harmless
        _quiet(b_cli, f"checkrclink stopserver {pair.nsp_b}")
        say(f"Starting the test server on {b_name} {pair.nsp_b}")
        server = b_cli.run_diagnostic(f"checkrclink startserver {pair.nsp_b} {pair.ip_a}")
        if _is_error(server):
            raise ArrayCliError(f"{b_name} refused the test server on {pair.nsp_b}: {server.strip().splitlines()[0]}")
        say(f"Measuring latency {a_name} {pair.nsp_a} → {pair.ip_b} …")
        out = a_cli.run_diagnostic(f"checkrclink startclient {pair.nsp_a} {pair.ip_b} {duration_s}",
                                   until=UNTIL, timeout=LATENCY_WAIT_S)
        result.output = out
        if _is_error(out):
            raise ArrayCliError(f"{a_name} refused the test client on {pair.nsp_a}: {out.strip().splitlines()[0]}")
        result.latency_ms, result.pings_lost_pct = parse_client_output(out)
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


def _quiet(cli, command: str) -> None:
    try:
        cli.run_diagnostic(command)
    except ArrayCliError:
        pass


def _is_error(text: str) -> bool:
    return text.lstrip().lower().startswith("error")
