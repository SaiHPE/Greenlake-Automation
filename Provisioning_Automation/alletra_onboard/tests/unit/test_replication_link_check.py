"""SPEC-020 — the link check: pairs from the read (R1), the checkrclink sequence and its allowlist
(R2), the parsed result (R3), the gate and the operator's option (R4), the as-built paragraph (R6)."""

from datetime import UTC, datetime

import pytest

from alletra_onboard.adapters.array import cli_client
from alletra_onboard.adapters.array.cli_client import (
    ArrayCliClient,
    ArrayCliError,
    diagnostic_refusal,
    refusal,
)
from alletra_onboard.application.replication import link_check
from alletra_onboard.application.replication.plan import check
from alletra_onboard.domain.replication import (
    LinkCheck,
    LinkCheckResult,
    LinkPair,
)
from tests.unit.test_replication_plan import _creds, _intent, _views

_RC_FIXTURES = __import__("pathlib").Path(__file__).resolve().parents[1] / "fixtures" / "rc_pair"

# The client's output as the array prints it (screenshot 2026-10-12), up to where the tool stops it.
CLIENT_OUTPUT = """Running Client Side
Running link test on:  4:5:4
Test length (secs):    600
Destination Addr:      127.127.202.86
Local IP Addr:         127.127.220.29
Local Device name:     fcnet1

-----------------------------------------------------------
Measuring link latency
-----------------------------------------------------------

Average measured latency: 200 ms
Pings Lost:               0 %

-----------------------------------------------------------
Starting throughput test, from 4:5:4 -> 127.127.202.86
"""
SERVER_OUTPUT = """Starting Server
Test length (secs):     172800
Running link test on:   4:5:4
Local IP Addr:          127.127.202.86
Local Device name:      FCNET
"""


# ------------------------------------------------------------------ R1: the pairs

def test_pairs_come_from_the_links_on_a_and_the_ports_on_b():
    a, b = _views()
    report = check(a, b, _intent())
    pairs, unchecked = link_check.plan_pairs(report)
    assert unchecked == []
    assert [(p.nsp_a, p.ip_a, p.nsp_b, p.ip_b) for p in pairs] == [
        ("0:4:3", "10.54.122.92", "0:4:3", "10.54.154.192"),
        ("1:4:3", "10.54.122.93", "1:4:3", "10.54.154.193"),
    ]


def test_a_link_whose_address_no_peer_port_carries_is_listed_not_checked():
    a, b = _views()
    report = check(a, b, _intent())
    report.peer.rcip_ports = [p for p in report.peer.rcip_ports if p.ip != "10.54.154.193"]
    pairs, unchecked = link_check.plan_pairs(report)
    assert [p.nsp_a for p in pairs] == ["0:4:3"]
    assert unchecked == ["A 1:4:3 → 10.54.154.193: no RCIP port on B carries 10.54.154.193."]


def test_no_partnership_means_nothing_to_measure():
    a, b = _views(b_overrides={"showport -rcip": "N:S:P State HwAddr IPAddr Netmask Gateway MTU Rate\n0:4:3 ready 00 10.9.9.1 255.255.255.0 - 1500 10Gbps\n"})
    pairs, unchecked = link_check.plan_pairs(check(a, b, _intent()))
    assert pairs == [] and "No Remote Copy partnership" in unchecked[0]


def test_parse_client_output_on_the_real_capture():
    # D22U27 0:4:3 -> its own 1:4:3, 2026-10-12 (tests/fixtures/rc_pair/README.md): an MTU phase follows the latency.
    from pathlib import Path
    text = (Path(__file__).resolve().parents[1] / "fixtures" / "rc_pair" / "D22U27" / "checkrclink_startclient.txt").read_text(encoding="utf-8")
    assert link_check.parse_client_output(text) == (0.044, 0.0)
    import re
    assert re.search(link_check.UNTIL, text)
    assert text.index("Pings Lost") < text.index("Starting max MTU test") < text.index("Starting throughput test")


# ------------------------------------------------------------------ R2: the allowlist of its own

@pytest.mark.parametrize("command", [
    "checkrclink startserver 0:4:3 10.54.122.92",
    "checkrclink stopserver 0:4:3",
    "checkrclink startclient 0:4:3 10.54.154.192 600",
    "checkrclink startclient 0:4:3 10.54.154.192 300",
    "checkrclink stopclient 1:4:3",
])
def test_the_four_checkrclink_forms_may_run_and_only_through_run_diagnostic(command):
    assert diagnostic_refusal(command) is None
    assert refusal(command) == "refused: 'checkrclink' is not a read-only show command"   # the console cannot


def test_the_rcip_ping_may_run_only_through_run_diagnostic():
    """SPEC-020 R2a: ICMP echo from one RCIP port; it changes nothing. The console still cannot send it."""
    assert diagnostic_refusal("controlport rcip ping -c 10 10.93.18.19 0:4:4") is None
    assert diagnostic_refusal("controlport rcip ping -c 20 10.93.18.19 0:4:4") is None
    assert refusal("controlport rcip ping -c 10 10.93.18.19 0:4:4") == "refused: 'controlport' is not a read-only show command"


@pytest.mark.parametrize("command, why", [
    ("controlport rcip ping -c 0 10.93.18.19 0:4:4", "ping count must be 1 to 20"),
    ("controlport rcip ping -c 21 10.93.18.19 0:4:4", "ping count must be 1 to 20"),
    ("controlport rcip ping 10.93.18.19 0:4:4", "may run here"),                          # no count: pings forever
    ("controlport rcip ping -c 10 0:4:4 10.93.18.19", "may run here"),
    ("controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4", "may run here"),         # a write stays out
    ("controlport rcip gw -f 10.93.18.1 0:4:4", "may run here"),
    ("controlport rcip state down -f 0:1:1", "may run here"),
    ("controlport rcip ping -c 10 10.93.18.19 0:4:4; removevv x", "forbidden shell metacharacter"),
])
def test_any_other_controlport_is_refused(command, why):
    assert why in diagnostic_refusal(command)


@pytest.mark.parametrize("command, why", [
    ("checkrclink startclient 0:4:3 10.54.154.192 60", "time must be 300 to 172800"),
    ("checkrclink startclient 0:4:3 10.54.154.192 172801", "time must be 300 to 172800"),
    ("checkrclink startclient 0:4:3 10.54.154.192", "only 'checkrclink startserver"),
    ("checkrclink startserver 0:4:3 peer.example", "only 'checkrclink startserver"),
    ("checkrclink portconn 0:4:3", "only 'checkrclink startserver"),
    ("checkrclink startserver 0:4:3 10.54.122.92; removevv x", "forbidden shell metacharacter"),
    ("removevv x", "only 'checkrclink startserver"),
    ("showsys", "only 'checkrclink startserver"),
])
def test_anything_else_is_refused_with_a_sentence(command, why):
    assert why in diagnostic_refusal(command)


class _Channel:
    """A paramiko channel that prints the client's output in pieces and then blocks (the throughput test)."""

    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks, self.closed, self.command = list(chunks), False, None

    def settimeout(self, _s):
        pass

    def exec_command(self, command):
        self.command = command

    def recv_ready(self):
        return bool(self.chunks)

    def recv(self, _n):
        return self.chunks.pop(0) if self.chunks else b""

    def exit_status_ready(self):
        return False

    def close(self):
        self.closed = True


class _Transport:
    def __init__(self, channel):
        self.channel = channel

    def open_session(self):
        return self.channel


class _Ssh:
    def __init__(self, channel):
        self.channel = channel

    def get_transport(self):
        return _Transport(self.channel)


def test_run_diagnostic_reads_until_the_latency_and_closes_the_channel(monkeypatch):
    monkeypatch.setattr(cli_client, "time", _FastTime())
    head, tail = CLIENT_OUTPUT.split("Average measured latency")
    channel = _Channel([head.encode(), b"Average measured latency" + tail.encode()])
    cli = ArrayCliClient("10.64.122.99", "3paradm", "pw")
    cli._client = _Ssh(channel)
    out = cli.run_diagnostic("checkrclink startclient 0:4:3 10.54.154.192 600", until=link_check.UNTIL, timeout=5)
    assert channel.command == "checkrclink startclient 0:4:3 10.54.154.192 600"
    assert channel.closed and "Pings Lost:               0 %" in out
    assert link_check.parse_client_output(out) == (200.0, 0.0)


def test_run_diagnostic_gives_up_when_no_latency_is_printed(monkeypatch):
    monkeypatch.setattr(cli_client, "time", _FastTime())
    channel = _Channel([b"Running Client Side\n"])
    cli = ArrayCliClient("10.64.122.99", "3paradm", "pw")
    cli._client = _Ssh(channel)
    out = cli.run_diagnostic("checkrclink startclient 0:4:3 10.54.154.192 600", until=link_check.UNTIL, timeout=0.5)
    assert channel.closed and link_check.parse_client_output(out) == (None, None)


def test_run_diagnostic_refuses_before_touching_the_array():
    cli = ArrayCliClient("10.64.122.99", "3paradm", "pw")
    cli._client = object()      # any exec would blow up
    with pytest.raises(ArrayCliError, match="time must be 300 to 172800"):
        cli.run_diagnostic("checkrclink startclient 0:4:3 10.54.154.192 60")


class _FastTime:
    """monotonic() that advances a little per call so the until-loop's deadline is reached without sleeping."""

    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        self.now += 0.1
        return self.now

    def sleep(self, _s) -> None:
        self.now += 0.2


# ------------------------------------------------------------------ R2/R3: the sequence on a fake pair

class _Cli:
    def __init__(self, host: str, log: list, *, server_answer: str = SERVER_OUTPUT, client_answer: str = CLIENT_OUTPUT,
                 links_answers: dict[str, list[str]] | None = None, ping_answer: str = "") -> None:
        self.host, self.log, self.server_answer, self.client_answer = host, log, server_answer, client_answer
        self.ping_answer = ping_answer
        # `showrcopy links` read after the check: the array's own capture unless a test gives a sequence
        self.links_answers = (links_answers or {}).get(host)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def run(self, command: str, timeout=None) -> str:
        self.log.append((self.host, command, False))
        assert command == "showrcopy links", command
        if self.links_answers:
            return self.links_answers.pop(0) if len(self.links_answers) > 1 else self.links_answers[0]
        array = {"10.64.122.99": "D22U27", "10.64.154.190": "E18U31"}[self.host]
        return (_RC_FIXTURES / array / "showrcopy_links.txt").read_text(encoding="utf-8")

    def run_diagnostic(self, command: str, *, until=None, timeout=None) -> str:
        self.log.append((self.host, command, until is not None))
        if command.startswith("checkrclink startserver"):
            return self.server_answer
        if command.startswith("checkrclink startclient"):
            return self.client_answer
        if command.startswith("controlport rcip ping"):
            return self.ping_answer
        return ""


def _factory(log: list, **kw):
    return lambda creds: _Cli(creds.host, log, **kw)


def _report():
    a, b = _views()
    return check(a, b, _intent())


_NOW = lambda: datetime(2026, 10, 12, 7, 0, tzinfo=UTC)


def test_the_sequence_per_pair_is_stop_start_server_client_until_latency_stop_client_stop_server():
    log: list = []
    said: list[str] = []
    result = link_check.run_link_check(_creds("10.64.122.99"), _intent().model_copy(), _report(),
                                       cli_factory=_factory(log), progress=said.append, now=_NOW)
    assert result.error is None and result.measured and result.at == "2026-10-12T07:00:00+00:00"
    assert [(r.pair.nsp_a, r.latency_ms, r.pings_lost_pct, r.status) for r in result.results] == [
        ("0:4:3", 200.0, 0.0, "measured"), ("1:4:3", 200.0, 0.0, "measured"),
    ]
    assert log[:5] == [
        ("10.64.154.190", "checkrclink stopserver 0:4:3", False),
        ("10.64.154.190", "checkrclink startserver 0:4:3 10.54.122.92", False),
        ("10.64.122.99", "checkrclink startclient 0:4:3 10.54.154.192 600", True),
        ("10.64.122.99", "checkrclink stopclient 0:4:3", False),
        ("10.64.154.190", "checkrclink stopserver 0:4:3", False),
    ]
    assert log[5][1] == "checkrclink stopserver 1:4:3" and len(log) == 12
    # 2026-11-03: the links are read again on both arrays after the last stop (a Primera kept a route).
    assert log[10:] == [("10.64.122.99", "showrcopy links", False), ("10.64.154.190", "showrcopy links", False)]
    assert said == [
        "Starting the test server on AlletraMP_E18U31 0:4:3", "Measuring latency AlletraMP_D22U27 0:4:3 → 10.54.154.192 …",
        "Stopping the client on AlletraMP_D22U27", "Stopping the server on AlletraMP_E18U31",
        "Starting the test server on AlletraMP_E18U31 1:4:3", "Measuring latency AlletraMP_D22U27 1:4:3 → 10.54.154.193 …",
        "Stopping the client on AlletraMP_D22U27", "Stopping the server on AlletraMP_E18U31",
        "Reading the Remote Copy links again on both arrays",
    ]
    assert result.modes == ["sync"] and result.worst_ms == 200.0 and result.over_limit() == ["sync"]
    assert "Starting throughput test" in result.results[0].output


def test_a_refused_server_fails_the_pair_and_the_stops_still_run():
    log: list = []
    result = link_check.run_link_check(_creds("10.64.122.99"), _intent(), _report(),
                                       cli_factory=_factory(log, server_answer="Error: Port 0:4:3 is not an RCIP port\n"), now=_NOW)
    assert result.measured is False and all(r.status == "failed" for r in result.results)
    assert result.results[0].detail == "AlletraMP_E18U31 refused the test server on 0:4:3: Error: Port 0:4:3 is not an RCIP port"
    assert [c for h, c, _ in log if h == "10.64.122.99"] == ["checkrclink stopclient 0:4:3", "checkrclink stopclient 1:4:3", "showrcopy links"]
    assert log[-3] == ("10.64.154.190", "checkrclink stopserver 1:4:3", False)


def test_a_client_that_prints_no_latency_fails_the_pair():
    log: list = []
    result = link_check.run_link_check(_creds("10.64.122.99"), _intent(), _report(),
                                       cli_factory=_factory(log, client_answer="Running Client Side\n"), now=_NOW)
    assert result.results[0].status == "failed" and "printed no latency within 120 s" in result.results[0].detail
    assert result.worst_ms is None and result.over_limit() == []


def test_within_the_limit_is_told_apart_from_over_it():
    pair = LinkPair(nsp_a="0:4:3", ip_a="a", nsp_b="0:4:3", ip_b="b")
    fast = LinkCheck(results=[LinkCheckResult(pair=pair, latency_ms=0.4, pings_lost_pct=0.0)], modes=["sync", "async"])
    slow = LinkCheck(results=[LinkCheckResult(pair=pair, latency_ms=12.0, pings_lost_pct=0.0)], modes=["sync", "async"])
    assert fast.over_limit() == [] and slow.over_limit() == ["sync"]
    assert LinkCheck(results=[LinkCheckResult(pair=pair, latency_ms=250.0)], modes=["async"]).over_limit() == ["async"]


def _fixture(name: str) -> str:
    """A capture from the rcip_pair fixtures, without its '# command' header line."""
    text = (_RC_FIXTURES.parent / "rcip_pair" / name).read_text(encoding="utf-8")
    return text.split("\n", 1)[1] if text.startswith("#") else text


def test_same_network_reads_the_primera_port_as_the_lab_set_it():
    from alletra_onboard.application.replication.read import parse_showport_rcip

    ports = {p.nsp: p for p in parse_showport_rcip(_fixture("showport_rcip_primera_gateway.txt"))}
    assert ports["0:1:1"].gateway == "10.93.18.1"
    assert link_check.same_network(ports["0:1:1"], "10.93.18.11")          # the Alletra's RCIP address
    assert not link_check.same_network(ports["0:1:1"], "10.54.122.92")


def _report_with_gateway_on_b():
    report = _report()
    for port in report.peer.rcip_ports:          # E18U31's ports, widened so A's addresses are on their network
        port.netmask, port.gateway = "255.255.0.0", "10.54.159.254"
    return report


def test_a_gateway_on_b_for_a_peer_on_its_own_network_is_noted_before_the_check():
    result = link_check.run_link_check(_creds("10.64.122.99"), _intent(), _report_with_gateway_on_b(),
                                       cli_factory=_factory([]), now=_NOW, sleep=lambda s: None)
    assert result.error is None and len(result.notes) == 2
    assert result.notes[0].startswith("AlletraMP_E18U31 0:4:3 has gateway 10.54.159.254, although 10.54.122.92 is on the port's own network")


def test_no_reply_names_the_gateway_the_server_routed_through():
    """Live 2026-11-03: the Primera's server added `10.93.18.11 -> 10.93.18.1`; the Alletra's client lost
    every ping and printed no latency. The pair's detail says so, not "no latency within 120 s"."""
    result = link_check.run_link_check(
        _creds("10.64.122.99"), _intent(), _report_with_gateway_on_b(), now=_NOW, sleep=lambda s: None,
        cli_factory=_factory([], server_answer=_fixture("checkrclink_startserver_gateway.txt"),
                             client_answer=_fixture("checkrclink_startclient_lost.txt")))
    detail = result.results[0].detail
    assert result.results[0].status == "failed" and result.results[0].pings_lost_pct == 100.0
    assert detail.startswith("No reply: AlletraMP_D22U27 0:4:3 sent the test to 10.54.154.192 and every ping was lost.")
    assert "routed its answers through gateway 10.93.18.1, although 10.54.122.92 is on the port's own network" in detail
    assert "printed no latency" not in detail


def test_a_latency_line_with_no_number_is_measured_with_ping_and_says_so():
    """Live 2026-11-06 through the lab router (it answered every ping twice): 0 % lost, MTU 1500 passed,
    and the client printed `Average measured latency: min ms`. SPEC-020 R2a: after the stops, ping the
    same address from the same port and take the average round trip."""
    log: list = []
    result = link_check.run_link_check(
        _creds("10.64.122.99"), _intent(), _report(), now=_NOW, sleep=lambda s: None,
        cli_factory=_factory(log, client_answer=_fixture("checkrclink_startclient_routed_no_number.txt"),
                             ping_answer=_fixture("controlport_rcip_ping_routed_redirect.txt")))
    r = result.results[0]
    assert (r.status, r.latency_ms, r.pings_lost_pct) == ("measured", 0.932, 0.0)
    assert r.detail == ("Measured with ping: AlletraMP_D22U27's link test printed 'Average measured latency: min ms' "
                        "with no number, so the tool sent 10 pings from 0:4:3 to 10.54.154.192; the average round trip "
                        "is 0.932 ms.")
    assert "$ controlport rcip ping -c 10 10.54.154.192 0:4:3" in r.output
    first = [c for _h, c, _u in log][:6]
    assert first == ["checkrclink stopserver 0:4:3", "checkrclink startserver 0:4:3 10.54.122.92",
                     "checkrclink startclient 0:4:3 10.54.154.192 600", "checkrclink stopclient 0:4:3",
                     "checkrclink stopserver 0:4:3", "controlport rcip ping -c 10 10.54.154.192 0:4:3"]   # after the stops
    assert result.measured is True and result.error is None


def test_a_ping_that_loses_any_reply_leaves_the_pair_unmeasured():
    lossy = "10 packets transmitted, 9 received, 10% packet loss, time 9010ms\nrtt min/avg/max/mdev = 0.05/0.06/0.09/0.01 ms\n"
    result = link_check.run_link_check(
        _creds("10.64.122.99"), _intent(), _report(), now=_NOW, sleep=lambda s: None,
        cli_factory=_factory([], client_answer=_fixture("checkrclink_startclient_routed_no_number.txt"), ping_answer=lossy))
    r = result.results[0]
    assert (r.status, r.latency_ms) == ("failed", None)
    assert r.detail.endswith("printed 'Average measured latency: min ms' with no number, and the ping that replaces it "
                             "lost 10 % of 10. Check the link and check again.")
    assert result.measured is False


def _links_down(text: str) -> str:
    return "\n".join(line.replace(" Up ", " Down ") if line.startswith("AlletraMP_E18U31") else line for line in text.splitlines())


def test_links_left_down_after_the_check_are_an_error_with_the_way_back():
    """Live 2026-11-03: after the check every RCIP link was Down (the Primera kept the test route)."""
    up = (_RC_FIXTURES / "D22U27" / "showrcopy_links.txt").read_text(encoding="utf-8")
    slept: list[float] = []
    result = link_check.run_link_check(
        _creds("10.64.122.99"), _intent(), _report(), now=_NOW, sleep=slept.append,
        cli_factory=_factory([], links_answers={"10.64.122.99": [_links_down(up)]}))
    assert all(r.status == "measured" for r in result.results) and result.measured is False
    assert result.error.startswith("After the link check these Remote Copy links are Down, and they were Up before it: "
                                   "AlletraMP_D22U27 0:4:3 → 10.54.154.192; AlletraMP_D22U27 1:4:3 → 10.54.154.193.")
    assert "`controlport rcip state down -f <port>`" in result.error and "Replication was not configured." in result.error
    assert sum(slept) == link_check.LINKS_SETTLE_S                         # waited before calling it broken


def test_links_back_up_within_the_settle_time_are_not_an_error():
    up = (_RC_FIXTURES / "D22U27" / "showrcopy_links.txt").read_text(encoding="utf-8")
    slept: list[float] = []
    result = link_check.run_link_check(
        _creds("10.64.122.99"), _intent(), _report(), now=_NOW, sleep=slept.append,
        cli_factory=_factory([], links_answers={"10.64.122.99": [_links_down(up), up]}))
    assert result.error is None and result.measured and slept == [link_check.LINKS_POLL_S]


# ------------------------------------------------------------------ R4: the gate is tested through the service
# (tests/unit/test_onboarding_service.py::test_replication_preview_reads_both_arrays_and_holds_the_plan and
# test_the_link_gate_refuses_without_a_check_and_over_the_limit_without_the_tick).


# ------------------------------------------------------------------ R6: the as-built paragraph

def test_the_as_built_states_the_measured_latency_and_the_operators_choice(tmp_path):
    from alletra_onboard.application.documents.asbuilt import generate_asbuilt
    from tests.unit.test_asbuilt_replication import _data, _read, _tab

    pair = {"nsp_a": "0:4:3", "ip_a": "10.54.122.92", "nsp_b": "0:4:3", "ip_b": "10.54.154.192"}
    checked = {"at": "2026-10-12T07:00:00+00:00", "duration_s": 600, "modes": ["sync"], "unchecked": [], "error": None,
               "results": [{"pair": pair, "status": "measured", "latency_ms": 12.0, "pings_lost_pct": 0.0, "detail": "", "output": ""}]}
    data = _data(replication_tab=_tab("sync"))
    data.link_check = checked
    data.replication_result = {**(data.replication_result or {}), "notes": [
        "Link check 2026-10-12T07:00:00+00:00: latency 12 ms on 1 link(s); over the 10 ms limit for sync — the operator accepted it and chose to continue."]}
    _, text = _read(generate_asbuilt(data, tmp_path / "a.docx")[0])
    assert "Link check" in text
    assert "worst latency 12 ms on 1 link(s); sync replication over RCIP needs 10 ms or less" in text
    assert "over HPE's limit for sync — the operator accepted the measured latency and continued." in text
    assert "A 0:4:3 (10.54.122.92) → B 0:4:3 (10.54.154.192)" in text and "12 ms" in text

    data.link_check = {**checked, "results": [{**checked["results"][0], "latency_ms": 0.4}]}
    data.replication_result = {**(data.replication_result or {}), "notes": []}
    _, text = _read(generate_asbuilt(data, tmp_path / "b.docx")[0])
    assert "worst latency 0.4 ms" in text and "within HPE's limit." in text
    assert "(ping)" not in text

    # SPEC-020 R2a: a latency measured with ping is marked, and the document says why
    data.link_check = {**checked, "results": [{**checked["results"][0], "latency_ms": 0.932,
                                               "detail": "Measured with ping: the link test printed no number."}]}
    _, text = _read(generate_asbuilt(data, tmp_path / "c.docx")[0])
    assert "0.932 ms (ping)" in text
    assert ("(ping): the array's link test printed its latency line with no number on that link, so the tool measured "
            "the average round trip with 10 pings from the same port to the same address.") in text
