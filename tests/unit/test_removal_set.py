"""SPEC-007 — the tool writes the removal script for what it created. Each test cites a requirement."""

from __future__ import annotations

import pytest
from pydantic import SecretStr
from test_plan_truth import (  # sibling module (rootdir conftest, no packages)
    REACHABLE,
    TruthfulFakeWsapi,
    _discovery,
)

from alletra_onboard.application.provisioning import apply as prov_apply
from alletra_onboard.application.provisioning import storage_provision as prov
from alletra_onboard.application.provisioning.apply import render_removal_commands
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


def _approval(intent=None):
    from alletra_onboard.domain.approval import Approval

    return Approval("test-run", "storage", {"A": (intent or _intent()).array},
                    save_record=lambda m: m.model_dump(mode="json"))


def _apply(fake, intent=None, discovery=None, *, plan=None) -> ProvisioningResult:
    resolved = intent or _intent()
    inputs = prov_apply.StorageInputs(resolved, discovery or _discovery(), REACHABLE,
                                      plan or prov.ProvisioningPlan())
    return prov_apply.apply_plan(inputs, _approval(resolved), wsapi_factory=lambda a, p, s: fake)


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
    # R3: the LIST is in paste order, not only its rendering (S-12 pasted the raw list).
    assert [i.command for i in result.removals] == render_removal_commands(result.removals)


def test_a_created_host_is_removed_after_its_set_in_the_raw_list():
    """S-12 live (2026-09-14): the host did not pre-exist (S-10 cleanup removed it), apply created it,
    and the raw list read vlun, vlun, HOST, hostset, vv, vv, vvset — a paste that removes members before
    their sets. The list must already be exports → vvset → volumes → hostset → host."""
    fake = TruthfulFakeWsapi(hosts=[])
    fake.created_templates[("set:vvs", "set:hs")] = [
        VlunTemplate(volume="vol01", target="set:hs", lun=0), VlunTemplate(volume="vol02", target="set:hs", lun=1),
    ]
    result = _apply(fake)
    assert result.error is None
    assert [i.kind for i in result.removals] == ["vlun", "vlun", "vvset", "volume", "volume", "hostset", "host"]
    assert result.removals[-1].command == "removehost esx1"


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


# ------------------------------------------------------------------ R6 a failed apply

class _FailingWsapi(TruthfulFakeWsapi):
    """The WSAPI client raises on an HTTP error, and whatever was written before it stays on the array."""

    def __init__(self, *, fail_on, made_by_the_failed_call=(), read_back_fails=False, **kw):
        super().__init__(**kw)
        self.fail_on, self.read_back_fails = fail_on, read_back_fails
        self.made_by_the_failed_call = list(made_by_the_failed_call)
        self.failed = False

    def _answer(self, kind, name, present):
        from alletra_onboard.domain.errors import WsapiError

        if (kind, name) == self.fail_on:
            raise WsapiError("HTTP 400: the array refused the request")
        return super()._answer(kind, name, present)

    def ensure_vlun(self, source_ref, target_ref, lun=None):
        from alletra_onboard.domain.errors import WsapiError

        if ("vlun", source_ref) == self.fail_on:
            self._vluns.extend(self.made_by_the_failed_call)      # the array presented it; the answer was lost
            self.failed = True
            raise WsapiError("timed out waiting for the array")
        return super().ensure_vlun(source_ref, target_ref, lun)

    def vlun_templates(self):
        from alletra_onboard.domain.errors import WsapiError

        if self.failed and self.read_back_fails:
            raise WsapiError("connection reset")
        return super().vlun_templates()


ESX1 = ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A, WWN_B])
MADE = [VlunTemplate(volume="vol01", target="set:hs", lun=0), VlunTemplate(volume="vol02", target="set:hs", lun=1)]


def test_a_failed_apply_still_removes_what_it_made_before_the_failure():
    result = _apply(_FailingWsapi(fail_on=("volume", "vol02"), hosts=[]))
    assert result.error == "Stopped while creating volume vol02: HTTP 400: the array refused the request"
    assert render_removal_commands(result.removals) == ["removevv -f vol01", "removehostset -f hs", "removehost esx1"]
    assert [i.command for i in result.removals] == render_removal_commands(result.removals)   # R3 holds too


@pytest.mark.parametrize("fail_on, label, show, remove, removed_before", [
    (("host", "esx1"), "host esx1", "showhost esx1", "removehost esx1", []),
    (("hostset", "hs"), "host set hs", "showhostset hs", "removehostset -f hs", ["removehost esx1"]),
    (("volume", "vol02"), "volume vol02", "showvv vol02", "removevv -f vol02",
     ["removevv -f vol01", "removehostset -f hs", "removehost esx1"]),
    (("vvset", "vvs"), "volume set vvs", "showvvset vvs", "removevvset -f vvs",
     ["removevv -f vol01", "removevv -f vol02", "removehostset -f hs", "removehost esx1"]),
])
def test_an_object_whose_create_failed_is_named_in_a_note_not_in_the_set(fail_on, label, show, remove, removed_before):
    """A timeout or a 5xx can lose the answer after the array made the object, and a retry would call it
    Exists. It is not added to the set (it may have been there before this run): a note names it."""
    result = _apply(_FailingWsapi(fail_on=fail_on, hosts=[]))
    assert result.error.startswith(f"Stopped while creating {label}: ")
    assert render_removal_commands(result.removals) == removed_before
    note = (f"The array may have made {label} before the error. If `{show}` lists it and it was not there "
            f"before this run, `{remove}` removes it.")
    assert result.removal_notes == [note]


def test_a_failure_among_the_exports_reads_back_what_the_array_presented():
    result = _apply(_FailingWsapi(fail_on=("vlun", "set:vvs"), made_by_the_failed_call=MADE, hosts=[ESX1]))
    assert result.error == "Stopped while creating export of vvs to hs: timed out waiting for the array"
    assert render_removal_commands(result.removals) == [
        "removevlun -f vol01 0 set:hs",
        "removevlun -f vol02 1 set:hs",
        "removevvset -f vvs",
        "removevv -f vol01",
        "removevv -f vol02",
        "removehostset -f hs",
    ]
    assert result.removal_notes == []


def test_exports_that_cannot_be_read_back_after_a_failure_are_named_in_a_note():
    result = _apply(_FailingWsapi(fail_on=("vlun", "set:vvs"), made_by_the_failed_call=MADE, read_back_fails=True, hosts=[ESX1]))
    assert result.error.startswith("Stopped while creating export of vvs to hs: ")
    assert not any(i.kind == "vlun" for i in result.removals)
    assert "removevv -f vol01" in render_removal_commands(result.removals)
    assert any("showvlun -t" in note for note in result.removal_notes)


def test_a_session_that_never_opened_wrote_nothing_and_removes_nothing():
    from alletra_onboard.domain.errors import WsapiError

    def refuse(approval, purpose, side):
        raise WsapiError("login refused")

    intent = _intent()
    result = prov_apply.apply_plan(
        prov_apply.StorageInputs(intent, _discovery(), REACHABLE, prov.ProvisioningPlan()),
        _approval(intent), wsapi_factory=refuse,
    )
    assert result.error == "login refused" and result.removals == [] and result.outcomes == []


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
    result = prov_apply.apply_plan(
        prov_apply.StorageInputs(intent, discovery, {"10.132.30.136"}, prov.ProvisioningPlan()),
        _approval(intent), wsapi_factory=lambda a, p, s: fake,
    )
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


# ------------------------------------------------------------------ Astra 4: reviewed-exists VLUN + scoped removal diff

def test_reviewed_exists_export_that_vanished_is_refused_without_writing():
    """An export the reviewed plan marked 'exists' that vanished before apply must NOT turn into a
    create; apply refuses and sends zero VLUN writes."""
    intent = _intent()
    discovery = _discovery()
    fake = TruthfulFakeWsapi(
        hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A, WWN_B])],
        host_sets={"hs": ["esx1"]},
        volumes=[
            prov.ArrayVolumeRecord(name="vol01", size_mib=20 * 1024, cpg="SSD_r6", provisioning_type="tpvv"),
            prov.ArrayVolumeRecord(name="vol02", size_mib=20 * 1024, cpg="SSD_r6", provisioning_type="tpvv"),
        ],
        volume_sets={"vvs": ["vol01", "vol02"]},
        vluns=[
            VlunTemplate(volume="vol01", target="set:hs", lun=0),
            VlunTemplate(volume="vol02", target="set:hs", lun=1),
        ],
    )
    plan = prov.build_plan(intent, discovery, reachable_hosts=REACHABLE, wsapi_factory=lambda c: fake)
    assert all(a.state == "exists" for a in plan.actions)

    # The reviewed export vanishes before apply runs.
    fake._vluns.clear()
    fake.writes.clear()
    result = _apply(fake, intent, discovery, plan=plan)
    assert result.error is not None and "Rebuild the plan" in result.error
    assert [w for w in fake.writes if w[0] == "vlun"] == []
    assert result.removals == []


def test_vanished_reviewed_exists_volume_refuses_before_any_write_with_no_false_removal_note():
    """A reviewed 'exists' volume that vanished before apply must be caught up front before ANY
    write (including earlier hosts/host sets) and must never emit a 'may have made' removal note."""
    intent = _intent()
    discovery = _discovery()
    fake = TruthfulFakeWsapi(
        volumes=[prov.ArrayVolumeRecord(name="vol01", size_mib=20 * 1024, cpg="SSD_r6", provisioning_type="tpvv")],
    )
    plan = prov.build_plan(intent, discovery, reachable_hosts=REACHABLE, wsapi_factory=lambda c: fake)
    assert next(a for a in plan.actions if a.kind == "volume" and a.name == "vol01").state == "exists"
    assert next(a for a in plan.actions if a.kind == "host" and a.name == "esx1").state == "create"

    # vol01 vanishes on the array before apply runs.
    fake._volumes.clear()
    fake.writes.clear()
    result = _apply(fake, intent, discovery, plan=plan)

    assert fake.writes == []
    assert result.error is not None and "vol01" in result.error and "Rebuild the plan" in result.error
    assert result.outcomes == []
    assert result.removals == []
    assert result.removal_notes == []


def test_reviewed_exists_host_missing_a_wwn_still_readds_it_on_apply():
    """A host the plan marked 'exists' still runs ensure_host on apply so a WWN lost since preview
    is re-added rather than silently skipped."""
    intent = _intent()
    discovery = _discovery()
    readded: list[tuple[str, list[str]]] = []

    class _ReconcilingHostWsapi(TruthfulFakeWsapi):
        def ensure_host(self, name, wwns, persona="VMware"):
            self.writes.append(("host", name))
            host = next((h for h in self._hosts if h.name == name), None)
            if host is None:
                return "created"
            missing = [w for w in wwns if w not in host.wwns]
            if not missing:
                return "exists"
            host.wwns.extend(missing)
            readded.append((name, missing))
            return "updated"

    fake = _ReconcilingHostWsapi(
        hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A, WWN_B])],
    )
    fake.created_templates[("set:vvs", "set:hs")] = [
        VlunTemplate(volume="vol01", target="set:hs", lun=0),
        VlunTemplate(volume="vol02", target="set:hs", lun=1),
    ]
    plan = prov.build_plan(intent, discovery, reachable_hosts=REACHABLE, wsapi_factory=lambda c: fake)
    assert next(a for a in plan.actions if a.kind == "host" and a.name == "esx1").state == "exists"

    # One WWN drops off esx1 between preview and apply.
    fake._hosts = [ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A])]
    result = _apply(fake, intent, discovery, plan=plan)

    assert result.error is None
    assert readded == [("esx1", [WWN_B])]
    assert next(o for o in result.outcomes if o.kind == "host" and o.name == "esx1").status == "updated"


def test_set_export_removal_set_includes_preexisting_array_members():
    """createVLUN on a volume set presents every member the array's set holds, including a
    pre-existing member (OLD_DATA) not in the intent; the removal set must cover it too."""
    intent = _intent()
    discovery = _discovery()
    fake = TruthfulFakeWsapi(
        hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A, WWN_B])],
        volumes=[
            prov.ArrayVolumeRecord(name="OLD_DATA", size_mib=20 * 1024, cpg="SSD_r6", provisioning_type="tpvv"),
            prov.ArrayVolumeRecord(name="vol01", size_mib=20 * 1024, cpg="SSD_r6", provisioning_type="tpvv"),
            prov.ArrayVolumeRecord(name="vol02", size_mib=20 * 1024, cpg="SSD_r6", provisioning_type="tpvv"),
        ],
        volume_sets={"vvs": ["OLD_DATA", "vol01", "vol02"]},
    )
    fake.created_templates[("set:vvs", "set:hs")] = [
        VlunTemplate(volume="OLD_DATA", target="set:hs", lun=0),
        VlunTemplate(volume="vol01", target="set:hs", lun=1),
        VlunTemplate(volume="vol02", target="set:hs", lun=2),
    ]
    plan = prov.build_plan(intent, discovery, reachable_hosts=REACHABLE, wsapi_factory=lambda c: fake)
    result = _apply(fake, intent, discovery, plan=plan)

    assert result.error is None
    vlun_cmds = [i.command for i in result.removals if i.kind == "vlun"]
    assert vlun_cmds == [
        "removevlun -f OLD_DATA 0 set:hs",
        "removevlun -f vol01 1 set:hs",
        "removevlun -f vol02 2 set:hs",
    ]


@pytest.mark.parametrize(
    ("label", "foreign"),
    [
        ("foreign_volume_on_this_target", VlunTemplate(volume="FOREIGN_VOL", target="set:hs", lun=7)),
        ("this_volume_on_foreign_target", VlunTemplate(volume="vol01", target="other_host", lun=8)),
    ],
)
def test_concurrent_foreign_export_never_enters_this_runs_removal_set(label, foreign):
    """Both halves of the (volume, target) scope filter: neither a foreign volume exported to our
    target nor our volume exported to a foreign target may enter this run's removal set."""
    intent = _intent()
    discovery = _discovery()

    class _ConcurrentForeignExportWsapi(TruthfulFakeWsapi):
        def ensure_vlun(self, volume_name, host_name, lun=None):
            status = super().ensure_vlun(volume_name, host_name, lun=lun)
            self._vluns.append(foreign)
            return status

    fake = _ConcurrentForeignExportWsapi(
        hosts=[ArrayHostRecord(name="esx1", persona="VMware", wwns=[WWN_A, WWN_B])],
    )
    fake.created_templates[("set:vvs", "set:hs")] = [
        VlunTemplate(volume="vol01", target="set:hs", lun=5),
        VlunTemplate(volume="vol02", target="set:hs", lun=6),
    ]
    plan = prov.build_plan(intent, discovery, reachable_hosts=REACHABLE, wsapi_factory=lambda c: fake)
    result = _apply(fake, intent, discovery, plan=plan)
    assert result.error is None
    vlun_cmds = [i.command for i in result.removals if i.kind == "vlun"]
    assert vlun_cmds == ["removevlun -f vol01 5 set:hs", "removevlun -f vol02 6 set:hs"]
    assert f"removevlun -f {foreign.volume} {foreign.lun} {foreign.target}" not in vlun_cmds


def test_store_failure_during_apply_returns_stopped_result_with_removals(tmp_path, monkeypatch):
    """A SQLite failure inside the coordinator's apply-record saver raises ApplyRecordError and
    produces the tailored 'Stopped while creating ...' result with removals, never step.crashed."""
    import sqlite3

    from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
    from alletra_onboard.application.runs.coordinator import RunCoordinator
    from alletra_onboard.application.runs.event_bus import InMemoryEventBus
    from alletra_onboard.config import Settings

    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    coord = RunCoordinator(Settings(), store, InMemoryEventBus())
    intent = _intent()
    fake = TruthfulFakeWsapi(hosts=[])

    saves = 0
    real_save_artifact = store.save_artifact

    def fail_on_6th(run_id: str, kind: str, payload: bytes) -> None:
        nonlocal saves
        saves += 1
        if saves == 6:
            raise sqlite3.OperationalError("database is locked")
        real_save_artifact(run_id, kind, payload)

    monkeypatch.setattr(store, "save_artifact", fail_on_6th)
    approval = _approval(intent)
    approval.save_record = coord.apply_record("test-run", "storage.apply.failed")
    inputs = prov_apply.StorageInputs(intent, _discovery(), REACHABLE, prov.ProvisioningPlan())
    result = prov_apply.apply_plan(inputs, approval, wsapi_factory=lambda a, p, s: fake)

    assert result.error is not None
    assert result.error.startswith("Stopped while creating ")
    assert "database is locked" in result.error
    cmds = render_removal_commands(result.removals)
    assert "removehostset -f hs" in cmds
    assert "removehost esx1" in cmds
