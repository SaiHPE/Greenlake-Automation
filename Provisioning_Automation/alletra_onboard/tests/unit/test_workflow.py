from alletra_onboard.domain.models import WorkflowPhase
from alletra_onboard.domain.workflow import next_phase


def test_skips_storage_fleet_when_disabled():
    assert next_phase(WorkflowPhase.DSCC_SETUP_SYSTEM, storage_fleet_enabled=False) == WorkflowPhase.COMPLETE


def test_uses_storage_fleet_when_enabled():
    assert next_phase(WorkflowPhase.DSCC_SETUP_SYSTEM, storage_fleet_enabled=True) == WorkflowPhase.STORAGE_FLEET_VERIFY
