"""SPEC-001 — the provisioning plan tells the truth. Each test cites the requirement it proves.

Fakes model the WSAPI's documented shapes (see the spec, §4); the client parsers are pinned to those
shapes in `test_wsapi_records_parse_the_documented_shapes` and owed a live capture (S-0)."""

from __future__ import annotations

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


# ------------------------------------------------------------------ §4 client parsers

def test_wsapi_records_parse_the_documented_shapes():
    from alletra_onboard.adapters.array import wsapi_client as wc

    hosts = wc.parse_hosts({"members": [
        {"name": "esx1", "persona": 8, "FCPaths": [{"wwn": "10:00:00:00:C9:00:00:01"}, {"wwn": WWN_B}]},
        {"name": "iscsi1", "persona": 2, "iSCSIPaths": [{"name": "iqn.x"}]},
    ]})
    assert hosts[0] == ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A, WWN_B])
    assert hosts[1].persona == "Generic-ALUA" and hosts[1].wwns == []

    vols = wc.parse_volumes({"members": [
        {"name": "vol01", "sizeMiB": 20480, "userCPG": "SSD_r6", "provisioningType": 2},
        {"name": "red01", "sizeMiB": 1024, "userCPG": "SSD_r6", "provisioningType": 6},
        {"name": "full01", "sizeMiB": 1024, "userCPG": "SSD_r6", "provisioningType": 1},
    ]})
    assert vols[0] == ArrayVolumeRecord(name="vol01", size_mib=20480, cpg="SSD_r6", provisioning_type="tpvv")
    assert vols[1].provisioning_type == "reduce" and vols[2].provisioning_type == "full"

    sets = wc.parse_sets({"members": [{"name": "hs", "setmembers": ["esx1"]}, {"name": "empty"}]})
    assert sets == {"hs": ["esx1"], "empty": []}


def test_hostset_target_normalises_both_wsapi_shapes():
    from alletra_onboard.adapters.array import wsapi_client as wc

    templates = wc.parse_vlun_templates({"members": [
        # template to a host set, reported with the set: prefix
        {"volumeName": "vol01", "hostname": "set:hs", "lun": 0, "type": 5, "active": False},
        # same export reported as bare name + HOST_SET type
        {"volumeName": "vol01", "hostname": "hs", "lun": 0, "type": 5, "active": False},
        # an ACTIVE path of that export collapses onto its template
        {"volumeName": "vol01", "hostname": "set:hs", "lun": 0, "type": 5, "active": True,
         "remoteName": WWN_A, "portPos": {"node": 0, "slot": 3, "cardPort": 4}},
        # a plain host export
        {"volumeName": "vol02", "hostname": "esx1", "lun": 3, "type": 3, "active": False},
    ]})
    assert templates == [
        VlunTemplate(volume="vol01", target="set:hs", lun=0),
        VlunTemplate(volume="vol02", target="esx1", lun=3),
    ]
