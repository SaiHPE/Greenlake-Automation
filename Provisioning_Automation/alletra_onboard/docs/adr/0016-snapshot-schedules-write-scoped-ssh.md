# ADR 0016 — How the tool creates snapshot schedules

**Status:** accepted 2026-11-17 (owner's decision), with the changes below; follows ADR 0025 ·
**Amends:** ADR 0001 (SSH is read-only), through ADR 0025's rule for SSH writes ·
**Departs from:** ADR 0006 (snapshots cloud-first) and the SCOPE line that names the DSCC client as
needed for snapshots · **Keeps:** ADR 0012 (no switch writes), ADR 0015 (its client and forms are not
widened) · **Spec:** [SPEC-023](../specs/SPEC-023-snapshots.md) · **Tracker:** BL-21 ·
**Work packet:** [workpackets/BL-21.md](../workpackets/BL-21.md)

## Context

BL-21 asks the tool to protect the volumes it provisions with snapshots: one taken now, and a
schedule that keeps taking them, each with an expiry. Two different things, with two different
control planes:

- **A snapshot now** has a WSAPI call. The `hpe3parclient` 4.5 in the venv has `createSnapshot`
  (`POST /volumes/<vol>` `{action: createSnapshot, parameters: {name, readOnly, expirationHours,
  retentionHours}}`) and `createSnapshotOfVolumeSet` (`POST /volumesets/<set>`, same body; the name
  may be a VV name pattern). It goes through the existing plan, approve, apply and removal machinery
  like `createVolume`. No decision needed.
- **A schedule** has no WSAPI call. Every schedule function in `hpe3parclient` 4.5 (`createSchedule`,
  `modifySchedule`, `suspendSchedule`, `resumeSchedule`, `deleteSchedule`, `getSchedule`) builds a CLI
  line (`createsched`, `setsched`, `removesched`, `showsched`) and sends it over the SDK's own SSH
  channel (`client.py` lines 4660 to 4860, read 2026-11-16). `GET /api/v1/schedules` answers HTTP 501,
  code 9, *unsupported operation for the resource*, on all four lab arrays (rack13-ARCUS OS 10.6.0,
  2026-11-16; D22U27 10.5.0, E18U31 10.5.60, VZ 10.5.51, 2026-11-17). The DSCC Block Storage API can
  create one as a protection policy of type `schedule` (reference mirror,
  `volume-sets/devicetype4createprotectionpolicy.md`): option B below.

What the lab arrays hold (read-only captures, SPEC-023 §2.1 and §2.2):

- D22U27 (`tests/fixtures/d22u27_snap/showsched.txt`): seven schedules, all active. Three run
  `createsv -f [-ro] -exp <n>h|m|d [-retain <n>h|d] [-addtoset <set>] <pattern> set:<vvset>`
  (`test_CRV_snapschedule`, `Pol-999`, `Test`); four run `compactcpg`.
- VZ (`vz_snap/showsched.txt`): one schedule, suspended, running `syncrcopy`.
- E18U31 was set up again on 2026-10-22: its `patchisched` schedule of 2026-10-07 is gone
  (`rc_pair/E18U31/showsched.txt` stays its record). rack13-ARCUS holds none.

A schedule is a name, a CLI command the array runs, and five cron fields. **A schedule is a command
the array will run later, as often as the cron says, with nobody watching.** That is the risk this
ADR is about: a write path for `createsched` that checks only the first word would let any command
in through the schedule.

The help of `createsched` and `createsv`, captured on the four arrays, settles the limits:
`-exp` and `-retain` take 1 minute to 1825 days (43,800 hours); a retention no longer than the
expiry and no longer than the system's `VVRetentionTimeMax` (14 days by default, the value on all
four arrays); 2048 virtual copies per volume; schedule names of at most 31 characters on OS 10.5
(127 on 10.6.0; `removesched` takes 31 on both); `all` and `upgrade` reserved. `createsched` without
`-f` asks for a confirmation when it predicts too many schedule starts in one minute, and the tool's
SSH session cannot answer it. On 10.6.0, `-immutable` makes a schedule with `-retain` impossible to
change or remove.

ADR 0025 (accepted the same day) sets one rule for every write over the array's SSH: exact forms,
only inside an approved apply, only on the plan's objects, an undo written before the write, a
read-back after it, no prompts, one client per kind. This ADR is the snapshot-schedule kind.

## Options

**A. A write-scoped SSH client that may run one command form: `createsched -f` wrapping a
`createsv` of exactly the planned source.** A new `ArraySnapCliClient`
(`adapters/array/snap_cli_client.py`), built only inside the apply of a snapshot plan the operator
approved, like ADR 0015's client. The whole command is checked, including the command inside the
quotes.
*For:* the operator gets the same experience as every other write (plan, tick, apply, verify,
removal set). Same pattern as ADR 0015, already reviewed and live. One command form; the blast radius
is snapshots of the run's own sources, each one expiring.
*Against:* a second SSH write kind. The quoted form has never been sent over our `exec_command` (the
SDK sends it through its own SSH helper): it is probed live before the client is built (LESSONS 28).

**B. The DSCC Block Storage API (`protectionPolicyType: schedule`).**
*For:* REST, no SSH write; DSCC shows and manages the schedule as a protection policy; it is the
route ADR 0006 chose for snapshots. Much of the client exists already: OAuth client credentials
(`adapters/greenlake/auth.py`), per-endpoint rate limiting and `202 + Location` polling
(`adapters/greenlake/http_client.py`), all live on onboarding.
*Against:* what is missing. The regional base URL (the tool calls only the global surface today);
`block-storage.*` permissions on the API client (onboarding needs none); the application-set ids the
policy works on (the tool provisions volume sets over WSAPI and never reads DSCC's ids); and a stable
version: the request paths carry only `v1alpha1` (developer.greenlake.hpe.com/docs/greenlake/services/
block-storage/public, read 2026-11-17). It also needs the array onboarded in DSCC, so it cannot serve a
provisioning-only run on an array the tool did not onboard. Research of 2026-10-07 §5 (3) found that
DSCC converts a CLI-made Remote Copy group one way into its own volume set, so the two planes do not
mix freely. Periods are DSCC's (15, 20, 30 minutes; 1 to 12 hours; a day; a month), which SPEC-023
adopts anyway.

**C. Command set only: the tool writes the `createsched` lines, the operator pastes them, the tool
verifies with `showsched`.**
*For:* no new write path. The plan, the lines and the verify are the same code as A, minus the apply
of the schedule rows.
*Against:* the owner already rejected this shape for arrays (ADR 0015). The operator types into an
array CLI what the tool could have run with the same checks; a mistyped paste is not checked before it
runs.

**D. Snapshots only (WSAPI); no schedules.**
*For:* nothing new to decide. *Against:* BL-21 asks for schedules; this ships half of it.

## Decision

**Option A**, with these changes from the proposal (review of 2026-11-17, accepted by the owner).

1. **The form carries `-f`.** Without it the array can stop for a confirmation (ADR 0025 condition 6).
   The one form is

   ```
   createsched -f "createsv -f [-ro] -exp <1..43800>h @vvname@.@y@@m@@d@@H@@M@@S@ <source>" "<min> <hour> * * <dow>" <name>
   ```

   `<source>` is `set:<vvset>` or a volume name. `-exp` is mandatory, so no schedule keeps snapshots
   for ever. The cron fields allow digits, commas and `*` only. `<name>` uses SPEC-023 R2's
   characters, 1 to 31 of them, and is not `all` or `upgrade`.
   `-f` also turns off the array's check on how many schedules start in one minute. So the plan makes
   that check itself (SPEC-023 R4, *Starts per minute*): D22U27 already starts four schedules at
   00:00, five on Sundays.
2. **No lock in this ADR.** A lock (`-retain` on a schedule, `retentionHours` on a snapshot now)
   cannot be undone until it ends, so under ADR 0025 condition 4 it is not allowed until a later ADR
   allows it by name. The client refuses `-retain`; the plan blocks a row with *Lock for*. When it is
   allowed, `-retain` is capped at the array's `VVRetentionTimeMax`, read from `GET /system`
   (1,209,600 s, 336 hours, on all four lab arrays), in the plan and in the client, as well as at
   `-exp`.
3. **2048 snapshots per volume.** The plan blocks a row when one volume's existing snapshots, plus the
   snapshot taken now, plus the ones the schedule keeps alive at once, exceed 2048 (the help's limit).
4. **Quotes only where the form puts them.** The shared `_FORBIDDEN_CHARS` refuses `"` (BL-46, with
   `' { } [ ] \`). This client lets `"` through only at the four fixed positions of the form: around
   the inner command and around the cron. Anywhere else it is refused, and so is every other
   character on the shared list (`\ [ ] { } $ ;` among them), inside the quotes as well as outside.
   So the inner command cannot carry the help's own `-comment \"…\"`, a Tcl substitution or a second
   command. Tests refuse the near-misses: no `-f`; the `createsched` options `-immutable`, `-run_once`,
   `-interval`, `-no_alert`; the `createsv` options `-rcopy`, `-comment`, `-addtoset`, `-retain`; an
   `rcgroup:` source; the names `all`, `upgrade` and anything over 31 characters.
5. **The tool finds its own snapshots by name and parent, never by parent alone.** The removal set,
   verify's count and the as-built match `copyOf` one of the source's members **and** the name the
   tool asked for (`<member>.initial` for the snapshot now; `<member>.` and twelve digits for the
   schedule's). Remote Copy makes snapshots of the same members (`rcpy.41.269.5` on D22U27, 57 on
   VZ); without the name, the removal set could name objects the plan never made.
6. **A suspended schedule of the same name is a conflict**, not *exists*: the plan would otherwise
   report a schedule as in place that takes no snapshots.
7. **This departs from ADR 0006**, which routes snapshots cloud-first (DSCC where entitled, WSAPI for
   depth), and from SCOPE.md's *Where the tool is today*, which names the DSCC client as needed for
   snapshots. Snapshots now and schedules go to the array directly. Option B stays open as its own
   work item if DSCC must show and manage the schedules.
8. **The form is pinned to the help of all four captures** (rack13-ARCUS, D22U27, E18U31, VZ), not
   only rack13-ARCUS: on OS 10.5 `createsched` itself caps names at 31 characters.

And, from the proposal, unchanged:

- A separate class, not a wider `ArrayRcCliClient`: each write client's list stays readable on one
  screen, and a reviewer can see what each feature may do.
- `removesched`, `setsched` and everything else stay off the client. The removal set is pasted by the
  operator (SPEC-007 R4); the tool never changes a schedule it did not make.
- `showsched` joins the read allowlist (`ALLOWED_COMMANDS`). It is a `show*` command and changes
  nothing; it is listed here because every allowlist change is said plainly.

## How the client meets ADR 0025

| Condition | `ArraySnapCliClient` |
|---|---|
| 1. Exact forms | The one form above; the inner `createsv` checked as an exact form of its own; `"` only at the four fixed positions; a test that accepts the form and tests that refuse each near-miss (item 4). |
| 2. Only inside an approved apply | Built by `application/snapshots/apply.py` after the server checks the approved plan id. The Console, verify, the as-built and discovery keep the read client. |
| 3. Only on the plan's objects | Built with the (schedule name, source) pairs of the plan's create rows; a well-formed `createsched` on any other name or source is refused and never sent. A client built without them writes nothing. |
| 4. An undo before the write | `removesched -f <name>` goes into the run's removal set before `createsched` is sent. The schedule's snapshots expire on their own (`-exp` is mandatory). No lock (item 2). |
| 5. A read-back after the write | `showsched` after each `createsched`: the schedule is there, `active`, with the planned command and cron, and every other schedule is as it was. Otherwise apply stops. |
| 6. No prompts | `createsched -f` and `createsv -f`. The starts-per-minute check `-f` turns off is made by the plan (item 1). |
| 7. One client per kind | Snapshot schedules only, in their own class, with one form. |

## First slice

Built in this order (work packet): the Snapshots tab, `showsched` read-only, the snapshot now over
WSAPI without a lock, verify, and an as-built section that records every schedule on the array; the
plan's schedule rows say *not written yet*. Then the schedule write client (step 9A), without
`-retain`.

**Confirmed live before it is built** (each a lab run the owner approves first):

1. A quoted `createsched -f` sent over the tool's own `exec_command`, read back with `showsched`, then
   removed with `removesched -f`.
2. `@vvname@.initial` taken as a volume-set snapshot name over WSAPI.
3. Whether DSCC or the array UI shows a schedule made from the CLI.
4. Whether DSCC made `Pol-999` and `Test` (each adds its snapshots to a set with `-addtoset`,
   `set-test999…` and `Test.Snapset`, which looks like DSCC's snapset model). If so, the tool copies
   DSCC's form; that is a new form, with its tests, said plainly in the pull request.
5. Whether read-only snapshots of the base count toward the 2048 limit. Until then the plan counts
   them.

## Consequences

- AGENTS.md hard rule 2 (ADR 0025's wording) names `ArraySnapCliClient` beside `ArrayRcCliClient`
  when step 9A ships; `adapters.instructions.md` and `docs/ARCHITECTURE.md` say the same.
- Schedules outlive the run. The plan, the result, the verify and the as-built say so in words: *the
  array will take a snapshot of <source> every <period> until someone removes the schedule*
  (LESSONS 31: name the write as loudly as what is withheld).
- Snapshots use space in the volume's own CPG (OS 10.5 has no separate snapshot CPG:
  `tests/fixtures/rack13_array/showvv_listcols.txt`, `SnpCPG` refused). Expiry is mandatory, so a
  schedule cannot fill a CPG without bound; the plan states the CPG's free space as a note.
- Not decided here: the lock; remote (peer-side) schedules; snapshot windows (from/until hour); months
  as a period; changing or suspending a schedule. Each would be a new form and a new decision.
