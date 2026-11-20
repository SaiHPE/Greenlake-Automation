"""GreenLake REST adapters."""

from __future__ import annotations

from typing import Any

from alletra_onboard.domain.errors import GreenLakeError


def json_object(response: Any, *, where: str = "GreenLake response") -> dict[str, Any]:
    """Parse a 2xx JSON object body; malformed JSON or a non-object becomes GreenLakeError."""
    try:
        body = response.json()
    except ValueError as exc:
        raise GreenLakeError(f"Malformed JSON in {where}: {exc}") from exc
    if not isinstance(body, dict):
        raise GreenLakeError(f"Unexpected {type(body).__name__} body in {where} (expected JSON object).")
    return body


def json_items(response: Any, *, where: str = "GreenLake response") -> list[dict[str, Any]]:
    """Parse a 2xx list-envelope body (`{items: [...]}`); non-object or non-list `items`, or any
    non-object entry, becomes GreenLakeError."""
    body = json_object(response, where=where)
    items = body.get("items", [])
    if not isinstance(items, list):
        raise GreenLakeError(f"Unexpected 'items' ({type(items).__name__}) in {where} (expected list).")
    for item in items:
        if not isinstance(item, dict):
            raise GreenLakeError(
                f"Unexpected {type(item).__name__} item in {where} (expected JSON object)."
            )
    return items
