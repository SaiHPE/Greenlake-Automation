"""Stage 1 least-privilege checks (STANDARD S2, ADR 0031)."""

from __future__ import annotations

import inspect

from pydantic import SecretStr

from alletra_onboard.adapters.array.wsapi_client import WsapiReader
from alletra_onboard.adapters.array.wsapi_writer import WsapiWriter
from alletra_onboard.application.provisioning.clients import make_wsapi
from alletra_onboard.application.runs.writer_clients import make_wsapi_writer
from alletra_onboard.domain.shared import EndpointCreds


class _ReadOnlyFakeSdk:
    """Records every SDK call and returns minimal valid payloads for reads."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __getattr__(self, name: str):
        def _call(*_args, **_kwargs):
            self.calls.append(name)
            if name == "getStorageSystemInfo":
                return {"name": "array-a"}
            if name == "getRemoteCopyGroup":
                return {"name": "grp1"}
            return {"members": []}

        return _call


def test_wsapi_reader_invokes_only_read_sdk_methods_and_exposes_no_writes():
    sdk = _ReadOnlyFakeSdk()
    reader = WsapiReader("192.0.2.1", "3paradm", "pw")
    reader._client = sdk

    args_for = {
        "find_host_by_wwn": ("10000090FA8B1111",),
        "remote_copy_group": ("grp1",),
    }
    public = sorted(
        name for name, obj in inspect.getmembers(WsapiReader, predicate=callable)
        if not name.startswith("_") and name not in ("connect", "close")
    )
    assert public, "expected public read methods on WsapiReader"
    for name in public:
        getattr(reader, name)(*args_for.get(name, ()))

    assert sdk.calls, "expected WsapiReader methods to query the SDK"
    non_reads = [c for c in sdk.calls if not c.startswith("get")]
    assert non_reads == [], f"WsapiReader invoked non-read SDK call(s): {non_reads}"

    writer_only = {
        name for name, obj in WsapiWriter.__dict__.items()
        if not name.startswith("_") and callable(obj)
    }
    assert writer_only and writer_only.isdisjoint(public)


def test_reader_and_writer_factories_return_distinct_privileges():
    creds = EndpointCreds(host="192.0.2.1", username="3paradm", password=SecretStr("pw"))
    reader = make_wsapi(creds)
    writer = make_wsapi_writer(creds)
    assert type(reader) is WsapiReader
    assert not isinstance(reader, WsapiWriter)
    assert isinstance(writer, WsapiWriter)
    assert isinstance(writer, WsapiReader)
