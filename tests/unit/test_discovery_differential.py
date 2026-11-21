"""Differential test for the shared N:S:P row filter (`nsp_rows` in domain/array_parse.py).

Runs `discover()` over every captured `showport` fixture set in `tests/fixtures/` plus a seeded
fuzz covering truncated lines, prose answers, dropped columns, empty WWPNs and malformed N:S:P
prefixes, comparing the refactored implementation against the pre-refactor row filters byte for byte.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from pydantic import SecretStr

from alletra_onboard.application.provisioning import discovery as disc
from alletra_onboard.domain.array_parse import nsp_parts
from alletra_onboard.domain.discovery import (
    ArrayPort,
    DiscoveryReport,
    EthernetPort,
    HostHba,
    HostIdentity,
)
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.provisioning import (
    DeclaredHost,
    HostSetRequest,
    ProvisioningIntent,
)
from alletra_onboard.domain.shared import EndpointCreds, Fabric, normalize_wwpn

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
GOLDEN = FIXTURES / "characterisation" / "discovery_golden.json"

_COMMAND_FILES: dict[str, str] = {
    "showport": "showport.txt",
    "showport -iscsi": "showport_iscsi.txt",
    "showport -rcip": "showport_rcip.txt",
    "showport -file": "showport_file.txt",
    "showhost -d": "showhost_d.txt",
    "showversion": "showversion.txt",
    "showsys": "showsys.txt",
}


class _FakeCli:
    def __init__(self, responses: dict[str, str]) -> None:
        self._responses = responses

    def __enter__(self) -> _FakeCli:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def run(self, command: str, **_kwargs: object) -> str:
        return self._responses.get(command, "")


class _FakeVCenter:
    def __enter__(self) -> _FakeVCenter:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def host_fc_hbas(self) -> list[object]:
        return []

    def host_identities(self) -> list[object]:
        return []


class _FakeWsapiV3:
    def __enter__(self) -> _FakeWsapiV3:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def get(self, _path: str) -> dict[str, object]:
        return {"members": {}}


def _intent() -> ProvisioningIntent:
    creds = EndpointCreds(host="10.0.0.5", username="u", password=SecretStr("p"))
    return ProvisioningIntent.from_simple(
        host_set_name="Diff_Hostset",
        array=creds,
        vcenter=EndpointCreds(host="vc", username="u", password=SecretStr("p")),
        switch_f1=EndpointCreds(host="sw-odd", username="u", password=SecretStr("p")),
        switch_f2=EndpointCreds(host="sw-even", username="u", password=SecretStr("p")),
        name_prefix="Diff_Vol",
        size_gib=64,
        count=1,
        members=["esx1"],
    )


def _fixture_cases() -> list[tuple[str, dict[str, str]]]:
    cases: list[tuple[str, dict[str, str]]] = []
    for showport_path in sorted(FIXTURES.rglob("showport.txt")):
        folder = showport_path.parent
        responses = {
            cmd: (folder / fname).read_text(encoding="utf-8")
            for cmd, fname in _COMMAND_FILES.items()
            if (folder / fname).is_file()
        }
        cases.append((str(folder.relative_to(FIXTURES)), responses))
    return cases


_PROSE_LINES = [
    "",
    "   ",
    "There is no specified port information.",
    "no ports listed",
    "N:S:P Mode State Node_WWN/IP Port_WWN/HW_Addr Type Protocol Label",
    "----------------------------------------------------------------",
    "8 total",
    "Error: invalid option",
]

_PORT_PREFIXES = [
    "0:3:1", "0:4:1", "0:4:3", "1:4:2", "1:5:1",
    "0:4", "0:4:1:2", "1:foo", "-1:0:1", "abc:def", "123",
]


def _mutate_lines(rng: random.Random, lines: list[str]) -> str:
    out: list[str] = []
    for line in lines:
        mode = rng.randrange(6)
        if mode == 0:
            out.append(line)
        elif mode == 1:
            # Truncate mid-line
            cut = rng.randint(0, len(line))
            out.append(line[:cut])
        elif mode == 2:
            # Drop trailing columns
            toks = line.split()
            keep = rng.randint(0, len(toks))
            out.append(" ".join(toks[:keep]))
        elif mode == 3:
            # Swap first token to edge-case N:S:P-like or invalid prefix
            toks = line.split()
            if toks:
                toks[0] = rng.choice(_PORT_PREFIXES)
                out.append(" ".join(toks))
        elif mode == 4:
            # Replace WWPN / address / unset markers with empty/dash/double-dash
            toks = line.split()
            if len(toks) >= 5:
                toks[4] = rng.choice(["-", "--", "", "0000000000000000", "nothex"])
            out.append(" ".join(toks))
        else:
            out.append(rng.choice(_PROSE_LINES))
    if rng.random() < 0.35:
        out.insert(0, rng.choice(_PROSE_LINES))
    return "\n".join(out) + "\n"


def _fuzz_cases(fixtures: list[tuple[str, dict[str, str]]], *, count: int = 80) -> list[tuple[str, dict[str, str]]]:
    rng = random.Random(20261121)
    sample_pool = [resp for _, resp in fixtures]
    cases: list[tuple[str, dict[str, str]]] = []
    for idx in range(count):
        base = rng.choice(sample_pool)
        mutated: dict[str, str] = {}
        for cmd in ("showport", "showport -iscsi", "showport -rcip", "showport -file", "showhost -d"):
            text = base.get(cmd, "")
            lines = text.splitlines() if text else list(_PROSE_LINES)
            mutated[cmd] = _mutate_lines(rng, lines)
        # Keep prose-only / empty responses in the mix
        if idx % 10 == 0:
            mutated["showport"] = "\n".join(rng.sample(_PROSE_LINES, k=4))
            mutated["showport -iscsi"] = "There is no specified port information.\n"
            mutated["showport -rcip"] = ""
            mutated["showport -file"] = "no ports listed\n"
        cases.append((f"fuzz-{idx:03d}", mutated))
    return cases


def _ref_parse_iscsi_ips(showport_iscsi: str) -> dict[str, str]:
    ips: dict[str, str] = {}
    for line in (showport_iscsi or "").splitlines():
        p = line.split()
        if len(p) >= 3 and p[0][:1].isdigit() and ":" in p[0]:
            ips[p[0]] = "" if p[1] == "offline" else p[2]
    return ips


def _ref_parse_ports(showport: str, iscsi_ips: dict[str, str]) -> list[ArrayPort]:
    out: list[ArrayPort] = []
    for line in (showport or "").splitlines():
        p = line.split()
        if len(p) < 7 or not p[0][:1].isdigit() or ":" not in p[0] or p[1] != "target":
            continue
        protocol = p[6]
        if protocol not in ("FC", "iSCSI"):
            continue
        nsp = nsp_parts(p[0])
        if nsp is None:
            continue
        node, slot, card_port = nsp
        port_type = p[5]
        if protocol == "FC":
            fabric: Fabric = "odd" if card_port % 2 == 1 else "even"
            out.append(ArrayPort(
                node=node, slot=slot, card_port=card_port, protocol="fc",
                wwpn=normalize_wwpn(p[4]), link_state=p[2], fabric=fabric,
                mode=p[1], port_type=port_type,
                usage=" ".join(p[7:]) if len(p) > 7 else "",
            ))
        else:
            out.append(ArrayPort(
                node=node, slot=slot, card_port=card_port, protocol="iscsi",
                address=iscsi_ips.get(p[0], ""), link_state=p[2], fabric=None,
                mode=p[1], port_type=port_type,
                usage=" ".join(p[7:]) if len(p) > 7 else "",
            ))
    return out


def _ref_parse_replication_ports(showport: str) -> list[EthernetPort]:
    out: list[EthernetPort] = []
    for line in (showport or "").splitlines():
        p = line.split()
        if len(p) < 7 or not p[0][:1].isdigit() or ":" not in p[0]:
            continue
        mode, state, port_type, protocol = p[1], p[2], p[5], p[6]
        if mode != "peer" or protocol != "IP" or port_type == "cluster":
            continue
        nsp = nsp_parts(p[0])
        if nsp is None:
            continue
        node, slot, card_port = nsp
        address = p[3] if p[3] not in ("-", "") else ""
        out.append(EthernetPort(
            node=node, slot=slot, card_port=card_port, role=port_type,
            mode=mode, link_state=state, address=address,
        ))
    return out


def _ref_parse_rcip_detail(showport_rcip: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for line in (showport_rcip or "").splitlines():
        p = line.split()
        if len(p) < 8 or not p[0][:1].isdigit() or ":" not in p[0]:
            continue
        out[p[0]] = {
            "netmask": "" if p[4] in ("-", "") else p[4],
            "gateway": "" if p[5] in ("-", "") else p[5],
            "mtu": "" if p[6] in ("-", "") else p[6],
            "rate": "" if p[7] in ("-", "") else p[7],
            "duplex": ("" if p[8] in ("-", "") else p[8]) if len(p) > 8 else "",
            "autoneg": ("" if p[9] in ("-", "") else p[9]) if len(p) > 9 else "",
        }
    return out


def _ref_parse_file_ports(showport_file: str) -> list[EthernetPort]:
    out: list[EthernetPort] = []
    for line in (showport_file or "").splitlines():
        p = line.split()
        if len(p) < 12 or not p[0][:1].isdigit() or ":" not in p[0]:
            continue
        nsp = nsp_parts(p[0])
        if nsp is None:
            continue
        node, slot, card_port = nsp
        address, _, prefix = p[3].partition("/")
        out.append(EthernetPort(
            node=node, slot=slot, card_port=card_port, role="file",
            mode=p[1], link_state=p[2], address=address, prefix_len=prefix,
            ip_disabled=p[4].upper() == "Y", gateway="" if p[5] == "-" else p[5], vlan=p[6], mtu=p[7],
            rate="" if p[8] in ("-", "n/a") else p[8], eth=p[9], link=p[10],
            failover_ips=[ip for ip in p[11:] if ip != "-"],
        ))
    return out


def _run_discover(responses: dict[str, str]) -> str:
    report = disc.discover(
        _intent(),
        array_cli_factory=lambda _c: _FakeCli(responses),
        vcenter_factory=lambda _c: _FakeVCenter(),
        wsapi_v3_factory=lambda _c: _FakeWsapiV3(),
    )
    return report.model_dump_json()


def test_discover_nsp_rows_matches_pre_refactor_on_captures_and_fuzz(monkeypatch) -> None:
    fixtures = _fixture_cases()
    assert fixtures, "expected captured showport.txt fixtures under tests/fixtures/"
    all_cases = fixtures + _fuzz_cases(fixtures)

    actual: dict[str, str] = {name: _run_discover(resp) for name, resp in all_cases}

    monkeypatch.setattr(disc, "parse_iscsi_ips", _ref_parse_iscsi_ips)
    monkeypatch.setattr(disc, "parse_ports", _ref_parse_ports)
    monkeypatch.setattr(disc, "parse_replication_ports", _ref_parse_replication_ports)
    monkeypatch.setattr(disc, "parse_rcip_detail", _ref_parse_rcip_detail)
    monkeypatch.setattr(disc, "parse_file_ports", _ref_parse_file_ports)

    for name, resp in all_cases:
        expected = _run_discover(resp)
        assert actual[name] == expected, f"discover() output differed for case {name}"


# ---------------- golden characterisation for discover / assemble_hosts / resolve_port_fabrics ----------------


class _RichCli(_FakeCli):
    def __init__(self, responses: dict[str, str], errors: set[str] | None = None, *, fail_enter: bool = False) -> None:
        super().__init__(responses)
        self._errors = errors or set()
        self._fail_enter = fail_enter

    def __enter__(self) -> _RichCli:
        if self._fail_enter:
            raise DeviceError("array ssh down")
        return self

    def run(self, command: str, **_kwargs: object) -> str:
        if command in self._errors:
            raise DeviceError(f"failed: {command}")
        return self._responses.get(command, "")


class _RichVCenter:
    def __init__(self, hbas: list[HostHba], idents: list[HostIdentity], *, fail_enter: bool = False, fail_ident: bool = False) -> None:
        self._hbas = hbas
        self._idents = idents
        self._fail_enter = fail_enter
        self._fail_ident = fail_ident

    def __enter__(self) -> _RichVCenter:
        if self._fail_enter:
            raise DeviceError("vcenter timeout")
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def host_fc_hbas(self) -> list[HostHba]:
        return list(self._hbas)

    def host_identities(self) -> list[HostIdentity]:
        if self._fail_ident:
            raise DeviceError("ident read failed")
        return list(self._idents)


class _FakeLinuxClient:
    def __init__(self, replies: dict[str, str], *, fail: bool = False) -> None:
        self._replies = replies
        self._fail = fail

    def __enter__(self) -> _FakeLinuxClient:
        if self._fail:
            raise DeviceError("ssh refused")
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def run(self, key: str) -> tuple[int, str]:
        return (0, self._replies[key]) if key in self._replies else (1, "")

    def read(self, key: str) -> str:
        return self._replies.get(key, "")


class _FakeWindowsClient:
    def __init__(self, replies: dict[str, str], *, fail: bool = False) -> None:
        self._replies = replies
        self._fail = fail

    def __enter__(self) -> _FakeWindowsClient:
        if self._fail:
            raise DeviceError("winrm refused")
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def read(self, key: str) -> str:
        return self._replies.get(key, "")


def _rich_intent(declared: list[DeclaredHost] | None = None, members: list[str] | None = None) -> ProvisioningIntent:
    base = _intent()
    host_sets = [HostSetRequest(name="Char_HS", members=members if members is not None else ["esx1"])]
    return base.model_copy(update={"declared_hosts": declared or [], "host_sets": host_sets})


def _fcfabric_reply(switch_name: str, wwpns: list[str]) -> str:
    lines = [f"Logical Name: {switch_name}"]
    for w in wwpns:
        lines.append(f"  F-Port attached {w}")
    return "\n".join(lines) + "\n"


def _host_pin(h) -> dict[str, object]:
    return {
        "name": h.name,
        "os": h.os,
        "sources": list(h.sources),
        "wwpns": list(h.wwpns),
        "iqns": list(h.iqns),
        "fabrics": list(h.fabrics),
        "logged_in": h.logged_in,
        "identified": h.identified,
        "in_run": h.in_run,
        "lookup": h.lookup,
        "host_read": h.host_read,
    }


def _discover_pin(report: DiscoveryReport, progress: list[str]) -> dict[str, object]:
    return {
        "hosts": [_host_pin(h) for h in report.hosts],
        "notes": list(report.notes),
        "error": report.error,
        "progress": progress,
    }


def _discover_scenarios() -> dict[str, dict[str, object]]:
    """Run discover() over all captured showport sets plus multi-source/error scenarios."""
    results: dict[str, dict[str, object]] = {}
    fixtures = _fixture_cases()
    for name, resp in fixtures:
        progress_lines: list[str] = []
        report = disc.discover(
            _intent(),
            array_cli_factory=lambda _c, r=resp: _RichCli(r),
            vcenter_factory=lambda _c: _RichVCenter([], []),
            wsapi_v3_factory=lambda _c: _FakeWsapiV3(),
            progress=progress_lines.append,
        )
        results[f"fixture:{name}"] = _discover_pin(report, progress_lines)

    # Rich scenario using rack13 iscsi_vlan capture + vCenter + declared hosts + host reads + fcfabric
    r13 = dict(next(r for n, r in fixtures if n.endswith("iscsi_vlan/rack13")))
    r13["showhost -d"] = (FIXTURES / "rack13_array" / "showhost_d.txt").read_text(encoding="utf-8")
    r13["showportdev fcfabric 0:3:3"] = _fcfabric_reply("SW_B", ["20330002AC02D495", "21340002AC02D495"])
    r13["showportdev fcfabric 0:3:4"] = _fcfabric_reply("SW_A", ["20340002AC02D495", "21330002AC02D495"])
    declared = [
        DeclaredHost(name="win-box", os="windows", address="10.10.0.20", username="admin", password=SecretStr("pw")),
        DeclaredHost(name="lnx-box", os="linux", address="10.10.0.21", username="root", password=SecretStr("pw"),
                     wwpns=["51402EC02089CC1C"]),
        DeclaredHost(name="esx-sheet", os="esxi", address="10.10.0.22", username="root", password=SecretStr("pw")),
        DeclaredHost(name="ghost-host", os="linux", address="10.10.0.99"),
    ]
    hbas = [
        HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A8", os="VMware ESXi 8.0.2"),
        HostHba(host_name="10.132.30.136", wwpn="10005CED8C5312A9", os="VMware ESXi 8.0.2"),
        HostHba(host_name="10.132.30.47", wwpn="100008F1EAC03DE7", os="VMware ESXi 8.0.2"),
    ]
    idents = [
        HostIdentity(host_name="10.132.30.136", serial_number="SN136", iqns=["iqn.1998-01.com.vmware:esx136"]),
        HostIdentity(host_name="iscsi-only-esx", serial_number="SNISCSI", iqns=["iqn.1998-01.com.vmware:esxiscsi"], os="ESXi 8"),
        HostIdentity(host_name="empty-esx", serial_number="SNEMPTY", iqns=[]),
    ]
    lin_replies = {
        "hostname": "lnx-box.lab",
        "os": 'PRETTY_NAME="RHEL 8.9"\n',
        "serial": "LNXSN1",
        "fc": "0x51402ec02089cc1c\n",
        "iqn": "InitiatorName=iqn.1994-05.com.redhat:lnxbox\n",
        "multipath": "",
    }
    win_replies = {
        "hostname": '"WIN-BOX"',
        "os": '{"Caption":"Windows Server 2022"}',
        "serial": '{"SerialNumber":"WINSN1"}',
        "initiators": '[{"NodeAddress":"iqn.1991-05.com.microsoft:win-box"}]',
        "mpio": '{"installed":true,"claimed":true,"disks":[]}',
    }
    prog_rich: list[str] = []
    rep_rich = disc.discover(
        _rich_intent(declared, members=["10.132.30.136", "vmenode"]),
        array_cli_factory=lambda _c: _RichCli(r13),
        vcenter_factory=lambda _c: _RichVCenter(hbas, idents),
        linux_host_factory=lambda _c: _FakeLinuxClient(lin_replies),
        windows_host_factory=lambda _c: _FakeWindowsClient(win_replies),
        wsapi_v3_factory=lambda _c: _FakeWsapiV3(),
        progress=prog_rich.append,
    )
    results["rich:rack13_multi_source"] = _discover_pin(rep_rich, prog_rich)

    # Error-branch scenarios: array SSH down; rcip/file/vcenter-ident/linux/windows errors; vcenter down
    err_cases = [
        ("err:array_down", _RichCli({}, fail_enter=True), _RichVCenter(hbas[:1], []), _rich_intent()),
        ("err:sub_reads_fail", _RichCli(r13, errors={"showport -rcip", "showport -file"}),
         _RichVCenter(hbas, [], fail_ident=True), _rich_intent(declared[:2])),
        ("err:vcenter_down", _RichCli(r13), _RichVCenter([], [], fail_enter=True), _rich_intent(declared)),
    ]
    for label, cli, vc, intent in err_cases:
        p_lines: list[str] = []
        rep = disc.discover(
            intent,
            array_cli_factory=lambda _c, c=cli: c,
            vcenter_factory=lambda _c, v=vc: v,
            linux_host_factory=lambda _c: _FakeLinuxClient({}, fail=True),
            windows_host_factory=lambda _c: _FakeWindowsClient({}, fail=True),
            wsapi_v3_factory=lambda _c: _FakeWsapiV3(),
            progress=p_lines.append,
        )
        results[label] = _discover_pin(rep, p_lines)
    return results


def _assemble_capture_cases() -> dict[str, list[dict[str, object]]]:
    """Captured showhost_d.txt files assembled into DiscoveredHost pins."""
    out: dict[str, list[dict[str, object]]] = {}
    for path in sorted(FIXTURES.rglob("showhost_d.txt")):
        key = "capture:" + str(path.relative_to(FIXTURES))
        array_hosts = disc.parse_showhost(path.read_text(encoding="utf-8"))
        rep = DiscoveryReport(
            array_ports=[
                ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC02F584", link_state="ready", fabric="odd"),
                ArrayPort(node=0, slot=3, card_port=3, protocol="fc", wwpn="20330002AC02D495", link_state="ready", fabric="even"),
                ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC02D495", link_state="ready", fabric="odd"),
                ArrayPort(node=1, slot=3, card_port=3, protocol="fc", wwpn="21330002AC02D495", link_state="ready", fabric="odd"),
                ArrayPort(node=1, slot=3, card_port=4, protocol="fc", wwpn="21340002AC02D495", link_state="ready", fabric="even"),
            ],
            array_hosts=array_hosts,
        )
        out[key] = [_host_pin(h) for h in disc.assemble_hosts(rep)]
    return out


def _resolve_fabrics_cases() -> dict[str, dict[str, object]]:
    topologies = {
        "zero_switches": {},
        "one_switch_same_parity": {"0:3:1": "SW1", "1:3:1": "SW1"},
        "one_switch_mixed_parity": {"0:3:1": "SW1", "0:3:2": "SW1"},
        "two_standard": {"0:3:1": "SW1", "1:3:1": "SW1", "0:3:2": "SW2", "1:3:2": "SW2"},
        "two_cross_cabled": {"0:3:1": "SW1", "0:3:4": "SW1", "1:3:1": "SW1", "0:3:2": "SW2", "1:3:2": "SW2"},
        "two_same_parity": {"0:3:1": "SW_A", "1:3:1": "SW_B"},
        "two_with_loss_sync": {"0:3:1": "SW1", "0:3:2": "SW2"},
        "three_switches": {"0:3:1": "SW1", "0:3:2": "SW2", "1:3:1": "SW3"},
    }
    out: dict[str, dict[str, object]] = {}
    for name, sw_map in topologies.items():
        fc_ports = [
            ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="2031", link_state="ready"),
            ArrayPort(node=0, slot=3, card_port=2, protocol="fc", wwpn="2032", link_state="ready"),
            ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="2034", link_state="ready"),
            ArrayPort(node=1, slot=3, card_port=1, protocol="fc", wwpn="2131", link_state="ready"),
            ArrayPort(node=1, slot=3, card_port=2, protocol="fc", wwpn="2132", link_state="loss_sync"),
        ]
        notes = disc.resolve_port_fabrics(fc_ports, sw_map)
        out[name] = {
            "ports": [[p.label, p.fabric, p.fabric_switch] for p in fc_ports],
            "notes": notes,
        }
    return out


def compute_discovery_captures() -> dict[str, object]:
    return {
        "discover": _discover_scenarios(),
        "assemble_hosts": _assemble_capture_cases(),
        "resolve_port_fabrics": _resolve_fabrics_cases(),
    }


def test_discovery_matches_golden_characterisation() -> None:
    expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
    actual = compute_discovery_captures()
    assert actual == expected
