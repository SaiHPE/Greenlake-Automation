from __future__ import annotations

from dataclasses import dataclass

from alletra_onboard.domain.models import RunMode, WorkflowPhase


@dataclass(frozen=True)
class StepDef:
    """One operator-facing step. The single source of truth for step identity + order.

    `key` is the stable id the frontend and `RunRecord.selected_steps` use. `phase` is the phase the
    run lands on when this step is the active one (so resume maps a persisted phase back to a step).
    `kind` groups steps: 'init' (the A->B->C onboarding), 'provision' (storage, Phase 2), 'verify'.
    """

    key: str
    label: str
    phase: WorkflowPhase
    kind: str


# Ordered registry — drives both the wizard step list and the service's advance logic.
STEP_REGISTRY: tuple[StepDef, ...] = (
    StepDef("greenlake", "GreenLake registration", WorkflowPhase.PREFLIGHT, "init"),
    StepDef("cloudinit", "Cloud Connectivity", WorkflowPhase.CLOUDINIT_CONNECT, "init"),
    StepDef("dscc", "DSCC Setup", WorkflowPhase.DSCC_SETUP_SYSTEM, "init"),
    StepDef("discover", "Discovery", WorkflowPhase.STORAGE_DISCOVER, "provision"),
    StepDef("zoning", "SAN Zoning", WorkflowPhase.STORAGE_ZONING, "provision"),
    StepDef("provision", "Provision storage", WorkflowPhase.STORAGE_PROVISION, "provision"),
    StepDef("verify", "Verify config & health", WorkflowPhase.CONFIG_VERIFY, "verify"),
)

# Preset modes -> the step keys they include. CUSTOM uses the explicit selection instead.
_MODE_STEPS: dict[RunMode, tuple[str, ...]] = {
    RunMode.FULL_ONBOARDING: ("greenlake", "cloudinit", "dscc", "verify"),
    RunMode.PROVISION_ONLY: ("discover", "zoning", "provision", "verify"),
    RunMode.BOTH: ("greenlake", "cloudinit", "dscc", "discover", "zoning", "provision", "verify"),
    RunMode.VERIFY_ONLY: ("verify",),
}


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


WORKFLOW_ORDER: tuple[WorkflowPhase, ...] = (
    WorkflowPhase.PREFLIGHT,
    WorkflowPhase.GL_DISCOVER_SERVICE,
    WorkflowPhase.GL_ADD_SUBSCRIPTION,
    WorkflowPhase.GL_REGISTER_DEVICE,
    WorkflowPhase.GL_ASSIGN_APPLICATION,
    WorkflowPhase.GL_APPLY_SUBSCRIPTION,
    WorkflowPhase.GL_VERIFY_DEVICE,
    WorkflowPhase.CLOUDINIT_CONNECT,
    WorkflowPhase.DSCC_SETUP_SYSTEM,
    WorkflowPhase.STORAGE_FLEET_VERIFY,
    WorkflowPhase.COMPLETE,
)


def next_phase(current: WorkflowPhase, *, storage_fleet_enabled: bool = False) -> WorkflowPhase:
    if current == WorkflowPhase.NOT_STARTED:
        return WorkflowPhase.PREFLIGHT
    if current == WorkflowPhase.DSCC_SETUP_SYSTEM and not storage_fleet_enabled:
        return WorkflowPhase.COMPLETE
    try:
        return WORKFLOW_ORDER[WORKFLOW_ORDER.index(current) + 1]
    except (ValueError, IndexError):
        return WorkflowPhase.COMPLETE


def is_terminal(phase: WorkflowPhase) -> bool:
    return phase == WorkflowPhase.COMPLETE
