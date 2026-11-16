# SPEC-023 — Snapshots and snapshot schedules for what the run provisions

**Status:** PROPOSED 2026-11-16 — spec, tests (expected to fail until built) and work packet. The
read-only capture ran on rack13-ARCUS (OS 10.6.0) the same night (`tests/fixtures/rack13_snap/`, §2.1)
and the read side is built (work packet step 2: the `showsched`, `createsv` and `showvv` parsers and the
WSAPI snapshot fields); nothing that writes is built. **Schedules wait on [ADR 0016](../adr/0016-snapshot-schedules-write-scoped-ssh.md)**
(PROPOSED; recommended option A). Snapshots taken now need no new decision (WSAPI).
**Tracker:** BL-21 · **Work packet:** [workpackets/BL-21.md](../workpackets/BL-21.md)
**Depends on:** SPEC-001 (plan truth), SPEC-007 (removal set), SPEC-015 (an optional tab, a step
gated on it), SPEC-002/018 (as-built sections)
**Owner (when built):** `domain/snapshots.py` (new), `application/snapshots/` (new context:
`read.py`, `plan.py`, `apply.py`, `verify.py`, `steps.py`), `application/platform/init_sheet.py`
(tab), `domain/workflow.py` (step), `adapters/array/wsapi_client.py` (snapshot calls),
`adapters/array/snap_cli_client.py` (new, ADR 0016 option A only),
`frontend/src/steps/SnapshotsStep.tsx` (new)

## 1. Problem

After provisioning, the engineer usually sets up local protection on the new volume sets: one
snapshot before the host writes anything, and a schedule that keeps snapshots for a set time. Today
that is done by hand in the array UI or CLI after the tool has left, and the as-built does not record
it. A wrong expiry fills a CPG; a schedule on the wrong set protects nothing; a schedule nobody wrote
down outlives the engagement.

## 2. What the array offers (facts, with where each comes from)

| Fact | Source | State |
|---|---|---|
| Snapshot of a volume: `POST /volumes/<vol>` `{action: "createSnapshot", parameters: {name, readOnly, expirationHours, retentionHours, comment, id}}` | `hpe3parclient` 4.5 `createSnapshot` (venv, read 2026-11-16) | confirmed in the SDK; never sent by this tool |
| Snapshot of a volume set: `POST /volumesets/<set>`, same body; `name` may be a VV name pattern | `hpe3parclient` 4.5 `createSnapshotOfVolumeSet` docstring | confirmed in the SDK; a pattern with a literal suffix (`@vvname@.initial`) is **unconfirmed: probe on the lab**. That a set's snapshots share one point in time is **confirmed (rack13-ARCUS, OS 10.6.0, 2026-11-16)** for the CLI (`help createsv`: consistent group snapshots); for WSAPI, still the live run |
| Errors include `INV_INPUT_RETAIN_GT_EXPIRE`, `NO_SNAP_CPG`, `SNAPSHOT_LIMIT_REACHED`, `EMPTY_SET`, `INV_INPUT_DUP_NAME` | same docstring | confirmed in the SDK |
| A snapshot reads back over WSAPI as `copyType` 3, `provisioningType` 3, `copyOf` = base, `readOnly`, `expirationTime8601`, `creationTime8601`, `userCPG` = the base's CPG | `tests/fixtures/rack13_wsapi/volumes.json` (12 snapshots, OS 10.5.55) | confirmed; the retention field's name is **unconfirmed** (none of the 12 had one; rack13-ARCUS on OS 10.6.0 had no snapshot at all on 2026-11-16) |
| `showvv` shows snapshots as `snp` / `vcopy`, `CopyOf`, `RO`; columns `ExpirationTime` and `RetentionEndTime` exist | `tests/fixtures/rack13_array/showvv.txt`, `showvv_listcols.txt` | confirmed; `-showcols Id,Name,Prov,Type,CopyOf,Rd,CPG,CreationTime,ExpirationTime,RetentionEndTime` runs and prints a time as `date time zone`, `--` when unset: **confirmed (rack13-ARCUS, OS 10.6.0, 2026-11-16)** (`rack13_snap/showvv_snapcols.txt`, base volumes only) |
| No separate snapshot CPG on OS 10.5: `-showcols … SnpCPG` is refused; the snapshot's `userCPG` is the base's | `showvv_listcols.txt`, `volumes.json` | confirmed |
| Data-reduction (`reduce`) volumes take snapshots | `volumes.json` (`vol1.*`, provisioningType 6, with snapshots) | confirmed |
| A schedule is `createsched "<command>" "<min> <hour> <dom> <month> <dow>" <name>`; remove `removesched -f <name>`; suspend/resume/rename `setsched` | `hpe3parclient` 4.5 `createSchedule`, `deleteSchedule`, `modifySchedule` (all over SSH); `rack13_snap/help_createsched.txt`, `help_removesched.txt` | **confirmed (rack13-ARCUS, OS 10.6.0, 2026-11-16)**: `createsched [options] <cmd> <taskschedule> <schedname>`, `createsv` is a command a schedule may run; `removesched [options] {<schedname>\|<pattern>}...` with `-f`. Sent over the tool's own SSH session: still the live run |
| No WSAPI schedule call in the SDK, and no schedule resource in WSAPI | same file; `rack13_snap/wsapi_schedules_probe.json` | **confirmed (rack13-ARCUS, OS 10.6.0, 2026-11-16)**: `GET /api/v1/schedules` answers HTTP 501, `{"code": 9, "desc": "unsupported operation for the resource"}`. Schedules are read with `showsched` and written only through the CLI |
| Captured schedule commands: `createsv -f -ro -exp 56h -retain 48h snp-@vvname@@m@@d@@H@@M@ set:<set>`; `createsv -f -ro -exp 1440m -addtoset <set> @vvname@.@y@@m@@d@@H@@M@@S@ set:<set>`; `createsv -f -addtoset <set> -exp 8h -retain 8h @vvname@.@y@@m@@d@@H@@M@@S@ set:<set>` | `tests/fixtures/rc_pair/D22U27/showsched.txt`, `E18U31/showsched.txt` (2026-10-07) | confirmed |
| `showsched` columns: SchedName, File/Command, Interval, Min, Hour, DOM, Month, DOW, CreatedBy, Status, Alert, NextRunTime; cron lists such as `0,4,8,12,16,20` and `0,15,30,45`; DOW `0` on a schedule named `…_sun`; Min printed `00` on one row, `0` on the others | same; `rack13_snap/showsched.txt` | confirmed: cron fields are compared as numbers. With no schedule the array prints `No scheduled tasks listed`: **confirmed (rack13-ARCUS, OS 10.6.0, 2026-11-16)** |
| Schedules run in the array's local time (NextRunTime printed with the array's zone) | same; `rack13_snap/showdate.txt`, `help_createsched.txt` | the zone is confirmed (`showdate`: `IST (Asia/Kolkata)` per node; WSAPI `/system` `timeZone`). The help's note that daylight-saving switchovers can run a job once, twice or not at all implies local time; that the cron hour is local time stays **unconfirmed** until a schedule runs (live step 6) |
| DSCC schedule periods: 15/20/30 minutes; 1, 2, 3, 4, 6, 8, 12 hours; 1 day; 1 month. Retention 1 hour to 1825 days | reference mirror `volume-sets/devicetype4createprotectionpolicy.md` | confirmed for DSCC; used here so a tool-made schedule is one DSCC could also express |
| Snapshot names: up to 31 characters up to OS 10.4.0, 248 from 10.4.2 | reference mirror `volume-sets/devicetype4volumesetssnapshotcreate.md`; `rack13_snap/help_createsv.txt` | confirmed for DSCC on B10000. The CLI on OS 10.6.0 takes 255; the plan keeps DSCC's 248, the stricter |
| `showsched` is **not** on the read allowlist today | `adapters/array/cli_client.py` `ALLOWED_COMMANDS` | confirmed; R3 adds it |

### 2.1 The capture of 2026-11-16 (rack13-ARCUS, OS 10.6.0)

`lab/snap_capture.py`, read-only, against rack13-ARCUS (CZ2D2K014S) instead of D22U27; the files and
what each settled are in `tests/fixtures/rack13_snap/README.md`. The array held no schedule and no
snapshot. All of the following is **confirmed (rack13-ARCUS, OS 10.6.0, 2026-11-16)** from the CLI's
own help, `GET /system` and the probe:

- WSAPI has no schedule resource (`GET /schedules`: HTTP 501, code 9). ADR 0016's premise holds.
- `createsched [options] <cmd> <taskschedule> <schedname>`; options `-f`, `-immutable`, `-interval`,
  `-no_alert`, `-no_rebalance`, `-run_once`. `createsv` is on the list of commands a schedule may run.
- Cron: five fields; minute 0-59, hour `*` or 0-23, day of month `*` or 1-31, month `*` or 1-12, day
  of week `*` or 0-6 with **0 = Sunday** (as R1 and R4 assume). Lists and ranges are allowed; no step
  syntax (`*/4`) is documented. `@hourly` to `@yearly` and `-interval 15-1440` also exist; the tool
  uses none of them.
- `createsv -exp` and `-retain` take 1 minute to 1825 days, so `HOURS_MAX = 43800` holds. The retention
  cannot be longer than the expiry (R2's last *Lock for* rule). `createsv -f` skips the confirmation
  `-retain` asks for.
- Schedule names: `createsched` takes 127 characters, `removesched` at most 31, so
  `SCHEDULE_NAME_MAX = 31` holds (a longer name could be made and never removed by name). `all` and
  `upgrade` are reserved.
- A snapshot of `set:<set>` is a consistent group snapshot, one point in time for every member.
- `removevv` refuses a volume that still has snapshots: R6's order (snapshots before volumes) is the
  array's own rule.
- `showsched` without `-all` hides the system's own schedules; with none it prints `No scheduled tasks
  listed`.
- The Virtual Lock licence (`virtualLock`) is on for rack13-ARCUS (`GET /system` `licenseState`).

**What the capture contradicts or narrows (owner to decide; R1 to R10 are unchanged so far):**

1. **Lock for above 14 days.** R2 accepts *Lock for* up to 43800 hours. The array refuses a retention
   longer than the system's `VVRetentionTimeMax` (14 days by default; rack13-ARCUS has the default,
   1209600 s). A row with *Lock for* above 336 hours passes the sheet and fails at apply. Proposed: the
   plan reads `VVRetentionTimeMax` from `GET /system` `parameters` and blocks the row.
2. **2048 virtual copies per volume.** The help states that limit. *Every 15 minutes* with *Keep for*
   above 512 hours keeps more than 2048 snapshots of each volume alive; R2 and R4 do not check it. The
   help's wording of which snapshots count (RW ones of a base or RW snapshot, RO ones of an RO
   snapshot) leaves open whether read-only snapshots of the base count. Proposed: a plan blocker when
   hours kept divided by the period exceeds 2048, until the live run says otherwise.
3. **`createsched` without `-f` can ask a question.** When it predicts too many schedule starts in one
   minute it asks for confirmation, and the tool's SSH session cannot answer. ADR 0016's form (R4 table
   row 2) has no `-f` on `createsched`. Proposed: `createsched -f "<createsv …>" "<cron>" <name>`, which
   changes the form `test_snap_cli_client.py` pins (the owner's call).
4. **`-immutable`** makes a schedule with `-retain` impossible to change or remove. The ADR 0016 form
   already refuses any option it does not list; keep it that way.
5. The capture was on OS 10.6.0, not D22U27 (OS 10.5.0). The help may differ on 10.5; the live run on
   D22U27 (section 6) is the check.

## 3. Requirements

**R1 — The sheet: an optional tab "Snapshots".** One row per volume set (or volume). A workbook
without the tab, or with the tab blank, parses exactly as today. Columns:

| Column | Default / rule |
|---|---|
| *Volume set or volume* (required) | the source; on the Volumes tab, or already on the array (checked at step time) |
| *Kind (set / volume)* | `set` |
| *Snapshot now (yes / no)* | `no`. One snapshot per member volume, named `<volume>.initial` |
| *Every* and *Unit (minutes / hours / days)* | blank = no schedule. Allowed: 15, 20, 30 minutes; 1, 2, 3, 4, 6, 8, 12 hours; 1 day |
| *Start hour (0-23, array time)* | `0`; hours and days only |
| *Days (blank = every day)* | `mon, tue, …` (three letters or full names); schedules only |
| *Keep for (hours)* (required) | how long each snapshot lives (`-exp`, WSAPI `expirationHours`); 1 to 43800 |
| *Lock for (hours, optional)* | blank. The array refuses to delete the snapshot until then (`-retain`, `retentionHours`) |
| *Read-only (yes / no)* | `yes` |
| *Schedule name (optional)* | blank = `<source>_snap`, shortened with a stable 4-hex suffix to 31 characters |

A tab, not columns on the Volumes tab: a schedule protects a set, the Volumes tab is per volume, and
a row must be able to name a set that is already on the array (as the Replication tab does since
v0.17.0).

**R2 — Validation at upload (blocking, one sentence each, prefixed *Snapshots tab — row '<source>'*).**
- *appears twice; one row per volume set or volume.*
- *: Kind must be 'set' or 'volume' (got 'x').*
- *asks for nothing: set Snapshot now to yes, or fill Every and Unit.*
- *: Every and Unit go together; fill both or neither.*
- *: every N unit is not a period the array schedules; use 15, 20 or 30 minutes, 1, 2, 3, 4, 6, 8 or 12 hours, or 1 day.*
- *: Start hour applies to hours and days; leave it blank for a schedule in minutes.*
- *: Start hour must be a whole number from 0 to 23 (got 'x').*
- *: Days applies to a schedule; fill Every and Unit, or leave Days blank.*
- *: Days must be day names separated by commas, such as mon, tue (got 'x').*
- *: Keep for must be a whole number of hours from 1 to 43800.*
- *: Lock for must be a whole number of hours from 1 to 43800, or blank.*
- *: Lock for cannot be longer than Keep for; the array refuses it.*
- *: Schedule name may use letters, digits, '.', '_' and '-' only, up to 31 characters.*
- *: schedule name 'n' is used by two rows.*
- A yes/no column holding anything else: the existing *must be 'yes' or 'no' (got 'x')* sentence.
- A run minted with the Snapshots step from a workbook without the tab: *The Snapshots step needs the
  'Snapshots' tab (the volume sets or volumes to snapshot), and this workbook has none filled in.*
  (HTTP 422, as SPEC-015 R4.)

**R3 — Read (read-only).** Over the read-only SSH client: `showversion` (name-length limit),
`showdate` (the array's time zone, shown next to *Start hour*), `showsched` (**added to
`ALLOWED_COMMANDS`; a `show*` command, said plainly in the pull request**), `showcpg`. Over WSAPI:
`GET /volumes` (already read; `parse_volumes` gains `copy_of`, `read_only`, `created`, `expires`)
and `GET /volumesets`. Never `GET /schedules`: WSAPI has no such resource (§2.1). The `showsched`
parser is pinned to the two captured lists and to the empty one on rack13-ARCUS; `showvv` with the
snapshot columns (`SHOWVV_SNAPCOLS`) is parsed too, so verify and the as-built can read an expiry from
the CLI as well as from WSAPI.

**R4 — Plan: exists / create / conflict (SPEC-001), from the same read apply will use (LESSONS 37).**
Per row:
- *Source:* absent from the array and not on the Volumes tab → blocker *"<source> is not on the
  array and not on the Volumes tab."*; on the Volumes tab but not on the array yet → blocker
  *"Provision storage first: <source> is not on the array yet."*; a set with no members → blocker.
- *Snapshot now:* per member, `<volume>.initial` absent → **create**; present with `copyOf` that
  volume → **exists**; present as anything else → **conflict**. One action per row, listing members.
  A name longer than the OS allows (31 below 10.4.2) → blocker naming the volume.
- *Schedule:* no schedule of that name → **create**; one with the same command and cron → **exists**;
  one with anything else → **conflict** (*"A schedule named n already runs '<command>' at '<cron>'.
  The tool never changes a schedule it did not make: name another on the Snapshots tab, or remove
  that one first."*). Another schedule whose command names the same source → a **note**, never a
  blocker (*"The array already takes snapshots of <source> on schedule n. Both will run."*). The
  member names plus the 13-character time suffix longer than the OS allows → blocker.
- A note per CPG: the free space read from `showcpg`, and that snapshots use the volume's own CPG.
- Every create shows the call it will make and the CLI it equals, in apply order:

| # | Write | Over | CLI shown |
|---|---|---|---|
| 1 | snapshot now, a set | WSAPI `POST /volumesets/<set>` `{action: createSnapshot, parameters: {name: "@vvname@.initial", readOnly, expirationHours[, retentionHours]}}` | `createsv [-ro] -exp <n>h [-retain <n>h] @vvname@.initial set:<set>` |
| 1 | snapshot now, a volume | WSAPI `POST /volumes/<vol>` same parameters, `name: "<vol>.initial"` | `createsv [-ro] -exp <n>h [-retain <n>h] <vol>.initial <vol>` |
| 2 | schedule | ADR 0016 option A: `ArraySnapCliClient.write(createsched …)`; option C: shown as a line to paste | `createsched "createsv -f [-ro] -exp <n>h [-retain <n>h] @vvname@.@y@@m@@d@@H@@M@@S@ <set:s or vol>" "<cron>" <name>` |

The cron is built from the row: minutes → `0,15,30,45 * * * <dow>`; hours → `0 <h0,h1,…> * * <dow>`
(start hour stepping by N, `*` when N is 1); 1 day → `0 <start hour> * * <dow>`; `<dow>` is `*` or
`0`–`6` with 0 = Sunday. Every 4 hours from 0 gives `0 0,4,8,12,16,20 * * *`, the captured
`test_CRV_snapschedule` fields; every day at 23 gives `0 23 * * *`, the captured `patchisched` ones.

**R5 — Approve and apply.** Nothing is written until the operator ticks *"I have reviewed this plan
and authorise creating these snapshots and schedules on <array>. The schedules keep running after
this run ends."* and clicks *Create snapshots and schedules* (409 on a blocker or conflict; the
approval clears on every new read, LESSONS 6). Order: (1) every snapshot now over WSAPI, then
(2) every schedule. Stop at the first refusal, report the row and the array's words. After each
`createsched`, `showsched` is read back; the row fails unless the schedule is there, `active`, with
the planned command and cron (cron fields compared as numbers: `00` is `0`). A refusal is judged against the array's own refusal texts, pinned
from the capture (LESSONS 39), including the SDK's *"The schedule format is <minute> <hour> <dom>
<month> <dow> …"* sentence.

**R6 — Removal set (SPEC-007; pasted, never run).** Exactly what this apply created, in this order,
ahead of any provisioning lines when the as-built unions them:
1. `removesched -f <name>` per schedule created (first, so it takes no more snapshots);
2. `removevv -f <snapshot>` per snapshot created now, found by diff (`copyOf` one of the source's
   members, present after and not before), never by the planned name;
3. a note: *Snapshots the schedule takes expire on their own after N hours. To remove them sooner,
   remove each with removevv -f.* When *Lock for* was set: *The array refuses to remove them before
   the lock ends (<time>).*
`RemovalItem.kind` gains `schedule` and `snapshot`; the shared order becomes schedule → snapshot →
vlun → vvset → volume → hostset → host, so a base volume is never removed before its snapshots.

**R7 — Verify (read-only).** After apply and on demand (*Check snapshots*): each snapshot now exists,
`copyOf` its base, read-only as asked, expiry within 10 minutes of creation + *Keep for*. Each
schedule is in `showsched`, `active`, command and cron as planned, with a next run time. Snapshots
the schedule has taken since (`copyOf` a member, created after the schedule) are counted. Verdict per
row: **Scheduled, next run <time>** · **Taking snapshots (n so far)** · **Not scheduled (reason)**.

**R8 — As-built.** A *Snapshots* section after *Provisioning performed* (after *Replication* when
present), only when the run has the tab: per row, the schedule in words (*every 4 hours from 00:00,
every day, kept 24 hours, read-only*), its status and next run, the snapshots taken now, the
snapshots the schedules hold at generation time (read then, never copied from the plan), other
schedules on the same sources marked *not configured by this run*, the calls with their CLI lines,
and the R6 block, plus one `removevv -f` line per snapshot the schedules hold at that moment.

**R9 — Step and modes.** `WorkflowPhase.STORAGE_SNAPSHOT`; registry entry `snapshots`
("Snapshots", kind `snapshot`) after `failover_test`, before `verify`. Presets unchanged: the step is
picked in *Custom* (open question 1). When the tab is filled and the chosen mode lacks the step, the
sheet review says *"The Snapshots tab is filled in; pick the Snapshots step to apply it."*

**R10 — UI (one page, `StepShell` / `useStepState`).**
```
Snapshots                                              [StatusLine: Plan ready · 2 to create]
Array time: IST (from the array)
┌ What the workbook asks for ───────────────────────────────────────────────────────────┐
│ zz_sn_vvs (set, 2 volumes)  Snapshot now · every 4 hours from 00:00 · kept 24 h · RO │
└───────────────────────────────────────────────────────────────────────────────────────┘
Plan                       State     What                                   [Show 2 commands]
  Snapshot now zz_sn_vvs   Create    zz_sn_vol01.initial, zz_sn_vol02.initial
  Schedule zz_sn_vvs_snap  Create    every 4 hours, kept 24 hours
Notes: SSD_r6 has 3.1 TiB free; snapshots use the volume's own CPG.
▸ Schedules already on the array (folded)
[ ] I have reviewed this plan and authorise ... The schedules keep running after this run ends.
                                         [Read the array again]  [Create snapshots and schedules]
Result → Removal set (Copy · Download .txt) → [Check snapshots]
```
A mockup in `frontend/mockups` is reviewed before the page is built (LESSONS 22).

## 4. Data contract (names the tests use)

```python
# application/platform/init_sheet.py
SNAPSHOTS_SHEET_NAME = "Snapshots"
SNAPSHOT_COLUMNS  # (key, header, required) in R1's order; keys: source, kind, snapshot_now, every,
                  # unit, at_hour, days, expire_hours, retain_hours, read_only, schedule_name
compose_workbook_bytes(..., snapshots: list[dict[str, str]] | None = None)
# R2's sentences are checked per row in the order R2 lists them; the first that applies is raised.

# domain/snapshots.py
SnapshotUnit = Literal["minutes", "hours", "days"]
ALLOWED_EVERY = {"minutes": (15, 20, 30), "hours": (1, 2, 3, 4, 6, 8, 12), "days": (1,)}
HOURS_MAX = 43800                 # help createsv: -exp / -retain up to 1825 days (built)
SCHEDULE_NAME_MAX = 31            # help removesched: at most 31 characters (built)
SCHEDULE_PATTERN = "@vvname@.@y@@m@@d@@H@@M@@S@"
NOW_SUFFIX = ".initial"

def derive_schedule_name(source: str) -> str
def schedule_cron(every: int, unit: SnapshotUnit, at_hour: int = 0, days: list[int] | None = None) -> str

class SnapshotRequest(BaseModel):
    source: str; kind: Literal["set", "volume"] = "set"; snapshot_now: bool = False
    every: int | None = None; unit: SnapshotUnit | None = None; at_hour: int = 0
    days: list[int] = []          # 0 = Sunday … 6 = Saturday; empty = every day
    expire_hours: int; retain_hours: int | None = None; read_only: bool = True
    schedule_name: str = ""
    source_ref -> str             # "set:<s>" or "<vol>"
    name -> str                   # schedule_name or derive_schedule_name(source)
    createsv_command() -> str     # "createsv -f -ro -exp 24h @vvname@.@y@@m@@d@@H@@M@@S@ set:s"
    createsched_command() -> str  # 'createsched "<createsv>" "<cron>" <name>'

class SnapshotIntent(BaseModel): requests: list[SnapshotRequest]
# ProvisioningIntent.snapshots: SnapshotIntent | None = None

class ArraySchedule(BaseModel):  # built
    name; command; interval; minute; hour; dom; month; dow; created_by; status; alert; next_run
    cron -> str                   # "<minute> <hour> <dom> <month> <dow>"

class SnapshotArrayView(BaseModel):
    name = ""; os_version = ""; time_zone = ""
    volumes: list[ArrayVolumeRecord]; vvsets: dict[str, list[str]]
    schedules: list[ArraySchedule]; cpg_free_mib: dict[str, int]

class SnapshotAction(BaseModel):
    kind: Literal["snapshot", "schedule"]; name; source; state: PlanState; reason = ""
    members: list[str] = []; cli: str = ""; call: str = ""
class SnapshotPlan(BaseModel): actions; notes: list[str]; blockers: list[str]

# application/snapshots/read.py (built)
def parse_showsched(text: str) -> list[ArraySchedule]
def parse_createsv(command: str) -> dict   # read_only, expire, retain, add_to_set, pattern, source; {} if not createsv
SHOWVV_SNAPCOLS = "showvv -showcols Id,Name,Prov,Type,CopyOf,Rd,CPG,CreationTime,ExpirationTime,RetentionEndTime"
def parse_showvv_snapcols(text: str) -> list[dict[str, str]]   # keyed by the header; "--" reads as ""
# application/snapshots/plan.py
def plan_snapshots(intent, view, *, planned_volumes=frozenset(), planned_vvsets=frozenset()) -> SnapshotPlan
# adapters/array/snap_cli_client.py (ADR 0016 option A)
def snap_write_refusal(command: str) -> str | None
```

## 5. Non-goals

Schedules on the peer array (DSCC `isRemote`), coordinated snapshots with Remote Copy, snapshot
windows (from/until hour), monthly schedules, changing, suspending or renaming a schedule, restore,
promote or clone, exporting a snapshot to a host, application-consistent snapshots (VSS, VMware
quiesce), the DSCC protection-policy API (ADR 0016 option B).

## 6. Verification

**Unit (written 2026-11-16 as expected failures, `strict=True`; each turns green when built):**
`tests/unit/test_snapshots_sheet.py` (R1, R2), `test_snapshots_domain.py` (cron, names, commands,
R4 plan, R6 order, R9), `test_snapshots_read.py` (R3 parsers on the captured `showsched` and
`volumes.json`), `test_snap_cli_client.py` (ADR 0016 option A form, `showsched` on the read list).
`test_snapshots_read.py` is green since 2026-11-16 and also pins the rack13-ARCUS capture (empty
`showsched`, `showvv` snapshot columns, the `/schedules` probe, the help's limits and forms).

**Capture before code (read-only): done 2026-11-16** on rack13-ARCUS (OS 10.6.0) rather than D22U27
→ `tests/fixtures/rack13_snap/` (help of `createsched`, `createsv`, `removesched`, `setsched`,
`showsched`, `removevv`; `showsched`; `showdate`; `showvv` snapshot columns; WSAPI `/system`,
`/volumes`, `/volumesets`, and the `/schedules` probe). It held no schedule and no snapshot, so a
populated `showsched` on OS 10.6 and a snapshot's `showvv` time columns are still to capture (live
steps 4 and 5 give both).

**Live run (lab D22U27; must pass before BL-21 closes):**
1. Nothing named `zz_sn_*` on the array; `showsched` saved.
2. Custom run *Provision storage → Snapshots → Verify → As-built*: `zz_sn_vol01`/`02` (1 GiB) in
   `zz_sn_vvs`; Snapshots row `zz_sn_vvs`, now yes, every 15 minutes, keep 2 hours.
3. Plan shows 2 creates, the CLI lines and the CPG note; approve; apply: 2 writes done.
4. `showvv` shows `zz_sn_vol01.initial`, `zz_sn_vol02.initial`, `snp`, `RO`, expiry about 2 hours out
   (this settles the `@vvname@.initial` pattern over WSAPI).
5. `showsched` shows `zz_sn_vvs_snap`, `active`, command and cron as planned (settles the quoted form
   over our SSH exec).
6. Wait 16 minutes; *Check snapshots* says *Taking snapshots (2 so far)*.
7. Read the array again: the plan says *exists* twice and creates nothing (LESSONS 37).
8. A second run whose row names schedule `zz_sn_vvs_snap` with *Keep for 3*: *conflict*, nothing
   written.
9. As-built generated: the Snapshots section with the schedule in words and the removal block.
10. Paste the removal set: accepted line by line (judged on the array's refusal texts); then the
    provisioning removal set; nothing `zz_sn_*` left; `showsched` equals step 1 apart from next run
    times; the lab's other schedules untouched.

## 7. Open questions for the owner

1. Presets: add *Snapshots* to *Provision only*, *Both* and *Provision, then replicate*, or keep it
   in *Custom* (proposed)?
2. ADR 0016: option A (proposed), B, C or D.
3. Is *Lock for* (`-retain`) licensed on every B10000 (on 3PAR it needed Virtual Lock)? What does the
   array say when it is not? Until known, the column stays optional and blank by default.
   *2026-11-16:* `virtualLock` is licensed on rack13-ARCUS; every B10000 is still open. New: the array
   caps *Lock for* at `VVRetentionTimeMax` (14 days by default), §2.1 item 1.
4. Does WSAPI take `@vvname@.initial` as a volume-set snapshot name, and are the members' snapshots
   taken at one point in time? (live step 4) *2026-11-16:* for the CLI, `createsv … set:<set>` is one
   point in time (`help createsv`); the WSAPI name pattern is still open.
5. Does the cron hour run in the array's local time? (live step 6, against `showdate`)
   *2026-11-16:* the help's daylight-saving note implies local time; still to see on the live run.
6. Upper bound of `-exp` / `expirationHours` on OS 10.5 (DSCC documents 1825 days for retention).
   *Settled for the CLI 2026-11-16:* 1 minute to 1825 days (43800 hours) for `-exp` and `-retain` on
   OS 10.6.0; WSAPI's `expirationHours` bound is assumed the same.
7. Schedule name rules and the number of schedules an array allows. *Settled in part 2026-11-16:*
   31 characters (`removesched`; `createsched` takes 127), `all` and `upgrade` reserved. The help gives
   no limit on the number of schedules, only a recommended number of starts per minute.
8. Does DSCC show a CLI-made schedule, and does it then manage or convert it? (look in DSCC after
   the live run)
9. Snapshot now naming: `<volume>.initial` (proposed) or a dated name? A fixed name is what keeps a
   rerun from taking a second one.
10. The three changes §2.1 proposes: a plan blocker for *Lock for* above `VVRetentionTimeMax`, a plan
    blocker past 2048 snapshots per volume, and `createsched -f` in ADR 0016's form.

## 8. Size

Domain and sheet (~200 lines), parsers (~80), plan (~150), apply (~120), verify (~90), write client
(~80, option A), as-built (~90), step page (~250), about 45 unit tests. One release.
