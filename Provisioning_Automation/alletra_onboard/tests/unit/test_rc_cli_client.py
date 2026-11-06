"""ADR 0015 / BL-41 — the write-scoped SSH client for Remote Copy links and targets. Every form it
accepts is a command run live on 2026-11-03 (tests/fixtures/rcip_pair/rcip_setup_commands_2026-11-03.log)
or spelled exactly as both arrays' own help gives it (tests/fixtures/rcip_pair/help/)."""

import re
from pathlib import Path

import pytest

from alletra_onboard.adapters.array.cli_client import ArrayCliClient, ArrayCliError, refusal
from alletra_onboard.adapters.array.rc_cli_client import (
    ArrayRcCliClient,
    answered_error,
    rc_write_refusal,
)

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "rcip_pair"
LIVE = (FIX / "rcip_setup_commands_2026-11-03.log").read_text(encoding="utf-8")
WRITES = ("controlport rcip addr", "controlport rcip ping", "startrcopy", "creatercopytarget")


def _live_writes() -> list[str]:
    return [m.group(1) for m in re.finditer(r"^\[[\d:]+\] \w+ [\d.]+ \$ (.+)$", LIVE, re.MULTILINE) if m.group(1).startswith(WRITES)]


def test_every_write_the_live_setup_ran_is_accepted_and_the_read_client_refuses_it():
    writes = _live_writes()
    assert writes == [
        "controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4",
        "controlport rcip addr -f 10.93.18.13 255.255.254.0 1:4:4",
        "controlport rcip ping -c 3 10.93.18.19 0:4:4",
        "controlport rcip ping -c 3 10.93.18.20 1:4:4",
        "startrcopy",
        "creatercopytarget PRIMERA630R11U22 IP 0:4:4:10.93.18.19 1:4:4:10.93.18.20",
        "creatercopytarget rack13-ARCUS IP 0:1:1:10.93.18.11 1:1:1:10.93.18.13",
    ]
    for command in writes:
        assert rc_write_refusal(command) is None, command
        assert refusal(command) is not None, command                      # ADR 0001's client stays read-only


@pytest.mark.parametrize("command", [
    "controlport rcip gw -f 10.93.18.1 0:1:1",
    "controlport rcip addr -f 10.93.18.11 23 0:4:4",
    "admitrcopylink PRIMERA630R11U22 0:4:4:10.93.18.19",
    "dismissrcopylink PRIMERA630R11U22 0:4:4:10.93.18.19 1:4:4:10.93.18.20",
    "removercopytarget PRIMERA630R11U22",
])
def test_the_rest_of_the_adr_list_is_accepted(command):
    assert rc_write_refusal(command) is None


@pytest.mark.parametrize("command, why", [
    ("controlport rcip addr 10.93.18.11 255.255.254.0 0:4:4", "only the Remote Copy link"),        # no -f: the array prompts
    ("controlport rcip delete -f 0:4:4", "only the Remote Copy link"),                             # undo is the operator's
    ("controlport rcip state down -f 0:1:1", "only the Remote Copy link"),
    ("controlport config iscsi 0:4:1", "only the Remote Copy link"),                               # never a port's role
    ("controlport offline 0:4:4", "only the Remote Copy link"),
    ("controlport rcip addr -f 10.93.18.300 255.255.254.0 0:4:4", "not a valid IPv4 address"),
    ("controlport rcip addr -f 10.93.18.11 33 0:4:4", "prefix length must be 1 to 32"),
    ("controlport rcip addr -f 10.93.18.11 0.0.0.255 0:4:4", "is not a netmask"),
    ("controlport rcip addr -f 10.93.18.11 0.0.0.0 0:4:4", "is not a netmask"),
    ("creatercopytarget PRIMERA630R11U22 FC 2FF70002AC02AC38 0:3:2:20320002AC02AC38", "only the Remote Copy link"),
    ("removercopytarget -cleargroups -f PRIMERA630R11U22", "only the Remote Copy link"),          # would remove groups
    ("stoprcopy -f -stopgroups -clear", "only the Remote Copy link"),
    ("removercopygroup -f zz_rc_vvs_rcg", "only the Remote Copy link"),
    ("startrcopy; removevv x", "forbidden shell metacharacter"),
    ("showsys", "only the Remote Copy link"),
])
def test_anything_else_is_refused_with_a_sentence(command, why):
    assert why in rc_write_refusal(command)


def test_the_syntax_the_tool_writes_is_the_one_both_arrays_document():
    for array in ("alletra", "primera"):
        controlport = (FIX / "help" / f"{array}_help_controlport.txt").read_text()
        assert "controlport rcip addr [-f] <IP_address> {<netmask>|<prefix_len>} <node:slot:port>" in controlport
        assert "controlport rcip ping [-c <count>" in controlport
        target = (FIX / "help" / f"{array}_help_creatercopytarget.txt").read_text()
        assert "creatercopytarget  [options] <target_name> IP [node:slot:port:IP_address...]" in target
        assert "admitrcopylink <target_name> <N:S:P:IP_address>..." in (FIX / "help" / f"{array}_help_admitrcopylink.txt").read_text()
        assert "removercopytarget [options] <target_name>" in (FIX / "help" / f"{array}_help_removercopytarget.txt").read_text()


def test_the_arrays_answers_read_as_success_or_refusal():
    assert not answered_error("Remote Copy interface change successful.\n")
    assert not answered_error("")                                                # startrcopy / creatercopytarget
    assert answered_error("Error: Link 0:4:3:10.54.154.192 appears to exist on another target.\n")


class _Exec:
    def __init__(self, answer: str) -> None:
        self.answer, self.commands = answer, []

    def exec_command(self, command, timeout=None):
        self.commands.append(command)
        out = type("S", (), {"read": lambda s: self.answer.encode()})()
        err = type("S", (), {"read": lambda s: b""})()
        return None, out, err


def test_write_refuses_before_sending_and_runs_what_is_allowed():
    client = ArrayRcCliClient("10.132.30.121", "3paradm", "pw")
    client._client = _Exec("Remote Copy interface change successful.\n")
    assert client.write("controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4").startswith("Remote Copy interface")
    with pytest.raises(ArrayCliError, match="only the Remote Copy link"):
        client.write("controlport rcip delete -f 0:4:4")
    assert client._client.commands == ["controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4"]
    assert not hasattr(ArrayCliClient, "write")                                  # the read client has no write path
