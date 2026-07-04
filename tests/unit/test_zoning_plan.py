"""Zoning PLAN (ADR 0004 revised) — the read-only, assisted command builder. No switch writes:
build the per-fabric SIST plan from read-only switch data, keep every alias, render the preview."""

from __future__ import annotations

from alletra_onboard.application.storage import zoning_plan as zp
from alletra_onboard.domain.storage import (
    ArrayPort, DiscoveryReport, EndpointCreds, HostHba, ProvisioningIntent, VolumeSpec,
)

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
    return ProvisioningIntent(
        host_set_name="hs", array=_creds("array"), vcenter=_creds("vc"),
        switch_f1=_creds("sw-f1"), switch_f2=_creds("sw-f2"),
        volume=VolumeSpec(name_prefix="v", size_gib=1),
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
    f1 = zp.render_commands(plan, {})["F1"]
    assert not any(c.startswith("alicreate") for c in f1)          # both aliases already exist
    assert 'zonecreate "hostx_HBA1_Port1_CRVLZ_MPB10K_LZ_031","hostx_HBA1_Port1;CRVLZ_MPB10K_LZ_031"' in f1
    assert 'cfgadd "F1_CFG","hostx_HBA1_Port1_CRVLZ_MPB10K_LZ_031"' in f1
    assert "cfgenable F1_CFG" in f1


def test_render_commands_alicreate_for_a_new_operator_alias():
    plan = zp.build_zoning_plan(_intent(), _discovery(), brocade_factory=_factory)
    cmds = zp.render_commands(plan, {"10000000000000AA": "CRVLZ_HOSTX_R1U1_HBA_1_Port_1"})
    assert 'alicreate "CRVLZ_HOSTX_R1U1_HBA_1_Port_1","10:00:00:00:00:00:00:aa"' in cmds["F1"]


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
    from alletra_onboard.domain.storage import AliasedWwpn, FabricZonePlan, ZoningPlan

    h1 = AliasedWwpn(wwpn="AA", display="aa", role="host", fabric="F1", suggested_alias="H")
    h2 = AliasedWwpn(wwpn="BB", display="bb", role="host", fabric="F1", suggested_alias="H")  # same alias
    arr = AliasedWwpn(wwpn="CC", display="cc", role="array", fabric="F1", nsp="0:3:1", suggested_alias="A")
    plan = ZoningPlan(fabrics=[FabricZonePlan(
        fabric="F1", switch_host="s", active_cfg="F1_CFG",
        hosts=[h1, h2], array_ports=[arr], pairs=[("AA", "CC"), ("BB", "CC")],
    )])
    zones = [c for c in zp.render_commands(plan, {})["F1"] if c.startswith("zonecreate")]
    assert len(zones) == 1   # both pairs collide on zone "H_A" -> deduped
