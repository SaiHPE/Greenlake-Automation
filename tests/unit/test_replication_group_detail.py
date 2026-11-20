"""BL-64 (the owner, 2026-11-19): "show all volumes in rcgroup including config, showrcopy -d".

Verify reads `showrcopy -d groups <group>` on this array for every group the run configured and carries
the group's settings and every volume with the verdict. Pinned to the captures in
`tests/fixtures/rc_pair/` (OS 10.5.0, sync and periodic, 2026-10-07 to 10) and
`tests/fixtures/rcip_pair/showrcopy_d/` (rack13-ARCUS OS 10.6.0 and PRIMERA630R11U22 OS 4.6.20, 2026-11-19).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import SecretStr

from alletra_onboard.adapters.array.cli_client import refusal
from alletra_onboard.application.replication.read import (
    group_detail_command,
    parse_showrcopy_detail,
    read_array,
    read_group_details,
)
from alletra_onboard.application.replication.verify import verify
from alletra_onboard.domain.provisioning import ProvisioningIntent, VolumeRequest
from alletra_onboard.domain.replication import (
    ProtectionRequest,
    RcGroupDetail,
    RcVolumeDetail,
    ReplicationAction,
    ReplicationIntent,
    ReplicationPlan,
)
from alletra_onboard.domain.shared import EndpointCreds

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
RC_PAIR = FIXTURES / "rc_pair"
RCIP = FIXTURES / "rcip_pair" / "showrcopy_d"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="3paradm", password=SecretStr("pw"))


# ---- the parser ------------------------------------------------------------------------------------

def test_the_10_6_primary_shows_the_groups_settings_and_every_volume_column():
    (group,) = parse_showrcopy_detail(_text(RCIP / "alletra_showrcopy_d_groups_demo_rc_vvs_rcg.txt"))
    assert group == RcGroupDetail(
        name="demo_rc_vvs_rcg", id=27, target="PRIMERA630R11U22", status="Started", role="Primary", mode="Periodic",
        local_user_cpg="SSD_r6", remote_user_cpg="SSD_r6",
        options=["auto_recover", "over_per_alert", "auto_synchronize"], period="5m", last_sync="2026-11-19 16:13:56 IST",
        volumes=[RcVolumeDetail(
            local_name="demo_rc_vol01", local_id=138, remote_name="demo_rc_vol01", remote_id=51913, sync_status="Synced",
            resync_snapshot="rcpy.27.138.18", sync_snapshot="none", volume_iteration="185493/71",
            resync_iteration="185493/71", sync_iteration="NA", last_sync="2026-11-19 16:13:57 IST",
            local_set="demo_rc_vvs", remote_set="NA")],
    )


def test_the_whole_10_6_view_skips_the_target_and_link_tables():
    groups = parse_showrcopy_detail(_text(RCIP / "alletra_showrcopy_d.txt"))
    assert [(g.name, g.id, [v.local_name for v in g.volumes]) for g in groups] == [
        ("demo_rc_vvs_rcg", 27, ["demo_rc_vol01"]), ("zz_rc_test_rcg", 28, ["zz_rc_test_v01"])]
    assert groups[1].volumes[0].resync_snapshot == "rcpy.28.175.18.1"


def test_the_primera_secondary_has_snapshot_cpgs_and_no_volume_sets():
    """OS 4.6.20 prints LocalSnapCpg and RmSnapCpg; a secondary's Options have no Last-Sync; its volume header
    has no LocalSet / RemoteSet. Its IDs are right-aligned and start left of their heading."""
    group = parse_showrcopy_detail(_text(RCIP / "primera_showrcopy_d.txt"))[0]
    assert (group.name, group.id, group.role, group.local_snap_cpg, group.remote_snap_cpg) == (
        "demo_rc_vvs_rcg.r185493", 70, "Secondary", "SSD_r6", "SSD_r6")
    assert (group.period, group.last_sync, group.options) == ("5m", "", ["auto_recover", "over_per_alert", "auto_synchronize"])
    (volume,) = group.volumes
    assert (volume.local_name, volume.local_id, volume.remote_name, volume.remote_id) == ("demo_rc_vol01", 51913, "demo_rc_vol01", 138)
    assert (volume.volume_iteration, volume.resync_iteration, volume.last_sync) == ("185493/71", "NA", "2026-11-19 16:15:50 IST")
    assert (volume.local_set, volume.remote_set) == ("", "")


def test_the_10_5_sync_capture_reads_every_group_and_every_volume():
    groups = {g.name: g for g in parse_showrcopy_detail(_text(RC_PAIR / "after_apply" / "D22U27" / "showrcopy_d.txt"))}
    assert list(groups) == ["300gb", "APP_Test", "Intern_Automation", "Intern_Automation2", "Test-RCG", "Test-RCG2",
                            "zz_rc_test_rcg", "zz_rc_vvs_rcg"]
    assert [v.local_name for v in groups["Intern_Automation"].volumes] == ["Automation1", "Automation2", "Automation3", "Automation4"]
    assert groups["APP_Test"].options == ["auto_recover", "auto_synchronize", "active_active"]
    ours = groups["zz_rc_vvs_rcg"]
    assert (ours.id, ours.mode, ours.period, ours.local_user_cpg, ours.remote_user_cpg) == (25, "Sync", "", "SSD_r6", "SSD_r6")
    assert ours.volumes == [RcVolumeDetail(
        local_name="zz_rc_vol01", local_id=12367, remote_name="zz_rc_vol01", remote_id=1772, sync_status="Synced",
        resync_snapshot="none", sync_snapshot="none", volume_iteration="NA", resync_iteration="NA", sync_iteration="NA",
        last_sync="NA", local_set="zz_rc_vvs", remote_set="NA")]


def test_a_group_with_no_cpg_and_no_policy_reads_blank_not_shifted():
    """Test-RCG prints nothing under LocalUserCpg, RmUserCpg and Options: blanks, not the next column's words."""
    group = next(g for g in parse_showrcopy_detail(_text(RC_PAIR / "D22U27" / "showrcopy_d_groups.txt")) if g.name == "Test-RCG")
    assert (group.local_user_cpg, group.remote_user_cpg, group.options, group.status) == ("", "", [], "Started")
    assert [v.local_name for v in group.volumes] == ["TestRC_VV1", "TestRC_VV2"]


def test_the_10_5_periodic_capture_with_a_stopped_group_beside_it():
    groups = {g.name: g for g in parse_showrcopy_detail(
        _text(RC_PAIR / "after_apply_periodic" / "D22U27" / "showrcopy_d_groups.txt"))}
    stopped = groups["300gb"].volumes[0]
    assert (stopped.sync_status, stopped.resync_snapshot, stopped.last_sync) == ("Stopped", "rcpy.22.269.5", "2026-10-09 23:32:20 IST")
    ours = groups["zz_rc_vvs_rcg"]
    assert (ours.mode, ours.period, ours.last_sync) == ("Periodic", "5m", "2026-10-09 23:39:23 IST")
    assert (ours.volumes[0].volume_iteration, ours.volumes[0].resync_iteration) == ("188150/1", "188150/1")


def test_a_missing_group_is_no_block():
    assert parse_showrcopy_detail(_text(RC_PAIR / "D22U27" / "showrcopy_groups_rcopy_async_test.txt")) == []


# ---- the command and the allowlist ---------------------------------------------------------------

def test_the_detail_read_passes_the_read_allowlist():
    """`showrcopy` is on the allowlist; `-d` only displays more (the array's own help), `groups <name>` limits it."""
    help_text = _text(RC_PAIR / "help" / "help_showrcopy.txt")
    assert "    -d\n        Displays more detailed configuration information." in help_text
    assert group_detail_command("zz_rc_vvs_rcg") == "showrcopy -d groups zz_rc_vvs_rcg"
    assert refusal(group_detail_command("zz_rc_vvs_rcg")) is None
    assert refusal("showrcopy -d groups zz_rc_vvs_rcg; removercopygroup zz_rc_vvs_rcg") is not None


class _Cli:
    def __init__(self, answers: dict[str, str], sent: list[str]) -> None:
        self.answers, self.sent = answers, sent

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def run(self, command: str, timeout=None) -> str:
        self.sent.append(command)
        return self.answers[command]


def test_read_group_details_sends_one_read_per_group_and_names_a_missing_one():
    sent: list[str] = []
    whole = _text(RC_PAIR / "after_apply" / "D22U27" / "showrcopy_d.txt")
    missing = _text(RC_PAIR / "D22U27" / "showrcopy_groups_rcopy_async_test.txt")
    answers = {"showrcopy -d groups zz_rc_vvs_rcg": whole, "showrcopy -d groups gone_rcg": missing}
    details, errors = read_group_details(_creds("a"), ["zz_rc_vvs_rcg", "gone_rcg"],
                                         array_cli_factory=lambda c: _Cli(answers, sent))
    assert sent == ["showrcopy -d groups zz_rc_vvs_rcg", "showrcopy -d groups gone_rcg"]
    assert list(details) == ["zz_rc_vvs_rcg"] and details["zz_rc_vvs_rcg"].volumes[0].local_id == 12367
    assert list(errors) == ["gone_rcg"] and errors["gone_rcg"].startswith("Error: group matching")


def test_a_failed_login_is_every_groups_reason():
    from alletra_onboard.domain.errors import ArrayCliError

    def refuse(creds):
        raise ArrayCliError("Login failed")
    details, errors = read_group_details(_creds("a"), ["g1", "g2"], array_cli_factory=refuse)
    assert details == {} and errors == {"g1": "Could not read a: Login failed", "g2": "Could not read a: Login failed"}


# ---- Verify carries them -------------------------------------------------------------------------

_SHOWVV_A = "Name VSize_MB\nzz_rc_vol01 10240\nzz_rc_test_v01 1024\n"


class _After:
    """The 2026-10-09 23:39 periodic capture of the lab pair, as read_array reads it."""

    def __init__(self, array: str) -> None:
        self.array = array

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def run(self, command: str, timeout=None) -> str:
        if command.startswith("showvv "):
            return _SHOWVV_A if self.array == "D22U27" else "Name VSize_MB\n"
        name = command.replace(" -", "_").replace(" ", "_") + ".txt"
        after = RC_PAIR / "after_apply_periodic" / self.array / name
        return _text(after if after.exists() else RC_PAIR / self.array / name)


def _prov() -> ProvisioningIntent:
    intent = ProvisioningIntent(
        array=_creds("10.64.122.99"), vcenter=_creds("vc"), switch_f1=_creds(""), switch_f2=_creds(""),
        volumes=[VolumeRequest(name="zz_rc_vol01", size_gib=10, cpg="SSD_r6", vvset="zz_rc_vvs")],
    )
    intent.replication = ReplicationIntent(
        peer=_creds("10.64.154.190"),
        protections=[ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", mode="async", rpo_minutes=10)],
    )
    return intent


_PLAN = ReplicationPlan(actions=[
    ReplicationAction(kind="group", name="zz_rc_vvs_rcg", state="create",
                      detail={"vvset": "zz_rc_vvs", "mode": "async", "period_seconds": 300, "peer_vvset": "zz_rc_vvs_rc"}),
    ReplicationAction(kind="group", name="zz_rc_test_rcg", state="create",
                      detail={"vvset": "zz_rc_test", "mode": "async", "period_seconds": 300, "peer_vvset": "zz_rc_test_rc"}),
])


def _views():
    a = read_array(_creds("10.64.122.99"), array_cli_factory=lambda c: _After("D22U27"))
    b = read_array(_creds("10.64.154.190"), array_cli_factory=lambda c: _After("E18U31"))
    return iter([a, b])


def test_verify_carries_each_groups_settings_and_every_volume():
    asked: list = []
    whole = _text(RC_PAIR / "after_apply_periodic" / "D22U27" / "showrcopy_d_groups.txt")

    def detail_fn(creds, groups, progress=None):
        asked.append((creds.host, groups))
        return {g.name: g for g in parse_showrcopy_detail(whole) if g.name in groups}, {}

    reads = _views()
    out = verify(_prov(), _PLAN, read_fn=lambda creds, progress=None: next(reads), detail_fn=detail_fn)
    assert asked == [("10.64.122.99", ["zz_rc_vvs_rcg", "zz_rc_test_rcg"])]         # this array, the run's groups only
    assert [g.verdict for g in out.groups] == ["replicating", "replicating"]          # the verdict is unchanged
    config = out.groups[0].config
    assert (config.name, config.mode, config.period, config.rpo_minutes, config.target) == (
        "zz_rc_vvs_rcg", "Periodic", "5m", 10, "AlletraMP_E18U31")
    assert [v.local_name for v in config.volumes] == ["zz_rc_vol01"]
    assert out.groups[1].config.rpo_minutes == 10          # the test group: twice its planned period
    event = out.model_dump(mode="json")
    assert event["groups"][0]["config"]["volumes"][0]["resync_snapshot"] == "rcpy.27.12373.5"


def test_a_group_whose_settings_could_not_be_read_is_a_note_not_a_failure():
    reads = _views()
    out = verify(_prov(), _PLAN, read_fn=lambda creds, progress=None: next(reads),
                 detail_fn=lambda creds, groups, progress=None: ({}, {g: "Login failed" for g in groups}))
    assert out.error is None and [g.config for g in out.groups] == [None, None]
    assert "The settings and volumes of zz_rc_vvs_rcg could not be read (showrcopy -d): Login failed" in out.notes


def test_without_a_detail_reader_verify_sends_no_detail_read():
    reads = _views()
    out = verify(_prov(), _PLAN, read_fn=lambda creds, progress=None: next(reads))
    assert [g.config for g in out.groups] == [None, None]


def test_the_live_run_reads_back_what_its_verify_reported():
    """Run 5ee6d1b9 (2026-11-19, rack13-ARCUS OS 10.6.0 -> PRIMERA630R11U22, async): the tool's own reads
    from the command log parse to the `config` its replication.verified event carried."""
    import json

    live = RCIP / "live_run_5ee6d1b9"
    event = json.loads(_text(live / "replication_verified.json"))
    groups = {g["group"]: g for g in event["verification"]["groups"]}
    assert set(groups) == {"zz_rc_vvs_rcg", "zz_rc_test_rcg"}
    for name, group in groups.items():
        (parsed,) = parse_showrcopy_detail(_text(live / f"showrcopy_d_groups_{name}.txt"))
        assert group["verdict"] == "replicating"
        assert parsed.model_copy(update={"rpo_minutes": 10}) == RcGroupDetail.model_validate(group["config"])
    vol = RcGroupDetail.model_validate(groups["zz_rc_vvs_rcg"]["config"]).volumes[0]
    assert (vol.local_name, vol.local_id, vol.remote_id, vol.resync_snapshot, vol.volume_iteration) == (
        "zz_rc_vol01", 326, 52064, "rcpy.29.326.19", "185493/1")
