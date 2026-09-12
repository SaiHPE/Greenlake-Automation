"""Zoning PLAN (ADR 0004 revised) — the read-only, assisted command builder. No switch writes:
build the per-fabric SIST plan from read-only switch data, keep every alias, render the preview.

Two kinds of tests here: small synthetic cases for the plan/render logic, and REAL-CAPTURE tests
against tests/fixtures/vz_fabric — full `nsshow`/`nscamshow`/`alishow`/`cfgactvshow` output taken
from the live VZ fabric switches on 2026-08-14. The synthetic cases alone let the alias-pollution
bug survive (a fake never dumps the trailing effective section the way a real switch does)."""

from __future__ import annotations

from pathlib import Path

from alletra_onboard.application.provisioning import zoning_plan as zp
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.discovery import ArrayPort, DiscoveryReport, HostHba
from alletra_onboard.domain.provisioning import ProvisioningIntent

_ARR_031 = "20:31:00:02:ac:02:f6:29"
_ARR_032 = "20:32:00:02:ac:02:f6:29"
_HOST_A = "10:00:00:00:00:00:00:aa"
_HOST_B = "10:00:00:00:00:00:00:bb"

_F1_NS = f"""
 N    010200;   3;{_ARR_031};2f:f7:00:02:ac:02:f6:29; 0x0
    PortSymb: [10] "MPB10K - 0:3:1"
    Device type: Physical Target
 N    010300;   3;{_HOST_A};20:00:00:00:00:00:00:aa; 0x0
    PortSymb: [10] "Emulex PPN-hostx"
    Device type: Physical Initiator
"""
# The array port carries TWO aliases on this shared fabric — the convention one + stale noise.
_F1_ALIS = f"""
 alias:\tCRVLZ_MPB10K_LZ_031
\t\t{_ARR_031}
 alias:\twinhost_fc_port_2
\t\t{_ARR_031}
 alias:\thostx_HBA1_Port1
\t\t{_HOST_A}
"""
_F1_CFG = "Defined configuration:\n cfg:\tOTHER\tz0\nEffective configuration:\n cfg:\tF1_CFG\n"

_F2_NS = f"""
 N    020200;   3;{_ARR_032};2f:f7:00:02:ac:02:f6:29; 0x0
    Device type: Physical Target
 N    020300;   3;{_HOST_B};20:00:00:00:00:00:00:bb; 0x0
    Device type: Physical Initiator
"""
_F2_ALIS = f" alias:\tCRVLZ_MPB10K_LZ_032\n\t\t{_ARR_032}\n"
_F2_CFG = "Effective configuration:\n cfg:\tF2_CFG\n"


class FakeBrocade:
    def __init__(self, ns, alis, cfg):
        self._ns, self._alis, self._cfg = ns, alis, cfg

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def nsshow(self):
        return self._ns

    def nscamshow(self):
        return ""

    def alishow(self):
        return self._alis

    def cfgshow(self):
        return self._cfg


def _creds(host):
    return EndpointCreds(host=host, username="u", password="p")


def _intent():
    return ProvisioningIntent.from_simple(
        host_set_name="hs", array=_creds("array"), vcenter=_creds("vc"),
        switch_f1=_creds("sw-f1"), switch_f2=_creds("sw-f2"),
        name_prefix="v", size_gib=1,
    )


def _factory(creds):
    if creds.host == "sw-f1":
        return FakeBrocade(_F1_NS, _F1_ALIS, _F1_CFG)
    return FakeBrocade(_F2_NS, _F2_ALIS, _F2_CFG)


def _discovery(hbas=None):
    return DiscoveryReport(
        host_hbas=hbas if hbas is not None else [
            HostHba(host_name="hostx", wwpn=_HOST_A), HostHba(host_name="hostx", wwpn=_HOST_B),
        ],
        array_ports=[
            ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC02F629", link_state="ready"),
            ArrayPort(node=0, slot=3, card_port=2, protocol="fc", wwpn="20320002AC02F629", link_state="ready"),
        ],
    )


def test_parse_aliases_keeps_all_aliases_per_wwpn():
    aliases = zp.parse_aliases(_F1_ALIS)
    assert aliases["20310002AC02F629"] == ["CRVLZ_MPB10K_LZ_031", "winhost_fc_port_2"]  # both, in order


def test_parse_active_cfg_uses_effective_not_first_defined():
    assert zp.parse_active_cfg(_F1_CFG) == "F1_CFG"   # not the decoy 'OTHER'


def test_build_plan_maps_fabrics_pairs_and_prefers_convention_alias():
    plan = zp.build_zoning_plan(_intent(), _discovery(), brocade_factory=_factory)
    f1 = next(f for f in plan.fabrics if f.fabric == "F1")
    assert f1.active_cfg == "F1_CFG"
    assert [h.host_name for h in f1.hosts] == ["hostx"]
    assert [p.nsp for p in f1.array_ports] == ["0:3:1"]
    assert f1.pairs == [("10000000000000AA", "20310002AC02F629")]   # single-init-single-target
    arr = f1.array_ports[0]
    assert arr.existing_aliases == ["CRVLZ_MPB10K_LZ_031", "winhost_fc_port_2"]  # multi-alias kept
    assert arr.suggested_alias == "CRVLZ_MPB10K_LZ_031"             # convention match, not the noise
    assert not plan.offline_hosts


def test_render_commands_reuses_existing_alias_no_alicreate():
    plan = zp.build_zoning_plan(_intent(), _discovery(), brocade_factory=_factory)
    f1 = zp.render_commands(plan, {})[0]["F1"]
    assert not any(c.startswith("alicreate") for c in f1)          # both aliases already exist
    assert 'zonecreate "hostx_HBA1_Port1_CRVLZ_MPB10K_LZ_031","hostx_HBA1_Port1;CRVLZ_MPB10K_LZ_031"' in f1
    assert 'cfgadd "F1_CFG","hostx_HBA1_Port1_CRVLZ_MPB10K_LZ_031"' in f1
    assert "cfgenable F1_CFG" in f1


def test_render_commands_alicreate_for_a_new_operator_alias():
    plan = zp.build_zoning_plan(_intent(), _discovery(), brocade_factory=_factory)
    cmds, _ = zp.render_commands(plan, {"10000000000000AA": "CRVLZ_HOSTX_R1U1_HBA_1_Port_1"})
    assert 'alicreate "CRVLZ_HOSTX_R1U1_HBA_1_Port_1","10:00:00:00:00:00:00:aa"' in cmds["F1"]


def test_alias_on_the_other_fabric_does_not_suppress_alicreate():
    # MEASURED live 2026-08-15: 41 alias names exist on BOTH lab fabrics. With one flat alias pool,
    # an alias defined only on F2 suppressed the F1 alicreate — so F1's zonecreate referenced a name
    # F1 has never defined, and the switch would reject the script. Alias existence is per fabric.
    f1_alis = f" alias:\tCRVLZ_MPB10K_LZ_031\n\t\t{_ARR_031}\n"     # F1 has NO alias for the host
    f2_alis = (
        f" alias:\thostx_HBA1_Port1\n\t\t{_HOST_A}\n"               # the host's alias lives on F2 only
        f" alias:\tCRVLZ_MPB10K_LZ_032\n\t\t{_ARR_032}\n"
    )

    def factory(creds):
        if creds.host == "sw-f1":
            return FakeBrocade(_F1_NS, f1_alis, _F1_CFG)
        return FakeBrocade(_F2_NS, f2_alis, _F2_CFG)

    plan = zp.build_zoning_plan(_intent(), _discovery(), brocade_factory=factory)
    host = next(f for f in plan.fabrics if f.fabric == "F1").hosts[0]
    assert host.existing_aliases == []                              # per-fabric truth: F1 has none

    cmds, _ = zp.render_commands(plan, {"10000000000000AA": "hostx_HBA1_Port1"})
    assert 'alicreate "hostx_HBA1_Port1","10:00:00:00:00:00:00:aa"' in cmds["F1"]


def test_transient_empty_nameserver_is_called_out_not_silently_accepted():
    # MEASURED live 2026-08-15: one plan run got an EMPTY local NS from a healthy F2 switch, so
    # both F2-resident array ports (carrying ACTIVE VLUNs!) silently vanished from the plan. A
    # ready port in neither fabric's NS is an anomaly the plan must report, twice over: the empty
    # local NS itself, and the specific unplaced ports.
    def factory(creds):
        if creds.host == "sw-f1":
            return FakeBrocade(_F1_NS, _F1_ALIS, _F1_CFG)
        return FakeBrocade("", "", _F2_CFG)                  # F2: nothing in the name server

    plan = zp.build_zoning_plan(_intent(), _discovery(), brocade_factory=factory)
    assert any("no LOCAL name-server entries" in n for n in plan.notes)
    unplaced = [n for n in plan.notes if "neither declared fabric's name server" in n]
    assert unplaced and "0:3:2" in unplaced[0]               # the ready F2-resident port, by name
    f2 = next(f for f in plan.fabrics if f.fabric == "F2")
    assert f2.array_ports == []                              # still absent — but never silently


def test_merged_fabric_is_called_out_not_silently_collapsed():
    # The meshed-lab failure mode: both declared switches are ISL'd into ONE fabric, both name
    # servers see the same devices, first-match placement lands everything on F1 and F2 comes back
    # empty. The plan must SAY so instead of presenting single-fabric zoning as dual-fabric.
    def factory(creds):
        return FakeBrocade(_F1_NS, _F1_ALIS, _F1_CFG)               # identical view from both switches

    plan = zp.build_zoning_plan(_intent(), _discovery(), brocade_factory=factory)
    assert any("merged fabric" in n.lower() for n in plan.notes)
    f2 = next(f for f in plan.fabrics if f.fabric == "F2")
    assert f2.hosts == [] and f2.array_ports == []                  # everything landed on F1


def test_offline_host_is_flagged_never_guessed():
    plan = zp.build_zoning_plan(
        _intent(),
        _discovery([HostHba(host_name="ghost", wwpn="10:00:00:00:00:00:00:cc")]),
        brocade_factory=_factory,
    )
    assert any("ghost" in entry for entry in plan.offline_hosts)
    ghost = "10000000000000CC"
    assert all(ghost not in pair for f in plan.fabrics for pair in f.pairs)   # nothing zoned for an offline host
    # The initiators the declared switches DO see are still candidates (union rule, 2026-09-12).
    assert {h.wwpn for f in plan.fabrics for h in f.hosts} == {"10000000000000AA", "10000000000000BB"}


def test_suggested_alias_prefers_unique_over_shared_junk():
    # SHARED_JUNK is bound to BOTH the host and the array port (freq >= 2) -> junk. A shared alias must
    # never be suggested (that's what made 3 hosts collide on one alias live); the unique one wins.
    alis = (
        f" alias:\tSHARED_JUNK\n\t\t{_HOST_A}\n"
        f" alias:\tSHARED_JUNK\n\t\t{_ARR_031}\n"
        f" alias:\tCRVProd_hostA_P1\n\t\t{_HOST_A}\n"
    )

    def factory(creds):
        return FakeBrocade(_F1_NS, alis, _F1_CFG) if creds.host == "sw-f1" else FakeBrocade(_F2_NS, "", _F2_CFG)

    plan = zp.build_zoning_plan(_intent(), _discovery(), brocade_factory=factory)
    f1 = next(f for f in plan.fabrics if f.fabric == "F1")
    host = next(h for h in f1.hosts if h.wwpn == "10000000000000AA")
    assert host.suggested_alias == "CRVProd_hostA_P1"   # unique, not the shared SHARED_JUNK


def test_render_commands_dedupes_colliding_zones():
    # If two hosts end up with the same alias, their SIST zone names collide -> emit each zone ONCE.
    from alletra_onboard.domain.zoning import AliasedWwpn, FabricZonePlan, ZoningPlan

    h1 = AliasedWwpn(wwpn="AA", display="aa", role="host", fabric="F1", suggested_alias="H")
    h2 = AliasedWwpn(wwpn="BB", display="bb", role="host", fabric="F1", suggested_alias="H")  # same alias
    arr = AliasedWwpn(wwpn="CC", display="cc", role="array", fabric="F1", nsp="0:3:1", suggested_alias="A")
    plan = ZoningPlan(fabrics=[FabricZonePlan(
        fabric="F1", switch_host="s", active_cfg="F1_CFG",
        hosts=[h1, h2], array_ports=[arr], pairs=[("AA", "CC"), ("BB", "CC")],
    )])
    zones = [c for c in zp.render_commands(plan, {})[0]["F1"] if c.startswith("zonecreate")]
    assert len(zones) == 1   # both pairs collide on zone "H_A" -> deduped


# ---------------- real captures (tests/fixtures/vz_fabric, live VZ fabric 2026-08-14) ----------------

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "vz_fabric"


def _fixture(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8", errors="replace")


def test_real_nsshow_classifies_devices_and_extracts_identity():
    devices = zp.parse_nameserver(_fixture("F1_nsshow.txt"))
    assert len(devices) == 7  # 2 physical array ports + 2 NPIV shadows + 3 host HBAs

    # Host identity comes from the SWITCH — no vCenter needed (and vCenter names these by IP anyway).
    hosts = {d.host_name: d for d in devices.values() if d.is_physical_initiator}
    assert set(hosts) == {"DL360G11D24U25", "DL360G11D24U26", "DL360G11D24U27"}
    assert all(d.os == "VMware ESXi 8.0.3" for d in hosts.values())

    # Array ports self-describe serial + n:s:p in PortSymb.
    targets = [d for d in devices.values() if d.is_physical_target]
    assert {d.array_nsp for d in targets} == {"0:3:1", "1:3:1"}
    assert all(d.array_serial == "SGHD44LQLS" for d in targets)

    # THE TRAP: each FC-NVMe-capable array port registers twice; the NPIV shadow has its own WWPN
    # but points at the physical port via Permanent Port Name. Zoning must use physical ports only.
    npiv = [d for d in devices.values() if d.is_npiv]
    assert len(npiv) == 2
    assert {d.permanent_wwpn for d in npiv} == {d.wwpn for d in targets}
    assert all(not d.is_physical_target and not d.is_physical_initiator for d in npiv)


def test_real_nscamshow_scales_to_the_shared_fabric():
    # The fabric-wide remote view: hundreds of devices across 28 switches. The parser must classify
    # them without choking, and still surface host identity for the ones that advertise it.
    devices = zp.parse_nameserver(_fixture("F1_nscamshow.txt"))
    assert len(devices) > 250
    windows_host = devices.get("10000090FA376EEA")
    assert windows_host is not None and windows_host.host_name == "BL460CG82WB63"
    assert "Windows" in windows_host.os


def test_real_alishow_is_not_polluted_by_the_trailing_effective_section():
    # alishow dumps the ENTIRE zone DB. Before the section guard, every WWPN in the trailing
    # effective configuration was attributed to the LAST alias — winhost_fc_port_2 came back bound
    # to 888 WWPNs; the zone database binds it to exactly one.
    aliases = zp.parse_aliases(_fixture("F1_alishow.txt"))
    carriers = [w for w, names in aliases.items() if "winhost_fc_port_2" in names]
    assert carriers == ["1000441EA1529015"]

    # And the genuine bindings survive: the site's own convention aliases resolve exactly.
    assert "CRV_VZ_DL360G11D24U25_Port1" in aliases["10009440C9D01212"]
    assert "MPB10K_D24U21_VZ_031" in aliases["20310002AC02F584"]


def test_real_cfgactvshow_yields_the_active_cfg_per_fabric():
    assert zp.parse_active_cfg(_fixture("F1_cfgactvshow.txt")) == "F1_CFG"
    assert zp.parse_active_cfg(_fixture("F2_cfgactvshow.txt")) == "F2_CFG"


# ---------------- the two DELTA acceptance cases, both from the same real captures ----------------

class _RealBrocade:
    """FakeBrocade fed the REAL switch output for one fabric."""

    def __init__(self, label: str):
        self._label = label

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def nsshow(self):
        return _fixture(f"{self._label}_nsshow.txt")

    def nscamshow(self):
        return _fixture(f"{self._label}_nscamshow.txt")

    def alishow(self):
        return _fixture(f"{self._label}_alishow.txt")

    def cfgshow(self):
        return _fixture(f"{self._label}_cfgactvshow.txt")


def _real_factory(creds):
    return _RealBrocade("F1" if creds.host == "sw-f1" else "F2")


# VZ: the fully-zoned green bed. 3 hosts x 2 HBAs; array ports 0:3:1/1:3:1 (F1), 0:3:2/1:3:2 (F2).
_VZ_HOSTS = [
    HostHba(host_name="CRV_VZ_DL360G11D24U25", wwpn="10009440C9D01212"),
    HostHba(host_name="CRV_VZ_DL360G11D24U25", wwpn="10009440C9D01213"),
    HostHba(host_name="CRV_VZ_DL360G11D24U26", wwpn="10005CBA2CFC835A"),
    HostHba(host_name="CRV_VZ_DL360G11D24U26", wwpn="10005CBA2CFC835B"),
    HostHba(host_name="CRV_VZ_DL360G11D24U27", wwpn="10005CBA2CFC8366"),
    HostHba(host_name="CRV_VZ_DL360G11D24U27", wwpn="10005CBA2CFC8367"),
]
_VZ_PORTS = [
    ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC02F584", link_state="ready"),
    ArrayPort(node=0, slot=3, card_port=2, protocol="fc", wwpn="20320002AC02F584", link_state="ready"),
    ArrayPort(node=1, slot=3, card_port=1, protocol="fc", wwpn="21310002AC02F584", link_state="ready"),
    ArrayPort(node=1, slot=3, card_port=2, protocol="fc", wwpn="21320002AC02F584", link_state="ready"),
]


def test_delta_on_the_fully_zoned_vz_bed_creates_nothing():
    # THE safety-critical acceptance case: VZ is already correctly zoned (12 SIST zones live).
    # Every candidate pair must land in already_zoned and the command preview must be EMPTY —
    # a generator that re-proposes existing zones against a production config is worse than none.
    plan = zp.build_zoning_plan(
        _intent(), DiscoveryReport(host_hbas=_VZ_HOSTS, array_ports=_VZ_PORTS),
        brocade_factory=_real_factory,
    )
    for fabric in plan.fabrics:
        assert fabric.active_cfg == f"{fabric.fabric}_CFG"
        assert len(fabric.pairs) == 6                    # 3 host HBAs x 2 array ports per fabric
        assert sorted(fabric.already_zoned) == sorted(fabric.pairs)   # every pair already covered
    assert not plan.offline_hosts

    commands, _skipped = zp.render_commands(plan, {})
    assert commands == {"F1": [], "F2": []}              # nothing to create, nothing suggested


# BGL 4UW0004497: the SAME shared fabrics, but its 3 ESXi hosts are NOT yet zoned to it.
_BGL_HOSTS = [
    HostHba(host_name="10.55.235.120", wwpn="100070106F583FD1"),
    HostHba(host_name="10.55.235.120", wwpn="100070106F583FD9"),
    HostHba(host_name="10.55.235.121", wwpn="100070106F582F91"),
    HostHba(host_name="10.55.235.121", wwpn="100070106F582F99"),
    HostHba(host_name="10.55.235.122", wwpn="100070106F58EF21"),
    HostHba(host_name="10.55.235.122", wwpn="100070106F58EF29"),
]
_BGL_PORTS = [
    # Real showport: 0:3:1, 0:3:4, 1:3:1 sit on F1 (0:3:4 despite even parity), 0:3:2/1:3:2/1:3:4 on F2.
    ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC07EFDC", link_state="ready"),
    ArrayPort(node=0, slot=3, card_port=2, protocol="fc", wwpn="20320002AC07EFDC", link_state="ready"),
    ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC07EFDC", link_state="ready"),
    ArrayPort(node=1, slot=3, card_port=1, protocol="fc", wwpn="21310002AC07EFDC", link_state="ready"),
    ArrayPort(node=1, slot=3, card_port=2, protocol="fc", wwpn="21320002AC07EFDC", link_state="ready"),
    ArrayPort(node=1, slot=3, card_port=4, protocol="fc", wwpn="21340002AC07EFDC", link_state="ready"),
]


def test_switch_derived_hosts_when_vcenter_reports_none():
    # vCenter unreachable is ROUTINE on a vault network. The fallback is the DECLARED switches' own
    # (local) name servers — nsshow, never the fabric-wide nscamshow, which on a shared SAN would
    # drag in every other team's initiators. Names come from the NS HN: field (Emulex advertises it).
    plan = zp.build_zoning_plan(
        _intent(), DiscoveryReport(host_hbas=[], array_ports=_VZ_PORTS),
        brocade_factory=_real_factory,
    )
    for fabric in plan.fabrics:
        assert len(fabric.hosts) == 3
        assert {h.host_name for h in fabric.hosts} == {"DL360G11D24U25", "DL360G11D24U26", "DL360G11D24U27"}
        assert all(h.host_source == "switch" for h in fabric.hosts)
        # Same WWPNs as the zoned bed -> the delta still recognises everything as existing.
        assert sorted(fabric.already_zoned) == sorted(fabric.pairs)
    assert any("vCenter reported no hosts" in n for n in plan.notes)


def test_vcenter_hosts_win_when_present_and_carry_their_source():
    plan = zp.build_zoning_plan(
        _intent(), DiscoveryReport(host_hbas=_VZ_HOSTS, array_ports=_VZ_PORTS),
        brocade_factory=_real_factory,
    )
    for fabric in plan.fabrics:
        assert len(fabric.hosts) == 3                       # no switch-derived duplicates
        assert all(h.host_source == "vcenter" for h in fabric.hosts)
    assert not any("vCenter reported no hosts" in n for n in plan.notes)


def test_switch_derived_host_without_hn_falls_back_to_empty_name():
    # QLogic HBAs advertise no HN: in NodeSymb — the host still appears (the WWPN identifies it);
    # host_name stays "" and the UI shows the WWPN instead.
    ns = (
        f" N    010200;   3;{_ARR_031};2f:f7:00:02:ac:02:f6:29; 0x0\n"
        '    PortSymb: [10] "MPB10K - 0:3:1"\n'
        "    Device type: Physical Target\n"
        f" N    010300;   3;{_HOST_A};20:00:00:00:00:00:00:aa; 0x0\n"
        '    NodeSymb: [40] "QMH2572 FW:v8.08.207 DVR:v10.02.09.300-k"\n'
        "    Device type: Physical Initiator\n"
    )

    def factory(creds):
        return FakeBrocade(ns, "", _F1_CFG) if creds.host == "sw-f1" else FakeBrocade("", "", _F2_CFG)

    plan = zp.build_zoning_plan(
        _intent(), DiscoveryReport(host_hbas=[], array_ports=_discovery().array_ports),
        brocade_factory=factory,
    )
    f1 = next(f for f in plan.fabrics if f.fabric == "F1")
    host = next(h for h in f1.hosts if h.wwpn == "10000000000000AA")
    assert host.host_name == "" and host.host_source == "switch"


def test_render_commands_honours_the_operator_selection():
    # ADR 0004 refinement: candidates are a MENU. The operator picks which array ports serve each
    # host; only the selected NEW pairs are rendered, and a selection can never resurrect a pair
    # the effective config already covers.
    plan = zp.build_zoning_plan(
        _intent(), DiscoveryReport(host_hbas=_BGL_HOSTS, array_ports=_BGL_PORTS),
        brocade_factory=_real_factory,
    )
    names = {h.wwpn: f"H{i}" for i, h in enumerate(_BGL_HOSTS)}
    names |= {p.wwpn: f"A{i}" for i, p in enumerate(_BGL_PORTS)}

    chosen = [("100070106F583FD1", "20310002AC07EFDC"), ("100070106F583FD1", "21310002AC07EFDC")]
    f1 = zp.render_commands(plan, names, chosen)[0]["F1"]
    assert sum(1 for c in f1 if c.startswith("zonecreate")) == 2
    assert sum(1 for c in f1 if c.startswith("alicreate")) == 3     # 1 host + 2 array ports, no more

    assert zp.render_commands(plan, names, [])[0]["F1"] == []          # empty selection -> no commands


def test_selected_pair_without_an_alias_is_reported_not_silently_dropped():
    # LIVE UI finding (v0.14.0-rc.1): the operator ticked 0:3:4 — a port the fabric has NO alias
    # for — clicked Generate, and the preview simply did not change. The pair was skipped inside
    # render_commands with no trace. A tick that produces nothing must explain itself.
    plan = zp.build_zoning_plan(
        _intent(), DiscoveryReport(host_hbas=_BGL_HOSTS, array_ports=_BGL_PORTS),
        brocade_factory=_real_factory,
    )
    host_wwpn = "100070106F583FD1"
    chosen = [(host_wwpn, "20340002AC07EFDC")]      # 0:3:4 — no alias exists on the fabric
    commands, skipped = zp.render_commands(plan, {host_wwpn: "H1"}, chosen)
    assert commands["F1"] == []                     # nothing renderable — correct
    assert len(skipped["F1"]) == 1                  # ...but SAID, not swallowed
    assert "array port 0:3:4" in skipped["F1"][0]
    assert "alias" in skipped["F1"][0]

    # Naming the port resolves it: the same selection now renders fully and skips nothing.
    commands, skipped = zp.render_commands(
        plan, {host_wwpn: "H1", "20340002AC07EFDC": "T_AlletraMPF22U13_0_3_4"}, chosen,
    )
    assert any(c.startswith('zonecreate "H1_T_AlletraMPF22U13_0_3_4"') for c in commands["F1"])
    assert 'alicreate "T_AlletraMPF22U13_0_3_4","20:34:00:02:ac:07:ef:dc"' in commands["F1"]
    assert skipped["F1"] == []


def test_delta_on_the_unzoned_bgl_hosts_proposes_everything_as_new():
    # Same fixtures, opposite answer: the BGL ESXi hosts are online in these fabrics (nscamshow)
    # but zoned to nothing — every candidate pair is NEW, and the preview creates all of it.
    plan = zp.build_zoning_plan(
        _intent(), DiscoveryReport(host_hbas=_BGL_HOSTS, array_ports=_BGL_PORTS),
        brocade_factory=_real_factory,
    )
    f1 = next(f for f in plan.fabrics if f.fabric == "F1")
    f2 = next(f for f in plan.fabrics if f.fabric == "F2")
    bgl = {h.wwpn for h in _BGL_HOSTS}
    # One HBA per BGL host per fabric from vCenter, PLUS the three VZ initiators plugged into the
    # declared switches (local NS) — the union rule of 2026-09-12: a live initiator on the declared
    # switch is a zoning candidate whether or not vCenter knows it. They carry their source.
    assert len([h for h in f1.hosts if h.wwpn in bgl]) == 3 and len([h for h in f2.hosts if h.wwpn in bgl]) == 3
    assert len(f1.hosts) == 6 and len(f2.hosts) == 6
    assert all(h.host_source == "vcenter" for h in f1.hosts if h.wwpn in bgl)
    assert all(h.host_source == "switch" for h in f1.hosts if h.wwpn not in bgl)
    assert any("not known to vCenter" in n for n in plan.notes)
    # 0:3:4 lands on F1 by the NAME SERVER even though its parity says even — placement here is
    # by actual fabric presence, so the miscabled port cannot be planned into the wrong fabric.
    assert {p.wwpn for p in f1.array_ports} == {"20310002AC07EFDC", "20340002AC07EFDC", "21310002AC07EFDC"}
    bgl_pairs_f1 = [pair for pair in f1.pairs if pair[0] in bgl]
    bgl_pairs_f2 = [pair for pair in f2.pairs if pair[0] in bgl]
    assert len(bgl_pairs_f1) == 9 and len(bgl_pairs_f2) == 9     # 3 HBAs x 3 ports per fabric
    assert f1.already_zoned == [] and f2.already_zoned == []

    # With operator-chosen aliases and the BGL pairs selected, the preview creates every alias +
    # zone, saves, and enables once.
    names = {h.wwpn: f"H{i}" for i, h in enumerate(_BGL_HOSTS)}
    names |= {p.wwpn: f"A{i}" for i, p in enumerate(_BGL_PORTS)}
    f1_cmds = zp.render_commands(plan, names, bgl_pairs_f1 + bgl_pairs_f2)[0]["F1"]
    assert sum(1 for c in f1_cmds if c.startswith("zonecreate")) == 9
    assert sum(1 for c in f1_cmds if c.startswith("alicreate")) == 6   # 3 host + 3 array aliases
    assert f1_cmds[-2:] == ["cfgsave", "cfgenable F1_CFG"]


def test_a_non_host_type_port_is_flagged_not_excluded():
    # ADR 0004 (2026-07-04, re-proven live 2026-08-15): a port the array does not call host-serving
    # USUALLY carries replication, but a production Primera's RCFC ports carry host logins too — a
    # hard exclusion removes host-serving ports. So it stays a candidate, carries a caution, is never
    # pre-selected, and the notes call it out.
    #
    # The caution keys off the array's Type, never the Label. The Label is free text: on
    # AlletraMP_D22U27 three Type=host ports read "peer port", "peer 1:3:1" and "Peer_port", and the
    # old Label rule flagged all three while the array's genuine peer ports (IP) never reached here.
    rcfc = "20:34:00:02:ac:02:f6:29"   # 0:3:4
    ns_f1 = _F1_NS + f"\n N    010400;   3;{rcfc};2f:f7:00:02:ac:02:f6:29; 0x0\n    Device type: Physical Target\n"

    def factory(creds):
        return FakeBrocade(ns_f1, _F1_ALIS, _F1_CFG) if creds.host == "sw-f1" else FakeBrocade(_F2_NS, _F2_ALIS, _F2_CFG)

    disc = _discovery()
    disc.array_ports.append(
        ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC02F629",
                  link_state="ready", port_type="peer", usage="RCFC")
    )
    plan = zp.build_zoning_plan(_intent(), disc, brocade_factory=factory)
    f1 = next(f for f in plan.fabrics if f.fabric == "F1")
    flagged = next(p for p in f1.array_ports if p.wwpn == "20340002AC02F629")
    assert "peer" in flagged.caution                       # a candidate, but marked
    plain = next(p for p in f1.array_ports if p.wwpn == "20310002AC02F629")
    assert plain.caution == ""                             # ordinary target ports carry no caution
    assert (flagged.wwpn not in {w for pair in f1.already_zoned for w in pair})  # never pre-selected
    assert any("not excluded" in note for note in plan.notes)


def test_a_host_port_whose_operator_label_says_peer_is_never_flagged():
    """The live defect on AlletraMP_D22U27: Type=host ports labelled 'peer port' / 'Peer_port' were
    all flagged as replication, because the caution read the free-text Label instead of the Type."""
    def factory(creds):
        return FakeBrocade(_F1_NS, _F1_ALIS, _F1_CFG) if creds.host == "sw-f1" else FakeBrocade(_F2_NS, _F2_ALIS, _F2_CFG)

    disc = _discovery()
    for port in disc.array_ports:
        port.port_type, port.usage = "host", "peer port"
    plan = zp.build_zoning_plan(_intent(), disc, brocade_factory=factory)
    assert not any("not excluded" in note for note in plan.notes), plan.notes
    assert all(p.caution == "" for f in plan.fabrics for p in f.array_ports)


# ---------------- real captures (tests/fixtures/rack13_fabric, live training fabric 2026-09-12) --------
# rack13arcus (CZ2D2K014S), cross-cabled: F1 = SAN6700R13U38 (.111, cfg mycfg) carries 0:3:4 + 1:3:3;
# F2 = SAN6700R13U40 (.112, cfg jul2prabhu) carries 0:3:3 + 1:3:4. Both fabrics have a SECOND switch
# over an ISL. The Windows host .137 has one HBA zoned on F2 and one unzoned on F1; ESXi .86's live HBA
# is plugged into F2's REMOTE switch; two more initiators sit on the declared switches unzoned.

_R13 = Path(__file__).resolve().parents[1] / "fixtures" / "rack13_fabric"


class _Rack13Brocade:
    def __init__(self, label):
        self._label = label

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def _f(self, name):
        return (_R13 / f"{self._label}_{name}.txt").read_text(encoding="utf-8")

    def nsshow(self):
        return self._f("nsshow")

    def nscamshow(self):
        return self._f("nscamshow")

    def alishow(self):
        return self._f("cfgshow")     # F1 has no aliases at all; F2's live in the Defined section

    def cfgshow(self):
        return self._f("cfgshow")

    def fabricshow(self):
        return self._f("fabricshow")

    def read(self, command):
        assert command == "switchshow"
        return self._f("switchshow")


def _rack13_factory(creds):
    return _Rack13Brocade("F1" if creds.host == "sw-f1" else "F2")


_R13_VCENTER = [
    HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A8", os="VMware ESXi 8.0.2"),
    HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A9", os="VMware ESXi 8.0.2"),
    HostHba(host_name="10.132.30.47", wwpn="100008F1EAC03DE7"),
    HostHba(host_name="10.132.30.47", wwpn="100008F1EAC03DE8"),
    HostHba(host_name="10.132.30.86", wwpn="51402EC02089CC38"),
    HostHba(host_name="10.132.30.86", wwpn="51402EC02089CC3A"),
]
_R13_PORTS = [
    ArrayPort(node=0, slot=3, card_port=3, protocol="fc", wwpn="20330002AC02D495", link_state="ready"),
    ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC02D495", link_state="ready"),
    ArrayPort(node=1, slot=3, card_port=3, protocol="fc", wwpn="21330002AC02D495", link_state="ready"),
    ArrayPort(node=1, slot=3, card_port=4, protocol="fc", wwpn="21340002AC02D495", link_state="ready"),
]


def _rack13_discovery():
    from alletra_onboard.domain.discovery import ArrayHost
    return DiscoveryReport(
        host_hbas=_R13_VCENTER, array_ports=_R13_PORTS,
        array_hosts=[
            ArrayHost(name="vmenode", persona="Generic-ALUA", wwpns={"10005CED8C531294": ["0:3:3", "1:3:4"]}),
            ArrayHost(name="", wwpns={   # the unclaimed bucket, verbatim from showhost -d
                "10005CBA2CFF6BD0": ["0:3:3", "1:3:4"], "10005CED8C5312A8": ["0:3:3", "1:3:4"],
                "51402EC02089CC1C": ["0:3:3", "1:3:4"], "51402EC02089CBDA": ["0:3:3", "1:3:4"],
                "100000109B507E49": ["0:3:3", "1:3:4"], "10005CED8C5312A9": ["0:3:4", "1:3:3"],
            }),
        ],
        notes=["Port 0:3:4 attaches to switch SAN6700R13U38 (odd fabric) but its card-port parity is even — using the switch (non-standard cabling)."],
    )


def _rack13_intent():
    from alletra_onboard.domain.provisioning import DeclaredHost
    return _intent().model_copy(update={"declared_hosts": [
        DeclaredHost(name="arcus-win137", os="windows", address="10.132.30.137",
                     wwpns=["51402EC02089CC1C", "51402EC02089CC1E"]),
    ]})


def test_rack13_parsers_read_switch_and_fabric_identity():
    name, domain = zp.parse_switchshow((_R13 / "F1_switchshow.txt").read_text())
    assert (name, domain) == ("SAN6700R13U38", 1)
    fabric, switches = zp.parse_fabricshow((_R13 / "F2_fabricshow.txt").read_text())
    assert fabric == "Training_Lab_Rack11"
    assert switches == {2: "SAN6700R13U40", 32: "SAN1624ZR12U40"}
    domains = zp.parse_nscam_domains((_R13 / "F2_nscamshow.txt").read_text())
    assert domains["51402EC02089CC38"] == 32                 # .86's HBA is on the remote switch


def test_rack13_zoning_candidates_are_the_union_of_every_source():
    # THE 2026-09-12 finding: with vCenter answering, the plan showed only vCenter's ESXi HBAs and
    # could not zone the Windows host's unzoned HBA. Every live initiator is now a candidate.
    plan = zp.build_zoning_plan(_rack13_intent(), _rack13_discovery(), brocade_factory=_rack13_factory)
    f1 = next(f for f in plan.fabrics if f.fabric == "F1")
    f2 = next(f for f in plan.fabrics if f.fabric == "F2")

    # Fabric identity, for the screen header.
    assert (f1.switch_name, f1.fabric_name, f1.switch_count, f1.active_cfg) == ("SAN6700R13U38", "Training_Lab_Rack12", 2, "mycfg")
    assert (f2.switch_name, f2.fabric_name, f2.switch_count, f2.active_cfg) == ("SAN6700R13U40", "Training_Lab_Rack11", 2, "jul2prabhu")
    assert [p.nsp for p in f1.array_ports] == ["0:3:4", "1:3:3"] and [p.node for p in f1.array_ports] == [0, 1]
    assert [p.nsp for p in f2.array_ports] == ["0:3:3", "1:3:4"]

    f1_hosts = {h.wwpn: h for h in f1.hosts}
    f2_hosts = {h.wwpn: h for h in f2.hosts}
    # vCenter host, both fabrics, zoned by kiranzone1 on F1.
    assert f1_hosts["10005CED8C5312A9"].host_source == "vcenter"
    assert f1.zone_names["10005CED8C5312A9|20340002AC02D495"] == ["kiranzone1"]
    assert f1.zone_names["10005CED8C5312A9|21330002AC02D495"] == ["kiranzone1"]
    # The Windows host from the SHEET: cc:1c zoned on F2 (named zone), cc:1e on F1 with NOTHING.
    win_f1, win_f2 = f1_hosts["51402EC02089CC1E"], f2_hosts["51402EC02089CC1C"]
    assert (win_f1.host_name, win_f1.host_source, win_f1.os) == ("arcus-win137", "sheet", "windows")
    assert not any(pair[0] == "51402EC02089CC1E" for pair in f1.already_zoned)
    assert {pair for pair in f1.pairs if pair[0] == "51402EC02089CC1E"} == {
        ("51402EC02089CC1E", "20340002AC02D495"), ("51402EC02089CC1E", "21330002AC02D495"),
    }
    assert "arcus__windows137_zone2" in f2.zone_names["51402EC02089CC1C|20330002AC02D495"]
    assert win_f2.host_source == "sheet"
    # .86's live HBA: vCenter-named, placed on F2 via the REMOTE switch — and the screen says which.
    assert f2_hosts["51402EC02089CC38"].placed_on_switch == "SAN1624ZR12U40"
    assert f1_hosts["10005CED8C5312A9"].placed_on_switch == ""       # on the declared switch itself
    # The array's own host object, by its array name; unclaimed logins by WWPN only.
    assert (f2_hosts["10005CED8C531294"].host_name, f2_hosts["10005CED8C531294"].host_source) == ("vmenode", "array")
    assert (f2_hosts["51402EC02089CBDA"].host_name, f2_hosts["51402EC02089CBDA"].host_source) == ("", "array")
    # Initiators nothing but the declared switch sees: the training team's Linux box, one Emulex
    # HBA per fabric, unzoned on both — named by the NS HN: field, OS from OS:.
    assert (f1_hosts["10005CED8C5312A3"].host_source, f1_hosts["10005CED8C5312A3"].host_name,
            f1_hosts["10005CED8C5312A3"].os) == ("switch", "localhost.localdomain", "Linux")
    assert f2_hosts["10005CED8C5312A2"].host_name == "localhost.localdomain"
    # Offline: .47 both HBAs and .86's second HBA are in neither fabric.
    assert sorted(plan.offline_hosts) == sorted([
        "10.132.30.47 (10:00:08:f1:ea:c0:3d:e7)", "10.132.30.47 (10:00:08:f1:ea:c0:3d:e8)",
        "10.132.30.86 (51:40:2e:c0:20:89:cc:3a)",
    ])
    # The NPIV FC-NVMe shadows of the array ports never become hosts.
    assert not any(h.wwpn.startswith("20340102") or h.wwpn.startswith("20330102") for h in f1.hosts + f2.hosts)
    assert any("not known to vCenter" in n for n in plan.notes)
    assert any("non-standard cabling" in n for n in plan.notes)      # discovery's cabling note surfaces here


def test_rack13_proposed_aliases_follow_the_convention_only_where_none_exist():
    plan = zp.build_zoning_plan(_rack13_intent(), _rack13_discovery(), brocade_factory=_rack13_factory)
    f1 = next(f for f in plan.fabrics if f.fabric == "F1")
    win = next(h for h in f1.hosts if h.wwpn == "51402EC02089CC1E")
    assert win.existing_aliases == [] and win.suggested_alias == ""   # render fallback stays empty
    assert win.proposed_alias == "arcus_win137_hba2"                  # cc:1c is hba1, cc:1e hba2
    port = next(p for p in f1.array_ports if p.nsp == "0:3:4")
    assert port.proposed_alias == "CZ2D2K014S_N0S3P4"                 # serial from the NS PortSymb
    linux = next(h for h in f1.hosts if h.wwpn == "10005CED8C5312A3")
    assert linux.proposed_alias == "localhost_localdomain_hba2"       # 12:a2 (F2) is hba1, 12:a3 hba2
    unclaimed = next(h for f in plan.fabrics for h in f.hosts if h.wwpn == "51402EC02089CBDA")
    assert unclaimed.proposed_alias == "host_cbda_hba1"               # nameless login: WWPN tail
    # A proposal is UI pre-fill only: rendering with no operator names still reports, never invents.
    _cmds, skipped = zp.render_commands(plan, {}, [("51402EC02089CC1E", "20340002AC02D495")])
    assert len(skipped["F1"]) == 1 and "alias" in skipped["F1"][0]


def test_rack13_f1_command_set_for_the_windows_hba_is_the_consultants_script():
    plan = zp.build_zoning_plan(_rack13_intent(), _rack13_discovery(), brocade_factory=_rack13_factory)
    names = {"51402EC02089CC1E": "arcus_win137_hba2", "20340002AC02D495": "rack13arcus_N0S3P4",
             "21330002AC02D495": "rack13arcus_N1S3P3"}
    chosen = [("51402EC02089CC1E", "20340002AC02D495"), ("51402EC02089CC1E", "21330002AC02D495")]
    cmds, skipped = zp.render_commands(plan, names, chosen)
    assert cmds["F1"] == [
        'alicreate "arcus_win137_hba2","51:40:2e:c0:20:89:cc:1e"',
        'alicreate "rack13arcus_N0S3P4","20:34:00:02:ac:02:d4:95"',
        'alicreate "rack13arcus_N1S3P3","21:33:00:02:ac:02:d4:95"',
        'zonecreate "arcus_win137_hba2_rack13arcus_N0S3P4","arcus_win137_hba2;rack13arcus_N0S3P4"',
        'zonecreate "arcus_win137_hba2_rack13arcus_N1S3P3","arcus_win137_hba2;rack13arcus_N1S3P3"',
        'cfgadd "mycfg","arcus_win137_hba2_rack13arcus_N0S3P4;arcus_win137_hba2_rack13arcus_N1S3P3"',
        "cfgsave",
        "cfgenable mycfg",
    ]
    assert cmds["F2"] == [] and skipped == {"F1": [], "F2": []}     # nothing selected on F2


def test_render_rejects_names_fos_would_reject_and_warns_on_enhanced_ones():
    plan = zp.build_zoning_plan(_rack13_intent(), _rack13_discovery(), brocade_factory=_rack13_factory)
    chosen = [("51402EC02089CC1E", "20340002AC02D495")]
    # A dot is illegal in every FOS release: the pair is skipped and the reason names the character.
    cmds, skipped = zp.render_commands(
        plan, {"51402EC02089CC1E": "arcus.win137", "20340002AC02D495": "A034"}, chosen,
    )
    assert cmds["F1"] == [] and len(skipped["F1"]) == 1 and "'.'" in skipped["F1"][0]
    # A hyphen is legal on FOS 8.1+ only: it renders, and the warning says so.
    names = {"51402EC02089CC1E": "arcus_win137-hba2", "20340002AC02D495": "A034"}
    cmds, skipped = zp.render_commands(plan, names, chosen)
    assert skipped["F1"] == [] and any(c.startswith('alicreate "arcus_win137-hba2"') for c in cmds["F1"])
    warnings = zp.alias_name_warnings(plan, names)
    assert len(warnings["F1"]) == 1 and "8.1.0" in warnings["F1"][0]
    # 65 characters is rejected outright.
    assert "65 characters" in zp.fos_name_problem("a" * 65)
    assert zp.fos_name_problem("Zone_1") == "" and zp.fos_name_warning("Zone_1") == ""
