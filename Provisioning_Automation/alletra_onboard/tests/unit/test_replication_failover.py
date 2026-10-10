"""SPEC-017 — the failover test sequence. A fake pair of arrays moves its roles the way the real ones
do after each WSAPI disaster-recovery action (the role names are the array's: Primary, Secondary,
Primary-Rev, Secondary-Rev; the status words Started/Stopped/Failsafe); the test checks the R2 table
is followed, R3 is measured, R5 stops with the observed state and the documented way back, and that
nothing is written before the normal starting state is confirmed."""

from __future__ import annotations

from pydantic import SecretStr

from alletra_onboard.application.replication.failover import (
    DR_ACTION_FAILOVER,
    DR_ACTION_RECOVER,
    DR_ACTION_RESTORE,
    read_group,
    recovery_action,
    run_failover_test,
    side_of,
)
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    FailoverSide,
    ProtectionRequest,
    RcGroup,
    RcGroupVolume,
    ReplicationArrayView,
    ReplicationIntent,
)
from alletra_onboard.domain.shared import EndpointCreds

P, S = "10.64.122.99", "10.64.154.190"
G, PG = "zz_rc_test_rcg", "zz_rc_test_rcg.r188150"


def _creds(host):
    return EndpointCreds(host=host, username="3paradm", password=SecretStr("pw"))


def _intent() -> ProvisioningIntent:
    return ProvisioningIntent(
        array=_creds(P), vcenter=_creds("vc"), switch_f1=_creds(""), switch_f2=_creds(""),
        replication=ReplicationIntent(peer=_creds(S), rtt_ms=1.0, protections=[ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6")]),
    )


class FakePair:
    """Both arrays' view of ONE group. `apply(where, verb)` moves the state the way the arrays do; the
    reads return RcGroups built from it. `sync_after` polls: how many reads of step 5 until Synced."""

    def __init__(self, *, mode="Sync", sync_after=1, last_sync="2026-10-10 15:42:48 IST", refuse=(), stuck=()):
        self.p = {"role": "Primary", "status": "Started", "synced": True}
        self.s = {"role": "Secondary", "status": "Started", "synced": True}
        self.mode, self.last_sync, self.refuse, self.stuck = mode, last_sync, set(refuse), set(stuck)
        self.sync_after, self.calls, self.reads = sync_after, [], 0

    # -- what the WSAPI writes do to the roles
    def stop(self, where, name):
        self.calls.append((where, "stop", name))
        if "stop" in self.refuse:
            raise RuntimeError("HTTP 403 RCOPY_GROUP_IS_BUSY")
        if "stop" not in self.stuck:
            self.p["status"] = self.s["status"] = "Stopped"

    def dr(self, where, name, action):
        verb = {DR_ACTION_FAILOVER: "failover", DR_ACTION_RECOVER: "recover", DR_ACTION_RESTORE: "restore"}[action]
        self.calls.append((where, verb, name))
        if verb in self.refuse:
            raise RuntimeError(f"HTTP 403 INV_OPERATION_RCOPY_GROUP_ROLE_CONFLICT ({verb})")
        if verb in self.stuck:
            return
        if verb == "failover":
            self.s["role"] = "Primary-Rev"
        elif verb == "recover":
            self.p["role"], self.p["status"], self.s["status"] = "Secondary-Rev", "Started", "Started"
            self.p["synced"] = self.s["synced"] = False
            self.sync_reads_left = self.sync_after
        elif verb == "restore":
            self.p.update(role="Primary", status="Started", synced=True)
            self.s.update(role="Secondary", status="Started", synced=True)

    # -- what `showrcopy groups <g>` shows
    def group(self, host, name) -> RcGroup | None:
        self.reads += 1
        side = self.p if host == P else self.s
        if side["role"] == "Secondary-Rev" or self.s["role"] == "Primary-Rev":
            if not side["synced"] and getattr(self, "sync_reads_left", 0) <= 0:
                self.p["synced"] = self.s["synced"] = True
            elif not side["synced"]:
                self.sync_reads_left -= 1
        status = "Synced" if side["synced"] else "Syncing"
        return RcGroup(name=name, target="AlletraMP_E18U31", status=side["status"], role=side["role"], mode=self.mode,
                       period="5m" if self.mode == "Periodic" else "",
                       volumes=[RcGroupVolume(local_name="zz_rc_test_v01", remote_name="zz_rc_test_v01", sync_status=status,
                                              last_sync=self.last_sync if self.mode == "Periodic" else "NA")])

    def view(self, host) -> ReplicationArrayView:
        name = "AlletraMP_D22U27" if host == P else "AlletraMP_E18U31"
        gname = G if host == P else PG
        g = self.group(host, gname)
        return ReplicationArrayView(host=host, name=name, system_id=188150 if host == P else 188146, rc_status="Started",
                                    groups=[g] if g else [])


class _Wsapi:
    def __init__(self, pair: FakePair, host: str):
        self.pair, self.host = pair, host

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def stop_remote_copy_group(self, name):
        self.pair.stop(self.host, name)
        return "stopped"

    def remote_copy_dr_action(self, name, action):
        self.pair.dr(self.host, name, action)


def _run(pair: FakePair, **kw):
    clock = {"t": 0.0}

    def tick():
        clock["t"] += 1.0
        return clock["t"]

    return run_failover_test(
        _intent(), G,
        wsapi_factory=lambda creds: _Wsapi(pair, creds.host),
        read_fn=lambda creds, progress=None: pair.view(creds.host),
        read_group_fn=lambda creds, name: pair.group(creds.host, name),
        sleep=lambda s: None, clock=tick,
        limits={"stop": 5, "failover": 5, "recover": 5, "sync": 30, "restore": 5, "poll": 1},
        **kw,
    )


# ------------------------------------------------------------------ R2 + R3: the sequence, sync and async

def test_the_sync_sequence_passes_and_ends_in_the_starting_state():
    pair = FakePair()
    rec = _run(pair)
    assert rec.result == "passed" and rec.error is None and rec.failed_step is None
    assert (rec.group, rec.peer_group, rec.mode, rec.primary_array, rec.peer_array) == (G, PG, "sync", "AlletraMP_D22U27", "AlletraMP_E18U31")
    # the writes, in order, each on the array the spec names (P for the stop, S for the role changes)
    assert pair.calls == [(P, "stop", G), (S, "failover", PG), (S, "recover", PG), (S, "restore", PG)]
    assert [(s.seq, s.outcome, s.where) for s in rec.steps] == [
        (0, "ok", "-"), (1, "ok", "P"), (2, "ok", "S"), (3, "ok", "-"), (4, "ok", "S"), (5, "ok", "-"), (6, "ok", "S"),
    ]
    assert [s.cli for s in rec.steps if s.cli] == [
        f"stoprcopygroup -f {G}", f"setrcopygroup failover -f {PG}", f"setrcopygroup recover -f {PG}", f"setrcopygroup restore -f {PG}",
    ]
    # states read after each step
    after = {s.seq: (s.primary.role, s.primary.status, s.peer.role, s.peer.status) for s in rec.steps}
    assert after[1] == ("Primary", "Stopped", "Secondary", "Stopped")
    assert after[2] == ("Primary", "Stopped", "Primary-Rev", "Stopped")
    assert after[4] == ("Secondary-Rev", "Started", "Primary-Rev", "Started")
    assert after[6] == ("Primary", "Started", "Secondary", "Started") and rec.steps[6].primary.synced == 1
    # R3: measured
    assert rec.time_to_failover_s is not None and rec.time_to_synced_s is not None
    assert all(s.seconds is not None and s.started_at and s.ended_at for s in rec.steps)
    assert rec.data_loss_bound == ""                     # sync: no bound to state
    assert "writable" in rec.steps[3].detail and "Not written to" in rec.steps[3].detail


def test_the_async_sequence_records_the_data_loss_bound_and_waits_for_the_sync_back():
    pair = FakePair(mode="Periodic", sync_after=3)
    rec = _run(pair)
    assert rec.result == "passed" and rec.mode == "async"
    assert rec.data_loss_bound.startswith("last sync before failover 2026-10-10 15:42:48 IST; failover completed at ")
    assert rec.steps[0].primary.last_sync == "2026-10-10 15:42:48 IST"
    assert rec.time_to_synced_s >= 1                       # the fake was Syncing at first; the wait polled


# ------------------------------------------------------------------ step 0: never write from a wrong start

def test_nothing_is_written_unless_the_group_starts_primary_started_and_synced():
    pair = FakePair()
    pair.p["status"] = "Stopped"
    rec = _run(pair)
    assert rec.result == "aborted" and rec.failed_step == 0 and pair.calls == []
    assert "starts only from the normal state" in rec.error and "Nothing was done" in rec.error
    assert rec.recovery_action == f"On AlletraMP_D22U27: startrcopygroup {G}"
    assert [s.outcome for s in rec.steps] == ["failed"]    # the sequence was not even planned

    pair = FakePair()
    pair.p["synced"] = False
    rec = _run(pair)
    assert rec.result == "aborted" and "0 of 1 volume(s) Synced" in rec.error and pair.calls == []

    pair = FakePair()
    pair.group = lambda host, name: None if host == P else FakePair.group(pair, host, name)   # not on P
    rec = _run(pair)
    assert rec.result == "aborted" and f"Group '{G}' is not on AlletraMP_D22U27" in rec.error and pair.calls == []


def test_an_unreadable_array_aborts_before_any_write():
    pair = FakePair()
    bad = ReplicationArrayView(host=S, read_error="Could not read 10.64.154.190: Login failed")
    rec = run_failover_test(_intent(), G, wsapi_factory=lambda c: _Wsapi(pair, c.host),
                            read_fn=lambda c, progress=None: bad if c.host == S else pair.view(c.host),
                            read_group_fn=lambda c, n: pair.group(c.host, n), sleep=lambda s: None)
    assert rec.result == "aborted" and rec.failed_step == 0 and rec.error.startswith("Could not read 10.64.154.190") and pair.calls == []


# ------------------------------------------------------------------ R5: stop and say the way back

def test_a_refused_failover_stops_at_step_2_with_the_start_line_as_the_way_back():
    pair = FakePair(refuse=("failover",))
    rec = _run(pair)
    assert rec.result == "failed" and rec.failed_step == 2
    assert "refused the failover" in rec.error and "ROLE_CONFLICT" in rec.error
    assert rec.observed_state == "AlletraMP_D22U27: Primary/Stopped · 1/1 Synced · AlletraMP_E18U31: Secondary/Stopped · 1/1 Synced"
    assert rec.recovery_action == f"On AlletraMP_D22U27: startrcopygroup {G}"
    assert [s.outcome for s in rec.steps] == ["ok", "ok", "failed", "skipped", "skipped", "skipped", "skipped"]
    assert pair.calls == [(P, "stop", G), (S, "failover", PG)]          # nothing after the failure


def test_a_refused_recover_leaves_primary_rev_and_names_recover_then_restore():
    pair = FakePair(refuse=("recover",))
    rec = _run(pair)
    assert rec.result == "failed" and rec.failed_step == 4
    assert rec.recovery_action == f"On AlletraMP_E18U31: setrcopygroup recover -f {PG} ; then setrcopygroup restore -f {PG}"
    assert rec.time_to_failover_s is not None and rec.time_to_synced_s is None


def test_a_sync_that_never_finishes_stops_at_step_5_and_names_restore():
    pair = FakePair(sync_after=10_000)
    rec = _run(pair)
    assert rec.result == "failed" and rec.failed_step == 5
    assert "Not every volume was Synced within 0 min" in rec.error
    assert rec.recovery_action == f"On AlletraMP_E18U31: setrcopygroup restore -f {PG}  (returns the group to its natural direction and starts it)"
    assert rec.steps[5].primary.role == "Secondary-Rev" and rec.steps[5].peer.role == "Primary-Rev"


def test_a_restore_that_does_not_come_back_stops_at_step_6():
    pair = FakePair(stuck=("restore",))
    rec = _run(pair)
    assert rec.result == "failed" and rec.failed_step == 6
    assert rec.observed_state.startswith("AlletraMP_D22U27: Secondary-Rev/Started")
    assert "setrcopygroup restore -f" in rec.recovery_action


def test_a_stop_that_never_takes_stops_at_step_1():
    pair = FakePair(stuck=("stop",))
    rec = _run(pair)
    assert rec.result == "failed" and rec.failed_step == 1 and "Not Stopped on both sides within 5 s" in rec.error
    assert rec.recovery_action == "The group is already in its natural direction and started; nothing to do."


# ------------------------------------------------------------------ the way-back table (ED6)

def _side(role, status, present=True, array="A", group="g"):
    return FailoverSide(array=array, group=group, present=present, role=role, status=status, volumes=1, synced=1)


def test_recovery_actions_follow_the_observed_roles_not_the_step():
    assert recovery_action(_side("Primary", "Stopped"), _side("Primary-Rev", "Stopped", array="B", group="g.r1")) == \
        "On B: setrcopygroup recover -f g.r1 ; then setrcopygroup restore -f g.r1"
    assert recovery_action(_side("Secondary-Rev", "Started"), _side("Primary-Rev", "Started", array="B", group="g.r1")).startswith(
        "On B: setrcopygroup restore -f g.r1")
    assert recovery_action(_side("Primary", "Stopped"), _side("Secondary", "Stopped", array="B")) == "On A: startrcopygroup g"
    assert recovery_action(_side("Primary", "Started"), _side("Secondary", "Started", array="B")) == \
        "The group is already in its natural direction and started; nothing to do."
    assert "reverse -natural" in recovery_action(_side("Primary-Rev", "Stopped"), _side("Secondary", "Stopped", array="B"))
    assert "Failsafe" in recovery_action(_side("Primary", "Failsafe"), _side("Primary-Rev", "Stopped", array="B", group="g.r1"))
    assert "missing on one side" in recovery_action(_side("Primary", "Started"), _side("", "", present=False))
    assert "contact HPE Support" in recovery_action(_side("Secondary", "Started"), _side("Secondary", "Started", array="B"))


# ------------------------------------------------------------------ the reads

def test_read_group_uses_showrcopy_groups_and_returns_none_when_absent():
    class Cli:
        def __init__(self):
            self.ran = []

        def __enter__(self):
            return self

        def __exit__(self, *e):
            return None

        def run(self, cmd, timeout=None):
            self.ran.append(cmd)
            if "ghost" in cmd:
                return "Remote Copy System Information\nStatus: Started, Normal\n\nGroup Information\n\nError: group matching ghost does not exist on the system\n"
            return ("Remote Copy System Information\nStatus: Started, Normal\n\nGroup Information\n\n"
                    "Name         Target           Status   Role       Mode     Options\n"
                    f"{G} AlletraMP_E18U31 Started  Primary    Sync     auto_recover\n"
                    "  LocalVV      ID   RemoteVV     ID   SyncStatus    LastSyncTime\n"
                    "  zz_rc_test_v01 1 zz_rc_test_v01 2 Synced NA\n")

    cli = Cli()
    g = read_group(_creds(P), G, array_cli_factory=lambda c: cli)
    assert cli.ran == [f"showrcopy groups {G}"] and g is not None and g.role == "Primary"
    assert read_group(_creds(P), "ghost", array_cli_factory=lambda c: cli) is None
    side = side_of("AlletraMP_D22U27", G, g)
    assert (side.role, side.status, side.mode, side.volumes, side.synced, side.last_sync) == ("Primary", "Started", "sync", 1, 1, "")
    assert side.summary == "Primary/Started · 1/1 Synced"
    assert side_of("X", G, None).summary == "not on the array"
