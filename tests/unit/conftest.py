from __future__ import annotations

import pytest
from pydantic import BaseModel

from alletra_onboard.domain.approval import Approval


def _unit_save(model: BaseModel) -> None:
    model.model_dump(mode="json")


@pytest.fixture(autouse=True)
def _bind_unit_approval_saver(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every unit apply test runs with saving active on Approval, as RunCoordinator.run_approved does."""
    orig_post_init = Approval.__post_init__

    def _with_saver(self: Approval) -> None:
        orig_post_init(self)
        if self.save_record is None:
            self.save_record = _unit_save

    monkeypatch.setattr(Approval, "__post_init__", _with_saver)
