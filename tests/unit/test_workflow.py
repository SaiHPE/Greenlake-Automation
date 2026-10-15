from alletra_onboard.domain.models import RunMode, WorkflowPhase
from alletra_onboard.domain.workflow import (
    REPLICATION_STEP_KEYS,
    STEP_REGISTRY,
    enabled_steps,
    initial_phase,
    next_enabled_phase,
)

# ---------------------------------------------------------------- decoupling: modes -> steps

def _keys(mode, selected=None):
    return [s.key for s in enabled_steps(mode, selected)]


def test_full_onboarding_steps_in_registry_order():
    assert _keys(RunMode.FULL_ONBOARDING) == ["greenlake", "cloudinit", "dscc", "verify", "asbuilt"]


def test_provision_only_excludes_init_steps():
    assert _keys(RunMode.PROVISION_ONLY) == ["discover", "zoning", "provision", "verify", "asbuilt"]


def test_verify_only_is_verify_then_asbuilt():
    assert _keys(RunMode.VERIFY_ONLY) == ["verify", "asbuilt"]


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


# ---------------------------------------------------------------- SPEC-015 R4: replication steps

def test_replicate_preset_runs_provisioning_then_replication_then_documents():
    assert _keys(RunMode.REPLICATE) == [
        "discover", "zoning", "provision", "replicate", "failover_test", "verify", "asbuilt",
    ]
    assert initial_phase(RunMode.REPLICATE) == WorkflowPhase.STORAGE_DISCOVER


def test_replication_steps_have_their_own_kind_and_phases():
    by_key = {s.key: s for s in STEP_REGISTRY}
    assert by_key["replicate"].kind == "replicate" and by_key["replicate"].phase == WorkflowPhase.STORAGE_REPLICATE
    assert by_key["failover_test"].kind == "replicate" and by_key["failover_test"].phase == WorkflowPhase.STORAGE_FAILOVER_TEST
    assert REPLICATION_STEP_KEYS == {"replicate", "failover_test"}
    # Existing presets are untouched: no replication step sneaks into BOTH or PROVISION_ONLY.
    assert not REPLICATION_STEP_KEYS & set(_keys(RunMode.BOTH))
    assert not REPLICATION_STEP_KEYS & set(_keys(RunMode.PROVISION_ONLY))


def test_custom_can_pick_replication_steps_in_registry_order():
    assert _keys(RunMode.CUSTOM, ["failover_test", "replicate", "provision"]) == ["provision", "replicate", "failover_test"]
