from __future__ import annotations

import csv
from pathlib import Path

from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig

# Single source of truth for the operator-facing CSV columns (template download + loader).
CSV_COLUMNS = (
    "serial_number,part_number,subscription_key,service_catalog_region_id,dscc_region_code,"
    "cloudinit_url,mgmt_ipv4,mask,gateway,dns,ntp,timezone,proxy_host,proxy_port,"
    "dscc_system_name,dscc_country,contact_first_name,contact_last_name,contact_language,"
    "contact_company,contact_phone,contact_email,secret_name,secret_username,secret_password,"
    "blueprint_name,apply_blueprint"
)

_CSV_EXAMPLE_ROW = (
    "SGHD00EXAMPLE,S0B84A,EXAMPLEKEY1234567890,ap-northeast,jp1,https://169.254.239.27/cloudinit,"
    "10.64.154.225,255.255.248.0,10.64.159.254,10.203.96.10;10.203.96.9,ntp1.example.net,Asia/Tokyo,"
    "proxy.example.net,8080,MPB10K-EXAMPLE,India,Jane,Doe,English,HPE,8000000000,jane.doe@example.com,"
    "b10000-admin,3paradm,,,false"
)


def csv_template() -> str:
    """The downloadable arrays.csv template (header + one illustrative row)."""
    return f"{CSV_COLUMNS}\n{_CSV_EXAMPLE_ROW}\n"


def load_work_items_csv(path: Path) -> list[ArrayWorkItem]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [_row_to_work_item(row) for row in rows]


def load_work_items_csv_text(text: str) -> list[ArrayWorkItem]:
    """Parse uploaded CSV content (the API's upload path — no temp file needed)."""
    rows = list(csv.DictReader(text.lstrip("﻿").splitlines()))
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
        # DSCC-only columns are optional so existing GreenLake/cloudinit CSVs still load;
        # the dscc command validates that the ones it needs are present before running.
        credential_name=row.get("secret_name") or "b10000-admin",
        username=row.get("secret_username") or "3paradm",
        password=row.get("secret_password") or None,
        contact_first_name=row.get("contact_first_name") or None,
        contact_last_name=row.get("contact_last_name") or None,
        contact_language=row.get("contact_language") or "English",
        contact_company=row.get("contact_company") or None,
        contact_phone=row.get("contact_phone") or None,
        contact_email=row.get("contact_email") or None,
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
