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


# ------------------------------------------------------------------ discovery

def test_discovery_assigns_host_fabric_from_nameserver():
    ns_odd = "\n".join([f"PortName: {w}" for w in (HOST_A, ARR_O1, ARR_O2)])
    ns_even = "\n".join([f"PortName: {w}" for w in (HOST_B, ARR_E1, ARR_E2)])
    hbas = [HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A)), HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_B))]

    report = disc.discover(
        _intent(),
        wsapi_factory=lambda c: FakeWsapi(ports=_ports()),
        vcenter_factory=lambda c: FakeVCenter(hbas),
        brocade_factory=lambda c: FakeBrocade(ns_odd if "odd" in c.host else ns_even, ""),
    )
    by_wwpn = {h.wwpn: h.fabric for h in report.host_hbas}
    assert by_wwpn[normalize_wwpn(HOST_A)] == "odd"
    assert by_wwpn[normalize_wwpn(HOST_B)] == "even"
    assert not report.notes  # all three sources succeeded


# ------------------------------------------------------------------ zoning report + remediation

def _discovered():
    return disc.DiscoveryReport(
        array_ports=_ports(),
        host_hbas=[
            HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_A), fabric="odd"),
            HostHba(host_name="esx1", wwpn=normalize_wwpn(HOST_B), fabric="even"),
        ],
    )


def test_zoning_report_marks_present_and_missing_and_remediates_with_cfgenable():
    report = zoning.build_report(
        _intent(),
        _discovered(),
        brocade_factory=lambda c: FakeBrocade("", CFGSHOW_ODD if "odd" in c.host else CFGSHOW_EVEN),
    )
    # odd fabric: HOST_A x {ARR_O1, ARR_O2}; the ARR_O1 pairing is present, ARR_O2 is missing.
    present = {(z.array_wwpn, z.present) for z in report.expected if z.fabric == "odd"}
    assert (normalize_wwpn(ARR_O1), True) in present
    assert (normalize_wwpn(ARR_O2), False) in present
    assert report.proper is False

    odd_rem = [r for r in report.remediations if r.fabric == "odd"][0]
    assert odd_rem.cfg_name == "PROD_F1"
    # additive + activated with cfgenable, never cfgsave-alone
    assert any(c.startswith("zonecreate ") for c in odd_rem.commands)
    assert odd_rem.commands[-1] == 'cfgenable "PROD_F1"'
    assert not any("cfgsave" in c for c in odd_rem.commands)


def test_apply_remediation_runs_commands_on_each_switch():
    report = zoning.build_report(
        _intent(),
        _discovered(),
        brocade_factory=lambda c: FakeBrocade("", CFGSHOW_ODD if "odd" in c.host else CFGSHOW_EVEN),
    )
    seen: dict[str, FakeBrocade] = {}

    def factory(creds):
        fake = FakeBrocade("", "")
        seen[creds.host] = fake
        return fake

    zoning.apply_remediation(_intent(), report.remediations, brocade_factory=factory)
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
