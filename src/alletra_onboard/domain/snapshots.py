"""Snapshot-context models (SPEC-023): what the array holds for snapshots and schedules.

Only the read side is here so far (work packet BL-21 step 2): the limits the array's own help states
and one schedule as `showsched` prints it. The request, plan and action models (step 1) are not
built yet.
"""

from __future__ import annotations

from pydantic import BaseModel

#: `help createsv` (rack13-ARCUS, OS 10.6.0, 2026-11-16): `-exp` and `-retain` take 1 minute to
#: 1825 days. 1825 days is 43800 hours.
HOURS_MAX = 43800
#: `help createsched` allows 127 characters, but `help removesched` takes at most 31: a longer name
#: could be created and never removed by name.
SCHEDULE_NAME_MAX = 31


class ArraySchedule(BaseModel):
    """One row of `showsched`, as printed. Cron fields stay text (`00` and `0` both occur)."""

    name: str
    command: str
    interval: str
    minute: str
    hour: str
    dom: str
    month: str
    dow: str
    created_by: str
    status: str
    alert: str
    next_run: str

    @property
    def cron(self) -> str:
        return f"{self.minute} {self.hour} {self.dom} {self.month} {self.dow}"
