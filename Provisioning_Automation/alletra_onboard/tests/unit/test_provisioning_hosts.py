"""SPEC-003 — provisioning sees every host the run knows. Each test cites the requirement it proves."""

from __future__ import annotations

from pydantic import SecretStr

from alletra_onboard.application.provisioning import storage_provision as prov
from alletra_onboard.application.provisioning.hosts import union_hosts
from alletra_onboard.domain.discovery import ArrayHost, DiscoveryReport, HostHba
from alletra_onboard.domain.provisioning import (
    DeclaredHost,
    HostSetRequest,
    ProvisioningIntent,
    VolumeRequest,
)
from alletra_onboard.domain.shared import EndpointCreds

ESX_A, ESX_B = "10005CED8C5312A8", "10005CED8C5312A9"     # 10.132.30.136, in vCenter
WIN_A = "51402EC02089CC1C"                                 # arcus-win137, sheet-declared
LNX_A, LNX_B = "100000109B5012A2", "100000109B5012A3"      # localhost.localdomain, fabric NS only
UNCLAIMED = "10005CBA2CFF6BD0"                             # logged in, no host object, no name


def _creds(h):
    return EndpointCreds(host=h, username="u", password=SecretStr("p"))


def _intent(**over) -> ProvisioningIntent:
    data = {
        "array": _creds("10.0.0.5"), "vcenter": _creds("vc"), "switch_f1": _creds("f1"), "switch_f2": _creds("f2"),
        "volumes": [VolumeRequest(name="vol01", size_gib=10)],
        "host_sets": [HostSetRequest(name="hs", members=[])],
    }
    data.update(over)
    return ProvisioningIntent(**data)


def _discovery(*, array_hosts=()) -> DiscoveryReport:
    return DiscoveryReport(
        host_hbas=[
            HostHba(host_name="10.132.30.136", wwpn=ESX_A, fabric="odd", os="VMware ESXi 8.0"),
            HostHba(host_name="10.132.30.136", wwpn=ESX_B, fabric="even", os="VMware ESXi 8.0"),
        ],
        array_hosts=list(array_hosts),
    )


ISCSI_HOST = ArrayHost(name="grp3_vmenode1", persona="Generic-ALUA", iqns={"iqn.2024-12.com.hpe:vmenode1:62150": ["0:4:1"]})
FC_ARRAY_HOST = ArrayHost(name="vmenode", persona="Generic-ALUA", wwpns={"10005CED8C531294": ["0:3:3", "1:3:4"]})
UNCLAIMED_ROW = ArrayHost(name="", wwpns={UNCLAIMED: ["0:3:3"]})
DECLARED_WIN = DeclaredHost(name="arcus-win137", os="windows", wwpns=[WIN_A])


def _zoning_plan() -> dict:
    return {"fabrics": [
        {"fabric": "F1", "switch_host": "10.132.30.111", "hosts": [
            {"wwpn": LNX_B, "display": "10:00:00:10:9b:50:12:a3", "role": "host", "fabric": "F1",
             "host_name": "localhost.localdomain", "host_source": "switch", "os": "Linux"},
            {"wwpn": "10000000C9999999", "display": "10:00:00:00:c9:99:99:99", "role": "host", "fabric": "F1",
             "host_name": "", "host_source": "switch", "os": ""},
            {"wwpn": ESX_B, "display": "10:00:5c:ed:8c:53:12:a9", "role": "host", "fabric": "F1",
             "host_name": "10.132.30.136", "host_source": "vcenter", "os": "VMware ESXi 8.0"},
        ], "array_ports": [], "pairs": [], "already_zoned": [], "zone_names": {}},
        {"fabric": "F2", "switch_host": "10.132.30.112", "hosts": [
            {"wwpn": LNX_A, "display": "10:00:00:10:9b:50:12:a2", "role": "host", "fabric": "F2",
             "host_name": "localhost.localdomain", "host_source": "switch", "os": "Linux"},
        ], "array_ports": [], "pairs": [], "already_zoned": [], "zone_names": {}},
    ], "offline_hosts": [], "notes": [], "error": None}


# ------------------------------------------------------------------ R1, R2 — the union

def test_union_orders_sources_vcenter_sheet_array_switch():
    hosts, notes = union_hosts(_discovery(array_hosts=[FC_ARRAY_HOST, ISCSI_HOST]), [DECLARED_WIN], _zoning_plan())
    assert list(hosts) == ["10.132.30.136", "arcus-win137", "vmenode", "grp3_vmenode1", "localhost.localdomain"]
    assert [h.source for h in hosts.values()] == ["vcenter", "sheet", "array", "array", "switch"]
    esx = hosts["10.132.30.136"]
    assert esx.wwpns == [ESX_A, ESX_B] and esx.persona == "VMware" and esx.transport == "fc"
    win = hosts["arcus-win137"]
    assert win.wwpns == [WIN_A] and win.persona == "WindowsServer" and win.os == "windows"
    lnx = hosts["localhost.localdomain"]
    assert sorted(lnx.wwpns) == sorted([LNX_A, LNX_B]) and lnx.persona == "Generic-ALUA"
    assert notes == [] or all("no host name" in n for n in notes)


def test_union_first_name_wins_and_later_sources_only_add():
    # the array knows 10.132.30.136 under the same name with one extra WWPN nobody else reports
    extra = "10005CED8C5312AA"
    same = ArrayHost(name="10.132.30.136", persona="WindowsServer", wwpns={ESX_A: [], extra: []})
    hosts, _ = union_hosts(_discovery(array_hosts=[same]), [], None)
    esx = hosts["10.132.30.136"]
    assert esx.source == "vcenter" and esx.persona == "VMware"        # first source keeps name + persona
    assert esx.wwpns == [ESX_A, ESX_B, extra]                          # the later source added an initiator
    # a WWPN already claimed under one name is NOT re-claimed by a different name
    other = DeclaredHost(name="typo-host", os="windows", wwpns=[ESX_A])
    hosts, _ = union_hosts(_discovery(), [other], None)
    assert "typo-host" not in hosts and hosts["10.132.30.136"].wwpns == [ESX_A, ESX_B]


def test_union_never_offers_nameless_initiators_but_counts_them():
    hosts, notes = union_hosts(_discovery(array_hosts=[UNCLAIMED_ROW]), [], _zoning_plan())
    assert "" not in hosts
    assert all(h.name for h in hosts.values())
    assert any("2 initiator(s) logged in with no host name" in n for n in notes)   # 1 array + 1 fabric


def test_union_array_host_keeps_its_persona_and_transport():
    hosts, _ = union_hosts(_discovery(array_hosts=[ISCSI_HOST, FC_ARRAY_HOST]), [], None)
    assert hosts["grp3_vmenode1"].persona == "Generic-ALUA" and hosts["grp3_vmenode1"].transport == "iscsi"
    assert hosts["vmenode"].transport == "fc" and hosts["vmenode"].wwpns == ["10005CED8C531294"]


def test_union_switch_hosts_come_from_the_zoning_plan_payload():
    without, _ = union_hosts(_discovery(), [], None)
    assert "localhost.localdomain" not in without
    with_plan, _ = union_hosts(_discovery(), [], _zoning_plan())
    assert with_plan["localhost.localdomain"].source == "switch"
    assert with_plan["10.132.30.136"].source == "vcenter"             # the plan's vcenter rows do not re-source


# ------------------------------------------------------------------ R4 — plan / apply / verify

class _Wsapi:
    def __init__(self):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def cpg_names(self):
        return ["SSD_r6"]

    def hosts(self):
        return []

    def host_sets(self):
        return {}

    def volumes(self):
        return []

    def volume_sets(self):
        return {}

    def vlun_templates(self):
        return []

    def ensure_host(self, name, wwns, persona="VMware"):
        self.calls.append(("host", name, tuple(wwns), persona)); return "created"

    def ensure_host_set(self, name, members):
        self.calls.append(("hostset", name, tuple(members))); return "created"

    def ensure_volume(self, *a):
        return "created"

    def ensure_volume_set(self, *a):
        return "created"

    def ensure_vlun(self, src, tgt, lun=None):
        self.calls.append(("vlun", src, tgt)); return "created"


def test_plan_and_apply_create_a_sheet_declared_windows_host():
    intent = _intent(declared_hosts=[DECLARED_WIN],
                     host_sets=[HostSetRequest(name="win_hs", members=["arcus-win137"])])
    reachable = {"arcus-win137"}
    fake = _Wsapi()
    plan = prov.build_plan(intent, _discovery(), reachable_hosts=reachable, wsapi_factory=lambda c: fake)
    host_rows = [a for a in plan.actions if a.kind == "host"]
    assert [a.name for a in host_rows] == ["arcus-win137"]
    assert host_rows[0].detail["persona"] == "WindowsServer" and host_rows[0].detail["wwns"] == [WIN_A]
    assert host_rows[0].detail["source"] == "sheet"
    result = prov.apply_plan(intent, _discovery(), reachable_hosts=reachable, wsapi_factory=lambda c: fake)
    assert result.error is None
    assert ("host", "arcus-win137", (WIN_A,), "WindowsServer") in fake.calls
    assert ("hostset", "win_hs", ("arcus-win137",)) in fake.calls
    assert ("vlun", "vol01", "set:win_hs") in fake.calls


def test_plan_notes_an_iscsi_only_member_of_an_fc_set():
    intent = _intent(host_sets=[HostSetRequest(name="mixed", members=["10.132.30.136", "grp3_vmenode1"])])
    fake = _Wsapi()
    plan = prov.build_plan(intent, _discovery(array_hosts=[ISCSI_HOST]), reachable_hosts={"10.132.30.136"},
                           wsapi_factory=lambda c: fake)
    hs = next(a for a in plan.actions if a.kind == "hostset")
    assert hs.detail["members"] == ["10.132.30.136", "grp3_vmenode1"]     # legal, so it stays
    assert any("grp3_vmenode1" in n and "iSCSI" in n for n in plan.notes)
    assert plan.blockers == []


def test_path_verification_targets_include_non_vcenter_hosts():
    intent = _intent(declared_hosts=[DECLARED_WIN],
                     host_sets=[HostSetRequest(name="hs", members=["10.132.30.136", "arcus-win137"])])
    targets = prov.exported_volumes_by_host(intent, _discovery(), {"10.132.30.136", "arcus-win137"})
    assert targets["arcus-win137"] == {"vol01"} and targets["10.132.30.136"] == {"vol01"}


# ------------------------------------------------------------------ R5 — the dropdown

def test_briefs_carry_source_transport_and_put_iscsi_last():
    briefs = prov.host_briefs(_discovery(array_hosts=[ISCSI_HOST, FC_ARRAY_HOST]), declared_hosts=[DECLARED_WIN],
                              zoning_plan=_zoning_plan())
    names = [b.name for b in briefs]
    assert names[-1] == "grp3_vmenode1"                                  # iSCSI-only last
    assert names[:2] == ["10.132.30.136", "arcus-win137"]
    by = {b.name: b for b in briefs}
    assert by["arcus-win137"].source == "sheet" and by["arcus-win137"].persona == "WindowsServer"
    assert by["grp3_vmenode1"].transport == "iscsi" and by["grp3_vmenode1"].fc_capable is False
    assert "iSCSI only" in by["grp3_vmenode1"].status
    assert by["localhost.localdomain"].source == "switch" and "both fabrics" in by["localhost.localdomain"].status
    assert by["arcus-win137"].fc_capable is True and "not logged in" in by["arcus-win137"].status


# ------------------------------------------------------------------ R7 — unchanged where vCenter is the only source

def test_vcenter_only_behaviour_is_unchanged():
    hosts, notes = union_hosts(_discovery(), [], None)
    assert list(hosts) == ["10.132.30.136"] and notes == []
    briefs = prov.host_briefs(_discovery())
    assert [b.name for b in briefs] == ["10.132.30.136"] and "both fabrics" in briefs[0].status
    fake = _Wsapi()
    plan = prov.build_plan(_intent(), _discovery(), reachable_hosts={"10.132.30.136"}, wsapi_factory=lambda c: fake)
    assert [a.name for a in plan.actions if a.kind == "host"] == ["10.132.30.136"]
    assert plan.notes == []
