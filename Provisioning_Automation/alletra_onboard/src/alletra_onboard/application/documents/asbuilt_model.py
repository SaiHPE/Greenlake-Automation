"""AsBuiltData — the per-deployment data model passed between as-built parsing and rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AsBuiltData:
    """The per-deployment values that fill the as-built (from read-only array reads + operator input)."""

    customer: str = ""       # operator-supplied — fills <Customer Name> / <Customer name>
    site: str = ""           # operator-supplied — the array doesn't store a Location/Site
    application_workload: str = ""   # operator-supplied — <Application/Workload> (Introduction)
    purpose: str = ""                # operator-supplied — <Purpose of using Block storage>
    name: str = ""
    model: str = ""
    serial_no: str = ""
    controller_nodes: str = ""
    os_version: str = ""
    drive_cages: str = ""
    cache_gb: str = ""
    nvme_ssd_disks: str = ""
    raw_capacity: str = ""
    raid: str = ""
    host_ports: str = ""
    mgmt_ip: str = ""
    netmask: str = ""
    gateway: str = ""
    ntp: str = ""
    dns: str = ""
    inventory: str = ""      # showinventory, verbatim
    checkhealth: str = ""    # checkhealth -svc -detail, verbatim
    # SPEC-002 array sections — raw `show*` text, parsed by the renderer like inventory/checkhealth.
    showhost_d: str = ""
    showhostset: str = ""
    showvv: str = ""
    showvv_cpg: str = ""     # showvv -showcols …UsrCPG… (R7); "" when that read failed
    showvvset: str = ""
    showvlun_t: str = ""
    showvlun_a: str = ""
    showport: str = ""               # read for Table 01; SPEC-024 R7 takes each port's state from it
    showport_iscsivlans: str = ""    # SPEC-024 R7: the VLAN-tagged iSCSI addresses
    showport_par: str = ""           # SPEC-025 R9: each port's connection mode and type
    showport_peer: str = ""          # SPEC-025 R9: the array's own listing of its peer ports
    read_errors: dict[str, str] = field(default_factory=dict)   # command -> error text (R6)
    # SPEC-002 run sections — the run's event payloads (JSON-shaped); None when the step did not run.
    zoning_plan: dict[str, Any] | None = None
    zoning_report: dict[str, Any] | None = None
    zoning_rendered: dict[str, Any] | None = None      # {commands: {fabric: [..]}, aliases, selected_pairs}
    provisioning_plan: dict[str, Any] | None = None
    provisioning_result: dict[str, Any] | None = None
    provisioning_applied_at: str = ""
    provisioning_removals: list[dict[str, Any]] = field(default_factory=list)   # RemovalItem dicts from EVERY apply in the run (SPEC-007)
    path_verification: dict[str, Any] | None = None
    # SPEC-018: replication. All None/empty when the workbook has no Replication tab (R4).
    replication_tab: dict[str, Any] | None = None            # {peer_host, rows: [{vvset, mode, rpo_minutes, peer_cpg}], failover_test}
    replication_report: dict[str, Any] | None = None         # replication.previewed -> report (JSON)
    replication_plan: dict[str, Any] | None = None           # replication.previewed -> plan (JSON)
    replication_result: dict[str, Any] | None = None         # replication.applied / .apply.failed -> result (JSON)
    # SPEC-021: every apply's removal lines, newest apply first (its groups go before the partnership a
    # first apply set up: removercopytarget refuses while a group still uses the target)
    replication_removals_a: list[str] = field(default_factory=list)
    replication_removals_b: list[str] = field(default_factory=list)
    # SPEC-021: every apply in run order, each with the plan previewed before it: {"plan", "result"}
    replication_applies: list[dict[str, Any]] = field(default_factory=list)
    replication_applied_at: str = ""
    replication_primary: object | None = None      # ReplicationArrayView read when the document is made (R3)
    replication_peer: object | None = None         # ReplicationArrayView of the peer, same moment
    # BL-64: `showrcopy -d groups <group>` on this array for each group this run configured, same moment:
    # group -> RcGroupDetail, and group -> why it could not be read
    replication_details: dict[str, Any] = field(default_factory=dict)
    replication_details_errors: dict[str, str] = field(default_factory=dict)
    link_check: dict[str, Any] | None = None                 # SPEC-020 R6: replication.link_checked -> link_check (JSON)
    failover_record: dict[str, Any] | None = None            # SPEC-017 R6; None = the test did not run
    # SPEC-028 R3: the file side, read when the document is made. No section when `file_report` is
    # None (no File ports and the service off) and the read did not fail.
    file_ports: list[Any] = field(default_factory=list)  # EthernetPort, from showport -file
    file_report: object | None = None               # FileReport
    file_read_error: str = ""                       # the read failed: named in the section and the warnings
    # SPEC-023 R8: snapshots. snapshots_tab is None when the workbook has no Snapshots tab.
    snapshots_tab: list[dict[str, Any]] | None = None        # SnapshotRequest dicts, one per row
    snapshots_plan: dict[str, Any] | None = None             # snapshots.previewed -> plan (JSON)
    snapshots_result: dict[str, Any] | None = None           # the latest snapshots.applied / .apply.failed -> result
    snapshots_applies: list[dict[str, Any]] = field(default_factory=list)   # every apply in run order: {"plan", "result"}
    snapshots_applied_at: str = ""
    snapshots_view: object | None = None           # SnapshotArrayView read when the document is made
    commands: list[dict[str, Any]] = field(default_factory=list)   # SPEC-019 R2: the run's command log, without output
    # SPEC-026: the handover reads, raw (handover.READS names the command for each); a failed one is in
    # read_errors. handover_read_at is None when the reads were not made: the section is then left out.
    showdate: str = ""
    showalert_d: str = ""
    showsys_space: str = ""
    handover_read_at: datetime | None = None
    run_created_at: datetime | None = None         # R4: "Before this run" compares each alert with it
    trusted_devices: list[dict[str, Any]] = field(default_factory=list)   # ADR 0026: DevicePinInfo dicts, fingerprints only
    # SPEC-024 R7: the sheet's iSCSI network rows (IscsiVlanRequest dicts), and the (port, VLAN) pairs a
    # plan of this run had to add, so an interface found now is marked "set up by this run".
    iscsi_network_rows: list[dict[str, Any]] = field(default_factory=list)
    iscsi_set_up_in_run: list[tuple[str, int]] = field(default_factory=list)
    # SPEC-025 R9: the Peer ports tab's rows (PeerPortRequest dicts), the run's last plan that set ports
    # (its commands, pasted by a consultant in the first slice) and the last read after the paste.
    peer_ports_rows: list[dict[str, Any]] = field(default_factory=list)
    peer_ports_plan: dict[str, Any] | None = None
    peer_ports_result: dict[str, Any] | None = None
