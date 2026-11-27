"""Operator approval token for array writes (STANDARD S3, ADR 0031).

An `Approval` is an in-memory value issued only by `RunCoordinator.issue_approval` after the
operator has reviewed and ticked a plan (or authorised the failover test). It carries the run id,
purpose, credentials for the arrays the reviewed plan names, and a `spent` flag. It is never
stored or serialised, and compares by identity only (`eq=False`).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel

from alletra_onboard.domain.shared import EndpointCreds, Fabric

Purpose = Literal["storage", "rc_groups", "rc_partnership", "snapshots", "failover", "zoning"]
Side = Literal["A", "B"]
SaveRecord = Callable[[BaseModel], None]


class ApprovalError(RuntimeError):
    """A device write was attempted without a live, matching operator approval."""


def require_approval(approval: object) -> Approval:
    """Return `approval` when it is an `Approval`, else raise `ApprovalError`."""
    if not isinstance(approval, Approval):
        raise ApprovalError("No valid operator approval was provided.")
    return approval


def _empty_arrays() -> Mapping[Side, EndpointCreds]:
    return MappingProxyType({})


def _empty_switches() -> Mapping[Fabric, EndpointCreds]:
    return MappingProxyType({})


@dataclass(eq=False)
class Approval:
    run_id: str
    purpose: Purpose
    arrays: Mapping[Side, EndpointCreds] = field(default_factory=_empty_arrays)
    switches: Mapping[Fabric, EndpointCreds] = field(default_factory=_empty_switches)
    spent: bool = False
    save_record: SaveRecord | None = None

    def __post_init__(self) -> None:
        self.arrays = MappingProxyType(dict(self.arrays))
        self.switches = MappingProxyType(dict(self.switches))

    def require_live(self) -> None:
        """Raise ApprovalError once this approval has been spent."""
        if self.spent:
            raise ApprovalError("This approval has already been used. Review and approve a new plan first.")

    def require_saver(self) -> SaveRecord:
        """Return the in-progress record saver bound by `run_approved`; never silently absent."""
        self.require_live()
        if self.save_record is None:
            raise ApprovalError("This approval has no apply record saver bound.")
        return self.save_record

    def creds_for(self, purpose: Purpose, side: Side) -> EndpointCreds:
        """Return the credentials for `side` when this approval is live and matches `purpose`."""
        self.require_live()
        if self.purpose != purpose:
            raise ApprovalError(f"This approval is for {self.purpose}, not {purpose}.")
        creds = self.arrays.get(side)
        if creds is None:
            raise ApprovalError(f"This approval does not include array {side}.")
        return creds

    def switch_creds_for(self, purpose: Purpose, fabric: Fabric) -> EndpointCreds:
        """Return the switch credentials for `fabric` when this approval is live and matches `purpose`."""
        self.require_live()
        if self.purpose != purpose:
            raise ApprovalError(f"This approval is for {self.purpose}, not {purpose}.")
        creds = self.switches.get(fabric)
        if creds is None:
            raise ApprovalError(f"This approval does not include fabric {fabric} switch.")
        return creds
