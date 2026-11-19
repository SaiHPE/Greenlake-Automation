from __future__ import annotations

from dataclasses import dataclass

from alletra_onboard.domain.models import RunMode, WorkflowPhase


@dataclass(frozen=True)
class StepDef:
    """One operator-facing step. The single source of truth for step identity + order.

    `key` is the stable id the frontend and `RunRecord.selected_steps` use. `phase` is the phase the
    run lands on when this step is the active one (so resume maps a persisted phase back to a step).
    `kind` groups steps: 'init' (the A->B->C onboarding), 'provision' (storage, Phase 2), 'replicate'
    (Remote Copy to a peer array — needs the Replication tab), 'migrate' (Peer Motion from a source
    array — needs the Migration tab), 'snapshot' (snapshots and a schedule — needs the Snapshots tab),
    'verify'. `lab_script` is the file in lab/ that drives this step live on lab hardware; when no
    script does, it is None and `no_lab_script` says why (docs/STANDARD.md X4). Neither is served to
    the frontend.
    """

    key: str
    label: str
    phase: WorkflowPhase
    kind: str
    lab_script: str | None
    no_lab_script: str = ""

    def __post_init__(self) -> None:
        if bool(self.lab_script) == bool(self.no_lab_script):
            raise ValueError(f"step {self.key}: name the lab script that drives it, or say why there is none")


# Ordered registry — drives both the wizard step list and the service's advance logic.
STEP_REGISTRY: tuple[StepDef, ...] = (
    StepDef("greenlake", "GreenLake registration", WorkflowPhase.PREFLIGHT, "init", "init_walk_lab.py"),
    StepDef("cloudinit", "Cloud Connectivity", WorkflowPhase.CLOUDINIT_CONNECT, "init", "init_walk_lab.py"),
    StepDef("dscc", "DSCC Setup", WorkflowPhase.DSCC_SETUP_SYSTEM, "init", "init_walk_lab.py"),
    StepDef("discover", "Discovery", WorkflowPhase.STORAGE_DISCOVER, "provision", "ui_live_lab.py"),
    # SPEC-024 R8: before zoning, because the zoning check is what sees an iSCSI host's login on the
    # address this step sets up. One step for every array-port feature, a section each (SPEC-025).
    StepDef("ports", "Array ports", WorkflowPhase.STORAGE_PORTS, "provision", None,
            "ui_live_lab.py opens its plan; no lab script applies one"),
    StepDef("zoning", "SAN Zoning", WorkflowPhase.STORAGE_ZONING, "provision", "ui_live_lab.py"),
    StepDef("migrate", "Migration", WorkflowPhase.STORAGE_MIGRATE, "migrate", None, "the step is not built yet"),
    StepDef("provision", "Provision storage", WorkflowPhase.STORAGE_PROVISION, "provision", "ui_provision_lab.py"),
    StepDef("replicate", "Replication", WorkflowPhase.STORAGE_REPLICATE, "replicate", "rcip_tool_lab.py"),
    StepDef("failover_test", "Failover test", WorkflowPhase.STORAGE_FAILOVER_TEST, "replicate", "rc_failover_lab.py"),
    # SPEC-023 R9: picked in Custom only; the presets are unchanged.
    StepDef("snapshots", "Snapshots", WorkflowPhase.STORAGE_SNAPSHOT, "snapshot", None,
            "snap_capture.py reads what the array holds; no lab script drives the step"),
    # "Verify configuration", not "…& health": the HPE Design System prohibits "health" in UI copy —
    # always "status". This label is served to the UI, so this is the only place it is spelled.
    StepDef("verify", "Verify configuration", WorkflowPhase.CONFIG_VERIFY, "verify", "ui_live_lab.py"),
    StepDef("asbuilt", "As-built document", WorkflowPhase.ASBUILT_DOCUMENT, "verify", "ui_live_lab.py"),
)

# Preset modes -> the step keys they include. CUSTOM uses the explicit selection instead.
_MODE_STEPS: dict[RunMode, tuple[str, ...]] = {
    RunMode.FULL_ONBOARDING: ("greenlake", "cloudinit", "dscc", "verify", "asbuilt"),
    RunMode.PROVISION_ONLY: ("discover", "ports", "zoning", "provision", "verify", "asbuilt"),
    RunMode.BOTH: ("greenlake", "cloudinit", "dscc", "discover", "ports", "zoning", "provision", "verify", "asbuilt"),
    RunMode.REPLICATE: ("discover", "ports", "zoning", "provision", "replicate", "failover_test", "verify", "asbuilt"),
    # Peer Motion creates the hosts and volumes on this array, so there is no Provision step (SPEC-027 R3).
    RunMode.MIGRATE: ("discover", "zoning", "migrate", "verify", "asbuilt"),
    RunMode.VERIFY_ONLY: ("verify", "asbuilt"),
}

#: Steps that exist only when the workbook carries the Replication tab (SPEC-015 R4).
REPLICATION_STEP_KEYS: frozenset[str] = frozenset(step.key for step in STEP_REGISTRY if step.kind == "replicate")

#: Registry steps whose work is not built yet -> the sentence the operator sees. A run that includes
#: one is refused when it is minted, and the UI shows its mode as unavailable with this sentence.
#: Remove the entry in the change that builds the step.
NOT_BUILT_STEPS: dict[str, str] = {
    "migrate": "The Migration step is not built yet.",
}


def mode_steps() -> dict[RunMode, tuple[str, ...]]:
    """The preset mode → step-keys map, for serving to the frontend (ADR 0011 Phase 2 — the UI
    renders the wizard from this instead of keeping a hand-synced mirror)."""
    return dict(_MODE_STEPS)


def enabled_steps(mode: RunMode, selected_steps: list[str] | None = None) -> list[StepDef]:
    """The steps to render/run for a mode, in registry order. CUSTOM honours selected_steps."""
    if mode == RunMode.CUSTOM:
        chosen = set(selected_steps or ())
    else:
        chosen = set(_MODE_STEPS.get(mode, _MODE_STEPS[RunMode.FULL_ONBOARDING]))
    return [step for step in STEP_REGISTRY if step.key in chosen]


def initial_phase(mode: RunMode, selected_steps: list[str] | None = None) -> WorkflowPhase:
    """The phase a freshly-created run of this mode should land on (its first enabled step)."""
    steps = enabled_steps(mode, selected_steps)
    return steps[0].phase if steps else WorkflowPhase.PREFLIGHT


def next_enabled_phase(
    mode: RunMode,
    selected_steps: list[str] | None,
    after_key: str,
    *,
    fallback: WorkflowPhase = WorkflowPhase.COMPLETE,
) -> WorkflowPhase:
    """The phase to advance to after the `after_key` init step finishes, honouring the selection.

    Only considers 'init' steps (the auto-advancing A->B->C chain); 'provision'/'verify' steps are
    triggered explicitly by the operator, so they are not part of this chain.
    """
    steps = [step for step in enabled_steps(mode, selected_steps) if step.kind == "init"]
    keys = [step.key for step in steps]
    if after_key in keys:
        index = keys.index(after_key)
        if index + 1 < len(steps):
            return steps[index + 1].phase
    return fallback
