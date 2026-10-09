"""SPEC-016 R2 (check) and R3 (plan) over the lab pair's fixtures: the partnership found by address,
each finding's sentence, exists / create / conflict, the WSAPI call with its CLI equivalent, and
R9 (existing groups listed, never planned)."""

from pathlib import Path

from pydantic import SecretStr

from alletra_onboard.application.replication.plan import build_plan, check, find_partnership
from alletra_onboard.application.replication.read import read_array
from alletra_onboard.domain.provisioning import ProvisioningIntent, VolumeRequest
from alletra_onboard.domain.replication import (
    TEST_GROUP,
    TEST_PEER_VVSET,
    TEST_VOLUME,
    TEST_VVSET,
    ProtectionRequest,
    ReplicationIntent,
)
from alletra_onboard.domain.shared import EndpointCreds

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "rc_pair"


class _Cli:
    def __init__(self, array: str, *, showvv: str = "", overrides: dict[str, str] | None = None) -> None:
        self.array, self.showvv, self.overrides = array, showvv, overrides or {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def run(self, command: str, timeout=None) -> str:
        if command in self.overrides:
            return self.overrides[command]
        if command.startswith("showvv "):
            return self.showvv
        return (_FIXTURES / self.array / (command.replace(" -", "_").replace(" ", "_") + ".txt")).read_text(encoding="utf-8")


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="3paradm", password=SecretStr("pw"))


# zz_rc_vvs is this run's freshly provisioned set (two 10 GiB volumes), present on D22U27's showvvset
# only through the override below; 300gb is the pre-existing set already in group 300gb.
_SHOWVV_A = "Name VSize_MB\n300gb 307200\nTest 1024\nzz_rc_vol01 10240\nzz_rc_vol02 10240\nzz_rc_test_v01 1024\n"
_VVSET_A_EXTRA = (_FIXTURES / "D22U27" / "showvvset.txt").read_text(encoding="utf-8") + \
    "90 zz_rc_vvs                       zz_rc_vol01              \n                                   zz_rc_vol02              \n"


def _views(*, a_overrides: dict[str, str] | None = None, b_overrides: dict[str, str] | None = None):
    a = read_array(_creds("10.64.122.99"), array_cli_factory=lambda c: _Cli("D22U27", showvv=_SHOWVV_A, overrides={"showvvset": _VVSET_A_EXTRA, **(a_overrides or {})}))
    b = read_array(_creds("10.64.154.190"), array_cli_factory=lambda c: _Cli("E18U31", showvv="Name VSize_MB\n", overrides=b_overrides or {}))
    return a, b


def _intent(rows=None, *, rtt=2.0, failover=True) -> ReplicationIntent:
    # The lab target carries six Sync groups, so the default row is sync (one mode per target).
    return ReplicationIntent(
        peer=_creds("10.64.154.190"), rtt_ms=rtt, failover_test=failover,
        protections=rows if rows is not None else [ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", mode="sync", rpo_minutes=None)],
    )


_ASYNC_ROW = ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6")          # async, RPO 10
# The primary's showrcopy with its Group Information emptied: a target that carries no group yet.
_RC_A_NO_GROUPS = (_FIXTURES / "D22U27" / "showrcopy.txt").read_text(encoding="utf-8").split("Group Information")[0] + "Group Information\n\n"


def _prov() -> ProvisioningIntent:
    return ProvisioningIntent(
        array=_creds("10.64.122.99"), vcenter=_creds("vc"), switch_f1=_creds(""), switch_f2=_creds(""),
        volumes=[VolumeRequest(name="zz_rc_vol01", size_gib=10, cpg="SSD_r6", vvset="zz_rc_vvs"),
                 VolumeRequest(name="zz_rc_vol02", size_gib=10, cpg="SSD_r6", vvset="zz_rc_vvs")],
    )


# ------------------------------------------------------------------ the partnership

def test_partnership_is_found_by_link_address_despite_the_misnamed_peer_target():
    a, b = _views()
    p = find_partnership(a, b)
    assert p is not None
    assert (p.target_on_primary, p.target_on_peer) == ("AlletraMP_E18U31", "AlletraMP_E18U31")   # the peer's own name, both sides
    assert (p.links_primary_up, p.links_primary_total, p.links_peer_up, p.links_peer_total) == (2, 2, 2, 2)
    assert p.mirror_config


def test_no_partnership_when_the_links_point_elsewhere():
    a, b = _views(b_overrides={"showport -rcip": "N:S:P State HwAddr IPAddr Netmask Gateway MTU Rate\n0:4:3 ready 00 10.9.9.1 255.255.255.0 - 1500 10Gbps\n"})
    assert find_partnership(a, b) is None
    report = check(a, b, _intent())
    assert any("No Remote Copy partnership between AlletraMP_D22U27 and AlletraMP_E18U31" in f and "v0.19" in f for f in report.findings)


# ------------------------------------------------------------------ R2 findings

def test_a_clean_pair_and_a_fresh_set_has_no_findings():
    a, b = _views()
    report = check(a, b, _intent())
    assert report.findings == [] and report.error is None


def test_an_async_row_on_a_target_that_carries_sync_groups_is_a_finding():
    # The live lesson of 2026-10-09: every write succeeded and the START was refused (HTTP 400 code 236,
    # "Group with different modes on a single target is not supported"). The check says so first.
    a, b = _views()
    report = check(a, b, _intent([_ASYNC_ROW]))
    [finding] = report.findings
    assert finding == (
        "Target 'AlletraMP_E18U31' already carries 6 sync group(s) (300gb, APP_Test, Intern_Automation, Intern_Automation2…); "
        "every group on one target must replicate in the same mode (HPE Support Matrix), so async groups cannot be started "
        "there. Use sync on the Replication tab, or a second target over spare RCIP ports (a link belongs "
        "to one target; the tool configures targets from v0.19)."
    )


def test_mixed_modes_on_the_tab_with_one_target_is_a_finding():
    a, b = _views(a_overrides={"showrcopy": _RC_A_NO_GROUPS})
    rows = [ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", mode="sync", rpo_minutes=None),
            ProtectionRequest(vvset="300gb", peer_cpg="SSD_r6")]
    report = check(a, b, _intent(rows))
    [finding] = [f for f in report.findings if "mixes" in f]
    assert finding == (
        "The Replication tab mixes sync and async rows and AlletraMP_D22U27 → AlletraMP_E18U31 has one target "
        "('AlletraMP_E18U31'); every group on one target must replicate in the same mode (HPE Support Matrix). Make all "
        "rows one mode, or add a second target over spare RCIP ports (a link belongs to one target; the tool configures "
        "targets from v0.19)."
    )
    assert report.partnership.target_by_mode == {"sync": "AlletraMP_E18U31"}


def test_stopped_groups_of_the_other_mode_are_still_a_finding_with_the_honest_sentence():
    # after_apply_periodic/: the six Sync groups STOPPED and the tool's two periodic groups started —
    # the array accepted that start (live 2026-10-09 23:39). The tool still refuses to plan it, and
    # says why; this run's own groups on the target are not "existing".
    periodic = _FIXTURES / "after_apply_periodic"
    a, b = _views(a_overrides={"showrcopy": (periodic / "D22U27" / "showrcopy.txt").read_text(encoding="utf-8")},
                  b_overrides={"showrcopy": (periodic / "E18U31" / "showrcopy.txt").read_text(encoding="utf-8")})
    # with the tool's own groups present this is a rerun and the target is theirs: no finding
    assert check(a, b, _intent([_ASYNC_ROW])).findings == []
    a.groups = [g for g in a.groups if not g.name.startswith("zz_rc_")]
    b.groups = [g for g in b.groups if not g.name.startswith("zz_rc_")]
    report = check(a, b, _intent([_ASYNC_ROW]))
    [finding] = report.findings
    assert finding == (
        "Target 'AlletraMP_E18U31' already carries 6 sync group(s) (300gb, APP_Test, Intern_Automation, Intern_Automation2…), "
        "all stopped. The array would start async groups beside them, but every group on one target must replicate in the "
        "same mode (HPE Support Matrix), so the tool will not put their restart at risk. Use sync on the Replication tab, or "
        "a second target over spare RCIP ports (a link belongs to one target; the tool configures targets from v0.19)."
    )


# ---- a pair laid out the way HPE describes for mixed modes: a target per mode over links of its own

_PORTS = ("0:4:3", "1:4:3", "0:4:4", "1:4:4")
_A_IPS = ("10.54.122.92", "10.54.122.93", "10.54.122.94", "10.54.122.95")
_B_IPS = ("10.54.154.192", "10.54.154.193", "10.54.154.194", "10.54.154.195")


def _second_target(array: str, mine: tuple[str, ...], theirs: tuple[str, ...], second: str, *, second_up: bool = True) -> dict[str, str]:
    """Overrides giving `array` four RCIP ports and a second target `second` over 0:4:4 / 1:4:4, the
    first target and the fixture's groups untouched."""
    ports = "N:S:P State HwAddr IPAddr Netmask/PrefixLen Gateway MTU Rate Duplex AutoNeg\n" + \
        "".join(f"{nsp} ready 00 {ip} 255.255.248.0 - 1500 10Gbps Full Yes\n" for nsp, ip in zip(_PORTS, mine))
    groups = (_FIXTURES / array / "showrcopy.txt").read_text(encoding="utf-8").split("Group Information")[1]
    up = "Up" if second_up else "Down"
    rc = ("Remote Copy System Information\nStatus: Started, Normal\n\nTarget Information\n\n"
          "Name ID Type Status Options Policy\nAlletraMP_E18U31 5 IP ready - mirror_config\n"
          f"{second} 6 IP ready - mirror_config\n\nLink Information\n\nTarget Node Address Status Options\n"
          f"AlletraMP_E18U31 0:4:3 {theirs[0]} Up -\nAlletraMP_E18U31 1:4:3 {theirs[1]} Up -\n"
          f"{second} 0:4:4 {theirs[2]} {up} -\n{second} 1:4:4 {theirs[3]} {up} -\n"
          + "".join(f"receive {nsp} {ip} Up -\n" for nsp, ip in zip(_PORTS, mine)) + "\nGroup Information" + groups)
    return {"showport -rcip": ports, "showrcopy": rc}


def _two_target_views(**kw):
    return _views(a_overrides=_second_target("D22U27", _A_IPS, _B_IPS, "E18U31_async", **kw),
                  b_overrides=_second_target("E18U31", _B_IPS, _A_IPS, "D22U27_async", **kw))


def test_two_targets_are_paired_by_the_ports_they_share_not_by_order_or_name():
    a, b = _two_target_views()
    p = find_partnership(a, b, modes={"sync", "async"})
    assert [(t.name, t.peer_name, t.links_up, t.peer_links_up, t.modes, t.groups) for t in p.targets] == [
        ("AlletraMP_E18U31", "AlletraMP_E18U31", 2, 2, ["sync"], 6),
        ("E18U31_async", "D22U27_async", 2, 2, [], 0),
    ]
    assert p.target_by_mode == {"sync": "AlletraMP_E18U31", "async": "E18U31_async"}


def test_mixed_rows_on_a_pair_with_a_target_per_mode_have_no_finding_and_each_row_gets_its_target():
    a, b = _two_target_views()
    rows = [ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", mode="sync", rpo_minutes=None),
            ProtectionRequest(vvset="zz_rc_vvs2", peer_cpg="SSD_r6")]
    a.vvsets["zz_rc_vvs2"] = ["zz_rc_vol02"]
    a.vvsets["zz_rc_vvs"] = ["zz_rc_vol01"]
    intent = _intent(rows, failover=False)
    report = check(a, b, intent)
    assert report.findings == []
    plan = build_plan(report, intent, _prov())
    by = {x.name: x for x in plan.actions if x.kind == "group"}
    assert by["zz_rc_vvs_rcg"].detail["target"] == "AlletraMP_E18U31"
    assert by["zz_rc_vvs2_rcg"].detail["target"] == "E18U31_async"
    assert by["zz_rc_vvs2_rcg"].calls[0].cli.endswith("zz_rc_vvs2_rcg E18U31_async:periodic")
    assert any(n == "Target per mode this run: async → 'E18U31_async', sync → 'AlletraMP_E18U31'." for n in plan.notes)


def test_an_async_row_goes_to_the_free_target_when_the_first_carries_sync_groups():
    a, b = _two_target_views()
    intent = _intent([_ASYNC_ROW])
    report = check(a, b, intent)
    assert report.findings == []
    assert report.partnership.target_on_primary == "E18U31_async"       # the one this run uses
    plan = build_plan(report, intent, _prov())
    group = next(x for x in plan.actions if x.kind == "group" and x.name == "zz_rc_vvs_rcg")
    assert group.detail["target"] == "E18U31_async"
    test_group = next(x for x in plan.actions if x.kind == "group" and x.name == TEST_GROUP)
    assert test_group.detail["target"] == "E18U31_async" and test_group.detail["mode"] == "async"


def test_links_are_judged_on_the_target_the_run_uses():
    a, b = _two_target_views(second_up=False)
    report = check(a, b, _intent([_ASYNC_ROW]))
    [finding] = report.findings
    assert finding == ("The partnership needs at least 2 links Up each way: AlletraMP_D22U27 → AlletraMP_E18U31 via target "
                       "'E18U31_async' has 0 of 2 Up, AlletraMP_E18U31 → AlletraMP_D22U27 via 'D22U27_async' has 0 of 2 Up.")
    assert check(a, b, _intent()).findings == []          # the sync target's links are fine


def test_a_rerun_keeps_a_group_on_the_target_it_was_created_on():
    # This run's async group already sits on the SECOND target; the first is empty on this view, so
    # "first empty target" would move it and conflict. The rerun must find it where it is.
    a, b = _two_target_views()
    a.groups = [g for g in a.groups if g.name == "300gb"]
    a.groups[0].name, a.groups[0].target, a.groups[0].mode = "zz_rc_vvs_rcg", "E18U31_async", "Periodic"
    a.groups[0].volumes = []
    intent = _intent([_ASYNC_ROW], failover=False)
    report = check(a, b, intent)
    assert report.partnership.target_by_mode == {"async": "E18U31_async"}


def test_a_fibre_channel_only_pair_says_so():
    fc = ("Remote Copy System Information\nStatus: Started, Normal\n\nTarget Information\n\n"
          "Name ID Type Status Options Policy\nSiteB 1 FC ready - mirror_config\n\nLink Information\n\n"
          "Target Node Address Status Options\nSiteB 0:3:2 20320202AC02DEF2 Up -\n\nGroup Information\n\n")
    a, b = _views(a_overrides={"showrcopy": fc, "showport -rcip": "There is no specified port information\n"})
    report = check(a, b, _intent())
    assert any(f.startswith("No Remote Copy partnership") for f in report.findings)
    assert any(f == "Remote Copy over Fibre Channel target(s) found (SiteB); this release supports Remote Copy over IP only (ADR 0015)."
               for f in report.findings)


def test_an_async_row_on_a_target_with_no_groups_has_no_mode_finding():
    a, b = _views(a_overrides={"showrcopy": _RC_A_NO_GROUPS})
    assert check(a, b, _intent([_ASYNC_ROW])).findings == []


def test_each_finding_has_its_sentence():
    a, b = _views()
    sync = dict(mode="sync", rpo_minutes=None)
    # a volume already in another group
    report = check(a, b, _intent([ProtectionRequest(vvset="300gb", peer_cpg="SSD_r6", **sync)]))
    assert any("Volume '300gb' (in set '300gb') is already in Remote Copy group '300gb'" in f for f in report.findings)
    # a set that is not on the primary
    report = check(a, b, _intent([ProtectionRequest(vvset="ghost", peer_cpg="SSD_r6", **sync)]))
    assert any("Volume set 'ghost' does not exist on AlletraMP_D22U27" in f for f in report.findings)
    # an empty set (New-test is '--' in the fixture)
    report = check(a, b, _intent([ProtectionRequest(vvset="New-test", peer_cpg="SSD_r6", **sync)]))
    assert any("'New-test' on AlletraMP_D22U27 is empty" in f for f in report.findings)
    # a peer CPG the peer does not have (E18U31 has only SSD_r6)
    report = check(a, b, _intent([ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="test", **sync)]))
    assert any("Peer CPG 'test' does not exist on AlletraMP_E18U31 (it has: SSD_r6)" in f for f in report.findings)
    # RTT over the limit for the mode
    report = check(a, b, _intent([ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", **sync)], rtt=12))
    assert any("12 ms; sync replication over RCIP needs 10 ms or less" in f for f in report.findings)


def test_remote_copy_not_started_and_too_few_links_are_findings():
    stopped = (_FIXTURES / "E18U31" / "showrcopy.txt").read_text(encoding="utf-8") \
        .replace("Status: Started, Normal", "Status: Stopped, Normal") \
        .replace("AlletraMP_E18U31 1:4:3 10.54.122.93  Up", "AlletraMP_E18U31 1:4:3 10.54.122.93  Down")
    a, b = _views(b_overrides={"showrcopy": stopped})
    report = check(a, b, _intent())
    assert any("Remote Copy is not started on AlletraMP_E18U31 (showrcopy says 'Stopped')" in f for f in report.findings)
    assert any("AlletraMP_E18U31 → AlletraMP_D22U27 via 'AlletraMP_E18U31' has 1 of 2 Up" in f for f in report.findings)


def test_a_peer_cpg_too_small_is_a_finding():
    a, b = _views(b_overrides={"showcpg": "Id Name Warn% VVs TPVVs TDVVs Used Free Total\n 0 SSD_r6 - 1 1 0 100 2048 2148\n"})
    report = check(a, b, _intent())
    assert any("Peer CPG 'SSD_r6' on AlletraMP_E18U31 has 2 GiB free; the volumes in 'zz_rc_vvs' need 20 GiB" in f for f in report.findings)


def test_a_failed_read_is_the_report_error():
    a, b = _views()
    a.read_error = "Could not read 10.64.122.99: Login failed"
    report = check(a, b, _intent())
    assert report.error == "Could not read 10.64.122.99: Login failed" and report.findings == []
    assert build_plan(report, _intent(), _prov()).error == report.error


# ------------------------------------------------------------------ R3 plan

def test_plan_creates_the_group_the_peer_set_and_the_test_objects_with_wsapi_and_cli():
    # An async row on a target with no groups yet: the full periodic rendering.
    a, b = _views(a_overrides={"showrcopy": _RC_A_NO_GROUPS})
    intent = _intent([_ASYNC_ROW])
    plan = build_plan(check(a, b, intent), intent, _prov())
    assert plan.blockers == [] and plan.error is None
    by = {(x.kind, x.name): x for x in plan.actions}
    g = by[("group", "zz_rc_vvs_rcg")]
    assert g.state == "create" and g.where == "A"
    assert "async, RPO 10 min (period 5 min) → AlletraMP_E18U31, 2 volume(s) from set 'zz_rc_vvs', secondaries on SSD_r6" == g.reason
    calls = [(c.where, c.cli) for c in g.calls]
    assert calls == [
        ("A", "creatercopygroup -usr_cpg SSD_r6 AlletraMP_E18U31:SSD_r6 zz_rc_vvs_rcg AlletraMP_E18U31:periodic"),
        ("A", "setrcopygroup period 5m AlletraMP_E18U31 zz_rc_vvs_rcg ; setrcopygroup pol auto_recover zz_rc_vvs_rcg ; setrcopygroup pol auto_synchronize zz_rc_vvs_rcg"),
        ("A", "admitrcopyvv -createvv zz_rc_vol01 zz_rc_vvs_rcg AlletraMP_E18U31:zz_rc_vol01"),
        ("A", "admitrcopyvv -createvv zz_rc_vol02 zz_rc_vvs_rcg AlletraMP_E18U31:zz_rc_vol02"),
        ("A", "startrcopygroup zz_rc_vvs_rcg"),
    ]
    assert g.calls[0].wsapi.startswith("POST /remotecopygroups {name: zz_rc_vvs_rcg, targets: [{targetName: AlletraMP_E18U31, mode: 2, userCPG: SSD_r6}], localUserCPG: SSD_r6}")
    assert "syncPeriod: 300" in g.calls[1].wsapi and "autoRecover: true" in g.calls[1].wsapi
    assert "volumeAutoCreation: true" in g.calls[2].wsapi
    peer_set = by[("peer_vvset", "zz_rc_vvs_rc")]
    assert peer_set.state == "create" and peer_set.where == "B" and peer_set.calls[0].cli == "createvvset zz_rc_vvs_rc zz_rc_vol01 zz_rc_vol02"
    # R4 order across the whole plan: test objects first; per group create → policies → admits → the
    # peer set that groups the secondaries → start; every call numbered once, in that order.
    ordered = sorted((c for x in plan.actions for c in x.calls), key=lambda c: c.seq)
    assert [c.seq for c in ordered] == list(range(1, len(ordered) + 1))
    clis = [c.cli for c in ordered]
    assert clis.index("createvvset zz_rc_vvs_rc zz_rc_vol01 zz_rc_vol02") < clis.index("startrcopygroup zz_rc_vvs_rcg")
    assert clis[0].startswith("createvv -tpvv") or clis[0].startswith("createvvset zz_rc_test ")
    # the failover test's own objects (SPEC-015 R3): volume + set on A, group IN THE ROWS' MODE, peer set on B
    assert by[("test_volume", TEST_VOLUME)].state == "exists"       # already on the array in _SHOWVV_A
    assert by[("test_vvset", TEST_VVSET)].state == "create"
    tg = by[("group", TEST_GROUP)]
    assert tg.state == "create" and tg.calls[0].cli.endswith(f"{TEST_GROUP} AlletraMP_E18U31:periodic")
    assert by[("peer_vvset", TEST_PEER_VVSET)].state == "create"
    assert plan.existing_groups == []
    assert any("named '<group>.r188150'" in n for n in plan.notes)


def test_on_the_lab_pair_the_rows_are_sync_and_so_is_the_test_group_and_existing_groups_are_listed():
    a, b = _views()
    intent = _intent()
    plan = build_plan(check(a, b, intent), intent, _prov())
    assert plan.blockers == []
    groups = {x.name: x for x in plan.actions if x.kind == "group"}
    assert groups["zz_rc_vvs_rcg"].calls[0].cli.endswith("AlletraMP_E18U31:sync")
    assert groups[TEST_GROUP].calls[0].cli.endswith("AlletraMP_E18U31:sync")          # follows the rows' mode
    assert all("period" not in c.cli for g in groups.values() for c in g.calls)
    # R9: the six pre-existing groups are listed and not planned
    assert plan.existing_groups == ["300gb", "APP_Test", "Intern_Automation", "Intern_Automation2", "Test-RCG", "Test-RCG2"]
    assert any("will not be touched" in n for n in plan.notes)


def test_sync_row_has_no_period_and_mode_1():
    a, b = _views()
    intent = _intent([ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", mode="sync", rpo_minutes=None)], rtt=3, failover=False)
    plan = build_plan(check(a, b, intent), intent, _prov())
    [g] = [x for x in plan.actions if x.kind == "group"]
    assert g.reason.startswith("sync → AlletraMP_E18U31")
    assert "mode: 1" in g.calls[0].wsapi and g.calls[0].cli.endswith("AlletraMP_E18U31:sync")
    assert "syncPeriod" not in g.calls[1].wsapi and "period" not in g.calls[1].cli
    assert not any(x.kind.startswith("test_") for x in plan.actions)


def test_an_existing_matching_group_is_exists_and_a_differing_one_is_a_conflict():
    rc_a = (_FIXTURES / "D22U27" / "showrcopy.txt").read_text(encoding="utf-8")
    # make the fixture's `300gb` group look like what the row would derive for set 300gb: name 300gb_rcg
    renamed = rc_a.replace("300gb        AlletraMP_E18U31 Started  Primary    Sync", "300gb_rcg    AlletraMP_E18U31 Started  Primary    Sync")
    a, b = _views(a_overrides={"showrcopy": renamed})
    row_match = ProtectionRequest(vvset="300gb", peer_cpg="SSD_r6", mode="sync", rpo_minutes=None)
    intent = _intent([row_match], rtt=2, failover=False)
    plan = build_plan(check(a, b, intent), intent, _prov())
    [g] = [x for x in plan.actions if x.kind == "group"]
    assert g.state == "exists" and g.reason == "Started, Primary, Sync, 2 volume(s)" and plan.blockers == []
    assert "300gb_rcg" not in plan.existing_groups

    row_diff = ProtectionRequest(vvset="300gb", peer_cpg="SSD_r6")       # async where the array has sync
    intent = _intent([row_diff], failover=False)
    plan = build_plan(check(a, b, intent), intent, _prov())
    [g] = [x for x in plan.actions if x.kind == "group"]
    assert g.state == "conflict" and g.reason == "exists but is sync, the sheet asks for async"
    assert (
        "Remote Copy group '300gb_rcg' exists on AlletraMP_D22U27 but is sync, the sheet asks for async. "
        "The tool never changes an existing group; remove it on the array or rename the volume set."
    ) in plan.blockers
    assert any("every group on one target must replicate in the same mode" in f for f in plan.blockers)


def test_no_mirror_config_starts_on_the_peer_first():
    rc_a = (_FIXTURES / "D22U27" / "showrcopy.txt").read_text(encoding="utf-8").replace("-       mirror_config", "-       no_mirror_config")
    a, b = _views(a_overrides={"showrcopy": rc_a})
    intent = _intent(failover=False)
    plan = build_plan(check(a, b, intent), intent, _prov())
    [g] = [x for x in plan.actions if x.kind == "group"]
    start = g.calls[-1]
    assert start.where == "B" and "on the peer first" in start.wsapi and start.cli == "startrcopygroup zz_rc_vvs_rcg"
