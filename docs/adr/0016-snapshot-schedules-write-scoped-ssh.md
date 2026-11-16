# ADR 0016 — How the tool creates snapshot schedules

**Status:** PROPOSED 2026-11-16 — the owner decides. Nothing is built until this is accepted.
**Would amend:** ADR 0001 (SSH is read-only) and AGENTS.md hard rule 2, only if option A is taken ·
**Keeps:** ADR 0012 (no switch writes), ADR 0015 (its client and allowlist are not widened) ·
**Spec:** [SPEC-023](../specs/SPEC-023-snapshots.md) · **Tracker:** BL-21

## Context

BL-21 asks the tool to protect the volumes it provisions with snapshots: one taken now, and a
schedule that keeps taking them, each with an expiry. Two different things, with two different
control planes:

- **A snapshot now** has a WSAPI call the tool already ships. The `hpe3parclient` 4.5 in the venv
  has `createSnapshot` (`POST /volumes/<vol>` `{action: createSnapshot, parameters: {name, readOnly,
  expirationHours, retentionHours}}`) and `createSnapshotOfVolumeSet` (`POST /volumesets/<set>`, same
  body; the name may be a VV name pattern). It goes through the existing plan, approve, apply and
  removal machinery like `createVolume`. No decision needed.
- **A schedule** has no WSAPI call that we know of. Every schedule function in `hpe3parclient` 4.5
  (`createSchedule`, `modifySchedule`, `suspendSchedule`, `resumeSchedule`, `deleteSchedule`,
  `getSchedule`) builds a CLI line (`createsched`, `setsched`, `removesched`, `showsched`) and sends it
  over the SDK's own SSH channel (`client.py` lines 4660 to 4860, read 2026-11-16). The DSCC Block
  Storage API can create one as a protection policy of type `schedule` (reference mirror,
  `volume-sets/devicetype4createprotectionpolicy.md`), but the tool has no DSCC API client today.
  Whether WSAPI 1.15 has a schedule resource at all was **unconfirmed**: the capture script
  (`lab/snap_capture.py`) asks `GET /api/v1/schedules` and records whatever the array answers.
  *Answered 2026-11-16 (rack13-ARCUS, OS 10.6.0):* HTTP 501, code 9, "unsupported operation for the
  resource". WSAPI has no schedule resource. The same capture's `help createsched` shows that
  `createsched` without `-f` can ask for a confirmation the tool's SSH session cannot give, and that
  `-immutable` makes a schedule impossible to remove (SPEC-023 §2.1).

What the lab arrays already hold (`tests/fixtures/rc_pair/*/showsched.txt`, captured 2026-10-07)
shows the shape a schedule takes on OS 10.5: a name, a CLI command the array runs, and five cron
fields. Three of the seven schedules there run `createsv -f [-ro] -exp <n>h|m [-retain <n>h]
[-addtoset <set>] <pattern> set:<vvset>`; the other four run `compactcpg`. **A schedule is a command
the array will run later, as often as the cron says, with nobody watching.** That is the risk this
ADR is about: a write path for `createsched` that checks only the first word would let any command
in through the schedule.

Hard rule 2 says array SSH is read-only, with one exception (ADR 0015's `ArrayRcCliClient`, Remote
Copy links and targets only). ADR 0015 set the precedent: the owner rejected a pasted command set for
array-side writes because both ends are B10000 arrays with one CLI dialect; a command set exists for
switches because switches are heterogeneous. The same reasoning applies here.

## Options

**A. A second write-scoped SSH client that may run one command form: `createsched` wrapping a
`createsv` of exactly the planned source (recommended).**
A new `ArraySnapCliClient` (`adapters/array/snap_cli_client.py`) with `SNAP_WRITE_FORMS`, built
only inside the apply of a snapshot plan the operator approved, exactly like ADR 0015's client. The
form is checked for its whole shape, **including the command inside the quotes**:

```
createsched "createsv -f [-ro] -exp <1..43800>h [-retain <1..43800>h] @vvname@.@y@@m@@d@@H@@M@@S@ <source>" "<min> <hour> * * <dow>" <name>
```

where `<source>` is `set:<vvset>` or a volume name, `-exp` is mandatory (the 43,800-hour upper
bound is unconfirmed, SPEC-023 open question 6) (no schedule may keep
snapshots for ever), and the cron fields allow digits, commas and `*` only. `removesched`, `setsched`
and anything else stay off the list: the removal set is pasted by the operator (SPEC-007 R4), and the
tool never changes a schedule it did not make.
*For:* the operator gets the same experience as every other write (plan, tick, apply, verify,
removal set). Same pattern as ADR 0015, already reviewed and live. One command form; blast radius is
snapshots of the run's own sources, each one expiring.
*Against:* a second exception to hard rule 2. The AGENTS.md rule, ADR 0001's consequence line and
`adapters.instructions.md` all change. The quoted-argument form has never been sent over our
`exec_command` (the SDK does it through its own SSH helper): one live probe before trusting it
(LESSONS 28).

**B. DSCC protection-policy API (`protectionPolicyType: schedule`).**
*For:* REST, no SSH write, and DSCC shows the schedule as a protection policy.
*Against:* the tool has no DSCC API client, and the API is `v1alpha1`. It needs the array onboarded
in DSCC and an API client entitled to Block Storage, so it cannot serve a provisioning-only run on an
array the tool did not onboard. The policy works on DSCC *application sets*; research 2026-10-07 §5
(3) found that a CLI-made Remote Copy group is converted one way into a DSCC volume set, so the two
planes do not mix freely. Allowed periods are DSCC's (15/20/30 minutes,
1 to 12 hours, a day, a month), which SPEC-023 adopts anyway. A new control plane for one feature.

**C. Command set only: the tool writes the `createsched` lines, the operator pastes them, the tool
verifies with `showsched`.**
*For:* no new write path; hard rule 2 untouched. The plan, the lines and the verify are the same code
as A, minus the apply of the schedule rows. Fast to build and prove.
*Against:* the owner already rejected this shape for arrays (ADR 0015). The operator types into an
array CLI what the tool could have run with the same checks; a mistyped paste is not checked before
it runs.

**D. Snapshots only (WSAPI); no schedules.**
*For:* nothing new to decide. *Against:* BL-21 asks for schedules; this ships half of it.

## Recommendation

**Option A**, with the form above and these guards:

1. A separate class, not a wider `ArrayRcCliClient`: each write client's list stays readable on one
   screen, and a reviewer can see what each feature may do.
2. The form is pinned to the array's own `help createsched` and `help createsv` (captured by
   `lab/snap_capture.py`) and to the three captured schedule lines, before the client is used.
3. The apply reads `showsched` back after every `createsched` and fails the row if the schedule is not
   there, active, with the planned command and cron.
4. The removal set (pasted, never run): `removesched -f <name>` first, then the snapshots.
5. Read side: `showsched` joins the read allowlist (`ALLOWED_COMMANDS`). It is a `show*` command
   and changes nothing; it is listed here because every allowlist change is said plainly.

If the owner prefers **C**, SPEC-023 holds as written except R5 step 2 (the schedule rows are shown
as lines to paste, and verify reads them). If **B**, SPEC-023 R5 step 2 and R1's period rules stand,
and a DSCC API client becomes its own work item.

## Consequences (if A is accepted)

- AGENTS.md hard rule 2 gains one sentence: the second write path is `ArraySnapCliClient`,
  `createsched` of a `createsv` on the run's own sources only, built only inside an approved snapshot
  plan. ADR 0001's consequence line and `adapters.instructions.md` say the same.
- Schedules outlive the run. The plan, the result, the verify and the as-built say so in words: *the
  array will take a snapshot of <source> every <period> until someone removes the schedule*
  (LESSONS 31: name the write as loudly as what is withheld).
- Snapshots use space in the volume's own CPG (OS 10.5 has no separate snapshot CPG:
  `tests/fixtures/rack13_array/showvv_listcols.txt`, `SnpCPG` refused). Expiry is mandatory, so a
  schedule cannot fill a CPG without bound; the plan states the CPG's free space as a note.
- Not decided here: remote (peer-side) schedules, snapshot windows (from/until hour), months as a
  period, and changing or suspending a schedule. Each would be a new form and a new decision.
