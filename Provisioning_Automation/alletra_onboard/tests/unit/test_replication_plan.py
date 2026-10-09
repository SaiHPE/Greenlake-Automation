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


def test_mixed_modes_on_the_tab_is_a_finding():
    a, b = _views(a_overrides={"showrcopy": _RC_A_NO_GROUPS})
    rows = [ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", mode="sync", rpo_minutes=None),
            ProtectionRequest(vvset="300gb", peer_cpg="SSD_r6")]
    report = check(a, b, _intent(rows))
    assert any(f.startswith("The Replication tab mixes async and sync rows") for f in report.findings)


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
    assert any("AlletraMP_E18U31 → AlletraMP_D22U27 has 1 of 2 Up" in f for f in report.findings)


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
