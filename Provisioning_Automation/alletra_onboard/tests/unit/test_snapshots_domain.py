"""SPEC-023 — snapshots and schedules from model objects: names, the cron and command lines (pinned to
the schedules captured on the lab pair; `createsched -f` since ADR 0016 was accepted, 2026-11-17), the
exists / create / conflict plan (R4, with the accepted ADR's blockers and notes), the removal order
(R6) and the step (R9). Written 2026-11-16/17 as expected failures; built 2026-11-17
(docs/workpackets/BL-21.md steps 1, 3, 5 and 6)."""

import pytest

PATTERN = "@vvname@.@y@@m@@d@@H@@M@@S@"


def _req(**kw):
    from alletra_onboard.domain.snapshots import SnapshotRequest

    base = {"source": "zz_sn_vvs", "expire_hours": 24}
    base.update(kw)
    return SnapshotRequest(**base)


def _vol(name, copy_of=""):
    from alletra_onboard.domain.provisioning import ArrayVolumeRecord

    return ArrayVolumeRecord(
        name=name, size_mib=1024, cpg="SSD_r6",
        provisioning_type="snp" if copy_of else "tpvv", copy_of=copy_of, read_only=bool(copy_of),
    )


def _view(*, volumes=None, vvsets=None, schedules=None, os_version="10.5.0"):
    from alletra_onboard.domain.snapshots import SnapshotArrayView

    return SnapshotArrayView(
        name="AlletraMP_D22U27", os_version=os_version, time_zone="IST",
        volumes=volumes if volumes is not None else [_vol("zz_sn_vol01"), _vol("zz_sn_vol02")],
        vvsets=vvsets if vvsets is not None else {"zz_sn_vvs": ["zz_sn_vol01", "zz_sn_vol02"]},
        schedules=schedules or [], cpg_free_mib={"SSD_r6": 3 * 1024 * 1024},
    )


def _schedule(name, command, cron, status="active"):
    from alletra_onboard.domain.snapshots import ArraySchedule

    minute, hour, dom, month, dow = cron.split()
    return ArraySchedule(
        name=name, command=command, interval="0", minute=minute, hour=hour, dom=dom, month=month,
        dow=dow, created_by="3paradm", status=status, alert="Y",
        next_run="2026-11-16 20:00:00 IST" if status == "active" else "--",
    )


def _plan(requests, view, **kw):
    from alletra_onboard.application.snapshots.plan import plan_snapshots
    from alletra_onboard.domain.snapshots import SnapshotIntent

    return plan_snapshots(SnapshotIntent(requests=requests), view, **kw)


# ------------------------------------------------------------------ names, cron, commands

def test_schedule_name_is_derived_and_shortened_with_a_stable_suffix():
    from alletra_onboard.domain.snapshots import SCHEDULE_NAME_MAX, derive_schedule_name

    assert derive_schedule_name("zz_sn_vvs") == "zz_sn_vvs_snap"
    long_name = "a_volume_set_with_a_very_long_name_01"
    derived = derive_schedule_name(long_name)
    assert len(derived) <= SCHEDULE_NAME_MAX
    assert derived.endswith("_snap")
    assert derived == derive_schedule_name(long_name)
    assert derived != derive_schedule_name(long_name[:-1] + "2")


@pytest.mark.parametrize(("every", "unit", "at_hour", "days", "cron"), [
    (4, "hours", 0, [], "0 0,4,8,12,16,20 * * *"),       # the captured test_CRV_snapschedule hours
    (1, "days", 23, [], "0 23 * * *"),                   # the captured patchisched fields
    (15, "minutes", 0, [], "0,15,30,45 * * * *"),
    (15, "minutes", 0, [1, 2, 3, 4, 5], "0,15,30,45 * * * 1,2,3,4,5"),
    (6, "hours", 2, [], "0 2,8,14,20 * * *"),
    (8, "hours", 20, [], "0 4,12,20 * * *"),             # wraps past midnight, sorted
    (1, "hours", 0, [0], "0 * * * 0"),
    (12, "hours", 0, [], "0 0,12 * * *"),
])
def test_cron_is_built_from_the_row(every, unit, at_hour, days, cron):
    from alletra_onboard.domain.snapshots import schedule_cron

    assert schedule_cron(every, unit, at_hour, days) == cron


def test_the_createsv_line_is_the_captured_patchisched_one_without_addtoset():
    req = _req(source="patchi", expire_hours=8, retain_hours=8, read_only=False, every=1, unit="days", at_hour=23)
    captured = f"createsv -f -addtoset patchisched.Snapset -exp 8h -retain 8h {PATTERN} set:patchi"
    assert req.createsv_command() == captured.replace("-addtoset patchisched.Snapset ", "")
    assert req.createsched_command() == f'createsched -f "{req.createsv_command()}" "0 23 * * *" patchi_snap'


def test_a_read_only_volume_row_names_the_volume_not_a_set():
    req = _req(source="zz_sn_vol01", kind="volume", every=4, unit="hours")
    assert req.source_ref == "zz_sn_vol01"
    assert req.createsv_command() == f"createsv -f -ro -exp 24h {PATTERN} zz_sn_vol01"
    assert req.name == "zz_sn_vol01_snap"


def test_a_schedule_name_from_the_sheet_wins():
    assert _req(every=4, unit="hours", schedule_name="nightly").name == "nightly"


# ------------------------------------------------------------------ R4: the plan

def test_a_fresh_set_plans_one_snapshot_and_one_schedule_in_apply_order():
    plan = _plan([_req(snapshot_now=True, every=4, unit="hours")], _view())
    assert plan.blockers == []
    assert [(a.kind, a.state) for a in plan.actions] == [("snapshot", "create"), ("schedule", "create")]
    snap, sched = plan.actions
    assert snap.members == ["zz_sn_vol01", "zz_sn_vol02"]
    assert snap.cli == "createsv -ro -exp 24h @vvname@.initial set:zz_sn_vvs"
    assert sched.name == "zz_sn_vvs_snap"
    assert sched.cli == (
        f'createsched -f "createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs" "0 0,4,8,12,16,20 * * *" zz_sn_vvs_snap'
    )
    assert any("SSD_r6" in n for n in plan.notes)          # the CPG free-space note


def test_a_rerun_finds_both_and_creates_nothing():
    req = _req(snapshot_now=True, every=4, unit="hours")
    view = _view(
        volumes=[_vol("zz_sn_vol01"), _vol("zz_sn_vol02"),
                 _vol("zz_sn_vol01.initial", "zz_sn_vol01"), _vol("zz_sn_vol02.initial", "zz_sn_vol02")],
        # the array may print 00 for 0: cron fields are compared as numbers
        schedules=[_schedule("zz_sn_vvs_snap", req.createsv_command(), "00 0,4,8,12,16,20 * * *")],
    )
    plan = _plan([req], view)
    assert [(a.kind, a.state) for a in plan.actions] == [("snapshot", "exists"), ("schedule", "exists")]
    assert plan.blockers == []


def test_a_schedule_of_that_name_doing_something_else_is_a_conflict_and_a_blocker():
    req = _req(every=4, unit="hours")
    other = _schedule("zz_sn_vvs_snap", f"createsv -f -ro -exp 48h {PATTERN} set:zz_sn_vvs", "0 0,4,8,12,16,20 * * *")
    plan = _plan([req], _view(schedules=[other]))
    assert [(a.kind, a.state) for a in plan.actions] == [("schedule", "conflict")]
    assert len(plan.blockers) == 1
    assert "never changes a schedule it did not make" in plan.blockers[0]


def test_a_foreign_schedule_on_the_same_set_is_a_note_not_a_blocker():
    foreign = _schedule("someone_elses", f"createsv -f -ro -exp 8h {PATTERN} set:zz_sn_vvs", "0 23 * * *")
    plan = _plan([_req(every=4, unit="hours")], _view(schedules=[foreign]))
    assert plan.blockers == []
    assert any("someone_elses" in n and "Both will run" in n for n in plan.notes)


def test_a_snapshot_name_taken_by_another_volume_is_a_conflict():
    view = _view(volumes=[_vol("zz_sn_vol01"), _vol("zz_sn_vol02"), _vol("zz_sn_vol01.initial")])
    plan = _plan([_req(snapshot_now=True)], view)
    assert plan.actions[0].state == "conflict"
    assert plan.blockers


def test_a_source_neither_on_the_array_nor_on_the_volumes_tab_blocks():
    plan = _plan([_req(source="nowhere_vvs", snapshot_now=True)], _view())
    assert plan.blockers == ["nowhere_vvs is not on the array and not on the Volumes tab."]


def test_a_source_still_to_be_provisioned_says_provision_first():
    plan = _plan([_req(source="zz_new_vvs", snapshot_now=True)], _view(), planned_vvsets={"zz_new_vvs"})
    assert plan.blockers == ["Provision storage first: zz_new_vvs is not on the array yet."]


def test_an_empty_set_blocks():
    plan = _plan([_req(snapshot_now=True)], _view(vvsets={"zz_sn_vvs": []}))
    assert plan.blockers and "zz_sn_vvs" in plan.blockers[0]


def test_a_snapshot_name_over_31_characters_blocks_below_os_10_4_2():
    long_vol = "zz_sn_volume_name_of_27chars"
    view = _view(volumes=[_vol(long_vol)], vvsets={"zz_sn_vvs": [long_vol]}, os_version="10.4.0")
    plan = _plan([_req(every=4, unit="hours")], view)
    assert plan.blockers and long_vol in plan.blockers[0]
    assert _plan([_req(every=4, unit="hours")], _view(
        volumes=[_vol(long_vol)], vvsets={"zz_sn_vvs": [long_vol]}, os_version="10.5.0",
    )).blockers == []


# ------------------------------------------------------------------ R4: ADR 0016 as accepted (2026-11-17)

def test_a_suspended_schedule_of_that_name_is_a_conflict_not_exists():
    req = _req(every=4, unit="hours")
    same = _schedule("zz_sn_vvs_snap", req.createsv_command(), "0 0,4,8,12,16,20 * * *", status="suspended")
    plan = _plan([req], _view(schedules=[same]))
    assert [(a.kind, a.state) for a in plan.actions] == [("schedule", "conflict")]
    assert len(plan.blockers) == 1
    assert "suspended" in plan.blockers[0]
    assert "never changes a schedule it did not make" in plan.blockers[0]


def test_a_lock_is_not_in_the_first_slice():
    """A locked snapshot cannot be removed until the lock ends (ADR 0025 condition 4)."""
    plan = _plan([_req(snapshot_now=True, every=4, unit="hours", retain_hours=8)], _view())
    assert plan.blockers == [(
        "zz_sn_vvs: Lock for is not offered yet. A locked snapshot cannot be removed until the lock "
        "ends; leave Lock for blank."
    )]


def test_more_than_2048_snapshots_of_one_volume_blocks():
    """The help: at most 2048 virtual copies per volume. Every snapshot of the member counts, read-only
    or not, until a live run shows which do."""
    # every 15 minutes kept 512 hours keeps 2048 alive: at the limit, not over it
    assert _plan([_req(every=15, unit="minutes", expire_hours=512)], _view()).blockers == []
    # the snapshot taken now makes 2049, on each member
    over = _plan([_req(snapshot_now=True, every=15, unit="minutes", expire_hours=512)], _view())
    assert len(over.blockers) == 2
    assert all("2049" in b and "2048" in b for b in over.blockers)
    # snapshots the member already has count too
    held = [_vol(f"zz_sn_vol01.{i:012d}", "zz_sn_vol01") for i in range(48)]
    view = _view(volumes=[_vol("zz_sn_vol01"), _vol("zz_sn_vol02"), *held])
    assert _plan([_req(every=1, unit="hours", expire_hours=2001)], view).blockers == [(
        "zz_sn_vol01 would hold up to 2049 snapshots; the array allows 2048 per volume. "
        "Keep them for less time, or take them less often."
    )]


def test_a_schedule_starting_with_others_in_the_same_minute_gets_a_note_not_a_blocker():
    """createsched -f turns off the array's own check on starts per minute, so the plan makes it.
    D22U27's schedules that start at midnight: four every day, a fifth on Sundays. A suspended one
    does not run, so it does not count."""
    midnight = [
        _schedule("test_CRV_snapschedule", "createsv -f -ro -exp 56h -retain 48h snp-@vvname@@m@@d@@H@@M@ "
                  "set:test_CRV_set", "00 0,4,8,12,16,20 * * *"),
        _schedule("compactcpg_SSD_r6_sun", "compactcpg -f SSD_r6", "0 0 * * 0"),
        _schedule("Compact-Task", "compactcpg SSD_r6", "0 0,5,10,15,20 * * *"),
        _schedule("Compact-Task1", "compactcpg SSD_r6", "0 0,5,10,15,17,20 * * *"),
        _schedule("Compact-Task2", "compactcpg -f SSD_r6", "0 0,5,10,15,17,20 * * *"),
        _schedule("SynRcopy_Schedule", "syncrcopy LZ_RcopyGroup1.r194089", "0 0 * * *", status="suspended"),
    ]
    plan = _plan([_req(every=1, unit="days", at_hour=0)], _view(schedules=midnight))
    assert plan.blockers == []
    assert any("5 schedules at 00:00" in n and "zz_sn_vvs_snap adds one" in n for n in plan.notes)
    quiet = _plan([_req(every=1, unit="days", at_hour=23)], _view(schedules=midnight))
    assert not any("adds one" in n for n in quiet.notes)


# ------------------------------------------------------------------ R6: removal order

def test_removal_runs_schedule_then_snapshots_then_the_provisioning_lines():
    from alletra_onboard.application.provisioning.storage_provision import render_removal_commands
    from alletra_onboard.domain.provisioning import RemovalItem

    items = [
        RemovalItem(kind="volume", name="zz_sn_vol01", command="removevv -f zz_sn_vol01"),
        RemovalItem(kind="vvset", name="zz_sn_vvs", command="removevvset -f zz_sn_vvs"),
        RemovalItem(kind="snapshot", name="zz_sn_vol01.initial", command="removevv -f zz_sn_vol01.initial"),
        RemovalItem(kind="schedule", name="zz_sn_vvs_snap", command="removesched -f zz_sn_vvs_snap"),
    ]
    assert render_removal_commands(items) == [
        "removesched -f zz_sn_vvs_snap",
        "removevv -f zz_sn_vol01.initial",
        "removevvset -f zz_sn_vvs",
        "removevv -f zz_sn_vol01",
    ]


# ------------------------------------------------------------------ R9: the step

def test_the_registry_has_the_snapshots_step_before_verify_and_the_presets_are_unchanged():
    from alletra_onboard.domain.models import RunMode
    from alletra_onboard.domain.workflow import STEP_REGISTRY, mode_steps

    keys = [s.key for s in STEP_REGISTRY]
    assert keys.index("failover_test") < keys.index("snapshots") < keys.index("verify")
    step = next(s for s in STEP_REGISTRY if s.key == "snapshots")
    assert (step.label, step.kind, step.phase.value) == ("Snapshots", "snapshot", "STORAGE_SNAPSHOT")
    assert all("snapshots" not in steps for mode, steps in mode_steps().items() if mode != RunMode.CUSTOM)
