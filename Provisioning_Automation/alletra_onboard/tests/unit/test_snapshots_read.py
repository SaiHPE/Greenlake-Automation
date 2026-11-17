"""SPEC-023 R3 — the snapshot reads, pinned to real captures: `showsched` on the lab pair
(tests/fixtures/rc_pair/*/showsched.txt, 2026-10-07), the WSAPI volume list with twelve snapshots
(tests/fixtures/rack13_wsapi/volumes.json, 2026-09-13), rack13-ARCUS on OS 10.6.0 with no schedule
and no snapshot (tests/fixtures/rack13_snap/, 2026-11-16: showsched, showvv's snapshot columns, the
WSAPI /schedules probe and the CLI's own help), and the same capture on three OS 10.5 arrays
(2026-11-17): D22U27 with seven schedules and 105 snapshots (d22u27_snap/), E18U31 with no schedule
and three snapshots without expiry (e18u31_snap/), VZ with one suspended schedule and 66 snapshots
(vz_snap/)."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

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


def test_showsched_on_rack13_os_10_6_reads_the_id_and_rebal_layout():
    """Captured 2026-11-17 on rack13-ARCUS (OS 10.6.0) right after the live check's createsched -f;
    the schedule was removed with removesched -f straight after (docs/validation/2026-11-17-rack13-live-w2.md).
    OS 10.6.0 starts each row with an Id column and adds Rebal before NextRunTime; the columns are
    taken by header word, so neither shifts the others."""
    from alletra_onboard.application.snapshots.read import parse_showsched, showsched_readable

    text = _snap("showsched_one.txt")
    assert showsched_readable(text)
    rows = parse_showsched(text)
    assert [(r.name, r.command, r.cron) for r in rows] == [
        ("zz_snap_probe", "createsv -f -ro -exp 1h @vvname@.@y@@m@@d@@H@@M@@S@ set:zz_snap_vvs", "0 3 * * *")]
    assert (rows[0].interval, rows[0].created_by, rows[0].status, rows[0].alert, rows[0].next_run) == (
        "0", "3paradm", "active", "Y", "2026-11-18 03:00:00 IST")


@pytest.mark.parametrize("folder", ["d22u27_snap", "vz_snap", "rack13_snap"])
def test_a_showsched_table_with_a_row_or_header_it_cannot_read_is_not_a_read(folder):
    """A layout not seen before must fail the read, never read as "no schedule" or drop a row: the apply
    would then lose the removal line of a schedule it made."""
    from alletra_onboard.application.snapshots.read import showsched_readable

    name = "showsched_one.txt" if folder == "rack13_snap" else "showsched.txt"
    lines = _fix(folder, name).splitlines()
    head = next(i for i, ln in enumerate(lines) if "SchedName" in ln.split()[:2])
    assert showsched_readable("\n".join(lines))
    cut_short = lines[:head + 1] + [" ".join(lines[head + 1].split()[:5])] + lines[head + 2:]
    assert not showsched_readable("\n".join(cut_short))
    no_status_column = lines[:head] + [lines[head].replace(" Status ", " ")] + lines[head + 1:]
    assert not showsched_readable("\n".join(no_status_column))


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


# ------------------------------------------------- D22U27, E18U31 and VZ, OS 10.5.x, 2026-11-17

OS_10_5 = {"d22u27_snap": "10.5.0", "e18u31_snap": "10.5.60", "vz_snap": "10.5.51"}


def _fix(folder: str, name: str) -> str:
    return (FIX / folder / name).read_text(encoding="utf-8")


def _sets(folder: str) -> dict[str, list[str]]:
    body = json.loads(_fix(folder, "wsapi_volumesets.json"))
    return {s["name"]: s.get("setmembers", []) for s in body["members"]}


def _cli_time(iso: str) -> str:
    """WSAPI's `2026-11-14T16:00:00+05:30` as showvv prints it on these arrays (all in IST)."""
    assert iso.endswith("+05:30"), iso
    return iso[:19].replace("T", " ") + " IST"


def test_showsched_reads_the_seven_schedules_of_d22u27_and_the_three_createsv_ones():
    from alletra_onboard.application.snapshots.read import parse_createsv, parse_showsched

    text = _fix("d22u27_snap", "showsched.txt")
    rows = {r.name: r for r in parse_showsched(text)}
    assert list(rows) == [
        "test_CRV_snapschedule", "compactcpg_SSD_r6_sun", "Pol-999",
        "Compact-Task", "Compact-Task1", "Compact-Task2", "Test",
    ]
    assert text.splitlines()[-1].split()[:2] == ["7", "total"]
    assert {r.status for r in rows.values()} == {"active"}
    assert all(r.next_run.endswith(" IST") and len(r.next_run.split()) == 3 for r in rows.values())

    parts = {name: parse_createsv(r.command) for name, r in rows.items()}
    assert [name for name, p in parts.items() if p] == ["test_CRV_snapschedule", "Pol-999", "Test"]
    assert parts["test_CRV_snapschedule"] == {
        "read_only": True, "expire": "56h", "retain": "48h", "add_to_set": "",
        "pattern": "snp-@vvname@@m@@d@@H@@M@", "source": "set:test_CRV_set",
    }
    assert rows["test_CRV_snapschedule"].cron == "00 0,4,8,12,16,20 * * *"
    assert parts["Pol-999"] == {
        "read_only": True, "expire": "1440m", "retain": "", "add_to_set": "set-test9991784524165764448212",
        "pattern": "@vvname@.@y@@m@@d@@H@@M@@S@", "source": "set:set-test999",
    }
    assert rows["Pol-999"].cron == "0,15,30,45 8,9,10,11,12,13,14,15,16,17,18,19,20 * * 0,1,2,3,4,5,6"
    assert rows["Pol-999"].created_by == "lab-user"         # scrubbed, padded so the columns stay put
    test = rows["Test"]
    assert test.command == (
        "createsv -f -addtoset Test.Snapset -exp 5d -retain 2d @vvname@.@y@@m@@d@@H@@M@@S@ set:300gb"
    )
    assert parts["Test"] == {
        "read_only": False, "expire": "5d", "retain": "2d", "add_to_set": "Test.Snapset",
        "pattern": "@vvname@.@y@@m@@d@@H@@M@@S@", "source": "set:300gb",
    }
    assert test.cron == "0 7 9 * *"                         # day of month 9: a monthly schedule
    assert (test.created_by, test.next_run) == ("3paradm", "2026-12-09 07:00:00 IST")
    assert rows["compactcpg_SSD_r6_sun"].dow == "0"
    assert parts["Compact-Task"] == {}


def test_showsched_reads_a_suspended_schedule_with_no_next_run_on_vz():
    from alletra_onboard.application.snapshots.read import parse_createsv, parse_showsched

    rows = parse_showsched(_fix("vz_snap", "showsched.txt"))
    assert len(rows) == 1
    row = rows[0]
    assert (row.name, row.command) == ("SynRcopy_Schedule", "syncrcopy LZ_RcopyGroup1.r194089")
    assert row.cron == "5 3,7,11,15,19,23 * * *"
    assert (row.created_by, row.status, row.alert, row.next_run) == ("3paradm", "suspended", "Y", "--")
    assert parse_createsv(row.command) == {}


def test_showsched_on_e18u31_with_no_schedules_is_an_empty_list():
    from alletra_onboard.application.snapshots.read import parse_showsched

    text = _fix("e18u31_snap", "showsched.txt")
    assert "No scheduled tasks listed" in text
    assert parse_showsched(text) == []


@pytest.mark.parametrize("folder, total, snapshots, expiring, locked", [
    ("d22u27_snap", 217, 105, 67, 23),
    ("vz_snap", 93, 66, 60, 57),
    ("e18u31_snap", 35, 3, 0, 0),
])
def test_showvv_and_wsapi_agree_on_every_snapshot_its_expiry_and_its_lock(
    folder, total, snapshots, expiring, locked,
):
    from alletra_onboard.adapters.array.wsapi_client import parse_volumes
    from alletra_onboard.application.snapshots.read import parse_showvv_snapcols

    cli = {r["Name"]: r for r in parse_showvv_snapcols(_fix(folder, "showvv_snapcols.txt"))}
    body = json.loads(_fix(folder, "wsapi_volumes.json"))
    raw = {m["name"]: m for m in body["members"]}
    wsapi = {v.name: v for v in parse_volumes(body)}
    assert len(cli) == total == body["total"]
    assert set(cli) == set(wsapi) == set(raw)
    assert sum(1 for v in wsapi.values() if v.copy_of) == snapshots
    assert sum(1 for r in cli.values() if r["Type"] == "vcopy") == snapshots
    assert sum(1 for v in wsapi.values() if v.expires) == expiring
    # The WSAPI name of a snapshot's lock (createsv -retain): retentionTime8601 and retentionTimeSec,
    # both absent when there is none.
    assert sum(1 for m in raw.values() if "retentionTime8601" in m) == locked
    assert sum(1 for m in raw.values() if "retentionTimeSec" in m) == locked
    for name, row in cli.items():
        vol, member = wsapi[name], raw[name]
        assert row["CopyOf"] == vol.copy_of, name
        assert (row["Rd"] == "RO") == vol.read_only, name
        assert (row["Prov"] == "snp") == (vol.provisioning_type == "snp") == (member["copyType"] == 3), name
        assert row["CreationTime"] == _cli_time(vol.created), name
        assert row["ExpirationTime"] == (_cli_time(vol.expires) if vol.expires else ""), name
        lock = member.get("retentionTime8601")
        assert row["RetentionEndTime"] == (_cli_time(lock) if lock else ""), name


def test_the_d22u27_schedules_ran_in_the_arrays_local_time_with_their_expiry_and_lock():
    """SPEC-023 open question 5: a schedule's cron hour is the array's local time. Pol-999 runs at
    minutes 0,15,30,45 of hours 8 to 20 and test_CRV_snapschedule at hours 0,4,8,12,16,20; their
    snapshots were created at those times in IST (+05:30), each with the schedule's -exp and -retain."""
    from alletra_onboard.adapters.array.wsapi_client import parse_volumes

    body = json.loads(_fix("d22u27_snap", "wsapi_volumes.json"))
    raw = {m["name"]: m for m in body["members"]}
    volumes = parse_volumes(body)
    sets = _sets("d22u27_snap")

    pol = [v for v in volumes if v.copy_of == "test999" and v.expires]
    assert len(pol) == 52                                   # 13 hours, 4 a hour, kept 24 hours
    for v in pol:
        created = datetime.fromisoformat(v.created)
        assert v.created.endswith("+05:30")
        assert 8 <= created.hour <= 20 and created.minute in (0, 15, 30, 45), v.name
        assert datetime.fromisoformat(v.expires) - created == timedelta(minutes=1440), v.name
        assert v.read_only and "retentionTime8601" not in raw[v.name]
        # @vvname@.@y@@m@@d@@H@@M@@S@ is "." and twelve digits, two-digit year, local time; the
        # seconds in the name can be one past the creation time (test999.261116170001, 17:00:00)
        assert v.name[:-2] == "test999." + created.strftime("%y%m%d%H%M"), v.name
        assert int(v.name[-2:]) - created.second in (0, 1), v.name
        assert v.name in sets["set-test9991784524165764448212"]      # -addtoset

    crv = [v for v in volumes if v.copy_of == "test_CRV.r" and v.expires]
    assert len(crv) == 15                                   # 2026-11-14 16:00 to 11-17 00:00, every 4 hours
    for v in crv:
        created = datetime.fromisoformat(v.created)
        assert created.hour in (0, 4, 8, 12, 16, 20) and created.minute == 0, v.name
        assert v.name == "snp-test_CRV.r" + created.strftime("%m%d%H%M")
        assert datetime.fromisoformat(v.expires) - created == timedelta(hours=56), v.name
        locked = datetime.fromisoformat(raw[v.name]["retentionTime8601"]) - created
        assert abs(locked - timedelta(hours=48)) <= timedelta(seconds=1), v.name


def test_e18u31_snapshots_have_no_expiry_and_no_lock():
    from alletra_onboard.adapters.array.wsapi_client import parse_volumes

    body = json.loads(_fix("e18u31_snap", "wsapi_volumes.json"))
    snaps = {v.name: v for v in parse_volumes(body) if v.copy_of}
    assert {name: v.copy_of for name, v in snaps.items()} == {
        "preRecover_LK04_20261116": "TPIPoc-NEW-RH-LK-04",
        "preRecover_LK06_20261116": "TPIPoc-NEW-RH-LK-06",
        "preRecover_LK05_20261116": "TPIPoc-NEW-RH-LK-05",
    }
    assert all(v.read_only and v.provisioning_type == "snp" and v.expires == "" for v in snaps.values())
    assert not any("retention" in key.lower() for member in body["members"] for key in member)


def test_remote_copy_snapshots_also_name_the_base_in_copy_of():
    """Why a schedule's snapshots cannot be counted by copyOf alone (SPEC-023 §2.2): Remote Copy's own
    snapshots of a member carry the same copyOf, and on a secondary array snapshots arrive from the
    primary's schedule with no schedule of their own."""
    from alletra_onboard.adapters.array.wsapi_client import parse_volumes
    from alletra_onboard.application.snapshots.read import parse_createsv, parse_showsched

    d22 = {m["name"]: m for m in json.loads(_fix("d22u27_snap", "wsapi_volumes.json"))["members"]}
    sets = _sets("d22u27_snap")
    assert sets["300gb"] == ["300gb", "Test"]                # the source of D22U27's schedule "Test"
    rc = d22["rcpy.41.269.5"]
    assert (rc["copyOf"], rc["readOnly"]) == ("300gb", True)
    assert rc["comment"] == "Remote Copy snapshot created for target 'AlletraMP_E18U31' of group '300gb'."

    vz = json.loads(_fix("vz_snap", "wsapi_volumes.json"))
    peer = "Remote Copy snapshot created for target 'MPB10K-E24U21-LZ' of group 'LZ_RcopyGroup1.r194089'."
    from_peer = {m["name"] for m in vz["members"] if m.get("comment") == peer}
    assert len(from_peer) == 57
    assert all(v.copy_of and v.read_only and v.expires for v in parse_volumes(vz) if v.name in from_peer)
    assert all("retentionTime8601" in m for m in vz["members"] if m["name"] in from_peer)
    assert not any(parse_createsv(r.command) for r in parse_showsched(_fix("vz_snap", "showsched.txt")))


@pytest.mark.parametrize("folder, free", [
    ("d22u27_snap", {"3sc": 179025, "SSD_r6": 403200, "test": 537075, "test_1": 19950}),
    ("e18u31_snap", {"SSD_r6": 238875}),
    ("vz_snap", {"SSD_r6": 256725}),
])
def test_showcpg_free_space_for_the_cpg_note(folder, free):
    from alletra_onboard.application.replication.read import parse_showcpg_free

    assert parse_showcpg_free(_fix(folder, "showcpg.txt")) == free


@pytest.mark.parametrize("folder, zone", [
    ("d22u27_snap", "Asia/Calcutta"), ("e18u31_snap", "Asia/Calcutta"), ("vz_snap", "Asia/Kolkata"),
])
def test_wsapi_has_no_schedule_resource_on_os_10_5_and_nothing_is_named_zz_sn(folder, zone):
    from alletra_onboard.application.snapshots.read import parse_showvv_snapcols

    probe = json.loads(_fix(folder, "wsapi_schedules_probe.json"))
    assert probe["http_status"] == 501
    assert json.loads(probe["body"]) == {"code": 9, "desc": "unsupported operation for the resource"}
    assert parse_showvv_snapcols(_fix(folder, "showvv_zz_sn.txt")) == []
    assert "No vv set listed" in _fix(folder, "showvvset_zz_sn.txt")
    # the same zone under two names; showdate and GET /system agree on each array
    assert all(line.endswith(f"IST ({zone})") for line in _fix(folder, "showdate.txt").splitlines()[2:])
    assert json.loads(_fix(folder, "wsapi_system.json"))["timeZone"] == zone


@pytest.mark.parametrize("folder", list(OS_10_5))
def test_the_help_on_os_10_5_states_the_limits_and_forms_the_domain_uses(folder):
    from alletra_onboard.application.snapshots.read import parse_createsv
    from alletra_onboard.domain.snapshots import HOURS_MAX, SCHEDULE_NAME_MAX

    assert _fix(folder, "showversion.txt").splitlines()[1] == f"Release version {OS_10_5[folder]}"
    createsched = _words(_fix(folder, "help_createsched.txt"))
    createsv = _words(_fix(folder, "help_createsv.txt"))
    removesched = _words(_fix(folder, "help_removesched.txt"))
    assert createsv.count("in the range of 1 minute - 1825 days") == 2       # -exp and -retain
    assert HOURS_MAX == 1825 * 24
    # On 10.5 createsched itself takes 31 characters (10.6.0: 127); removesched takes 31 on both.
    assert "The name can be up to 31 characters in length." in createsched
    assert "Can be at most 31 characters in length." in removesched
    assert SCHEDULE_NAME_MAX == 31
    assert "createsched [options] <cmd> <taskschedule> <schedname>" in createsched
    assert "createsv [options] <SV_name> <copy_of_VV | VV_set | RC_group>" in createsv
    assert " creategroupsv createsv creategroupvvcopy " in createsched   # createsv may be scheduled
    assert "day-of-week * or 0-6 (0 is Sunday)" in createsched
    assert "Do not ask for confirmation to create the new scheduled task." in createsched
    assert "-f Do not ask for confirmation before creating a volume with retention time (-retain)." in createsv
    assert "then the retention time cannot be longer than the expiration time." in createsv
    assert "The default value for the system's VVRetentionTimeMax is 14 days." in createsv
    assert "A maximum of 2048 virtual copies per volume are allowed." in createsv
    assert "Consistent group snapshots are all created at the same point in time" in createsv
    example = 'createsched "createsv -ro -exp 2h @vvname@.@s@ set:dbora" "0 8-17 * * *" sv_dbora_task'
    assert example in createsched
    assert parse_createsv("createsv -ro -exp 2h @vvname@.@s@ set:dbora")["source"] == "set:dbora"
    # 10.6.0 options that 10.5 lacks; the tool's form uses none of them
    assert "-immutable" not in createsched and "-no_rebalance" not in createsched
    assert "-noerror" not in createsv
    system = json.loads(_fix(folder, "wsapi_system.json"))
    assert system["parameters"]["VVRetentionTimeMax"] == 14 * 24 * 3600
    assert system["licenseInfo"]["licenseState"]["virtualLock"] is True
    assert system["contact"] == "lab-user"                   # scrubbed


def test_the_help_is_the_same_on_the_three_os_10_5_arrays_and_differs_from_10_6():
    for name in ("help_createsched.txt", "help_createsv.txt", "help_removesched.txt", "help_removevv.txt",
                 "help_showsched.txt"):
        assert len({_fix(folder, name) for folder in OS_10_5}) == 1, name
    assert _fix("d22u27_snap", "help_setsched.txt") == _fix("vz_snap", "help_setsched.txt")
    assert _fix("e18u31_snap", "help_setsched.txt") != _fix("d22u27_snap", "help_setsched.txt")   # 10.5.60
    assert _fix("d22u27_snap", "help_removesched.txt") == _snap("help_removesched.txt")
    assert _fix("d22u27_snap", "help_removevv.txt") == _snap("help_removevv.txt")
    assert "The name can be up to 127 characters in length." in _words(_snap("help_createsched.txt"))
