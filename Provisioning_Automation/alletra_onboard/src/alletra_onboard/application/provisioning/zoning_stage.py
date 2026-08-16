"""Stage the operator-selected zones into each fabric's DEFINED configuration (ADR 0004, revised
2026-08-15 write-path mandate). Additive only: `alicreate` → `zonecreate` → `cfgadd` → `cfgsave`.
**Never `cfgenable`** — activation replaces the effective config fabric-wide and stays a manual
human action — and never any delete: existing zones cannot be touched from here (the adapter's
write patterns have no delete verb).

The sequence per fabric is built around the live-measured FOS behaviors (2026-08-15, FOS 9.2.2):

1. `cfgtransshow` — refuse if ANY zoning transaction is already open. Committing would auto-abort
   another admin's in-flight work (documented FOS behavior); the tool never risks that. The FOS 9.0+
   fabric lock (5-minute default) enforces the same thing switch-side.
2. Staleness re-check — the plan was built from an earlier `cfgshow`; another admin may have changed
   zoning since. The effective-config name must still match, and none of the zone names we are about
   to create may already exist in the defined config.
3. Execute the additive commands. Any FOS complaint aborts the transaction (`cfgtransabort` — rolls
   back OUR uncommitted work only) so nothing partial is ever committed.
4. `cfgsave` with the confirmation answered 'y'. A canceled save exits 248 and raises.
5. VERIFY by re-reading `cfgshow`: every zone present in the DEFINED section, and the effective
   config unchanged. cfgsave's exit status alone is never trusted.

The result carries the Broadcom defined≠effective warning verbatim in spirit: the divergence is
documented to yield different effective zoning across switches on a zone merge or HA failover, so
activation must be an explicit, prompt hand-off — not an indefinitely deferred afterthought.
"""

from __future__ import annotations

import re
from typing import Callable

from alletra_onboard.application.provisioning.clients import make_brocade
from alletra_onboard.application.provisioning.zoning_plan import parse_active_cfg, render_commands
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.zoning import FabricStageResult, ZoningPlan, ZoningStageResult

# Shown until a human activates. Paraphrases Broadcom's own cfgsave warning (FOS 9.2.x Advanced
# Zoning guide): the staged state is non-traffic-affecting in steady state, but not risk-free.
DIVERGENCE_WARNING = (
    "The defined and effective zoning configurations now differ on the staged fabric(s). Broadcom "
    "documents that a persistent divergence can produce DIFFERENT effective zoning across switches "
    "if a zone merge or HA failover occurs. Have the SAN team run the hand-off command during a "
    "maintenance window promptly — do not leave the divergence in place indefinitely."
)

_ZONE_LINE = r"zone:\s+{name}\b"


def _defined_section(cfgshow: str) -> str:
    """The DEFINED portion of `cfgshow` — everything before the effective section."""
    return (cfgshow or "").split("Effective configuration")[0]


def stage_zones(
    intent: ProvisioningIntent,
    plan: ZoningPlan,
    aliases: dict[str, str],
    selected_pairs: list[tuple[str, str]],
    *,
    brocade_factory: Callable = make_brocade,
) -> ZoningStageResult:
    """Render the operator's selection and stage it on each fabric switch (defined config only).
    Every failure is per-fabric and leaves that switch exactly as found (transaction aborted)."""
    commands, skipped = render_commands(plan, aliases, selected_pairs)
    result = ZoningStageResult(warning="")
    creds = {"F1": intent.switch_f1, "F2": intent.switch_f2}

    for fabric in plan.fabrics:
        label = fabric.fabric
        cmds = [c for c in commands.get(label, []) if not c.startswith("cfgenable")]
        zone_names = [m.group(1) for c in cmds if (m := re.match(r'zonecreate "([^"]+)"', c))]
        fr = FabricStageResult(
            fabric=label, switch_host=creds[label].host, skipped=list(skipped.get(label, [])),
        )
        result.fabrics.append(fr)
        if not zone_names:
            continue  # nothing selected/renderable on this fabric — not an error

        try:
            with brocade_factory(creds[label]) as switch:
                # 1) Never stack onto anyone's open transaction — ours would commit theirs or
                #    theirs would swallow ours; either way it is not this tool's call to make.
                trans = switch.cfgtransshow()
                if "no outstanding" not in trans.lower() and "there is no" not in trans.lower():
                    fr.error = (
                        "another zoning transaction is open on this switch (fabric lock) — retry "
                        "once it clears. The tool never aborts someone else's work. "
                        f"[{trans.strip().splitlines()[0] if trans.strip() else 'cfgtransshow gave no detail'}]"
                    )
                    continue

                # 2) The plan is a snapshot; re-check it against the switch as it is NOW.
                before = switch.cfgshow()
                cfg_now = parse_active_cfg(before)
                if fabric.active_cfg and cfg_now != fabric.active_cfg:
                    fr.error = (
                        f"the effective configuration changed since the plan was built "
                        f"({fabric.active_cfg!r} → {cfg_now!r}) — rebuild the zoning plan first"
                    )
                    continue
                defined_before = _defined_section(before)
                collisions = [
                    z for z in zone_names if re.search(_ZONE_LINE.format(name=re.escape(z)), defined_before)
                ]
                if collisions:
                    fr.error = (
                        "zone name(s) already exist in the defined configuration: "
                        + ", ".join(collisions)
                        + " — rebuild the plan (the delta is stale) or choose different alias names"
                    )
                    continue

                # 3) Additive commands; any refusal rolls the whole transaction back.
                done: list[str] = []
                try:
                    for cmd in cmds:
                        switch.write(cmd)
                        done.append(cmd)
                    switch.cfgsave_defined()
                except Exception as exc:  # noqa: BLE001
                    switch.cfgtransabort()
                    fr.error = (
                        f"{exc} — the transaction was aborted, nothing was committed "
                        f"({len(done)}/{len(cmds)} command(s) had been accepted before the failure)"
                    )
                    continue
                fr.staged = done

                # 4) Trust nothing: prove the zones landed in DEFINED and the effective cfg is untouched.
                after = switch.cfgshow()
                defined_after = _defined_section(after)
                missing = [
                    z for z in zone_names if not re.search(_ZONE_LINE.format(name=re.escape(z)), defined_after)
                ]
                cfg_after = parse_active_cfg(after)
                if missing:
                    fr.error = (
                        "cfgsave reported success but the defined configuration is missing zone(s): "
                        + ", ".join(missing) + " — inspect the switch before doing anything else"
                    )
                elif cfg_after != cfg_now:
                    fr.error = (
                        f"the EFFECTIVE configuration changed during staging ({cfg_now!r} → {cfg_after!r}) "
                        "— this tool never activates; investigate before anyone runs cfgenable"
                    )
                else:
                    fr.verified = True
                    fr.handoff = f"cfgenable {cfg_now}" if cfg_now else ""
        except Exception as exc:  # noqa: BLE001 - one unreachable switch must not sink the other fabric
            fr.error = str(exc)

    if any(f.verified and f.staged for f in result.fabrics):
        result.warning = DIVERGENCE_WARNING
    return result
