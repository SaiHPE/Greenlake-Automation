"""ADR 0016 (accepted 2026-11-17, with the review's changes; follows ADR 0025) and SPEC-023 R3 — the
read allowlist gains `showsched`, and a write-scoped SSH client may run ONE form: `createsched -f` of a
`createsv -f` on one source, with an expiry and no lock. The command inside the quotes is checked too:
a schedule is a command the array runs later, so a check on the first word would let anything in.
Not built yet: every test here is expected to fail until the work packet's step that names it is done
(docs/workpackets/BL-21.md). The array's help is captured on four arrays: rack13-ARCUS (OS 10.6.0,
2026-11-16), D22U27, E18U31 and VZ (OS 10.5.x, 2026-11-17)."""

import re
from pathlib import Path

import pytest

from alletra_onboard.adapters.array.cli_client import refusal

FIX = Path(__file__).resolve().parents[1] / "fixtures"
CAPTURES = {"rack13_snap": "10.6.0", "d22u27_snap": "10.5.0", "e18u31_snap": "10.5.60", "vz_snap": "10.5.51"}
PATTERN = "@vvname@.@y@@m@@d@@H@@M@@S@"
GOOD = f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 0,4,8,12,16,20 * * *" zz_sn_vvs_snap'
NAME_31 = "zz_sn_" + "v" * 25
CLIENT = "BL-21 step 9A: the write client is not built yet"


@pytest.mark.xfail(reason="BL-21 step 7: showsched is not on the read allowlist yet", strict=True)
def test_showsched_is_on_the_read_allowlist_and_its_writes_are_not():
    from alletra_onboard.adapters.array.cli_client import ALLOWED_COMMANDS

    assert "showsched" in ALLOWED_COMMANDS
    assert refusal("showsched") is None
    for write in ("createsched x y z", "removesched -f zz_sn_vvs_snap", "setsched -suspend zz_sn_vvs_snap",
                  "createsv -ro zz_sn_vol01.initial zz_sn_vol01"):
        assert refusal(write) is not None, write


@pytest.mark.parametrize("command", [
    GOOD,
    f'createsched -f "createsv -f -exp 8h {PATTERN} set:patchi" "0 23 * * *" patchi_snap',   # read-write
    f'createsched -f "createsv -f -ro -exp 2h {PATTERN} zz_sn_vol01" "0,15,30,45 * * * 1,2,3,4,5" zz_sn_vol01_snap',
    f'createsched -f "createsv -f -ro -exp 43800h {PATTERN} set:zz_sn_vvs" "0 0 * * 0" {NAME_31}',   # the limits
])
@pytest.mark.xfail(reason=CLIENT, strict=True)
def test_the_one_form_is_accepted(command):
    from alletra_onboard.adapters.array.snap_cli_client import snap_write_refusal

    assert snap_write_refusal(command) is None
    assert refusal(command) is not None                     # the read client stays read-only


@pytest.mark.parametrize("command", [
    # without -f the array can stop for a confirmation the session cannot give
    f'createsched "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 0,4,8,12,16,20 * * *" zz_sn_vvs_snap',
    'createsched -f "removevv -f zz_sn_vol01" "0 * * * *" evil',                    # any other inner command
    f'createsched -f "createsv -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" no_inner_f',
    f'createsched -f "createsv -f -ro {PATTERN} set:zz_sn_vvs" "0 * * * *" no_expiry',   # -exp is mandatory
    f'createsched -f "createsv -f -ro -exp 43801h {PATTERN} set:zz_sn_vvs" "0 * * * *" too_long',
    f'createsched -f "createsv -f -ro -exp 0h {PATTERN} set:zz_sn_vvs" "0 * * * *" zero',
    # no lock in the first slice (ADR 0025 condition 4), nor one longer than the expiry
    f'createsched -f "createsv -f -exp 8h -retain 8h {PATTERN} set:patchi" "0 23 * * *" patchi_snap',
    f'createsched -f "createsv -f -ro -exp 24h -retain 48h {PATTERN} set:zz_sn_vvs" "0 * * * *" lock_gt_keep',
    f'createsched -f "createsv -f -ro -exp 24h -addtoset s {PATTERN} set:zz_sn_vvs" "0 * * * *" addtoset',
    # createsched options the form does not list
    f'createsched -f -immutable "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" immutable',
    f'createsched -f -run_once "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" run_once',
    f'createsched -f -interval 60 "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "* * * * 1-5" interval',
    f'createsched -f -no_alert "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" no_alert',
    # createsv options and sources the form does not list
    f'createsched -f "createsv -f -rcopy -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" rcopy',
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} rcgroup:zz_sn_rcg" "0 * * * *" rcgroup',
    f'createsched -f "createsv -f -ro -exp 24h -comment note {PATTERN} set:zz_sn_vvs" "0 * * * *" comment',
    f'createsched -f "createsv -f -ro -exp 24h -comment \\"a note\\" {PATTERN} set:zz_sn_vvs" "0 * * * *" quoted',
    # cron fields: digits, commas and * only; no day of month or month
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "@hourly" macro',
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 */4 * * *" step_syntax',
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 0 1 * *" day_of_month',
    # names: reserved, or longer than 31 (removesched's limit, and createsched's own on OS 10.5)
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" all',
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" upgrade',
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" {NAME_31}x',
    # a quote where the form has none, and the Tcl and shell characters, inside the quotes or out
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" "zz_sn_vvs_snap"',
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs; removevv -f x" "0 * * * *" chained',
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} [removevv -f zz_sn_vol01]" "0 * * * *" substitution',
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} {{set:zz_sn_vvs}}" "0 * * * *" braces',
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:$vvs" "0 * * * *" variable',
    f"createsched -f 'createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs' '0 * * * *' single_quotes",
    f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 * * * *" back\\slash',
    "removesched -f zz_sn_vvs_snap",
    "setsched -suspend zz_sn_vvs_snap",
    "createsv -ro -exp 24h zz_sn_vol01.initial zz_sn_vol01",                       # snapshots now go over WSAPI
    "showsched",
])
@pytest.mark.xfail(reason=CLIENT, strict=True)
def test_everything_else_is_refused(command):
    from alletra_onboard.adapters.array.snap_cli_client import snap_write_refusal

    assert snap_write_refusal(command) is not None


@pytest.mark.xfail(reason=CLIENT, strict=True)
def test_the_client_writes_only_the_schedules_of_the_approved_plan():
    """ADR 0025 condition 3: a well-formed createsched on a name or a source the approved plan does not
    name is refused, and a client built without the plan's objects writes nothing."""
    from alletra_onboard.adapters.array.snap_cli_client import (
        SnapPlanObjects,
        snap_object_refusal,
        snap_write_refusal,
    )

    objects = SnapPlanObjects(schedules=frozenset({("zz_sn_vvs_snap", "set:zz_sn_vvs")}))
    assert snap_object_refusal(GOOD, objects) is None
    for command in (GOOD.replace("set:zz_sn_vvs", "set:prod_vvs"), GOOD.replace("zz_sn_vvs_snap", "zz_sn_x_snap")):
        assert snap_write_refusal(command) is None          # well formed ...
        assert snap_object_refusal(command, objects) is not None   # ... but not in the plan
    assert snap_object_refusal(GOOD, SnapPlanObjects()) is not None


@pytest.mark.parametrize("folder", list(CAPTURES))
@pytest.mark.xfail(reason=CLIENT, strict=True)
def test_the_form_matches_the_arrays_own_help(folder):
    """Pinned to `help createsched` and `help createsv` from lab/snap_capture.py on all four lab arrays.
    On OS 10.5 createsched itself takes names of at most 31 characters (10.6.0: 127)."""
    from alletra_onboard.adapters.array.snap_cli_client import snap_write_refusal

    def words(name: str) -> str:
        return " ".join((FIX / folder / name).read_text(encoding="utf-8").split())

    assert (FIX / folder / "showversion.txt").read_text(encoding="utf-8").splitlines()[1] == (
        f"Release version {CAPTURES[folder]}"
    )
    createsched = words("help_createsched.txt")
    createsv = words("help_createsv.txt")
    assert "createsched [options] <cmd> <taskschedule> <schedname>" in createsched
    assert "-f Do not detect when a new scheduled task exceeds the recommended number" in createsched
    assert re.search(r"Only the following commands can be scheduled: [a-z ]*\bcreatesv\b", createsched)
    assert "day-of-week * or 0-6 (0 is Sunday)" in createsched
    for option in ("-exp", "-retain", "-ro", "-f"):
        assert option in createsv
    assert createsv.count("in the range of 1 minute - 1825 days") == 2      # -exp and -retain: 43800 h
    limit = int(re.search(r"The name can be up to (\d+) characters in length\.", createsched).group(1))
    assert limit == (127 if CAPTURES[folder] == "10.6.0" else 31)
    assert snap_write_refusal(GOOD) is None
    form = GOOD.rsplit(" ", 1)[0]
    assert snap_write_refusal(f"{form} {'z' * min(limit, 31)}") is None
    assert snap_write_refusal(f"{form} {'z' * (min(limit, 31) + 1)}") is not None
