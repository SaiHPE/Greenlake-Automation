from alletra_onboard.domain.models import RunMode, WorkflowPhase
from alletra_onboard.domain.workflow import (
    enabled_steps,
    initial_phase,
    next_enabled_phase,
    next_phase,
)


def test_skips_storage_fleet_when_disabled():
    assert next_phase(WorkflowPhase.DSCC_SETUP_SYSTEM, storage_fleet_enabled=False) == WorkflowPhase.COMPLETE


def test_uses_storage_fleet_when_enabled():
    assert next_phase(WorkflowPhase.DSCC_SETUP_SYSTEM, storage_fleet_enabled=True) == WorkflowPhase.STORAGE_FLEET_VERIFY


# ---------------------------------------------------------------- decoupling: modes -> steps

def _keys(mode, selected=None):
    return [s.key for s in enabled_steps(mode, selected)]


def test_full_onboarding_steps_in_registry_order():
    assert _keys(RunMode.FULL_ONBOARDING) == ["greenlake", "cloudinit", "dscc", "verify"]


def test_provision_only_excludes_init_steps():
    assert _keys(RunMode.PROVISION_ONLY) == ["discover", "zoning", "provision", "verify"]


def test_verify_only_is_just_verify():
    assert _keys(RunMode.VERIFY_ONLY) == ["verify"]


def test_custom_honours_explicit_selection_in_registry_order():
    # order follows the registry regardless of how the operator listed them
    assert _keys(RunMode.CUSTOM, ["verify", "greenlake"]) == ["greenlake", "verify"]


def test_initial_phase_is_first_enabled_step():
    assert initial_phase(RunMode.FULL_ONBOARDING) == WorkflowPhase.PREFLIGHT
    assert initial_phase(RunMode.PROVISION_ONLY) == WorkflowPhase.STORAGE_DISCOVER
    assert initial_phase(RunMode.VERIFY_ONLY) == WorkflowPhase.CONFIG_VERIFY


def test_next_enabled_phase_follows_init_chain():
    # full onboarding: greenlake -> cloudinit -> dscc
    assert next_enabled_phase(RunMode.FULL_ONBOARDING, [], "greenlake") == WorkflowPhase.CLOUDINIT_CONNECT
    assert next_enabled_phase(RunMode.FULL_ONBOARDING, [], "cloudinit") == WorkflowPhase.DSCC_SETUP_SYSTEM


def test_next_enabled_phase_skips_deselected_init_step():
    # a custom run that drops cloudinit: greenlake advances straight to dscc
    custom = ["greenlake", "dscc"]
    assert next_enabled_phase(RunMode.CUSTOM, custom, "greenlake") == WorkflowPhase.DSCC_SETUP_SYSTEM


def test_next_enabled_phase_falls_back_to_complete_when_no_more_init():
    assert next_enabled_phase(RunMode.CUSTOM, ["greenlake"], "greenlake") == WorkflowPhase.COMPLETE
