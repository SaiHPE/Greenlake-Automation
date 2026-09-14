"""SPEC-007 — the tool writes the removal script for what it created. Each test cites a requirement."""

from __future__ import annotations

from pydantic import SecretStr

from alletra_onboard.application.provisioning import storage_provision as prov
from alletra_onboard.application.provisioning.storage_provision import render_removal_commands
from alletra_onboard.domain.discovery import DiscoveryReport, HostHba
from alletra_onboard.domain.provisioning import (
    ArrayHostRecord,
    ExportRequest,
    HostSetRequest,
    ProvisioningIntent,
    ProvisioningResult,
    RemovalItem,
    VlunTemplate,
    VolumeRequest,
)
from alletra_onboard.domain.shared import EndpointCreds
from test_plan_truth import REACHABLE, TruthfulFakeWsapi, _discovery  # sibling module (rootdir conftest, no packages)

WWN_A, WWN_B = "10000000C9000001", "10000000C9000002"


def _creds(h):
    return EndpointCreds(host=h, username="u", password=SecretStr("p"))


def _intent(**over) -> ProvisioningIntent:
    data = {
        "array": _creds("10.0.0.5"), "vcenter": _creds("vc"), "switch_f1": _creds("f1"), "switch_f2": _creds("f2"),
        "volumes": [VolumeRequest(name="vol01", size_gib=20, vvset="vvs"), VolumeRequest(name="vol02", size_gib=20, vvset="vvs")],
        "host_sets": [HostSetRequest(name="hs", members=["esx1"])],
        "exports": [ExportRequest(source_kind="vvset", source_name="vvs", target_kind="hostset", target_name="hs")],
    }
    data.update(over)
    return ProvisioningIntent(**data)


def _apply(fake, intent=None, discovery=None) -> ProvisioningResult:
    return prov.apply_plan(intent or _intent(), discovery or _discovery(), reachable_hosts=REACHABLE,
                           wsapi_factory=lambda c: fake)


# ------------------------------------------------------------------ R1, R2, R3

def test_removal_covers_only_what_this_apply_created_in_dependency_order():
    fake = TruthfulFakeWsapi(hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A, WWN_B])])
    fake.created_templates[("set:vvs", "set:hs")] = [
        VlunTemplate(volume="vol01", target="set:hs", lun=5), VlunTemplate(volume="vol02", target="set:hs", lun=6),
    ]
    result = _apply(fake)
    assert result.error is None
    assert render_removal_commands(result.removals) == [
        "removevlun -f vol01 5 set:hs",
        "removevlun -f vol02 6 set:hs",
        "removevvset -f vvs",
        "removevv -f vol01",
        "removevv -f vol02",
        "removehostset -f hs",
    ]
    assert not any(i.kind == "host" for i in result.removals)          # esx1 existed — never removed
    assert result.removal_notes == []


def test_export_removals_come_from_the_template_diff_not_the_status():
    """A set export completed member by member: only the NEW member's LUN is in the removal set."""
    fake = TruthfulFakeWsapi(
        hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A, WWN_B])],
        host_sets={"hs": ["esx1"]}, volume_sets={"vvs": ["vol01", "vol02"]},
        vluns=[VlunTemplate(volume="vol01", target="set:hs", lun=0)],
    )
    fake.created_templates[("vol02", "set:hs")] = [VlunTemplate(volume="vol02", target="set:hs", lun=1)]
    result = _apply(fake)
    vlun_cmds = [i.command for i in result.removals if i.kind == "vlun"]
    assert vlun_cmds == ["removevlun -f vol02 1 set:hs"]                # never LUN 0 — it was there before


# ------------------------------------------------------------------ R1 note

def test_updated_objects_are_not_reverted_but_named():
    fake = TruthfulFakeWsapi(hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A])],
                             host_sets={"hs": []})
    fake.answers[("host", "esx1")] = "updated"
    fake.answers[("hostset", "hs")] = "updated"
    fake.created_templates[("set:vvs", "set:hs")] = [
        VlunTemplate(volume="vol01", target="set:hs", lun=0), VlunTemplate(volume="vol02", target="set:hs", lun=1),
    ]
    result = _apply(fake)
    kinds = {i.kind for i in result.removals}
    assert "host" not in kinds and "hostset" not in kinds
    assert any("Not reverted" in n and "esx1" in n and "hs" in n for n in result.removal_notes)


# ------------------------------------------------------------------ R3 render, R5 empty

def test_render_orders_by_kind_and_dedups_across_two_applies():
    first = [RemovalItem(kind="host", name="h2", command="removehost h2"),
             RemovalItem(kind="volume", name="v1", command="removevv -f v1")]
    second = [RemovalItem(kind="vlun", name="v1 LUN 0 → set:hs", command="removevlun -f v1 0 set:hs"),
              RemovalItem(kind="volume", name="v1", command="removevv -f v1"),          # duplicate
              RemovalItem(kind="hostset", name="hs", command="removehostset -f hs")]
    assert render_removal_commands(first + second) == [
        "removevlun -f v1 0 set:hs", "removevv -f v1", "removehostset -f hs", "removehost h2",
    ]


def test_nothing_created_means_an_empty_set():
    fake = TruthfulFakeWsapi(
        hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A, WWN_B])],
        host_sets={"hs": ["esx1"]},
        volumes=[prov.ArrayVolumeRecord(name="vol01", size_mib=20480, cpg="SSD_r6", provisioning_type="tpvv"),
                 prov.ArrayVolumeRecord(name="vol02", size_mib=20480, cpg="SSD_r6", provisioning_type="tpvv")],
        volume_sets={"vvs": ["vol01", "vol02"]},
        vluns=[VlunTemplate(volume="vol01", target="set:hs", lun=0), VlunTemplate(volume="vol02", target="set:hs", lun=1)],
    )
    result = _apply(fake)
    assert result.error is None and result.removals == [] and render_removal_commands([]) == []


# ------------------------------------------------------------------ the live case, pinned

def test_the_second_session_cleanup_would_have_been_generated():
    """S-4, 2026-09-14 12:39: the objects the tool created, and the fourteen lines the operator then
    typed by hand at 13:11 (rack13_cleanup_20260914_131157). Minus the run-2 objects, which an
    earlier apply created — those come from that apply's own set."""
    esx = ArrayHostRecord(name="10.132.30.136", persona="VMware", wwns=["10005CED8C5312A8", "10005CED8C5312A9"])
    before = [VlunTemplate(volume="zz_t2_vol01", target="set:zz_t2_hs", lun=0),
              VlunTemplate(volume="zz_t2_vol02", target="set:zz_t2_hs", lun=1),
              VlunTemplate(volume="zz_t2_vol03", target="10.132.30.136", lun=2)]
    fake = TruthfulFakeWsapi(
        hosts=[esx], host_sets={"zz_t2_hs": ["10.132.30.136"]},
        volumes=[prov.ArrayVolumeRecord(name="zz_t2_vol01", size_mib=1024, cpg="SSD_r6", provisioning_type="tpvv"),
                 prov.ArrayVolumeRecord(name="zz_t2_vol02", size_mib=1024, cpg="SSD_r6", provisioning_type="reduce"),
                 prov.ArrayVolumeRecord(name="zz_t2_vol03", size_mib=2048, cpg="SSD_r6", provisioning_type="tpvv"),
                 prov.ArrayVolumeRecord(name="zz_t3_vol01", size_mib=10240, cpg="SSD_r6", provisioning_type="tpvv")],
        volume_sets={"zz_t2_vvs": ["zz_t2_vol01", "zz_t2_vol02"]}, vluns=before,
    )
    fake.created_templates[("set:zz_t3_vvs", "set:zz_t3_hs")] = [
        VlunTemplate(volume="zz_t3_vol01", target="set:zz_t3_hs", lun=5),
        VlunTemplate(volume="zz_t3_vol02", target="set:zz_t3_hs", lun=6),
    ]
    discovery = DiscoveryReport(host_hbas=[
        HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A8", fabric="odd", os="VMware ESXi"),
        HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A9", fabric="even", os="VMware ESXi"),
        HostHba(host_name="10.132.30.86", wwpn="51402EC02089CC38", os="VMware ESXi"),
        HostHba(host_name="10.132.30.86", wwpn="51402EC02089CC3A", os="VMware ESXi"),
    ])
    from alletra_onboard.domain.provisioning import DeclaredHost
    intent = _intent(
        volumes=[VolumeRequest(name="zz_t2_vol01", size_gib=1, vvset="zz_t2_vvs"),
                 VolumeRequest(name="zz_t2_vol02", size_gib=1, provisioning_type="reduce", vvset="zz_t2_vvs"),
                 VolumeRequest(name="zz_t2_vol03", size_gib=2),
                 VolumeRequest(name="zz_t3_vol01", size_gib=10, vvset="zz_t3_vvs"),
                 VolumeRequest(name="zz_t3_vol02", size_gib=2, vvset="zz_t3_vvs")],
        host_sets=[HostSetRequest(name="zz_t2_hs", members=["10.132.30.136"]),
                   HostSetRequest(name="zz_t3_hs", members=["10.132.30.136", "10.132.30.86"]),
                   HostSetRequest(name="zz_t3_win", members=["arcus-win137"])],
        declared_hosts=[DeclaredHost(name="arcus-win137", os="windows", wwpns=["51402EC02089CC1C"])],
        exports=[ExportRequest(source_kind="vvset", source_name="zz_t2_vvs", target_kind="hostset", target_name="zz_t2_hs"),
                 ExportRequest(source_kind="vvset", source_name="zz_t3_vvs", target_kind="hostset", target_name="zz_t3_hs")],
    )
    result = prov.apply_plan(intent, discovery, reachable_hosts={"10.132.30.136"}, wsapi_factory=lambda c: fake)
    assert result.error is None
    assert render_removal_commands(result.removals) == [
        "removevlun -f zz_t3_vol01 5 set:zz_t3_hs",
        "removevlun -f zz_t3_vol02 6 set:zz_t3_hs",
        "removevvset -f zz_t3_vvs",
        "removevv -f zz_t3_vol02",
        "removehostset -f zz_t3_hs",
        "removehostset -f zz_t3_win",
        "removehost 10.132.30.86",
        "removehost arcus-win137",
    ]
    # and with R11 in place the run-2 export is NOT re-sent, so it is not in this apply's set either
    assert not any("zz_t2" in c for c in render_removal_commands(result.removals))
