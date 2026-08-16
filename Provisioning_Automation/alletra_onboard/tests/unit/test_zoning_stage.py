"""The zoning WRITE path (ADR 0004, 2026-08-15 write-path mandate).

Two layers under test:

1. The adapter's write guard — strict per-verb regexes are the ONLY way onto the wire, so deletes
   and `cfgenable` are structurally unreachable, and operator-typed names are validated against FOS
   naming rules before anything is sent.
2. `stage_zones` — the per-fabric sequence built on the live-measured FOS 9.2.2 behaviors: refuse a
   foreign transaction, re-check staleness, additive commands, cfgsave answered 'y', verify by
   re-reading cfgshow. A failure anywhere aborts the tool's OWN transaction and commits nothing.
"""

from __future__ import annotations

import pytest

from alletra_onboard.adapters.fabric.brocade_client import BrocadeClient, BrocadeError, BrocadeRefused
from alletra_onboard.application.provisioning import zoning_stage as zs
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.zoning import AliasedWwpn, FabricZonePlan, ZoningPlan

# ---------------------------------------------------------------- adapter write guard

_GOOD_ALICREATE = 'alicreate "H1_Port1","10:00:00:00:00:00:00:aa"'


def _adapter(status=0, out=""):
    c = BrocadeClient("sw", "u", "p")
    c._exec_status = lambda cmd, stdin_data=None: (status, out)  # no network in unit tests
    return c


def test_write_accepts_only_the_three_additive_shapes():
    c = _adapter()
    c.write(_GOOD_ALICREATE)
    c.write('zonecreate "H1_A1","H1;A1"')
    c.write('cfgadd "F1_CFG","H1_A1;H2_A2"')


@pytest.mark.parametrize("cmd", [
    'zonedelete "some_zone"',                    # deletes do not exist on this surface
    'alidelete "some_alias"',
    'cfgremove "F1_CFG","z"',
    'cfgclear',
    'cfgenable "F1_CFG"',                        # activation is a HUMAN action, always
    'cfgsave',                                   # only reachable via cfgsave_defined (answered prompt)
    'alicreate "1starts_with_digit","10:00:00:00:00:00:00:aa"',   # FOS names start with a letter
    'alicreate "bad name","10:00:00:00:00:00:00:aa"',             # no spaces in names
    'alicreate "H1","10:00:00:00:00:00:aa"',                      # short WWPN
    'zonecreate "z","a;b;c"',                    # SIST: exactly two members
    _GOOD_ALICREATE + " && reboot",              # trailing junk breaks the shape
])
def test_write_refuses_everything_else(cmd):
    with pytest.raises(BrocadeRefused):
        _adapter().write(cmd)


def test_write_raises_with_fos_own_words_on_any_output():
    # These commands are silent on success (measured live: exit 0, no output) — any text back is
    # the switch complaining, and the operator must see FOS's words, not a generic failure.
    with pytest.raises(BrocadeError, match="already contains"):
        _adapter(out='"H1_Port1" already contains an entry').write(_GOOD_ALICREATE)
    with pytest.raises(BrocadeError, match="exit 1"):
        _adapter(status=1).write(_GOOD_ALICREATE)


def test_cfgsave_defined_detects_the_cancel_path():
    # Measured live on FOS 9.2.2: a canceled save prints "Operation canceled..." and exits 248.
    with pytest.raises(BrocadeError, match="did not commit"):
        _adapter(status=248, out="Operation canceled...").cfgsave_defined()
    _adapter(status=0, out="Updating flash ...").cfgsave_defined()  # the success shape


# ---------------------------------------------------------------- stage_zones orchestration

_HOST = "10000000000000AA"
_ARR = "20310002AC02F629"
_ZONE = "H1_A031"  # alias_for(host)_alias_for(array)


def _plan(active_cfg="F1_CFG"):
    return ZoningPlan(fabrics=[FabricZonePlan(
        fabric="F1", switch_host="sw-f1", active_cfg=active_cfg,
        hosts=[AliasedWwpn(wwpn=_HOST, display="10:00:00:00:00:00:00:aa", role="host", fabric="F1",
                           host_name="esx1")],
        array_ports=[AliasedWwpn(wwpn=_ARR, display="20:31:00:02:ac:02:f6:29", role="array",
                                 fabric="F1", nsp="0:3:1")],
        pairs=[(_HOST, _ARR)],
    )])


_ALIASES = {_HOST: "H1", _ARR: "A031"}
_SELECTED = [(_HOST, _ARR)]


def _intent():
    return ProvisioningIntent.from_simple(
        host_set_name="hs", array=EndpointCreds(host="a", username="u", password="p"),
        vcenter=EndpointCreds(host="v", username="u", password="p"),
        switch_f1=EndpointCreds(host="sw-f1", username="u", password="p"),
        switch_f2=EndpointCreds(host="sw-f2", username="u", password="p"),
        name_prefix="t", size_gib=1,
    )


class FakeSwitch:
    """A FOS switch with a transaction buffer, modelled on the live 9.2.2 measurements."""

    def __init__(self, *, open_transaction=False, cfg="F1_CFG", predefined=(),
                 refuse_verb=None, cancel_save=False, lose_after_save=False):
        self.open_transaction = open_transaction
        self.cfg = cfg
        self.defined = list(predefined)   # committed zone names in the defined config
        self.pending = []                 # zone names in the (uncommitted) transaction buffer
        self.writes = []
        self.refuse_verb = refuse_verb
        self.cancel_save = cancel_save
        self.lose_after_save = lose_after_save
        self.saved = False
        self.aborted = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def cfgtransshow(self):
        if self.open_transaction:
            return "Current transaction token is 0x4945\nIt is abortable\nFabric-Lock State: Active"
        return "There is no outstanding zoning transaction"

    def cfgshow(self):
        zones = "".join(f" zone:\t{z}\tH1;A031\n" for z in self.defined)
        return f"Defined configuration:\n cfg:\t{self.cfg}\t{_ZONE}\n{zones}" \
               f"Effective configuration:\n cfg:\t{self.cfg}\n"

    def write(self, cmd):
        verb = cmd.split()[0]
        if verb == self.refuse_verb:
            raise BrocadeError(f"the switch refused '{cmd}': error")
        self.writes.append(cmd)
        if verb == "zonecreate":
            self.pending.append(cmd.split('"')[1])

    def cfgsave_defined(self):
        if self.cancel_save:
            raise BrocadeError("cfgsave did not commit (exit 248): Operation canceled...")
        self.saved = True
        if not self.lose_after_save:
            self.defined.extend(self.pending)
        self.pending = []

    def cfgtransabort(self):
        self.aborted = True
        self.pending = []


def _stage(switch, plan=None):
    return zs.stage_zones(_intent(), plan or _plan(), _ALIASES, _SELECTED,
                          brocade_factory=lambda creds: switch)


def test_stage_happy_path_commits_verifies_and_hands_off():
    sw = FakeSwitch()
    result = _stage(sw)
    fr = result.fabrics[0]
    assert fr.error is None and fr.verified
    assert fr.staged == [
        'alicreate "H1","10:00:00:00:00:00:00:aa"',
        'alicreate "A031","20:31:00:02:ac:02:f6:29"',
        f'zonecreate "{_ZONE}","H1;A031"',
        f'cfgadd "F1_CFG","{_ZONE}"',
    ]
    assert not any(c.startswith("cfgenable") for c in fr.staged)   # never executed, only handed off
    assert fr.handoff == "cfgenable F1_CFG"
    assert sw.saved and not sw.aborted
    assert "divergence" in result.warning.lower() or "differ" in result.warning.lower()


def test_stage_refuses_a_foreign_transaction():
    sw = FakeSwitch(open_transaction=True)
    fr = _stage(sw).fabrics[0]
    assert fr.error and "another zoning transaction" in fr.error
    assert sw.writes == [] and not sw.aborted        # never touched, never aborted someone else's


def test_stage_refuses_when_the_effective_cfg_changed_since_planning():
    sw = FakeSwitch(cfg="SOMEONE_ELSES_CFG")
    fr = _stage(sw).fabrics[0]
    assert fr.error and "changed since the plan" in fr.error
    assert sw.writes == []


def test_stage_refuses_a_zone_name_collision_in_the_defined_config():
    sw = FakeSwitch(predefined=[_ZONE])
    fr = _stage(sw).fabrics[0]
    assert fr.error and "already exist" in fr.error
    assert sw.writes == []


def test_stage_aborts_its_own_transaction_on_a_mid_sequence_refusal():
    sw = FakeSwitch(refuse_verb="cfgadd")
    fr = _stage(sw).fabrics[0]
    assert fr.error and "aborted" in fr.error and "nothing was committed" in fr.error
    assert sw.aborted and not sw.saved
    assert fr.staged == []                           # nothing reported as staged


def test_stage_aborts_when_cfgsave_cancels():
    sw = FakeSwitch(cancel_save=True)
    fr = _stage(sw).fabrics[0]
    assert fr.error and "did not commit" in fr.error
    assert sw.aborted and not sw.saved


def test_stage_distrusts_cfgsave_and_verifies_by_reading_back():
    # cfgsave claims success but the defined config does not contain the zone: the one failure mode
    # that reports success while having done nothing — verification must catch it.
    sw = FakeSwitch(lose_after_save=True)
    result = _stage(sw)
    fr = result.fabrics[0]
    assert not fr.verified
    assert fr.error and "missing zone" in fr.error
    assert result.warning == ""                      # no verified staging -> no divergence claim


def test_stage_skips_a_fabric_with_nothing_renderable():
    # Nothing selected -> no zonecreate -> the switch is never contacted at all.
    def explode(creds):
        raise AssertionError("must not connect when there is nothing to stage")
    result = zs.stage_zones(_intent(), _plan(), _ALIASES, [], brocade_factory=explode)
    fr = result.fabrics[0]
    assert fr.error is None and fr.staged == [] and result.warning == ""
