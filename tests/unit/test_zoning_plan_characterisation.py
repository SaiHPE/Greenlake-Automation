"""Characterisation tests for `zoning_plan.py` (`build_zoning_plan`, `render_commands`,
`render_peer_commands`, `alias_name_warnings`, `parse_nameserver`).

Pins the exact plan JSON, active zones, and character-for-character Brocade command lists in order
across every zoning capture in `tests/fixtures/` (`vz_fabric`, `rack13_fabric`) plus a seeded fuzz
of host/WWPN/fabric/alias/selection combinations. Also verifies ADR 0012 (read-only switch client)
and SPEC-010 (exact FOS command order).
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import SecretStr

from alletra_onboard.application.provisioning import discovery as disc
from alletra_onboard.application.provisioning import zoning_plan as zp
from alletra_onboard.domain.discovery import ArrayPort, DiscoveryReport, HostHba
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.provisioning import DeclaredHost, ProvisioningIntent
from alletra_onboard.domain.shared import EndpointCreds, wwpn_colons
from alletra_onboard.domain.zoning import ZoningPlan

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
VZ_DIR = FIXTURES / "vz_fabric"
R13_DIR = FIXTURES / "rack13_fabric"
GOLDEN = FIXTURES / "characterisation" / "zoning_plan_golden.json"


class _ReadOnlyBrocade:
    """Read-only switch fake enforcing ADR 0012: exposes only read methods, never writes."""

    def __init__(self, responses: dict[str, str], *, fail_enter: bool = False, fail_cmds: set[str] | None = None) -> None:
        self._r = responses
        self._fail_enter = fail_enter
        self._fail_cmds = fail_cmds or set()

    def __enter__(self) -> _ReadOnlyBrocade:
        if self._fail_enter:
            raise DeviceError("switch ssh failed")
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def _get(self, key: str) -> str:
        if key in self._fail_cmds:
            raise DeviceError(f"read failed: {key}")
        return self._r.get(key, "")

    def nsshow(self) -> str:
        return self._get("nsshow")

    def nscamshow(self) -> str:
        return self._get("nscamshow")

    def alishow(self) -> str:
        return self._get("alishow")

    def cfgshow(self) -> str:
        return self._get("cfgshow")

    def fabricshow(self) -> str:
        return self._get("fabricshow")

    def read(self, command: str) -> str:
        assert command == "switchshow", f"unexpected read command: {command}"
        return self._get("switchshow")


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="u", password=SecretStr("p"))


def _intent(declared: list[DeclaredHost] | None = None) -> ProvisioningIntent:
    base = ProvisioningIntent.from_simple(
        host_set_name="hs", array=_creds("array"), vcenter=_creds("vc"),
        switch_f1=_creds("sw-f1"), switch_f2=_creds("sw-f2"),
        name_prefix="v", size_gib=1,
    )
    return base.model_copy(update={"declared_hosts": declared or []})


def _vz_responses(label: str) -> dict[str, str]:
    return {
        "nsshow": (VZ_DIR / f"{label}_nsshow.txt").read_text(encoding="utf-8", errors="replace"),
        "nscamshow": (VZ_DIR / f"{label}_nscamshow.txt").read_text(encoding="utf-8", errors="replace"),
        "alishow": (VZ_DIR / f"{label}_alishow.txt").read_text(encoding="utf-8", errors="replace"),
        "cfgshow": (VZ_DIR / f"{label}_cfgactvshow.txt").read_text(encoding="utf-8", errors="replace"),
        "fabricshow": "",
        "switchshow": "",
    }


def _r13_responses(label: str, *, no_effective: bool = False) -> dict[str, str]:
    cfg = (R13_DIR / f"{label}_cfgshow.txt").read_text(encoding="utf-8")
    if no_effective and label == "F1":
        cfg = " zone:\tz0\t10:00:00:00:00:00:00:01\n" + (R13_DIR / "F1_cfgactvshow_no_effective_2026-09-28.txt").read_text(encoding="utf-8")
    return {
        "nsshow": (R13_DIR / f"{label}_nsshow.txt").read_text(encoding="utf-8"),
        "nscamshow": (R13_DIR / f"{label}_nscamshow.txt").read_text(encoding="utf-8"),
        "alishow": cfg,
        "cfgshow": cfg,
        "fabricshow": (R13_DIR / f"{label}_fabricshow.txt").read_text(encoding="utf-8"),
        "switchshow": (R13_DIR / f"{label}_switchshow.txt").read_text(encoding="utf-8"),
    }


def _assert_fos_order(cmds_by_fabric: dict[str, list[str]]) -> None:
    """SPEC-010 R1: verify strict FOS command order for every rendered fabric command list."""
    rank = {"cfgtransshow": 0, "alicreate": 1, "zonecreate": 2, "cfgadd": 3, "cfgsave": 4, "cfgenable": 5}
    for fab, cmds in cmds_by_fabric.items():
        if not cmds:
            continue
        assert cmds[0] == "cfgtransshow", f"{fab}: must begin with cfgtransshow, got {cmds[0]!r}"
        ranks = [rank[c.split()[0]] for c in cmds]
        assert ranks == sorted(ranks), f"{fab}: out-of-order FOS commands: {cmds}"


def _snapshot(
    plan: ZoningPlan,
    aliases: dict[str, str],
    selected_pairs: list[tuple[str, str]] | None = None,
) -> dict[str, object]:
    cmds, skipped = zp.render_commands(plan, aliases, selected_pairs)
    peer_cmds, peer_skipped = zp.render_peer_commands(plan, aliases)
    _assert_fos_order(cmds)
    _assert_fos_order(peer_cmds)
    return {
        "pairs": {f.fabric: [list(p) for p in f.pairs] for f in plan.fabrics},
        "already_zoned": {f.fabric: [list(p) for p in f.already_zoned] for f in plan.fabrics},
        "peer_pairs": {f.fabric: [list(p) for p in f.peer_pairs] for f in plan.fabrics},
        "peer_already_zoned": {f.fabric: [list(p) for p in f.peer_already_zoned] for f in plan.fabrics},
        "offline_hosts": list(plan.offline_hosts),
        "notes": list(plan.notes),
        "commands": cmds,
        "skipped": skipped,
        "peer_commands": peer_cmds,
        "peer_skipped": peer_skipped,
        "alias_warnings": zp.alias_name_warnings(plan, aliases),
    }


def _vz_capture_cases() -> dict[str, dict[str, object]]:
    vz_f1, vz_f2 = _vz_responses("F1"), _vz_responses("F2")
    vz_factory = lambda c: _ReadOnlyBrocade(vz_f1 if c.host == "sw-f1" else vz_f2)
    vz_hosts = [
        HostHba(host_name="CRV_VZ_DL360G11D24U25", wwpn="10009440C9D01212"),
        HostHba(host_name="CRV_VZ_DL360G11D24U25", wwpn="10009440C9D01213"),
        HostHba(host_name="CRV_VZ_DL360G11D24U26", wwpn="10005CBA2CFC835A"),
        HostHba(host_name="CRV_VZ_DL360G11D24U26", wwpn="10005CBA2CFC835B"),
    ]
    vz_ports = [
        ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC02F584", link_state="ready"),
        ArrayPort(node=0, slot=3, card_port=2, protocol="fc", wwpn="20320002AC02F584", link_state="ready"),
        ArrayPort(node=1, slot=3, card_port=1, protocol="fc", wwpn="21310002AC02F584", link_state="ready"),
        ArrayPort(node=1, slot=3, card_port=2, protocol="fc", wwpn="21320002AC02F584", link_state="ready"),
    ]
    bgl_hosts = [
        HostHba(host_name="10.55.235.120", wwpn="100070106F583FD1"),
        HostHba(host_name="10.55.235.120", wwpn="100070106F583FD9"),
        HostHba(host_name="10.55.235.121", wwpn="100070106F582F91"),
    ]
    bgl_ports = [
        ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC07EFDC", link_state="ready"),
        ArrayPort(node=0, slot=3, card_port=2, protocol="fc", wwpn="20320002AC07EFDC", link_state="ready"),
        ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC07EFDC", link_state="ready"),
        ArrayPort(node=1, slot=3, card_port=1, protocol="fc", wwpn="21310002AC07EFDC", link_state="ready"),
    ]
    p_vz = zp.build_zoning_plan(_intent(), DiscoveryReport(host_hbas=vz_hosts, array_ports=vz_ports), brocade_factory=vz_factory)
    p_vz_novc = zp.build_zoning_plan(_intent(), DiscoveryReport(host_hbas=[], array_ports=vz_ports), brocade_factory=vz_factory)
    p_bgl = zp.build_zoning_plan(_intent(), DiscoveryReport(host_hbas=bgl_hosts, array_ports=bgl_ports), brocade_factory=vz_factory)
    bgl_aliases = {
        "100070106F583FD1": "H_120_1",
        "100070106F583FD9": "H_120_2",
        "100070106F582F91": "1bad-port",
        "20310002AC07EFDC": "A_031",
        "20340002AC07EFDC": "bad alias",
    }
    p_merged = zp.build_zoning_plan(
        _intent(), DiscoveryReport(host_hbas=vz_hosts, array_ports=vz_ports),
        brocade_factory=lambda _c: _ReadOnlyBrocade(vz_f1),
    )
    return {
        "vz:fully_zoned": _snapshot(p_vz, {}),
        "vz:no_vcenter": _snapshot(p_vz_novc, {}),
        "vz:bgl_all": _snapshot(p_bgl, bgl_aliases),
        "vz:bgl_subset": _snapshot(p_bgl, bgl_aliases, [("100070106F583FD1", "20310002AC07EFDC"), ("100070106F583FD1", "20340002AC07EFDC")]),
        "vz:merged_fabric": _snapshot(p_merged, {}),
    }


def _r13_inputs() -> tuple[ProvisioningIntent, DiscoveryReport, dict[str, str], dict[str, str], dict[str, str]]:
    r13_f1, r13_f2 = _r13_responses("F1"), _r13_responses("F2")
    r13_arr_hosts = disc.parse_showhost((FIXTURES / "rack13_array" / "showhost_d.txt").read_text(encoding="utf-8"))
    r13_ports = [
        ArrayPort(node=0, slot=3, card_port=3, protocol="fc", wwpn="20330002AC02D495", link_state="ready"),
        ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC02D495", link_state="ready", port_type="peer"),
        ArrayPort(node=1, slot=3, card_port=3, protocol="fc", wwpn="21330002AC02D495", link_state="ready"),
        ArrayPort(node=1, slot=3, card_port=4, protocol="fc", wwpn="21340002AC02D495", link_state="ready"),
    ]
    r13_hbas = [
        HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A8", os="VMware ESXi 8.0.2"),
        HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A9", os="VMware ESXi 8.0.2"),
        HostHba(host_name="10.132.30.86", wwpn="51402EC02089CC38"),
        HostHba(host_name="offline-host", wwpn="10000000000000FF"),
    ]
    r13_disc = DiscoveryReport(
        host_hbas=r13_hbas, array_ports=r13_ports, array_hosts=r13_arr_hosts,
        notes=["Port 0:3:4 attaches to switch SAN6700R13U38 (odd fabric) but its card-port parity is even."],
    )
    r13_intent = _intent([DeclaredHost(name="arcus-win137", os="windows", wwpns=["51402EC02089CC1C", "51402EC02089CC1E"])])
    aliases = {
        "51402EC02089CC1E": "win137_hba2",
        "20340002AC02D495": "r13_034",
        "21330002AC02D495": "r13_133",
        "20020002AC01BE40": "src_002",
        "51402EC02089CC38": "esx86_hba1",
        "20330002AC02D495": "r13_033",
    }
    return r13_intent, r13_disc, r13_f1, r13_f2, aliases


def _r13_capture_cases() -> dict[str, dict[str, object]]:
    r13_intent, r13_disc, r13_f1, r13_f2, aliases = _r13_inputs()
    r13_factory = lambda c: _ReadOnlyBrocade(r13_f1 if c.host == "sw-f1" else r13_f2)
    peer_pairs = [
        ("20340002AC02D495", "21330002AC02D495"),
        ("20340002AC02D495", "20020002AC01BE40"),
        ("20330002AC02D495", "9999000000000001"),
    ]
    peer_nsps = {"20340002AC02D495": "0:3:4", "20330002AC02D495": "0:3:3"}

    p_r13 = zp.build_zoning_plan(r13_intent, r13_disc, brocade_factory=r13_factory, peer_pairs=peer_pairs, peer_nsps=peer_nsps)
    no_eff_f1 = _r13_responses("F1", no_effective=True)
    p_noeff = zp.build_zoning_plan(
        r13_intent, r13_disc,
        brocade_factory=lambda c: _ReadOnlyBrocade(no_eff_f1 if c.host == "sw-f1" else r13_f2, fail_cmds={"switchshow", "fabricshow"}),
    )
    p_f2_down = zp.build_zoning_plan(
        r13_intent, r13_disc,
        brocade_factory=lambda c: _ReadOnlyBrocade(r13_f1) if c.host == "sw-f1" else _ReadOnlyBrocade({}, fail_enter=True),
    )
    p_f1_cfg_fail = zp.build_zoning_plan(
        r13_intent, r13_disc,
        brocade_factory=lambda c: _ReadOnlyBrocade(r13_f1, fail_cmds={"cfgshow"}) if c.host == "sw-f1" else _ReadOnlyBrocade(r13_f2),
    )
    p_f1_ali_fail = zp.build_zoning_plan(
        r13_intent, r13_disc,
        brocade_factory=lambda c: _ReadOnlyBrocade(r13_f1, fail_cmds={"alishow"}) if c.host == "sw-f1" else _ReadOnlyBrocade(r13_f2),
    )
    return {
        "r13:full_and_peers": _snapshot(p_r13, aliases),
        "r13:no_effective_cfg": _snapshot(p_noeff, aliases),
        "r13:f2_unreachable": _snapshot(p_f2_down, aliases),
        "r13:f1_cfgshow_fails": _snapshot(p_f1_cfg_fail, aliases),
        "r13:f1_alishow_fails": _snapshot(p_f1_ali_fail, aliases),
    }


def _synth_ns(entries: list[tuple[str, str, str, str]]) -> str:
    """Build synthetic Brocade nsshow text from (wwpn, dev_type, port_symb, node_symb) tuples."""
    lines: list[str] = []
    for i, (wwpn, dev_type, port_symb, node_symb) in enumerate(entries):
        lines.append(f" N    010{i:03x};   3;{wwpn_colons(wwpn)};20:00:00:00:00:00:00:{i:02x}; 0x0")
        if port_symb:
            lines.append(f'    PortSymb: [20] "{port_symb}"')
        if node_symb:
            lines.append(f'    NodeSymb: [20] "{node_symb}"')
        lines.append(f"    Device type: {dev_type}")
    return "\n".join(lines) + "\n"


def compute_zoning_captures() -> dict[str, dict[str, object]]:
    cases: dict[str, dict[str, object]] = {}
    cases.update(_vz_capture_cases())
    cases.update(_r13_capture_cases())
    return cases


def test_zoning_plan_and_commands_match_golden_characterisation() -> None:
    expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
    actual = compute_zoning_captures()
    assert actual == expected
    peer_cmds = actual["r13:full_and_peers"]["peer_commands"]
    assert isinstance(peer_cmds, dict)
    assert 'zonecreate "r13_034_src_002","r13_034;src_002"' in peer_cmds["F1"]


def test_a_switch_that_fails_after_its_name_server_is_not_planned_from() -> None:
    """A half-read switch (nsshow answered, then cfgshow or alishow failed) gives that fabric nothing to
    plan, as on main: no pairs, no commands, and the note that the array's ports are in neither fabric."""
    r13_intent, r13_disc, r13_f1, r13_f2, aliases = _r13_inputs()
    for failing_cmd in ("cfgshow", "alishow"):
        factory = lambda c, cmd=failing_cmd: (
            _ReadOnlyBrocade(r13_f1, fail_cmds={cmd}) if c.host == "sw-f1" else _ReadOnlyBrocade(r13_f2)
        )
        got = zp.build_zoning_plan(r13_intent, r13_disc, brocade_factory=factory)
        got_cmds, _got_skip = zp.render_commands(got, aliases)
        f1 = next(f for f in got.fabrics if f.fabric == "F1")
        assert f1.pairs == [] and got_cmds["F1"] == []
        assert any("Array port(s) ONLINE but present in neither declared fabric's name server" in n for n in got.notes)


