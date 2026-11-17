"""SPEC-031 part A — Remote Copy over Fibre Channel on a partnership that already exists.

The read (R1) and the partnership by WWN (R3, R4) are pinned to captures: rack13-ARCUS's `showport` of
2026-11-03 (`rcip_pair/before/alletra/`) and 2026-11-16 (`peer_ports/rack13/`), E18U31's with two peer
ports (`peer_ports/E18U31/`, 2026-11-17), and the Primera's failed FC target for rack13-ARCUS
(`rcip_pair/before/primera/`, 2026-11-03). No lab pair replicates over FC today (research 2026-11-17 §4),
so a working FC pair exists here only as model objects built on those captures.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alletra_onboard.application.replication.plan import build_plan, check, find_partnership
from alletra_onboard.application.replication.read import parse_showport_roles
from alletra_onboard.domain.replication import (
    PortRole,
    ProtectionRequest,
    RcGroup,
    RcipPort,
    RcLink,
    RcTarget,
    ReplicationArrayView,
    ReplicationIntent,
)
from tests.unit import test_replication_partnership as rcip_pair
from tests.unit import test_replication_plan as rc_pair

FIX = Path(__file__).resolve().parents[1] / "fixtures"


def _ports(path: str) -> ReplicationArrayView:
    roles, first = parse_showport_roles((FIX / path).read_text(encoding="utf-8"))
    return ReplicationArrayView(ports=roles, fc_node_wwn=first)


# ------------------------------------------------------------------ R1: the read

def test_rack13_keeps_each_fc_ports_wwn_beside_its_node_wwn_on_both_captures():
    for path in ("rcip_pair/before/alletra/showport.txt", "peer_ports/rack13/showport.txt"):
        view = _ports(path)
        assert (view.ports["0:3:3"].node_wwn, view.ports["0:3:3"].port_wwn) == ("2FF70002AC02D495", "20330002AC02D495")
        assert view.ports["1:3:4"].port_wwn == "21340002AC02D495"
        assert view.fc_node_wwns == {"2FF70002AC02D495"}
        assert len(view.fc_port_wwns) == 8
        # an iSCSI or IP row's hardware address is not a WWN
        assert view.ports["0:4:1"].port_wwn == "" and view.ports["0:4:3"].port_wwn == ""


def test_e18u31_keeps_every_fc_node_wwn_its_peer_ports_own_one_too():
    view = _ports("peer_ports/E18U31/showport.txt")
    assert view.fc_node_wwns == {"2FF70002AC02DEF2", "2FF70202AC02DEF2"}
    assert view.ports["0:3:2"].port_wwn == "20320202AC02DEF2" and view.ports["0:3:2"].type == "peer"
    assert view.fc_node_wwn == "2FF70002AC02DEF2"        # SPEC-021 still reads the first FC row's


# ------------------------------------------------------------------ R3/R4: the partnership by WWN

PRIMERA_FC = "rack13-ARCUS_PRIMERA"
# The Primera's two RCFC-labelled ports (showport, 2026-11-03), the ones its old target's links went out on.
PRIMERA_RCFC = {"0:3:2": "20320002AC02AC38", "1:3:2": "21320002AC02AC38"}


def _lab_pair(a_over=None, b_over=None):
    """rack13-ARCUS (A) and the Primera 630 (B) as they were on 2026-11-03, before the RCIP setup."""
    return rcip_pair._views(a_over, b_over)


def _intent(**kw) -> ReplicationIntent:
    return ReplicationIntent(peer=rcip_pair._creds(rcip_pair.B_HOST), failover_test=False,
                             protections=[ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", mode="sync", rpo_minutes=None)],
                             **kw)


def test_the_primeras_fc_target_resolves_to_rack13_by_node_wwn_and_link_wwns():
    rack13, primera = _lab_pair()
    report = check(rack13, primera, _intent())
    assert report.partnership is None and not report.mixed_transports
    assert report.findings[:2] == [
        ("No Remote Copy partnership between rack13-ARCUS and PRIMERA630R11U22: no two targets point at each other, "
        "by RCIP address or by Fibre Channel WWN. Fix the Fibre Channel partnership on the arrays (what each target "
        "shows is below), then read both arrays again."),
        ("PRIMERA630R11U22 has target 'rack13-ARCUS_PRIMERA' for rack13-ARCUS over Fibre Channel, found by node WWN and "
        "port WWN (Fibre Channel, status failed, 0 of 2 links Up); rack13-ARCUS has no Fibre Channel target that "
        "points back at PRIMERA630R11U22."),
    ]
    # R4: the Replication network tab sets up RCIP only; an FC pair is not sent there
    assert not any("Replication network tab" in f or "over IP only" in f for f in report.findings)


def _rack13_target_back(*targets: tuple[str, dict[str, str]]):
    """rack13-ARCUS holding FC targets for the Primera (none exists in any capture): each (name, {local
    port: Primera port WWN}). rack13's free ports 0:3:3 and 1:3:4 are the ones the Primera's links address."""
    rows = "".join(f"{name} {i} FC ready 2FF70002AC02AC38 mirror_config\n" for i, (name, _) in enumerate(targets, 1))
    links = "".join(f"{name} {nsp} {wwn} Down -\n" for name, ports in targets for nsp, wwn in ports.items())
    return {"showrcopy": ("Remote Copy System Information\nStatus: Started, Normal\n\nTarget Information\n\n"
                          f"Name ID Type Status Options Policy\n{rows}\nLink Information\n\n"
                          f"Target Node Address Status Options\n{links}\nGroup Information\n\n")}


def test_with_a_target_back_the_pair_is_an_fc_partnership_paired_by_the_ports_in_use_not_by_order():
    decoy = ("old_primera", {"0:3:3": "20330002AC02AC38", "1:3:4": "21330002AC02AC38"})    # Primera host ports
    back = ("PRIMERA630R11U22", {"0:3:3": PRIMERA_RCFC["0:3:2"], "1:3:4": PRIMERA_RCFC["1:3:2"]})
    rack13, primera = _lab_pair(a_over=_rack13_target_back(decoy, back))
    p = find_partnership(primera, rack13)
    assert p is not None and p.transport == "FC"
    assert (p.target_on_primary, p.target_on_peer) == (PRIMERA_FC, "PRIMERA630R11U22")
    assert (p.links_primary_up, p.links_primary_total) == (0, 2)
    assert [(t.name, t.peer_name, t.transport) for t in p.targets] == [(PRIMERA_FC, "PRIMERA630R11U22", "FC")]
    report = check(primera, rack13, _intent())
    assert report.partnership is not None and report.partnership.transport == "FC"
    assert ("The partnership needs at least 2 links Up each way: PRIMERA630R11U22 → rack13-ARCUS via target "
            "'rack13-ARCUS_PRIMERA' has 0 of 2 Up, rack13-ARCUS → PRIMERA630R11U22 via 'PRIMERA630R11U22' has 0 of 2 "
            "Up.") in report.findings


def test_the_rcip_pairs_still_match_by_address_and_say_ip():
    a, b = rc_pair._views()
    p = find_partnership(a, b)
    assert p is not None and p.transport == "IP" and {t.transport for t in p.targets} == {"IP"}
    plan = build_plan(check(a, b, rc_pair._intent()), rc_pair._intent(), rc_pair._prov())
    assert any(n.startswith("Partnership over RCIP: AlletraMP_D22U27 → AlletraMP_E18U31 via target 'AlletraMP_E18U31'")
               for n in plan.notes)


def test_a_target_whose_node_wwn_matches_but_a_link_wwn_does_not_is_named_with_that_wwn():
    text = (FIX / "rcip_pair" / "before" / "primera" / "showrcopy.txt").read_text(encoding="utf-8")
    stray = text.replace("rack13-ARCUS_PRIMERA 1:3:2 21340002AC02D495", "rack13-ARCUS_PRIMERA 1:3:2 21340002AC02D499")
    rack13, primera = _lab_pair(b_over={"showrcopy": stray})
    report = check(rack13, primera, _intent())
    assert ("PRIMERA630R11U22 has Fibre Channel target 'rack13-ARCUS_PRIMERA' that does not resolve to rack13-ARCUS: "
            "link 1:3:2 → 21340002AC02D499 addresses no port of rack13-ARCUS.") in report.findings
    assert not any("Replication network tab" in f for f in report.findings)


# Two arrays with RCIP ports and FC ports. No capture of a working FC pair exists: the model objects keep
# the shape of the captured rows (`showport` mode, Type and WWN columns; `showrcopy` targets and links).
A_NODE, B_NODE = "2FF70002AC0000A1", "2FF70002AC0000B2"
A_FC = {"0:3:3": "20330002AC0000A1", "1:3:3": "21330002AC0000A1"}
B_FC = {"0:3:3": "20330002AC0000B2", "1:3:3": "21330002AC0000B2"}


def _fc_ports(node: str, wwns: dict[str, str]) -> dict[str, PortRole]:
    return {nsp: PortRole(nsp=nsp, mode="initiator", state="ready", type="rcfc", protocol="FC", node_wwn=node, port_wwn=wwn)
            for nsp, wwn in wwns.items()}


def _target(view_links: list, name: str, *, fc: bool, to: dict[str, str], status="ready", up="Up", node="") -> RcTarget:
    view_links.extend(RcLink(target=name, nsp=nsp, address=addr, status=up) for nsp, addr in to.items())
    return RcTarget(name=name, type="FC" if fc else "IP", status=status, options=node if fc else "", policy="mirror_config")


def _mixed_pair(*, fc_status="ready", fc_up="Up", fc_group="Started"):
    """arrayA and arrayB partnered over IP, and arrayB also holding an FC target for arrayA."""
    a_links: list = []
    b_links: list = []
    a = ReplicationArrayView(
        host="a", name="arrayA", rc_status="Started", ports=_fc_ports(A_NODE, A_FC),
        rcip_ports=[RcipPort(nsp="0:4:4", ip="10.0.0.1"), RcipPort(nsp="1:4:4", ip="10.0.0.2")],
        targets=[_target(a_links, "arrayB", fc=False, to={"0:4:4": "10.0.0.11", "1:4:4": "10.0.0.12"})],
        links=a_links, vvsets={"zz_rc_vvs": ["v1"]}, cpg_free_mib={"SSD_r6": 10 ** 7})
    b = ReplicationArrayView(
        host="b", name="arrayB", rc_status="Started", ports=_fc_ports(B_NODE, B_FC),
        rcip_ports=[RcipPort(nsp="0:4:4", ip="10.0.0.11"), RcipPort(nsp="1:4:4", ip="10.0.0.12")],
        targets=[_target(b_links, "arrayA", fc=False, to={"0:4:4": "10.0.0.1", "1:4:4": "10.0.0.2"}),
                 _target(b_links, "arrayA_fc", fc=True, node=A_NODE, status=fc_status, up=fc_up,
                         to={"0:3:3": A_FC["0:3:3"], "1:3:3": A_FC["1:3:3"]})],
        links=b_links, groups=[RcGroup(name="db_rcg", target="arrayA_fc", status=fc_group)] if fc_group else [],
        cpg_free_mib={"SSD_r6": 10 ** 7})
    return a, b


def test_an_ip_and_an_fc_target_between_the_same_two_arrays_block_and_plan_nothing():
    a, b = _mixed_pair()
    intent = _intent()
    report = check(a, b, intent)
    assert report.mixed_transports and report.partnership is None and find_partnership(a, b) is None
    assert report.findings == [
        ("arrayA and arrayB show Remote Copy targets towards each other over IP and over Fibre Channel: arrayA target "
        "'arrayB' (IP, status ready, 2 of 2 links Up); arrayB target 'arrayA' (IP, status ready, 2 of 2 links Up); "
        "arrayB target 'arrayA_fc' (Fibre Channel, status ready, 2 of 2 links Up, started group db_rcg). The arrays "
        "keep one partnership per pair, and a target in one transport stops one in the other from working, so the "
        "tool will not use either and plans nothing. None of them is failed, so the tool offers no removal: agree "
        "with the array owners which transport stays.")
    ]
    plan = build_plan(report, intent, rc_pair._prov())
    assert plan.actions == [] and plan.blockers == report.findings
    # with the Replication network tab too, the step sets nothing up beside them
    intent = _intent(network=rcip_pair.NETWORK)
    plan = build_plan(check(a, b, intent), intent, rc_pair._prov())
    assert plan.actions == [] and len(plan.blockers) == 1


def test_only_a_failed_target_with_no_link_up_and_no_started_group_is_offered_for_removal():
    a, b = _mixed_pair(fc_status="failed", fc_up="Down", fc_group="Stopped")
    [finding] = check(a, b, _intent()).findings
    assert finding.endswith(
        "Remove the failed one first: on arrayB, `removercopytarget -cleargroups -f arrayA_fc` (this also removes the "
        "groups on that target; their volumes stay). Save `showrcopy -d groups` before.")
    assert finding.count("removercopytarget") == 1


# ------------------------------------------------------------------ R6: latency over Fibre Channel

def _working_fc_pair(*, a_host="a", b_host="b") -> tuple[ReplicationArrayView, ReplicationArrayView]:
    """SiteA and SiteB replicating over Fibre Channel: one FC target each way, 2 links Up each, Remote Copy
    started, no RCIP port configured. Volume set HS (V01) on SiteA to protect."""
    a_links: list = []
    b_links: list = []
    a = ReplicationArrayView(
        host=a_host, name="SiteA", serial="SA", system_id=100, os_version="10.5.60", rc_status="Started",
        rc_health="Normal", ports=_fc_ports(A_NODE, A_FC),
        targets=[_target(a_links, "SiteB", fc=True, node=B_NODE, to={"0:3:3": B_FC["0:3:3"], "1:3:3": B_FC["1:3:3"]})],
        links=a_links, cpg_free_mib={"SSD_r6": 10 ** 7}, vvsets={"HS": ["V01"]}, volume_size_mib={"V01": 10240},
    )
    b = ReplicationArrayView(
        host=b_host, name="SiteB", serial="SB", system_id=200, os_version="10.5.60", rc_status="Started",
        rc_health="Normal", ports=_fc_ports(B_NODE, B_FC),
        targets=[_target(b_links, "SiteA", fc=True, node=A_NODE, to={"0:3:3": A_FC["0:3:3"], "1:3:3": A_FC["1:3:3"]})],
        links=b_links, cpg_free_mib={"SSD_r6": 10 ** 7},
    )
    return a, b


async def _fc_run(tmp_path, monkeypatch, *, rtt_ms, mode="async"):
    """A REPLICATE run on the working FC pair, read and planned; (service, run id, the plan's id)."""
    from pydantic import SecretStr

    from alletra_onboard.application.replication import apply as replication_apply
    from alletra_onboard.application.replication import read as replication_read
    from alletra_onboard.domain.models import RunMode
    from alletra_onboard.domain.replication import ReplicationOutcome, ReplicationResult
    from alletra_onboard.domain.shared import EndpointCreds
    from tests.unit.test_onboarding_service import _item, _prov_intent, _service

    a, b = _working_fc_pair()
    monkeypatch.setattr(replication_read, "read_array", lambda creds, progress=None: a if creds.host == "a" else b)
    monkeypatch.setattr(replication_apply, "apply_plan", lambda plan, provisioning, *, progress=None, **kw: ReplicationResult(
        outcomes=[ReplicationOutcome(kind="group", name="HS_rcg", status="created")], groups_created=["HS_rcg"]))
    intent = _prov_intent()
    intent.volumes[0].vvset = "HS"
    intent.replication = ReplicationIntent(
        peer=EndpointCreds(host="b", username="u", password=SecretStr("p")), failover_test=False, rtt_ms=rtt_ms,
        protections=[ProtectionRequest(vvset="HS", peer_cpg="SSD_r6", mode=mode, rpo_minutes=10 if mode == "async" else None)],
    )
    service = _service(tmp_path)
    run = service.create_run(_item(), mode=RunMode.REPLICATE, provisioning_intent=intent)
    service.start_replication_preview(run.run_id)
    await service.wait(run.run_id)
    plan = service.replication.previewed_plan(run.run_id)
    assert plan.blockers == [] and any(x.state == "create" for x in plan.actions)
    return service, run.run_id, plan.plan_id


def _applied_notes(service, run_id) -> list[str]:
    return next(e for e in service.list_events(run_id) if e.event_type == "replication.applied").data["result"]["notes"]


async def test_an_fc_pair_with_a_blank_rtt_is_refused_with_the_sentence_and_offers_no_link_check(tmp_path, monkeypatch):
    from alletra_onboard.application.service import StepPreconditionError

    service, run_id, plan_id = await _fc_run(tmp_path, monkeypatch, rtt_ms=None)
    report = service.replication.current_report(run_id)
    assert report.partnership.transport == "FC" and report.rtt_ms is None and report.modes == ["async"]
    with pytest.raises(StepPreconditionError) as refused:
        service.start_replication_apply(run_id, approved_plan=plan_id, accept_latency=True)
    assert str(refused.value) == ("Type the round-trip time between the arrays on the Replication tab: the tool "
                                  "cannot measure Fibre Channel links yet.")
    with pytest.raises(StepPreconditionError, match="the arrays replicate over Fibre Channel. Type the round-trip time"):
        service.start_link_check(run_id, duration_s=600)


@pytest.mark.parametrize("mode", ["async", "sync"])
async def test_an_fc_pair_over_10_ms_is_refused_and_accepted_with_continue_anyway(tmp_path, monkeypatch, mode):
    from alletra_onboard.application.service import StepPreconditionError

    service, run_id, plan_id = await _fc_run(tmp_path, monkeypatch, rtt_ms=11, mode=mode)
    with pytest.raises(StepPreconditionError) as refused:
        service.start_replication_apply(run_id, approved_plan=plan_id)
    assert str(refused.value) == (f"The round-trip time typed on the Replication tab is 11 ms; {mode} replication over "
                                  "Fibre Channel needs 10 ms or less. Tick 'Continue anyway' to configure it regardless.")
    service.start_replication_apply(run_id, approved_plan=plan_id, accept_latency=True)
    await service.wait(run_id)
    assert _applied_notes(service, run_id) == [
        ("Round-trip time 11 ms, typed on the Replication tab by the engineer, not measured (the tool cannot measure "
        f"Fibre Channel links yet); over the 10 ms limit for {mode} over Fibre Channel — the operator accepted it and "
        "chose to continue.")]


async def test_an_fc_pair_at_10_ms_passes_and_says_the_value_was_typed(tmp_path, monkeypatch):
    service, run_id, plan_id = await _fc_run(tmp_path, monkeypatch, rtt_ms=10)
    service.start_replication_apply(run_id, approved_plan=plan_id)
    await service.wait(run_id)
    assert _applied_notes(service, run_id) == [
        ("Round-trip time 10 ms, typed on the Replication tab by the engineer, not measured (the tool cannot measure "
        "Fibre Channel links yet); within the limit.")]


def test_an_async_rtt_rcip_allows_is_not_a_finding_over_fc_and_the_link_check_skips_fc_links():
    """Over RCIP 50 ms async is within 200 ms; over Fibre Channel it is over 10 ms, and the apply holds it to that
    (above). The RCIP finding is unchanged; an FC pair gets no RCIP sentence."""
    from alletra_onboard.application.replication.link_check import FC_ONLY, plan_pairs

    a, b = _working_fc_pair()
    intent = _intent(rtt_ms=50)
    intent.protections = [ProtectionRequest(vvset="HS", peer_cpg="SSD_r6", mode="async")]
    report = check(a, b, intent)
    assert report.findings == [] and report.rtt_ms == 50 and report.modes == ["async"]
    # every FC link is skipped with the one sentence, whatever RCIP ports the array has
    a.rcip_ports = [RcipPort(nsp="0:4:4", ip="10.0.0.1")]
    assert plan_pairs(check(a, b, intent)) == ([], [FC_ONLY])


# ------------------------------------------------------------------ R8: groups, apply and verify over FC

# The lab pair D22U27 <-> E18U31 (rc_pair/, 2026-10-07) carried over Fibre Channel instead of RCIP: each
# side's target is Type FC with the other's node WWN, and its two links leave from a free FC port and address
# the other's FC port WWN (D22U27 0:3:2 <-> E18U31 0:3:3, D22U27 1:3:3 <-> E18U31 1:3:3; WWNs from showport).
# No RCIP port is configured. Everything else in the captures is as the arrays printed it.
_OVER_FC = {
    "D22U27": ({"0:4:3": "0:3:2", "1:4:3": "1:3:3"}, {"0:3:2": "20330002AC02DEF2", "1:3:3": "21330002AC02DEF2"}, "2FF70002AC02DEF2"),
    "E18U31": ({"0:4:3": "0:3:3", "1:4:3": "1:3:3"}, {"0:3:3": "20320002AC02DEF6", "1:3:3": "21330002AC02DEF6"}, "2FF70002AC02DEF6"),
}
_NO_RCIP = {"showport -rcip": "There is no specified port information\n",
            "showrctransport -rcip": "There is no specified port information\n"}


def _over_fc(array: str, capture: str = "") -> dict[str, str]:
    ports, peer_wwn, peer_node = _OVER_FC[array]
    out = []
    for line in (FIX / "rc_pair" / capture / array / "showrcopy.txt").read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) == 6 and p[0] == "AlletraMP_E18U31" and p[2] == "IP":
            line = f"{p[0]} {p[1]} FC {p[3]} {peer_node} {p[5]}"
        elif len(p) >= 4 and p[0] in ("AlletraMP_E18U31", "receive") and p[1] in ports:
            line = f"{p[0]} {ports[p[1]]} {peer_wwn[ports[p[1]]]} {' '.join(p[3:])}"
        out.append(line)
    return {"showrcopy": "\n".join(out) + "\n", **_NO_RCIP}


def test_groups_plan_apply_and_verify_over_fibre_channel_make_the_same_calls_as_over_rcip():
    from alletra_onboard.application.replication.apply import apply_plan
    from alletra_onboard.application.replication.read import read_array
    from alletra_onboard.application.replication.verify import verify
    from tests.unit import test_replication_apply as rc_apply

    prov = rc_apply._prov()
    ip_a, ip_b = rc_apply._views()
    fc_a, fc_b = rc_apply._views(a_overrides=_over_fc("D22U27"), b_overrides=_over_fc("E18U31"))
    assert fc_a.rcip_ports == [] and fc_b.rcip_ports == [] and {t.type for t in fc_a.targets + fc_b.targets} == {"FC"}
    fc_report = check(fc_a, fc_b, prov.replication)
    assert fc_report.findings == [] and fc_report.partnership.transport == "FC"
    assert (fc_report.partnership.links_primary_up, fc_report.partnership.links_peer_up) == (2, 2)

    ip_plan = build_plan(check(ip_a, ip_b, prov.replication), prov.replication, prov)
    fc_plan = build_plan(fc_report, prov.replication, prov)
    assert fc_plan.blockers == []
    calls = [[(c.seq, c.where, c.wsapi, c.cli) for x in plan.actions for c in x.calls] for plan in (ip_plan, fc_plan)]
    assert calls[0] and calls[1] == calls[0]          # the groups address the target by name, whatever its transport
    assert any(n.startswith("Partnership over Fibre Channel: AlletraMP_D22U27 → AlletraMP_E18U31 via target "
                            "'AlletraMP_E18U31' (2/2 links Up)") for n in fc_plan.notes)

    ip_log: list = []
    fc_log: list = []
    ip_result = apply_plan(ip_plan, prov, wsapi_factory=rc_apply._factory(ip_log))
    fc_result = apply_plan(fc_plan, prov, wsapi_factory=rc_apply._factory(fc_log))
    assert fc_result.error is None and fc_log == ip_log
    assert (fc_result.removals_a, fc_result.removals_b) == (ip_result.removals_a, ip_result.removals_b)

    # verify reads the arrays back: the live capture minutes after the first apply (after_apply/), over FC
    def after(array: str, showvv: str):
        over = {**_over_fc(array, "after_apply"),
                "showvvset": (FIX / "rc_pair" / "after_apply" / array / "showvvset.txt").read_text(encoding="utf-8")}
        return read_array(rc_apply._creds("x"), array_cli_factory=lambda c: rc_apply._Cli(array, showvv=showvv, overrides=over))

    reads = iter([after("D22U27", rc_apply._SHOWVV_A), after("E18U31", "Name VSize_MB\n")])
    out = verify(prov, fc_plan, read_fn=lambda creds, progress=None: next(reads))
    assert out.error is None and out.links_ok
    assert out.links_detail == ("AlletraMP_D22U27 → AlletraMP_E18U31 via 'AlletraMP_E18U31' 2/2 links Up · "
                                "AlletraMP_E18U31 → AlletraMP_D22U27 via 'AlletraMP_E18U31' 2/2 links Up")
    assert [(g.group, g.verdict) for g in out.groups] == [("zz_rc_vvs_rcg", "replicating"), ("zz_rc_test_rcg", "replicating")]


# ------------------------------------------------------------------ R7: the as-built

def test_the_as_built_names_the_fc_links_the_transport_and_says_the_latency_was_typed(tmp_path):
    from alletra_onboard.application.documents.asbuilt import generate_asbuilt
    from tests.unit import test_asbuilt_replication as doc_tests

    a, b = _working_fc_pair()
    note = ("Round-trip time 11 ms, typed on the Replication tab by the engineer, not measured (the tool cannot measure "
            "Fibre Channel links yet); over the 10 ms limit for async over Fibre Channel — the operator accepted it and "
            "chose to continue.")
    tab = {"peer_host": "b", "failover_test": False, "rtt_ms": 11.0,
           "rows": [{"vvset": "HS", "mode": "async", "rpo_minutes": 10, "peer_cpg": "SSD_r6"}]}
    out, _ = generate_asbuilt(doc_tests._data(replication_tab=tab, replication_primary=a, replication_peer=b,
                                              replication_result={"outcomes": [], "notes": [note]}),
                              tmp_path / "fc.docx")
    doc, text = doc_tests._read(out)
    tables = doc_tests._tables(doc)
    assert tables[("Array", "Serial", "OS", "Remote Copy", "Replication ports")] == [
        ["This array: SiteA", "SA", "10.5.60", "Started, Normal", "0:3:3 → 20330002AC0000B2; 1:3:3 → 21330002AC0000B2"],
        ["Peer: SiteB", "SB", "10.5.60", "Started, Normal", "0:3:3 → 20330002AC0000A1; 1:3:3 → 21330002AC0000A1"],
    ]
    assert ("Partnered: SiteA → SiteB via target 'SiteB' (2/2 links Up); SiteB → SiteA via target 'SiteA' (2/2 links "
            "Up). Over Fibre Channel, found by port WWN.") in text
    assert tables[("Array", "Target", "Policy", "Link (port → peer port WWN)", "Status")][0] == [
        "SiteA", "SiteB", "mirror_config", "0:3:3 → 20330002AC0000B2", "Up"]
    assert ("Typed by the engineer on the Replication tab, not measured: 11 ms. The tool cannot measure Fibre Channel "
            "links yet. Async replication over Fibre Channel needs 10 ms or less. The typed time is over HPE's limit for "
            "async — the operator accepted the typed time and continued.") in text
    assert "checkrclink" not in text and "RCIP" not in text


def test_the_old_fc_target_guard_reads_every_node_wwn_of_the_other_array():
    """LESSONS 41: the R5 blocker reads the same WWNs as the partnership. With a peer port listed first, the
    first FC row's node WWN is the peer port's `0202` one, and an FC target for the array was missed."""
    from alletra_onboard.application.replication.partnership import stale_fc_targets

    peer_first = {"0:3:1": PortRole(nsp="0:3:1", mode="initiator", state="ready", type="peer", protocol="FC",
                                    node_wwn="2FF70202AC0000A1", port_wwn="20310202AC0000A1"), **_fc_ports(A_NODE, A_FC)}
    a = ReplicationArrayView(name="arrayA", ports=peer_first, fc_node_wwn="2FF70202AC0000A1")
    b_links: list = []
    b = ReplicationArrayView(name="arrayB", links=b_links, targets=[
        _target(b_links, "arrayA_fc", fc=True, node=A_NODE, status="failed", up="Down", to={"0:3:3": A_FC["0:3:3"]})])
    [msg] = stale_fc_targets(a, b)
    assert "`removercopytarget -cleargroups -f arrayA_fc`" in msg
