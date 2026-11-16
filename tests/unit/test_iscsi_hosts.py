"""BL-44 — iSCSI hosts are created from their iSCSI name. Pinned to the D22U27 capture of 2026-10-26
(tests/fixtures/d22u27_iscsi) and the rack13arcus host records (tests/fixtures/rack13_wsapi)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters.array.wsapi_client import (
    _WSAPI_PERSONA,
    WsapiClient,
    WsapiError,
    parse_hosts,
)
from alletra_onboard.application.provisioning import storage_provision as prov
from alletra_onboard.application.provisioning import zoning
from alletra_onboard.application.provisioning.discovery import parse_showhost
from alletra_onboard.domain.discovery import ArrayHost, ArrayPort, DiscoveryReport, HostHba
from alletra_onboard.domain.provisioning import (
    ArrayHostRecord,
    DeclaredHost,
    ExportRequest,
    HostSetRequest,
    ProvisioningIntent,
    VolumeRequest,
)
from alletra_onboard.domain.shared import EndpointCreds

FIX = Path(__file__).resolve().parents[1] / "fixtures"
D22 = FIX / "d22u27_iscsi"
LINUX_IQN = "iqn.1994-05.com.redhat:6e35c4a016a0"   # the lab Linux host 10.54.159.49
OTHER_IQN = "iqn.1991-05.com.microsoft:win-tn3n7rujk3v"
WWN_A = "10000000C9000001"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ what the array reports

def test_parse_hosts_reads_iscsi_names_from_the_rack13_records():
    records = {r.name: r for r in parse_hosts(_load(FIX / "rack13_wsapi" / "hosts.json"))}
    assert records["grp3_vmenode1"].iqns and all(i.startswith("iqn.") for i in records["grp3_vmenode1"].iqns)
    assert records["grp3_vmenode1"].wwns == []
    assert all(not r.iqns for r in records.values() if r.wwns)        # no host there has both


def test_parse_hosts_on_d22u27_leaves_fc_hosts_as_they_were():
    records = {r.name: r for r in parse_hosts(_load(D22 / "wsapi_hosts.json"))}
    assert len(records) == 8 and all(r.iqns == [] for r in records.values())
    assert records["ESX1"].wwns == ["1000D0BF9CB7A3C9", "1000D0BF9CB7A3D1"]   # one entry per port, de-duplicated
    assert records["ESX1"].persona == "VMware" and records["test2-alletra"].persona == "Generic-ALUA"


def test_parse_hosts_drops_a_repeated_iscsi_name_whatever_its_case():
    body = {"members": [{"name": "h", "iSCSIPaths": [{"name": LINUX_IQN}, {"name": LINUX_IQN.upper()}, {"name": ""}]}]}
    assert parse_hosts(body)[0].iqns == [LINUX_IQN]


def test_wsapi_persona_ids_are_the_ones_d22u27_reports():
    wsapi = {p["name"]: p["wsapiAssignedId"] for p in _load(D22 / "wsapi_hostpersonas.json")["members"]}
    for name in ("Generic-ALUA", "VMware", "WindowsServer"):
        assert _WSAPI_PERSONA[name] == wsapi[name]
    cli = (D22 / "showhost_listpersona.txt").read_text()
    assert " 11 VMware " in cli and wsapi["VMware"] == 8               # the CLI numbering is not the WSAPI one


def test_the_cli_help_matches_what_the_tool_relies_on():
    create = (D22 / "help_createhost.txt").read_text()
    assert "createhost -iscsi [options] <hostname> [<iscsi_name>...]" in create
    assert "up to 31 characters" in create
    remove = (D22 / "help_removehost.txt").read_text()
    assert "A host that has one or more VLUNs exported on it cannot be removed." in remove


# ------------------------------------------------------------------ what the array did (live, 2026-10-26)

def test_the_live_create_call_is_the_one_ensure_iscsi_host_sends():
    """Run eba8f3a7 on D22U27: the array answered 201 to exactly this body."""
    writes = (D22 / "wsapi_writes_live.txt").read_text()
    assert ('POST /hosts { "name": "zz_is_linux", "iSCSINames": [ "' + LINUX_IQN + '" ], "persona": 2 }  ->  HTTP 201') in writes
    stub = _StubSdk()
    _client(stub).ensure_iscsi_host("zz_is_linux", [LINUX_IQN], persona="Generic-ALUA")
    assert stub.calls == [("create", "zz_is_linux", [LINUX_IQN], [], {"persona": 2})]


def test_the_host_the_array_made_reads_back_as_an_iscsi_host():
    record = parse_hosts({"members": [_load(D22 / "wsapi_host_zz_is_linux.json")]})[0]
    assert (record.name, record.persona, record.wwns, record.iqns, record.id) == (
        "zz_is_linux", "Generic-ALUA", [], [LINUX_IQN], 8)
    assert prov._judge_iscsi_host("zz_is_linux", [LINUX_IQN], "Generic-ALUA", [record]) == (
        "exists", f"carries its iSCSI name ({LINUX_IQN})")


def test_showhost_lists_the_new_host_as_not_logged_in_with_no_address():
    host = parse_showhost((D22 / "showhost_d_zz_is_linux.txt").read_text())[0]
    assert host.name == "zz_is_linux" and host.persona == "Generic-ALUA"
    assert host.iqns == {LINUX_IQN: []} and host.addresses == {}       # f6ff:… is a placeholder, not an IP


# ------------------------------------------------------------------ the client: ensure_iscsi_host

class _StubSdk:
    """getHosts / createHost / modifyHost with the WSAPI's record shape (FCPaths + iSCSIPaths)."""

    def __init__(self, hosts=None):
        self.hosts = {n: {"fc": list(fc), "iscsi": list(iscsi)} for n, (fc, iscsi) in (hosts or {}).items()}
        self.calls: list[tuple] = []

    def getHosts(self):
        return {"members": [
            {"name": n, "FCPaths": [{"wwn": w} for w in h["fc"]], "iSCSIPaths": [{"name": i} for i in h["iscsi"]]}
            for n, h in self.hosts.items()
        ]}

    def createHost(self, name, iscsiNames=None, FCWwns=None, optional=None):
        self.calls.append(("create", name, list(iscsiNames or []), list(FCWwns or []), dict(optional or {})))
        self.hosts[name] = {"fc": list(FCWwns or []), "iscsi": list(iscsiNames or [])}

    def modifyHost(self, name, mods):
        self.calls.append(("modify", name, dict(mods)))
        self.hosts[name]["iscsi"] += mods.get("iSCSINames", [])


def _client(stub) -> WsapiClient:
    c = WsapiClient("192.0.2.1", "u", "p")
    c._client = stub
    return c


def test_ensure_iscsi_host_creates_with_the_iqn_and_the_wsapi_persona():
    stub = _StubSdk()
    assert _client(stub).ensure_iscsi_host("linux-test", [LINUX_IQN], persona="Generic-ALUA") == "created"
    assert stub.calls == [("create", "linux-test", [LINUX_IQN], [], {"persona": 2})]   # never FC and iSCSI together


def test_ensure_iscsi_host_is_a_no_op_when_the_host_carries_its_iqn():
    stub = _StubSdk(hosts={"linux-test": ([], [LINUX_IQN.upper()])})
    assert _client(stub).ensure_iscsi_host("linux-test", [LINUX_IQN], persona="Generic-ALUA") == "exists"
    assert stub.calls == []


def test_ensure_iscsi_host_adds_only_the_missing_iqn():
    stub = _StubSdk(hosts={"linux-test": ([], [LINUX_IQN])})
    assert _client(stub).ensure_iscsi_host("linux-test", [LINUX_IQN, OTHER_IQN]) == "updated"
    assert stub.calls == [("modify", "linux-test", {"pathOperation": 1, "iSCSINames": [OTHER_IQN]})]


def test_ensure_iscsi_host_refuses_an_iqn_owned_by_another_host():
    stub = _StubSdk(hosts={"someone": ([], [LINUX_IQN])})
    with pytest.raises(WsapiError, match="someone"):
        _client(stub).ensure_iscsi_host("linux-test", [LINUX_IQN])
    assert stub.calls == []


def test_ensure_iscsi_host_refuses_to_add_an_iqn_to_an_fc_host():
    stub = _StubSdk(hosts={"esx1": ([WWN_A], [])})
    with pytest.raises(WsapiError, match="FC WWNs"):
        _client(stub).ensure_iscsi_host("esx1", [LINUX_IQN])
    assert stub.calls == []


def test_ensure_iscsi_host_needs_an_iqn_and_a_known_persona():
    with pytest.raises(WsapiError, match="no iSCSI name"):
        _client(_StubSdk()).ensure_iscsi_host("linux-test", [])
    with pytest.raises(WsapiError, match="unknown host persona"):
        _client(_StubSdk()).ensure_iscsi_host("linux-test", [LINUX_IQN], persona="Generic")


def test_iqn_owners_reads_get_hosts_lower_cased():
    stub = _StubSdk(hosts={"linux-test": ([], [LINUX_IQN.upper()]), "esx1": ([WWN_A], [])})
    assert _client(stub).iqn_owners() == {LINUX_IQN: "linux-test"}


# ------------------------------------------------------------------ plan and apply

def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="u", password=SecretStr("p"))


def _intent(declared, members, **over) -> ProvisioningIntent:
    data = {
        "array": _creds("10.64.122.99"), "vcenter": _creds("vc"), "switch_f1": _creds("f1"), "switch_f2": _creds("f2"),
        "declared_hosts": declared,
        "volumes": [VolumeRequest(name="zz_is_vol01", size_gib=1, cpg="SSD_r6")],
        "host_sets": [HostSetRequest(name="zz_is_hs", members=members)],
        "exports": [ExportRequest(source_kind="volume", source_name="zz_is_vol01", target_kind="hostset", target_name="zz_is_hs")],
    }
    data.update(over)
    return ProvisioningIntent(**data)


LINUX = DeclaredHost(name="linux-test", os="linux", address="10.54.159.49", iqn=LINUX_IQN)


class _Array:
    """The array as provisioning sees it: records in, every write recorded."""

    def __init__(self, hosts=()):
        self._hosts = list(hosts)
        self.writes: list[tuple] = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def cpg_names(self):
        return ["SSD_r6"]

    def hosts(self):
        return list(self._hosts)

    def host_sets(self):
        return {}

    def volumes(self):
        return []

    def volume_sets(self):
        return {}

    def vlun_templates(self):
        return []

    def ensure_host(self, name, wwns, persona="VMware"):
        self.writes.append(("fc-host", name, tuple(wwns), persona))
        return "created"

    def ensure_iscsi_host(self, name, iqns, persona="VMware"):
        self.writes.append(("iscsi-host", name, tuple(iqns), persona))
        self._hosts.append(ArrayHostRecord(name=name, persona=persona, iqns=list(iqns), id=9))
        return "created"

    def ensure_host_set(self, name, members):
        self.writes.append(("hostset", name, tuple(members)))
        return "created"

    def ensure_volume(self, name, *a):
        self.writes.append(("volume", name))
        return "created"

    def ensure_volume_set(self, name, members):
        return "created"

    def ensure_vlun(self, source_ref, target_ref, lun=None):
        self.writes.append(("vlun", source_ref, target_ref))
        return "created"


def _row(plan, kind, name):
    return next(a for a in plan.actions if a.kind == kind and a.name == name)


def test_a_sheet_iscsi_host_is_planned_for_creation_with_its_iqn_and_os_persona():
    plan = prov.build_plan(_intent([LINUX], ["linux-test"]), DiscoveryReport(), reachable_hosts=set(),
                           wsapi_factory=lambda c: _Array())
    row = _row(plan, "host", "linux-test")
    assert row.state == "create" and LINUX_IQN in row.description and "Generic-ALUA" in row.description
    assert row.detail["iqns"] == [LINUX_IQN] and row.detail["wwns"] == []
    assert _row(plan, "hostset", "zz_is_hs").detail["members"] == ["linux-test"]
    assert not any("not supported" in n for n in plan.notes)
    # D22U27 has no iSCSI port, so the IQN cannot be logged in: the export waits, the host does not.
    assert not [a for a in plan.actions if a.kind == "vlun"]
    assert any("held back" in n and "zz_is_hs" in n for n in plan.notes)
    wait = next(n for n in plan.notes if "reachable" in n.lower())
    assert "iSCSI" in wait and "linux-test" in wait and "zoning is applied" not in wait and "both fabrics" not in wait
    assert plan.blockers == []


def test_apply_makes_the_iscsi_host_and_its_removal_line():
    array = _Array()
    result = prov.apply_plan(_intent([LINUX], ["linux-test"]), DiscoveryReport(), reachable_hosts=set(),
                             wsapi_factory=lambda c: array)
    assert result.error is None
    assert ("iscsi-host", "linux-test", (LINUX_IQN,), "Generic-ALUA") in array.writes
    assert not [w for w in array.writes if w[0] in ("fc-host", "vlun")]
    host = next(o for o in result.outcomes if o.kind == "host")
    assert host.status == "created" and "1 iSCSI name" in host.detail and "WWN" not in host.detail
    assert "removehost linux-test" in prov.render_removal_commands(result.removals)


def test_an_iscsi_host_whose_iqn_is_logged_in_unclaimed_gets_its_export():
    """The real order on an array with iSCSI ports: the server logs in first (an unclaimed row in
    `showhost -d`), then the tool makes its host object — the gate must see that login. FC ports as
    on D22U27 (showport 2026-10-26): the gate checks FC zoning too and needs the array's FC ports."""
    fc = [ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC02DEF6", link_state="ready", fabric="odd"),
          ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC02DEF6", link_state="ready", fabric="even")]
    discovery = DiscoveryReport(array_ports=fc, array_hosts=[ArrayHost(name="", iqns={LINUX_IQN: ["0:4:1", "1:4:1"]})])
    intent = _intent([LINUX], ["linux-test"])
    report = zoning.build_report(intent, discovery)
    assert report.iscsi_hosts == {"linux-test": ["0:4:1", "1:4:1"]} and "linux-test" in report.zoned_hosts
    array = _Array()
    prov.apply_plan(intent, discovery, reachable_hosts=set(report.zoned_hosts), wsapi_factory=lambda c: array)
    assert ("vlun", "zz_is_vol01", "set:zz_is_hs") in array.writes


def test_an_iqn_that_belongs_to_another_host_blocks_the_plan():
    array = _Array(hosts=[ArrayHostRecord(name="someone", persona="Generic-ALUA", iqns=[LINUX_IQN.upper()])])
    plan = prov.build_plan(_intent([LINUX], ["linux-test"]), DiscoveryReport(), reachable_hosts=set(),
                           wsapi_factory=lambda c: array)
    row = _row(plan, "host", "linux-test")
    assert row.state == "conflict" and "belongs to host someone" in row.reason
    assert any("linux-test" in b for b in plan.blockers)


def test_an_fc_host_of_the_same_name_blocks_the_plan():
    array = _Array(hosts=[ArrayHostRecord(name="linux-test", persona="Generic-ALUA", wwns=[WWN_A])])
    plan = prov.build_plan(_intent([LINUX], ["linux-test"]), DiscoveryReport(), reachable_hosts=set(),
                           wsapi_factory=lambda c: array)
    row = _row(plan, "host", "linux-test")
    assert row.state == "conflict" and "FC WWN" in row.reason


def test_an_existing_iscsi_host_missing_the_sheet_iqn_is_an_update():
    array = _Array(hosts=[ArrayHostRecord(name="linux-test", persona="Generic-ALUA", iqns=[OTHER_IQN])])
    discovery = DiscoveryReport(array_hosts=parse_showhost(
        f" 9 linux-test Generic-ALUA {OTHER_IQN} --- n/a\n"))
    plan = prov.build_plan(_intent([LINUX], ["linux-test"]), discovery, reachable_hosts=set(),
                           wsapi_factory=lambda c: array)
    row = _row(plan, "host", "linux-test")
    assert row.state == "update" and LINUX_IQN in row.reason and OTHER_IQN not in row.reason


def test_a_host_with_fc_and_iscsi_is_made_from_fc_only_and_says_so():
    both = DeclaredHost(name="dual", os="linux", wwpns=[WWN_A], iqn=LINUX_IQN)
    array = _Array()
    intent = _intent([both], ["dual"])
    plan = prov.build_plan(intent, DiscoveryReport(), reachable_hosts=set(), wsapi_factory=lambda c: array)
    assert "1 FC WWN" in _row(plan, "host", "dual").description
    assert any("FC and iSCSI both found for dual" in n for n in plan.notes)
    prov.apply_plan(intent, DiscoveryReport(), reachable_hosts=set(), wsapi_factory=lambda c: array)
    assert [w[0] for w in array.writes if w[0].endswith("host")] == ["fc-host"]


def test_fc_hosts_still_go_through_ensure_host():
    hbas = [HostHba(host_name="esx1", wwpn=WWN_A, fabric="odd", os="VMware ESXi")]
    array = _Array()
    prov.apply_plan(_intent([], ["esx1"]), DiscoveryReport(host_hbas=hbas), reachable_hosts=set(),
                    wsapi_factory=lambda c: array)
    assert ("fc-host", "esx1", (WWN_A,), "VMware") in array.writes
    assert not [w for w in array.writes if w[0] == "iscsi-host"]


NQN = "nqn.2014-08.org.nvmexpress:uuid:1234"


def test_an_nvme_host_on_the_array_is_left_as_it_is_not_given_its_nqn_as_an_iqn():
    """`showhost -d` files an NQN with the IQNs; WSAPI keeps it in NVMETCPPaths, not iSCSIPaths."""
    discovery = DiscoveryReport(array_hosts=parse_showhost(f" 9 nvme1 Generic-ALUA {NQN} 0:4:1 10.1.1.1\n"))
    array = _Array(hosts=[ArrayHostRecord(name="nvme1", persona="Generic-ALUA")])
    intent = _intent([], ["nvme1"])
    plan = prov.build_plan(intent, discovery, reachable_hosts=set(), wsapi_factory=lambda c: array)
    row = _row(plan, "host", "nvme1")
    assert row.state == "exists" and "NVMe" in row.reason and NQN not in row.description
    prov.apply_plan(intent, discovery, reachable_hosts=set(), wsapi_factory=lambda c: array)
    assert ("fc-host", "nvme1", (), "Generic-ALUA") in array.writes          # ensure_host with no WWN: no write
    assert not [w for w in array.writes if w[0] == "iscsi-host"]


def test_an_nvme_host_that_is_not_on_the_array_is_not_planned():
    discovery = DiscoveryReport(array_hosts=parse_showhost(f"-- -- -- {NQN} 0:4:1 10.1.1.1\n"))
    nvme = DeclaredHost(name="nvme2", os="linux", address="10.1.1.1")
    plan = prov.build_plan(_intent([nvme], ["nvme2"]), discovery, reachable_hosts=set(), wsapi_factory=lambda c: _Array())
    assert not [a for a in plan.actions if a.kind == "host"]


def test_an_array_with_iscsi_ports_only_still_opens_the_gate_for_a_logged_in_iqn():
    iscsi_ports = [ArrayPort(node=n, slot=4, card_port=1, protocol="iscsi", address=f"10.0.0.{n}", link_state="ready")
                   for n in (0, 1)]
    discovery = DiscoveryReport(array_ports=iscsi_ports,
                                array_hosts=[ArrayHost(name="", iqns={LINUX_IQN: ["0:4:1", "1:4:1"]})])
    report = zoning.build_report(_intent([LINUX], ["linux-test"]), discovery)
    assert report.error is None and report.proper
    assert report.zoned_hosts == ["linux-test"] and report.iscsi_hosts == {"linux-test": ["0:4:1", "1:4:1"]}


def test_an_array_with_no_fc_port_still_refuses_to_check_fc_hosts():
    hbas = [HostHba(host_name="esx1", wwpn=WWN_A, fabric="odd", os="VMware ESXi")]
    discovery = DiscoveryReport(host_hbas=hbas, array_hosts=[ArrayHost(name="", iqns={LINUX_IQN: ["0:4:1"]})])
    report = zoning.build_report(_intent([LINUX], ["esx1", "linux-test"]), discovery)
    assert report.error and "no array FC target ports" in report.error and not report.proper
    assert report.zoned_hosts == ["linux-test"]                              # the iSCSI host is still judged
    alone = zoning.build_report(_intent([], ["esx1"]), DiscoveryReport(host_hbas=hbas))
    assert alone.error and alone.zoned_hosts == [] and alone.iscsi_hosts == {}   # as before BL-44


# ------------------------------------------------------------------ the zoning step's sentence

def _report(**fields):
    from alletra_onboard.domain.zoning import ExpectedZone, ZoningReport

    expected = [ExpectedZone(fabric=f, switch_host="sw", name=f"esx1_{f}", host_wwpn=WWN_A, array_wwpn="x", present=p)
                for f, p in fields.pop("fc", [])]
    return ZoningReport(expected=expected, **fields)


def test_the_live_run_reads_as_iscsi_not_as_zones_for_the_san_team():
    """Run eba8f3a7 said "Zoning needs 0 zone(s) … hand the command set to the SAN team … nothing can be
    provisioned" for one iSCSI host — and then created it."""
    text = zoning.summary(_report(iscsi_hosts={"zz_is_linux": []}))
    assert "SAN team" not in text and "0 zone" not in text and "nothing can be provisioned" not in text
    assert "iSCSI not logged in: zz_is_linux" in text and "can still be created" in text


def test_a_mixed_run_names_both_the_zones_and_the_iscsi_logins():
    text = zoning.summary(_report(fc=[("odd", True), ("even", False)], zoned_hosts=[],
                                  iscsi_hosts={"linux-test": []}))
    assert "Zoning needs 1 zone(s)" in text and "iSCSI not logged in: linux-test" in text
    proper = zoning.summary(_report(iscsi_hosts={"linux-test": ["0:4:1"]}, zoned_hosts=["linux-test"], proper=True))
    assert proper == "Every iSCSI host is logged in to the array; no zoning is needed."


def test_fc_only_runs_read_exactly_as_before():
    assert zoning.summary(_report(fc=[("odd", True), ("even", True)], zoned_hosts=["esx1"], proper=True)) == \
        "Zoning is correct on both fabrics."
    assert zoning.summary(_report(fc=[("odd", True), ("even", False)])) == (
        "Zoning needs 1 zone(s). Build the plan, select the pairs and hand the command set to the SAN team to "
        "apply, then re-verify. No host is zoned on both fabrics yet, so nothing can be provisioned.")
