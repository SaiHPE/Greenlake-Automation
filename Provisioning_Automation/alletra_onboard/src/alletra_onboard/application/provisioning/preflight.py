"""Read-only readiness preflight for a provisioning run.

Runs BEFORE discovery, so a missing prerequisite is named plainly — "the array's WSAPI is not
reachable", "CPG SSD_r6 is not on this array", "vCenter reports no ESXi hosts" — instead of
surfacing later as a failed step with a stack of events for the operator to decode.

Every check is a fixed query with a fixed verdict. **Nothing here writes to the array**: the
subscription gate (an array that has not completed GreenLake onboarding refuses to create
volumes) is deliberately NOT probed with a throwaway volume — it is translated where it
actually surfaces, in the apply step's error handling.

`fail` means the run cannot succeed as configured. `warn` means proceed with your eyes open.
"""

from __future__ import annotations

from typing import Callable

from alletra_onboard.application.provisioning.clients import make_vcenter, make_wsapi
from alletra_onboard.domain.provisioning import PreflightCheck, PreflightReport, ProvisioningIntent

# The array reports linkState as the WSAPI enum (4 = ready); tolerate a textual form too.
_READY_LINK_STATES = {"4", "ready"}


def _cpg_check(intent: ProvisioningIntent, free_by_cpg: dict[str, int]) -> PreflightCheck:
    """Every CPG the sheet's volumes name must exist. Capacity is a WARNING, not a failure: thin and
    data-reduction volumes do not consume their nominal size up front, so a request larger than the
    current free space is legitimate and the array will accept it."""
    wanted: dict[str, int] = {}
    for volume in intent.volumes:
        wanted[volume.cpg] = wanted.get(volume.cpg, 0) + volume.size_mib

    missing = sorted(cpg for cpg in wanted if cpg not in free_by_cpg)
    if missing:
        available = ", ".join(sorted(free_by_cpg)) or "none"
        return PreflightCheck(
            key="cpg", label="Provisioning groups", status="fail",
            detail=f"Not on this array: {', '.join(missing)}. Available: {available}.",
        )

    tight = [
        f"{cpg} requests {wanted[cpg]} MiB against {free_by_cpg[cpg]} MiB free"
        for cpg in sorted(wanted) if free_by_cpg[cpg] < wanted[cpg]
    ]
    if tight:
        return PreflightCheck(
            key="cpg", label="Provisioning groups", status="warn",
            detail="Thin provisioning allows this, but capacity is short: " + "; ".join(tight),
        )
    return PreflightCheck(
        key="cpg", label="Provisioning groups", status="pass",
        detail=", ".join(f"{cpg} ({free_by_cpg[cpg]} MiB free)" for cpg in sorted(wanted)) or "none requested",
    )


def _names_check(intent: ProvisioningIntent, existing: set[str]) -> PreflightCheck:
    """Names the run will create that are already on the array. A WARNING, not a failure — apply is
    idempotent and reports such objects as 'exists' — but the operator should know before previewing."""
    planned = [v.name for v in intent.volumes]
    planned += [hs.name for hs in intent.host_sets]
    planned += sorted({v.vvset for v in intent.volumes if v.vvset})

    clash = sorted(name for name in planned if name in existing)
    if clash:
        return PreflightCheck(
            key="names", label="Object names", status="warn",
            detail=f"Already on the array, so they will be reused rather than created: {', '.join(clash)}.",
        )
    return PreflightCheck(
        key="names", label="Object names", status="pass",
        detail=f"{len(planned)} name(s) free on this array.",
    )


def _ports_check(ports: list) -> PreflightCheck:
    ready = [p for p in ports if str(getattr(p, "link_state", "")).lower() in _READY_LINK_STATES]
    if not ports:
        return PreflightCheck(
            key="ports", label="Array FC ports", status="fail",
            detail="The array reports no FC target ports — hosts cannot be served over FC.",
        )
    if not ready:
        return PreflightCheck(
            key="ports", label="Array FC ports", status="fail",
            detail=f"None of the {len(ports)} FC target port(s) has a ready link.",
        )
    fabrics = sorted({getattr(p, "fabric", "") for p in ready if getattr(p, "fabric", "")})
    detail = f"{len(ready)} of {len(ports)} FC target port(s) ready"
    if fabrics:
        detail += f" across {', '.join(fabrics)}"
    return PreflightCheck(key="ports", label="Array FC ports", status="pass", detail=detail + ".")


def _vcenter_check(intent: ProvisioningIntent, vcenter_factory: Callable) -> PreflightCheck:
    """vCenter is the only source of host HBAs, and the apply step refuses to provision with zero
    discovered hosts — so an empty host list is a failure, not a warning."""
    try:
        with vcenter_factory(intent.vcenter) as vcenter:
            hbas = vcenter.host_fc_hbas()
    except Exception as exc:  # noqa: BLE001 - report it, never raise out of a preflight
        return PreflightCheck(
            key="vcenter", label="vCenter", status="fail",
            detail=f"Could not reach vCenter {intent.vcenter.host}: {exc}",
        )

    hosts = sorted({hba.host_name for hba in hbas if hba.host_name})
    if not hosts:
        return PreflightCheck(
            key="vcenter", label="vCenter", status="fail",
            detail="vCenter reports no ESXi host HBAs — provisioning refuses to run with no hosts.",
        )
    return PreflightCheck(
        key="vcenter", label="vCenter", status="pass",
        detail=f"{len(hosts)} ESXi host(s) with FC HBAs: {', '.join(hosts)}.",
    )


def run_preflight(
    intent: ProvisioningIntent,
    *,
    wsapi_factory: Callable = make_wsapi,
    vcenter_factory: Callable = make_vcenter,
) -> PreflightReport:
    """Check every prerequisite the run depends on, read-only. Independent of discovery by design —
    this is what tells the operator *why* discovery would fail."""
    checks: list[PreflightCheck] = []

    try:
        with wsapi_factory(intent.array) as array:
            system = array.system_name()
            free_by_cpg = array.cpg_free_mib()
            existing = (
                set(array.host_names()) | set(array.host_set_names())
                | set(array.volume_names()) | set(array.volume_set_names())
            )
            ports = array.array_fc_ports()
    except Exception as exc:  # noqa: BLE001
        checks.append(PreflightCheck(
            key="array", label="Array management API", status="fail",
            detail=f"Could not reach {intent.array.host} over WSAPI: {exc}",
        ))
        # The array answers three of the five checks; without it they are unknowable, so report
        # vCenter (independently reachable) and stop rather than guessing.
        checks.append(_vcenter_check(intent, vcenter_factory))
        return PreflightReport.of(checks)

    checks.append(PreflightCheck(
        key="array", label="Array management API", status="pass",
        detail=f"Connected to {system or intent.array.host} over WSAPI.",
    ))
    checks.append(_cpg_check(intent, free_by_cpg))
    checks.append(_names_check(intent, existing))
    checks.append(_ports_check(ports))
    checks.append(_vcenter_check(intent, vcenter_factory))
    return PreflightReport.of(checks)
