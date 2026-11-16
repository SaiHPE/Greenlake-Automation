"""Validate the SHIPPED zoning write path against a real FOS switch — the code under test is the
product's own BrocadeClient + stage_zones, not a mirror of it.

What it does (WRITE=1 only; the default run is read-only and prints what would happen):

    1. Reads the switch (read-only) to learn the live effective config name.
    2. Builds a synthetic single-pair plan whose two members are FAKE WWPNs
       (aa:bb:cc:dd:ee:00:00:01/02) — no real device carries them, so even if the zone were ever
       activated it can never match a login or move traffic.
    3. Runs the shipped `stage_zones`: cfgtransshow guard → staleness re-check → alicreate ×2 →
       zonecreate → cfgadd → cfgsave (answered 'y') → cfgshow read-back verification.
    4. Independently re-reads the switch and proves the objects are in the DEFINED config and the
       effective config is untouched.
    5. Prints the REMOVAL commands for the SAN team. This script deletes NOTHING — the product's
       write surface has no delete verb, and cleanup of the zz_probe objects is a disclosed manual
       action, exactly like the zz_val test zone before it.

Objects created (all prefixed, all fake-membered):
    aliases  zz_probe_h / zz_probe_a      zone  zz_probe_h_zz_probe_a      + cfgadd to the live cfg

Run from the repo root (the venv has the package installed editable):
    .\\.venv\\Scripts\\python.exe scripts\\validation\\stage_writepath_validate.py            # read-only preview
    $env:WRITE="1"; .\\.venv\\Scripts\\python.exe scripts\\validation\\stage_writepath_validate.py
"""

from __future__ import annotations

import os
import sys

from alletra_onboard.adapters.fabric.brocade_client import BrocadeClient
from alletra_onboard.application.provisioning.zoning_plan import parse_active_cfg
from alletra_onboard.application.provisioning.zoning_stage import stage_zones
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.zoning import AliasedWwpn, FabricZonePlan, ZoningPlan

SW_HOST = os.environ.get("SW_HOST", "10.64.122.146")   # VZ F1 (FOS 9.2.2, proven reachable)
SW_USER = os.environ.get("SW_USER", "admin")
SW_PW = os.environ.get("SW_PW", "")                    # export SW_PW before running
WRITE = os.environ.get("WRITE") == "1"

FAKE_HOST = "AABBCCDDEE000001"                         # never a real device
FAKE_ARR = "AABBCCDDEE000002"
ALIAS_H, ALIAS_A = "zz_probe_h", "zz_probe_a"
ZONE = f"{ALIAS_H}_{ALIAS_A}"


def main() -> int:
    if not SW_PW:
        print("Set SW_PW (and optionally SW_HOST/SW_USER) in the environment first.")
        return 2

    creds = EndpointCreds(host=SW_HOST, username=SW_USER, password=SW_PW)
    print(f"Switch: {SW_HOST}   mode: {'WRITE (staged only, never activated)' if WRITE else 'READ-ONLY preview'}")

    # 1) Read-only: the live effective cfg + a leftover check from a previous run.
    with BrocadeClient(SW_HOST, SW_USER, SW_PW) as sw:
        cfg_text = sw.cfgshow()
        active_cfg = parse_active_cfg(cfg_text)
        leftovers = [n for n in (ALIAS_H, ALIAS_A, ZONE) if n in cfg_text]
        print(f"Effective cfg: {active_cfg or '(none)'}")
        if leftovers:
            print(f"!! zz_probe objects already on the switch from a previous run: {leftovers}")
            print("   Have them removed first (removal commands are printed at the end).")
            _print_removal(active_cfg)
            return 1

    plan = ZoningPlan(fabrics=[FabricZonePlan(
        fabric="F1", switch_host=SW_HOST, active_cfg=active_cfg,
        hosts=[AliasedWwpn(wwpn=FAKE_HOST, display=_colons(FAKE_HOST), role="host",
                           fabric="F1", host_name="zz-probe-host")],
        array_ports=[AliasedWwpn(wwpn=FAKE_ARR, display=_colons(FAKE_ARR), role="array",
                                 fabric="F1", nsp="9:9:9")],
        pairs=[(FAKE_HOST, FAKE_ARR)],
    )])
    aliases = {FAKE_HOST: ALIAS_H, FAKE_ARR: ALIAS_A}
    intent = ProvisioningIntent.from_simple(
        host_set_name="zz", array=EndpointCreds(host="unused", username="u", password="p"),
        vcenter=EndpointCreds(host="unused", username="u", password="p"),
        switch_f1=creds, switch_f2=creds,   # only F1 carries a renderable pair; F2 is never contacted
        name_prefix="zz", size_gib=1,
    )

    if not WRITE:
        print("\nWould stage (via the shipped stage_zones):")
        print(f'  alicreate "{ALIAS_H}","{_colons(FAKE_HOST)}"')
        print(f'  alicreate "{ALIAS_A}","{_colons(FAKE_ARR)}"')
        print(f'  zonecreate "{ZONE}","{ALIAS_H};{ALIAS_A}"')
        if active_cfg:
            print(f'  cfgadd "{active_cfg}","{ZONE}"')
        print("  cfgsave  (answered 'y' — DEFINED config only; cfgenable is never run)")
        print("\nRe-run with WRITE=1 to execute.")
        return 0

    # 2) The shipped write path, end to end.
    result = stage_zones(intent, plan, aliases, [(FAKE_HOST, FAKE_ARR)])
    fr = result.fabrics[0]
    print(f"\nstaged:   {fr.staged}")
    print(f"verified: {fr.verified}")
    print(f"handoff:  {fr.handoff}  (DO NOT RUN — activation stays manual; the members are fake anyway)")
    print(f"error:    {fr.error}")
    if result.warning:
        print(f"warning:  {result.warning}")

    # 3) Independent read-back, outside stage_zones' own verification.
    with BrocadeClient(SW_HOST, SW_USER, SW_PW) as sw:
        after = sw.cfgshow()
        defined = after.split("Effective configuration")[0]
        print(f"\nindependent read-back: zone in DEFINED config: {ZONE in defined}")
        print(f"effective cfg unchanged: {parse_active_cfg(after) == active_cfg}")
        print(f"zone in EFFECTIVE section: {ZONE in after.split('Effective configuration')[-1]} (must be False)")

    _print_removal(active_cfg)
    return 0 if fr.verified else 1


def _print_removal(active_cfg: str) -> None:
    print("\n--- removal (SAN team / manual — this script and the product never delete) ---")
    if active_cfg:
        print(f'  cfgremove "{active_cfg}","{ZONE}"')
    print(f'  zonedelete "{ZONE}"')
    print(f'  alidelete "{ALIAS_H}"')
    print(f'  alidelete "{ALIAS_A}"')
    print("  cfgsave")


def _colons(wwpn: str) -> str:
    return ":".join(wwpn[i:i + 2] for i in range(0, 16, 2)).lower()


if __name__ == "__main__":
    sys.exit(main())
