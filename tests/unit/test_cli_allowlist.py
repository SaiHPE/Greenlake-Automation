"""SPEC-026 R1 and LESSONS 46: a command joins the read allowlist only after every option its captured
`help` offers has been read, and none of them acts.

Reads only the fixtures: the array's own help pages in `tests/fixtures/handover/<array>/help_<command>.txt`,
captured read-only on rack13 (OS 10.6.0), D22U27 (10.5.0), E18U31 (10.5.60) and VZ (10.5.51). An option
a later OS adds fails here until someone reads its help and either adds it to the reviewed list below
(it filters, windows, sorts or formats) or refuses it in the client. The allowlist pins themselves join
this file when the four commands are added (work packet BL-24, step 2). `srstatrcvv` is reviewed here
but stays off the allowlist until a started Remote Copy group is captured (ADR 0019).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

HANDOVER = Path(__file__).resolve().parents[1] / "fixtures" / "handover"
ARRAYS = ("rack13", "D22U27", "E18U31", "VZ")

# What each System Reporter report option does, from the captured help. None of them acts.
_SRSTAT = {
    "-attime": "formats: one row per group at one time, instead of rows over time",
    "-btsecs": "windows: the report's begin time",
    "-etsecs": "windows: the report's end time",
    "-hires": "windows: 5-minute samples",
    "-hourly": "windows: hourly samples",
    "-daily": "windows: daily samples",
    "-summary": "formats: min, avg, max or percentile rows instead of samples",
    "-groupby": "formats: one row per node, port, volume or group",
    "-compareby": "filters: only the top or bottom N objects",
    "-sortcol": "sorts: by a column",
}

# The reviewed read-only options, per command. Every reason starts with what the option does.
READ_ONLY_OPTIONS: dict[str, dict[str, str]] = {
    "showalert": {
        "-n": "filters: New alerts only (the default)",
        "-a": "filters: acknowledged alerts only",
        "-f": "filters: fixed alerts only",
        "-all": "filters: every customer alert",
        "-d": "formats: detailed blocks",
        "-oneline": "formats: one line per alert",
        "-svc": "filters: service alerts only",
        "-wide": "formats: message text not truncated",
    },
    "srstatcpu": dict(_SRSTAT),
    "srstatport": {
        **_SRSTAT,
        "-port_type": "filters: ports of the given types",
        "-both": "filters: control and data transfers",
        "-ctl": "filters: control transfers only",
        "-data": "filters: data transfers only (the default)",
    },
    "srstatvv": {
        **_SRSTAT,
        "-usr_cpg": "filters: volumes whose user space is in the given CPGs",
        "-prov": "filters: volumes of the given provisioning types",
    },
    "srstatrcvv": {
        **_SRSTAT,
        "-vv": "filters: the given volumes or volume sets",
        "-target": "filters: the given Remote Copy targets",
        "-mode": "filters: the given target modes",
        "-group": "filters: the given Remote Copy groups",
    },
}
_WHAT = ("filters:", "windows:", "sorts:", "formats:")

_OPTIONS_SECTION = re.compile(r"^OPTIONS\n(?P<body>.*?)^[A-Z]", re.MULTILINE | re.DOTALL)
_OPTION_LINE = re.compile(r"^ {4}(-\w.*)$")   # an option starts a line indented four spaces
_OPTION_NAME = re.compile(r"^-\w+$")


def help_options(text: str) -> set[str]:
    """The option names in a `help` page's OPTIONS section. Alternatives share a line
    (`-both | -ctl | -data`); an argument follows in angle brackets (`-compareby <top|bottom>,...`)."""
    section = _OPTIONS_SECTION.search(text)
    assert section, "no OPTIONS section: not a help page this test can read"
    names: set[str] = set()
    for line in section.group("body").splitlines():
        m = _OPTION_LINE.match(line)
        if not m:
            continue
        for part in m.group(1).split("<", 1)[0].split("|"):
            name = part.strip()
            assert _OPTION_NAME.match(name), f"unexpected option line: {line!r}"
            names.add(name)
    return names


def _help(command: str, array: str) -> str:
    return (HANDOVER / array / f"help_{command}.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize("array", ARRAYS)
@pytest.mark.parametrize("command", sorted(READ_ONLY_OPTIONS))
def test_every_option_in_the_captured_help_is_reviewed_read_only(command, array):
    unreviewed = help_options(_help(command, array)) - READ_ONLY_OPTIONS[command].keys()
    assert not unreviewed, (
        f"{command} on {array} offers {sorted(unreviewed)}: read its help; add each to the reviewed "
        "list if it only filters, windows, sorts or formats, or refuse it in the client (LESSONS 46)"
    )


@pytest.mark.parametrize("command", sorted(READ_ONLY_OPTIONS))
def test_the_reviewed_list_is_exactly_what_the_arrays_offer(command):
    offered = set().union(*(help_options(_help(command, a)) for a in ARRAYS))
    assert offered == READ_ONLY_OPTIONS[command].keys()


@pytest.mark.parametrize("array", ARRAYS)
@pytest.mark.parametrize("command", sorted(READ_ONLY_OPTIONS))
def test_any_role_may_run_it(command, array):
    authority = re.search(r"^AUTHORITY\n\s+(.+)$", _help(command, array), re.MULTILINE)
    assert authority and authority.group(1).strip() == "Any role in the system"


def test_every_reviewed_option_says_what_it_does():
    for command, options in READ_ONLY_OPTIONS.items():
        for option, what in options.items():
            assert what.startswith(_WHAT), f"{command} {option}: {what!r}"


def test_an_option_that_acts_fails_the_review():
    """The check above can fail: an acting option added to a real help page is caught."""
    text = _help("showalert", "rack13").replace(
        "    -d\n", "    -rescan\n        Rescans the ports.\n\n    -d\n", 1,
    )
    assert help_options(text) - READ_ONLY_OPTIONS["showalert"].keys() == {"-rescan"}


def test_alternatives_on_one_line_are_each_read():
    assert {"-both", "-ctl", "-data"} <= help_options(_help("srstatport", "VZ"))
