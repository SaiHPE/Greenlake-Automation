"""DocumentSteps — the 'verify'-kind steps: post-init verification and the as-built document.

Both are read-only SSH reads of the array and both run AFTER the run's outcome is decided, so
neither ever changes the run status — a failure here cannot un-succeed an onboarding. The UI reacts
to the emitted events instead.
"""

from __future__ import annotations

import asyncio
from typing import Callable

from alletra_onboard.application.documents.asbuilt import generate_asbuilt
from alletra_onboard.application.documents.asbuilt_parse import parse_asbuilt
from alletra_onboard.application.runs.coordinator import RunCoordinator
from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.documents.verification import verify
from alletra_onboard.domain.models import ArrayWorkItem, RunRecord, WorkflowPhase
from alletra_onboard.domain.shared import EndpointCreds


class DocumentSteps:
    # Read-only reads whose section markers `parse_asbuilt` expects (order is not significant).
    _ASBUILT_COMMANDS: tuple[str, ...] = (
        "shownode", "showcage", "showsys -d", "shownet", "showversion",
        "showpd", "showcpg", "showport", "showport -par",
        "showinventory -csvtable", "checkhealth -svc -detail",
    )

    def __init__(self, coord: RunCoordinator, *, verify_fn: Callable = verify) -> None:
        self._coord = coord
        self._verify_fn = verify_fn
        self._asbuilt: dict[str, bytes] = {}  # generated as-built .docx bytes, per run

    # ------------------------------------------------------------------ post-init verification

    def start_verify(self, run_id: str, *, username: str, password: str) -> RunRecord:
        coord = self._coord
        run, item = coord.get_run(run_id), coord.get_work_item(run_id)
        coord.spawn(run_id, self._run_verify(run, item, username, password))
        return run

    async def _run_verify(self, run: RunRecord, item: ArrayWorkItem, username: str, password: str) -> None:
        # The run is already COMPLETE; verification is a read-only confidence check and must NEVER
        # change the run status — a failure here can't un-succeed the onboarding.
        coord = self._coord
        coord.emit(run.run_id, WorkflowPhase.CONFIG_VERIFY, "step.started", "Verifying the array configuration over SSH…")
        try:
            report = await asyncio.to_thread(self._verify_fn, item, username, password)
        except Exception as exc:  # noqa: BLE001 - never propagate (the guard would mark the run failed)
            coord.emit(
                run.run_id,
                WorkflowPhase.CONFIG_VERIFY,
                "verify.failed",
                f"Verification error: {type(exc).__name__}: {str(exc)[:200]}",
            )
            return
        if not report.reachable:
            coord.emit(run.run_id, WorkflowPhase.CONFIG_VERIFY, "verify.failed", report.error or "Could not reach the array over SSH.")
            return
        coord.emit(
            run.run_id,
            WorkflowPhase.CONFIG_VERIFY,
            "verify.completed",
            f"Verified the array — {report.passed} OK, {report.mismatches} mismatch(es), "
            f"{report.health_total} health issue(s).",
            data={"report": report.model_dump(mode="json")},
        )

    # ------------------------------------------------------------------ as-built document (last step)

    def start_asbuilt(
        self, run_id: str, *, username: str, password: str, customer: str = "", site: str = "",
        application_workload: str = "", purpose: str = "",
    ) -> RunRecord:
        coord = self._coord
        run, item = coord.get_run(run_id), coord.get_work_item(run_id)
        intent = coord.store.get_provisioning_intent(run_id)
        host = intent.array.host if intent else item.network.mgmt_ipv4
        coord.spawn(run_id, self._run_asbuilt(
            run, item, host, username, password, customer, site, application_workload, purpose,
        ))
        return run

    async def _run_asbuilt(self, run: RunRecord, item: ArrayWorkItem, host: str, username: str,
                           password: str, customer: str, site: str,
                           application_workload: str = "", purpose: str = "") -> None:
        # Read-only (SSH show*/checkhealth/showinventory -csvtable) -> the as-built .docx. Post-onboarding
        # and read-only, so like verify it NEVER changes the run status; the UI reacts to the events.
        coord = self._coord
        coord.emit(run.run_id, WorkflowPhase.ASBUILT_DOCUMENT, "asbuilt.started",
                   f"Reading {host} (read-only) and building the as-built document…")
        try:
            data = await asyncio.to_thread(self._collect_asbuilt, host, username, password)
            # The step's own fields win over the workbook's — the operator is looking at the
            # document about to be produced, and the sheet may have been filled weeks earlier.
            data.customer = customer or item.customer_name or ""
            data.site = site or item.site or ""
            data.application_workload = application_workload or item.application_workload or ""
            data.purpose = purpose or item.storage_purpose or ""
            docx_bytes, warnings = await asyncio.to_thread(self._render_asbuilt, data)
        except Exception as exc:  # noqa: BLE001 - report, never propagate (would mark the run failed)
            coord.emit(run.run_id, WorkflowPhase.ASBUILT_DOCUMENT, "asbuilt.failed",
                       f"As-built generation failed: {type(exc).__name__}: {str(exc)[:200]}")
            return
        self._asbuilt[run.run_id] = docx_bytes
        try:
            coord.store.save_artifact(run.run_id, "asbuilt_docx", docx_bytes)
        except Exception:  # noqa: BLE001
            # The document exists and is downloadable from memory. Failing to persist it must not
            # escape: the guard around this task would mark a finished run failed, which this step
            # is documented never to do.
            pass
        summary = f"As-built ready for {data.name or data.serial_no or host} — {len(docx_bytes) // 1024} KB."
        if warnings:
            # The document is produced regardless, so the warnings must travel WITH it — in the
            # message and in the event data — or a rushed operator sends an incomplete as-built.
            summary += f" {len(warnings)} item(s) need attention before sending."
        coord.emit(run.run_id, WorkflowPhase.ASBUILT_DOCUMENT, "asbuilt.generated", summary,
                   data={"serial": data.serial_no, "name": data.name, "customer": data.customer,
                         "size": len(docx_bytes), "warnings": warnings})

    def _collect_asbuilt(self, host: str, username: str, password: str):
        creds = EndpointCreds(host=host, username=username, password=password)
        lines: list[str] = []
        with make_array_cli(creds) as cli:
            for cmd in self._ASBUILT_COMMANDS:
                lines.append(f"===== $ {cmd} =====")
                lines.append(cli.run(cmd))
        return parse_asbuilt("\n".join(lines))

    def _render_asbuilt(self, data) -> tuple[bytes, list[str]]:
        import os
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".docx")
        os.close(fd)
        try:
            _out, warnings = generate_asbuilt(data, path)
            with open(path, "rb") as f:
                return f.read(), warnings
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def get_asbuilt(self, run_id: str) -> bytes | None:
        cached = self._asbuilt.get(run_id)
        if cached is not None:
            return cached
        stored = self._coord.store.load_artifact(run_id, "asbuilt_docx")
        if stored is not None:
            self._asbuilt[run_id] = stored
        return stored
