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
    # "Verify configuration", not "…& health": the HPE Design System prohibits "health" in UI copy —
    # always "status". This label is served to the UI, so this is the only place it is spelled.
    StepDef("verify", "Verify configuration", WorkflowPhase.CONFIG_VERIFY, "verify"),
    StepDef("asbuilt", "As-built document", WorkflowPhase.ASBUILT_DOCUMENT, "verify"),
)

# Preset modes -> the step keys they include. CUSTOM uses the explicit selection instead.
_MODE_STEPS: dict[RunMode, tuple[str, ...]] = {
    RunMode.FULL_ONBOARDING: ("greenlake", "cloudinit", "dscc", "verify", "asbuilt"),
    RunMode.PROVISION_ONLY: ("discover", "zoning", "provision", "verify", "asbuilt"),
    RunMode.BOTH: ("greenlake", "cloudinit", "dscc", "discover", "zoning", "provision", "verify", "asbuilt"),
    RunMode.VERIFY_ONLY: ("verify", "asbuilt"),
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
