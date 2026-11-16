"""ADR 0016 (PROPOSED, option A) and SPEC-023 R3 — the read allowlist gains `showsched`, and a
write-scoped SSH client may run ONE form: `createsched` of a `createsv` on one source, with an expiry.
The command inside the quotes is checked too: a schedule is a command the array runs later, so a
check on the first word would let anything in. Not built yet: every test here is expected to fail
until the work packet's step that names it is done (docs/workpackets/BL-21.md). If the owner does not
take option A, the work packet says which tests to delete. The array's help is captured
(tests/fixtures/rack13_snap/, rack13-ARCUS, OS 10.6.0, 2026-11-16)."""

from pathlib import Path

import pytest

from alletra_onboard.adapters.array.cli_client import refusal

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "rack13_snap"
PATTERN = "@vvname@.@y@@m@@d@@H@@M@@S@"
GOOD = f'createsched "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 0,4,8,12,16,20 * * *" zz_sn_vvs_snap'


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
    f'createsched "createsv -f -exp 8h -retain 8h {PATTERN} set:patchi" "0 23 * * *" patchi_snap',
    f'createsched "createsv -f -ro -exp 2h {PATTERN} zz_sn_vol01" "0,15,30,45 * * * 1,2,3,4,5" zz_sn_vol01_snap',
])
@pytest.mark.xfail(reason="BL-21 step 9A: the write client waits on ADR 0016", strict=True)
def test_the_one_form_is_accepted(command):
    from alletra_onboard.adapters.array.snap_cli_client import snap_write_refusal

    assert snap_write_refusal(command) is None
    assert refusal(command) is not None                     # the read client stays read-only


@pytest.mark.parametrize("command", [
    'createsched "removevv -f zz_sn_vol01" "0 * * * *" evil',                       # any other inner command
    f'createsched "createsv -f -ro {PATTERN} set:zz_sn_vvs" "0 * * * *" no_expiry',   # -exp is mandatory
    f'createsched "createsv -f -ro -exp 43801h {PATTERN} set:zz_sn_vvs" "0 * * * *" too_long',
    f'createsched "createsv -f -ro -exp 24h -retain 48h {PATTERN} set:zz_sn_vvs" "0 * * * *" lock_gt_keep',
    f'createsched "createsv -f -ro -exp 24h -addtoset s {PATTERN} set:zz_sn_vvs" "0 * * * *" addtoset',
    f'createsched "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "@hourly" macro',
    f'createsched "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 */4 * * *" step_syntax',
    f'createsched "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 0 1 * *" day_of_month',
    f'createsched "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs; removevv -f x" "0 * * * *" chained',
    "removesched -f zz_sn_vvs_snap",
    "setsched -suspend zz_sn_vvs_snap",
    "createsv -ro -exp 24h zz_sn_vol01.initial zz_sn_vol01",                       # snapshots now go over WSAPI
    "showsched",
])
@pytest.mark.xfail(reason="BL-21 step 9A: the write client waits on ADR 0016", strict=True)
def test_everything_else_is_refused(command):
    from alletra_onboard.adapters.array.snap_cli_client import snap_write_refusal

    assert snap_write_refusal(command) is not None


@pytest.mark.xfail(
    reason="BL-21 step 9A: the help is captured (rack13_snap); the write client is not built", strict=True,
)
def test_the_form_matches_the_arrays_own_help():
    """Pinned to `help createsched` and `help createsv` from lab/snap_capture.py (rack13-ARCUS, OS 10.6.0,
    2026-11-16)."""
    from alletra_onboard.adapters.array.snap_cli_client import snap_write_refusal

    createsched = (FIX / "help_createsched.txt").read_text(encoding="utf-8")
    createsv = (FIX / "help_createsv.txt").read_text(encoding="utf-8")
    assert "createsched" in createsched
    for option in ("-exp", "-retain", "-ro", "-f"):
        assert option in createsv
    assert snap_write_refusal(GOOD) is None
