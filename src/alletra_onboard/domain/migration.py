"""Migration-context models (SPEC-027): what the Migration tab asks for.

The run's array is the destination B10000, reached with the run's one array credential (ADR 0013).
The source array (a 3PAR, Primera or Alletra 9000) is a read-only step credential, held like the
replication peer and the switches: the tool only reads it, over the SSH read client, and never writes
to it. Peer Motion, in this array's UI or DSCC, does the import with its own source account (ADR 0020).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from alletra_onboard.domain.shared import EndpointCreds

MigrationType = Literal["online", "minimally disruptive", "offline"]
MigrationProvisioning = Literal["thin", "reduce"]
Orchestration = Literal["array UI", "DSCC"]

MIGRATION_TYPES: tuple[MigrationType, ...] = ("online", "minimally disruptive", "offline")
MIGRATION_PROVISIONING: tuple[MigrationProvisioning, ...] = ("thin", "reduce")
ORCHESTRATIONS: tuple[Orchestration, ...] = ("array UI", "DSCC")


class MigrationHostRequest(BaseModel):
    """One row of the Migration tab: a host on the source array whose volumes move to this array."""

    host: str                                       # its name on the SOURCE array
    type: MigrationType = "online"
    cpg: str                                        # the CPG on this (the destination) array
    provisioning: MigrationProvisioning = "thin"


class MigrationIntent(BaseModel):
    """The Migration tab, parsed. Absent on a run whose workbook has no such tab."""

    source: EndpointCreds
    orchestration: Orchestration = "array UI"
    hosts: list[MigrationHostRequest] = Field(default_factory=list)
