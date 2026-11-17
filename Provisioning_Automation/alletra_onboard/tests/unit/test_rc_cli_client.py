"""ADR 0015 / BL-41 — the write-scoped SSH client for Remote Copy links and targets. Every form it
accepts is a command run live on 2026-11-03 (tests/fixtures/rcip_pair/rcip_setup_commands_2026-11-03.log)
or spelled exactly as both arrays' own help gives it (tests/fixtures/rcip_pair/help/). ADR 0025
condition 3 (BL-58): it writes only on the ports, addresses and target of the plan it was built with."""

import re
from pathlib import Path

import pytest

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.array.cli_client import ArrayCliClient, ArrayCliError, refusal
from alletra_onboard.adapters.array.rc_cli_client import (
    UNBOUND,
    ArrayRcCliClient,
    RcPlanObjects,
    answered_error,
    rc_write_refusal,
)

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "rcip_pair"
LIVE = (FIX / "rcip_setup_commands_2026-11-03.log").read_text(encoding="utf-8")
WRITES = ("controlport rcip addr", "controlport rcip ping", "startrcopy", "creatercopytarget")


# The 2026-11-03 run's plan, per array: the only ports, addresses and target each client may write on
# (test_replication_partnership.py derives the same from the plan).
ALLETRA_OBJECTS = RcPlanObjects(ports=frozenset({"0:4:4", "1:4:4"}), addresses=frozenset({"10.93.18.11", "10.93.18.13"}),
                                peer_addresses=frozenset({"10.93.18.19", "10.93.18.20"}),
                                targets=frozenset({"PRIMERA630R11U22"}))
PRIMERA_OBJECTS = RcPlanObjects(ports=frozenset({"0:1:1", "1:1:1"}), addresses=frozenset({"10.93.18.19", "10.93.18.20"}),
                                peer_addresses=frozenset({"10.93.18.11", "10.93.18.13"}),
                                targets=frozenset({"rack13-ARCUS"}))


def _live_writes_by_array() -> list[tuple[str, str]]:
    found = re.finditer(r"^\[[\d:]+\] (\w+) [\d.]+ \$ (.+)$", LIVE, re.MULTILINE)
    return [(m.group(1), m.group(2)) for m in found if m.group(2).startswith(WRITES)]


def _live_writes() -> list[str]:
    return [command for _array, command in _live_writes_by_array()]


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
    # BL-51: allowed once and never sent by the tool; removal sets name them as text for the operator
    ("admitrcopylink PRIMERA630R11U22 0:4:4:10.93.18.19", "only the Remote Copy link"),
    ("dismissrcopylink PRIMERA630R11U22 0:4:4:10.93.18.19 1:4:4:10.93.18.20", "only the Remote Copy link"),
    ("removercopytarget PRIMERA630R11U22", "only the Remote Copy link"),
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


def _bound(objects: RcPlanObjects | None = ALLETRA_OBJECTS, answer: str = "") -> ArrayRcCliClient:
    client = ArrayRcCliClient("10.132.30.121", "3paradm", "pw", objects=objects)
    client._client = _Exec(answer)
    return client


@pytest.fixture
def recorded():
    got: list[dict] = []
    token = command_log.bind(got.append)
    yield got
    command_log.unbind(token)


def test_write_refuses_before_sending_and_runs_what_is_allowed():
    client = _bound(answer="Remote Copy interface change successful.\n")
    assert client.write("controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4").startswith("Remote Copy interface")
    with pytest.raises(ArrayCliError, match="only the Remote Copy link"):
        client.write("controlport rcip delete -f 0:4:4")
    assert client._client.commands == ["controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4"]
    assert not hasattr(ArrayCliClient, "write")                                  # the read client has no write path


# ------------------------------------------------------------------ ADR 0025 condition 3: the plan's objects only

def test_every_live_write_passes_a_client_bound_to_that_runs_plan_and_not_the_other_arrays():
    clients = {"alletra": _bound(ALLETRA_OBJECTS), "primera": _bound(PRIMERA_OBJECTS)}
    other = {"alletra": "primera", "primera": "alletra"}
    for array, command in _live_writes_by_array():
        clients[array].write(command)
        if command != "startrcopy":                                              # names no object
            assert clients[other[array]].write_refusal(command).startswith("refused: "), command
    assert clients["alletra"]._client.commands == [c for a, c in _live_writes_by_array() if a == "alletra"]
    assert clients["primera"]._client.commands == [
        "creatercopytarget rack13-ARCUS IP 0:1:1:10.93.18.11 1:1:1:10.93.18.13"]


WITH_GATEWAY = RcPlanObjects(ports=ALLETRA_OBJECTS.ports, addresses=ALLETRA_OBJECTS.addresses | {"10.93.18.1"},
                             peer_addresses=ALLETRA_OBJECTS.peer_addresses, targets=ALLETRA_OBJECTS.targets)


@pytest.mark.parametrize("command", [
    "controlport rcip gw -f 10.93.18.1 0:4:4",
    "controlport rcip ping 10.93.18.20 1:4:4",
])
def test_every_form_on_the_plans_objects_is_sent(command):
    client = _bound(WITH_GATEWAY)
    client.write(command)
    assert client._client.commands == [command]


@pytest.mark.parametrize("command, why", [
    ("controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:3", "refused: port 0:4:3 is not in the approved plan"),
    ("controlport rcip addr -f 10.93.18.12 255.255.254.0 0:4:4",
     "refused: address 10.93.18.12 is not one the approved plan sets on this array"),
    ("controlport rcip addr -f 10.93.18.19 255.255.254.0 0:4:4",                 # the peer's address, set here
     "refused: address 10.93.18.19 is not one the approved plan sets on this array"),
    ("controlport rcip gw -f 10.93.18.2 0:4:4", "refused: address 10.93.18.2 is not one the approved plan sets"),
    ("controlport rcip gw -f 10.93.18.1 1:1:1", "refused: port 1:1:1 is not in the approved plan"),
    ("controlport rcip ping -c 3 10.93.18.21 0:4:4", "refused: peer address 10.93.18.21 is not in the approved plan"),
    ("controlport rcip ping -c 3 10.93.18.19 0:4:3", "refused: port 0:4:3 is not in the approved plan"),
    ("creatercopytarget OTHER_ARRAY IP 0:4:4:10.93.18.19 1:4:4:10.93.18.20",
     "refused: target OTHER_ARRAY is not in the approved plan"),
    ("creatercopytarget PRIMERA630R11U22 IP 0:4:4:10.93.18.19 0:4:3:10.93.18.20",
     "refused: port 0:4:3 is not in the approved plan"),
    ("creatercopytarget PRIMERA630R11U22 IP 0:4:4:10.93.18.19 1:4:4:10.93.18.21",
     "refused: peer address 10.93.18.21 is not in the approved plan"),
])
def test_the_same_form_on_another_object_is_refused_recorded_and_never_sent(command, why, recorded):
    assert rc_write_refusal(command) is None                                     # well formed: only the object is wrong
    client = _bound(WITH_GATEWAY)
    with pytest.raises(ArrayCliError) as exc:
        client.write(command)
    assert str(exc.value).startswith(why)
    assert client._client.commands == []
    [entry] = recorded
    assert (entry["command"], entry["ok"], entry["write"], entry["result"]) == (command, False, True, str(exc.value))


def test_a_client_built_without_the_plans_objects_refuses_every_write(recorded):
    client = _bound(None)
    for command in [*_live_writes(), "removercopytarget PRIMERA630R11U22"]:
        with pytest.raises(ArrayCliError, match=UNBOUND):
            client.write(command)
    assert client._client.commands == []
    assert len(recorded) == len(_live_writes()) + 1 and all(not e["ok"] and e["result"] == UNBOUND for e in recorded)
    assert ArrayRcCliClient("10.132.30.121", "3paradm", "pw").write_refusal("startrcopy") == UNBOUND


def test_an_empty_plan_still_allows_only_startrcopy():
    client = _bound(RcPlanObjects())
    assert client.write_refusal("startrcopy") is None
    assert client.write_refusal("controlport rcip ping -c 3 10.93.18.19 0:4:4") == "refused: port 0:4:4 is not in the approved plan"
