"""Characterisation tests pinning the exact public behaviour of `init_sheet.py`:
templates (`full` and `init-only`), all tab parsers, cross-tab invariants, `parse_upload`
problem collection, and `compose_workbook_bytes` (including row-table replacement).
"""

from __future__ import annotations

import datetime
import io

import pytest
from openpyxl import Workbook, load_workbook

from alletra_onboard.application.platform.init_sheet import (
    HOSTS_SHEET_NAME,
    HOSTSETS_SHEET_NAME,
    ISCSI_NETWORK_SHEET_NAME,
    MIGRATION_SHEET_NAME,
    PEER_PORTS_SHEET_NAME,
    PROVISIONING_SHEET_NAME,
    REPLICATION_NETWORK_SHEET_NAME,
    REPLICATION_SHEET_NAME,
    SHEET_NAME,
    SNAPSHOTS_SHEET_NAME,
    VOLUMES_SHEET_NAME,
    build_template_bytes,
    compose_workbook_bytes,
    parse_upload,
    parse_workbook_bytes,
)
from alletra_onboard.domain.models import RunMode
from alletra_onboard.domain.snapshots import SNAPSHOTS_TAB_NEEDED

_COMPLETE_INIT = {
    "gl_client_id": "client-123",
    "gl_client_secret": "=secret xyz ",
    "gl_token_url": "https://global.api.greenlake.hpe.com/authorization/v2/oauth2/tenant/token",
    "serial_number": "SGHD45FF0Y",
    "part_number": "S0B84A",
    "subscription_key": "YHHDKEY1234567890",
    "service_catalog_region_id": "ap-northeast",
    "dscc_region_code": "jp1",
    "mgmt_ipv4": "192.0.2.10",
    "mask": "255.255.255.0",
    "gateway": "192.0.2.1",
    "dns1": "192.0.2.53",
    "ntp": "ntp.example.net",
    "timezone": "UTC",
    "contact_first_name": "Jane",
    "contact_last_name": "Doe",
    "contact_language": "English",
    "contact_company": "HPE",
    "contact_phone": "8000000000",
    "contact_email": "jane@example.com",
    "dscc_system_name": "MPB10K-CHAR",
    "dscc_country": "India",
    "secret_name": "b10000-admin",
    "secret_username": "3paradm",
}

_TARGETS = {
    "prov_array_host": "192.0.2.10",
    "prov_array_user": "3paradm",
    "prov_array_password": "=arr pw ",
    "prov_vcenter_host": "vc.example.net",
    "prov_vcenter_user": "administrator@vsphere.local",
    "prov_vcenter_password": "vpw",
}

_VOLUMES = [{"name": "vol01", "size_gib": "10", "vvset": "vvs01"}]
_HOSTSETS = [{"name": "hs01", "members": "esx1"}]
_PEER = {"peer_host": "192.0.2.20", "peer_user": "3paradm", "peer_password": "=peer pw"}
_SOURCE = {"source_host": "192.0.2.30", "source_user": "reader", "source_password": "=src pw"}


def _wb(**kwargs) -> bytes:
    defaults = {
        "base": None,
        "init": {"serial_number": "SGHD45FF0Y", "mgmt_ipv4": "192.0.2.10"},
        "targets": _TARGETS,
        "volumes": _VOLUMES,
        "hostsets": _HOSTSETS,
    }
    defaults.update(kwargs)
    return compose_workbook_bytes(**defaults)


def _delete_tabs(data: bytes, *names: str) -> bytes:
    wb = load_workbook(io.BytesIO(data))
    for name in names:
        if name in wb.sheetnames:
            del wb[name]
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


# ------------------------------------------------------------------ templates (full vs init-only)


def test_template_sheet_names_and_port_text_formats():
    full = load_workbook(io.BytesIO(build_template_bytes(init_only=False)))
    assert full.sheetnames == [
        SHEET_NAME,
        PROVISIONING_SHEET_NAME,
        VOLUMES_SHEET_NAME,
        HOSTS_SHEET_NAME,
        HOSTSETS_SHEET_NAME,
        REPLICATION_SHEET_NAME,
        REPLICATION_NETWORK_SHEET_NAME,
        ISCSI_NETWORK_SHEET_NAME,
        PEER_PORTS_SHEET_NAME,
        MIGRATION_SHEET_NAME,
        SNAPSHOTS_SHEET_NAME,
        "Prerequisites",
    ]
    assert full[REPLICATION_NETWORK_SHEET_NAME].cell(row=3, column=2).number_format == "@"
    assert full[ISCSI_NETWORK_SHEET_NAME].cell(row=3, column=1).number_format == "@"
    assert full[PEER_PORTS_SHEET_NAME].cell(row=3, column=1).number_format == "@"

    init_only = load_workbook(io.BytesIO(build_template_bytes(init_only=True)))
    assert init_only.sheetnames == [SHEET_NAME, "Prerequisites"]


# ------------------------------------------------------------------ Snapshots tab


def test_snapshots_tab_valid_variants_and_defaults():
    rows = [
        {"source": "vvs_min", "every": "15", "unit": "minute", "expire_hours": "24"},
        {
            "source": "vol_hr",
            "kind": "VOLUME",
            "snapshot_now": "y",
            "every": "4.0",
            "unit": "HOURS",
            "at_hour": "23.0",
            "days": "sun, Mon, , friday, mon",
            "expire_hours": "43800",
            "retain_hours": "43800",
            "read_only": "false",
            "schedule_name": "A.b_c-1",
        },
        {
            "source": "vvs_day",
            "every": "1",
            "unit": "day",
            "at_hour": "0",
            "expire_hours": "72",
            "retain_hours": "24",
            "read_only": "0",
        },
        # snapshot_now only: at_hour is ignored when there is no schedule; two rows without schedules
        # do not collide on schedule_name.
        {"source": "vvs_now_a", "snapshot_now": "1", "at_hour": "99", "expire_hours": "12", "schedule_name": "same"},
        {"source": "vvs_now_b", "snapshot_now": "true", "expire_hours": "12", "schedule_name": "same"},
    ]
    snap = parse_workbook_bytes(
        _wb(snapshots=rows), mode=RunMode.CUSTOM, selected_steps=["snapshots"],
    ).provisioning_intent.snapshots
    assert snap is not None
    assert [(r.source, r.kind, r.snapshot_now, r.every, r.unit, r.at_hour, r.days, r.expire_hours, r.retain_hours, r.read_only, r.schedule_name) for r in snap.requests] == [
        ("vvs_min", "set", False, 15, "minutes", 0, [], 24, None, True, ""),
        ("vol_hr", "volume", True, 4, "hours", 23, [0, 1, 5], 43800, 43800, False, "A.b_c-1"),
        ("vvs_day", "set", False, 1, "days", 0, [], 72, 24, False, ""),
        ("vvs_now_a", "set", True, None, None, 0, [], 12, None, True, "same"),
        ("vvs_now_b", "set", True, None, None, 0, [], 12, None, True, "same"),
    ]


@pytest.mark.parametrize(("rows", "expected"), [
    (
        [{"source": "s1", "every": "abc", "unit": "hours", "expire_hours": "24"}],
        ("Snapshots tab — row 's1': every abc hours is not a period the array schedules; "
        "use 15, 20 or 30 minutes, 1, 2, 3, 4, 6, 8 or 12 hours, or 1 day."),
    ),
    (
        [{"source": "s1", "every": "2", "unit": "days", "expire_hours": "24"}],
        ("Snapshots tab — row 's1': every 2 days is not a period the array schedules; "
        "use 15, 20 or 30 minutes, 1, 2, 3, 4, 6, 8 or 12 hours, or 1 day."),
    ),
    (
        [{"source": "s1", "every": "1", "unit": "weeks", "expire_hours": "24"}],
        ("Snapshots tab — row 's1': every 1 weeks is not a period the array schedules; "
        "use 15, 20 or 30 minutes, 1, 2, 3, 4, 6, 8 or 12 hours, or 1 day."),
    ),
    (
        [{"source": "s1", "every": "1", "unit": "hours", "at_hour": "-1", "expire_hours": "24"}],
        "Snapshots tab — row 's1': Start hour must be a whole number from 0 to 23 (got '-1').",
    ),
    (
        [{"source": "s1", "every": "1", "unit": "hours", "at_hour": "1.5", "expire_hours": "24"}],
        "Snapshots tab — row 's1': Start hour must be a whole number from 0 to 23 (got '1.5').",
    ),
    (
        [{"source": "s1", "snapshot_now": "yes", "expire_hours": "0"}],
        "Snapshots tab — row 's1': Keep for must be a whole number of hours from 1 to 43800.",
    ),
    (
        [{"source": "s1", "snapshot_now": "yes", "expire_hours": "24", "retain_hours": "43801"}],
        "Snapshots tab — row 's1': Lock for must be a whole number of hours from 1 to 43800, or blank.",
    ),
    (
        [{"source": "s1", "snapshot_now": "yes", "expire_hours": "24", "schedule_name": "a" * 32}],
        "Snapshots tab — row 's1': Schedule name may use letters, digits, '.', '_' and '-' only, up to 31 characters.",
    ),
    (
        [{"source": "s1", "snapshot_now": "yes", "expire_hours": "24", "schedule_name": "ALL"}],
        "Snapshots tab — row 's1': Schedule name 'ALL' is kept by the array for itself; choose another.",
    ),
    (
        [{"source": "s1", "snapshot_now": "yes", "expire_hours": "24", "schedule_name": "Upgrade"}],
        "Snapshots tab — row 's1': Schedule name 'Upgrade' is kept by the array for itself; choose another.",
    ),
    (
        [{"source": "s1", "snapshot_now": "maybe", "expire_hours": "24"}],
        "Snapshots tab — row 's1': Snapshot now must be 'yes' or 'no' (got 'maybe').",
    ),
])
def test_snapshots_tab_exact_error_messages(rows, expected):
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(_wb(snapshots=rows), mode=RunMode.CUSTOM, selected_steps=["snapshots"])
    assert str(exc.value) == expected


def test_snapshots_tab_missing_returns_none_and_raises_when_step_selected():
    without = _delete_tabs(_wb(), SNAPSHOTS_SHEET_NAME)
    assert parse_workbook_bytes(without, mode=RunMode.PROVISION_ONLY).provisioning_intent.snapshots is None
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(without, mode=RunMode.CUSTOM, selected_steps=["snapshots"])
    assert str(exc.value) == SNAPSHOTS_TAB_NEEDED


# ------------------------------------------------------------------ Replication & Replication network tabs


def test_replication_tab_aliases_sync_ignores_rpo_and_optional_only_tab_is_blank():
    # Optional fields alone (no required peer fields and no rows) count as a blank tab -> None.
    only_opt = _wb(replication={"fields": {"rtt_ms": "5", "failover_test": "no"}, "rows": []})
    assert parse_workbook_bytes(only_opt, mode=RunMode.PROVISION_ONLY).provisioning_intent.replication is None

    rows = [
        {"vvset": "s1", "mode": "Asynchronous Periodic", "rpo_minutes": "15.0", "peer_cpg": "SSD_r6"},
        {"vvset": "s2", "mode": "synchronous", "rpo_minutes": "ignored", "peer_cpg": "FC_r6", "auto_synchronize": "0"},
        {"vvset": "s3", "mode": "asynchronous", "peer_cpg": "SSD_r6"},
    ]
    rep = parse_workbook_bytes(
        _wb(replication={"fields": {**_PEER, "rtt_ms": "0"}, "rows": rows}),
        mode=RunMode.REPLICATE,
    ).provisioning_intent.replication
    assert rep is not None
    assert rep.rtt_ms == 0.0
    assert [(p.vvset, p.mode, p.rpo_minutes, p.auto_synchronize) for p in rep.protections] == [
        ("s1", "async", 15, True),
        ("s2", "sync", None, False),
        ("s3", "async", 10, True),
    ]


@pytest.mark.parametrize(("fields", "rows", "expected"), [
    (
        {**_PEER, "rtt_ms": "-1"},
        [{"vvset": "s1", "peer_cpg": "SSD_r6"}],
        "Replication tab — 'Measured round-trip time (ms)' cannot be negative.",
    ),
    (
        _PEER,
        [{"vvset": "s1", "peer_cpg": "SSD_r6", "mode": "3DC"}],
        ("Replication tab — row 's1': Mode must be 'async' or 'sync' (got '3DC'); "
        "Peer Persistence, Active Sync, SLD and 3DC are not supported in this version."),
    ),
    (
        _PEER,
        [{"vvset": "s1", "peer_cpg": "SSD_r6", "mode": "mirror"}],
        "Replication tab — row 's1': Mode must be 'async' or 'sync' (got 'mirror').",
    ),
    (
        _PEER,
        [{"vvset": "s1", "peer_cpg": "SSD_r6", "rpo_minutes": "-2"}],
        "Replication tab — row 's1': RPO must be a whole number of minutes, 1 or more (got '-2').",
    ),
    (
        _PEER,
        [{"vvset": "s1", "peer_cpg": "SSD_r6", "rpo_minutes": "1.5"}],
        "Replication tab — row 's1': RPO must be a whole number of minutes, 1 or more (got '1.5').",
    ),
    (
        {**_PEER, "rtt_ms": "10.1"},
        [{"vvset": "s1", "peer_cpg": "SSD_r6", "mode": "sync"}],
        ("Replication tab — row 's1': the measured round-trip time is 10.1 ms; "
        "sync replication over RCIP needs 10 ms or less (HPE Support Matrix)."),
    ),
    (
        _PEER,
        [{"vvset": "s1", "peer_cpg": "SSD_r6", "auto_synchronize": "nah"}],
        "Replication tab — row 's1': Auto synchronize must be 'yes' or 'no' (got 'nah').",
    ),
])
def test_replication_tab_exact_error_messages(fields, rows, expected):
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(
            _wb(replication={"fields": fields, "rows": rows}),
            mode=RunMode.REPLICATE,
        )
    assert str(exc.value) == expected


def test_replication_network_tab_valid_time_ports_and_exact_errors():
    good_net = [
        {"array": "this", "port": "0:4:4", "ip": "192.0.2.101", "netmask": "255.255.255.0", "gateway": "192.0.2.1"},
        {"array": "peer", "port": "0:4:4", "ip": "192.0.2.102", "netmask": "255.255.255.0"},
        {"array": "this", "port": "1:4:4", "ip": "192.0.2.103", "netmask": "255.255.255.0"},
        {"array": "peer", "port": "1:4:4", "ip": "192.0.2.104", "netmask": "255.255.255.0"},
    ]
    data = _wb(replication={"fields": _PEER, "rows": [{"vvset": "vvs01", "peer_cpg": "SSD_r6"}], "network": good_net})
    # Excel sometimes stores N:S:P as a time value; verify it reads back identically.
    wb = load_workbook(io.BytesIO(data))
    wb[REPLICATION_NETWORK_SHEET_NAME].cell(row=3, column=2).value = datetime.time(0, 4, 4)
    buf = io.BytesIO()
    wb.save(buf)
    rep = parse_workbook_bytes(buf.getvalue(), mode=RunMode.REPLICATE).provisioning_intent.replication
    assert [(r.side, r.nsp, r.ip, r.gateway) for r in rep.network] == [
        ("A", "0:4:4", "192.0.2.101", "192.0.2.1"),
        ("B", "0:4:4", "192.0.2.102", ""),
        ("A", "1:4:4", "192.0.2.103", ""),
        ("B", "1:4:4", "192.0.2.104", ""),
    ]


@pytest.mark.parametrize(("net", "expected"), [
    (
        [{"array": "other", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"}],
        "Replication network tab — row 'other 0:4:4': Array must be 'this' or 'peer' (got 'other').",
    ),
    (
        [{"array": "this", "port": "0:4:4"}],
        "Replication network tab — row 'this 0:4:4': missing RCIP address, Netmask.",
    ),
    (
        [{"array": "this", "port": "00:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"}],
        "Replication network tab — row 'this 00:4:4': Port must be N:S:P, like 0:4:4 (got '00:4:4').",
    ),
    (
        [{"array": "this", "port": "0:4:4", "ip": "999.0.0.1", "netmask": "255.255.255.0"}],
        "Replication network tab — row 'this 0:4:4': RCIP address '999.0.0.1' is not an IPv4 address.",
    ),
    (
        [{"array": "this", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "0.0.0.255"}],
        "Replication network tab — row 'this 0:4:4': Netmask '0.0.0.255' is not a netmask (like 255.255.254.0).",
    ),
    (
        [{"array": "this", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0", "gateway": "bad"}],
        "Replication network tab — row 'this 0:4:4': Gateway 'bad' is not an IPv4 address.",
    ),
    (
        [
            {"array": "this", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"},
            {"array": "this", "port": "0:4:4", "ip": "192.0.2.2", "netmask": "255.255.255.0"},
        ],
        "Replication network tab — row 'this 0:4:4': port 0:4:4 is named twice on the same array.",
    ),
    (
        [
            {"array": "this", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"},
            {"array": "peer", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"},
        ],
        "Replication network tab — row 'peer 0:4:4': address 192.0.2.1 is used twice.",
    ),
    (
        [
            {"array": "this", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"},
            {"array": "peer", "port": "1:4:4", "ip": "192.0.2.2", "netmask": "255.255.255.0"},
        ],
        ("Replication network tab — ports pair node to node, and these have no partner on the other "
        "array's same node: this 0:4:4, peer 1:4:4."),
    ),
    (
        [
            {"array": "this", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"},
            {"array": "peer", "port": "0:4:4", "ip": "192.0.2.2", "netmask": "255.255.255.0"},
        ],
        ("Replication network tab — the partnership needs at least 2 links: name two ports on this "
        "array and two on the peer, one per node."),
    ),
])
def test_replication_network_tab_exact_error_messages(net, expected):
    data = _wb(replication={"fields": _PEER, "rows": [{"vvset": "vvs01", "peer_cpg": "SSD_r6"}], "network": net})
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(data, mode=RunMode.REPLICATE)
    assert str(exc.value) == expected


# ------------------------------------------------------------------ iSCSI network tab


def test_iscsi_network_tab_slash31_and_exact_error_messages():
    # /31 has no network/broadcast address to avoid.
    rows = [
        {"port": "0:4:1", "vlan": "100", "ip": "192.0.2.0", "netmask": "255.255.255.254"},
        {"port": "1:4:1", "vlan": "100", "ip": "192.0.2.1", "netmask": "255.255.255.254"},
    ]
    parsed = parse_workbook_bytes(_wb(iscsi_network=rows), mode=RunMode.PROVISION_ONLY).provisioning_intent
    assert [(r.nsp, r.vlan_id, r.ip) for r in parsed.iscsi_network] == [
        ("0:4:1", 100, "192.0.2.0"),
        ("1:4:1", 100, "192.0.2.1"),
    ]


@pytest.mark.parametrize(("rows", "expected"), [
    (
        [{"vlan": "100", "ip": "192.0.2.10", "netmask": "255.255.255.0"}],
        "iSCSI network tab — row ' VLAN 100': missing Port (N:S:P).",
    ),
    (
        [{"port": "bad", "vlan": "100", "ip": "192.0.2.10", "netmask": "255.255.255.0"}],
        "iSCSI network tab — row 'bad VLAN 100': Port must be N:S:P, like 0:4:1 (got 'bad').",
    ),
    (
        [{"port": "0:4:1", "vlan": "4095", "ip": "192.0.2.10", "netmask": "255.255.255.0"}],
        "iSCSI network tab — row '0:4:1 VLAN 4095': VLAN ID must be a whole number from 1 to 4094 (got '4095').",
    ),
    (
        [{"port": "0:4:1", "vlan": "100", "ip": "bad", "netmask": "255.255.255.0"}],
        "iSCSI network tab — row '0:4:1 VLAN 100': iSCSI address 'bad' is not an IPv4 address.",
    ),
    (
        [{"port": "0:4:1", "vlan": "100", "ip": "192.0.2.10", "netmask": "0.0.0.0"}],
        "iSCSI network tab — row '0:4:1 VLAN 100': Netmask '0.0.0.0' is not a netmask (like 255.255.255.0).",
    ),
    (
        [{"port": "0:4:1", "vlan": "100", "ip": "192.0.2.10", "netmask": "255.255.255.0", "gateway": "bad"}],
        "iSCSI network tab — row '0:4:1 VLAN 100': Gateway 'bad' is not an IPv4 address.",
    ),
    (
        [{"port": "0:4:1", "vlan": "100", "ip": "192.0.2.10", "netmask": "255.255.255.0", "gateway": "198.51.100.1"}],
        "iSCSI network tab — row '0:4:1 VLAN 100': Gateway 198.51.100.1 is not on the network 192.0.2.0/24 of 192.0.2.10.",
    ),
    (
        [{"port": "0:4:1", "vlan": "100", "ip": "192.0.2.0", "netmask": "255.255.255.0"}],
        "iSCSI network tab — row '0:4:1 VLAN 100': 192.0.2.0 is the network or broadcast address of 192.0.2.0/24.",
    ),
    (
        [{"port": "0:4:1", "vlan": "100", "ip": "192.0.2.255", "netmask": "255.255.255.0"}],
        "iSCSI network tab — row '0:4:1 VLAN 100': 192.0.2.255 is the network or broadcast address of 192.0.2.0/24.",
    ),
    (
        [
            {"port": "0:4:1", "vlan": "100", "ip": "192.0.2.10", "netmask": "255.255.255.0"},
            {"port": "0:4:1", "vlan": "100", "ip": "192.0.2.11", "netmask": "255.255.255.0"},
        ],
        "iSCSI network tab — row '0:4:1 VLAN 100': port 0:4:1 has VLAN 100 twice.",
    ),
    (
        [
            {"port": "0:4:1", "vlan": "100", "ip": "192.0.2.10", "netmask": "255.255.255.0"},
            {"port": "1:4:1", "vlan": "100", "ip": "192.0.2.10", "netmask": "255.255.255.0"},
        ],
        "iSCSI network tab — row '1:4:1 VLAN 100': address 192.0.2.10 is used twice.",
    ),
    (
        [
            {"port": "0:4:1", "vlan": "100", "ip": "192.0.2.10", "netmask": "255.255.255.0"},
            {"port": "1:4:1", "vlan": "100", "ip": "198.51.100.10", "netmask": "255.255.255.0"},
        ],
        ("iSCSI network tab — VLAN 100 is on two networks: 192.0.2.0/24 on 0:4:1 and "
        "198.51.100.0/24 on 1:4:1. One VLAN is one network."),
    ),
    (
        [
            {"port": "0:4:1", "vlan": "100", "ip": "192.0.2.10", "netmask": "255.255.255.0"},
            {"port": "1:4:1", "vlan": "200", "ip": "192.0.2.11", "netmask": "255.255.255.0"},
        ],
        ("iSCSI network tab — VLAN 100 and VLAN 200 are both on 192.0.2.0/24. "
        "Give each VLAN a network of its own."),
    ),
])
def test_iscsi_network_tab_exact_error_messages(rows, expected):
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(_wb(iscsi_network=rows), mode=RunMode.PROVISION_ONLY)
    assert str(exc.value) == expected


# ------------------------------------------------------------------ Peer ports tab & cross-role guard


def test_peer_ports_tab_dedups_wwpns_and_exact_errors():
    rows = [
        {"port": "0:3:2", "source_wwpns": "20:31:00:02:ac:02:ac:38, 20310002AC02AC38; 20320002ac02ac38"},
        {"port": "1:3:2"},
    ]
    peer_ports = parse_workbook_bytes(_wb(peer_ports=rows), mode=RunMode.PROVISION_ONLY).provisioning_intent.peer_ports
    assert [(p.nsp, p.source_wwpns) for p in peer_ports.ports] == [
        ("0:3:2", ["20310002AC02AC38", "20320002AC02AC38"]),
        ("1:3:2", []),
    ]


@pytest.mark.parametrize(("rows", "expected"), [
    (
        [{"port": "bad"}],
        "Peer ports tab — row 'bad': Port must be N:S:P, like 0:3:2 (got 'bad').",
    ),
    (
        [{"port": "0:3:2", "source_wwpns": "not-a-wwpn"}],
        "Peer ports tab — row '0:3:2': 'not-a-wwpn' is not a WWPN (16 hex digits, colons allowed).",
    ),
    (
        [{"port": "0:3:2"}, {"port": "0:3:2"}],
        "Peer ports tab — port 0:3:2 is named twice.",
    ),
    (
        [{"port": "0:3:2"}, {"port": "0:3:3"}],
        ("Peer ports tab — peer ports go in pairs across nodes: name at least one port on each of two nodes "
        "(got 0:3:2, 0:3:3 only on node 0), so the migration keeps a path when a node restarts."),
    ),
])
def test_peer_ports_tab_exact_error_messages(rows, expected):
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(_wb(peer_ports=rows), mode=RunMode.PROVISION_ONLY)
    assert str(exc.value) == expected


def test_peer_port_cannot_share_a_port_with_this_arrays_rcip_row():
    net = [
        {"array": "this", "port": "0:3:2", "ip": "192.0.2.101", "netmask": "255.255.255.0"},
        {"array": "peer", "port": "0:3:2", "ip": "192.0.2.102", "netmask": "255.255.255.0"},
        {"array": "this", "port": "1:4:4", "ip": "192.0.2.103", "netmask": "255.255.255.0"},
        {"array": "peer", "port": "1:4:4", "ip": "192.0.2.104", "netmask": "255.255.255.0"},
    ]
    data = _wb(
        replication={"fields": _PEER, "rows": [{"vvset": "vvs01", "peer_cpg": "SSD_r6"}], "network": net},
        peer_ports=[{"port": "0:3:2"}, {"port": "1:3:2"}],
    )
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(data, mode=RunMode.PROVISION_ONLY)
    assert str(exc.value) == "Peer ports tab — port 0:3:2 is also on the Replication network tab; a port has one role."


# ------------------------------------------------------------------ Migration tab


def test_migration_tab_optional_only_field_still_requires_source_host():
    data = _wb(migration={"fields": {"orchestration": "array"}, "rows": []})
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(data, mode=RunMode.PROVISION_ONLY)
    assert str(exc.value) == "Migration tab — enter the source array's management address (the array the data moves from)."


# ------------------------------------------------------------------ Provisioning tab & parse_upload


@pytest.mark.parametrize(("targets_patch", "volumes", "hostsets", "hosts", "expected"), [
    (
        {"prov_default_type": "thick"}, _VOLUMES, _HOSTSETS, [],
        "Default provisioning type must be 'tpvv' or 'reduce'.",
    ),
    (
        {}, [{"name": "v1", "size_gib": "10", "provisioning_type": "thick"}], _HOSTSETS, [],
        "Volume 'v1' — Type must be 'tpvv' or 'reduce'.",
    ),
    (
        {}, [{"name": "v1", "size_gib": "ten"}], _HOSTSETS, [],
        "Volume 'v1' — Size (GiB) must be a number.",
    ),
    (
        {}, [{"name": "v1", "size_gib": "10", "vvset": "bad+set"}], _HOSTSETS, [],
        "Volume 'v1' — VV-set: the array takes only letters, digits, '.', '-' and '_' in a volume set name, not '+'. Rename it.",
    ),
    (
        {}, _VOLUMES, _HOSTSETS, [{"name": "h1", "wwpns": "1234"}],
        "Hosts tab — host 'h1' has an FC WWPN that is not 16 hex digits: 1234. A mistyped WWPN produces a zone that matches nothing.",
    ),
    (
        {}, _VOLUMES, _HOSTSETS, [{"name": "h1", "iqn": "not-an-iqn"}],
        "Hosts tab — host 'h1' has an iSCSI IQN that does not start with 'iqn.': not-an-iqn",
    ),
    (
        {}, _VOLUMES, _HOSTSETS, [{"name": "h1", "os": "aix"}],
        "Hosts tab — host 'h1' has an unrecognised OS 'aix' (esxi / windows / linux / vme).",
    ),
    (
        {}, _VOLUMES, _HOSTSETS, [{"name": "h1", "password": "pw"}],
        "Hosts tab — host 'h1' has a login password but no login username.",
    ),
    (
        {}, _VOLUMES, _HOSTSETS, [{"name": "h1", "username": "root"}],
        "Hosts tab — host 'h1' has a login but no IP address to log in to.",
    ),
])
def test_provisioning_tab_exact_error_messages(targets_patch, volumes, hostsets, hosts, expected):
    data = _wb(targets={**_TARGETS, **targets_patch}, volumes=volumes, hostsets=hostsets, hosts=hosts)
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(data, mode=RunMode.PROVISION_ONLY)
    assert str(exc.value) == expected


def test_provisioning_tab_missing_required_tab_and_absent_hosts_tab():
    missing_vol = _delete_tabs(_wb(), VOLUMES_SHEET_NAME)
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(missing_vol, mode=RunMode.PROVISION_ONLY)
    assert str(exc.value) == "The 'Volumes' tab is required for provisioning but was not found in the workbook."

    without_hosts = _delete_tabs(_wb(), HOSTS_SHEET_NAME)
    parsed = parse_workbook_bytes(without_hosts, mode=RunMode.PROVISION_ONLY)
    assert parsed.provisioning_intent.declared_hosts == []


def test_parse_upload_collects_problems_across_tabs_and_drops_bad_tabs():
    data = compose_workbook_bytes(
        base=None,
        init=_COMPLETE_INIT,
        targets=_TARGETS,
        volumes=[{"name": "v_ok", "size_gib": "10"}],
        hostsets=_HOSTSETS,
        hosts=[{"name": "bad_host", "os": "solaris"}, {"name": "ok_host", "os": "linux"}],
        replication={"fields": {**_PEER, "peer_host": "192.0.2.10"}, "rows": [{"vvset": "vvs01", "peer_cpg": "SSD_r6"}]},
        migration={"fields": {**_SOURCE, "source_host": "192.0.2.10"}, "rows": [{"host": "h1", "cpg": "SSD_r6"}]},
        snapshots=[{"source": "s1", "snapshot_now": "no", "expire_hours": "24"}],
    )
    parsed, problems = parse_upload(data)
    assert [h.name for h in parsed.provisioning_intent.declared_hosts] == ["ok_host"]
    assert parsed.provisioning_intent.replication is None
    assert parsed.provisioning_intent.migration is None
    assert parsed.provisioning_intent.snapshots is None
    assert problems == [
        "Hosts tab — host 'bad_host' has an unrecognised OS 'solaris' (esxi / windows / linux / vme).",
        "Snapshots tab — row 's1' asks for nothing: set Snapshot now to yes, or fill Every and Unit.",
        "Replication tab — the peer array (192.0.2.10) is this run's own array. Replication needs a second array: enter the OTHER array's management IP.",
        "Migration tab — the source array (192.0.2.10) is this run's own array. This run's array is the destination: enter the address of the array the data moves from.",
    ]


# ------------------------------------------------------------------ compose_workbook_bytes & _replace_row_table


def test_compose_workbook_errors_text_cells_and_adding_missing_tabs():
    with pytest.raises(ValueError, match=r"^The base is not an \.xlsx workbook\.$"):
        compose_workbook_bytes(base=b"not-a-zip")

    init_only = build_template_bytes(init_only=True)
    with pytest.raises(ValueError, match=r"^The base workbook has no 'Volumes' tab\.$"):
        compose_workbook_bytes(base=init_only, volumes=_VOLUMES)

    # Leading '=' is written as a text cell, never a formula.
    composed = compose_workbook_bytes(base=None, init={"gl_client_secret": "=1+1"}, targets=_TARGETS)
    wb = load_workbook(io.BytesIO(composed))
    secret_cell = next(r[1] for r in wb[SHEET_NAME].iter_rows(min_row=2) if r[0].value and "API Client Secret" in str(r[0].value))
    assert secret_cell.value == "=1+1" and secret_cell.data_type == "s"

    # Adding every optional tab onto an older base that predates them all.
    older = _delete_tabs(
        _wb(),
        REPLICATION_SHEET_NAME,
        REPLICATION_NETWORK_SHEET_NAME,
        ISCSI_NETWORK_SHEET_NAME,
        PEER_PORTS_SHEET_NAME,
        MIGRATION_SHEET_NAME,
        SNAPSHOTS_SHEET_NAME,
    )
    added = compose_workbook_bytes(
        base=older,
        replication={
            "fields": _PEER,
            "rows": [{"vvset": "vvs01", "peer_cpg": "SSD_r6"}],
            "network": [
                {"array": "this", "port": "0:4:4", "ip": "192.0.2.101", "netmask": "255.255.255.0"},
                {"array": "peer", "port": "0:4:4", "ip": "192.0.2.102", "netmask": "255.255.255.0"},
                {"array": "this", "port": "1:4:4", "ip": "192.0.2.103", "netmask": "255.255.255.0"},
                {"array": "peer", "port": "1:4:4", "ip": "192.0.2.104", "netmask": "255.255.255.0"},
            ],
        },
        iscsi_network=[{"port": "0:4:1", "vlan": "120", "ip": "192.0.2.11", "netmask": "255.255.255.0"}],
        peer_ports=[{"port": "0:3:2"}, {"port": "1:3:2"}],
        migration={"fields": _SOURCE, "rows": [{"host": "h1", "cpg": "SSD_r6"}]},
        snapshots=[{"source": "vvs01", "snapshot_now": "yes", "expire_hours": "24"}],
    )
    added_wb = load_workbook(io.BytesIO(added))
    assert added_wb.sheetnames == [
        SHEET_NAME,
        PROVISIONING_SHEET_NAME,
        VOLUMES_SHEET_NAME,
        HOSTS_SHEET_NAME,
        HOSTSETS_SHEET_NAME,
        "Prerequisites",
        REPLICATION_SHEET_NAME,
        REPLICATION_NETWORK_SHEET_NAME,
        ISCSI_NETWORK_SHEET_NAME,
        PEER_PORTS_SHEET_NAME,
        MIGRATION_SHEET_NAME,
        SNAPSHOTS_SHEET_NAME,
    ]
    intent = parse_workbook_bytes(added, mode=RunMode.PROVISION_ONLY).provisioning_intent
    assert intent.replication is not None and len(intent.replication.network) == 4
    assert len(intent.iscsi_network) == 1
    assert intent.peer_ports is not None and len(intent.peer_ports.ports) == 2
    assert intent.migration is not None and len(intent.migration.hosts) == 1
    assert intent.snapshots is not None and len(intent.snapshots.requests) == 1


@pytest.mark.parametrize(("kwargs", "mode", "steps", "expected"), [
    # Replication tab errors surface before Replication network errors.
    (
        {
            "replication": {
                "fields": {**_PEER, "rtt_ms": "-1"},
                "rows": [{"vvset": "s1", "peer_cpg": "SSD_r6"}],
                "network": [{"array": "other", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"}],
            },
        },
        RunMode.REPLICATE,
        None,
        "Replication tab — 'Measured round-trip time (ms)' cannot be negative.",
    ),
    (
        {
            "replication": {
                "fields": _PEER,
                "rows": [{"vvset": "s1", "peer_cpg": "SSD_r6", "mode": "mirror"}],
                "network": [{"array": "other", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"}],
            },
        },
        RunMode.REPLICATE,
        None,
        "Replication tab — row 's1': Mode must be 'async' or 'sync' (got 'mirror').",
    ),
    (
        {
            "replication": {
                "fields": {**_PEER, "failover_test": "maybe"},
                "rows": [{"vvset": "s1", "peer_cpg": "SSD_r6"}],
                "network": [{"array": "other", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"}],
            },
        },
        RunMode.REPLICATE,
        None,
        "Replication network tab — row 'other 0:4:4': Array must be 'this' or 'peer' (got 'other').",
    ),
    # Snapshots: Start hour checked before Days; Schedule name checked before Read-only.
    (
        {
            "snapshots": [
                {"source": "s1", "every": "15", "unit": "minutes", "at_hour": "2", "days": "funday", "expire_hours": "24"},
            ],
        },
        RunMode.CUSTOM,
        ["snapshots"],
        "Snapshots tab — row 's1': Start hour applies to hours and days; leave it blank for a schedule in minutes.",
    ),
    (
        {
            "snapshots": [
                {"source": "s1", "every": "1", "unit": "hours", "at_hour": "24", "days": "funday", "expire_hours": "24"},
            ],
        },
        RunMode.CUSTOM,
        ["snapshots"],
        "Snapshots tab — row 's1': Start hour must be a whole number from 0 to 23 (got '24').",
    ),
    (
        {
            "snapshots": [
                {"source": "s1", "snapshot_now": "yes", "expire_hours": "24", "schedule_name": "bad name", "read_only": "maybe"},
            ],
        },
        RunMode.CUSTOM,
        ["snapshots"],
        "Snapshots tab — row 's1': Schedule name may use letters, digits, '.', '_' and '-' only, up to 31 characters.",
    ),
    # RCIP: address checked before netmask; port-twice checked before address-twice.
    (
        {
            "replication": {
                "fields": _PEER,
                "rows": [{"vvset": "s1", "peer_cpg": "SSD_r6"}],
                "network": [{"array": "this", "port": "0:4:4", "ip": "999.0.0.1", "netmask": "0.0.0.255"}],
            },
        },
        RunMode.REPLICATE,
        None,
        "Replication network tab — row 'this 0:4:4': RCIP address '999.0.0.1' is not an IPv4 address.",
    ),
    (
        {
            "replication": {
                "fields": _PEER,
                "rows": [{"vvset": "s1", "peer_cpg": "SSD_r6"}],
                "network": [
                    {"array": "this", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"},
                    {"array": "this", "port": "0:4:4", "ip": "192.0.2.1", "netmask": "255.255.255.0"},
                ],
            },
        },
        RunMode.REPLICATE,
        None,
        "Replication network tab — row 'this 0:4:4': port 0:4:4 is named twice on the same array.",
    ),
])
def test_rule_precedence_on_two_fault_inputs(kwargs, mode, steps, expected):
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(_wb(**kwargs), mode=mode, selected_steps=steps)
    assert str(exc.value) == expected


def test_compose_refuses_table_without_expected_header_row():
    wb = Workbook()
    wb.active.title = SHEET_NAME
    ws = wb.create_sheet(VOLUMES_SHEET_NAME)
    ws.append(["Something unrelated"])
    buf = io.BytesIO()
    wb.save(buf)
    with pytest.raises(ValueError) as exc:
        compose_workbook_bytes(base=buf.getvalue(), volumes=_VOLUMES)
    assert str(exc.value) == "'Volumes' has no header row with a 'Volume name' column"
