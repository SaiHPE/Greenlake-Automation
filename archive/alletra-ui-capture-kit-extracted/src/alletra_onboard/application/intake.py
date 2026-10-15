from __future__ import annotations

import csv
from pathlib import Path

from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig


def load_work_items_csv(path: Path) -> list[ArrayWorkItem]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [_row_to_work_item(row) for row in rows]


def _split_semicolon(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def _row_to_work_item(row: dict[str, str]) -> ArrayWorkItem:
    network = NetworkConfig(
        mgmt_ipv4=row["mgmt_ipv4"],
        mask=row["mask"],
        gateway=row["gateway"],
        dns=_split_semicolon(row.get("dns")),
        ntp=row["ntp"],
        timezone=row["timezone"],
        proxy_host=row.get("proxy_host") or None,
        proxy_port=int(row["proxy_port"]) if row.get("proxy_port") else None,
    )
    dscc_setup = DsccSetupConfig(
        system_name=row["dscc_system_name"],
        country=row["dscc_country"],
        blueprint_name=row.get("blueprint_name") or None,
        apply_blueprint=(row.get("apply_blueprint") or "").lower() in {"1", "true", "yes"},
    )
    return ArrayWorkItem(
        serial_number=row["serial_number"],
        part_number=row["part_number"],
        subscription_key=row["subscription_key"],
        service_catalog_region_id=row["service_catalog_region_id"],
        dscc_region_code=row["dscc_region_code"],
        cloudinit_url=row["cloudinit_url"],
        network=network,
        dscc_setup=dscc_setup,
    )
