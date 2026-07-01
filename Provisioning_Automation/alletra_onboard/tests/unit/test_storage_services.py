"""Unit tests for the storage services with fake adapters — validate the orchestration and the
cfgshow parser without a live array / vCenter / switches."""

from __future__ import annotations

from pydantic import SecretStr

from alletra_onboard.application.storage import discovery as disc
from alletra_onboard.application.storage import storage_provision as prov
from alletra_onboard.application.storage import zoning
from alletra_onboard.domain.storage import (
    ArrayPort,
    EndpointCreds,
    HostHba,
    NameserverEntry,
    ProvisioningIntent,
    VolumeSpec,
    normalize_wwpn,
)

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
        volume=VolumeSpec(name_prefix="CRV_Prod", size_gib=1024, count=2),
    )
    data.update(over)
    return ProvisioningIntent(**data)


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

    def run(self, cmd: str) -> str:
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
    def __init__(self, *, ports=(), hosts=(), host_sets=(), volumes=(), vsets=(), cpgs=("SSD_r6",)):
        self._ports = list(ports)
        self.hosts, self.host_sets = set(hosts), set(host_sets)
        self.volumes, self.vsets, self.cpgs = set(volumes), set(vsets), set(cpgs)
        self.calls: list[tuple] = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def array_fc_ports(self):
        return self._ports

    def cpg_names(self):
        return list(self.cpgs)

    def host_names(self):
        return list(self.hosts)

    def host_set_names(self):
        return list(self.host_sets)

    def volume_names(self):
        return list(self.volumes)

    def volume_set_names(self):
        return list(self.vsets)

    def ensure_host(self, name, wwns):
        self.calls.append(("host", name, tuple(wwns)))
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

    def ensure_vlun(self, vol, host):
        self.calls.append(("vlun", vol, host))
        return "created"


# ------------------------------------------------------------------ cfgshow parser

def test_parse_active_zones_resolves_aliases_and_effective():
    zones, cfg = zoning.parse_active_zones(CFGSHOW_ODD)
    assert cfg == "PROD_F1"
    assert zones["Z1"] == {normalize_wwpn(HOST_A), normalize_wwpn(ARR_O1)}


# ------------------------------------------------------------------ discovery (array-side)
# WWPNs: esx1 fully zoned (A odd, B even); esx2 odd-only (C odd, D never seen); esx3 not seen at all.
_A, _B = "10000000000000A1", "10000000000000B1"
_C, _D = "10000000000000C1", "10000000000000D1"
_E, _F = "10000000000000E1", "10000000000000E2"

_SHOWPORT_A = """N:S:P   Mode     State --Node_WWN/IP--- -Port_WWN/HW_Addr-    Type Protocol Label
0:3:1 target     ready 2FF70002AC02F629   20310002AC02F629    host       FC     -
0:3:2 target     ready 2FF70002AC02F629   20320002AC02F629    host       FC     -
1:3:1 target     ready 2FF70002AC02F629   21310002AC02F629    host       FC     -
1:3:2 target     ready 2FF70002AC02F629   21320002AC02F629    host       FC     -
0:4:1 target   offline          0.0.0.0       40A6B7E032E0    free    iSCSI     -"""


def _ns(arr_wwpn: str, hosts: list[tuple[str, str]]) -> str:
    """Render a showportdev ns block: a self-row (skipped) + one row per (host_name, port_wwpn)."""
    rows = ["    PtId LpID Hadr Node_WWN Port_WWN ftrs svpm bbct flen vp_WWN SNN Name",
            f"0x330200 0x00 0x00 2FF70002AC02F629 {arr_wwpn} 0x8800 0x0012 n/a 0x0800 {arr_wwpn} HPE Alletra port"]
    for name, port in hosts:
        rows.append(f"0x331000 0x08 0x00 2000{port[4:]} {port} 0x0000 0x0000 0x0000 0x0000 {arr_wwpn} Emulex {name}")
    return "\n".join(rows)


_ARRAY_BLOCKS = {
    "showport": _SHOWPORT_A,
    "showportdev ns 0:3:1": _ns("20310002AC02F629", [("esx1", _A), ("esx2", _C)]),
    "showportdev ns 1:3:1": _ns("21310002AC02F629", [("esx1", _A), ("esx2", _C)]),
    "showportdev ns 0:3:2": _ns("20320002AC02F629", [("esx1", _B)]),
    "showportdev ns 1:3:2": _ns("21320002AC02F629", [("esx1", _B)]),
}


def test_discovery_reads_array_and_assigns_fabric_no_switch():
    # esx1's two HBAs (A, B) come from vCenter; the array's showportdev ns puts A on odd, B on even.
    hbas = [HostHba(host_name="esx1", wwpn=_A), HostHba(host_name="esx1", wwpn=_B)]
    report = disc.discover(
        _intent(),
        array_cli_factory=lambda c: FakeArrayCli(_ARRAY_BLOCKS),
        vcenter_factory=lambda c: FakeVCenter(hbas),
    )
    assert len(report.array_ports) == 4                       # 4 ready FC target ports; iSCSI skipped
    by_wwpn = {h.wwpn: h.fabric for h in report.host_hbas}
    assert by_wwpn[_A] == "odd" and by_wwpn[_B] == "even"     # fabric assigned from the ARRAY ns
    assert any(e.host_name == "esx1" and e.fabric == "odd" and e.array_port == "0:3:1"
               for e in report.nameserver)
    assert not report.notes  # both sources succeeded, every HBA placed on a fabric


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
    """A DiscoveryReport shaped like the array-side discover() output: 4 target ports + the per-port
    ns logins. esx1 is logged in on both fabrics (A odd, B even); esx2 only on odd (C)."""
    ports = [
        ArrayPort(node=0, slot=3, card_port=1, wwpn="20310002AC02F629", link_state="ready", fabric="odd"),
        ArrayPort(node=1, slot=3, card_port=1, wwpn="21310002AC02F629", link_state="ready", fabric="odd"),
        ArrayPort(node=0, slot=3, card_port=2, wwpn="20320002AC02F629", link_state="ready", fabric="even"),
        ArrayPort(node=1, slot=3, card_port=2, wwpn="21320002AC02F629", link_state="ready", fabric="even"),
    ]
    ns = []
    for nsp, arr in (("0:3:1", "20310002AC02F629"), ("1:3:1", "21310002AC02F629")):
        ns.append(NameserverEntry(fabric="odd", array_port=nsp, array_wwpn=arr, host_wwpn=_A, host_name="esx1"))
        ns.append(NameserverEntry(fabric="odd", array_port=nsp, array_wwpn=arr, host_wwpn=_C, host_name="esx2"))
    for nsp, arr in (("0:3:2", "20320002AC02F629"), ("1:3:2", "21320002AC02F629")):
        ns.append(NameserverEntry(fabric="even", array_port=nsp, array_wwpn=arr, host_wwpn=_B, host_name="esx1"))
    return disc.DiscoveryReport(array_ports=ports, nameserver=ns, host_hbas=hbas)


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


def test_apply_remediation_runs_commands_on_each_switch():
    from alletra_onboard.domain.storage import ZoneRemediation

    rem = [ZoneRemediation(fabric="odd", switch_host="sw-odd", cfg_name="PROD_F1",
                           commands=['zonecreate "z","aa;bb"', 'cfgadd "PROD_F1","z"', 'cfgenable "PROD_F1"'])]
    seen: dict[str, FakeBrocade] = {}

    def factory(creds):
        fake = FakeBrocade("", "")
        seen[creds.host] = fake
        return fake

    zoning.apply_remediation(_intent(), rem, brocade_factory=factory)
    assert any(cmd.startswith("cfgenable") for cmd in seen["sw-odd"].applied)


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
    # volumes are exported to the host SET (set:<name>), not per-host
    assert ("vlun", "CRV_Prod01", "set:CRVLZ_Hostset") in fake.calls
    assert result.error is None
