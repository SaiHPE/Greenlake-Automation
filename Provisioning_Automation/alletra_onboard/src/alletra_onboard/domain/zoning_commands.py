"""Pure Brocade FOS zoning write-command validation (ADR 0033, ADR 0025).

Lives in `domain` (zero I/O) so both `adapters/fabric/brocade_writer.py` (runtime send guard)
and `application/provisioning/zoning_apply.py` (build-time plan validation) enforce the exact
same five prompt-free FOS v9.2 forms without violating S2-brocade-writer or L3-clients-only.
"""

from __future__ import annotations

import re

from alletra_onboard.domain.plan_objects import ZoningPlanObjects
from alletra_onboard.domain.shared import normalize_wwpn
from alletra_onboard.domain.zoning import fos_name_problem

FORBIDDEN_WRITE_CHARS = frozenset("|&`$><\n\r\\'")
_WWPN_LOWER = r"(?:[0-9a-f]{2}:){7}[0-9a-f]{2}"

BROCADE_WRITE_FORMS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("alicreate", re.compile(rf'^alicreate "(?P<alias>[^"]+)","(?P<wwpn>{_WWPN_LOWER})"$')),
    ("zonecreate", re.compile(r'^zonecreate "(?P<zone>[^"]+)","(?P<m1>[^";]+);(?P<m2>[^";]+)"$')),
    ("cfgadd", re.compile(r'^cfgadd "(?P<cfg>[^"]+)","(?P<zones>[^"]+)"$')),
    ("cfgenable", re.compile(r'^cfgenable "(?P<cfg>[^"]+)" -f$')),
    ("cfgtransabort", re.compile(r"^cfgtransabort$")),
)


def match_zoning_write_form(command: str) -> tuple[str, re.Match[str]] | None:
    for kind, pattern in BROCADE_WRITE_FORMS:
        match = pattern.match(command)
        if match is not None:
            return kind, match
    return None


def _names_refusal(kind: str, match: re.Match[str]) -> str | None:
    if kind == "alicreate":
        names = [match.group("alias")]
    elif kind == "zonecreate":
        names = [match.group("zone"), match.group("m1"), match.group("m2")]
    elif kind == "cfgadd":
        members = match.group("zones").split(";")
        if any(not z for z in members):
            return "refused: cfgadd zone list contains an empty entry"
        if len(set(members)) != len(members):
            return "refused: cfgadd zone list contains duplicate zone names"
        names = [match.group("cfg"), *members]
    elif kind == "cfgenable":
        names = [match.group("cfg")]
    else:
        return None
    for name in names:
        if why := fos_name_problem(name):
            return f"refused: '{name}' {why}"
    return None


def zoning_write_refusal(command: str) -> str | None:
    """Why `BrocadeZoneWriter.write` refuses the shape of `command`, or None when it matches an exact form."""
    if any(ch in command for ch in FORBIDDEN_WRITE_CHARS):
        return "refused: command contains a forbidden shell metacharacter"
    matched = match_zoning_write_form(command)
    if matched is None:
        return ("refused: only exact Brocade zoning apply commands may run here "
                "(alicreate, zonecreate, cfgadd, cfgenable -f, cfgtransabort)")
    kind, match = matched
    return _names_refusal(kind, match)


def _check_cfg_object(kind: str, match: re.Match[str], objects: ZoningPlanObjects) -> str | None:
    cfg = match.group("cfg")
    if cfg != objects.active_cfg:
        return f"refused: cfg '{cfg}' does not match the approved active cfg '{objects.active_cfg}'"
    if not objects.zones:
        return "refused: approved plan contains no zones to activate"
    if kind != "cfgadd":
        return None
    planned_zones = {zone for zone, _m1, _m2 in objects.zones}
    for zone in match.group("zones").split(";"):
        if zone not in planned_zones:
            return f"refused: zone '{zone}' is not in the approved plan"
    return None


def zoning_object_refusal(command: str, objects: ZoningPlanObjects) -> str | None:
    """Why `BrocadeZoneWriter.write` refuses a well-formed `command` for naming an object outside the approved plan."""
    if shape_err := zoning_write_refusal(command):
        return shape_err
    matched = match_zoning_write_form(command)
    if matched is None:
        return "refused: command does not match an allowed form"
    kind, match = matched
    if kind == "cfgtransabort":
        return None
    if kind == "alicreate":
        pair = (match.group("alias"), normalize_wwpn(match.group("wwpn")))
        allowed = {(name, normalize_wwpn(wwpn)) for name, wwpn in objects.aliases}
        return None if pair in allowed else f"refused: alias '{pair[0]}' ({match.group('wwpn')}) is not in the approved plan"
    if kind == "zonecreate":
        triple = (match.group("zone"), match.group("m1"), match.group("m2"))
        return None if triple in objects.zones else f"refused: zone '{triple[0]}' is not in the approved plan"
    return _check_cfg_object(kind, match, objects)
