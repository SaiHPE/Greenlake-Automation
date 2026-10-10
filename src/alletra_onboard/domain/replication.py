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

#: Support Matrix (RCIP), OS 10.5 column — research 2026-10-07 §3.
RTT_LIMIT_MS: dict[str, float] = {"sync": 10.0, "async": 200.0}
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


class ReplicationIntent(BaseModel):
    """The Replication tab, parsed. Absent on a run whose workbook has no such tab."""

    peer: EndpointCreds
    rtt_ms: float | None = None
    protections: list[ProtectionRequest] = Field(default_factory=list)
    failover_test: bool = True
    failover_group: str = ""        # blank -> the tool's own test group (TEST_GROUP)

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


class ReplicationArrayView(BaseModel):
    """Everything the Replication step read from ONE array, read-only."""

    host: str = ""
    name: str = ""
    serial: str = ""
    system_id: int | None = None        # `showsys` ID, decimal — the peer names our groups `<g>.r<id>`
    os_version: str = ""
    rc_status: str = ""                 # Started | Stopped | ""
    rc_health: str = ""                 # Normal | …
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
    the peer's target for us carries the peer's own name). `target_on_primary` / `target_on_peer`
    are the target this run uses first; `targets` lists every one; `target_by_mode` is the choice
    per sheet mode (a mode without an entry has no target it may start on)."""

    target_on_primary: str
    target_on_peer: str
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
    kind: Literal["group", "peer_vvset", "test_volume", "test_vvset"]
    name: str
    where: Literal["A", "B"] = "A"
    state: Literal["create", "exists", "conflict"] = "create"
    reason: str = ""
    calls: list[PlannedCall] = Field(default_factory=list)
    detail: dict = Field(default_factory=dict)


class ReplicationPlan(BaseModel):
    actions: list[ReplicationAction] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)      # findings + conflicts; non-empty refuses apply
    notes: list[str] = Field(default_factory=list)
    existing_groups: list[str] = Field(default_factory=list)   # R9: present, never touched
    error: str | None = None


# ------------------------------------------------------------------ apply (R4) and its removal set (R7)

class ReplicationOutcome(BaseModel):
    """What the array said for one planned write."""

    kind: Literal["group", "peer_vvset", "test_volume", "test_vvset", "volume_admit", "start", "policy"]
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
