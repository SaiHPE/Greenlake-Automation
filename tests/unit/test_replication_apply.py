"""SPEC-016 R4 (apply), R6 (verify) and R7 (removal set) with a fake WSAPI client: the fixed order,
exists-on-rerun, stop-at-first-failure with the removal set bounded to what was created, and the
verdicts from `showrcopy` states."""

from pathlib import Path

import pytest
from pydantic import SecretStr

from alletra_onboard.application.replication.apply import apply_plan
from alletra_onboard.application.replication.plan import build_plan, check
from alletra_onboard.application.replication.read import read_array
from alletra_onboard.application.replication.verify import peer_group_name, verify
from alletra_onboard.domain.provisioning import ProvisioningIntent, VolumeRequest
from alletra_onboard.domain.replication import (
    ProtectionRequest,
    RcGroup,
    RcGroupVolume,
    ReplicationAction,
    ReplicationArrayView,
    ReplicationIntent,
    ReplicationPlan,
)
from alletra_onboard.domain.shared import EndpointCreds

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "rc_pair"


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="3paradm", password=SecretStr("pw"))


# ------------------------------------------------------------------ a plan from the lab pair fixtures

class _Cli:
    def __init__(self, array: str, *, showvv: str, vvset_extra: str = "", overrides: dict | None = None) -> None:
        self.array, self.showvv, self.vvset_extra, self.overrides = array, showvv, vvset_extra, overrides or {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def run(self, command: str, timeout=None) -> str:
        if command in self.overrides:
            return self.overrides[command]
        if command.startswith("showvv "):
            return self.showvv
        text = (_FIXTURES / self.array / (command.replace(" -", "_").replace(" ", "_") + ".txt")).read_text(encoding="utf-8")
        return text + (self.vvset_extra if command == "showvvset" else "")


_SHOWVV_A = "Name VSize_MB\n300gb 307200\nTest 1024\nzz_rc_vol01 10240\nzz_rc_vol02 10240\n"
_VVSET_A_EXTRA = "90 zz_rc_vvs                       zz_rc_vol01              \n                                   zz_rc_vol02              \n"


def _views(a_overrides=None, b_overrides=None):
    a = read_array(_creds("10.64.122.99"), array_cli_factory=lambda c: _Cli("D22U27", showvv=_SHOWVV_A, vvset_extra=_VVSET_A_EXTRA, overrides=a_overrides))
    b = read_array(_creds("10.64.154.190"), array_cli_factory=lambda c: _Cli("E18U31", showvv="Name VSize_MB\n", overrides=b_overrides))
    return a, b


def _prov(*, failover=True) -> ProvisioningIntent:
    intent = ProvisioningIntent(
        array=_creds("10.64.122.99"), vcenter=_creds("vc"), switch_f1=_creds(""), switch_f2=_creds(""),
        volumes=[VolumeRequest(name="zz_rc_vol01", size_gib=10, cpg="SSD_r6", vvset="zz_rc_vvs"),
                 VolumeRequest(name="zz_rc_vol02", size_gib=10, cpg="SSD_r6", vvset="zz_rc_vvs")],
    )
    intent.replication = ReplicationIntent(
        peer=_creds("10.64.154.190"), rtt_ms=1.0, failover_test=failover,
        # the lab target carries six Sync groups: one mode per target, so the row is sync
        protections=[ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", mode="sync", rpo_minutes=None)],
    )
    return intent


def _plan(prov: ProvisioningIntent) -> ReplicationPlan:
    a, b = _views()
    return build_plan(check(a, b, prov.replication), prov.replication, prov)


# ------------------------------------------------------------------ the fake WSAPI client

class _FakeWsapi:
    """Records every write in order; `existing` names answer 'exists'; `fail_at` raises on that call."""

    def __init__(self, label: str, log: list, *, existing: set[str] | None = None, fail_at: str | None = None) -> None:
        self.label, self.log, self.existing, self.fail_at = label, log, existing or set(), fail_at

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def _call(self, what: str, name: str) -> str:
        key = f"{what} {name}"
        self.log.append((self.label, key))
        if self.fail_at == key:
            raise RuntimeError(f"array refused {key}: simulated")
        return "exists" if name in self.existing else "created"

    def ensure_volume(self, name, cpg, size_mib, ptype):
        return self._call("createvv", name)

    def ensure_volume_set(self, name, members):
        return self._call("createvvset", name)

    def create_remote_copy_group(self, name, *, target, mode, peer_cpg, local_cpg=""):
        return self._call("creatercopygroup", name)

    def set_remote_copy_group(self, name, *, target, period_seconds, auto_recover, auto_synchronize):
        self.log.append((self.label, f"setrcopygroup {name} period={period_seconds} ar={auto_recover} as={auto_synchronize}"))
        return ""

    def admit_remote_copy_volume(self, group, volume, *, target, secondary=None):
        return self._call("admitrcopyvv", f"{volume}->{group}")

    def start_remote_copy_group(self, name):
        status = self._call("startrcopygroup", name)
        return "started" if status == "created" else status


def _factory(log, *, a: _FakeWsapi | None = None, b: _FakeWsapi | None = None):
    a = a or _FakeWsapi("A", log)
    b = b or _FakeWsapi("B", log)

    def make(creds):
        return a if creds.host == "10.64.122.99" else b
    return make


# ------------------------------------------------------------------ R4: order

def test_apply_writes_in_the_fixed_order_and_builds_both_removal_blocks():
    prov = _prov()
    plan = _plan(prov)
    log: list = []
    result = apply_plan(plan, prov, wsapi_factory=_factory(log))
    assert result.error is None
    assert result.groups_created == ["zz_rc_vvs_rcg", "zz_rc_test_rcg"]
    assert log == [
        ("A", "createvv zz_rc_test_v01"),
        ("A", "createvvset zz_rc_test"),
        ("A", "creatercopygroup zz_rc_vvs_rcg"),
        ("A", "setrcopygroup zz_rc_vvs_rcg period=None ar=True as=True"),
        ("A", "admitrcopyvv zz_rc_vol01->zz_rc_vvs_rcg"),
        ("A", "admitrcopyvv zz_rc_vol02->zz_rc_vvs_rcg"),
        ("B", "createvvset zz_rc_vvs_rc"),
        ("A", "startrcopygroup zz_rc_vvs_rcg"),
        ("A", "creatercopygroup zz_rc_test_rcg"),
        ("A", "setrcopygroup zz_rc_test_rcg period=None ar=True as=True"),
        ("A", "admitrcopyvv zz_rc_test_v01->zz_rc_test_rcg"),
        ("B", "createvvset zz_rc_test_rc"),
        ("A", "startrcopygroup zz_rc_test_rcg"),
    ]
    # R7: groups first (stop, dismiss each volume, remove), then the test set, then the test volume; B separately
    assert result.removals_a == [
        "stoprcopygroup -f zz_rc_vvs_rcg",
        "dismissrcopyvv -f -removevv zz_rc_vol01 zz_rc_vvs_rcg",
        "dismissrcopyvv -f -removevv zz_rc_vol02 zz_rc_vvs_rcg",
        "removercopygroup -f zz_rc_vvs_rcg",
        "stoprcopygroup -f zz_rc_test_rcg",
        "dismissrcopyvv -f -removevv zz_rc_test_v01 zz_rc_test_rcg",
        "removercopygroup -f zz_rc_test_rcg",
        "removevvset -f zz_rc_test",
        "removevv -f zz_rc_test_v01",
    ]
    assert result.removals_b == ["removevvset -f zz_rc_vvs_rc", "removevvset -f zz_rc_test_rc"]
    assert [o.status for o in result.outcomes].count("created") == len(result.outcomes)


def test_apply_starts_on_the_peer_when_the_target_policy_is_no_mirror_config():
    prov = _prov(failover=False)
    rc_a = (_FIXTURES / "D22U27" / "showrcopy.txt").read_text(encoding="utf-8").replace("-       mirror_config", "-       no_mirror_config")
    a, b = _views(a_overrides={"showrcopy": rc_a})
    plan = build_plan(check(a, b, prov.replication), prov.replication, prov)
    log: list = []
    result = apply_plan(plan, prov, wsapi_factory=_factory(log))
    assert result.error is None
    assert log[-1] == ("B", "startrcopygroup zz_rc_vvs_rcg")
    assert next(o for o in result.outcomes if o.kind == "start").where == "B"


# ------------------------------------------------------------------ rerun and failure

def test_rerun_reports_exists_and_puts_nothing_pre_existing_in_the_removal_set():
    prov = _prov(failover=False)
    plan = _plan(prov)
    log: list = []
    a = _FakeWsapi("A", log, existing={"zz_rc_vvs_rcg", "zz_rc_vol01->zz_rc_vvs_rcg", "zz_rc_vol02->zz_rc_vvs_rcg"})
    b = _FakeWsapi("B", log, existing={"zz_rc_vvs_rc"})
    result = apply_plan(plan, prov, wsapi_factory=_factory(log, a=a, b=b))
    assert result.error is None and result.groups_created == []
    assert result.removals_a == [] and result.removals_b == []
    assert {o.status for o in result.outcomes if o.kind in ("group", "volume_admit", "peer_vvset")} == {"exists"}
    assert next(o for o in result.outcomes if o.kind == "start").detail == "was already started"


def test_a_failure_mid_way_stops_and_the_removal_set_covers_only_what_was_created():
    prov = _prov(failover=False)
    plan = _plan(prov)
    log: list = []
    a = _FakeWsapi("A", log, fail_at="admitrcopyvv zz_rc_vol02->zz_rc_vvs_rcg")
    result = apply_plan(plan, prov, wsapi_factory=_factory(log, a=a))
    assert result.error.startswith("Stopped after 3 write(s): array refused admitrcopyvv zz_rc_vol02->zz_rc_vvs_rcg: simulated")
    assert log[-1] == ("A", "admitrcopyvv zz_rc_vol02->zz_rc_vvs_rcg")          # nothing after the failure
    assert result.removals_a == [
        "stoprcopygroup -f zz_rc_vvs_rcg",
        "dismissrcopyvv -f -removevv zz_rc_vol01 zz_rc_vvs_rcg",
        "removercopygroup -f zz_rc_vvs_rcg",
    ]
    assert result.removals_b == []
    assert result.outcomes[-1].status == "failed"


def test_apply_refuses_a_plan_with_findings_or_an_error():
    prov = _prov()
    plan = ReplicationPlan(blockers=["No Remote Copy partnership between A and B."])
    log: list = []
    result = apply_plan(plan, prov, wsapi_factory=_factory(log))
    assert result.error == "the plan has blocking findings; nothing was applied" and log == []
    result = apply_plan(ReplicationPlan(error="Could not read 10.64.122.99: Login failed"), prov, wsapi_factory=_factory(log))
    assert result.error.startswith("Could not read") and log == []


# ------------------------------------------------------------------ the WSAPI client's group calls

class _StubRcSdk:
    """Stands in for hpe3parclient's remote-copy surface. Enforces the rule the live array taught us
    (D22U27, WSAPI 1.15, 2026-10-09): one `modifyRemoteCopyGroup` body may carry `syncPeriod` OR
    `policies`, not both — HTTP 400 code 44."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def modifyRemoteCopyGroup(self, name, optional=None):
        entry = (optional or {})["targets"][0]
        if "syncPeriod" in entry and "policies" in entry:
            raise RuntimeError("Bad request (HTTP 400) 44 - invalid input: parameters cannot be present at the same time - policies, syncPeriod")
        self.calls.append(("modify", name, entry))

    def createRemoteCopyGroup(self, name, targets, optional=None):
        self.calls.append(("create", name, targets, optional))

    def addVolumeToRemoteCopyGroup(self, group, volume, targets, optional=None):
        self.calls.append(("admit", group, volume, targets, optional))

    def startRemoteCopy(self, name, optional=None):
        self.calls.append(("start", name))


def _wsapi(stub):
    from alletra_onboard.adapters.array.wsapi_client import WsapiClient

    c = WsapiClient("192.0.2.1", "u", "p")
    c._client = stub
    return c


def test_period_and_policies_go_in_two_puts_period_first():
    stub = _StubRcSdk()
    note = _wsapi(stub).set_remote_copy_group("g", target="B", period_seconds=300, auto_recover=True, auto_synchronize=True)
    assert note == ""
    assert stub.calls == [
        ("modify", "g", {"targetName": "B", "syncPeriod": 300}),
        ("modify", "g", {"targetName": "B", "policies": {"autoRecover": True, "autoSynchronize": True}}),
    ]


def test_a_sync_group_sets_policies_only():
    stub = _StubRcSdk()
    _wsapi(stub).set_remote_copy_group("g", target="B", period_seconds=None, auto_recover=False, auto_synchronize=True)
    assert stub.calls == [("modify", "g", {"targetName": "B", "policies": {"autoRecover": False, "autoSynchronize": True}})]


def test_group_create_admit_and_start_bodies_match_the_wsapi_reference():
    stub = _StubRcSdk()
    c = _wsapi(stub)
    assert c.create_remote_copy_group("g", target="B", mode="async", peer_cpg="SSD_r6", local_cpg="SSD_r6") == "created"
    assert c.create_remote_copy_group("s", target="B", mode="sync", peer_cpg="SSD_r6") == "created"
    assert c.admit_remote_copy_volume("g", "v1", target="B") == "created"
    assert c.start_remote_copy_group("g") == "started"
    assert stub.calls == [
        ("create", "g", [{"targetName": "B", "mode": 2, "userCPG": "SSD_r6"}], {"localUserCPG": "SSD_r6"}),
        ("create", "s", [{"targetName": "B", "mode": 1, "userCPG": "SSD_r6"}], None),
        ("admit", "g", "v1", [{"targetName": "B", "secVolumeName": "v1"}], {"volumeAutoCreation": True}),
        ("start", "g"),
    ]


# ------------------------------------------------------------------ R6: verify

def _view(name: str, system_id: int, groups: list[RcGroup], vvsets: dict | None = None) -> ReplicationArrayView:
    return ReplicationArrayView(
        host=name.lower(), name=name, system_id=system_id, rc_status="Started", groups=groups, vvsets=vvsets or {},
        rcip_ports=[], targets=[], links=[],
    )


def _group(name: str, *, status="Started", role="Primary", mode="Periodic", volumes: list[tuple[str, str]], target="AlletraMP_E18U31") -> RcGroup:
    return RcGroup(name=name, target=target, status=status, role=role, mode=mode,
                   volumes=[RcGroupVolume(local_name=v, remote_name=v, sync_status=s, last_sync="2026-10-08 10:00:00 IST" if s == "Synced" else "NA") for v, s in volumes])


def _verify_with(a_groups, b_groups, *, b_vvsets=None, plan_groups=("zz_rc_vvs_rcg",)):
    prov = _prov(failover=False)
    plan = ReplicationPlan(actions=[
        ReplicationAction(kind="group", name=g, state="create", detail={"mode": "async", "period_seconds": 300, "peer_vvset": f"{g[:-4]}_rc"})
        for g in plan_groups
    ])
    a = _view("AlletraMP_D22U27", 188150, a_groups)
    b = _view("AlletraMP_E18U31", 188146, b_groups, b_vvsets)
    # the partnership links come from the fixtures' views; graft them on so links_ok is judged
    fa, fb = _views()
    a.rcip_ports, a.targets, a.links = fa.rcip_ports, fa.targets, fa.links
    b.rcip_ports, b.targets, b.links = fb.rcip_ports, fb.targets, fb.links
    reads = iter([a, b])
    return verify(prov, plan, read_fn=lambda creds, progress=None: next(reads))


def test_peer_group_name_carries_the_primary_system_id():
    a, _ = _views()
    assert peer_group_name("zz_rc_vvs_rcg", a) == "zz_rc_vvs_rcg.r188150"


def test_verify_replicating_when_started_primary_here_secondary_there_and_all_synced():
    out = _verify_with(
        [_group("zz_rc_vvs_rcg", volumes=[("zz_rc_vol01", "Synced"), ("zz_rc_vol02", "Synced")])],
        [_group("zz_rc_vvs_rcg.r188150", role="Secondary", volumes=[("zz_rc_vol01", "Synced"), ("zz_rc_vol02", "Synced")])],
        b_vvsets={"zz_rc_vvs_rc": ["zz_rc_vol01", "zz_rc_vol02"]},
    )
    assert out.error is None and out.links_ok
    [g] = out.groups
    assert g.verdict == "replicating" and g.peer_group == "zz_rc_vvs_rcg.r188150" and g.next_step == ""
    assert g.detail == "Started · Primary here, Secondary on the peer · Periodic · 2 volume(s) Synced · last sync 2026-10-08 10:00:00 IST"


def test_verify_syncing_is_reported_not_failed():
    out = _verify_with(
        [_group("zz_rc_vvs_rcg", volumes=[("zz_rc_vol01", "Synced"), ("zz_rc_vol02", "Syncing")])],
        [_group("zz_rc_vvs_rcg.r188150", role="Secondary", volumes=[("zz_rc_vol01", "Synced"), ("zz_rc_vol02", "Syncing")])],
    )
    [g] = out.groups
    assert g.verdict == "syncing" and "initial sync in progress (1 of 2 volumes Synced)" in g.detail and g.next_step == ""


@pytest.mark.parametrize("a_group, b_group, expect", [
    (_group("zz_rc_vvs_rcg", status="Stopped", volumes=[("v", "Stopped")]),
     _group("zz_rc_vvs_rcg.r188150", status="Stopped", role="Secondary", volumes=[("v", "Stopped")]), "Start the group"),
    (_group("zz_rc_vvs_rcg", volumes=[("v", "Stale")]),
     _group("zz_rc_vvs_rcg.r188150", role="Secondary", volumes=[("v", "Stale")]), "full resynchronisation"),
    (_group("zz_rc_vvs_rcg", status="Failsafe", volumes=[("v", "Synced")]),
     _group("zz_rc_vvs_rcg.r188150", role="Secondary", volumes=[("v", "Synced")]), "Failsafe"),
    (_group("zz_rc_vvs_rcg", role="Secondary-Rev", volumes=[("v", "Synced")]),
     _group("zz_rc_vvs_rcg.r188150", role="Primary-Rev", volumes=[("v", "Synced")]), "failover or reverse has happened"),
    (_group("zz_rc_vvs_rcg", volumes=[("v", "Synced")]), None, "peer has no group"),
])
def test_verify_not_replicating_names_hpes_next_step(a_group, b_group, expect):
    out = _verify_with([a_group], [b_group] if b_group else [])
    [g] = out.groups
    assert g.verdict == "not_replicating" and expect in g.next_step


def test_verify_a_group_missing_on_this_array_and_a_short_peer_set():
    out = _verify_with([], [])
    [g] = out.groups
    assert g.verdict == "not_replicating" and g.detail == "not on this array"
    out = _verify_with(
        [_group("zz_rc_vvs_rcg", volumes=[("zz_rc_vol01", "Synced"), ("zz_rc_vol02", "Synced")])],
        [_group("zz_rc_vvs_rcg.r188150", role="Secondary", volumes=[("zz_rc_vol01", "Synced"), ("zz_rc_vol02", "Synced")])],
        b_vvsets={"zz_rc_vvs_rc": ["zz_rc_vol01"]},
    )
    assert out.groups[0].verdict == "replicating" and "peer set zz_rc_vvs_rc has 1 of 2 volumes" in out.groups[0].detail


def test_verify_reports_a_failed_read_as_its_error():
    prov = _prov(failover=False)
    bad = ReplicationArrayView(host="10.64.122.99", read_error="Could not read 10.64.122.99: Login failed")
    out = verify(prov, ReplicationPlan(), read_fn=lambda creds, progress=None: bad)
    assert out.error == "Could not read 10.64.122.99: Login failed" and out.groups == []


def test_verify_on_the_live_after_apply_capture_says_replicating_for_both_groups():
    """The 2026-10-09 22:07 capture, minutes after the first live apply: both groups Started, Primary on
    D22U27, Secondary on E18U31 as `<g>.r188150`, Synced; peer sets hold the secondaries."""
    after = _FIXTURES / "after_apply"

    class _After(_Cli):
        def run(self, command, timeout=None):
            name = command.replace(" -", "_").replace(" ", "_")
            if command.startswith("showrcopy") or command == "showvvset":
                return (after / self.array / (name + ".txt")).read_text(encoding="utf-8")
            return super().run(command, timeout)

    a = read_array(_creds("10.64.122.99"), array_cli_factory=lambda c: _After("D22U27", showvv=_SHOWVV_A))
    b = read_array(_creds("10.64.154.190"), array_cli_factory=lambda c: _After("E18U31", showvv="Name VSize_MB\n"))
    assert a.vvsets["zz_rc_vvs"] == ["zz_rc_vol01"] and a.vvsets["zz_rc_test"] == ["zz_rc_test_v01"]
    assert b.vvsets["zz_rc_vvs_rc"] == ["zz_rc_vol01"] and b.vvsets["zz_rc_test_rc"] == ["zz_rc_test_v01"]
    assert not any(s.startswith("RCP_") for s in a.vvsets)          # the WSAPI path made no RCP_ set
    plan = ReplicationPlan(actions=[
        ReplicationAction(kind="group", name="zz_rc_vvs_rcg", state="create", detail={"mode": "sync", "peer_vvset": "zz_rc_vvs_rc"}),
        ReplicationAction(kind="group", name="zz_rc_test_rcg", state="create", detail={"mode": "sync", "peer_vvset": "zz_rc_test_rc"}),
    ])
    reads = iter([a, b])
    out = verify(_prov(), plan, read_fn=lambda creds, progress=None: next(reads))
    assert out.error is None and out.links_ok
    assert out.links_detail == ("AlletraMP_D22U27 → AlletraMP_E18U31 via 'AlletraMP_E18U31' 2/2 links Up · "
                               "AlletraMP_E18U31 → AlletraMP_D22U27 via 'AlletraMP_E18U31' 2/2 links Up")
    assert [(g.group, g.peer_group, g.verdict, g.detail) for g in out.groups] == [
        ("zz_rc_vvs_rcg", "zz_rc_vvs_rcg.r188150", "replicating", "Started · Primary here, Secondary on the peer · Sync · 1 volume(s) Synced"),
        ("zz_rc_test_rcg", "zz_rc_test_rcg.r188150", "replicating", "Started · Primary here, Secondary on the peer · Sync · 1 volume(s) Synced"),
    ]
    # the six pre-existing groups are still there, untouched
    assert len(a.groups) == 8 and len(b.groups) == 8
