"""SPEC-021 R4/R5: RCIP ports and partnership apply over the write-scoped SSH client (ADR 0015,
STANDARD S2). Planning lives in `partnership.py`; only this module imports `replication/clients.py`."""

from __future__ import annotations

import time
from collections.abc import Callable

from alletra_onboard.application.replication.clients import make_rc_writer
from alletra_onboard.application.replication.partnership import plan_objects
from alletra_onboard.application.replication.read import parse_showport_rcip, parse_showrcopy
from alletra_onboard.domain.array_parse import answered_error
from alletra_onboard.domain.errors import ArrayCliError
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    ReplicationAction,
    ReplicationOutcome,
    ReplicationPlan,
    ReplicationResult,
    pair_ports,
)

#: How long the apply waits for every planned link to show Up.
LINKS_UP_WAIT_S = 180.0
LINKS_UP_POLL_S = 10.0


def apply_partnership(
    plan: ReplicationPlan, provisioning: ProvisioningIntent, *, rc_cli_factory: Callable = make_rc_writer,
    progress: Callable[[str], None] | None = None, sleep: Callable[[float], None] = time.sleep,
) -> ReplicationResult:
    """SPEC-021 R4: ports on A, ports on B, ping each pair, start Remote Copy, a target each way, links
    Up. Stops at the first refusal; the removal set (R5) covers exactly what was created."""
    result = ReplicationResult()
    intent = provisioning.replication
    if intent is None:
        result.error = "this run has no Replication tab"
        return result
    say = progress or (lambda _m: None)
    created_ports: dict[str, list[str]] = {"A": [], "B": []}
    started: dict[str, bool] = {}               # side -> Remote Copy was not configured before
    targets: dict[str, str] = {}

    def record(kind, name, where, status, detail="") -> None:
        result.outcomes.append(ReplicationOutcome(kind=kind, name=name, where=where, status=status, detail=detail))

    def compose() -> None:
        for side in ("A", "B"):
            lines = [f"removercopytarget {targets[side]}"] if side in targets else []
            if side in started:
                lines.append("stoprcopy -f -stopgroups -clear" if started[side] else "stoprcopy -f")
            lines += [f"controlport rcip delete -f {nsp}" for nsp in created_ports[side]]
            if side == "A":
                result.removals_a = lines
            else:
                result.removals_b = lines

    def actions(kind: str, side: str) -> list[ReplicationAction]:
        return [x for x in plan.actions if x.kind == kind and x.where == side and x.state == "create"]

    try:
        with (rc_cli_factory(provisioning.array, plan_objects(plan, "A")) as a_cli,
              rc_cli_factory(intent.peer, plan_objects(plan, "B")) as b_cli):
            cli = {"A": a_cli, "B": b_cli}

            def write(side: str, command: str) -> str:
                out = cli[side].write(command)
                if answered_error(out):
                    raise ArrayCliError(f"{'this array' if side == 'A' else 'the peer'} refused `{command}`: "
                                        + next(ln.strip() for ln in out.splitlines() if ln.strip().lower().startswith("error")))
                return out

            for side in ("A", "B"):
                for x in actions("rcip_port", side):
                    d = x.detail
                    say(f"Setting RCIP address {d['ip']} on {x.name} ({side})…")
                    created_ports[side].append(x.name)          # before the write: a half-done address is undone too
                    compose()
                    write(side, f"controlport rcip addr -f {d['ip']} {d['netmask']} {x.name}")
                    if d.get("gateway"):
                        write(side, f"controlport rcip gw -f {d['gateway']} {x.name}")
                    back = {p.nsp: p for p in parse_showport_rcip(cli[side].run("showport -rcip"))}.get(x.name)
                    if back is None or back.ip != d["ip"]:
                        raise ArrayCliError(f"after setting it, showport -rcip does not show {d['ip']} on {x.name}")
                    if d.get("gateway") and back.gateway != d["gateway"]:
                        raise ArrayCliError(f"after setting it, showport -rcip shows gateway {back.gateway or 'none'} on "
                                            f"{x.name}, not {d['gateway']}")
                    record("rcip_port", x.name, side, "created",
                           f"{d['ip']} {d['netmask']}" + (f", gateway {d['gateway']}" if d.get("gateway") else "") + f", {back.state}")

            for pa, pb in pair_ports(intent.network):
                say(f"Ping {pb.ip} from {pa.nsp}…")
                out = a_cli.write(f"controlport rcip ping -c 3 {pb.ip} {pa.nsp}")
                line = next((ln.strip() for ln in out.splitlines() if "packet loss" in ln), out.strip()[-120:])
                if " 0% packet loss" not in f" {line}":
                    raise ArrayCliError(f"ping from {pa.nsp} to {pb.ip}: {line}. Check the cable and the network of "
                                        f"{pa.nsp}; nothing after the addresses was done")
                record("ping", f"{pa.nsp} → {pb.ip}", "A", "created", line)

            for side in ("A", "B"):
                for x in actions("rc_service", side):
                    say(f"Starting Remote Copy ({side})…")
                    started[side] = not x.detail.get("was_configured")
                    compose()
                    write(side, "startrcopy")
                    status = parse_showrcopy(cli[side].run("showrcopy"))["status"]
                    if status != "Started":
                        raise ArrayCliError(f"after startrcopy, showrcopy says '{status or 'not configured'}'")
                    record("rc_service", "Remote Copy", side, "created", "started")

            for side in ("A", "B"):
                for x in actions("target", side):
                    links = x.detail["links"]
                    say(f"Creating target {x.name} ({side})…")
                    targets[side] = x.name
                    compose()
                    write(side, f"creatercopytarget {x.name} IP {' '.join(links)}")
                    names = [t.name for t in parse_showrcopy(cli[side].run("showrcopy targets"))["targets"]]
                    if x.name not in names:
                        raise ArrayCliError(f"after creatercopytarget, showrcopy targets does not list '{x.name}'")
                    record("target", x.name, side, "created", f"{len(links)} link(s): {', '.join(links)}")

            say("Waiting for the links to come up…")
            waited, down = 0.0, []
            while True:
                down = []
                for side, cli_ in cli.items():
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
                sleep(LINKS_UP_POLL_S)
                waited += LINKS_UP_POLL_S
            if down:
                raise ArrayCliError(f"links not Up after {LINKS_UP_WAIT_S:g} s: {'; '.join(down)}")
            record("links", "Remote Copy links", "A", "created", "every planned link Up on both arrays")
    except Exception as exc:  # the array's words, where it stopped, what to remove
        done = sum(1 for o in result.outcomes if o.status == "created")
        result.error = (f"Stopped after {done} step(s): {exc}. The removal set below undoes exactly what was "
                        "created before the failure.")
        record("links", "—", "A", "failed", str(exc))
    compose()
    return result
