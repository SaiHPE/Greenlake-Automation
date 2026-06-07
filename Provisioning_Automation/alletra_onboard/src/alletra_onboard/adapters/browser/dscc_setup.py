from __future__ import annotations

from alletra_onboard.domain.models import ArrayWorkItem, BrowserResultStatus


class DsccSetupAdapter:
    async def run(self, item: ArrayWorkItem, run_id: str) -> BrowserResultStatus:
        if not item.dscc_region_code:
            return BrowserResultStatus.FAILED_TERMINAL
        return BrowserResultStatus.WAITING_FOR_OPERATOR
