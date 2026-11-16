"""SPEC-023 R3 — the snapshot reads, pinned to real captures: `showsched` on the lab pair
(tests/fixtures/rc_pair/*/showsched.txt, 2026-10-07), the WSAPI volume list with twelve snapshots
(tests/fixtures/rack13_wsapi/volumes.json, 2026-09-13), and rack13-ARCUS on OS 10.6.0 with no schedule
and no snapshot (tests/fixtures/rack13_snap/, 2026-11-16: showsched, showvv's snapshot columns, the
WSAPI /schedules probe and the CLI's own help)."""

import json
from pathlib import Path

FIX = Path(__file__).resolve().parents[1] / "fixtures"
SNAP = FIX / "rack13_snap"


def _snap(name: str) -> str:
    return (SNAP / name).read_text(encoding="utf-8")


def _words(text: str) -> str:
    """The help wraps sentences across lines; compare on single spaces."""
    return " ".join(text.split())


def _showsched(array: str) -> str:
    return (FIX / "rc_pair" / array / "showsched.txt").read_text(encoding="utf-8")


def test_showsched_reads_every_row_of_the_d22u27_capture_with_spaces_in_the_command():
    from alletra_onboard.application.snapshots.read import parse_showsched

    rows = parse_showsched(_showsched("D22U27"))
    assert [r.name for r in rows] == [
        "test_CRV_snapschedule", "compactcpg_SSD_r6_sun", "Pol-999",
        "Compact-Task", "Compact-Task1", "Compact-Task2",
    ]
    crv = rows[0]
    assert crv.command == (
        "createsv -f -ro -exp 56h -retain 48h snp-@vvname@@m@@d@@H@@M@ set:test_CRV_set"
    )
    assert (crv.minute, crv.hour, crv.dom, crv.month, crv.dow) == ("00", "0,4,8,12,16,20", "*", "*", "*")
    assert (crv.created_by, crv.status, crv.alert) == ("3paradm", "active", "Y")
    assert crv.next_run == "2026-10-07 20:00:00 IST"
    pol = rows[2]
    assert pol.minute == "0,15,30,45"
    assert pol.hour == "8,9,10,11,12,13,14,15,16,17,18,19,20"
    assert pol.dow == "0,1,2,3,4,5,6"
    assert rows[1].dow == "0"                       # the `_sun` schedule: 0 is Sunday


def test_showsched_reads_the_one_row_of_the_e18u31_capture():
    from alletra_onboard.application.snapshots.read import parse_showsched

    rows = parse_showsched(_showsched("E18U31"))
    assert len(rows) == 1
    row = rows[0]
    assert row.name == "patchisched"
    assert row.command == (
        "createsv -f -addtoset patchisched.Snapset -exp 8h -retain 8h "
        "@vvname@.@y@@m@@d@@H@@M@@S@ set:patchi"
    )
    assert row.cron == "0 23 * * *"


def test_showsched_with_no_schedules_is_an_empty_list():
    from alletra_onboard.application.snapshots.read import parse_showsched

    assert parse_showsched("") == []


def test_createsv_commands_are_read_into_their_options():
    from alletra_onboard.application.snapshots.read import parse_createsv

    crv = parse_createsv("createsv -f -ro -exp 56h -retain 48h snp-@vvname@@m@@d@@H@@M@ set:test_CRV_set")
    assert crv == {
        "read_only": True, "expire": "56h", "retain": "48h", "add_to_set": "",
        "pattern": "snp-@vvname@@m@@d@@H@@M@", "source": "set:test_CRV_set",
    }
    patch = parse_createsv(
        "createsv -f -addtoset patchisched.Snapset -exp 8h -retain 8h @vvname@.@y@@m@@d@@H@@M@@S@ set:patchi"
    )
    assert patch["read_only"] is False
    assert patch["add_to_set"] == "patchisched.Snapset"
    assert patch["source"] == "set:patchi"
    pol = parse_createsv(
        "createsv -f -ro -exp 1440m -addtoset set-test9991784524165764448212 "
        "@vvname@.@y@@m@@d@@H@@M@@S@ set:set-test999"
    )
    assert (pol["expire"], pol["retain"]) == ("1440m", "")


def test_parse_volumes_keeps_the_snapshot_fields_of_the_rack13_capture():
    from alletra_onboard.adapters.array.wsapi_client import parse_volumes

    body = json.loads((FIX / "rack13_wsapi" / "volumes.json").read_text(encoding="utf-8"))
    by_name = {v.name: v for v in parse_volumes(body)}
    snap = by_name["vol1.0.260910000000"]
    assert snap.provisioning_type == "snp"
    assert snap.copy_of == "vol1.0"
    assert snap.read_only is True
    assert snap.created == "2026-09-10T00:00:00+05:30"
    assert snap.expires == "2026-10-10T00:00:00+05:30"
    assert snap.cpg == "SSD_r6"                    # no separate snapshot CPG on OS 10.5
    base = by_name["vol1.0"]
    assert (base.copy_of, base.read_only, base.expires) == ("", False, "")
    assert sum(1 for v in by_name.values() if v.copy_of) == 12


# ------------------------------------------------------------------ rack13-ARCUS, OS 10.6.0, 2026-11-16

def test_showsched_on_rack13_with_no_schedules_is_an_empty_list():
    from alletra_onboard.application.snapshots.read import parse_showsched

    text = _snap("showsched.txt")
    assert "No scheduled tasks listed" in text
    assert parse_showsched(text) == []


def test_showvv_snapshot_columns_of_the_rack13_capture():
    from alletra_onboard.adapters.array.wsapi_client import parse_volumes
    from alletra_onboard.application.snapshots.read import SHOWVV_SNAPCOLS, parse_showvv_snapcols

    text = _snap("showvv_snapcols.txt")
    assert text.splitlines()[0] == f"# {SHOWVV_SNAPCOLS}"
    rows = {r["Name"]: r for r in parse_showvv_snapcols(text)}
    assert len(rows) == 35                                   # the listing's own "35 total"
    shared = rows["test_vme_shared"]
    assert (shared["Id"], shared["Prov"], shared["Type"], shared["CopyOf"], shared["Rd"], shared["CPG"]) == (
        "37", "tdvv", "base", "", "RW", "SSD_r6",
    )
    assert shared["CreationTime"] == "2026-10-29 14:32:34 IST"
    assert (shared["ExpirationTime"], shared["RetentionEndTime"]) == ("", "")
    assert rows[".mgmtdata"]["CPG"] == ""
    assert {r["Type"] for r in rows.values()} == {"base"}     # no snapshot on the array
    assert not any(r["CopyOf"] or r["ExpirationTime"] or r["RetentionEndTime"] for r in rows.values())

    # the same 35 volumes over WSAPI, none a snapshot, and the same creation time in ISO form
    wsapi = {v.name: v for v in parse_volumes(json.loads(_snap("wsapi_volumes.json")))}
    assert set(wsapi) == set(rows)
    assert not any(v.copy_of or v.read_only or v.expires or v.provisioning_type == "snp" for v in wsapi.values())
    assert wsapi["test_vme_shared"].created == "2026-10-29T14:32:34+05:30"
    assert parse_showvv_snapcols(_snap("showvv_zz_sn.txt")) == []          # "no vv listed"


def test_wsapi_has_no_schedule_resource():
    """Why schedules are read with showsched and cannot be written over WSAPI."""
    probe = json.loads(_snap("wsapi_schedules_probe.json"))
    assert probe["http_status"] == 501
    assert json.loads(probe["body"]) == {"code": 9, "desc": "unsupported operation for the resource"}


def test_the_help_states_the_limits_the_domain_uses():
    from alletra_onboard.domain.snapshots import HOURS_MAX, SCHEDULE_NAME_MAX

    createsv = _words(_snap("help_createsv.txt"))
    assert createsv.count("in the range of 1 minute - 1825 days") == 2       # -exp and -retain
    assert HOURS_MAX == 1825 * 24
    assert "The name can be up to 127 characters in length." in _words(_snap("help_createsched.txt"))
    assert "Can be at most 31 characters in length." in _words(_snap("help_removesched.txt"))
    assert SCHEDULE_NAME_MAX == 31                           # so the removal line can name it


def test_the_help_gives_the_createsched_and_createsv_forms():
    from alletra_onboard.application.snapshots.read import parse_createsv

    createsched = _words(_snap("help_createsched.txt"))
    createsv = _words(_snap("help_createsv.txt"))
    assert "createsched [options] <cmd> <taskschedule> <schedname>" in createsched
    assert "createsv [options] <SV_name> <copy_of_VV | VV_set | RC_group>" in createsv
    assert "checkhealth compactcpg compactld compactvv creategroupsv createsv " in createsched
    assert "day-of-week * or 0-6 (0 is Sunday)" in createsched
    # createsched asks for confirmation when it predicts too many starts in a minute, unless -f
    assert "Do not ask for confirmation to create the new scheduled task." in createsched
    # createsv -f is what skips the confirmation -retain asks for
    assert "-f Do not ask for confirmation before creating a volume with retention time (-retain)." in createsv
    assert "then the retention time cannot be longer than the expiration time." in createsv
    assert "The default value for the system's VVRetentionTimeMax is 14 days." in createsv
    system = json.loads(_snap("wsapi_system.json"))
    assert system["parameters"]["VVRetentionTimeMax"] == 14 * 24 * 3600   # rack13 keeps the default
    assert "A maximum of 2048 virtual copies per volume are allowed." in createsv
    assert "Consistent group snapshots are all created at the same point in time" in createsv

    # the array's own example of a scheduled set snapshot reads into its options
    example = 'createsched "createsv -ro -exp 2h @vvname@.@s@ set:dbora" "0 8-17 * * *" sv_dbora_task'
    assert example in createsched
    assert parse_createsv("createsv -ro -exp 2h @vvname@.@s@ set:dbora") == {
        "read_only": True, "expire": "2h", "retain": "", "add_to_set": "",
        "pattern": "@vvname@.@s@", "source": "set:dbora",
    }
    assert parse_createsv("compactcpg -f SSD_r6") == {}
