from __future__ import annotations

from alletra_onboard.domain.models import WorkflowPhase


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
