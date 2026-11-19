"""Replication-context models (SPEC-015): what the Replication tab asks for.

One array's run protects its own volume sets to ONE peer array over an existing Remote Copy
partnership. Direction is always this run's array -> the peer. The peer credential is a step
credential like the switches' (ADR 0013 covers the run's own array).
"""

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field

from alletra_onboard.domain.shared import EndpointCreds

ReplicationMode = Literal["async", "sync"]
#: SPEC-031 R2: a Remote Copy target's transport, the `Type` column of `showrcopy targets`.
Transport = Literal["IP", "FC"]
#: How every sentence names a transport.
TRANSPORT_WORDS: dict[str, str] = {"IP": "over RCIP", "FC": "over Fibre Channel"}

#: Support Matrix, OS 10.5 column — research 2026-10-07 §3. Over Fibre Channel (RCFC) the limit is 10 ms
#: for sync and for async (research 2026-11-17 §7). Read it through `rtt_limit_ms`, which names the transport.
RTT_LIMIT_MS: dict[str, dict[str, float]] = {"IP": {"sync": 10.0, "async": 200.0}, "FC": {"sync": 10.0, "async": 10.0}}


def rtt_limit_ms(transport: str, mode: str) -> float:
    """The round-trip time limit of one mode over one transport (0 for a mode the table does not know)."""
    return RTT_LIMIT_MS[transport].get(mode, 0.0)


def rtt_limit_text(transport: str, mode: str) -> str:
    """'async replication over Fibre Channel needs 10 ms or less': every sentence names the transport."""
    return f"{mode} replication {TRANSPORT_WORDS[transport]} needs {rtt_limit_ms(transport, mode):g} ms or less"

#: A group name may be at most 22 characters under `mirror_config` (the peer side appends `.r<id>`).
GROUP_NAME_MAX = 22
#: RPO in whole minutes; the array period is RPO / 2 (its minimum period is 15 s).
RPO_MINUTES_DEFAULT = 10
RPO_MINUTES_MIN = 1

#: The failover test's own objects (SPEC-015 R3) — created and removed by the Replication step.
TEST_VOLUME = "zz_rc_test_v01"
TEST_VVSET = "zz_rc_test"
TEST_GROUP = "zz_rc_test_rcg"
TEST_PEER_VVSET = "zz_rc_test_rc"
TEST_VOLUME_GIB = 1


def derive_group_name(vvset: str) -> str:
    """`<volume set>_rcg`, shortened with a stable 4-hex suffix when that would exceed 22 characters
    (the suffix is a hash of the full set name, so the same set always derives the same group)."""
    name = f"{vvset}_rcg"
    if len(name) <= GROUP_NAME_MAX:
        return name
    tag = hashlib.sha1(vvset.encode("utf-8")).hexdigest()[:4]
    keep = GROUP_NAME_MAX - len("_rcg") - len(tag) - 1
    return f"{vvset[:keep]}_{tag}_rcg"


class ProtectionRequest(BaseModel):
    """One Remote Copy group to create over one volume set (a Protection row)."""

    vvset: str
    mode: ReplicationMode = "async"
    rpo_minutes: int | None = RPO_MINUTES_DEFAULT   # async only; None for sync
    peer_cpg: str
    peer_vvset: str = ""                             # blank -> `<vvset>_rc`
    auto_synchronize: bool = True
    auto_recover: bool = True

    @property
    def group_name(self) -> str:
        return derive_group_name(self.vvset)

    @property
    def peer_vvset_name(self) -> str:
        return self.peer_vvset or f"{self.vvset}_rc"

    @property
    def period_seconds(self) -> int | None:
        """What `setrcopygroup period` / WSAPI `syncPeriod` get: RPO / 2, in seconds."""
        return self.rpo_minutes * 30 if self.mode == "async" and self.rpo_minutes else None


class RcipPortRequest(BaseModel):
    """One row of the Replication network tab (SPEC-021 R1): an RCIP port the run uses, on this array
    (`A`) or the peer (`B`)."""

    side: Literal["A", "B"]
    nsp: str
    ip: str
    netmask: str
    gateway: str = ""

    @property
    def node(self) -> str:
        return self.nsp.split(":")[0]


def pair_ports(network: list[RcipPortRequest]) -> list[tuple[RcipPortRequest, RcipPortRequest]]:
    """(this array's port, the peer's port) node to node, in sheet order (SPEC-021 R1). A row without a
    partner on the same node is left out; the sheet parser refuses such a sheet before it gets here."""
    a_rows = [r for r in network if r.side == "A"]
    b_by_node: dict[str, list[RcipPortRequest]] = {}
    for r in network:
        if r.side == "B":
            b_by_node.setdefault(r.node, []).append(r)
    pairs = []
    for a in a_rows:
        if b_by_node.get(a.node):
            pairs.append((a, b_by_node[a.node].pop(0)))
    return pairs


class ReplicationIntent(BaseModel):
    """The Replication tab, parsed. Absent on a run whose workbook has no such tab."""

    peer: EndpointCreds
    rtt_ms: float | None = None
    protections: list[ProtectionRequest] = Field(default_factory=list)
    failover_test: bool = True
    failover_group: str = ""        # blank -> the tool's own test group (TEST_GROUP)
    # SPEC-021: the RCIP ports to set up. Empty = the partnership must exist already (SPEC-016).
    network: list[RcipPortRequest] = Field(default_factory=list)

    @property
    def failover_group_name(self) -> str:
        return self.failover_group or TEST_GROUP


# ------------------------------------------------------------------ what the arrays say (SPEC-016 R1)

class RcipPort(BaseModel):
    """One row of `showport -rcip` — a configured Remote Copy IP port."""

    nsp: str
    state: str = ""
    ip: str = ""
    netmask: str = ""
    gateway: str = ""
    mtu: str = ""
    rate: str = ""


class RcTransport(BaseModel):
    """One row of `showrctransport -rcip` — a port and the peer address it talks to."""

    nsp: str
    state: str = ""
    ip: str = ""
    peer_ip: str = ""
    netmask: str = ""
    gateway: str = ""


class RcTarget(BaseModel):
    """`showrcopy targets`: Name ID Type Status Options Policy."""

    name: str
    id: int | None = None
    type: str = ""
    status: str = ""
    options: str = ""
    policy: str = ""            # mirror_config | no_mirror_config

    @property
    def mirror_config(self) -> bool:
        return "mirror_config" in self.policy and not self.policy.startswith("no_")

    @property
    def is_fc(self) -> bool:
        """SPEC-031 R2: a Fibre Channel target. Its Options carry the peer's node WWN and its links address
        the peer's port WWNs (an IP target's links address RCIP addresses)."""
        return self.type.upper() == "FC"


class RcLink(BaseModel):
    """`showrcopy links`: Target Node Address Status. `receive` rows are this array's own inbound ports."""

    target: str
    nsp: str
    address: str
    status: str = ""

    @property
    def up(self) -> bool:
        return self.status.lower() == "up"

    @property
    def inbound(self) -> bool:
        return self.target == "receive"


class RcGroupVolume(BaseModel):
    local_name: str
    local_id: int | None = None
    remote_name: str = ""
    remote_id: int | None = None
    sync_status: str = ""       # Synced | Syncing | Stopped | Stale | NotSynced | …
    sync_progress: str = ""     # "100%" when the array prints "Syncing (100%)"
    last_sync: str = ""         # NA on sync groups; a timestamp on periodic ones


class RcGroup(BaseModel):
    """One group block of `showrcopy groups`."""

    name: str
    target: str
    status: str = ""            # Started | Stopped | Failsafe
    role: str = ""              # Primary | Secondary | Primary-Rev | Secondary-Rev
    mode: str = ""              # Sync | Periodic | Async
    options: list[str] = Field(default_factory=list)   # the policies (auto_recover, over_per_alert, …)
    period: str = ""            # periodic groups: "5m" (the Options column's `Period 5m`)
    last_sync: str = ""         # periodic primaries: the Options column's `Last-Sync <timestamp>`
    volumes: list[RcGroupVolume] = Field(default_factory=list)

    @property
    def mode_key(self) -> str:
        """The sheet's word for the array's mode: Periodic -> async."""
        return "sync" if self.mode.lower() == "sync" else "async"

    @property
    def volume_names(self) -> list[str]:
        return [v.local_name for v in self.volumes]


class RcVolumeDetail(BaseModel):
    """One volume row of `showrcopy -d groups <group>`: every column the array prints, as printed
    (`NA`, `none` and blanks kept). Column meanings from the array's `clihelp -col showrcopy`."""

    local_name: str
    local_id: int | None = None
    remote_name: str = ""
    remote_id: int | None = None
    sync_status: str = ""           # Synced | Syncing (45%) | Stopped | Stale | NotSynced | …
    resync_snapshot: str = ""       # Resync_ss: the starting point of the remote volume ("none" or a snapshot)
    sync_snapshot: str = ""         # Sync_ss: the destination point of a resync in progress
    volume_iteration: str = ""      # VV_iter, e.g. "185493/71"
    resync_iteration: str = ""      # R_iter
    sync_iteration: str = ""        # S_iter
    last_sync: str = ""             # LastSyncTime: NA on sync groups, a time on periodic ones
    local_set: str = ""             # LocalSet (not printed by every OS)
    remote_set: str = ""            # RemoteSet


class RcGroupDetail(BaseModel):
    """One group block of `showrcopy -d groups <group>`: the group's configuration and every volume in it.
    `rpo_minutes` is the workbook's, filled by Verify (the array prints the period, not the RPO)."""

    name: str
    id: int | None = None
    target: str = ""
    status: str = ""                # Started | Stopped | Failsafe | …
    role: str = ""                  # Primary | Secondary, optionally -Rev
    mode: str = ""                  # Sync | Periodic | Async
    local_user_cpg: str = ""        # LocalUserCpg
    local_snap_cpg: str = ""        # LocalSnapCpg (Primera OS 4.x prints it)
    remote_user_cpg: str = ""       # RmUserCpg
    remote_snap_cpg: str = ""       # RmSnapCpg
    options: list[str] = Field(default_factory=list)    # the policies
    period: str = ""                # periodic groups: "5m"
    last_sync: str = ""             # periodic primaries: the Options column's Last-Sync
    rpo_minutes: int | None = None
    volumes: list[RcVolumeDetail] = Field(default_factory=list)


class PortRole(BaseModel):
    """One row of `showport`: what a port is (SPEC-021 R2)."""

    nsp: str
    mode: str = ""              # target | initiator | peer
    state: str = ""             # ready | offline | loss_sync | …
    type: str = ""              # host | disk | free | rcip | file | cluster | …
    protocol: str = ""          # FC | iSCSI | IP | NVMe | …
    node_wwn: str = ""          # FC rows: the array's node WWN (a peer port has a `0202` one of its own)
    port_wwn: str = ""          # FC rows: the port's own WWN, the address an FC Remote Copy link uses

    @property
    def rcip_capable(self) -> bool:
        """An Ethernet peer port that is free or already RCIP — the only kind the tool addresses."""
        return self.protocol.upper() == "IP" and self.mode == "peer" and self.type in ("free", "rcip")


class ReplicationArrayView(BaseModel):
    """Everything the Replication step read from ONE array, read-only."""

    host: str = ""
    name: str = ""
    serial: str = ""
    system_id: int | None = None        # `showsys` ID, decimal — the peer names our groups `<g>.r<id>`
    os_version: str = ""
    rc_status: str = ""                 # Started | Stopped | "" (Remote Copy not configured)
    rc_health: str = ""                 # Normal | …
    ports: dict[str, PortRole] = Field(default_factory=dict)   # SPEC-021 R2, from `showport`
    fc_node_wwn: str = ""               # the first FC row's (SPEC-021); SPEC-031 reads every one: fc_node_wwns
    rcip_ports: list[RcipPort] = Field(default_factory=list)
    transports: list[RcTransport] = Field(default_factory=list)
    targets: list[RcTarget] = Field(default_factory=list)
    links: list[RcLink] = Field(default_factory=list)
    groups: list[RcGroup] = Field(default_factory=list)
    cpg_free_mib: dict[str, int] = Field(default_factory=dict)
    vvsets: dict[str, list[str]] = Field(default_factory=dict)
    volume_size_mib: dict[str, int] = Field(default_factory=dict)
    read_error: str | None = None

    @property
    def rc_started(self) -> bool:
        return self.rc_status.lower() == "started"

    @property
    def rcip_addresses(self) -> set[str]:
        return {p.ip for p in self.rcip_ports if p.ip}

    @property
    def fc_node_wwns(self) -> set[str]:
        """Every FC node WWN the array shows (SPEC-031 R1). The one source, with `fc_port_wwns`, for "which
        WWNs belong to this array" (LESSONS 41): the partnership and the as-built read both from here."""
        wwns = {p.node_wwn for p in self.ports.values() if p.node_wwn}
        return (wwns | {self.fc_node_wwn}) if self.fc_node_wwn else wwns

    @property
    def fc_port_wwns(self) -> set[str]:
        """Every FC port WWN the array shows: what the other array's FC links address."""
        return {p.port_wwn for p in self.ports.values() if p.port_wwn}

    def group(self, name: str) -> RcGroup | None:
        return next((g for g in self.groups if g.name == name), None)

    def volume_group(self, volume: str) -> str | None:
        """The group a volume already belongs to, if any (a volume is in at most one)."""
        for g in self.groups:
            if volume in g.volume_names:
                return g.name
        return None


class PartnerTarget(BaseModel):
    """One target on the primary whose outbound links point at the peer, with the peer's target that
    answers over the same ports. A pair may have several (HPE's own layout for mixed modes is one
    target per mode over separate links); `modes` are the sheet words for the groups it already carries."""

    name: str
    peer_name: str = ""
    transport: Transport = "IP"
    links_up: int = 0
    links_total: int = 0
    peer_links_up: int = 0
    peer_links_total: int = 0
    mirror_config: bool = True
    modes: list[str] = Field(default_factory=list)      # of groups not planned by this run
    groups: int = 0
    own_modes: list[str] = Field(default_factory=list)  # of this run's groups already on it (rerun)


class Partnership(BaseModel):
    """The targets that point at each other, found by LINK ADDRESS (never by name — on the lab pair
    the peer's target for us carries the peer's own name): RCIP addresses over IP, port WWNs over Fibre
    Channel (SPEC-031 R3). A pair has one transport. `target_on_primary` / `target_on_peer`
    are the target this run uses first; `targets` lists every one; `target_by_mode` is the choice
    per sheet mode (a mode without an entry has no target it may start on)."""

    target_on_primary: str
    target_on_peer: str
    transport: Transport = "IP"
    links_primary_up: int = 0
    links_peer_up: int = 0
    links_primary_total: int = 0
    links_peer_total: int = 0
    mirror_config: bool = True
    targets: list[PartnerTarget] = Field(default_factory=list)
    target_by_mode: dict[str, str] = Field(default_factory=dict)

    def target_for(self, mode: str) -> PartnerTarget | None:
        name = self.target_by_mode.get(mode)
        return next((t for t in self.targets if t.name == name), None) if name else None


class ReplicationReport(BaseModel):
    """R1 + R2: both arrays read, the partnership resolved, the blocking findings."""

    primary: ReplicationArrayView
    peer: ReplicationArrayView
    partnership: Partnership | None = None
    findings: list[str] = Field(default_factory=list)      # blocking, one sentence each
    notes: list[str] = Field(default_factory=list)
    error: str | None = None
    # SPEC-031 R3: the arrays show IP and FC targets towards each other; the step plans nothing.
    mixed_transports: bool = False
    # SPEC-031 R6: the round-trip time typed on the Replication tab (it stands in for the measurement over
    # Fibre Channel) and the modes this run's groups replicate in, for the limit it is held to.
    rtt_ms: float | None = None
    modes: list[str] = Field(default_factory=list)


# ------------------------------------------------------------------ the link check (SPEC-020)

#: `checkrclink startclient <N:S:P> <addr> <time>`: the array's documented range for <time>.
LINK_CHECK_TIME_MIN = 300
LINK_CHECK_TIME_MAX = 172800
LINK_CHECK_TIME_DEFAULT = 600


class LinkPair(BaseModel):
    """One outbound link of A toward B, as the two ports and addresses `checkrclink` needs (R1)."""

    nsp_a: str
    ip_a: str
    nsp_b: str
    ip_b: str

    @property
    def label(self) -> str:
        return f"A {self.nsp_a} → B {self.nsp_b} ({self.ip_b})"


class LinkCheckResult(BaseModel):
    """What `checkrclink` said for one pair (R3)."""

    pair: LinkPair
    status: Literal["measured", "failed"] = "measured"
    latency_ms: float | None = None
    pings_lost_pct: float | None = None
    detail: str = ""            # the array's words on failure
    output: str = ""            # the client's output up to the stop


class LinkCheck(BaseModel):
    """The run's link check: every pair measured, against the limit of each mode on the tab."""

    at: str = ""
    duration_s: int = LINK_CHECK_TIME_DEFAULT
    results: list[LinkCheckResult] = Field(default_factory=list)
    unchecked: list[str] = Field(default_factory=list)     # pairs not checked, with the reason
    modes: list[str] = Field(default_factory=list)         # the sheet modes this run configures
    notes: list[str] = Field(default_factory=list)
    error: str | None = None

    @property
    def worst_ms(self) -> float | None:
        values = [r.latency_ms for r in self.results if r.latency_ms is not None]
        return max(values) if values else None

    @property
    def measured(self) -> bool:
        return self.error is None and any(r.status == "measured" for r in self.results)

    def over_limit(self) -> list[str]:
        """The modes on the tab whose RTT limit the worst latency exceeds. The link check measures RCIP links only."""
        worst = self.worst_ms
        if worst is None:
            return []
        return [m for m in self.modes if worst > rtt_limit_ms("IP", m)]


# ------------------------------------------------------------------ the plan (SPEC-016 R3)

class PlannedCall(BaseModel):
    """One write the apply will make, as the WSAPI call and the CLI it is equivalent to. `seq` is
    its position in the apply order across the whole plan (R4): a group's start comes after the
    peer volume set that groups its secondaries."""

    where: Literal["A", "B"]
    wsapi: str
    cli: str
    seq: int = 0


class ReplicationAction(BaseModel):
    kind: Literal["group", "peer_vvset", "test_volume", "test_vvset", "rcip_port", "rc_service", "target"]
    name: str
    where: Literal["A", "B"] = "A"
    state: Literal["create", "exists", "conflict"] = "create"
    reason: str = ""
    calls: list[PlannedCall] = Field(default_factory=list)
    detail: dict = Field(default_factory=dict)


#: SPEC-021: the action kinds that set up the partnership (over SSH, ADR 0015).
PARTNERSHIP_KINDS = ("rcip_port", "rc_service", "target")


class ReplicationPlan(BaseModel):
    actions: list[ReplicationAction] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)      # findings + conflicts; non-empty refuses apply
    notes: list[str] = Field(default_factory=list)
    existing_groups: list[str] = Field(default_factory=list)   # R9: present, never touched
    error: str | None = None
    # Set when the step holds the plan for approval; the apply must quote it back (BL-52).
    plan_id: str = ""

    @property
    def sets_up_partnership(self) -> bool:
        """SPEC-021 R3: the plan creates ports, Remote Copy or targets; its apply does only that."""
        return any(a.kind in PARTNERSHIP_KINDS and a.state == "create" for a in self.actions)


# ------------------------------------------------------------------ apply (R4) and its removal set (R7)

class ReplicationOutcome(BaseModel):
    """What the array said for one planned write."""

    kind: Literal["group", "peer_vvset", "test_volume", "test_vvset", "volume_admit", "start", "policy",
                  "rcip_port", "rc_service", "target", "ping", "links"]
    name: str
    where: Literal["A", "B"] = "A"
    status: Literal["created", "exists", "failed", "skipped"] = "created"
    detail: str = ""


class ReplicationResult(BaseModel):
    outcomes: list[ReplicationOutcome] = Field(default_factory=list)
    removals_a: list[str] = Field(default_factory=list)    # CLI lines the operator pastes on A, in order
    removals_b: list[str] = Field(default_factory=list)    # … and on B
    notes: list[str] = Field(default_factory=list)
    groups_created: list[str] = Field(default_factory=list)
    error: str | None = None


# ------------------------------------------------------------------ verify (R6)

GroupVerdict = Literal["replicating", "syncing", "not_replicating"]


class GroupVerification(BaseModel):
    group: str
    peer_group: str = ""                 # `<group>.r<id>` as the peer names it
    verdict: GroupVerdict = "not_replicating"
    detail: str = ""                     # one line for the operator
    next_step: str = ""                  # HPE's documented action when not replicating
    volumes_total: int = 0
    volumes_synced: int = 0
    config: RcGroupDetail | None = None  # `showrcopy -d groups <group>` on this array: settings and every volume


class ReplicationVerification(BaseModel):
    links_ok: bool = False
    links_detail: str = ""
    groups: list[GroupVerification] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    error: str | None = None


# ------------------------------------------------------------------ failover test (SPEC-017)

#: WSAPI `recoverRemoteCopyGroupFromDisaster` action codes (hpe3parclient), with the CLI verb each is.
DR_ACTION_FAILOVER = 7      # setrcopygroup failover: the secondary becomes Primary-Rev
DR_ACTION_RECOVER = 9       # setrcopygroup recover: the old primary becomes Secondary-Rev, sync back
DR_ACTION_RESTORE = 10      # setrcopygroup restore: natural direction, started

FailoverOutcome = Literal["pending", "ok", "failed", "skipped"]
FailoverResult = Literal["passed", "failed", "aborted"]


class FailoverSide(BaseModel):
    """What one array showed for the group after a step (`showrcopy groups <group>`)."""

    array: str = ""                 # the array's name
    group: str = ""                 # the group's name on that array (the peer adds .r<id>)
    present: bool = True
    role: str = ""                  # Primary | Secondary | Primary-Rev | Secondary-Rev
    status: str = ""                # Started | Stopped | Failsafe
    mode: str = ""
    volumes: int = 0
    synced: int = 0
    last_sync: str = ""             # periodic groups: the newest LastSyncTime seen

    @property
    def summary(self) -> str:
        if not self.present:
            return "not on the array"
        bits = [f"{self.role}/{self.status}", f"{self.synced}/{self.volumes} Synced"]
        if self.last_sync and self.last_sync != "NA":
            bits.append(f"last sync {self.last_sync}")
        return " · ".join(bits)


class FailoverStepRecord(BaseModel):
    """One row of the SPEC-017 R2 table, with what was measured (R3)."""

    seq: int
    title: str
    where: Literal["P", "S", "-"] = "-"
    action: str = ""                # the WSAPI call, or "(read)"
    cli: str = ""                   # the CLI equivalent
    expected: str = ""
    started_at: str = ""
    ended_at: str = ""
    seconds: float | None = None
    primary: FailoverSide | None = None
    peer: FailoverSide | None = None
    outcome: FailoverOutcome = "pending"
    detail: str = ""


class FailoverRecord(BaseModel):
    group: str
    peer_group: str = ""
    mode: str = ""                  # sync | async
    primary_array: str = ""
    peer_array: str = ""
    started_at: str = ""
    ended_at: str = ""
    steps: list[FailoverStepRecord] = Field(default_factory=list)
    result: FailoverResult = "aborted"
    failed_step: int | None = None
    time_to_failover_s: float | None = None     # step 2: until the peer shows Primary-Rev
    time_to_synced_s: float | None = None       # step 5: until every volume is Synced after recover
    data_loss_bound: str = ""                   # async: the last sync before failover and how old it was
    observed_state: str = ""                    # on failure: both sides, one line
    recovery_action: str = ""                   # on failure: HPE's documented way back, as CLI lines
    error: str | None = None
