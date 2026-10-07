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
