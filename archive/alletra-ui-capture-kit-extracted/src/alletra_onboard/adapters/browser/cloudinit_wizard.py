from __future__ import annotations

from alletra_onboard.domain.models import ArrayWorkItem, BrowserResultStatus


class CloudinitWizardAdapter:
    async def run(self, item: ArrayWorkItem, run_id: str) -> BrowserResultStatus:
        if not item.cloudinit_url.startswith("https://169.254."):
            return BrowserResultStatus.WAITING_FOR_OPERATOR
        return BrowserResultStatus.WAITING_FOR_OPERATOR
