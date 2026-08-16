"""Unit tests for the storage services with fake adapters — validate the orchestration and the
cfgshow parser without a live array / vCenter / switches."""

from __future__ import annotations

from pydantic import SecretStr

from alletra_onboard.application.provisioning import discovery as disc
from alletra_onboard.application.provisioning import storage_provision as prov
from alletra_onboard.application.provisioning import zoning
from alletra_onboard.domain.shared import EndpointCreds, normalize_wwpn
from alletra_onboard.domain.discovery import ArrayHost, ArrayPort, HostHba
from alletra_onboard.domain.provisioning import ExportRequest, ProvisioningIntent

# Concrete WWPNs (colon form for switch output; normalized for the domain objects).
ARR_O1 = "20:31:00:02:ac:02:f6:29"  # node0 slot3 port1 (odd)
ARR_O2 = "21:31:00:02:ac:02:f6:29"  # node1 slot3 port1 (odd)
ARR_E1 = "20:32:00:02:ac:02:f6:29"  # node0 slot3 port2 (even)
ARR_E2 = "21:32:00:02:ac:02:f6:29"  # node1 slot3 port2 (even)
HOST_A = "10:00:00:00:c9:00:00:01"  # esx1 HBA -> odd
HOST_B = "10:00:00:00:c9:00:00:02"  # esx1 HBA -> even


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="u", password=SecretStr("p"))


def _intent(**over) -> ProvisioningIntent:
    data = dict(
        host_set_name="CRVLZ_Hostset",
        array=_creds("10.0.0.5"),
        vcenter=_creds("vc"),
        switch_f1=_creds("sw-odd"),
        switch_f2=_creds("sw-even"),
        name_prefix="CRV_Prod", size_gib=1024, count=2,
    )
    data.update(over)
    return ProvisioningIntent.from_simple(**data)


def _ports() -> list[ArrayPort]:
    return [
        ArrayPort(node=0, slot=3, card_port=1, wwpn=normalize_wwpn(ARR_O1), link_state="ready", fabric="odd"),
        ArrayPort(node=1, slot=3, card_port=1, wwpn=normalize_wwpn(ARR_O2), link_state="ready", fabric="odd"),
        ArrayPort(node=0, slot=3, card_port=2, wwpn=normalize_wwpn(ARR_E1), link_state="ready", fabric="even"),
        ArrayPort(node=1, slot=3, card_port=2, wwpn=normalize_wwpn(ARR_E2), link_state="ready", fabric="even"),
    ]


# Effective config already has esx1/HOST_A zoned to ARR_O1 (present); everything else is missing.
CFGSHOW_ODD = f"""
Defined configuration:
 cfg:\tPROD_F1\tZ1; Zother
 zone:\tZ1\tali_hostA; ali_arrO1
 zone:\tZother\t50:00:00:00:00:00:00:09
 alias:\tali_hostA\t{HOST_A}
 alias:\tali_arrO1\t{ARR_O1}

Effective configuration:
 cfg:\tPROD_F1
 zone:\tZ1
\t\t{HOST_A}
\t\t{ARR_O1}
"""
CFGSHOW_EVEN = """
Effective configuration:
 cfg:\tPROD_F2
 zone:\tZsomething
\t\t50:00:00:00:00:00:00:0a
"""


class FakeBrocade:
    def __init__(self, ns: str, cfg: str):
        self._ns, self._cfg = ns, cfg
        self.applied: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def nsshow(self):
        return self._ns

    def cfgshow(self):
        return self._cfg

    def apply(self, commands):
        self.applied.extend(commands)
        return [(c, "operation succeeded") for c in commands]


class FakeArrayCli:
    """Stand-in for ArrayCliClient — returns canned showport / showportdev ns text per command."""

    def __init__(self, blocks: dict):
        self.blocks = blocks

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def run(self, cmd: str, timeout: float | None = None) -> str:
        return self.blocks.get(cmd, "")


class FakeVCenter:
    def __init__(self, hbas):
        self._hbas = hbas

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def host_fc_hbas(self):
        return list(self._hbas)


class FakeWsapi:
    def __init__(self, *, ports=(), hosts=(), host_sets=(), volumes=(), vsets=(), cpgs=("SSD_r6",),
                 cpg_free=10_000_000):  # MiB free per CPG; default comfortably above the fake intent
        self._ports = list(ports)
        self.hosts, self.host_sets = set(hosts), set(host_sets)
        self.volumes, self.vsets, self.cpgs = set(volumes), set(vsets), set(cpgs)
        self.cpg_free = cpg_free
        self.calls: list[tuple] = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def array_fc_ports(self):
        return self._ports

    def system_name(self):
        return "AlletraTest"

    def cpg_names(self):
        return list(self.cpgs)

    def cpg_free_mib(self):
        return {name: self.cpg_free for name in self.cpgs}

    def host_names(self):
        return list(self.hosts)

    def host_set_names(self):
        return list(self.host_sets)

    def volume_names(self):
        return list(self.volumes)

    def volume_set_names(self):
        return list(self.vsets)

    def ensure_host(self, name, wwns, persona="VMware"):
        self.calls.append(("host", name, tuple(wwns), persona))
        return "exists" if name in self.hosts else "created"

    def ensure_host_set(self, name, members):
        self.calls.append(("hostset", name))
        return "exists" if name in self.host_sets else "created"

    def ensure_volume(self, name, cpg, size_mib, ptype):
        self.calls.append(("volume", name, size_mib, ptype))
        return "exists" if name in self.volumes else "created"

    def ensure_volume_set(self, name, members):
        self.calls.append(("vvset", name))
        return "created"

    def ensure_vlun(self, vol, host, lun=None):
        self.calls.append(("vlun", vol, host) if lun is None else ("vlun", vol, host, lun))
        return "created"


# ------------------------------------------------------------------ cfgshow parser

def test_parse_active_zones_resolves_aliases_and_effective():
    zones, cfg = zoning.parse_active_zones(CFGSHOW_ODD)
    assert cfg == "PROD_F1"
    assert zones["Z1"] == {normalize_wwpn(HOST_A), normalize_wwpn(ARR_O1)}


# ------------- discovery (array-side, real HPE Primera A630 / Alletra MP command formats) -------------
# esx1 fully zoned (A odd, B even); esx2 odd-only (C odd, D never seen); esx3 not seen at all.
_A, _B = "10000000000000A1", "10000000000000B1"
_C, _D = "10000000000000C1", "10000000000000D1"
_E, _F = "10000000000000E1", "10000000000000E2"

# Real `showport`: FC host ports 0:3:3/0:3:4 + node-1 pair, iSCSI 0:4:x, and a SAS disk port (skipped).
_SHOWPORT = """N:S:P      Mode     State --Node_WWN/IP--- -Port_WWN/HW_Addr- Type Protocol       Label Partner FailoverState
0:0:1 initiator     ready 50002ACFF7025515   50002AC001025515 disk      SAS        DP-1       -             -
0:3:3    target     ready 2FF70002AC025515   20330002AC025515 host       FC           -   1:3:3          none
0:3:4    target     ready 2FF70002AC025515   20340002AC025515 host       FC        RCFC   1:3:4          none
1:3:3    target     ready 2FF70002AC025515   21330002AC025515 host       FC           -   0:3:3          none
1:3:4    target     ready 2FF70002AC025515   21340002AC025515 host       FC        RCFC   0:3:4          none
0:4:1    target     ready                -       B47AF1090E36 free    iSCSI           -       -             -
0:4:2    target   offline                -       B47AF1090E37 free    iSCSI           -       -             -"""

_SHOWPORT_ISCSI = """N:S:P State   IPAddr        Netmask/PrefixLen Gateway       TPGT  MTU   Rate iSNS_Addr iSNS_Port STGT VLAN
0:4:1 ready   10.55.234.221 255.255.248.0     10.55.239.254   41 1500 10Gbps 0.0.0.0        3205   41 Y
0:4:2 offline 0.0.0.0       0.0.0.0           0.0.0.0         42  n/a    n/a 0.0.0.0        3205   42 Y"""


def _showhost_d(rows: list[tuple[str, str, str, str]]) -> str:
    """Render `showhost -d`: one line per (name, persona, wwn, port). Real 6-column layout."""
    out = ["Id Name Persona ------------WWN/iSCSI_Name/NQN------------ Port IP_addr"]
    for i, (name, persona, wwn, port) in enumerate(rows, 1):
        out.append(f"{i} {name} {persona} {wwn} {port} n/a")
    return "\n".join(out)


_ARRAY_BLOCKS = {
    "showport": _SHOWPORT,
    "showport -iscsi": _SHOWPORT_ISCSI,
    # esx1: A logged in on 0:3:3 (odd), B on 0:3:4 (even). A Windows host with an unconnected WWN too.
    "showhost -d": _showhost_d([
        ("esx1", "VMware", _A, "0:3:3"),
        ("esx1", "VMware", _B, "0:3:4"),
        ("winbox", "WindowsServer", "50060B0000C2EE28", "---"),
    ]),
}


def test_discovery_reads_all_ports_and_hosts_from_showhost():
    hbas = [HostHba(host_name="esx1", wwpn=_A), HostHba(host_name="esx1", wwpn=_B)]
    report = disc.discover(
        _intent(),
        array_cli_factory=lambda c: FakeArrayCli(_ARRAY_BLOCKS),
        vcenter_factory=lambda c: FakeVCenter(hbas),
    )
    fc = [p for p in report.array_ports if p.protocol == "fc"]
    iscsi = [p for p in report.array_ports if p.protocol == "iscsi"]
    assert len(fc) == 4 and len(iscsi) == 2          # SAS/disk excluded; iSCSI kept incl. the offline one
    assert {p.link_state for p in iscsi} == {"ready", "offline"}
    assert next(p for p in iscsi if p.link_state == "ready").address == "10.55.234.221"
    # showhost -d -> curated hosts, each WWPN mapped to the array ports it's logged into
    esx1 = next(h for h in report.array_hosts if h.name == "esx1")
    assert esx1.persona == "VMware" and esx1.wwpns[_A] == ["0:3:3"] and esx1.wwpns[_B] == ["0:3:4"]
    winbox = next(h for h in report.array_hosts if h.name == "winbox")
    assert winbox.wwpns["50060B0000C2EE28"] == []    # configured but not logged in (no n:s:p)
    # vCenter HBAs assigned to the fabric they log into ON THE ARRAY (via showhost, not the switch)
    by_wwpn = {h.wwpn: h.fabric for h in report.host_hbas}
    assert by_wwpn[_A] == "odd" and by_wwpn[_B] == "even"
    assert not report.notes


# ------------------------------------------------------------------ zoning report + remediation

def _discovered():
    return disc.DiscoveryReport(
        array_ports=_ports(),
        host_hbas=[
            HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A), fabric="odd"),
            HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_B), fabric="even"),
        ],
    )


def _disc_for_zoning(hbas: list[HostHba]) -> "disc.DiscoveryReport":
    """A DiscoveryReport shaped like the array-side discover() output: FC ports + showhost logins.
    esx1 is logged in on both fabrics (A on 0:3:3=odd, B on 0:3:4=even); esx2 only on odd (C)."""
    ports = [
        ArrayPort(node=0, slot=3, card_port=3, protocol="fc", wwpn="20330002AC025515", link_state="ready", fabric="odd"),
        ArrayPort(node=1, slot=3, card_port=3, protocol="fc", wwpn="21330002AC025515", link_state="ready", fabric="odd"),
        ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC025515", link_state="ready", fabric="even"),
        ArrayPort(node=1, slot=3, card_port=4, protocol="fc", wwpn="21340002AC025515", link_state="ready", fabric="even"),
    ]
    array_hosts = [
        ArrayHost(name="esx1", persona="VMware", wwpns={_A: ["0:3:3", "1:3:3"], _B: ["0:3:4"]}),  # both fabrics
        ArrayHost(name="esx2", persona="VMware", wwpns={_C: ["0:3:3"]}),                            # odd only
    ]
    return disc.DiscoveryReport(array_ports=ports, array_hosts=array_hosts, host_hbas=hbas)


def test_array_side_zoning_verify_and_reconciliation():
    hbas = [
        HostHba(host_name="esx1", wwpn=_A), HostHba(host_name="esx1", wwpn=_B),
        HostHba(host_name="esx2", wwpn=_C), HostHba(host_name="esx2", wwpn=_D),
        HostHba(host_name="esx3", wwpn=_E), HostHba(host_name="esx3", wwpn=_F),
    ]
    report = zoning.build_report(_intent(), _disc_for_zoning(hbas))
    assert report.source == "array" and report.error is None

    status = {(z.name, z.present) for z in report.expected}
    assert ("esx1_odd", True) in status and ("esx1_even", True) in status     # fully zoned
    assert ("esx2_odd", True) in status and ("esx2_even", False) in status    # odd-only -> gap
    # esx3 is on neither fabric -> unverified (not zoned OR offline), not a silent pass
    assert report.unverified_hosts == ["esx3"]
    assert any("esx3" in n and "EITHER fabric" in n for n in report.notes)
    assert report.proper is False

    # best-effort remediation for esx2's missing even-fabric WWPN (D), additive + cfgenable
    even = [r for r in report.remediations if r.fabric == "even"]
    assert even and any("zonecreate" in c for c in even[0].commands)
    assert even[0].commands[-1].startswith("cfgenable")
    assert not any("cfgsave" in c for r in report.remediations for c in r.commands)


def test_array_side_zoning_all_present_is_proper():
    # esx1 only, fully zoned on both fabrics -> proper, no unverified.
    report = zoning.build_report(
        _intent(),
        _disc_for_zoning([HostHba(host_name="esx1", wwpn=_A), HostHba(host_name="esx1", wwpn=_B)]),
    )
    assert report.proper is True and not report.unverified_hosts


def test_brocade_write_surface_is_additive_only_no_delete_no_activation():
    # ADR 0004 (revised 2026-08-15, write-path mandate): the write surface is EXACTLY the three
    # additive shapes + cfgsave_defined/cfgtransabort. Guard that no delete verb and no cfgenable
    # can ever creep in — activation is a human action, and existing zones must be untouchable.
    from alletra_onboard.adapters.fabric import brocade_client as bc

    assert set(bc.ALLOWED_WRITE) == {"alicreate", "zonecreate", "cfgadd"}
    for forbidden in ("cfgenable", "cfgsave", "zonedelete", "alidelete", "cfgremove", "cfgclear",
                      "cfgdelete", "zoneremove", "aliremove"):
        assert forbidden not in bc.ALLOWED_WRITE
        assert forbidden not in bc.ALLOWED_READ
    assert not hasattr(zoning, "apply_remediation")   # the legacy remediation text is never executed


# ------------------------------------------------------------------ provisioning plan + apply

def test_build_plan_flags_existing_and_lists_actions():
    plan = prov.build_plan(
        _intent(),
        _discovered(),
        wsapi_factory=lambda c: FakeWsapi(hosts={"esx1"}, volumes={"CRV_Prod01"}),
    )
    kinds = [(a.kind, a.name, a.exists) for a in plan.actions]
    assert ("host", "esx1", True) in kinds          # esx1 already exists
    assert ("volume", "CRV_Prod01", True) in kinds  # already exists
    assert ("volume", "CRV_Prod02", False) in kinds
    assert ("vlun", "CRV_Prod01", False) in kinds   # export actions present
    assert plan.error is None


def test_apply_plan_is_idempotent_and_exports_to_host_set():
    fake = FakeWsapi(hosts={"esx1"})
    result = prov.apply_plan(_intent(), _discovered(), wsapi_factory=lambda c: fake)
    statuses = {(o.kind, o.name): o.status for o in result.outcomes}
    assert statuses[("host", "esx1")] == "exists"
    assert statuses[("volume", "CRV_Prod01")] == "created"
    # with NO explicit exports, the default is every volume -> the host SET (set:<name>) at auto LUN
    assert ("vlun", "CRV_Prod01", "set:CRVLZ_Hostset") in fake.calls
    assert result.error is None


def test_explicit_exports_override_the_default_and_carry_source_target_and_lun():
    # Stage 2: the operator-composed exports drive presentation instead of the each-vol->each-hostset
    # default — a VV-set to a host-set at an explicit LUN, and a single volume to a single host (auto).
    intent = _intent().model_copy(update={"exports": [
        ExportRequest(source_kind="vvset", source_name="CRV_VVSet", target_kind="hostset",
                      target_name="CRVLZ_Hostset", lun=100),
        ExportRequest(source_kind="volume", source_name="CRV_Prod01", target_kind="host",
                      target_name="esx1"),
    ]})
    fake = FakeWsapi(hosts={"esx1"})
    result = prov.apply_plan(intent, _discovered(), wsapi_factory=lambda c: fake)
    # source/target refs get the WSAPI set: prefix; explicit LUN is recorded, auto LUN is not
    assert ("vlun", "set:CRV_VVSet", "set:CRVLZ_Hostset", 100) in fake.calls
    assert ("vlun", "CRV_Prod01", "esx1") in fake.calls
    # the default (each volume -> set:CRVLZ_Hostset) must NOT fire when explicit exports are given
    assert ("vlun", "CRV_Prod02", "set:CRVLZ_Hostset") not in fake.calls
    assert result.error is None


def test_build_plan_previews_explicit_exports_with_lun_text():
    intent = _intent().model_copy(update={"exports": [
        ExportRequest(source_kind="volume", source_name="CRV_Prod01", target_kind="hostset",
                      target_name="CRVLZ_Hostset", lun=7),
    ]})
    fake = FakeWsapi(hosts={"esx1"})
    plan = prov.build_plan(intent, _discovered(), wsapi_factory=lambda c: fake)
    vluns = [a for a in plan.actions if a.kind == "vlun"]
    assert len(vluns) == 1  # only the one composed export, not the each-vol default
    assert "LUN 7" in vluns[0].description
    assert vluns[0].detail == {"source": "CRV_Prod01", "target": "set:CRVLZ_Hostset", "lun": 7}


def test_read_array_objects_returns_sorted_existing_and_degrades_on_error():
    fake = FakeWsapi(hosts={"h1"}, host_sets={"hs1"}, volumes={"v2", "v1"}, vsets={"vs1"}, cpgs={"SSD_r6", "NL_r6"})
    objs = prov.read_array_objects(_intent(), wsapi_factory=lambda c: fake)
    assert objs["cpgs"] == ["NL_r6", "SSD_r6"]  # sorted
    assert objs["volumes"] == ["v1", "v2"] and objs["hosts"] == ["h1"]
    assert objs["error"] is None

    def boom(_creds):
        raise RuntimeError("array down")
    degraded = prov.read_array_objects(_intent(), wsapi_factory=boom)
    assert degraded["hosts"] == [] and degraded["volumes"] == []
    assert "array down" in degraded["error"]


def test_host_briefs_summarize_fabric_login_status():
    briefs = prov.host_briefs(_discovered())  # esx1: HOST_A on odd + HOST_B on even
    assert [b.name for b in briefs] == ["esx1"]
    assert "both fabrics" in briefs[0].status
    assert len(briefs[0].wwpns) == 2

    # a host whose HBAs log into no fabric reads as not-logged-in (off / unzoned)
    one = disc.DiscoveryReport(host_hbas=[HostHba(host_name="esx9", wwpn=normalize_wwpn(HOST_A), fabric=None)])
    assert "not logged in" in prov.host_briefs(one)[0].status


def test_persona_derived_from_host_os():
    from alletra_onboard.domain.provisioning import persona_for_os

    assert persona_for_os("VMware ESXi 8.0.3") == "VMware"
    assert persona_for_os("Microsoft Windows Server 2019") == "WindowsServer"
    assert persona_for_os("Red Hat Enterprise Linux 9") == "Generic-ALUA"
    assert persona_for_os(None) == "VMware"  # default — discovery is ESXi-only today


def test_wsapi_persona_ids_match_the_array_enum():
    # Regression guard for the CLI-vs-WSAPI persona trap. createHost needs the WSAPI enum
    # (VMware=8, WindowsServer=11, Generic-ALUA=2), NOT the CLI `showhost -listpersona` numbers
    # (where VMware=11). Verified against hpe3parclient's HOST_PERSONA_* constants + a live array.
    from alletra_onboard.adapters.array.wsapi_client import _WSAPI_PERSONA

    assert _WSAPI_PERSONA["VMware"] == 8
    assert _WSAPI_PERSONA["WindowsServer"] == 11
    assert _WSAPI_PERSONA["Generic-ALUA"] == 2


# ---------------- ensure_host reconciliation (adapter-level, stub SDK) ----------------

class _StubSdk:
    """Stands in for hpe3parclient: just enough surface for ensure_host.

    Deliberately does NOT implement findHost — the real SDK's findHost runs `createhost` over its
    own (unconfigured) SSH channel, and modelling it as a working query is exactly how the live
    reconciliation bug hid behind green tests. Ownership comes from getHosts + FCPaths, the same
    surface the shipped client now reads."""

    def __init__(self, hosts=None):
        self.hosts = {n: set(w) for n, w in (hosts or {}).items()}
        self.calls = []

    def getHosts(self):
        return {"members": [
            {"name": n, "FCPaths": [{"wwn": w} for w in sorted(wwns)]}
            for n, wwns in self.hosts.items()
        ]}

    def createHost(self, name, FCWwns=None, optional=None):
        self.calls.append(("create", name, list(FCWwns), dict(optional or {})))
        self.hosts[name] = set(FCWwns)

    def modifyHost(self, name, mods):
        self.calls.append(("modify", name, dict(mods)))
        self.hosts.setdefault(name, set()).update(mods.get("FCWWNs", []))


def _client_with(stub):
    from alletra_onboard.adapters.array.wsapi_client import WsapiClient

    c = WsapiClient("192.0.2.1", "u", "p")
    c._client = stub
    return c


# 16-hex like the real thing — normalize_wwpn strips non-hex, so "W1"-style tokens would vanish.
_WA, _WB = "AABBCCDDEE000001", "AABBCCDDEE000002"


def test_ensure_host_adds_missing_wwpns_to_existing_host():
    # The silent single-path trap (audit G4), REPRODUCED LIVE 2026-08-15 before this design: a host
    # holding only HBA-1 must GAIN HBA-2 via modifyHost ADD carrying ONLY the missing WWN —
    # re-adding a present WWN draws EXISTENT_PATH from the array even against the same host.
    stub = _StubSdk(hosts={"esx1": {_WA}})
    assert _client_with(stub).ensure_host("esx1", [_WA, _WB]) == "updated"
    op, name, mods = stub.calls[0]
    assert (op, name) == ("modify", "esx1")
    assert mods == {"pathOperation": 1, "FCWWNs": [_WB]}    # ADD, and ONLY the missing one
    assert stub.hosts["esx1"] == {_WA, _WB}


def test_ensure_host_exists_only_when_every_wwn_is_registered():
    stub = _StubSdk(hosts={"esx1": {_WA, _WB}})
    assert _client_with(stub).ensure_host("esx1", [_WA, _WB]) == "exists"
    assert stub.calls == []                                  # a true no-op stays a no-op


def test_ensure_host_creates_with_wsapi_persona():
    stub = _StubSdk()
    assert _client_with(stub).ensure_host("esx1", [_WA], persona="VMware") == "created"
    assert stub.calls == [("create", "esx1", [_WA], {"persona": 8})]


def test_ensure_host_refuses_wwn_owned_by_another_host():
    import pytest
    from alletra_onboard.adapters.array.wsapi_client import WsapiError

    stub = _StubSdk(hosts={"other": {_WB}})
    with pytest.raises(WsapiError, match="other"):
        _client_with(stub).ensure_host("esx1", [_WA, _WB])
    assert stub.calls == []                                  # refused before any write


def test_ensure_host_repopulates_an_empty_existing_host():
    # The host object exists by name with no WWNs at all (a half-finished manual create):
    # reconcile by adding, not by crashing into EXISTENT_HOST.
    stub = _StubSdk(hosts={"esx1": set()})
    assert _client_with(stub).ensure_host("esx1", [_WA, _WB]) == "updated"
    assert stub.hosts["esx1"] == {_WA, _WB}


def test_find_host_by_wwn_reads_getHosts_never_sdk_findHost():
    # The SDK's findHost is a trap (it runs `createhost` over its own unconfigured SSH channel and
    # this client's old broad-except turned that into None-for-everything). The lookup must work on
    # a stub with NO findHost at all, from getHosts alone.
    stub = _StubSdk(hosts={"esx1": {_WA}})
    c = _client_with(stub)
    assert c.find_host_by_wwn(_WA) == "esx1"
    assert c.find_host_by_wwn(_WA.lower()) == "esx1"         # normalization on the lookup side
    assert c.find_host_by_wwn(_WB) is None
    assert not hasattr(stub, "findHost")


# ---------------- provisioning corrections (2026-08-15 methodology audit) ----------------

def test_build_plan_hard_gates_on_a_missing_cpg():
    # sd00003946: volume create fails with NON_EXISTENT_CPG — a missing CPG is a blocker, not a note.
    intent = _intent()
    for v in intent.volumes:
        v.cpg = "NOT_THERE"
    plan = prov.build_plan(intent, _discovered(), wsapi_factory=lambda c: FakeWsapi())
    assert plan.error and "NOT_THERE" in plan.error
    assert plan.actions == []                     # nothing offered for approval on a broken premise


def test_apply_creates_only_the_selected_hosts():
    # ADR 0010's ideal subset (audit G6): the operator composed esx1 into the host set — the other
    # vCenter hosts must NOT get array host objects (a shared vCenter is a whole datacenter).
    from alletra_onboard.domain.provisioning import HostSetRequest

    intent = _intent()
    intent.host_sets = [HostSetRequest(name="HS", members=["esx1"])]
    report = _discovered()
    report.host_hbas.append(HostHba(host_name="esx2", wwpn=normalize_wwpn(_C), fabric="odd"))
    fake = FakeWsapi()
    result = prov.apply_plan(intent, report, wsapi_factory=lambda c: fake)
    assert result.error is None
    assert [c[1] for c in fake.calls if c[0] == "host"] == ["esx1"]


def test_default_export_refuses_the_multi_hostset_cross_product():
    # The old default presented EVERY volume to EVERY host set — the same VMFS volume to unrelated
    # clusters. With >1 host set and no composed exports, both preview and apply refuse (audit G7).
    from alletra_onboard.domain.provisioning import HostSetRequest

    intent = _intent()
    intent.host_sets = [
        HostSetRequest(name="HS1", members=["esx1"]),
        HostSetRequest(name="HS2", members=["esx1"]),
    ]
    plan = prov.build_plan(intent, _discovered(), wsapi_factory=lambda c: FakeWsapi())
    assert plan.error and "refusing" in plan.error
    result = prov.apply_plan(intent, _discovered(), wsapi_factory=lambda c: FakeWsapi())
    assert result.error and "Compose the exports" in result.error


def test_export_lun_id_bounded_by_the_platform_range():
    # 0..16383 on the 3PAR lineage — LUN 4000 was observed live on a production Primera, so the
    # "obvious" 0..255 bound would be wrong in both directions.
    import pytest
    from pydantic import ValidationError
    from alletra_onboard.domain.provisioning import ExportRequest

    def _ex(lun):
        return ExportRequest(source_kind="volume", source_name="v",
                             target_kind="hostset", target_name="h", lun=lun)

    for ok in (0, 4000, 16383):
        _ex(ok)
    with pytest.raises(ValidationError):
        _ex(16384)
    with pytest.raises(ValidationError):
        _ex(-1)


def test_subscription_refusal_is_translated_to_the_onboarding_gate():
    # Hit live on a fresh B10000: every create refused until GreenLake onboarding completes. The
    # raw message reads like a WSAPI defect — the translation names the sequencing fix.
    from alletra_onboard.adapters.array.wsapi_client import WsapiClient, WsapiError

    err = WsapiClient("h", "u", "p")._translate(
        Exception("Error: Array has not yet completed the subscription process"),
        where="createVolume CRV_Prod01",
    )
    assert isinstance(err, WsapiError) and "GreenLake" in str(err)


class _StubSdkSets(_StubSdk):
    """_StubSdk plus host/volume sets, for the set-membership reconciliation."""

    def __init__(self, sets=None):
        super().__init__()
        self.sets = {n: list(m) for n, m in (sets or {}).items()}

    def getHostSet(self, name):
        if name not in self.sets:
            raise LookupError(name)
        return {"setmembers": list(self.sets[name])}

    getVolumeSet = getHostSet

    def createHostSet(self, name, setmembers=None):
        self.calls.append(("createset", name, list(setmembers or [])))
        self.sets[name] = list(setmembers or [])

    def modifyHostSet(self, name, action=None, setmembers=None):
        self.calls.append(("modifyset", name, action, list(setmembers or [])))
        self.sets[name].extend(setmembers or [])


def test_ensure_host_set_adds_missing_members():
    # Same reconciliation principle as ensure_host (audit G4): exists-with-missing-members must
    # GAIN them — additive only, a member someone else added is never removed.
    stub = _StubSdkSets(sets={"HS": ["esx1"]})
    assert _client_with(stub).ensure_host_set("HS", ["esx1", "esx2"]) == "updated"
    op, name, action, members = stub.calls[-1]
    assert (op, name, members) == ("modifyset", "HS", ["esx2"]) and action is not None
    assert stub.sets["HS"] == ["esx1", "esx2"]


def test_ensure_host_set_exists_means_every_member_verified():
    stub = _StubSdkSets(sets={"HS": ["esx1", "esx2", "someone_elses_host"]})
    assert _client_with(stub).ensure_host_set("HS", ["esx1", "esx2"]) == "exists"
    assert stub.calls == []                       # the extra member is none of our business


def test_ensure_host_set_creates_when_absent():
    stub = _StubSdkSets()
    assert _client_with(stub).ensure_host_set("HS", ["esx1"]) == "created"
    assert stub.calls == [("createset", "HS", ["esx1"])]


# ---------------- readiness preflight (read-only; runs BEFORE discovery) ----------------

def _preflight(*, wsapi=None, hbas=(), **intent_over):
    from alletra_onboard.application.provisioning import preflight

    return preflight.run_preflight(
        _intent(**intent_over),
        wsapi_factory=lambda c: wsapi if wsapi is not None else FakeWsapi(ports=_ports()),
        vcenter_factory=lambda c: FakeVCenter(hbas),
    )


def _by_key(report):
    return {c.key: c for c in report.checks}


def test_preflight_all_green_when_array_and_vcenter_are_ready():
    report = _preflight(hbas=[HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A), os="VMware ESXi 8.0.3")])
    assert report.ready is True
    assert {c.status for c in report.checks} == {"pass"}
    assert "esx1" in _by_key(report)["vcenter"].detail


def test_preflight_fails_loudly_when_the_array_is_unreachable_but_still_reports_vcenter():
    class Dead:
        def __enter__(self):
            raise OSError("connection refused")

        def __exit__(self, *a):
            return False

    report = _preflight(wsapi=Dead(), hbas=[HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A))])
    checks = _by_key(report)
    assert report.ready is False
    assert checks["array"].status == "fail" and "connection refused" in checks["array"].detail
    # vCenter is independently reachable, so it is still answered rather than guessed at.
    assert checks["vcenter"].status == "pass"
    assert "cpg" not in checks and "names" not in checks  # unknowable without the array


def test_preflight_fails_when_the_sheet_names_a_cpg_the_array_does_not_have():
    report = _preflight(wsapi=FakeWsapi(ports=_ports(), cpgs=("NL_r6",)), cpg="SSD_r6",
                        hbas=[HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A))])
    cpg = _by_key(report)["cpg"]
    assert report.ready is False
    assert cpg.status == "fail" and "SSD_r6" in cpg.detail and "NL_r6" in cpg.detail


def test_preflight_warns_but_does_not_block_on_tight_capacity_or_existing_names():
    # Thin volumes do not consume their nominal size, and apply is idempotent — neither is fatal.
    report = _preflight(
        wsapi=FakeWsapi(ports=_ports(), cpg_free=1, volumes=("CRV_Prod01",)),
        hbas=[HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A))],
    )
    checks = _by_key(report)
    assert report.ready is True  # warnings never block
    assert checks["cpg"].status == "warn"
    assert checks["names"].status == "warn" and "CRV_Prod01" in checks["names"].detail


def test_preflight_fails_when_vcenter_reports_no_hosts_because_apply_would_refuse():
    report = _preflight(hbas=[])
    vc = _by_key(report)["vcenter"]
    assert report.ready is False
    assert vc.status == "fail" and "no ESXi host" in vc.detail


def test_preflight_fails_when_no_fc_target_port_has_a_ready_link():
    dark = [ArrayPort(node=0, slot=3, card_port=1, wwpn=normalize_wwpn(ARR_O1),
                      link_state="loss_sync", mode="target", fabric="odd")]
    report = _preflight(wsapi=FakeWsapi(ports=dark),
                        hbas=[HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A))])
    ports = _by_key(report)["ports"]
    assert report.ready is False
    assert ports.status == "fail" and "ready link" in ports.detail


def test_preflight_does_not_count_initiator_ports_as_host_capacity():
    # Live shape from 4UW0004497: ready FC ports, but two of them are mode 3 (initiator) and serve
    # replication, not hosts. Counting them would overstate the array's host-facing capacity.
    mixed = [
        ArrayPort(node=0, slot=3, card_port=1, wwpn=normalize_wwpn(ARR_O1), link_state="ready", mode="target", fabric="odd"),
        ArrayPort(node=0, slot=3, card_port=3, wwpn=normalize_wwpn(ARR_O2), link_state="ready", mode="initiator", fabric="odd"),
    ]
    report = _preflight(wsapi=FakeWsapi(ports=mixed),
                        hbas=[HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A))])
    ports = _by_key(report)["ports"]
    assert ports.status == "pass"
    assert "1 of 1 FC target port(s) ready" in ports.detail
    assert "1 initiator/peer port(s) excluded" in ports.detail


def test_preflight_fails_when_every_fc_port_is_initiator_mode():
    only_initiators = [
        ArrayPort(node=0, slot=3, card_port=3, wwpn=normalize_wwpn(ARR_O1), link_state="ready", mode="initiator", fabric="odd"),
    ]
    report = _preflight(wsapi=FakeWsapi(ports=only_initiators),
                        hbas=[HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A))])
    ports = _by_key(report)["ports"]
    assert report.ready is False
    assert ports.status == "fail" and "initiator or peer mode" in ports.detail


def test_wsapi_port_enums_map_to_the_cli_vocabulary():
    # ArrayPort.link_state is documented as "ready | offline | loss_sync"; the WSAPI reports integers.
    # Leaking "4" into that field would break every consumer that compares against "ready".
    from alletra_onboard.adapters.array.wsapi_client import _PORT_LINK_STATE, _PORT_MODE

    assert _PORT_LINK_STATE[4] == "ready"
    assert _PORT_MODE[2] == "target" and _PORT_MODE[3] == "initiator"


def test_preflight_never_writes_to_the_array():
    # The whole contract: readiness is established by reads. A create here would be a defect —
    # the subscription gate is translated at apply time, not probed with a throwaway volume.
    fake = FakeWsapi(ports=_ports())
    _preflight(wsapi=fake, hbas=[HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A))])
    assert fake.calls == []


def test_wsapi_volume_bodies_match_what_the_array_accepts():
    # Regression guard for the data-reduction body. Proven live on a B10000 (WSAPI 1.15.60 /
    # OS 10.5.60.36) with throwaway zz_recon_* volumes in SSD_r6:
    #   {"tdvv": True, "compression": True} -> 400 code 78 "one of the parameters is required: tpvv,reduce"
    #   {"tpvv": True, "compression": True} -> 400 code 42 "unrecognized name: compression"
    #   {"reduce": True}                    -> 201, reads back provisioningType=6, dedup on
    # `compression` is not a field on this API at all, and `tdvv` is the legacy 3PAR spelling.
    from alletra_onboard.adapters.array.wsapi_client import WsapiClient

    class SpyClient:
        def __init__(self) -> None:
            self.calls: list[tuple] = []

        def createVolume(self, name, cpg, size_mib, optional=None):  # noqa: N802 - SDK spelling
            self.calls.append((name, cpg, size_mib, optional))

    client = WsapiClient(host="array", username="3paradm", password="x")
    spy = SpyClient()
    client._client = spy

    assert client.ensure_volume("v_reduce", "SSD_r6", 1024, "reduce") == "created"
    assert client.ensure_volume("v_thin", "SSD_r6", 1024, "tpvv") == "created"

    bodies = {call[0]: call[3] for call in spy.calls}
    assert bodies["v_reduce"] == {"reduce": True}   # NOT tdvv, and no compression key
    assert bodies["v_thin"] == {"tpvv": True}


def test_apply_plan_sets_persona_per_host_os():
    d = disc.DiscoveryReport(host_hbas=[
        HostHba(host_name="esx1", wwpn=_A, os="VMware ESXi 8.0.3"),
        HostHba(host_name="winbox", wwpn=_B, os="Microsoft Windows Server 2022"),
    ])
    fake = FakeWsapi()
    prov.apply_plan(_intent(), d, wsapi_factory=lambda c: fake)
    personas = {c[1]: c[3] for c in fake.calls if c[0] == "host"}  # ("host", name, wwns, persona)
    assert personas == {"esx1": "VMware", "winbox": "WindowsServer"}  # name per host, not hardcoded


# ---------------- fabric resolution (#3: fabric from showportdev fcfabric, parity fallback) ----------------
_SW_F2 = "SW6600_Q5U38_F2"   # the switch the odd-parity host ports (…:3) attach to (real calibration)
_SW_F1 = "SW6600_Q5U39_F1"   # the switch the even-parity host ports (…:4) attach to


def _fc4() -> list[ArrayPort]:
    """The four FC host ports (nodes 0/1 x ports :3/:4), fabric pre-set by parity as parse_ports leaves them."""
    return [
        ArrayPort(node=0, slot=3, card_port=3, protocol="fc", wwpn="20330002AC025515", link_state="ready", fabric="odd"),
        ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC025515", link_state="ready", fabric="even"),
        ArrayPort(node=1, slot=3, card_port=3, protocol="fc", wwpn="21330002AC025515", link_state="ready", fabric="odd"),
        ArrayPort(node=1, slot=3, card_port=4, protocol="fc", wwpn="21340002AC025515", link_state="ready", fabric="even"),
    ]


def test_resolve_fabrics_switch_agreeing_with_parity_is_silent():
    # The real Primera calibration: :3 ports -> F2 switch, :4 ports -> F1 switch. Same GROUPING as parity.
    ports = _fc4()
    sw = {"0:3:3": _SW_F2, "1:3:3": _SW_F2, "0:3:4": _SW_F1, "1:3:4": _SW_F1}
    notes = disc.resolve_port_fabrics(ports, sw)
    assert {p.label: p.fabric for p in ports} == {"0:3:3": "odd", "1:3:3": "odd", "0:3:4": "even", "1:3:4": "even"}
    assert next(p for p in ports if p.label == "0:3:3").fabric_switch == _SW_F2
    assert notes == []          # switch agrees with parity -> identical result, nothing to report


def test_resolve_fabrics_overrides_parity_on_nonstandard_cabling():
    # 1:3:4 (even card-port) is miscabled onto the F2 switch, where the odd ports live -> parity is wrong.
    ports = _fc4()
    sw = {"0:3:3": _SW_F2, "1:3:3": _SW_F2, "0:3:4": _SW_F1, "1:3:4": _SW_F2}
    notes = disc.resolve_port_fabrics(ports, sw)
    assert next(p for p in ports if p.label == "1:3:4").fabric == "odd"   # follows the switch, not parity
    assert any("1:3:4" in n and "non-standard" in n for n in notes)


def test_resolve_fabrics_falls_back_to_parity_without_switch_data():
    # e.g. every host port is loss_sync (the 225 today) -> no fcfabric data -> parity, no noise.
    ports = _fc4()
    notes = disc.resolve_port_fabrics(ports, {})
    assert {p.label: p.fabric for p in ports} == {"0:3:3": "odd", "1:3:3": "odd", "0:3:4": "even", "1:3:4": "even"}
    assert all(p.fabric_switch == "" for p in ports)
    assert notes == []


def test_resolve_fabrics_more_than_two_switches_uses_parity_with_note():
    ports = _fc4()
    sw = {"0:3:3": "SWA", "1:3:3": "SWB", "0:3:4": "SWC", "1:3:4": "SWC"}
    notes = disc.resolve_port_fabrics(ports, sw)
    assert next(p for p in ports if p.label == "0:3:3").fabric == "odd"   # parity fallback
    assert any("3 fabric switches" in n for n in notes)


def test_resolve_fabrics_two_switches_same_parity_labels_by_switch():
    # Both attach-switches sit at odd card-port parity -> parity can't name them; stable-order labelling.
    ports = [
        ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC025515", link_state="ready", fabric="odd"),
        ArrayPort(node=1, slot=3, card_port=3, protocol="fc", wwpn="21330002AC025515", link_state="ready", fabric="odd"),
    ]
    notes = disc.resolve_port_fabrics(ports, {"0:3:1": "SWB", "1:3:3": "SWA"})
    assert {p.fabric for p in ports} == {"odd", "even"}                   # split into two distinct slots
    assert any("same card-port parity" in n for n in notes)


def _fcfabric(port_wwpn: str, switch_name: str) -> str:
    """Minimal `showportdev fcfabric` text: the port's WWPN sits as the attached N-Port on switch_name."""
    return (
        "Fabric information\n"
        f"  Logical Name: {switch_name}\n"
        f"    13 2000000000000001 F-Port Online unknown {port_wwpn} N-Port\n"
    )


def test_discovery_refines_fabric_from_switch():
    blocks = dict(_ARRAY_BLOCKS)
    blocks["showportdev fcfabric 0:3:3"] = _fcfabric("20330002AC025515", "SWX_F2")
    blocks["showportdev fcfabric 1:3:3"] = _fcfabric("21330002AC025515", "SWX_F2")
    blocks["showportdev fcfabric 0:3:4"] = _fcfabric("20340002AC025515", "SWY_F1")
    blocks["showportdev fcfabric 1:3:4"] = _fcfabric("21340002AC025515", "SWY_F1")
    hbas = [HostHba(host_name="esx1", wwpn=_A), HostHba(host_name="esx1", wwpn=_B)]
    report = disc.discover(
        _intent(),
        array_cli_factory=lambda c: FakeArrayCli(blocks),
        vcenter_factory=lambda c: FakeVCenter(hbas),
    )
    fc = {p.label: p for p in report.array_ports if p.protocol == "fc"}
    assert fc["0:3:3"].fabric_switch == "SWX_F2" and fc["0:3:3"].fabric == "odd"
    assert fc["0:3:4"].fabric_switch == "SWY_F1" and fc["0:3:4"].fabric == "even"
    assert not report.notes        # switch agrees with parity -> silent


def test_switch_for_wwpn_finds_the_f_port_switch():
    text = _fcfabric("20330002AC025515", "SWX_F2")
    assert disc.switch_for_wwpn(text, "20:33:00:02:ac:02:55:15") == "SWX_F2"   # colon form normalizes
    assert disc.switch_for_wwpn(text, "DEADBEEFDEADBEEF") is None


def test_discovery_emits_progress_for_each_substep():
    """Discovery reports progress so a long run (per-port fabric probe + vCenter) doesn't look hung."""
    msgs: list[str] = []
    disc.discover(
        _intent(),
        array_cli_factory=lambda c: FakeArrayCli(_ARRAY_BLOCKS),
        vcenter_factory=lambda c: FakeVCenter([HostHba(host_name="esx1", wwpn=_A)]),
        progress=msgs.append,
    )
    joined = " ".join(msgs).lower()
    assert "ssh" in joined and "port" in joined and "vcenter" in joined     # each phase announced
    # per-port fabric probe is the slow part -> it must report which port it is on (e.g. "0:3:3 (1/4)")
    assert any("resolving" in m.lower() and "0:3:3" in m for m in msgs)


# ---------------------------------------------------------------- tier-2 path verification (ADR 0010)

# Real `showvlun -a` rows from a live Alletra MP (VZ, OS 10.5.51). Type is two words ("host set"), the
# volume name is long — the parser must anchor on the n:s:p port token, not fixed offsets.
_VZ_SHOWVLUN_A = """\
Lun VVName                               HostName              -Host_WWN/iSCSI_Name/Host_NQN-  Port     Type Status ID
  1 VZ_ESXi_Profile_bk                   CRV_VZ_DL360G11D24U25 10009440C9D01212               0:3:1 host set nonopt 10
  4 2nd_Attempt_sv_CRV_LZ_Infra_RW       CRV_VZ_DL360G11D24U25 10009440C9D01212               0:3:1 host set active 10
  1 VZ_ESXi_Profile_bk                   CRV_VZ_DL360G11D24U25 10009440C9D01213               0:3:2 host set nonopt 10
  1 VZ_ESXi_Profile_bk                   CRV_VZ_DL360G11D24U25 10009440C9D01212               1:3:1 host set active 11
  1 VZ_ESXi_Profile_bk                   CRV_VZ_DL360G11D24U25 10009440C9D01213               1:3:2 host set active 11
"""


def test_parse_showvlun_active_real_sample():
    from alletra_onboard.application.provisioning.path_verify import parse_showvlun_active

    paths = parse_showvlun_active(_VZ_SHOWVLUN_A)
    assert len(paths) == 5                                   # header skipped, 5 data rows
    p = paths[1]                                             # the 'active' Infra path on 0:3:1
    assert p.lun == 4 and p.volume == "2nd_Attempt_sv_CRV_LZ_Infra_RW"
    assert p.host == "CRV_VZ_DL360G11D24U25"
    assert p.host_wwpn == "10009440C9D01212" and p.port == "0:3:1" and p.status == "active"


def test_verify_paths_live_both_fabrics():
    from alletra_onboard.application.provisioning.path_verify import parse_showvlun_active, verify_paths

    paths = parse_showvlun_active(_VZ_SHOWVLUN_A)
    rep = verify_paths({"CRV_VZ_DL360G11D24U25"}, {"VZ_ESXi_Profile_bk"}, paths)
    h = rep.hosts[0]
    assert h.verdict == "live"
    assert h.fabrics == ["even", "odd"]                     # 0:3:1/1:3:1 odd + 0:3:2/1:3:2 even
    assert h.hbas_with_paths == 2                           # both HBAs carry a live path
    assert h.dead_volumes == []


def test_verify_paths_no_path_when_host_absent():
    from alletra_onboard.application.provisioning.path_verify import parse_showvlun_active, verify_paths

    paths = parse_showvlun_active(_VZ_SHOWVLUN_A)
    rep = verify_paths({"esx-offline"}, {"VZ_ESXi_Profile_bk"}, paths)
    h = rep.hosts[0]
    assert h.verdict == "no_path" and h.hbas_with_paths == 0
    assert h.dead_volumes == ["VZ_ESXi_Profile_bk"]         # exported target with no live path
    assert "not zoned" in h.detail.lower()


def test_verify_paths_partial_single_fabric():
    from alletra_onboard.application.provisioning.path_verify import parse_showvlun_active, verify_paths

    text = (
        "Lun VVName HostName -Host_WWN- Port Type Status ID\n"
        "  1 Vol1 esx1 10000000AAAA0001 0:3:1 host set active 10\n"   # odd fabric only
    )
    rep = verify_paths({"esx1"}, {"Vol1"}, parse_showvlun_active(text))
    h = rep.hosts[0]
    assert h.verdict == "partial" and h.fabrics == ["odd"]
    assert "missing the even fabric" in h.detail


def test_verify_paths_joins_by_wwpn_across_naming_namespaces():
    # MEASURED live 2026-08-15: vCenter names hosts by bare IP (10.55.235.120 / 10.99.1.1) while the
    # array's host objects carry rack names (CRV_VZ_DL360G11D24U25) — zero exact-name matches across
    # three arrays, so an exact-name join reported no_path for every pre-existing host. The HBA WWPN
    # is the only key the two namespaces share.
    from alletra_onboard.application.provisioning.path_verify import parse_showvlun_active, verify_paths

    paths = parse_showvlun_active(_VZ_SHOWVLUN_A)
    rep = verify_paths(
        {"10.99.1.1"}, {"VZ_ESXi_Profile_bk"}, paths,
        wwpns_by_host={"10.99.1.1": {"10009440C9D01212", "10009440C9D01213"}},
    )
    h = rep.hosts[0]
    assert h.verdict == "live"                              # not the old no_path lie
    assert h.hbas_with_paths == 2
    assert "CRV_VZ_DL360G11D24U25" in h.detail              # names the array object it matched

    # Without the WWPN map the name join still finds nothing — the regression this test pins.
    bare = verify_paths({"10.99.1.1"}, {"VZ_ESXi_Profile_bk"}, paths)
    assert bare.hosts[0].verdict == "no_path"


def test_verify_paths_uses_discovered_fabric_over_parity_on_miscabled_ports():
    # MEASURED environment (4UW0004497): port 0:3:4 has an EVEN card port but is cabled to the F1
    # (odd) switch. A host with paths on 0:3:1 + 0:3:4 has both paths on ONE fabric — parity alone
    # would call it "live on both fabrics", a false redundancy claim. Discovery's switch-derived
    # fabric map must win; parity remains the fallback when no map is supplied.
    from alletra_onboard.application.provisioning.path_verify import parse_showvlun_active, verify_paths

    text = (
        "Lun VVName HostName -Host_WWN- Port Type Status ID\n"
        "  1 Vol1 esx1 10000000AAAA0001 0:3:1 host set active 10\n"
        "  1 Vol1 esx1 10000000AAAA0002 0:3:4 host set active 10\n"   # even parity, but F1-cabled
    )
    paths = parse_showvlun_active(text)

    with_map = verify_paths({"esx1"}, {"Vol1"}, paths, {"0:3:1": "odd", "0:3:4": "odd"})
    assert with_map.hosts[0].verdict == "partial"           # the truth: one fabric, no redundancy
    assert with_map.hosts[0].fabrics == ["odd"]

    parity_only = verify_paths({"esx1"}, {"Vol1"}, paths)
    assert parity_only.hosts[0].verdict == "live"           # the lie parity tells on this cabling


def test_verify_provisioned_paths_reads_showvlun_and_reports():
    from alletra_onboard.application.provisioning.path_verify import verify_provisioned_paths

    class _FakeCli:
        def __init__(self):
            self.cmds = []

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def run(self, cmd, **k):
            self.cmds.append(cmd)
            return _VZ_SHOWVLUN_A

    fake = _FakeCli()
    intent = _intent(name_prefix="VZ_ESXi_Profile_bk", size_gib=10, count=1)
    d = disc.DiscoveryReport(host_hbas=[HostHba(host_name="CRV_VZ_DL360G11D24U25", wwpn=_A)])
    rep = verify_provisioned_paths(intent, d, array_cli_factory=lambda creds: fake)

    assert "showvlun -a" in fake.cmds                        # it read the array, read-only
    h = next(x for x in rep.hosts if x.host == "CRV_VZ_DL360G11D24U25")
    assert h.verdict == "live" and "VZ_ESXi_Profile_bk" in h.live_volumes
