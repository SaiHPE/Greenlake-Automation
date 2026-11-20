"""SPEC-021 R4/R5: RCIP ports and partnership apply over the write-scoped SSH client (ADR 0015,
STANDARD S2). Planning lives in `partnership.py`; only this module imports `replication/clients.py`."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from alletra_onboard.application.replication.clients import make_rc_writer
from alletra_onboard.application.replication.partnership import plan_objects
from alletra_onboard.application.replication.read import parse_showport_rcip, parse_showrcopy
from alletra_onboard.application.runs.apply_record import maybe_made, recorded_write
from alletra_onboard.domain.approval import Approval, SaveRecord
from alletra_onboard.domain.array_parse import answered_error
from alletra_onboard.domain.errors import ApplyRecordError, ArrayCliError, DeviceError
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    ReplicationAction,
    ReplicationIntent,
    ReplicationOutcome,
    ReplicationPlan,
    ReplicationResult,
    pair_ports,
)

if TYPE_CHECKING:
    from alletra_onboard.application.replication.clients import ArrayRcCliClient

#: How long the apply waits for every planned link to show Up.
LINKS_UP_WAIT_S = 180.0
LINKS_UP_POLL_S = 10.0


@dataclass
class _PartnerState:
    cli: dict[str, ArrayRcCliClient]
    result: ReplicationResult
    save: SaveRecord
    say: Callable[[str], None]
    created_ports: dict[str, list[str]] = field(default_factory=lambda: {"A": [], "B": []})
    started: dict[str, bool] = field(default_factory=dict)
    targets: dict[str, str] = field(default_factory=dict)

    def record(self, kind, name, where, status, detail="") -> None:
        self.result.outcomes.append(ReplicationOutcome(kind=kind, name=name, where=where, status=status, detail=detail))

    def compose(self) -> None:
        for side in ("A", "B"):
            lines = [f"removercopytarget {self.targets[side]}"] if side in self.targets else []
            if side in self.started:
                lines.append("stoprcopy -f -stopgroups -clear" if self.started[side] else "stoprcopy -f")
            lines += [f"controlport rcip delete -f {nsp}" for nsp in self.created_ports[side]]
            if side == "A":
                self.result.removals_a = lines
            else:
                self.result.removals_b = lines

    def write(self, side: str, command: str) -> str:
        out = self.cli[side].write(command)
        if answered_error(out):
            raise ArrayCliError(f"{'this array' if side == 'A' else 'the peer'} refused `{command}`: "
                                + next(ln.strip() for ln in out.splitlines() if ln.strip().lower().startswith("error")))
        return out


def _actions(plan: ReplicationPlan, kind: str, side: str) -> list[ReplicationAction]:
    return [x for x in plan.actions if x.kind == kind and x.where == side and x.state == "create"]


def _apply_ports(plan: ReplicationPlan, st: _PartnerState) -> None:
    for side in ("A", "B"):
        for x in _actions(plan, "rcip_port", side):
            d = x.detail
            st.say(f"Setting RCIP address {d['ip']} on {x.name} ({side})…")
            note = maybe_made(f"RCIP address {d['ip']} on {x.name} ({side})", "showport -rcip",
                              f"controlport rcip delete -f {x.name}")
            # ADR 0025 condition 4: the removal line is on record before the command is sent.
            st.created_ports[side].append(x.name)
            st.compose()
            with recorded_write(st.result, note, st.save):
                st.write(side, f"controlport rcip addr -f {d['ip']} {d['netmask']} {x.name}")
                if d.get("gateway"):
                    st.write(side, f"controlport rcip gw -f {d['gateway']} {x.name}")
                back = {p.nsp: p for p in parse_showport_rcip(st.cli[side].run("showport -rcip"))}.get(x.name)
                if back is None or back.ip != d["ip"]:
                    raise ArrayCliError(f"after setting it, showport -rcip does not show {d['ip']} on {x.name}")
                if d.get("gateway") and back.gateway != d["gateway"]:
                    raise ArrayCliError(f"after setting it, showport -rcip shows gateway {back.gateway or 'none'} on "
                                        f"{x.name}, not {d['gateway']}")
                st.record("rcip_port", x.name, side, "created",
                          f"{d['ip']} {d['netmask']}" + (f", gateway {d['gateway']}" if d.get("gateway") else "") + f", {back.state}")


def _ping_pairs(intent: ReplicationIntent, st: _PartnerState) -> None:
    for pa, pb in pair_ports(intent.network):
        st.say(f"Ping {pb.ip} from {pa.nsp}…")
        out = st.cli["A"].write(f"controlport rcip ping -c 3 {pb.ip} {pa.nsp}")
        line = next((ln.strip() for ln in out.splitlines() if "packet loss" in ln), out.strip()[-120:])
        if " 0% packet loss" not in f" {line}":
            raise ArrayCliError(f"ping from {pa.nsp} to {pb.ip}: {line}. Check the cable and the network of "
                                f"{pa.nsp}; nothing after the addresses was done")
        st.record("ping", f"{pa.nsp} → {pb.ip}", "A", "created", line)


def _apply_service_and_targets(plan: ReplicationPlan, st: _PartnerState) -> None:
    for side in ("A", "B"):
        for x in _actions(plan, "rc_service", side):
            st.say(f"Starting Remote Copy ({side})…")
            st.started[side] = not x.detail.get("was_configured")
            st.compose()
            with recorded_write(st.result, maybe_made(f"Remote Copy ({side})", "showrcopy"), st.save):
                st.write(side, "startrcopy")
                status = parse_showrcopy(st.cli[side].run("showrcopy"))["status"]
                if status != "Started":
                    raise ArrayCliError(f"after startrcopy, showrcopy says '{status or 'not configured'}'")
                st.record("rc_service", "Remote Copy", side, "created", "started")
    for side in ("A", "B"):
        for x in _actions(plan, "target", side):
            links = x.detail["links"]
            st.say(f"Creating target {x.name} ({side})…")
            note = maybe_made(f"target {x.name} ({side})", "showrcopy targets", f"removercopytarget {x.name}")
            st.targets[side] = x.name
            st.compose()
            with recorded_write(st.result, note, st.save):
                st.write(side, f"creatercopytarget {x.name} IP {' '.join(links)}")
                names = [t.name for t in parse_showrcopy(st.cli[side].run("showrcopy targets"))["targets"]]
                if x.name not in names:
                    raise ArrayCliError(f"after creatercopytarget, showrcopy targets does not list '{x.name}'")
                st.record("target", x.name, side, "created", f"{len(links)} link(s): {', '.join(links)}")


def _wait_links_up(plan: ReplicationPlan, st: _PartnerState) -> None:
    st.say("Waiting for the links to come up…")
    waited, down = 0.0, []
    while True:
        down = []
        for side, cli_ in st.cli.items():
            want = next((x for x in plan.actions if x.kind == "target" and x.where == side), None)
            if want is None:
                continue
            target = want.detail.get("existing") or want.name
            links = [lk for lk in parse_showrcopy(cli_.run("showrcopy links"))["links"] if lk.target == target]
            down += [f"{side} {lk.nsp} → {lk.address} {lk.status}" for lk in links if not lk.up]
            if not links:
                down.append(f"{side}: no link on target '{target}'")
        if not down or waited >= LINKS_UP_WAIT_S:
            break
        time.sleep(LINKS_UP_POLL_S)
        waited += LINKS_UP_POLL_S
    if down:
        raise ArrayCliError(f"links not Up after {LINKS_UP_WAIT_S:g} s: {'; '.join(down)}")
    st.record("links", "Remote Copy links", "A", "created", "every planned link Up on both arrays")


def apply_partnership(
    plan: ReplicationPlan, provisioning: ProvisioningIntent, approval: Approval, *,
    rc_cli_factory: Callable = make_rc_writer, progress: Callable[[str], None] | None = None,
) -> ReplicationResult:
    """SPEC-021 R4: ports on A, ports on B, ping each pair, start Remote Copy, a target each way, links
    Up. Stops at the first refusal; the removal set (R5) covers exactly what was created."""
    result = ReplicationResult()
    intent = provisioning.replication
    if intent is None:
        result.error = "this run has no Replication tab"
        return result
    st: _PartnerState | None = None
    save = approval.require_saver()
    try:
        with (rc_cli_factory(approval, "A", plan_objects(plan, "A")) as a_cli,
              rc_cli_factory(approval, "B", plan_objects(plan, "B")) as b_cli):
            st = _PartnerState(cli={"A": a_cli, "B": b_cli}, result=result,
                               save=save, say=progress or (lambda _m: None))
            _apply_ports(plan, st)
            _ping_pairs(intent, st)
            _apply_service_and_targets(plan, st)
            _wait_links_up(plan, st)
    except (DeviceError, ApplyRecordError) as exc:  # the array's words, where it stopped, what to remove
        done = sum(1 for o in result.outcomes if o.status == "created")
        result.error = (f"Stopped after {done} step(s): {exc}. The removal set below undoes exactly what was "
                        "created before the failure.")
        result.outcomes.append(ReplicationOutcome(kind="links", name="—", where="A", status="failed", detail=str(exc)))
    if st is not None:
        st.compose()
    return result
