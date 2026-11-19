"""RunCoordinator — the genuinely shared core of every step: run lifecycle, the guarded
background-task spawner, status/phase persistence and event emission (store + SSE fan-out).

Step logic itself lives in the per-context step services (application/onboarding/steps.py,
application/storage/steps.py, application/documents/steps.py); they all compose this coordinator.
"""

from __future__ import annotations

import asyncio
import contextvars
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from uuid import uuid4

from alletra_onboard.adapters import command_log, device_trust
from alletra_onboard.application.runs.event_bus import ConsoleBus, InMemoryEventBus
from alletra_onboard.application.runs.trust import RunTrustBook
from alletra_onboard.config import Settings, load_settings
from alletra_onboard.domain.models import (
    ArrayCredential,
    ArrayWorkItem,
    RunEvent,
    RunMode,
    RunRecord,
    RunStatus,
    WorkflowPhase,
)
from alletra_onboard.domain.ports import RunStore
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.snapshots import SNAPSHOTS_TAB_NEEDED
from alletra_onboard.domain.trust import DevicePin, TrustKind, retrust, retrusted_message
from alletra_onboard.domain.workflow import NOT_BUILT_STEPS, enabled_steps, initial_phase


class RunNotFoundError(LookupError):
    pass


class RunBusyError(RuntimeError):
    """A background step is already executing for this run."""


class StepPreconditionError(RuntimeError):
    """A step was requested before its prerequisite ran (e.g. zoning/provision before discovery)."""


def new_plan_id() -> str:
    return uuid4().hex


def check_approval(approved_plan: str | None, held_plan_id: str) -> None:
    """The apply names the plan the operator ticked (LESSONS 7); the server checks it, not only the
    screen. Not authentication: any local caller can read the id from the run's events. It makes the
    approval explicit and tied to one plan, so a plan rebuilt between the tick and the click is caught."""
    if not approved_plan:
        raise StepPreconditionError("Tick the approval for this plan first.")
    if approved_plan != held_plan_id:
        raise StepPreconditionError("The plan changed since it was approved. Review the new plan and tick again.")


class DevicePinNotFoundError(LookupError):
    """The run holds no pin for that device address, port and kind."""


class PendingSheetNotFoundError(LookupError):
    """A complete sheet was uploaded but its server-side hold is gone (already turned into a run, or
    the state DB was reset) — the operator should re-upload the Initialisation sheet."""


class RunCoordinator:
    def __init__(self, settings: Settings, store: RunStore, events: InMemoryEventBus) -> None:
        self.settings = settings
        self.store = store
        self.events = events
        self.console = ConsoleBus()
        self._tasks: dict[str, asyncio.Task] = {}
        self._last_phase: dict[str, WorkflowPhase] = {}

    def current_settings(self) -> Settings:
        # Re-read settings (incl. .env) at each step so GreenLake credentials entered in the
        # Configure screen AFTER the server started take effect without a restart. The startup
        # snapshot (self.settings) is only a fallback if reloading ever fails.
        try:
            return load_settings()
        except Exception:  # noqa: BLE001
            return self.settings

    # ------------------------------------------------------------------ run lifecycle

    def create_run(
        self,
        item: ArrayWorkItem,
        *,
        mode: RunMode = RunMode.FULL_ONBOARDING,
        selected_steps: list[str] | None = None,
        provisioning_intent: ProvisioningIntent | None = None,
    ) -> RunRecord:
        selected = list(selected_steps or [])
        if any(step.kind == "replicate" for step in enabled_steps(mode, selected)) and (
            provisioning_intent is None or provisioning_intent.replication is None
        ):
            raise ValueError(
                "The Replication and Failover test steps need the workbook's 'Replication' tab (peer array "
                "and the volume sets to protect). Fill it in and upload again, or choose a mode without them."
            )
        if any(step.kind == "migrate" for step in enabled_steps(mode, selected)) and (
            provisioning_intent is None or provisioning_intent.migration is None
        ):
            raise ValueError(
                "The Migration step needs the workbook's 'Migration' tab (the source array and the hosts to "
                "migrate). Fill it in and upload again, or choose a mode without it."
            )
        if any(step.kind == "snapshot" for step in enabled_steps(mode, selected)) and (
            provisioning_intent is None or provisioning_intent.snapshots is None
        ):
            raise ValueError(SNAPSHOTS_TAB_NEEDED)
        not_built = [NOT_BUILT_STEPS[step.key] for step in enabled_steps(mode, selected) if step.key in NOT_BUILT_STEPS]
        if not_built:
            raise ValueError(" ".join(not_built) + " Choose a mode without it.")
        if (
            any(step.key == "provision" for step in enabled_steps(mode, selected))
            and provisioning_intent is not None
            and not provisioning_intent.volumes
        ):
            raise ValueError(
                "The Volumes tab is empty, so there is nothing to provision. To replicate volume sets that "
                "already exist on the array, choose Custom with Replication (and Failover test, As-built)."
            )
        run = RunRecord(
            serial_number=item.serial_number,
            status=RunStatus.READY,
            current_phase=initial_phase(mode, selected),  # land on the first enabled step
            mode=mode,
            selected_steps=selected,
        )
        self.store.upsert_run(run)
        self.store.save_work_item(run.run_id, item)
        if provisioning_intent is not None:
            self.store.save_provisioning_intent(run.run_id, provisioning_intent)
        self.emit(
            run.run_id,
            run.current_phase,
            "run.created",
            f"Run created for {item.serial_number} ({mode.value})",
        )
        return run

    def stash_pending_sheet(
        self, work_item: ArrayWorkItem, provisioning_intent: ProvisioningIntent | None,
        workbook: bytes | None = None,
    ) -> str:
        """Hold a parsed COMPLETE sheet server-side and return a single-use token. The run is minted
        later, when the operator picks a mode (ADR 0005 revision) — device passwords never round-trip
        to the browser. `workbook`: the file, held when the upload listed problems in some tabs."""
        token = uuid4().hex
        self.store.save_pending_sheet(token, work_item, provisioning_intent, workbook)
        return token

    def pending_sheet_workbook(self, token: str) -> bytes | None:
        return self.store.pending_sheet_workbook(token)

    def create_run_from_pending(
        self,
        token: str,
        *,
        mode: RunMode = RunMode.FULL_ONBOARDING,
        selected_steps: list[str] | None = None,
        checked_intent: ProvisioningIntent | None = None,
    ) -> RunRecord:
        """Mint the run for a previously-uploaded complete sheet, now that the operator has chosen a
        mode. Consumes the pending-sheet hold (single use). `checked_intent`: the intent of the sheet
        checked again for the chosen steps, used instead of the held one when there is one."""
        popped = self.store.pop_pending_sheet(token)
        if popped is None:
            raise PendingSheetNotFoundError(token)
        work_item, provisioning_intent = popped
        return self.create_run(
            work_item,
            mode=mode,
            selected_steps=selected_steps,
            provisioning_intent=checked_intent if checked_intent is not None else provisioning_intent,
        )

    def get_provisioning_intent(self, run_id: str) -> ProvisioningIntent:
        intent = self.store.get_provisioning_intent(run_id)
        if intent is None:
            raise RunNotFoundError(run_id)
        return intent

    def get_run(self, run_id: str) -> RunRecord:
        run = self.store.get_run(run_id)
        if run is None:
            raise RunNotFoundError(run_id)
        return run

    def get_work_item(self, run_id: str) -> ArrayWorkItem:
        item = self.store.get_work_item(run_id)
        if item is None:
            raise RunNotFoundError(run_id)
        return item

    def array_host(self, run_id: str) -> str:
        """The address of THE array this run is about — one answer, for every step.

        A run covers one array, but its address is stated in up to two places: the Initialisation
        tab's management IP (present whenever the array is initialised or verified) and the
        Provisioning tab's array host (present whenever a provisioning step is selected). The sheet
        parser REFUSES a workbook where both are given and disagree, so whichever exists here is
        THE array — this is not a preference between two candidates.

        Steps used to make this choice independently and reached different boxes in the same run:
        verify read the Initialisation IP while the as-built read the Provisioning one, so verify
        passed against the array being onboarded and the as-built timed out against another
        (measured live: 10.132.30.121 vs 10.64.186.90).
        """
        item = self.get_work_item(run_id)
        mgmt = (item.network.mgmt_ipv4 or "").strip()
        if mgmt:
            return mgmt
        intent = self.store.get_provisioning_intent(run_id)
        return (intent.array.host or "").strip() if intent else ""

    def array_credential(self, run_id: str) -> ArrayCredential:
        """THE array credential of this run (ADR 0013 / SPEC-008 R1), from the sheet: the Provisioning
        tab's array admin when a provisioning intent is held, else the DSCC system credential when its
        password was supplied, else none. Every step that needs the array takes it from here; the
        secret never leaves the process except through the clients that log in with it."""
        host = self.array_host(run_id)
        intent = self.store.get_provisioning_intent(run_id)
        if intent is not None and intent.array.password.get_secret_value():
            return ArrayCredential(available=True, source="provisioning", username=intent.array.username,
                                   host=host, secret=intent.array.password)
        item = self.get_work_item(run_id)
        setup = item.dscc_setup
        if setup.password is not None and setup.password.get_secret_value():
            return ArrayCredential(available=True, source="dscc_setup", username=setup.username,
                                   host=host, secret=setup.password)
        return ArrayCredential(host=host)

    def list_runs(self) -> list[RunRecord]:
        return self.store.list_runs()

    def list_events(self, run_id: str) -> list[RunEvent]:
        return self.store.list_events(run_id)

    def mark_complete(self, run_id: str) -> RunRecord:
        run = self.get_run(run_id)
        self.set_state(run, RunStatus.SUCCEEDED, WorkflowPhase.COMPLETE)
        self.emit(run_id, WorkflowPhase.COMPLETE, "run.completed", "Operator confirmed DSCC finalize — onboarding complete")
        return run

    async def wait(self, run_id: str) -> None:
        """Await the run's active background task (used by tests and graceful shutdown)."""
        task = self._tasks.get(run_id)
        if task is not None:
            await task

    # ------------------------------------------------------------------ step infrastructure

    def spawn(self, run_id: str, coro) -> None:
        existing = self._tasks.get(run_id)
        if existing is not None and not existing.done():
            coro.close()
            raise RunBusyError(run_id)
        # the step's task, and every asyncio.to_thread it starts, records its commands to this run and
        # checks every device it reaches against this run's pins (ADR 0026)
        ctx = contextvars.copy_context()
        ctx.run(command_log.bind, self.command_sink(run_id))
        trust = self.trust_book(run_id)
        ctx.run(device_trust.bind, trust)
        self._tasks[run_id] = asyncio.create_task(self._guarded(run_id, coro, trust), context=ctx)

    # ------------------------------------------------------------------ SPEC-019 command log

    def record_command(self, run_id: str, entry: dict) -> dict:
        """Store one command record and push it to open console panes. Call on the event loop."""
        entry = dict(entry, seq=self.store.append_command(run_id, entry))
        self.console.publish(run_id, entry)
        return entry

    def command_sink(self, run_id: str) -> Callable[[dict], None]:
        loop = asyncio.get_running_loop()
        loop_thread = threading.get_ident()

        def sink(entry: dict) -> None:
            if threading.get_ident() == loop_thread:
                self.record_command(run_id, entry)
            else:
                loop.call_soon_threadsafe(self.record_command, run_id, entry)

        return sink

    @contextmanager
    def recording(self, run_id: str) -> Iterator[None]:
        """For reads made outside a spawned step (a route's to_thread, the console prompt): the command
        log and the run's device pins, as a spawned step has them."""
        token = command_log.bind(self.command_sink(run_id))
        trust = self.trust_book(run_id, step=False)
        trust_token = device_trust.bind(trust)
        try:
            yield
        finally:
            device_trust.unbind(trust_token)
            command_log.unbind(token)
            try:
                trust.finish()
            except Exception:  # noqa: BLE001 - a note on the run must not replace the route's own answer
                pass

    # ------------------------------------------------------------------ ADR 0026 device trust

    def trust_book(self, run_id: str, *, step: bool = True) -> RunTrustBook:
        """This run's pins for one step (or, `step=False`, one route). Call on the event loop."""
        return RunTrustBook(self, run_id, device_ca_bundle=self.device_ca_bundle(), step=step)

    def device_ca_bundle(self) -> str | None:
        """The customer's device CA bundle setting (ADR 0026), read fresh like every step's settings."""
        return (self.current_settings().alletra_device_ca_bundle or "").strip() or None

    def step_phase(self, run_id: str) -> WorkflowPhase:
        """The phase of the step now running for this run: the last phase it emitted in, else the run's."""
        phase = self._last_phase.get(run_id)
        if phase is not None:
            return phase
        run = self.store.get_run(run_id)
        return run.current_phase if run else WorkflowPhase.NOT_STARTED

    def device_pins(self, run_id: str) -> list[DevicePin]:
        self.get_run(run_id)
        return self.store.list_device_pins(run_id)

    def retrust_device(self, run_id: str, *, kind: TrustKind, host: str, port: int, fingerprint: str) -> DevicePin:
        """The operator's separate, logged action: trust the key the device presented when it was
        refused. `fingerprint` is the one they compared, so a key that changed again is not trusted."""
        run = self.get_run(run_id)
        pin = self.store.get_device_pin(run_id, kind, host, port)
        if pin is None:
            raise DevicePinNotFoundError(f"This run has not reached {host} over {kind.value.upper()} yet.")
        try:
            new = retrust(pin, fingerprint)
        except ValueError as exc:
            raise StepPreconditionError(str(exc)) from exc
        self.store.save_device_pin(run_id, new)
        self.emit(run_id, run.current_phase, "device.retrusted", retrusted_message(new),
                  data={"kind": new.kind.value, "host": new.host, "port": new.port, "device": new.device,
                        "was": pin.key.fingerprint, "now": new.key.fingerprint})
        return new

    def list_commands(self, run_id: str, since: int = 0) -> list[dict]:
        return self.store.list_commands(run_id, since)

    async def _guarded(self, run_id: str, coro, trust: RunTrustBook | None = None) -> None:
        # A crash must never leave a run stuck in RUNNING with no trace.
        try:
            await coro
        except Exception as exc:  # noqa: BLE001 - background task; record, don't crash the app.
            run = self.store.get_run(run_id)
            if run is not None:
                self.set_state(run, RunStatus.RETRYABLE_FAILURE)
            self.emit(
                run_id,
                run.current_phase if run else WorkflowPhase.NOT_STARTED,
                "step.crashed",
                f"{type(exc).__name__}: {str(exc)[:300]}",
            )
        finally:
            if trust is not None:
                try:
                    trust.finish()
                except Exception:  # noqa: BLE001 - reporting a refusal must not crash the app
                    pass

    def set_state(self, run: RunRecord, status: RunStatus, phase: WorkflowPhase | None = None) -> None:
        run.status = status
        if phase is not None:
            run.current_phase = phase
        run.updated_at = datetime.now(UTC)
        self.store.upsert_run(run)

    def emit(
        self, run_id: str, phase: WorkflowPhase, event_type: str, message: str, data: dict | None = None
    ) -> None:
        event = RunEvent(run_id=run_id, phase=phase, event_type=event_type, message=message, data=data or {})
        self._last_phase[run_id] = phase
        self.store.append_event(event)
        self.events.publish_sync(event)
