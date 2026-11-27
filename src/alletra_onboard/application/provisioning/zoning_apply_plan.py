"""Pure Brocade FOS zoning apply-plan builder (ADR 0033).

Builds per-fabric `ZoningApplyPlan` and reverse-order removal command sets from rendered host and
peer zoning commands, rejecting host/peer alias or zone collisions and validating every generated
write command against the exact FOS grammar (`domain/zoning_commands.py`) at build time.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from alletra_onboard.application.provisioning.zoning_plan import render_commands
from alletra_onboard.application.runs.coordinator import new_plan_id
from alletra_onboard.domain.plan_objects import ZoningPlanObjects
from alletra_onboard.domain.shared import Fabric, normalize_wwpn, wwpn_colons
from alletra_onboard.domain.zoning import (
    FabricZonePlan,
    FabricZoningApplyPlan,
    ZoningApplyPlan,
    ZoningPlan,
)
from alletra_onboard.domain.zoning_commands import (
    zoning_object_refusal,
    zoning_write_refusal,
)

_ALICREATE_RE = re.compile(r'^alicreate "([^"]+)","([^"]+)"$')
_ZONECREATE_RE = re.compile(r'^zonecreate "([^"]+)","([^";]+);([^";]+)"$')

LABEL_TO_FABRIC: dict[str, Fabric] = {"F1": "odd", "F2": "even", "odd": "odd", "even": "even"}
_FABRIC_TO_LABEL: dict[Fabric, str] = {"odd": "F1", "even": "F2"}


def fabric_label(fabric: Fabric) -> str:
    return _FABRIC_TO_LABEL[fabric]


def plan_objects_for(fab: FabricZoningApplyPlan) -> ZoningPlanObjects:
    return ZoningPlanObjects(
        active_cfg=fab.active_cfg,
        aliases=tuple((name, normalize_wwpn(wwpn)) for name, wwpn in fab.aliases.items()),
        zones=tuple((zone, m1, m2) for zone, (m1, m2) in fab.zones.items()),
    )


def _extract_objects(raw_commands: list[str]) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    aliases: dict[str, str] = {}
    zones: dict[str, tuple[str, str]] = {}
    for cmd in raw_commands:
        if m := _ALICREATE_RE.match(cmd):
            name = m.group(1)
            norm = normalize_wwpn(m.group(2))
            if len(norm) != 16:
                raise ValueError(f"Alias '{name}' has invalid WWPN '{m.group(2)}'.")
            disp = wwpn_colons(norm)
            if name in aliases and aliases[name] != disp:
                raise ValueError(
                    f"Alias '{name}' maps to two different WWPNs ({aliases[name]} and {disp}) "
                    "across host and peer commands."
                )
            aliases[name] = disp
        elif m := _ZONECREATE_RE.match(cmd):
            zone, pair = m.group(1), (m.group(2), m.group(3))
            if zone in zones and zones[zone] != pair:
                raise ValueError(
                    f"Zone '{zone}' maps to two different member pairs ({zones[zone]} and {pair}) "
                    "across host and peer commands."
                )
            zones[zone] = pair
    return aliases, zones


def _build_removals(
    active_cfg: str, aliases: dict[str, str], zones: dict[str, tuple[str, str]],
) -> list[str]:
    zone_names = list(zones)
    alias_names = list(aliases)
    if not zone_names and not alias_names:
        return []
    out: list[str] = []
    if zone_names:
        out.append(f'cfgremove "{active_cfg}","{";".join(zone_names)}"')
    for zone in reversed(zone_names):
        out.append(f'zonedelete "{zone}"')
    for alias in reversed(alias_names):
        out.append(f'alidelete "{alias}"')
    out.append(f'cfgenable "{active_cfg}" -f')
    return out


def _validate_apply_commands(fab: FabricZoningApplyPlan) -> None:
    objects = plan_objects_for(fab)
    for cmd in fab.commands:
        if why := (zoning_write_refusal(cmd) or zoning_object_refusal(cmd, objects)):
            raise ValueError(f"Command '{cmd}' cannot be applied on {fab.switch_host}: {why}")


def _build_fabric_apply_plan(
    fab: FabricZonePlan, raw_commands: list[str],
) -> FabricZoningApplyPlan | None:
    fabric = LABEL_TO_FABRIC.get(fab.fabric)
    if fabric is None or not fab.active_cfg or not raw_commands:
        return None
    fab_aliases, fab_zones = _extract_objects(raw_commands)
    if not fab_zones:
        return None
    write_commands: list[str] = [
        *(f'alicreate "{alias}","{wwpn}"' for alias, wwpn in fab_aliases.items()),
        *(f'zonecreate "{zone}","{m1};{m2}"' for zone, (m1, m2) in fab_zones.items()),
        f'cfgadd "{fab.active_cfg}","{";".join(fab_zones)}"',
        f'cfgenable "{fab.active_cfg}" -f',
    ]
    entry = FabricZoningApplyPlan(
        fabric=fabric,
        switch_host=fab.switch_host,
        active_cfg=fab.active_cfg,
        aliases=fab_aliases,
        zones=fab_zones,
        commands=write_commands,
        removals=_build_removals(fab.active_cfg, fab_aliases, fab_zones),
    )
    _validate_apply_commands(entry)
    return entry


def build_apply_plan(
    plan: ZoningPlan,
    aliases: dict[str, str],
    selected_pairs: Sequence[Sequence[str]] | None,
    commands: dict[str, list[str]] | None = None,
    peer_commands: dict[str, list[str]] | None = None,
) -> ZoningApplyPlan:
    """Build per-fabric opt-in Brocade apply plans from the rendered host and peer command sets."""
    if commands is None:
        pairs = None if selected_pairs is None else [(p[0], p[1]) for p in selected_pairs]
        commands, _skipped = render_commands(plan, aliases, pairs)
    peer_map = peer_commands or {}
    fabrics: list[FabricZoningApplyPlan] = []
    for fab in plan.fabrics:
        combined = [*(commands.get(fab.fabric) or []), *(peer_map.get(fab.fabric) or [])]
        if entry := _build_fabric_apply_plan(fab, combined):
            fabrics.append(entry)
    return ZoningApplyPlan(plan_id=new_plan_id() if fabrics else "", fabrics=fabrics)
