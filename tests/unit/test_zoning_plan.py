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
    assert all(not f.pairs for f in plan.fabrics)                  # nothing zoned for an offline host


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
    # One HBA per host per fabric; the fabric membership comes from the real name server.
    assert len(f1.hosts) == 3 and len(f2.hosts) == 3
    # 0:3:4 lands on F1 by the NAME SERVER even though its parity says even — placement here is
    # by actual fabric presence, so the miscabled port cannot be planned into the wrong fabric.
    assert {p.wwpn for p in f1.array_ports} == {"20310002AC07EFDC", "20340002AC07EFDC", "21310002AC07EFDC"}
    assert len(f1.pairs) == 9 and len(f2.pairs) == 9     # 3 HBAs x 3 ports per fabric
    assert f1.already_zoned == [] and f2.already_zoned == []

    # With operator-chosen aliases, the preview creates every alias + zone and enables once.
    names = {h.wwpn: f"H{i}" for i, h in enumerate(_BGL_HOSTS)}
    names |= {p.wwpn: f"A{i}" for i, p in enumerate(_BGL_PORTS)}
    f1_cmds = zp.render_commands(plan, names)[0]["F1"]
    assert sum(1 for c in f1_cmds if c.startswith("zonecreate")) == 9
    assert sum(1 for c in f1_cmds if c.startswith("alicreate")) == 6   # 3 host + 3 array aliases
    assert f1_cmds[-1] == "cfgenable F1_CFG"


def test_rcfc_and_peer_ports_are_flagged_not_excluded():
    # ADR 0004 (2026-07-04, re-proven live 2026-08-15): RCFC/Peer labels USUALLY mean replication,
    # but a production Primera's RCFC-labelled target ports carry host logins (Type=host) — a hard
    # exclusion removes host-serving ports. So the port stays a candidate, carries a caution, is
    # never pre-selected, and the notes call it out.
    rcfc = "20:34:00:02:ac:02:f6:29"   # 0:3:4, showport Label "RCFC"
    ns_f1 = _F1_NS + f"\n N    010400;   3;{rcfc};2f:f7:00:02:ac:02:f6:29; 0x0\n    Device type: Physical Target\n"

    def factory(creds):
        return FakeBrocade(ns_f1, _F1_ALIS, _F1_CFG) if creds.host == "sw-f1" else FakeBrocade(_F2_NS, _F2_ALIS, _F2_CFG)

    disc = _discovery()
    disc.array_ports.append(
        ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC02F629", link_state="ready", usage="RCFC")
    )
    plan = zp.build_zoning_plan(_intent(), disc, brocade_factory=factory)
    f1 = next(f for f in plan.fabrics if f.fabric == "F1")
    flagged = next(p for p in f1.array_ports if p.wwpn == "20340002AC02F629")
    assert "RCFC" in flagged.caution                       # a candidate, but marked
    plain = next(p for p in f1.array_ports if p.wwpn == "20310002AC02F629")
    assert plain.caution == ""                             # ordinary target ports carry no caution
    assert (flagged.wwpn not in {w for pair in f1.already_zoned for w in pair})  # never pre-selected
    assert any("RCFC" in note and "not excluded" in note for note in plan.notes)
