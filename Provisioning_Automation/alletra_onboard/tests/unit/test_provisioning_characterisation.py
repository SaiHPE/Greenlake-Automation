"""Characterisation tests for `hosts.py` (`union_hosts`, `resolve_declared_hosts`) and
`storage_provision.py` (`build_plan`).

Pins exact host-union ordering, alias resolution, notes, and full `ProvisioningPlan` JSON on real
captured device data (`rack13_array`, `rack13_wsapi`, `d22u27_iscsi`, `rack13_fabric`) plus a
seeded fuzz of host/volume/set/export/reachability combinations.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import SecretStr

from alletra_onboard.adapters.array import wsapi_parse as wc
from alletra_onboard.application.provisioning import discovery as disc
from alletra_onboard.application.provisioning import hosts as prov_hosts
from alletra_onboard.application.provisioning import storage_provision as prov
from alletra_onboard.domain.discovery import (
    ArrayHost,
    ArrayPort,
    DiscoveryReport,
    HostHba,
    HostIdentity,
    HostRead,
)
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.provisioning import (
    ArrayHostRecord,
    DeclaredHost,
    ExportRequest,
    HostSetRequest,
    ProvisioningIntent,
    VlunTemplate,
    VolumeRequest,
)
from alletra_onboard.domain.shared import ArrayVolumeRecord, EndpointCreds

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
R13_WSAPI = FIXTURES / "rack13_wsapi"
D22_ISCSI = FIXTURES / "d22u27_iscsi"
GOLDEN = FIXTURES / "characterisation" / "provisioning_golden.json"


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="u", password=SecretStr("p"))


def _base_intent(**over: object) -> ProvisioningIntent:
    data: dict[str, object] = {
        "array": _creds("10.0.0.5"),
        "vcenter": _creds("vc"),
        "switch_f1": _creds("f1"),
        "switch_f2": _creds("f2"),
        "volumes": [VolumeRequest(name="vol01", size_gib=10, cpg="SSD_r6")],
        "host_sets": [HostSetRequest(name="hs", members=["esx1"])],
    }
    data.update(over)
    return ProvisioningIntent.model_validate(data)


class _FakeWsapiReader:
    def __init__(self, state: dict[str, object] | None = None, *, fail: bool = False) -> None:
        s = state or {}
        self._hosts = list(s.get("hosts", ()))  # list[ArrayHostRecord]
        self._host_sets = dict(s.get("host_sets", {}))
        self._volumes = list(s.get("volumes", ()))
        self._volume_sets = dict(s.get("volume_sets", {}))
        self._vluns = list(s.get("vluns", ()))
        self._cpgs = list(s.get("cpgs", ("SSD_r6",)))
        self._fail = fail

    def __enter__(self) -> _FakeWsapiReader:
        if self._fail:
            raise DeviceError("wsapi unreachable")
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def cpg_names(self) -> list[str]:
        return list(self._cpgs)

    def hosts(self) -> list[ArrayHostRecord]:
        return list(self._hosts)

    def host_sets(self) -> dict[str, list[str]]:
        return dict(self._host_sets)

    def volumes(self) -> list[ArrayVolumeRecord]:
        return list(self._volumes)

    def volume_sets(self) -> dict[str, list[str]]:
        return dict(self._volume_sets)

    def vlun_templates(self) -> list[VlunTemplate]:
        return list(self._vluns)


def _r13_wsapi_reader() -> _FakeWsapiReader:
    def load(name: str) -> dict:
        return json.loads((R13_WSAPI / f"{name}.json").read_text(encoding="utf-8"))

    return _FakeWsapiReader({
        "hosts": wc.parse_hosts(load("hosts")),
        "host_sets": wc.parse_sets(load("hostsets")),
        "volumes": wc.parse_volumes(load("volumes")),
        "volume_sets": wc.parse_sets(load("volumesets")),
        "vluns": wc.parse_vlun_templates(load("vluns")),
        "cpgs": ("SSD_r6",),
    })


def _union_pin(
    discovery: DiscoveryReport,
    declared: list[DeclaredHost],
    zoning_plan: dict | None = None,
) -> dict[str, object]:
    _res_plain, how_plain = prov_hosts.resolve_declared_hosts(declared, discovery, canonical_names=False)
    _res_canon, how_canon = prov_hosts.resolve_declared_hosts(declared, discovery, canonical_names=True)
    hosts, notes = prov_hosts.union_hosts(discovery, declared, zoning_plan)
    return {
        "how_plain": how_plain,
        "how_canon": how_canon,
        "hosts_order": list(hosts),
        "hosts": {
            k: {
                "source": v.source,
                "transport": v.transport,
                "persona": v.persona,
                "wwpns": list(v.wwpns),
                "iqns": list(v.iqns),
                "aliases": list(v.aliases),
            }
            for k, v in hosts.items()
        },
        "notes": notes,
    }


def _plan_pin(plan) -> dict[str, object]:
    return {
        "actions": [[a.kind, a.name, a.state, a.reason] for a in plan.actions],
        "blockers": list(plan.blockers),
        "notes": list(plan.notes),
        "error": plan.error,
    }


def _hosts_capture_cases() -> dict[str, object]:
    r13_hosts = disc.parse_showhost((FIXTURES / "rack13_array" / "showhost_d.txt").read_text(encoding="utf-8"))
    d22_hosts = disc.parse_showhost((D22_ISCSI / "showhost_d.txt").read_text(encoding="utf-8"))
    r13_disc = DiscoveryReport(
        host_hbas=[
            HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A8", fabric="odd", os="VMware ESXi 8.0"),
            HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A9", fabric="even", os="VMware ESXi 8.0"),
            HostHba(host_name="esx01.lab.local", wwpn="1000000000000001", os="ESXi"),
            HostHba(host_name="esx01.other.local", wwpn="1000000000000002", os="ESXi"),
        ],
        host_identities=[
            HostIdentity(host_name="esx-iqn.lab", iqns=["iqn.1998-01.com.vmware:esxiqn"]),
        ],
        array_hosts=r13_hosts,
        host_reads=[
            HostRead(host_name="read-win", address="10.10.0.5", method="winrm", os="windows",
                     wwpns=["51402EC02089CC1C"], iqns=["iqn.1991-05.com.microsoft:read-win"]),
        ],
    )
    declared = [
        DeclaredHost(name="read-win", address="10.10.0.5"),
        DeclaredHost(name="esx-alias", os="esxi", wwpns=["10005CED8C5312A8"]),
        DeclaredHost(name="esx01", os="esxi"),
        DeclaredHost(name="esx-iqn"),
        DeclaredHost(name="vmenode"),
        DeclaredHost(name="by-ip", address="10.132.30.87"),
        DeclaredHost(name="vmenode2"),
        DeclaredHost(name="10.132.30.99", address="10.132.30.99"),
        DeclaredHost(name="win-explicit", os="windows", wwpns=["51402EC02089CC1E"]),
    ]
    zplan = {"fabrics": [{"fabric": "F1", "hosts": [
        {"wwpn": "100000109B5012A3", "host_name": "sw-linux", "host_source": "switch", "os": "Linux"},
        {"wwpn": "10000000C9999999", "host_name": "", "host_source": "switch", "os": ""},
        {"wwpn": "10005CED8C5312A8", "host_name": "10.132.30.136", "host_source": "vcenter", "os": "ESXi"},
    ]}]}
    d22_disc = DiscoveryReport(array_hosts=d22_hosts, notes=["vCenter discovery failed: timeout"])
    d22_declared = [DeclaredHost(name="missing-box", address="10.0.0.9")]
    return {
        "capture:rack13": _union_pin(r13_disc, declared, zplan),
        "capture:d22u27_vcenter_down": _union_pin(d22_disc, d22_declared, None),
    }


def _build_plan_capture_cases() -> dict[str, object]:
    r13_reader = _r13_wsapi_reader()
    r13_arr_hosts = disc.parse_showhost((FIXTURES / "rack13_array" / "showhost_d.txt").read_text(encoding="utf-8"))
    r13_disc = DiscoveryReport(
        host_hbas=[
            HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A8", fabric="odd", os="VMware ESXi"),
            HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A9", fabric="even", os="VMware ESXi"),
        ],
        array_ports=[
            ArrayPort(node=0, slot=3, card_port=3, protocol="fc", wwpn="20330002AC02D495", link_state="ready", fabric="odd"),
            ArrayPort(node=1, slot=3, card_port=4, protocol="fc", wwpn="21340002AC02D495", link_state="ready", fabric="even"),
        ],
        array_hosts=r13_arr_hosts,
    )
    out: dict[str, object] = {}

    i_exists = _base_intent(
        volumes=[
            VolumeRequest(name="zz_t2_vol01", size_gib=1, cpg="SSD_r6", vvset="zz_t2_vvs"),
            VolumeRequest(name="zz_t2_vol02", size_gib=1, cpg="SSD_r6", provisioning_type="reduce", vvset="zz_t2_vvs"),
            VolumeRequest(name="zz_t2_vol03", size_gib=2, cpg="SSD_r6"),
        ],
        host_sets=[HostSetRequest(name="zz_t2_hs", members=["10.132.30.136"])],
        exports=[
            ExportRequest(source_kind="vvset", source_name="zz_t2_vvs", target_kind="hostset", target_name="zz_t2_hs"),
            ExportRequest(source_kind="volume", source_name="zz_t2_vol03", target_kind="host", target_name="10.132.30.136", lun=2),
        ],
    )
    out["r13:all_exists"] = _plan_pin(
        prov.build_plan(i_exists, r13_disc, reachable_hosts={"10.132.30.136"}, wsapi_factory=lambda _c: r13_reader)
    )

    d22_wsapi = wc.parse_hosts(json.loads((D22_ISCSI / "wsapi_hosts.json").read_text(encoding="utf-8")))
    nvme_host = ArrayHost(name="nvme-box", persona="Generic-ALUA", iqns={"nqn.2014-08.org.nvmexpress:uuid:1": ["0:4:1"]})
    mixed_disc = r13_disc.model_copy(update={"array_hosts": [*r13_arr_hosts, nvme_host]})
    i_mixed = _base_intent(
        declared_hosts=[
            DeclaredHost(name="bad host name with spaces", os="windows", wwpns=["51402EC02089CC1C"]),
            DeclaredHost(name="new-iscsi", os="linux", iqn="iqn.1994-05.com.redhat:newiscsi"),
            DeclaredHost(name="both-transports", os="linux", wwpns=["10000000000000BB"], iqn="iqn.1994-05.com.redhat:both"),
            DeclaredHost(name="alias-136", os="esxi", wwpns=["10005CED8C5312A8"]),
        ],
        volumes=[
            VolumeRequest(name="zz_t2_vol01", size_gib=5, cpg="SSD_r6", vvset="zz_t2_vvs"),
            VolumeRequest(name="new_vol", size_gib=10, cpg="SSD_r6", vvset="zz_t2_vvs"),
            VolumeRequest(name="unpresented_vol", size_gib=2, cpg="SSD_r6"),
        ],
        host_sets=[
            HostSetRequest(name="zz_t2_hs", members=["alias-136", "new-iscsi", "nvme-box", "bad host name with spaces", "unknown-m"]),
            HostSetRequest(name="empty_hs", members=[]),
        ],
        exports=[
            ExportRequest(source_kind="vvset", source_name="zz_t2_vvs", target_kind="hostset", target_name="zz_t2_hs"),
            ExportRequest(source_kind="volume", source_name="new_vol", target_kind="host", target_name="new-iscsi"),
            ExportRequest(source_kind="volume", source_name="new_vol", target_kind="hostset", target_name="empty_hs"),
        ],
    )
    out["r13:mixed_verdicts"] = _plan_pin(
        prov.build_plan(i_mixed, mixed_disc, reachable_hosts={"10.132.30.136"}, wsapi_factory=lambda _c: r13_reader)
    )

    out["err:wsapi_down"] = _plan_pin(
        prov.build_plan(i_exists, r13_disc, reachable_hosts={"10.132.30.136"},
                        wsapi_factory=lambda _c: _FakeWsapiReader(fail=True))
    )
    out["err:missing_cpg"] = _plan_pin(
        prov.build_plan(_base_intent(volumes=[VolumeRequest(name="v1", size_gib=1, cpg="NO_SUCH_CPG")]),
                        r13_disc, reachable_hosts={"10.132.30.136"}, wsapi_factory=lambda _c: r13_reader)
    )
    out["err:multi_hs_no_exports"] = _plan_pin(
        prov.build_plan(_base_intent(host_sets=[
            HostSetRequest(name="hs1", members=["10.132.30.136"]),
            HostSetRequest(name="hs2", members=["vmenode"]),
        ], exports=[]), r13_disc, reachable_hosts={"10.132.30.136"}, wsapi_factory=lambda _c: r13_reader)
    )
    out["d22:no_hosts_selected"] = _plan_pin(
        prov.build_plan(_base_intent(host_sets=[], exports=[]), r13_disc, reachable_hosts=set(),
                        wsapi_factory=lambda _c: _FakeWsapiReader({"hosts": d22_wsapi}))
    )
    return out


def compute_provisioning_captures() -> dict[str, object]:
    return {
        "hosts_captures": _hosts_capture_cases(),
        "build_plan": _build_plan_capture_cases(),
    }


def test_hosts_and_build_plan_match_golden_characterisation() -> None:
    expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
    actual = compute_provisioning_captures()
    assert actual == expected


def test_mixed_case_iscsi_iqns_are_both_kept() -> None:
    """Two IQNs differing only by case must not collapse in `_judge_iscsi_host` (as on main)."""
    iqns = ["iqn.1991-05.com.microsoft:WIN-A", "iqn.1991-05.com.microsoft:win-a"]
    on_array = [ArrayHostRecord(name="win-a", persona="WindowsServer", iqns=["iqn.1991-05.com.microsoft:existing"])]
    assert prov._judge_iscsi_host("win-a", iqns, "WindowsServer", on_array) == (
        "update", f"adds 2 iSCSI name: {iqns[0]}, {iqns[1]}")

    report = DiscoveryReport(array_hosts=[
        ArrayHost(name="win-a", persona="WindowsServer", iqns={iqns[0]: ["0:4:1"], iqns[1]: ["1:4:1"]}),
    ])
    intent = _base_intent(host_sets=[HostSetRequest(name="hs", members=["win-a"])])
    reader = _FakeWsapiReader({"hosts": on_array, "cpgs": ("SSD_r6",)})
    plan = prov.build_plan(intent, report, reachable_hosts={"win-a"}, wsapi_factory=lambda _c: reader)
    assert plan.error is None
    assert [(a.kind, a.name, a.state, a.reason) for a in plan.actions] == [
        ("host", "win-a", "update", f"adds 2 iSCSI name: {iqns[0]}, {iqns[1]}"),
        ("hostset", "hs", "create", ""),
        ("volume", "vol01", "create", ""),
        ("vlun", "vol01", "create", ""),
    ]


