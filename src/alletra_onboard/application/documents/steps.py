"""DocumentSteps — the 'verify'-kind steps: post-init verification and the as-built document.

Both are read-only SSH reads of the array and both run AFTER the run's outcome is decided, so
neither ever changes the run status — a failure here cannot un-succeed an onboarding. The UI reacts
to the emitted events instead.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any

from pydantic import SecretStr

from alletra_onboard.application.documents import handover
from alletra_onboard.application.documents.asbuilt import generate_asbuilt
from alletra_onboard.application.documents.asbuilt_parse import parse_asbuilt
from alletra_onboard.application.documents.asbuilt_replication import rc_group_names
from alletra_onboard.application.documents.verification import verify
from alletra_onboard.application.provisioning import iscsi_network, peer_ports, peer_ports_read
from alletra_onboard.application.provisioning.clients import make_array_cli, make_wsapi_v3
from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.runs.coordinator import RunCoordinator, StepPreconditionError
from alletra_onboard.application.snapshots import read as snapshots_read
from alletra_onboard.application.unified_file import read as file_read
from alletra_onboard.domain import events
from alletra_onboard.domain.discovery import EthernetPort
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.models import ArrayWorkItem, RunRecord, WorkflowPhase
from alletra_onboard.domain.network import IscsiVlanRequest
from alletra_onboard.domain.peer_ports import PeerPortIntent
from alletra_onboard.domain.replication import ReplicationIntent
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.trust import DevicePinInfo
from alletra_onboard.domain.unified_file import FileReport


def _format_ts(ts: Any) -> str:
    return ts.isoformat() if hasattr(ts, "isoformat") else str(ts)


def _record_ports_event(ev: dict, data, peer_sets: dict[str, dict]) -> None:
    # SPEC-025 R9: the last plan that set ports (its commands) and the last read after the paste.
    peer = ev.get("peer") or {}
    for action in (peer.get("plan") or {}).get("actions") or []:
        if action.get("state") == "create" and action.get("nsp") not in peer_sets:
            peer_sets[action.get("nsp")] = action
    if peer.get("result"):
        data.peer_ports_result = peer["result"]
    # SPEC-024 R7: an interface this run's plan had to add, found on the array now, was set up in this run.
    plan = (ev.get("iscsi") or {}).get("plan") or {}
    for action in plan.get("actions") or []:
        key = (action.get("nsp", ""), action.get("vlan_id"))
        if action.get("state") == "create" and key not in data.iscsi_set_up_in_run:
            data.iscsi_set_up_in_run.append(key)


def _record_apply_event(
    etype: str, ev: dict, data, last_rc_plan: dict | None, last_snap_plan: dict | None,
) -> tuple[dict | None, dict | None]:
    # SPEC-007 R6: a failed apply's objects are undone too; a retry calls them Exists.
    if etype in ("zoning.applied", "zoning.apply.failed"):
        data.zoning_applies.append(ev.get("result") or {})
    elif etype in ("storage.applied", "storage.apply.failed"):
        data.provisioning_removals.extend((ev.get("result") or {}).get("removals") or [])
    elif etype == "replication.previewed":
        last_rc_plan = ev.get("plan")
        if ev.get("report") is not None:
            data.replication_report = ev["report"]
    elif etype in ("replication.applied", "replication.apply.failed"):
        data.replication_applies.append({"plan": last_rc_plan, "result": ev.get("result") or {}})
    elif etype == "snapshots.previewed":
        last_snap_plan = ev.get("plan")
    elif etype in ("snapshots.applied", "snapshots.apply.failed"):
        data.snapshots_applies.append({"plan": last_snap_plan, "result": ev.get("result") or {}})
    return last_rc_plan, last_snap_plan


def _finalize_run_records(data, peer_sets: dict[str, dict], seen: dict[str, datetime]) -> None:
    if peer_sets:
        data.peer_ports_plan = {"actions": list(peer_sets.values())}
    for entry in reversed(data.replication_applies):          # SPEC-021: newest apply first, each line once
        for key, merged in (("removals_a", data.replication_removals_a), ("removals_b", data.replication_removals_b)):
            merged.extend(line for line in entry["result"].get(key) or [] if line not in merged)
    if "provisioning_result" in seen:
        data.provisioning_applied_at = _format_ts(seen["provisioning_result"])
    if "replication_result" in seen:
        data.replication_applied_at = _format_ts(seen["replication_result"])
    if "snapshots_result" in seen:
        data.snapshots_applied_at = _format_ts(seen["snapshots_result"])


class DocumentSteps:
    # Read-only reads whose section markers `parse_asbuilt` expects (order is not significant).
    _ASBUILT_COMMANDS: tuple[str, ...] = (
        "shownode", "showcage", "showsys -d", "shownet", "showversion",
        "showpd", "showcpg", "showport", "showport -par",
        "showinventory -csvtable", "checkhealth -svc -detail",
    )
    # SPEC-002 array sections: AsBuiltData field -> the read that fills it. Each runs in its own
    # try so one failing listing costs one section, not the document (R6).
    _ASBUILT_LISTINGS: tuple[tuple[str, str], ...] = (
        ("showhost_d", "showhost -d"),
        ("showhostset", "showhostset"),
        ("showvv", "showvv"),
        # `showvv -listcols` on OS 10.5.55 (rack13arcus, 2026-09-13) names the column CPG; UsrCPG/SnpCPG
        # are rejected ("Invalid columns specified"). Header-driven parsing accepts either spelling.
        ("showvv_cpg", "showvv -showcols Id,Name,Prov,Type,CPG,VSize_MB"),
        ("showvvset", "showvvset"),
        ("showvlun_t", "showvlun -t"),
        ("showvlun_a", "showvlun -a"),
        # SPEC-024 R7: the VLAN-tagged iSCSI addresses
        ("showport_iscsivlans", "showport -iscsivlans"),
        # SPEC-025 R9: the array's own listing of its peer ports
        ("showport_peer", "showport -peer"),
    )
    # SPEC-002 run sections: event type -> (AsBuiltData field, payload key). The LATEST event of
    # each type wins; the two zoning-check types share a field so whichever came last wins.
    _ASBUILT_RECORDS: Mapping[str, tuple[str, str | None]] = MappingProxyType({
        "zoning.plan": ("zoning_plan", "plan"),
        "zoning.previewed": ("zoning_report", "report"),
        "zoning.proper": ("zoning_report", "report"),
        "zoning.rendered": ("zoning_rendered", None),
        "zoning.applied": ("zoning_apply", "result"),
        "zoning.apply.failed": ("zoning_apply", "result"),
        "storage.previewed": ("provisioning_plan", "plan"),
        "storage.applied": ("provisioning_result", "result"),
        "storage.apply.failed": ("provisioning_result", "result"),     # SPEC-007 R6: a failed apply made objects too
        "storage.paths.verified": ("path_verification", "verification"),
        # SPEC-018: the replication plan and what the apply did (a failed apply also carries a result)
        "replication.previewed": ("replication_plan", "plan"),
        "replication.applied": ("replication_result", "result"),
        "replication.apply.failed": ("replication_result", "result"),
        # SPEC-020 R6: the measured latency
        "replication.link_checked": ("link_check", "link_check"),
        "replication.link_check.failed": ("link_check", "link_check"),
        # SPEC-017 R6: the failover test's record, passed or not
        "failover.completed": ("failover_record", "record"),
        "failover.failed": ("failover_record", "record"),
        # SPEC-023 R8: the snapshot plan and what the latest apply did (a failed apply carries a result too)
        "snapshots.previewed": ("snapshots_plan", "plan"),
        "snapshots.applied": ("snapshots_result", "result"),
        "snapshots.apply.failed": ("snapshots_result", "result"),
    })

    def __init__(self, coord: RunCoordinator, *, verify_fn: Callable = verify,
                 read_replication: Callable = replication_read.read_array,
                 read_replication_details: Callable = replication_read.read_group_details,
                 read_file: Callable = file_read.read_array_file,
                 wsapi_v3_factory: Callable = make_wsapi_v3,
                 read_snapshots: Callable = snapshots_read.read_array,
                 read_iscsi_vlans: Callable = iscsi_network.read_iscsi_vlans,
                 read_peer_ports: Callable = peer_ports_read.read_view) -> None:
        self._coord = coord
        self._verify_fn = verify_fn
        self._read_replication = read_replication
        self._read_replication_details = read_replication_details
        self._read_file = read_file
        self._wsapi_v3_factory = wsapi_v3_factory
        self._read_snapshots = read_snapshots
        self._read_iscsi_vlans = read_iscsi_vlans
        self._read_peer_ports = read_peer_ports
        self._asbuilt: dict[str, bytes] = {}  # generated as-built .docx bytes, per run

    # ------------------------------------------------------------------ post-init verification

    def resolve_credential(self, run_id: str, username: str | None, password: str | None) -> tuple[str, str]:
        """SPEC-008 R2: an explicit pair overrides; otherwise the run's own credential (ADR 0013); with
        neither the step refuses with the sentence the UI shows. A username alone is not a credential."""
        if username and password:
            return username, password
        cred = self._coord.array_credential(run_id)
        if cred.available and cred.secret is not None:
            return cred.username, cred.secret.get_secret_value()
        raise StepPreconditionError(
            "This run holds no array credential — enter the array admin username and password."
        )

    def start_verify(self, run_id: str, *, username: str | None = None, password: str | None = None) -> RunRecord:
        coord = self._coord
        run, item = coord.get_run(run_id), coord.get_work_item(run_id)
        username, password = self.resolve_credential(run_id, username, password)
        coord.spawn(run_id, self._run_verify(run, item, username, password))
        return run

    async def _run_verify(self, run: RunRecord, item: ArrayWorkItem, username: str, password: str) -> None:
        # The run is already COMPLETE; verification is a read-only confidence check and must NEVER
        # change the run status — a failure here can't un-succeed the onboarding.
        coord = self._coord
        coord.emit(run.run_id, WorkflowPhase.CONFIG_VERIFY, events.STEP_STARTED, "Verifying the array configuration over SSH…")
        try:
            report = await asyncio.to_thread(self._verify_fn, item, username, password)
        except Exception as exc:  # never propagate (the guard would mark the run failed)
            coord.emit(
                run.run_id,
                WorkflowPhase.CONFIG_VERIFY,
                events.VERIFY_FAILED,
                f"Verification error: {type(exc).__name__}: {str(exc)[:200]}",
            )
            return
        if not report.reachable:
            coord.emit(run.run_id, WorkflowPhase.CONFIG_VERIFY, events.VERIFY_FAILED, report.error or "Could not reach the array over SSH.")
            return
        iscsi = ""
        rows = self._iscsi_rows(run.run_id)
        creds = EndpointCreds(host=coord.array_host(run.run_id), username=username, password=SecretStr(password))
        if rows:
            # SPEC-024 R6, read-only: the sheet's iSCSI network rows against showport -iscsivlans.
            try:
                vlans = await asyncio.to_thread(self._read_iscsi_vlans, creds)
                report.iscsi_vlans = iscsi_network.verify_iscsi_vlans(rows, vlans)
                present = sum(1 for c in report.iscsi_vlans if c.status == "present")
                iscsi = f" iSCSI VLAN addresses: {present} of {len(rows)} present."
            except (DeviceError, ValueError) as exc:  # one read failing costs its section, not the report
                report.iscsi_vlans_error = f"`showport -iscsivlans` could not be read: {exc}"
                iscsi = " The iSCSI VLAN addresses could not be read."
        peer = self._peer_intent(run.run_id)
        if peer is not None:
            # SPEC-025 R6, read-only: the planned peer ports as the array reads them now.
            view = await asyncio.to_thread(self._read_peer_ports, creds)
            if view.read_error:
                report.peer_ports_error = view.read_error
                iscsi += " The peer ports could not be read."
            else:
                report.peer_ports = peer_ports.verify_peer_ports(peer, view)
                ready = sum(1 for c in report.peer_ports if c.ok)
                iscsi += f" Peer ports: {ready} of {len(report.peer_ports)} ready."
        coord.emit(
            run.run_id,
            WorkflowPhase.CONFIG_VERIFY,
            events.VERIFY_COMPLETED,
            f"Verified the array — {report.passed} OK, {report.mismatches} mismatch(es), "
            f"{report.health_total} health issue(s).{iscsi}",
            events.VerifyData(report=report),
        )

    def _peer_intent(self, run_id: str) -> PeerPortIntent | None:
        intent = self._coord.store.get_provisioning_intent(run_id)
        return intent.peer_ports if intent is not None else None

    def _iscsi_rows(self, run_id: str) -> list[IscsiVlanRequest]:
        intent = self._coord.store.get_provisioning_intent(run_id)
        return list(intent.iscsi_network) if intent is not None else []

    # ------------------------------------------------------------------ as-built document (last step)

    def start_asbuilt(
        self, run_id: str, *, username: str | None = None, password: str | None = None, customer: str = "",
        site: str = "", application_workload: str = "", purpose: str = "",
    ) -> RunRecord:
        coord = self._coord
        run, item = coord.get_run(run_id), coord.get_work_item(run_id)
        # The run's array — the same one verify checks. Not chosen here; see RunCoordinator.array_host.
        host = coord.array_host(run_id)
        username, password = self.resolve_credential(run_id, username, password)
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
        coord.emit(run.run_id, WorkflowPhase.ASBUILT_DOCUMENT, events.ASBUILT_STARTED,
                   f"Reading {host} (read-only) and building the as-built document…")
        try:
            data = await asyncio.to_thread(self._collect_asbuilt, host, username, password)
            data.run_created_at = run.created_at
            self._run_records(run.run_id, data)
            creds = EndpointCreds(host=host, username=username, password=SecretStr(password))
            intent = coord.store.get_provisioning_intent(run.run_id)
            if intent is not None:
                data.iscsi_network_rows = [r.model_dump(mode="json") for r in intent.iscsi_network]
                if intent.peer_ports is not None:
                    data.peer_ports_rows = [r.model_dump(mode="json") for r in intent.peer_ports.ports]
                if intent.replication is not None:
                    # SPEC-018 R3: the replication states are read from BOTH arrays now, not copied from the plan
                    data.replication_tab = self._replication_tab(intent.replication)
                    data.replication_primary, data.replication_peer = await asyncio.to_thread(
                        self._collect_replication, creds, intent.replication.peer,
                    )
                    # BL-64: every volume and the settings of each group this run configured (showrcopy -d)
                    names = rc_group_names(data)
                    if names:
                        data.replication_details, data.replication_details_errors = await asyncio.to_thread(
                            self._read_replication_details, creds, names)
                if intent.snapshots is not None:
                    # SPEC-023 R8: schedules and snapshots are read now, not copied from the plan
                    data.snapshots_tab = [r.model_dump(mode="json") for r in intent.snapshots.requests]
                    data.snapshots_view = await asyncio.to_thread(self._read_snapshots, creds)
            # The step's own fields win over the workbook's — the operator is looking at the
            # document about to be produced, and the sheet may have been filled weeks earlier.
            data.customer = customer or item.customer_name or ""
            data.site = site or item.site or ""
            data.application_workload = application_workload or item.application_workload or ""
            data.purpose = purpose or item.storage_purpose or ""
            # ADR 0026: after every read above, so a device first reached for this document is listed too
            data.trusted_devices = [DevicePinInfo.of(pin).model_dump(mode="json")
                                    for pin in coord.device_pins(run.run_id)]
            docx_bytes, warnings = await asyncio.to_thread(self._render_asbuilt, data)
            status = self._handover_status(data)
        except Exception as exc:  # report, never propagate (would mark the run failed)
            coord.emit(run.run_id, WorkflowPhase.ASBUILT_DOCUMENT, events.ASBUILT_FAILED,
                       f"As-built generation failed: {type(exc).__name__}: {str(exc)[:200]}")
            return
        self._asbuilt[run.run_id] = docx_bytes
        # The document exists and is downloadable from memory. Failing to persist it must not
        # escape: the guard around this task would mark a finished run failed, which this step
        # is documented never to do.
        coord.save_artifact_best_effort(run.run_id, "asbuilt_docx", docx_bytes)
        summary = f"As-built ready for {data.name or data.serial_no or host} — {len(docx_bytes) // 1024} KB."
        if warnings:
            # The document is produced regardless, so the warnings must travel WITH it — in the
            # message and in the event data — or a rushed operator sends an incomplete as-built.
            summary += f" {len(warnings)} item(s) need attention before sending."
        coord.emit(
            run.run_id, WorkflowPhase.ASBUILT_DOCUMENT, events.ASBUILT_GENERATED, summary,
            events.AsBuiltResultData(serial=data.serial_no, name=data.name, customer=data.customer,
                                     size=len(docx_bytes), warnings=warnings, handover=status),
        )

    @staticmethod
    def _handover_status(data) -> events.HandoverStatus | None:
        """SPEC-026 R10: the page's Status at handover, from the same reads as the document. None when
        the reads were not made."""
        if data.handover_read_at is None:
            return None
        return handover.summarise(handover.read_from(data))

    def _collect_asbuilt(self, host: str, username: str, password: str):
        creds = EndpointCreds(host=host, username=username, password=SecretStr(password))
        lines: list[str] = []
        outputs: dict[str, str] = {}
        with make_array_cli(creds) as cli:
            for cmd in self._ASBUILT_COMMANDS:
                outputs[cmd] = cli.run(cmd)
                lines.append(f"===== $ {cmd} =====")
                lines.append(outputs[cmd])
            data = parse_asbuilt("\n".join(lines))
            data.showport = outputs.get("showport", "")
            self._read_into(cli, data, self._ASBUILT_LISTINGS)  # R6: name it, keep going
            # SPEC-028 R3: the file side, in the same session; no section on an array without one
            data.file_ports, data.file_report, data.file_read_error = self._collect_file(cli, creds)
            # SPEC-026 R3: the array's clock, alerts and capacity, each failing on its own (R8), read last
            data.handover_read_at = datetime.now(UTC)
            self._read_into(cli, data, handover.READS)  # R8: name it, keep going
        return data

    @staticmethod
    def _read_into(cli, data, pairs: tuple[tuple[str, str], ...]) -> None:
        for attr, cmd in pairs:
            try:
                setattr(data, attr, cli.run(cmd))
            except DeviceError as exc:
                data.read_errors[cmd] = f"{type(exc).__name__}: {exc}"

    def _run_records(self, run_id: str, data) -> None:
        """Fill the run sections from the run's own events: the latest payload per event type, plus
        the union of every apply's removal items (SPEC-007 — a run may apply more than once)."""
        seen: dict[str, datetime] = {}
        peer_sets: dict[str, dict] = {}     # each port's first planned set (SPEC-025 R9)
        last_rc_plan: dict | None = None
        last_snap_plan: dict | None = None
        for event in self._coord.list_events(run_id):
            if event.event_type in ("ports.previewed", "ports.completed"):
                _record_ports_event(event.data, data, peer_sets)
            else:
                last_rc_plan, last_snap_plan = _record_apply_event(
                    event.event_type, event.data, data, last_rc_plan, last_snap_plan,
                )
            target = self._ASBUILT_RECORDS.get(event.event_type)
            if target is None:
                continue
            attr, key = target
            payload = event.data if key is None else event.data.get(key)
            if payload is None:
                continue
            setattr(data, attr, payload)
            seen[attr] = event.created_at
        _finalize_run_records(data, peer_sets, seen)
        data.commands = [{k: v for k, v in c.items() if k != "output"} for c in self._coord.list_commands(run_id)]

    @staticmethod
    def _replication_tab(replication: ReplicationIntent) -> dict:
        return {
            "peer_host": replication.peer.host,
            "rows": [{"vvset": r.vvset, "mode": r.mode, "rpo_minutes": r.rpo_minutes, "peer_cpg": r.peer_cpg}
                     for r in replication.protections],
            "failover_test": replication.failover_test,
            "rtt_ms": replication.rtt_ms,       # SPEC-031 R7: over Fibre Channel the latency is the typed one
        }

    def _collect_replication(self, primary: EndpointCreds, peer: EndpointCreds):
        """Both arrays, read-only, at generation time. A read that fails is the view's `read_error`;
        the renderer names it and the document is still produced (R3)."""
        return self._read_replication(primary), self._read_replication(peer)

    def _collect_file(self, cli, creds: EndpointCreds) -> tuple[list[EthernetPort], FileReport | None, str]:
        """(File ports, FileReport or None, read error), over the open SSH session and, when the
        array has a file side, one WSAPI v3 session with the run's credential. A failed read is
        named in the section and the warnings; the document is still produced."""
        try:
            ports, report = self._read_file(cli, self._wsapi_v3_factory(creds))
        except Exception as exc:  # R6 pattern: name it, keep going
            return [], None, f"{type(exc).__name__}: {exc}"
        return ports, report, ""

    def _render_asbuilt(self, data) -> tuple[bytes, list[str]]:
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
