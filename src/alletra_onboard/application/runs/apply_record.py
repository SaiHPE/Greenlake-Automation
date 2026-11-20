"""In-progress apply records (STANDARD S5, ADR 0031 Stage 3).

Every array write puts an inspect-first note on record in the run's store before sending and
replaces it with the confirmed removal set once the write returns. Reopening an interrupted run
promotes any unclosed record to the step's existing `*.apply.failed` / `failover.failed` event.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from pydantic import BaseModel

from alletra_onboard.domain.approval import Purpose, SaveRecord
from alletra_onboard.domain.models import WorkflowPhase
from alletra_onboard.domain.provisioning import ProvisioningResult
from alletra_onboard.domain.replication import ReplicationResult
from alletra_onboard.domain.snapshots import SnapshotResult

APPLY_RECORD_ARTIFACT = "apply_in_progress"
INTERRUPTED_APPLY_ERROR = (
    "Apply was interrupted before it finished. Inspect the array before retrying; "
    "the removal set and notes below record what was confirmed or in flight."
)
ApplyResult = ProvisioningResult | ReplicationResult | SnapshotResult

# Maps each failure event recorded in-flight to (phase, success_event, payload_key).
APPLY_RECORDS: dict[str, tuple[WorkflowPhase, str, str]] = {
    "storage.apply.failed": (WorkflowPhase.STORAGE_PROVISION, "storage.applied", "result"),
    "replication.apply.failed": (WorkflowPhase.STORAGE_REPLICATE, "replication.applied", "result"),
    "snapshots.apply.failed": (WorkflowPhase.STORAGE_SNAPSHOT, "snapshots.applied", "result"),
    "failover.failed": (WorkflowPhase.STORAGE_FAILOVER_TEST, "failover.completed", "record"),
}
PURPOSE_EVENT: dict[Purpose, str] = {
    "storage": "storage.apply.failed",
    "rc_groups": "replication.apply.failed",
    "rc_partnership": "replication.apply.failed",
    "snapshots": "snapshots.apply.failed",
    "failover": "failover.failed",
}
TERMINAL_APPLY_EVENTS = frozenset({*APPLY_RECORDS, *(ok for _ph, ok, _k in APPLY_RECORDS.values())})


def try_save_record(save: SaveRecord, model: BaseModel) -> str | None:
    """Save an in-progress record without raising on store failures; returns error text on failure."""
    try:
        save(model)
    except (sqlite3.Error, OSError, RuntimeError, ValueError) as exc:
        return str(exc)
    return None


def maybe_made(what: str, check: str, remove: str = "") -> str:
    """SPEC-007 R6 / STANDARD S5 inspect-first wording for a write in flight."""
    if remove:
        return (f"The array may have made {what} before the error. If `{check}` lists it and it was not there "
                f"before this run, `{remove}` removes it.")
    return f"The array may have changed {what} before the error. Inspect with `{check}` first."


@contextmanager
def recorded_write(result: ApplyResult, note: str, save: SaveRecord) -> Iterator[None]:
    """Save an inspect-first note before a write; on clean exit drop it and save the confirmed result."""
    (result.notes if isinstance(result, ReplicationResult) else result.removal_notes).append(note)
    save(result)
    yield
    notes = result.notes if isinstance(result, ReplicationResult) else result.removal_notes
    if note in notes:
        notes.remove(note)
    save(result)
