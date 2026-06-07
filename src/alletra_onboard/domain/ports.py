from __future__ import annotations

from typing import Protocol

from alletra_onboard.domain.models import ArrayWorkItem, BrowserResultStatus, RunEvent, RunRecord


class EventSink(Protocol):
    async def publish(self, event: RunEvent) -> None: ...


class RunStore(Protocol):
    def initialize(self) -> None: ...
    def upsert_run(self, run: RunRecord) -> None: ...
    def get_run(self, run_id: str) -> RunRecord | None: ...
    def append_event(self, event: RunEvent) -> None: ...


class CloudinitWizard(Protocol):
    async def run(self, item: ArrayWorkItem, run_id: str) -> BrowserResultStatus: ...


class DsccSetupWizard(Protocol):
    async def run(self, item: ArrayWorkItem, run_id: str) -> BrowserResultStatus: ...
