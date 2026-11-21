"""SPEC-019 — the command log and the read-only console prompt (section 4 Verification)."""

from __future__ import annotations

import asyncio

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.array import cli_client
from alletra_onboard.adapters.array.cli_client import ArrayCliClient
from alletra_onboard.adapters.array.wsapi_client import _record_calls
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.application.runs.console import REFUSED, console_text
from alletra_onboard.application.runs.coordinator import StepPreconditionError
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import Settings
from alletra_onboard.domain.errors import ArrayCliError, GreenLakeHttpError
from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig, RunRecord
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import ProtectionRequest, ReplicationIntent
from alletra_onboard.domain.shared import EndpointCreds
from tests.unit import fake_tls

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
                                     "showvv; removevv zz", "showvv | more", "showvv `x`",
                                     "showtarget -rescan", "showtarget -lun all -RESCAN"])
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


def test_an_allowed_command_is_refused_with_an_option_that_acts():
    """The name check alone passed `showtarget -rescan`, which makes the peer ports rescan for targets."""
    assert cli_client.refusal("showtarget -rescan") == (
        "refused: 'showtarget -rescan' is not a read: it makes the peer ports rescan for targets")
    assert cli_client.refusal("showtarget -lun all -rescan") is not None
    assert cli_client.refusal("showtarget") is None
    assert cli_client.refusal("showtarget -lun all") is None


@pytest.mark.parametrize("ch", ['"', "'", "{", "}", "[", "]", "\\"])
def test_each_tcl_quoting_or_substitution_character_is_refused(ch):
    """The array CLI is Tcl-based: these characters could run a second command or hide an option."""
    assert cli_client.refusal(f"showvv zz{ch}") == "refused: command contains a forbidden shell metacharacter"


@pytest.mark.parametrize("command", [
    "showvv [removevv -f zz]",          # command substitution would run removevv
    'showtarget "-rescan"',             # quoting hides the acting option from the option check
    "showtarget '-rescan'",
    "showtarget {-rescan}",
    "showtarget \\-rescan",
])
def test_tcl_substitution_or_quoting_cannot_slip_an_action_past_the_check(command):
    assert "metacharacter" in cli_client.refusal(command)


@pytest.mark.parametrize("command", ["showtarget -rescan", "showvv [removevv -f zz]", 'showtarget "-rescan"'])
def test_an_acting_option_or_a_substitution_is_recorded_and_never_sent(recorded, command):
    cli = _cli("x")
    with pytest.raises(ArrayCliError, match="refused"):
        cli.run(command)
    assert cli._client.sent == [] and recorded[0]["ok"] is False and "refused" in recorded[0]["result"]


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


# ------------------------------------------------------------------ vCenter, hosts and GreenLake

SUB_KEY = "SUBKEY-7Q2X9"
GL_SECRET = "gl-client-secret-value"
JWT = "eyJhbGciOi.payload.signature"


def test_the_redaction_policy_runs_over_every_record(recorded):
    command_log.record(target="h", transport="ssh", command="x", started=0.0, ok=True,
                       result="Authorization: Bearer abc.def-ghi",
                       output=f"client_secret={GL_SECRET}\nsubscription_key: {SUB_KEY}")
    [e] = recorded
    assert "abc.def-ghi" not in e["result"] and GL_SECRET not in e["output"] and SUB_KEY not in e["output"]


def test_command_log_record_never_validates_or_raises_on_unusual_values(recorded):
    """A completed device call must never turn into an exception because of a logging field value."""
    record_fn = command_log.record
    record_fn(target=None, transport="ssh", command="showsys", started=0.0, ok=None, result="ok", write=None)
    record_fn(target="10.0.0.1", transport="ssh", command="showsys", started=0.0, ok=1, result="ok", write=False)
    assert len(recorded) == 2
    assert recorded[0]["ok"] is None and recorded[0]["target"] is None and recorded[0]["write"] is None
    assert recorded[1]["ok"] == 1 and type(recorded[1]["ok"]) is int


def _vcenter(monkeypatch, *, connect=None):
    from types import SimpleNamespace as NS

    from alletra_onboard.adapters.vcenter import vcenter_client
    from tests.unit.test_esxi_paths import NAA1, _path, _storage_device

    esxi = NS(name="esx1", config=NS(storageDevice=_storage_device(luns={NAA1: [_path("active", "vmhba1")]})))
    view = NS(view=[esxi], Destroy=lambda: None)
    content = NS(rootFolder=None, viewManager=NS(CreateContainerView=lambda *a: view))
    monkeypatch.setattr(vcenter_client, "vim", NS(HostSystem=object))
    monkeypatch.setattr(vcenter_client, "SmartConnect", connect or (lambda **kw: NS(RetrieveContent=lambda: content)))
    # BL-53 reads and compares vCenter's certificate before login; a made-up one stands in for it
    fake_tls.install(monkeypatch).devices[("vc.lab", 443)] = fake_tls.self_signed_der("vc.lab")
    return vcenter_client.VCenterClient("vc.lab", "administrator@vsphere.local", PW)


def test_vcenter_login_and_inventory_reads_are_recorded_without_the_password(monkeypatch, recorded):
    client = _vcenter(monkeypatch)
    client.connect()
    luns = client.host_luns()
    login, read = recorded
    assert (login["target"], login["transport"], login["command"], login["ok"], login["write"]) == (
        "vc.lab", "vcenter", "login {user, password: ********}", True, False)
    assert read["command"].startswith("read HostSystem") and read["result"] == f"ok, {len(luns)} found"
    assert '"host_name": "esx1"' in read["output"] and read["write"] is False
    assert PW not in str(recorded)


def test_a_refused_vcenter_login_is_recorded_and_still_raises(monkeypatch, recorded):
    from alletra_onboard.adapters.vcenter import vcenter_client

    class InvalidLogin(Exception):
        msg = f"Cannot complete login for {PW}."

    def refuse(**kwargs):
        raise InvalidLogin()

    with pytest.raises(vcenter_client.VCenterError):
        _vcenter(monkeypatch, connect=refuse).connect()
    [e] = recorded
    assert e["ok"] is False and e["result"].startswith("InvalidLogin: Cannot complete login") and PW not in str(e)


class _SshChannel:
    def __init__(self, status: int) -> None:
        self.status = status

    def recv_exit_status(self) -> int:
        return self.status


class _SshOut(_Stream):
    def __init__(self, text: str, status: int) -> None:
        super().__init__(text)
        self.channel = _SshChannel(status)


class _LinuxSsh:
    def __init__(self, answers: dict[str, tuple[int, str] | Exception]) -> None:
        self.answers = answers

    def exec_command(self, command, timeout=None):
        answer = self.answers[command]
        if isinstance(answer, Exception):
            raise answer
        return None, _SshOut(answer[1], answer[0]), _Stream("")


def test_linux_host_reads_are_recorded_with_exit_status_and_output(recorded):
    from alletra_onboard.adapters.hosts.linux_ssh import COMMANDS, LinuxHostClient

    client = LinuxHostClient("10.0.0.20", "root", PW)
    client._client = _LinuxSsh({COMMANDS["hostname"]: (0, "rhel92lab01\n"),
                                COMMANDS["multipath"]: (1, f"need to be root {PW}\n"),
                                COMMANDS["iqn"]: TimeoutError("timed out")})
    assert client.read("hostname") == "rhel92lab01\n"
    assert client.run("multipath") == (1, f"need to be root {PW}\n")      # the caller still gets the real text
    assert client.run("iqn") == (-1, "")
    ok, refused, failed = recorded
    assert (ok["target"], ok["transport"], ok["command"], ok["ok"], ok["result"], ok["output"], ok["write"]) == (
        "10.0.0.20", "host-ssh", "hostname", True, "exit 0", "rhel92lab01\n", False)
    assert (refused["command"], refused["ok"], refused["result"]) == ("multipath -ll", False, "exit 1")
    assert (failed["command"], failed["ok"], failed["result"]) == (COMMANDS["iqn"], False, "TimeoutError")
    assert PW not in str(recorded)


class _WinResponse:
    def __init__(self, status: int, out: str) -> None:
        self.status_code, self.std_out = status, out.encode()


def test_windows_host_reads_and_the_login_probe_are_recorded(monkeypatch, recorded):
    from alletra_onboard.adapters.hosts import windows_winrm

    class Session:
        def __init__(self, url, **kwargs):
            self.url = url

        def run_ps(self, script):
            if ":5985/" in self.url:
                raise ConnectionError("refused")
            return _WinResponse(0, "WIN-LAB01" if script == windows_winrm.SCRIPTS["hostname"] else f"x {PW}")

    monkeypatch.setattr(windows_winrm, "winrm", type("W", (), {"Session": Session}))
    client = windows_winrm.WindowsHostClient("10.0.0.21", "administrator", PW)
    client.connect()
    assert client.read("serial") == f"x {PW}"
    http_probe, https_probe, serial = recorded
    assert (http_probe["transport"], http_probe["command"], http_probe["ok"], http_probe["result"]) == (
        "winrm", "$env:COMPUTERNAME", False, "ConnectionError")
    assert (https_probe["ok"], https_probe["output"]) == (True, "WIN-LAB01")
    assert (serial["target"], serial["command"], serial["result"], serial["write"]) == (
        "10.0.0.21", windows_winrm.SCRIPTS["serial"], "exit 0", False)
    assert PW not in str(recorded)


class _Token:
    client_secret = GL_SECRET

    async def token(self) -> str:
        return JWT


async def test_greenlake_calls_are_recorded_as_method_and_path_only(monkeypatch, recorded):
    import httpx
    import respx

    from alletra_onboard.adapters.greenlake import http_client
    from alletra_onboard.adapters.greenlake.devices import DevicesClient
    from alletra_onboard.adapters.greenlake.subscriptions import SubscriptionsClient

    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr(http_client.asyncio, "sleep", _no_sleep)
    http = http_client.GreenLakeHttpClient("https://api.example", _Token())
    with respx.mock:
        respx.get("https://api.example/subscriptions/v1/subscriptions").mock(side_effect=[
            httpx.Response(429), httpx.Response(200, json={"items": [{"key": SUB_KEY}]})])
        respx.post("https://api.example/subscriptions/v1/subscriptions").mock(
            return_value=httpx.Response(202, headers={"Location": "https://api.example/subscriptions/v1/async-operations/op-9"}))
        respx.post("https://api.example/devices/v2beta1/devices").mock(return_value=httpx.Response(202))
        respx.patch(url__startswith="https://api.example/devices/v1/devices").mock(return_value=httpx.Response(400))
        await SubscriptionsClient(http).find_by_key(SUB_KEY)
        await SubscriptionsClient(http).add_subscription(SUB_KEY)
        await DevicesClient(http).add_storage_device("SGH123", "S0B84A", {}, dry_run=True)
        with pytest.raises(GreenLakeHttpError):
            await DevicesClient(http).assign_application("dev-1", "sm-1", "ap-northeast")
    retried, read, subscribe, dry_run, assign = recorded
    assert {e["target"] for e in recorded} == {"api.example"} and {e["transport"] for e in recorded} == {"greenlake"}
    assert (retried["command"], retried["ok"], retried["result"]) == (
        "GET /subscriptions/v1/subscriptions", False, "HTTP 429, retrying")
    assert (read["result"], read["write"]) == ("HTTP 200", False)
    assert (subscribe["command"], subscribe["write"], subscribe["output"]) == (
        "POST /subscriptions/v1/subscriptions", True, "Location: /subscriptions/v1/async-operations/op-9")
    assert (dry_run["command"], dry_run["write"]) == ("POST /devices/v2beta1/devices?dry-run=true", False)
    assert (assign["command"], assign["ok"], assign["result"], assign["write"]) == (
        "PATCH /devices/v1/devices", False, "HTTP 400", True)
    text = str(recorded)
    assert SUB_KEY not in text and JWT not in text and GL_SECRET not in text and "sm-1" not in text


async def test_the_greenlake_token_request_shows_neither_the_secret_nor_the_token(recorded):
    import httpx
    import respx

    from alletra_onboard.adapters.greenlake.auth import OAuthClientCredentials

    url = "https://sso.example/authorization/v2/oauth2/ws-1/token"
    provider = OAuthClientCredentials(url, "cid", GL_SECRET)
    with respx.mock:
        respx.post(url).mock(side_effect=[httpx.Response(200, json={"access_token": JWT, "expires_in": 900}),
                                          httpx.Response(401, text=f"bad secret {GL_SECRET}")])
        assert await provider.token() == JWT
        provider._expires_at = provider._expires_at.replace(year=2000)
        with pytest.raises(GreenLakeHttpError):
            await provider.token()
    ok, refused = recorded
    assert (ok["target"], ok["transport"], ok["command"], ok["output"], ok["write"]) == (
        "sso.example", "greenlake", "POST /authorization/v2/oauth2/ws-1/token (client credentials withheld)",
        "(token withheld)", False)
    assert (refused["ok"], refused["result"]) == (False, "HTTP 401")
    assert GL_SECRET not in str(recorded) and JWT not in str(recorded)


def test_the_as_built_names_vcenter_host_and_greenlake_calls(tmp_path):
    from alletra_onboard.application.documents.asbuilt import generate_asbuilt
    from tests.unit.test_asbuilt_replication import _data, _read, _tables

    commands = [
        {"at": "2026-11-17T08:00:00+00:00", "target": "global.api.greenlake.hpe.com", "transport": "greenlake",
         "command": "PATCH /devices/v1/devices", "result": "HTTP 202", "write": True},
        {"at": "2026-11-17T08:01:00+00:00", "target": "vc.lab", "transport": "vcenter",
         "command": "login {user, password: ********}", "result": "ok", "write": False},
        {"at": "2026-11-17T08:01:01+00:00", "target": "10.0.0.20", "transport": "host-ssh",
         "command": "multipath -ll", "result": "exit 0", "write": False},
        {"at": "2026-11-17T08:01:02+00:00", "target": "10.0.0.21", "transport": "winrm",
         "command": "$env:COMPUTERNAME", "result": "exit 0", "write": False},
    ]
    out, _ = generate_asbuilt(_data(commands=commands), tmp_path / "c.docx")
    doc, text = _read(out)
    assert "1 change(s) and 3 read-only command(s)" in text
    tables = _tables(doc)
    assert tables[("Time", "Device", "Via", "Call", "Result")] == [
        ["2026-11-17 08:00 UTC", "global.api.greenlake.hpe.com", "GreenLake API", "PATCH /devices/v1/devices", "HTTP 202"]]
    assert tables[("Device", "Via", "Command", "Times")] == [
        ["vc.lab", "vCenter", "login {user, password: ********}", "1"],
        ["10.0.0.20", "Linux host (SSH)", "multipath -ll", "1"],
        ["10.0.0.21", "Windows host (WinRM)", "$env:COMPUTERNAME", "1"]]


def test_command_log_record_tolerates_closed_loop_or_store_failure():
    """STANDARD E2: a broken sink (closed event loop or locked SQLite) never breaks the command."""
    import sqlite3

    for exc in (RuntimeError("Event loop is closed"), sqlite3.OperationalError("database is locked")):
        def _broken(_entry, err=exc):
            raise err

        token = command_log.bind(_broken)
        try:
            command_log.record(target="10.0.0.1", transport="ssh", command="showsys",
                               started=0.0, ok=True, result="ok")
        finally:
            command_log.unbind(token)
