"""Differential test for the shared N:S:P row filter (`nsp_rows` in domain/array_parse.py).

Runs `discover()` over every captured `showport` fixture set in `tests/fixtures/` plus a seeded
fuzz covering truncated lines, prose answers, dropped columns, empty WWPNs and malformed N:S:P
prefixes, comparing the refactored implementation against the pre-refactor row filters byte for byte.
"""

from __future__ import annotations

import random
from pathlib import Path

from pydantic import SecretStr

from alletra_onboard.application.provisioning import discovery as disc
from alletra_onboard.domain.array_parse import nsp_parts
from alletra_onboard.domain.discovery import ArrayPort, EthernetPort
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.shared import EndpointCreds, Fabric, normalize_wwpn

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

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
