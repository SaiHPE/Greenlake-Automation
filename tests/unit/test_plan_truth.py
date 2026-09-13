"""SPEC-001 — the provisioning plan tells the truth. Each test cites the requirement it proves.

Fakes model the WSAPI's documented shapes (see the spec, §4); the client parsers are pinned to those
shapes in `test_wsapi_records_parse_the_documented_shapes` and owed a live capture (S-0)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import SecretStr

from alletra_onboard.application.provisioning import storage_provision as prov
from alletra_onboard.domain.discovery import DiscoveryReport, HostHba
from alletra_onboard.domain.provisioning import (
    ActionOutcome,
    ArrayHostRecord,
    ArrayVolumeRecord,
    ExportRequest,
    HostSetRequest,
    ProvisioningIntent,
    VlunTemplate,
    VolumeRequest,
)
from alletra_onboard.domain.shared import EndpointCreds

# Normalised form (what normalize_wwpn produces and every domain record carries).
WWN_A = "10000000C9000001"
WWN_B = "10000000C9000002"
WWN_C = "10000000C9000003"


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="u", password=SecretStr("p"))


def _intent(**over) -> ProvisioningIntent:
    """Two 20 GiB tpvv volumes in VV-set `vvs`, host set `hs` of every discovered host, exports composed
    explicitly so the test controls the source/target shape."""
    data = dict(
        array=_creds("10.0.0.5"), vcenter=_creds("vc"), switch_f1=_creds("f1"), switch_f2=_creds("f2"),
        volumes=[
            VolumeRequest(name="vol01", size_gib=20, cpg="SSD_r6", vvset="vvs"),
            VolumeRequest(name="vol02", size_gib=20, cpg="SSD_r6", vvset="vvs"),
        ],
        host_sets=[HostSetRequest(name="hs", members=[])],
        exports=[ExportRequest(source_kind="vvset", source_name="vvs", target_kind="hostset", target_name="hs")],
    )
    data.update(over)
    return ProvisioningIntent(**data)


def _discovery() -> DiscoveryReport:
    return DiscoveryReport(host_hbas=[
        HostHba(host_name="esx1", wwpn=WWN_A, fabric="odd", os="VMware ESXi"),
        HostHba(host_name="esx1", wwpn=WWN_B, fabric="even", os="VMware ESXi"),
    ])


REACHABLE = {"esx1"}


class TruthfulFakeWsapi:
    """Array state as records, the way SPEC-001 §4 has the client return them. Every read is counted
    and every write is recorded, so R9 (read once, never write) is checkable."""

    def __init__(self, *, hosts=(), host_sets=None, volumes=(), volume_sets=None, vluns=(), cpgs=("SSD_r6",)):
        self._hosts = list(hosts)
        self._host_sets = dict(host_sets or {})
        self._volumes = list(volumes)
        self._volume_sets = dict(volume_sets or {})
        self._vluns = list(vluns)
        self._cpgs = list(cpgs)
        self.reads: list[str] = []
        self.writes: list[tuple] = []
        # What ensure_* should answer, per (kind, name); default derives from presence.
        self.answers: dict[tuple[str, str], str] = {}
        # Templates to "appear" after a created export, keyed by (source_ref, target_ref).
        self.created_templates: dict[tuple[str, str], list[VlunTemplate]] = {}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    # reads
    def cpg_names(self):
        self.reads.append("cpgs"); return list(self._cpgs)

    def hosts(self):
        self.reads.append("hosts"); return list(self._hosts)

    def host_sets(self):
        self.reads.append("host_sets"); return dict(self._host_sets)

    def volumes(self):
        self.reads.append("volumes"); return list(self._volumes)

    def volume_sets(self):
        self.reads.append("volume_sets"); return dict(self._volume_sets)

    def vlun_templates(self):
        self.reads.append("vluns"); return list(self._vluns)

    # writes
    def _answer(self, kind, name, present):
        self.writes.append((kind, name))
        return self.answers.get((kind, name), "exists" if present else "created")

    def ensure_host(self, name, wwns, persona="VMware"):
        return self._answer("host", name, any(h.name == name for h in self._hosts))

    def ensure_host_set(self, name, members):
        return self._answer("hostset", name, name in self._host_sets)

    def ensure_volume(self, name, cpg, size_mib, ptype):
        return self._answer("volume", name, any(v.name == name for v in self._volumes))

    def ensure_volume_set(self, name, members):
        return self._answer("vvset", name, name in self._volume_sets)

    def ensure_vlun(self, source_ref, target_ref, lun=None):
        self.writes.append(("vlun", source_ref, target_ref, lun))
        self._vluns.extend(self.created_templates.get((source_ref, target_ref), []))
        return self.answers.get(("vlun", source_ref), "created")


def _plan(fake, intent=None, discovery=None):
    return prov.build_plan(intent or _intent(), discovery or _discovery(), reachable_hosts=REACHABLE,
                           wsapi_factory=lambda c: fake)


def _row(plan, kind, name):
    return next(a for a in plan.actions if a.kind == kind and a.name == name)


VOL01_OK = ArrayVolumeRecord(name="vol01", size_mib=20 * 1024, cpg="SSD_r6", provisioning_type="tpvv")


# ------------------------------------------------------------------ R2 volumes

def test_volume_exists_only_when_size_cpg_and_type_match():
    plan = _plan(TruthfulFakeWsapi(volumes=[VOL01_OK]))
    row = _row(plan, "volume", "vol01")
    assert row.state == "exists" and row.exists is True
    assert "20 GiB" in row.reason and "matches" in row.reason
    assert _row(plan, "volume", "vol02").state == "create"
    assert plan.blockers == []


@pytest.mark.parametrize("on_array, expect_in_reason", [
    (VOL01_OK.model_copy(update={"size_mib": 10 * 1024}), "10 GiB"),
    (VOL01_OK.model_copy(update={"cpg": "NL_r6"}), "NL_r6"),
    (VOL01_OK.model_copy(update={"provisioning_type": "reduce"}), "reduce"),
])
def test_volume_conflict_names_every_differing_attribute(on_array, expect_in_reason):
    plan = _plan(TruthfulFakeWsapi(volumes=[on_array]))
    row = _row(plan, "volume", "vol01")
    assert row.state == "conflict" and row.exists is True
    assert expect_in_reason in row.reason and "intent" in row.reason
    assert any("vol01" in b for b in plan.blockers)


# ------------------------------------------------------------------ R3 hosts

def test_host_update_lists_the_missing_wwns():
    fake = TruthfulFakeWsapi(hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A])])
    row = _row(_plan(fake), "host", "esx1")
    assert row.state == "update"
    assert "adds 1 WWN" in row.reason and WWN_B in row.reason
    assert WWN_A not in row.reason


def test_host_conflict_when_a_wwn_belongs_to_another_host_blocks_apply():
    fake = TruthfulFakeWsapi(hosts=[ArrayHostRecord(name="other-host", persona="VMware", wwns=[WWN_B])])
    plan = _plan(fake)
    row = _row(plan, "host", "esx1")
    assert row.state == "conflict"
    assert "other-host" in row.reason and WWN_B in row.reason
    assert any("esx1" in b and "other-host" in b for b in plan.blockers)


def test_host_persona_difference_is_a_reason_not_a_conflict():
    fake = TruthfulFakeWsapi(hosts=[ArrayHostRecord(name="esx1", persona="WindowsServer", wwns=[WWN_A, WWN_B])])
    plan = _plan(fake)
    row = _row(plan, "host", "esx1")
    assert row.state == "exists"
    assert "WindowsServer" in row.reason and "left unchanged" in row.reason
    assert plan.blockers == []


# ------------------------------------------------------------------ R4 sets

def test_hostset_and_vvset_update_list_missing_members():
    fake = TruthfulFakeWsapi(host_sets={"hs": []}, volume_sets={"vvs": ["vol01"]})
    plan = _plan(fake)
    hs = _row(plan, "hostset", "hs")
    assert hs.state == "update" and "esx1" in hs.reason
    vvs = _row(plan, "vvset", "vvs")
    assert vvs.state == "update" and "vol02" in vvs.reason and "vol01" not in vvs.reason.split(":")[-1]


# ------------------------------------------------------------------ R5 exports

def test_export_exists_when_the_template_is_on_the_array():
    intent = _intent(exports=[
        ExportRequest(source_kind="volume", source_name="vol01", target_kind="host", target_name="esx1", lun=5),
    ])
    fake = TruthfulFakeWsapi(vluns=[VlunTemplate(volume="vol01", target="esx1", lun=5)])
    row = _row(_plan(fake, intent), "vlun", "vol01")
    assert row.state == "exists" and "LUN 5" in row.reason


def test_vvset_export_partially_present_is_update():
    # the array records a set export as one template per member volume (showvlun -t semantics)
    fake = TruthfulFakeWsapi(vluns=[VlunTemplate(volume="vol01", target="set:hs", lun=0)])
    row = _row(_plan(fake), "vlun", "vvs")
    assert row.state == "update"
    assert "1 of 2" in row.reason
    both = TruthfulFakeWsapi(vluns=[
        VlunTemplate(volume="vol01", target="set:hs", lun=0), VlunTemplate(volume="vol02", target="set:hs", lun=1),
    ])
    assert _row(_plan(both), "vlun", "vvs").state == "exists"


def test_export_conflicts_on_lun_taken_or_lun_changed():
    intent = _intent(exports=[
        ExportRequest(source_kind="volume", source_name="vol01", target_kind="hostset", target_name="hs", lun=7),
    ])
    taken = TruthfulFakeWsapi(vluns=[VlunTemplate(volume="someone_else", target="set:hs", lun=7)])
    plan = _plan(taken, intent)
    row = _row(plan, "vlun", "vol01")
    assert row.state == "conflict" and "someone_else" in row.reason and "LUN 7" in row.reason
    assert plan.blockers

    moved = TruthfulFakeWsapi(vluns=[VlunTemplate(volume="vol01", target="set:hs", lun=3)])
    row = _row(_plan(moved, intent), "vlun", "vol01")
    assert row.state == "conflict" and "LUN 3" in row.reason and "7" in row.reason


def test_export_auto_lun_matches_any_lun():
    intent = _intent(exports=[
        ExportRequest(source_kind="volume", source_name="vol01", target_kind="hostset", target_name="hs"),
    ])
    fake = TruthfulFakeWsapi(vluns=[VlunTemplate(volume="vol01", target="set:hs", lun=42)])
    assert _row(_plan(fake, intent), "vlun", "vol01").state == "exists"


# ------------------------------------------------------------------ R9 read discipline

def test_plan_reads_each_object_type_once_and_never_writes():
    fake = TruthfulFakeWsapi(volumes=[VOL01_OK], vluns=[VlunTemplate(volume="vol01", target="set:hs", lun=0)])
    _plan(fake)
    assert fake.writes == []
    assert sorted(fake.reads) == sorted(set(fake.reads))          # no read repeated
    assert set(fake.reads) == {"cpgs", "hosts", "host_sets", "volumes", "volume_sets", "vluns"}


# ------------------------------------------------------------------ R6 blockers

def test_plan_summary_counts_come_from_state_not_the_old_boolean():
    fake = TruthfulFakeWsapi(
        hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A])],       # update
        volumes=[VOL01_OK.model_copy(update={"size_mib": 1024})],                     # conflict
    )
    plan = _plan(fake)
    states = [a.state for a in plan.actions]
    assert states.count("update") == 1 and states.count("conflict") == 1
    assert all(a.exists == (a.state != "create") for a in plan.actions)
    assert len(plan.blockers) == 1


# ------------------------------------------------------------------ R7 / R8 apply

def test_apply_accepts_updated_and_continues_past_it():
    """P-12: an 'updated' host used to fail ActionOutcome validation and abort every later object."""
    fake = TruthfulFakeWsapi(hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A])])
    fake.answers[("host", "esx1")] = "updated"
    fake.created_templates[("set:vvs", "set:hs")] = [
        VlunTemplate(volume="vol01", target="set:hs", lun=0), VlunTemplate(volume="vol02", target="set:hs", lun=1),
    ]
    result = prov.apply_plan(_intent(), _discovery(), reachable_hosts=REACHABLE, wsapi_factory=lambda c: fake)
    assert result.error is None
    by = {(o.kind, o.name): o for o in result.outcomes}
    assert by[("host", "esx1")].status == "updated"
    assert by[("volume", "vol01")].status == "created"          # the loop went on
    assert by[("vlun", "vvs")].status == "created"
    assert ActionOutcome(kind="host", name="x", status="updated")  # the model itself admits it


def test_apply_reads_back_created_exports_and_fails_the_missing_one():
    fake = TruthfulFakeWsapi()
    # the array says "created" but no template appears on read-back
    result = prov.apply_plan(_intent(), _discovery(), reachable_hosts=REACHABLE, wsapi_factory=lambda c: fake)
    vlun = next(o for o in result.outcomes if o.kind == "vlun")
    assert vlun.status == "failed" and "read-back" in vlun.detail

    honest = TruthfulFakeWsapi()
    honest.created_templates[("set:vvs", "set:hs")] = [
        VlunTemplate(volume="vol01", target="set:hs", lun=0), VlunTemplate(volume="vol02", target="set:hs", lun=1),
    ]
    result = prov.apply_plan(_intent(), _discovery(), reachable_hosts=REACHABLE, wsapi_factory=lambda c: honest)
    vlun = next(o for o in result.outcomes if o.kind == "vlun")
    assert vlun.status == "created" and "LUN 0" in vlun.detail and "LUN 1" in vlun.detail
    assert honest.reads.count("vluns") == 1                       # one read-back, not one per export


# ------------------------------------------------------------------ §4 client parsers (pinned to S-0)

WSAPI_FIX = Path(__file__).resolve().parents[1] / "fixtures" / "rack13_wsapi"


def _wsapi(name: str) -> dict:
    return json.loads((WSAPI_FIX / f"{name}.json").read_text(encoding="utf-8"))


def test_wsapi_records_parse_the_captured_shapes():
    """rack13arcus, 2026-09-13 12:33, zz_t2_* present (tests/fixtures/rack13_wsapi/README.md)."""
    from alletra_onboard.adapters.array import wsapi_client as wc

    hosts = {h.name: h for h in wc.parse_hosts(_wsapi("hosts"))}
    esx = hosts["10.132.30.136"]
    assert esx.persona == "VMware"
    assert esx.wwns == ["10005CED8C5312A8", "10005CED8C5312A9"]     # FCPaths repeats each WWN per port
    assert hosts["vmenode"].persona == "Generic-ALUA" and hosts["vmenode"].wwns == ["10005CED8C531294"]
    assert hosts["grp3_vmenode1"].wwns == []                           # iSCSI-only host: no FC WWNs

    vols = {v.name: v for v in wc.parse_volumes(_wsapi("volumes"))}
    assert len(vols) == 51
    assert vols["zz_t2_vol01"] == ArrayVolumeRecord(name="zz_t2_vol01", size_mib=1024, cpg="SSD_r6", provisioning_type="tpvv")
    assert vols["zz_t2_vol02"].provisioning_type == "reduce"          # created with {"reduce": true} -> 6
    assert vols["zz_t2_vol03"].size_mib == 2048
    assert vols["admin"].provisioning_type == "full"
    assert vols[".shared.SSD_r6_0"].provisioning_type == "dds"
    assert vols["vol1.0.260910000000"].provisioning_type == "snp"

    hs = wc.parse_sets(_wsapi("hostsets"))
    assert len(hs) == 6 and hs["zz_t2_hs"] == ["10.132.30.136"]
    vs = wc.parse_sets(_wsapi("volumesets"))
    assert vs["zz_t2_vvs"] == ["zz_t2_vol01", "zz_t2_vol02"] and vs["test.Snapset"] == []   # setmembers absent


def test_vlun_templates_are_the_inactive_records_taken_as_is():
    """94 records: 74 active paths (hostname = the MEMBER host, type 5) + 20 templates (hostname as
    the array names the target). The first draft's 'type 5 => prefix set:' would have produced
    `set:10.132.30.136` from every active path."""
    from alletra_onboard.adapters.array import wsapi_client as wc

    templates = wc.parse_vlun_templates(_wsapi("vluns"))
    assert len(templates) == 20
    assert VlunTemplate(volume="zz_t2_vol01", target="set:zz_t2_hs", lun=0) in templates
    assert VlunTemplate(volume="zz_t2_vol02", target="set:zz_t2_hs", lun=1) in templates
    assert VlunTemplate(volume="zz_t2_vol03", target="10.132.30.136", lun=2) in templates
    assert not any(t.target.startswith("set:10.") for t in templates)
    assert [t for t in templates if t.target == "10.132.30.136"] == [VlunTemplate(volume="zz_t2_vol03", target="10.132.30.136", lun=2)]
    # records without an `active` field (unknown firmware) are kept and de-duplicated
    legacy = wc.parse_vlun_templates({"members": [
        {"volumeName": "v", "hostname": "set:hs", "lun": 0, "type": 5},
        {"volumeName": "v", "hostname": "set:hs", "lun": 0, "type": 5},
    ]})
    assert legacy == [VlunTemplate(volume="v", target="set:hs", lun=0)]


def test_plan_against_the_captured_array_says_everything_exists():
    """S-1 in miniature: the run-2 intent against the array as captured right after run 2."""
    from alletra_onboard.adapters.array import wsapi_client as wc

    intent = _intent(
        volumes=[VolumeRequest(name="zz_t2_vol01", size_gib=1, cpg="SSD_r6", vvset="zz_t2_vvs"),
                 VolumeRequest(name="zz_t2_vol02", size_gib=1, cpg="SSD_r6", provisioning_type="reduce", vvset="zz_t2_vvs"),
                 VolumeRequest(name="zz_t2_vol03", size_gib=2, cpg="SSD_r6")],
        host_sets=[HostSetRequest(name="zz_t2_hs", members=["10.132.30.136"])],
        exports=[ExportRequest(source_kind="vvset", source_name="zz_t2_vvs", target_kind="hostset", target_name="zz_t2_hs"),
                 ExportRequest(source_kind="volume", source_name="zz_t2_vol03", target_kind="host", target_name="10.132.30.136", lun=2)],
    )
    discovery = DiscoveryReport(host_hbas=[
        HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A8", fabric="odd", os="VMware ESXi"),
        HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A9", fabric="even", os="VMware ESXi"),
    ])
    fake = TruthfulFakeWsapi(
        hosts=wc.parse_hosts(_wsapi("hosts")), host_sets=wc.parse_sets(_wsapi("hostsets")),
        volumes=wc.parse_volumes(_wsapi("volumes")), volume_sets=wc.parse_sets(_wsapi("volumesets")),
        vluns=wc.parse_vlun_templates(_wsapi("vluns")),
    )
    plan = prov.build_plan(intent, discovery, reachable_hosts={"10.132.30.136"}, wsapi_factory=lambda c: fake)
    assert plan.error is None and plan.blockers == []
    assert {a.state for a in plan.actions} == {"exists"}, [(a.kind, a.name, a.state, a.reason) for a in plan.actions]
    assert _row(plan, "vlun", "zz_t2_vvs").reason == "already exported at LUN 0, LUN 1"
    assert _row(plan, "vlun", "zz_t2_vol03").reason == "already exported at LUN 2"


# ------------------------------------------------------------------ §6 live capture (S-0, 2026-09-13 12:33)

_WSAPI = Path(__file__).resolve().parents[1] / "fixtures" / "rack13_wsapi"


def _wsapi(name: str) -> dict:
    import json
    return json.loads((_WSAPI / f"{name}.json").read_text(encoding="utf-8"))


def test_live_wsapi_capture_pins_vlun_templates():
    """rack13arcus reports a set export's ACTIVE paths with hostname = the member host and type 5.
    Templates are the inactive records, as-is — the type-5 prefix rule must never invent set:<host>."""
    from alletra_onboard.adapters.array import wsapi_client as wc

    templates = wc.parse_vlun_templates(_wsapi("vluns"))
    assert VlunTemplate(volume="zz_t2_vol01", target="set:zz_t2_hs", lun=0) in templates
    assert VlunTemplate(volume="zz_t2_vol02", target="set:zz_t2_hs", lun=1) in templates
    assert VlunTemplate(volume="zz_t2_vol03", target="10.132.30.136", lun=2) in templates
    assert not any(t.target.startswith("set:10.132.") for t in templates)          # no invented set
    assert not any(t.target == "10.132.30.136" and t.volume != "zz_t2_vol03" for t in templates)
    assert len(templates) == 20                                                     # the inactive records


def test_live_wsapi_capture_pins_volumes_and_hosts():
    from alletra_onboard.adapters.array import wsapi_client as wc

    vols = {v.name: v for v in wc.parse_volumes(_wsapi("volumes"))}
    assert len(vols) == 51
    assert vols["zz_t2_vol01"] == ArrayVolumeRecord(name="zz_t2_vol01", size_mib=1024, cpg="SSD_r6", provisioning_type="tpvv")
    assert vols["zz_t2_vol02"].provisioning_type == "reduce"                        # created with {"reduce": true}
    assert vols[".mgmtdata"].provisioning_type == "full" and vols[".shared.SSD_r6_0"].provisioning_type == "dds"
    assert vols["vol1.0.260910000000"].provisioning_type == "snp"

    hosts = {h.name: h for h in wc.parse_hosts(_wsapi("hosts"))}
    esx = hosts["10.132.30.136"]
    assert esx.persona == "VMware"
    assert esx.wwns == ["10005CED8C5312A8", "10005CED8C5312A9"]                    # 4 FCPaths, 2 WWNs
    assert hosts["grp3_vmenode1"].persona == "Generic-ALUA" and hosts["grp3_vmenode1"].wwns == []

    assert wc.parse_sets(_wsapi("hostsets"))["zz_t2_hs"] == ["10.132.30.136"]
    assert "vol1" in wc.parse_sets(_wsapi("volumesets"))
