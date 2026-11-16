"""SPEC-019 — the command log and the read-only console prompt (section 4 Verification)."""

from __future__ import annotations

import asyncio

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.array import cli_client
from alletra_onboard.adapters.array.cli_client import ArrayCliClient, ArrayCliError
from alletra_onboard.adapters.array.wsapi_client import _record_calls
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.application.runs.console import REFUSED, console_text
from alletra_onboard.application.runs.coordinator import StepPreconditionError
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig, RunRecord
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import ProtectionRequest, ReplicationIntent
from alletra_onboard.domain.shared import EndpointCreds

PW = "s3cret-pw"


class _Stream:
    def __init__(self, text: str) -> None:
        self.text = text

    def read(self) -> bytes:
        return self.text.encode()


class _Paramiko:
    def __init__(self, out: str = "", err: str = "") -> None:
        self.out, self.err, self.sent = out, err, []

    def exec_command(self, command, timeout=None):
        self.sent.append(command)
        return None, _Stream(self.out), _Stream(self.err)


def _cli(out="", err="") -> ArrayCliClient:
    cli = ArrayCliClient("10.0.0.1", "3paradm", PW)
    cli._client = _Paramiko(out, err)
    return cli


@pytest.fixture
def recorded():
    got: list[dict] = []
    token = command_log.bind(got.append)
    yield got
    command_log.unbind(token)


# ------------------------------------------------------------------ R1: one record per command

def test_nothing_is_recorded_when_no_run_is_bound():
    assert not command_log.active()
    assert _cli("Id Name\n").run("showvv") == "Id Name\n"     # and the read still works


def test_the_ssh_client_records_command_output_and_duration(recorded):
    _cli("Id Name\n 1 vol01\n").run("showvv -showcols Name,VSize_MB")
    [e] = recorded
    assert (e["target"], e["transport"], e["command"], e["ok"], e["result"], e["write"]) == (
        "10.0.0.1", "ssh", "showvv -showcols Name,VSize_MB", True, "ok", False)
    assert e["output"] == "Id Name\n 1 vol01\n" and e["duration_s"] >= 0 and e["at"]


def test_the_array_error_text_marks_the_record_failed(recorded):
    _cli(err="Error: vv zz does not exist\n").run("showvv zz")
    assert (recorded[0]["ok"], recorded[0]["result"]) == (False, "Error: vv zz does not exist")


def test_a_refused_command_is_recorded_and_never_sent(recorded):
    cli = _cli("x")
    with pytest.raises(ArrayCliError, match="not a read-only show command"):
        cli.run("removevv -f zz")
    assert cli._client.sent == [] and recorded[0]["ok"] is False and "refused" in recorded[0]["result"]


def test_the_password_and_overlong_output_never_leave_the_client(recorded):
    _cli(f"login {PW} ok\n" + "y" * (command_log.MAX_OUTPUT_BYTES + 5000)).run("showsys")
    out = recorded[0]["output"]
    assert PW not in out and command_log.REDACTED in out
    assert out.endswith("(4 KB truncated)") and len(out.encode()) < command_log.MAX_OUTPUT_BYTES + 100


class _Http:
    def __init__(self, fail: Exception | None = None) -> None:
        self.fail = fail

    def _time_request(self, url, method, **kwargs):
        if self.fail:
            raise self.fail
        body = {"key": "SESSION-KEY"} if url.endswith("/credentials") else {"members": [{"name": "v"}]}
        return type("Resp", (), {"status_code": 201 if method == "POST" else 200})(), body


class _Sdk:
    def __init__(self, fail=None) -> None:
        self.http = _Http(fail)


def test_wsapi_calls_are_recorded_with_the_login_and_session_key_withheld(recorded):
    sdk = _Sdk()
    _record_calls(sdk, "10.0.0.1", "https://10.0.0.1:443/api/v1", PW)
    sdk.http._time_request("https://10.0.0.1:443/api/v1/credentials", "POST", body={"user": "3paradm", "password": PW})
    sdk.http._time_request("https://10.0.0.1:443/api/v1/volumes", "GET")
    sdk.http._time_request("https://10.0.0.1:443/api/v1/volumes", "POST", body={"name": "zz", "sizeMiB": 1024})
    sdk.http._time_request("https://10.0.0.1:443/api/v1/credentials/SESSION-KEY", "DELETE")
    login, read, write, logout = recorded
    assert login["command"] == "POST /credentials {user, password: ********}"
    assert login["output"] == "(session key withheld)" and PW not in str(recorded) and "SESSION-KEY" not in str(recorded)
    assert (read["command"], read["result"], read["write"]) == ("GET /volumes", "HTTP 200", False)
    assert '"name": "v"' in read["output"]
    assert write["command"].startswith("POST /volumes {") and write["write"] is True and write["result"] == "HTTP 201"
    # opening and closing the session change nothing on the array, so the as-built does not list them
    assert logout["command"] == "DELETE /credentials/********"
    assert login["write"] is False and logout["write"] is False


def test_a_refused_wsapi_call_is_recorded_with_its_status_and_still_raises(recorded):
    exc = RuntimeError("Conflict (HTTP 409) 73 - volume exists")
    exc.http_status = 409
    sdk = _Sdk(fail=exc)
    _record_calls(sdk, "10.0.0.1", "https://10.0.0.1:443/api/v1", PW)
    with pytest.raises(RuntimeError):
        sdk.http._time_request("https://10.0.0.1:443/api/v1/volumes", "POST", body={"name": "zz"})
    assert recorded[0]["ok"] is False and recorded[0]["result"].startswith("HTTP 409: Conflict")


# ------------------------------------------------------------------ R2: durable, in order

def test_the_store_keeps_commands_in_order_and_returns_them_since_a_seq(tmp_path):
    store = SqliteRunStore(tmp_path / "s.db")
    store.initialize()
    for rid in ("r1", "r2"):
        store.upsert_run(RunRecord(run_id=rid, serial_number="S"))
    for n in range(3):
        assert store.append_command("r1", {"command": f"show{n}"}) == n + 1
    store.append_command("r2", {"command": "other"})
    assert [e["command"] for e in store.list_commands("r1")] == ["show0", "show1", "show2"]
    assert [e["seq"] for e in store.list_commands("r1", since=1)] == [2, 3]
    assert [e["command"] for e in store.list_commands("r2")] == ["other"]


# ------------------------------------------------------------------ a run's step and the prompt

def _item() -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number="CZ2D320BT1", part_number="S0B84A", subscription_key=SecretStr("k"),
        service_catalog_region_id="ap-northeast", dscc_region_code="jp1",
        cloudinit_url="https://169.254.1.1/cloudinit",
        network=NetworkConfig(mgmt_ipv4="10.0.0.1", mask="255.255.255.0", gateway="10.0.0.254", dns=["10.0.0.2"],
                              ntp="ntp", timezone="UTC"),
        dscc_setup=DsccSetupConfig(system_name="a01", country="India"),
    )


def _intent(peer: bool) -> ProvisioningIntent:
    def creds(host):
        return EndpointCreds(host=host, username="3paradm", password=SecretStr(PW))

    intent = ProvisioningIntent.from_simple(host_set_name="HS", array=creds("10.0.0.1"), vcenter=creds("vc"),
                                            switch_f1=creds("sw1"), switch_f2=creds("sw2"),
                                            name_prefix="V", size_gib=1, count=1)
    if peer:
        intent.replication = ReplicationIntent(peer=creds("10.0.0.9"), protections=[ProtectionRequest(vvset="HS", peer_cpg="SSD_r6")])
    return intent


def _service(tmp_path, *, peer=False):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_item(), provisioning_intent=_intent(peer))
    return service, run.run_id


async def test_a_spawned_step_records_reads_made_in_its_worker_threads(tmp_path):
    service, run_id = _service(tmp_path)
    live = service.coordinator.console.subscribe(run_id)

    async def step():
        await asyncio.to_thread(lambda: _cli("ok\n").run("showsys"))

    service.coordinator.spawn(run_id, step())
    await service.wait(run_id)
    await asyncio.sleep(0)                      # the worker thread hands the record to the loop
    [e] = service.coordinator.list_commands(run_id)
    assert (e["seq"], e["command"], e["output"]) == (1, "showsys", "ok\n")
    assert live.get_nowait()["command"] == "showsys"
    assert not command_log.active()             # the binding stayed inside the step's task


@pytest.mark.parametrize("command", ["removevv -f zz", "setrcopygroup failover -f g", "createvv SSD zz 1g",
                                     "showvv; removevv zz", "showvv | more", "showvv `x`"])
async def test_the_prompt_refuses_anything_but_the_read_allowlist(tmp_path, command):
    service, run_id = _service(tmp_path)
    opened = []
    service.console.cli_factory = lambda creds: opened.append(creds) or pytest.fail("no connection for a refusal")
    out = await service.console.run(run_id, command)
    assert out == {"ok": False, "refused": True, "output": REFUSED, "target": "10.0.0.1"}
    assert opened == []
    await asyncio.sleep(0)
    [e] = service.coordinator.list_commands(run_id)
    assert e["ok"] is False and e["result"].endswith("(console)")


class _FakeCli:
    def __init__(self, creds, text="Name VSize_MB\nzz 1024\n") -> None:
        self.creds, self.text, self.ran = creds, text, []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def run(self, command):
        self.ran.append(command)
        command_log.record(target=self.creds.host, transport="ssh", command=command, started=0.0, ok=True,
                           result="ok", output=self.text)
        return self.text


async def test_the_prompt_runs_a_read_with_the_runs_own_credential(tmp_path):
    service, run_id = _service(tmp_path)
    used = []
    service.console.cli_factory = lambda creds: used.append(creds) or _FakeCli(creds)
    out = await service.console.run(run_id, "  showvv   -showcols Name,VSize_MB ")
    assert out == {"ok": True, "refused": False, "output": "Name VSize_MB\nzz 1024\n", "target": "10.0.0.1"}
    assert (used[0].host, used[0].username, used[0].password.get_secret_value()) == ("10.0.0.1", "3paradm", PW)
    await asyncio.sleep(0)
    assert [e["command"] for e in service.coordinator.list_commands(run_id)] == ["showvv -showcols Name,VSize_MB"]


async def test_the_peer_target_reads_the_replication_peer_and_needs_the_tab(tmp_path):
    service, run_id = _service(tmp_path / "a")
    with pytest.raises(StepPreconditionError, match="no Replication tab"):
        await service.console.run(run_id, "showrcopy groups", target="peer")
    assert service.console.targets(run_id) == {"array": "3paradm@10.0.0.1"}

    service, run_id = _service(tmp_path / "b", peer=True)
    service.console.cli_factory = lambda creds: _FakeCli(creds, "Name Role\n")
    out = await service.console.run(run_id, "showrcopy groups zz_rc_vvs_rcg.r188150", target="peer")
    assert out["target"] == "10.0.0.9" and out["ok"] is True
    assert service.console.targets(run_id) == {"array": "3paradm@10.0.0.1", "peer": "3paradm@10.0.0.9"}


def test_open_terminal_passes_no_password_and_refuses_an_unsafe_name(tmp_path):
    service, run_id = _service(tmp_path)
    launched = []
    service.console.launcher = launched.append
    assert service.console.open_terminal(run_id) == {"launched": True, "command": "ssh 3paradm@10.0.0.1", "error": None}
    assert launched == [["ssh", "3paradm@10.0.0.1"]]

    intent = _intent(False)
    intent.array = EndpointCreds(host="10.0.0.1", username="3paradm & calc", password=SecretStr(PW))
    service.store.save_provisioning_intent(run_id, intent)
    out = service.console.open_terminal(run_id)
    assert out["launched"] is False and len(launched) == 1


def test_the_text_log_has_one_header_line_per_command_and_indented_output():
    text = console_text([{"at": "2026-10-11T10:00:01+00:00", "target": "10.0.0.1", "transport": "ssh",
                          "command": "showsys", "duration_s": 0.4, "result": "ok", "output": "ID Name\n1 a01\n"}])
    assert text == "10:00:01  10.0.0.1 (ssh)  showsys  0.4s  ok\n    ID Name\n    1 a01\n"


def test_the_allowlist_check_is_the_clients_own():
    assert cli_client.refusal("showvv -showcols Name,VSize_MB") is None
    assert "metacharacter" in cli_client.refusal("showvv && removevv x")


# ------------------------------------------------------------------ R2: the as-built appendix

def test_the_as_built_lists_every_change_and_counts_the_reads(tmp_path):
    from alletra_onboard.application.documents.asbuilt import generate_asbuilt
    from tests.unit.test_asbuilt_replication import _data, _h1, _read, _tables

    commands = [
        {"at": "2026-10-11T08:00:00+00:00", "target": "10.64.122.99", "transport": "ssh", "command": "showvv", "result": "ok", "write": False},
        {"at": "2026-10-11T08:00:01+00:00", "target": "10.64.122.99", "transport": "ssh", "command": "showvv", "result": "ok", "write": False},
        {"at": "2026-10-11T08:00:02+00:00", "target": "10.64.122.99", "transport": "wsapi",
         "command": 'POST /volumes {"name": "zz_rc_vol01", "sizeMiB": 1024}', "result": "HTTP 201", "write": True},
    ]
    out, _ = generate_asbuilt(_data(commands=commands), tmp_path / "c.docx")
    doc, text = _read(out)
    assert _h1(doc)[-1] == "Commands run on the array"
    assert "1 change(s) and 2 read-only command(s)" in text
    tables = _tables(doc)
    assert tables[("Time", "Device", "Via", "Call", "Result")] == [
        ["2026-10-11 08:00 UTC", "10.64.122.99", "WSAPI", 'POST /volumes {"name": "zz_rc_vol01", "sizeMiB": 1024}', "HTTP 201"]]
    assert tables[("Device", "Via", "Command", "Times")] == [["10.64.122.99", "CLI (SSH)", "showvv", "2"]]

    out, _ = generate_asbuilt(_data(), tmp_path / "none.docx")
    assert "Commands run on the array" not in _h1(_read(out)[0])     # no log, no appendix
