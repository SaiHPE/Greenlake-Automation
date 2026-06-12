from __future__ import annotations

from pydantic import ValidationError

from alletra_onboard.domain.models import ArrayWorkItem


class ValidationService:
    def validate_work_item(self, payload: dict) -> tuple[ArrayWorkItem | None, list[str]]:
        try:
            return ArrayWorkItem.model_validate(payload), []
        except ValidationError as error:
            return None, [f"{'.'.join(map(str, issue['loc']))}: {issue['msg']}" for issue in error.errors()]
