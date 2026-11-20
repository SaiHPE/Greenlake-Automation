#!/usr/bin/env python3
"""END-TO-END VALIDATION of the provisioning + zoning code against the VZ reference environment.

This drives the **shipped product functions** — not mirrors of them. Every mirror we have ever
written has agreed with the product right up until the moment it didn't (see docs/LESSONS.md 28:
`ensure_volume` sent a body no Alletra MP has ever accepted, and every fake-based test passed).

Run it ON THE VZ JUMP BOX (10.54.122.137). vCenter lives on the isolated 10.99.1.x vault VLAN and
is unreachable from anywhere else, and discovery cannot complete without it.

    git clone https://github.hpe.com/g-sai-roopesh/greenlake-automation
    pip install pydantic paramiko pyvmomi "python-3parclient>=4.2.14"
    cd Greenlake-Automation/Provisioning_Automation/alletra_onboard
    set PYTHONPATH=src
    python -u scripts/validation/vz_validate.py

Phases 1-5 and 7 are READ-ONLY. Phase 6 writes to the array. The switches are only ever read.
Opt in explicitly:

    WRITE=1        phase 6 - create zz_val_* objects on the array (nothing existing is touched)

NOTHING IS EVER DELETED. The zz_val_* objects are left in place for inspection; remove them with
scripts/provisioning/ui_prov_teardown.py when you are done (it is prefix-guarded).
"""

from __future__ import annotations

import os
import sys
import traceback

# --------------------------------------------------------------------------- config (env-overridable)
# This repository is PUBLIC. Passwords are REQUIRED from the environment and have no defaults here
# — never add one, not even a vendor default (docs/LESSONS.md 21).


def _secret(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        sys.exit(f"Set ${name}. Credentials are never stored in this repository.\n"
                 f"Required: $ARRAY_PW, $VC_PW, $SW_PW")
    return value


ARRAY_IP   = os.environ.get("ARRAY_IP", "10.64.122.140")        # MPB10K-D24U21-VZ
ARRAY_USER = os.environ.get("ARRAY_USER", "3paradm")
ARRAY_PW   = _secret("ARRAY_PW")
VC_IP      = os.environ.get("VC_IP", "10.99.1.100")             # CRV-VZ-VC (vault VLAN)
VC_USER    = os.environ.get("VC_USER", "administrator@vsphere.local")
VC_PW      = _secret("VC_PW")
SW1_IP     = os.environ.get("SW1_IP", "10.64.122.146")          # VZ-SAN-F1 (odd)
SW2_IP     = os.environ.get("SW2_IP", "10.64.122.145")          # VZ-SAN-F2 (even)
SW_USER    = os.environ.get("SW_USER", "admin")
SW_PW      = _secret("SW_PW")
CPG        = os.environ.get("CPG", "SSD_r6")

DO_WRITE = os.environ.get("WRITE") == "1"

PREFIX = "zz_val"          # every object this script may create starts here
TEST_LUN = int(os.environ.get("TEST_LUN", "250"))

from alletra_onboard.domain.shared import EndpointCreds                      # noqa: E402
from alletra_onboard.domain.provisioning import (                            # noqa: E402
    ExportRequest, HostSetRequest, ProvisioningIntent, VolumeRequest,
)
from alletra_onboard.application.provisioning import apply as prov_apply      # noqa: E402
from alletra_onboard.application.provisioning import discovery as disc       # noqa: E402
from alletra_onboard.application.provisioning import path_verify             # noqa: E402
from alletra_onboard.application.provisioning import preflight               # noqa: E402
from alletra_onboard.application.provisioning import storage_provision as prov  # noqa: E402
from alletra_onboard.application.provisioning import zoning                  # noqa: E402
from alletra_onboard.application.provisioning import zoning_plan             # noqa: E402

results: list[tuple[str, str, str]] = []      # (phase, PASS/FAIL/SKIP, detail)


def head(n: str) -> None:
    print("\n" + "=" * 78); print(n); print("=" * 78)


def record(phase: str, ok: bool | None, detail: str = "") -> None:
    status = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
    results.append((phase, status, detail))
    print(f"\n   >>> {phase}: {status} {detail}")


def creds(host: str, user: str, pw: str) -> EndpointCreds:
    return EndpointCreds(host=host, username=user, password=pw)


def make_intent() -> ProvisioningIntent:
    """Two volumes exercising BOTH provisioning types, one host set over the discovered hosts, and
    two exports covering both source kinds and both LUN modes."""
    return ProvisioningIntent(
        array=creds(ARRAY_IP, ARRAY_USER, ARRAY_PW),
        vcenter=creds(VC_IP, VC_USER, VC_PW),
        switch_f1=creds(SW1_IP, SW_USER, SW_PW),
        switch_f2=creds(SW2_IP, SW_USER, SW_PW),
        volumes=[
            VolumeRequest(name=f"{PREFIX}_vol_thin", size_gib=1, provisioning_type="tpvv",
                          cpg=CPG, vvset=f"{PREFIX}_vvset"),
            VolumeRequest(name=f"{PREFIX}_vol_reduce", size_gib=1, provisioning_type="reduce", cpg=CPG),
        ],
        host_sets=[HostSetRequest(name=f"{PREFIX}_hostset", members=[])],   # [] => all discovered
        exports=[
            ExportRequest(source_kind="vvset", source_name=f"{PREFIX}_vvset",
                          target_kind="hostset", target_name=f"{PREFIX}_hostset", lun=TEST_LUN),
            ExportRequest(source_kind="volume", source_name=f"{PREFIX}_vol_reduce",
                          target_kind="hostset", target_name=f"{PREFIX}_hostset", lun=None),  # auto
        ],
    )


def guard(intent: ProvisioningIntent) -> None:
    """Fail closed: refuse to run the write phase if anything to be CREATED is not a throwaway."""
    names = [v.name for v in intent.volumes] + [hs.name for hs in intent.host_sets]
    names += [v.vvset for v in intent.volumes if v.vvset]
    bad = [n for n in names if not n.startswith(PREFIX)]
    if bad:
        sys.exit(f"REFUSING TO WRITE: non-throwaway names in the intent: {bad}")


# =========================================================================== phases
def phase_preflight(intent):
    head("PHASE 1 - readiness preflight (READ-ONLY)  [preflight.run_preflight]")
    rep = preflight.run_preflight(intent)
    for c in rep.checks:
        print(f"   {c.status.upper():5} {c.label:26} {c.detail}")
    record("1 preflight", rep.ready, f"ready={rep.ready}, {len(rep.checks)} checks")
    return rep


def phase_discovery(intent):
    head("PHASE 2 - discovery (READ-ONLY)  [discovery.discover]")
    rep = disc.discover(intent, progress=lambda m: print(f"   .. {m}"))
    print(f"\n   array_ports={len(rep.array_ports)}  array_hosts={len(rep.array_hosts)}  "
          f"host_hbas={len(rep.host_hbas)}")
    for p in rep.array_ports:
        print(f"      port {p.label:6} {p.protocol:6} {p.link_state:10} fabric={p.fabric} "
              f"switch={p.fabric_switch!r}")
    for h in rep.array_hosts:
        print(f"      array host {h.name:26} persona={h.persona:8} {dict(h.wwpns)}")
    for hba in rep.host_hbas:
        print(f"      vcenter    {hba.host_name:26} {hba.wwpn} fabric={hba.fabric} os={hba.os!r}")
    for n in rep.notes:
        print(f"      NOTE: {n}")
    hosts = {h.host_name for h in rep.host_hbas}
    record("2 discovery", bool(hosts) and not rep.error,
           f"{len(hosts)} vCenter host(s), {len(rep.array_ports)} port(s); error={rep.error}")
    return rep


def phase_zoning_verify(intent, discovery):
    head("PHASE 3 - zoning VERIFY, array-side compute only  [zoning.build_report]")
    rep = zoning.build_report(intent, discovery)
    print(f"   {rep.model_dump_json(indent=2)[:2500]}")
    # `error is None` is NOT success: build_report degrades gracefully and reports why in notes.
    # An empty report with "run Discovery first" is a non-answer, not a pass.
    answered = bool(rep.expected)
    record("3 zoning verify", answered,
           f"{len(rep.expected)} expected host(s), proper={rep.proper}"
           + ("" if answered else "  <-- produced no answer; see notes"))
    return rep


def phase_zoning_plan(intent, discovery):
    head("PHASE 4 - zoning PLAN, reads BOTH switches READ-ONLY  [zoning_plan.build_zoning_plan]")
    plan = zoning_plan.build_zoning_plan(intent, discovery)
    print(f"   {plan.model_dump_json(indent=2)[:4000]}")
    # CRITICAL: an empty plan because everything is already zoned looks IDENTICAL to an empty plan
    # because the switch could not be read. Only the second is a failure, and `error` is None for
    # both — the reason lives in notes/active_cfg. Never treat "empty" as "nothing to do" without
    # first proving both fabrics were actually read.
    unread = [f.fabric for f in plan.fabrics if not f.active_cfg]
    if unread:
        record("4 zoning plan", False,
               f"fabric(s) {unread} were NOT READ (no active cfg) — the empty plan is a non-answer, "
               f"not 'nothing to do'. notes={plan.notes}")
    else:
        record("4 zoning plan", True,
               f"both fabrics read (cfgs: {[f.active_cfg for f in plan.fabrics]}); "
               f"{sum(len(f.pairs) for f in plan.fabrics)} pair(s) proposed — on the fully-zoned VZ "
               f"the correct answer is 0")
    return plan


def phase_preview(intent, discovery, reachable_hosts):
    head("PHASE 5 - tier-1 PREVIEW (READ-ONLY)  [storage_provision.build_plan]")
    plan = prov.build_plan(intent, discovery, reachable_hosts=reachable_hosts)
    for a in plan.actions:
        print(f"   {a.kind:8} {a.name:24} exists={str(a.exists):5} {a.description}")
    for n in plan.notes:
        print(f"   NOTE: {n}")
    record("5 tier-1 preview", plan.error is None,
           f"{len(plan.actions)} action(s); error={plan.error}")
    return plan


def phase_apply(intent, discovery, reachable_hosts, plan):
    head("PHASE 6 - tier-1 APPLY *** WRITES TO THE ARRAY ***  [provisioning.apply.apply_plan]")
    guard(intent)
    from alletra_onboard.domain.approval import Approval

    approval = Approval("validation", "storage", {"A": intent.array}, save_record=lambda _m: None)
    res = prov_apply.apply_plan(prov_apply.StorageInputs(intent, discovery, reachable_hosts, plan), approval)
    for o in res.outcomes:
        print(f"   {o.kind:8} {o.name:24} -> {o.status:8} {o.detail}")
    failed = [o for o in res.outcomes if o.status == "failed"]
    record("6 tier-1 apply", res.error is None and not failed,
           f"{len(res.outcomes)} outcome(s), {len(failed)} failed; error={res.error}")
    return res


def phase_paths(intent, discovery, reachable_hosts):
    head("PHASE 7 - tier-2 PATH VERIFY (READ-ONLY)  [path_verify.verify_provisioned_paths]")
    rep = path_verify.verify_provisioned_paths(intent, discovery, reachable_hosts=reachable_hosts)
    for h in rep.hosts:
        print(f"   {h.host:26} {h.verdict:8} hbas={h.hbas_with_paths} fabrics={h.fabrics}")
        print(f"        {h.detail}")
    for n in rep.notes:
        print(f"   NOTE: {n}")
    live = sum(1 for h in rep.hosts if h.verdict == "live")
    record("7 tier-2 paths", rep.error is None and live == len(rep.hosts) and bool(rep.hosts),
           f"{live}/{len(rep.hosts)} host(s) live on both fabrics; error={rep.error}")
    return rep


# =========================================================================== main
def main() -> int:
    # Print every resolved target INCLUDING usernames. These come from the environment, and a shell
    # that ran an earlier probe will still carry its variables — a stale $SW_USER/$SW1_IP silently
    # points this harness at the wrong fabric and every result becomes meaningless.
    print("VZ VALIDATION — resolved targets (override via environment):")
    print(f"   array    {ARRAY_USER}@{ARRAY_IP}   cpg={CPG}")
    print(f"   vcenter  {VC_USER}@{VC_IP}")
    print(f"   switches {SW_USER}@{SW1_IP} (F1) / {SW_USER}@{SW2_IP} (F2)")
    print(f"   WRITE={DO_WRITE}  prefix={PREFIX}  test LUN={TEST_LUN}")
    if VC_IP.startswith("10.99.") :
        print("   NOTE: vCenter is on the isolated vault VLAN — this must run on the VZ jump box.")
    intent = make_intent()

    discovery = None
    for name, fn in (("preflight", lambda: phase_preflight(intent)),
                     ("discovery", lambda: phase_discovery(intent))):
        try:
            out = fn()
            if name == "discovery":
                discovery = out
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            record(f"{name}", False, f"EXCEPTION {type(exc).__name__}: {exc}")

    if discovery is None:
        print("\nDiscovery failed — the remaining phases need it. Stopping.")
    else:
        zoning_rep = None
        reachable = set() if DO_WRITE else {h.host_name for h in discovery.host_hbas}
        try:
            zoning_rep = phase_zoning_verify(intent, discovery)
            if zoning_rep.zoned_hosts:
                reachable = set(zoning_rep.zoned_hosts)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            record("3 zoning verify", False, f"EXCEPTION {type(exc).__name__}: {exc}")

        preview_plan = None
        try:
            phase_zoning_plan(intent, discovery)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            record("4 zoning plan", False, f"EXCEPTION {type(exc).__name__}: {exc}")
        try:
            preview_plan = phase_preview(intent, discovery, reachable)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            record("5 preview", False, f"EXCEPTION {type(exc).__name__}: {exc}")

        if DO_WRITE:
            if preview_plan is None:
                record("6 tier-1 apply", False, "skipped — preview did not produce a plan")
            else:
                for name, fn in (("6 apply", lambda: phase_apply(intent, discovery, reachable, preview_plan)),
                                 ("7 paths", lambda: phase_paths(intent, discovery, reachable))):
                    try:
                        fn()
                    except Exception as exc:  # noqa: BLE001
                        traceback.print_exc()
                        record(name, False, f"EXCEPTION {type(exc).__name__}: {exc}")
        else:
            record("6 tier-1 apply", None, "set WRITE=1 to run")
            record("7 tier-2 paths", None, "set WRITE=1 to run (needs the applied export)")

    head("SUMMARY")
    for phase, status, detail in results:
        print(f"   {status:5} {phase:22} {detail}")
    failed = [r for r in results if r[1] == "FAIL"]
    print(f"\n   {len(failed)} FAILED, "
          f"{sum(1 for r in results if r[1] == 'PASS')} passed, "
          f"{sum(1 for r in results if r[1] == 'SKIP')} skipped")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
