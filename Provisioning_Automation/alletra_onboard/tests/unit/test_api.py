import io

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook
from pydantic import SecretStr

from alletra_onboard import __version__
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.api.app import create_app
from alletra_onboard.application.platform.intake import csv_template
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    DsccSetupConfig,
    NetworkConfig,
    VerificationReport,
)
from alletra_onboard.domain.workflow import STEP_REGISTRY, mode_steps


def _client(tmp_path) -> TestClient:
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    return TestClient(create_app(service))


def _work_item_payload() -> dict:
    item = ArrayWorkItem(
        serial_number="SGHD45FF0Y",
        part_number="S0B84A",
        subscription_key=SecretStr("REALKEY123"),
        service_catalog_region_id="ap-northeast",
        dscc_region_code="jp1",
        cloudinit_url="https://169.254.239.27/cloudinit",
        network=NetworkConfig(
            mgmt_ipv4="10.64.154.225",
            mask="255.255.248.0",
            gateway="10.64.159.254",
            dns=["10.203.96.10"],
            ntp="ntp.example.com",
            timezone="Asia/Kolkata",
        ),
        dscc_setup=DsccSetupConfig(system_name="array01", country="India"),
    )
    payload = item.model_dump(mode="json")
    payload["subscription_key"] = "REALKEY123"  # model_dump masks; the client sends the real key
    return payload


def test_health(tmp_path):
    body = _client(tmp_path).get("/health").json()
    assert body["status"] == "ok"
    assert body["version"] == __version__  # SPEC-006 R1: the session report names the build


def test_index_is_revalidated_while_hashed_assets_cache_forever(tmp_path):
    # The UI is served from the same origin every release; without this policy the browser keeps
    # showing the PREVIOUS interface after an upgrade until a hard refresh (seen live on 0.13.0).
    client = _client(tmp_path)
    index = client.get("/")
    assert index.status_code == 200
    assert index.headers.get("cache-control") == "no-cache"
    asset = client.get("/assets/anything.js")  # policy applies to the path, whatever the status
    assert asset.headers.get("cache-control") == "public, max-age=31536000, immutable"


def test_app_profile_serves_the_step_registry(tmp_path):
    # ADR 0011 Phase 2: the wizard renders from the SERVED registry — this payload IS the contract
    # that replaced the hand-synced frontend mirror (modes.ts).
    body = _client(tmp_path).get("/app/profile").json()
    # SPEC-023 R9 (BL-21) added the Snapshots step, kind "snapshot", after the failover test.
    assert [s["key"] for s in body["steps"]] == [
        "greenlake", "cloudinit", "dscc", "discover", "ports", "zoning", "migrate", "provision",
        "replicate", "failover_test", "snapshots", "verify", "asbuilt",
    ]
    assert all(s["label"] and s["kind"] in ("init", "provision", "replicate", "migrate", "snapshot", "verify")
               and s["phase"]
               for s in body["steps"])
    assert body["modes"]["VERIFY_ONLY"] == ["verify", "asbuilt"]
    assert body["modes"]["FULL_ONBOARDING"] == ["greenlake", "cloudinit", "dscc", "verify", "asbuilt"]
    # SPEC-024 R8 (BL-25): Array ports sits between Discovery and SAN Zoning in the Provision only, Both and
    # Provision then replicate presets. Changed on purpose when the step joined the registry.
    assert body["modes"]["PROVISION_ONLY"] == ["discover", "ports", "zoning", "provision", "verify", "asbuilt"]
    # BOTH is every step EXCEPT the replication pair and the migration step, which need their own tabs
    # (SPEC-015 R4, SPEC-027 R3), and the Snapshots step, which is picked in Custom only (SPEC-023 R9).
    # Changed on purpose when each of those steps joined the registry.
    assert body["modes"]["BOTH"] == [s["key"] for s in body["steps"]
                                     if s["kind"] not in ("replicate", "migrate", "snapshot")]
    assert body["modes"]["REPLICATE"] == ["discover", "ports", "zoning", "provision", "replicate", "failover_test", "verify", "asbuilt"]
    # The Migrate preset is SPEC-027's own: discover, zoning, migrate (Peer Motion creates the volumes).
    assert body["modes"]["MIGRATE"] == ["discover", "zoning", "migrate", "verify", "asbuilt"]
    # A step whose work is not built yet is served with the sentence the mode chooser shows.
    unavailable = {s["key"]: s["unavailable"] for s in body["steps"] if s["unavailable"]}
    assert unavailable == {"migrate": "The Migration step is not built yet."}
    # Optional-dependency capability: a frozen build that fails to bundle the 3PAR SDK degrades
    # silently until WSAPI is first touched (how v0.14.0-rc.1 shipped broken). In the dev env the
    # SDK is installed so this must be True; on a packaged build, this one field is the smoke test.
    assert body["capabilities"]["wsapi_sdk"] is True


def test_create_get_and_list_runs_masks_secret(tmp_path):
    client = _client(tmp_path)
    created = client.post("/runs", json={"work_item": _work_item_payload()})
    assert created.status_code == 200
    run_id = created.json()["run"]["run_id"]

    detail = client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["run"]["serial_number"] == "SGHD45FF0Y"
    # the API must never echo the subscription key
    assert "REALKEY123" not in detail.text

    assert any(r["run_id"] == run_id for r in client.get("/runs").json()["runs"])
    events = client.get(f"/runs/{run_id}/events").json()["events"]
    assert events and events[0]["event_type"] == "run.created"


def test_run_not_found_is_404(tmp_path):
    client = _client(tmp_path)
    assert client.get("/runs/nope").status_code == 404
    assert client.post("/runs/nope/provision", json={}).status_code == 404


def test_mark_complete(tmp_path):
    client = _client(tmp_path)
    run_id = client.post("/runs", json={"work_item": _work_item_payload()}).json()["run"]["run_id"]
    done = client.post(f"/runs/{run_id}/complete")
    assert done.json()["run"]["status"] == "succeeded"


def test_prereq_firewall_and_connectivity(tmp_path, monkeypatch):
    client = _client(tmp_path)

    fw = client.get("/prereqs/firewall?region=jp1")
    assert fw.status_code == 200
    rules = fw.json()["rules"]
    fqdns = [r["fqdn"] for r in rules]
    assert "console.greenlake.hpe.com" in fqdns
    assert "jp1.data.cloud.hpe.com" in fqdns  # <instance> substituted for the region
    assert all(r["port"] == "TCP 443" for r in rules)

    txt = client.get("/prereqs/firewall.txt?region=jp1")
    assert txt.status_code == 200
    assert "attachment" in txt.headers["content-disposition"]
    assert "console.greenlake.hpe.com" in txt.text

    # Connectivity does real network I/O — stub it so the test stays hermetic.
    from alletra_onboard.application.platform import prereqs

    async def fake_check(region="jp1", timeout=5.0, manual_proxy=None):
        return [
            prereqs.ConnectivityResult("console.greenlake.hpe.com", 443, True, "reachable"),
            prereqs.ConnectivityResult("device.cloud.hpe.com", 443, False, "blocked (ConnectionRefusedError)"),
        ]

    monkeypatch.setattr(prereqs, "check_connectivity", fake_check)
    conn = client.get("/prereqs/connectivity?region=jp1").json()
    assert conn["all_reachable"] is False
    assert {c["host"] for c in conn["results"]} == {"console.greenlake.hpe.com", "device.cloud.hpe.com"}


def test_init_sheet_template_has_prerequisites_tab(tmp_path):
    import io

    from openpyxl import load_workbook

    resp = _client(tmp_path).get("/init-sheet/template")
    assert resp.status_code == 200
    wb = load_workbook(io.BytesIO(resp.content))
    assert wb.sheetnames[0] == "Initialisation"  # the fillable tab stays first (the parser reads it)
    assert "Prerequisites" in wb.sheetnames


def test_verify_endpoint_accepts_credentials_and_validates(tmp_path):
    # Inject a stub verify_fn so the endpoint never attempts a real SSH connection.
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(
        Settings(), store, InMemoryEventBus(),
        verify_fn=lambda item, username, password: VerificationReport(reachable=True),
    )
    client = TestClient(create_app(service))
    run_id = client.post("/runs", json={"work_item": _work_item_payload()}).json()["run"]["run_id"]
    client.post(f"/runs/{run_id}/complete")

    ok = client.post(f"/runs/{run_id}/verify", json={"username": "3paradm", "password": "pw"})
    assert ok.status_code == 200

    # SPEC-008 R2 (ADR 0013): this run came from a bare work item — no sheet credential — so a request
    # without a full pair is refused with the operator sentence, not a schema error
    refused = client.post(f"/runs/{run_id}/verify", json={"username": "3paradm"})
    assert refused.status_code == 409 and "holds no array credential" in refused.json()["detail"]
    assert client.post(f"/runs/{run_id}/verify", json={}).status_code == 409
    # R3: the run detail says so, and never carries a password
    detail = client.get(f"/runs/{run_id}").json()
    assert detail["array_credential"] == {"available": False, "source": "none", "username": "", "host": "10.64.154.225"}
    # unknown run -> 404
    assert client.post("/runs/nope/verify", json={"username": "u", "password": "p"}).status_code == 404


def test_template_and_parse_round_trip(tmp_path):
    client = _client(tmp_path)
    template = client.get("/work-items/template")
    assert template.status_code == 200
    assert template.text == csv_template()

    parsed = client.post("/work-items/parse", json={"csv_text": template.text})
    assert parsed.status_code == 200
    items = parsed.json()["work_items"]
    assert len(items) == 1 and items[0]["serial_number"] == "SGHD00EXAMPLE"
    # parse echoes back what the operator uploaded (for the editable form) — NOT masked...
    assert items[0]["subscription_key"] == "EXAMPLEKEY1234567890"
    # ...except passwords, which are never echoed.
    assert "password" not in items[0]["dscc_setup"]

    bad = client.post("/work-items/parse", json={"csv_text": "not,a,real\nheader,row,x"})
    assert bad.status_code == 422


# A COMPLETE sheet: every main-tab required field + the Provisioning tab (ADR 0005 revision — the
# sheet is filled in full BEFORE a mode is chosen, and the upload validates the whole superset).
_COMPLETE_MAIN = {
    "gl_client_id": "client-123", "gl_client_secret": "secret-xyz",
    "gl_token_url": "https://global.api.greenlake.hpe.com/authorization/v2/oauth2/t/token",
    "serial_number": "SGHD45FF0Y", "part_number": "S0B84A", "subscription_key": "YHHDKEY123",
    "service_catalog_region_id": "ap-northeast", "dscc_region_code": "jp1",
    "mgmt_ipv4": "10.64.154.225", "mask": "255.255.248.0", "gateway": "10.64.159.254",
    "dns1": "10.203.96.10", "ntp": "ntp1.example.net", "timezone": "Asia/Kolkata",
    "contact_first_name": "Jane", "contact_last_name": "Doe", "contact_language": "English",
    "contact_company": "HPE", "contact_phone": "8000000000", "contact_email": "jane@example.com",
    "dscc_system_name": "MPB10K-TEST", "dscc_country": "India",
    "secret_name": "b10000-admin", "secret_username": "3paradm",
}
_COMPLETE_PROV = {
    "targets": {
        "prov_array_host": "10.64.154.225", "prov_array_user": "3paradm", "prov_array_password": "arraypw",
        "prov_vcenter_host": "vc.example.com", "prov_vcenter_user": "administrator@vsphere.local",
        "prov_vcenter_password": "vcpw",
    },
    "volumes": [{"name": "CRV_Prod01", "size_gib": "1024"}],
    "hostsets": [{"name": "CRVLZ_Hostset"}],
}


def _fill_template(template_bytes: bytes, values: dict[str, str], prov: dict | None = None) -> str:
    """Fill the Value column of the Initialisation tab (and optionally the Provisioning + Volumes +
    Host sets tabs) -> base64 xlsx."""
    import base64
    import io

    from openpyxl import load_workbook

    from alletra_onboard.application.platform.init_sheet import (
        HOSTSET_COLUMNS,
        HOSTSETS_SHEET_NAME,
        PROVISIONING_SECTIONS,
        PROVISIONING_SHEET_NAME,
        SECTIONS,
        VOLUME_COLUMNS,
        VOLUMES_SHEET_NAME,
    )

    def _norm(s):
        return str(s).strip().removesuffix("*").strip()

    def fill_kv(ws, sections, data):
        label_to_key = {label: key for _, fields in sections for key, label, _, _ in fields}
        for row in ws.iter_rows(min_row=2):
            if row[0].value is None:
                continue
            key = label_to_key.get(_norm(row[0].value))
            if key in data:
                row[1].value = data[key]

    def fill_table(ws, columns, records):
        header_to_key = {_norm(label): key for key, label, _ in columns}
        header_row, col_of = None, {}
        for r in ws.iter_rows():
            found = {header_to_key[_norm(c.value)]: c.column for c in r if c.value is not None and _norm(c.value) in header_to_key}
            if found:
                header_row, col_of = r[0].row, found
                break
        for i, rec in enumerate(records):
            for key, val in rec.items():
                ws.cell(row=header_row + 1 + i, column=col_of[key], value=val)

    wb = load_workbook(io.BytesIO(template_bytes))
    fill_kv(wb.active, SECTIONS, values)
    if prov is not None and PROVISIONING_SHEET_NAME in wb.sheetnames:
        fill_kv(wb[PROVISIONING_SHEET_NAME], PROVISIONING_SECTIONS, prov.get("targets", {}))
        fill_table(wb[VOLUMES_SHEET_NAME], VOLUME_COLUMNS, prov.get("volumes", []))
        fill_table(wb[HOSTSETS_SHEET_NAME], HOSTSET_COLUMNS, prov.get("hostsets", []))
    buffer = io.BytesIO()
    wb.save(buffer)
    return base64.b64encode(buffer.getvalue()).decode()


def _upload_complete(client) -> str:
    """Upload a complete sheet and return the hold token."""
    template = client.get("/init-sheet/template").content
    b64 = _fill_template(template, _COMPLETE_MAIN, _COMPLETE_PROV)
    resp = client.post("/init-sheet/upload", json={"content_b64": b64})
    assert resp.status_code == 200, resp.text
    return resp.json()["token"]


def test_init_sheet_upload_holds_complete_sheet_and_saves_creds(tmp_path, monkeypatch):
    import base64

    from alletra_onboard.application.platform.configuring import read_env

    monkeypatch.chdir(tmp_path)  # the API writes .env in the working directory
    client = _client(tmp_path)

    template = client.get("/init-sheet/template")
    assert template.status_code == 200
    assert "spreadsheetml" in template.headers["content-type"]

    b64 = _fill_template(template.content, _COMPLETE_MAIN, _COMPLETE_PROV)
    resp = client.post("/init-sheet/upload", json={"content_b64": b64})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    # A complete sheet is HELD (token), not turned into a run yet — the mode step mints the run.
    assert body["token"] and "run" not in body
    assert body["credentials_saved"] is True
    assert body["work_item"]["serial_number"] == "SGHD45FF0Y"
    # the admin password is not in the sheet at all, and is never echoed to the UI
    assert "password" not in body["work_item"]["dscc_setup"]
    # GreenLake credentials from the sheet were written to .env
    env = read_env(tmp_path / ".env")
    assert env["GL_CLIENT_ID"] == "client-123"
    assert env["GL_CLIENT_SECRET"] == "secret-xyz"

    # a non-xlsx upload is a clean 422
    bad = client.post("/init-sheet/upload", json={"content_b64": base64.b64encode(b"nope").decode()})
    assert bad.status_code == 422


def test_incomplete_sheet_is_rejected_regardless_of_mode(tmp_path, monkeypatch):
    # The sheet must be COMPLETE at upload (no mode is chosen yet) — a sparse sheet is a clean 422.
    monkeypatch.chdir(tmp_path)
    client = _client(tmp_path)
    template = client.get("/init-sheet/template").content
    b64 = _fill_template(template, {"serial_number": "SGHD45FF0Y", "mgmt_ipv4": "10.64.154.225"})
    resp = client.post("/init-sheet/upload", json={"content_b64": b64})
    assert resp.status_code == 422
    assert "API Client" in resp.text  # missing GreenLake creds reported


def test_run_from_sheet_creates_run_with_chosen_mode(tmp_path, monkeypatch):
    # The mode is chosen AFTER the sheet: /runs/from-sheet mints the run from the held sheet + mode.
    monkeypatch.chdir(tmp_path)
    client = _client(tmp_path)
    token = _upload_complete(client)

    resp = client.post("/runs/from-sheet", json={"token": token, "mode": "VERIFY_ONLY"})
    assert resp.status_code == 200, resp.text
    run = resp.json()["run"]
    assert run["mode"] == "VERIFY_ONLY"
    assert run["current_phase"] == "CONFIG_VERIFY"  # resumes straight to the SSH check
    assert run["serial_number"] == "SGHD45FF0Y"

    # the hold is single-use — a second attempt with the same token is a clean 410
    again = client.post("/runs/from-sheet", json={"token": token, "mode": "BOTH"})
    assert again.status_code == 410


def test_run_from_sheet_unknown_token_is_410(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client = _client(tmp_path)
    resp = client.post("/runs/from-sheet", json={"token": "does-not-exist", "mode": "FULL_ONBOARDING"})
    assert resp.status_code == 410


def test_proxy_status_and_manual_override(tmp_path, monkeypatch):
    import os

    monkeypatch.chdir(tmp_path)
    for v in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        monkeypatch.delenv(v, raising=False)
    try:
        client = _client(tmp_path)
        saved = client.post("/prereqs/proxy", json={"proxy": "myproxy:3128"}).json()
        assert saved["manual"] == "myproxy:3128"
        assert saved["effective"] == "http://myproxy:3128" and saved["source"] == "manual"
        got = client.get("/prereqs/proxy").json()
        assert got["source"] == "manual" and got["effective"] == "http://myproxy:3128"
        cleared = client.post("/prereqs/proxy", json={"proxy": ""}).json()
        assert not cleared["manual"]  # override removed -> falls back to auto-detect
    finally:
        for v in ("ALLETRA_PROXY", "HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "NO_PROXY", "no_proxy"):
            os.environ.pop(v, None)


def test_proxy_can_be_forced_direct_and_the_choice_persists(tmp_path, monkeypatch):
    """REPORTED FROM THE UI: a detected proxy could not be removed — an empty override means
    "auto-detect", so there was no way to say "this machine has no proxy". Saving the direct
    sentinel must: report forced_direct, resolve to no proxy, clear the published env, and land in
    .env so it survives a restart (an empty value cannot — set_env_values ignores empties by design
    so a blank field never wipes a saved secret)."""
    import os

    from alletra_onboard.application.platform import proxy as proxymod

    monkeypatch.chdir(tmp_path)
    for v in ("ALLETRA_PROXY", "HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        monkeypatch.delenv(v, raising=False)
    # A machine WITH a system proxy, so forcing direct has something to override.
    monkeypatch.setattr(proxymod, "_win_system_proxy", lambda url: "http://detected:8080")
    try:
        client = _client(tmp_path)
        auto = client.get("/prereqs/proxy").json()
        assert auto["source"] == "system" and auto["detected"] == "http://detected:8080"

        forced = client.post("/prereqs/proxy", json={"proxy": "direct"}).json()   # any accepted word
        assert forced["forced_direct"] is True
        assert forced["effective"] is None and forced["source"] == "direct"
        assert forced["detected"] == "http://detected:8080"    # still reported, just not used
        assert "HTTPS_PROXY" not in os.environ                 # and nothing left routing traffic

        assert "ALLETRA_PROXY=direct://" in (tmp_path / ".env").read_text(encoding="utf-8")

        back = client.post("/prereqs/proxy", json={"proxy": ""}).json()           # -> auto-detect
        assert back["forced_direct"] is False and back["effective"] == "http://detected:8080"
    finally:
        for v in ("ALLETRA_PROXY", "HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "NO_PROXY", "no_proxy"):
            os.environ.pop(v, None)


def test_app_profile_defaults_to_full(tmp_path, monkeypatch):
    monkeypatch.delenv("ALLETRA_PROFILE", raising=False)
    prof = _client(tmp_path).get("/app/profile").json()
    assert prof["profile"] == "full" and prof["init_only"] is False and "Onboarding" in prof["title"]


@pytest.mark.parametrize(("profile", "title", "mode"), [
    ("full", "Alletra MP B10000 Onboarding", "BOTH"),
    ("init-only", "Alletra MP Initialization", "FULL_ONBOARDING"),
])
def test_each_build_profile_serves_the_step_registry_and_takes_a_workbook_to_a_run(
        tmp_path, monkeypatch, profile, title, mode):
    """STANDARD X3: both builds start, serve the step registry and mint a run from their own workbook.
    The init-only build was the only one checked here before; a moved module must not break either."""
    provisioning_tab = profile == "full"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ALLETRA_PROFILE", profile)
    client = _client(tmp_path)

    prof = client.get("/app/profile").json()
    assert prof["profile"] == profile and prof["init_only"] is (profile == "init-only") and prof["title"] == title
    # both builds serve the whole registry and every preset; the UI narrows the mode chooser from `init_only`
    assert [s["key"] for s in prof["steps"]] == [s.key for s in STEP_REGISTRY]
    assert prof["modes"] == {preset.value: list(keys) for preset, keys in mode_steps().items()}

    # the init-only template ships an onboarding-only sheet — no Provisioning tab
    tpl = client.get("/init-sheet/template").content
    wb = load_workbook(io.BytesIO(tpl))
    assert "Initialisation" in wb.sheetnames and ("Provisioning" in wb.sheetnames) is provisioning_tab

    # an onboarding-only sheet (no Provisioning creds) uploads fine under the init-only profile
    filled = _fill_template(tpl, _COMPLETE_MAIN, _COMPLETE_PROV if provisioning_tab else None)
    resp = client.post("/init-sheet/upload", json={"content_b64": filled})
    assert resp.status_code == 200, resp.text
    assert resp.json()["token"]
    # and it mints a run of the profile's own kind, which the API then serves
    minted = client.post("/runs/from-sheet", json={"token": resp.json()["token"], "mode": mode})
    assert minted.status_code == 200, minted.text
    run = minted.json()["run"]
    assert run["mode"] == mode
    assert client.get(f"/runs/{run['run_id']}").json()["run"]["serial_number"] == _COMPLETE_MAIN["serial_number"]


def test_storage_builder_saves_composition_and_objects_needs_discovery(tmp_path):
    client = _client(tmp_path)
    token = _upload_complete(client)
    run = client.post("/runs/from-sheet", json={"token": token, "mode": "BOTH"}).json()["run"]
    rid = run["run_id"]

    # the dropdown palette needs discovery first -> 409
    assert client.get(f"/runs/{rid}/storage/objects").status_code == 409

    # the builder saves the composed host-set membership + exports onto the intent (no discovery needed)
    builder = {
        "host_sets": [{"name": "CRVLZ_Hostset", "members": ["esx1", "esx2"]}],
        "exports": [{"source_kind": "volume", "source_name": "CRV_Prod01",
                     "target_kind": "hostset", "target_name": "CRVLZ_Hostset", "lun": 10}],
        "vvsets": {},
    }
    resp = client.post(f"/runs/{rid}/storage/builder", json=builder)
    assert resp.status_code == 200, resp.text
    comp = resp.json()
    assert comp["exports"][0]["lun"] == 10
    assert comp["host_sets"][0]["members"] == ["esx1", "esx2"]

    # tier-2 path verify is registered and also needs discovery first -> 409
    assert client.post(f"/runs/{rid}/storage/verify-paths").status_code == 409

    # SPEC-016: the replication preview is registered; a workbook without the Replication tab -> 409
    refused = client.post(f"/runs/{rid}/replication/preview")
    assert refused.status_code == 409 and "no Replication tab" in refused.json()["detail"]
    # SPEC-017: so is the failover test, with and without a body
    assert client.post(f"/runs/{rid}/replication/failover-test").status_code == 409
    refused = client.post(f"/runs/{rid}/replication/failover-test", json={"group": "zz_rc_test_rcg", "confirm": None})
    assert refused.status_code == 409 and "no Replication tab" in refused.json()["detail"]
    # and REPLICATE mode cannot even be minted from such a workbook -> 422 with the sentence
    token = _upload_complete(client)
    minted = client.post("/runs/from-sheet", json={"token": token, "mode": "REPLICATE"})
    assert minted.status_code == 422 and "'Replication' tab" in minted.json()["detail"]


def test_config_roundtrip_masks_secret(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the API writes .env in the working directory
    client = _client(tmp_path)
    saved = client.post(
        "/config",
        json={"gl_client_id": "abc", "gl_client_secret": "supersecret", "gl_token_url": "https://t"},
    )
    assert saved.status_code == 200
    body = saved.json()
    assert body["configured"] is True
    assert body["values"]["GL_CLIENT_ID"] == "abc"
    assert body["values"]["GL_CLIENT_SECRET"] == "****"
    assert "supersecret" not in saved.text


def test_init_sheet_compose_round_trips_through_upload(tmp_path, monkeypatch):
    """SPEC-006 R3: the session runner sends the operator's sheet + scenario rows and uploads what comes
    back; the run's intent must carry the scenario rows and nothing from the base's row tables."""
    import base64

    monkeypatch.chdir(tmp_path)
    client = _client(tmp_path)
    template = client.get("/init-sheet/template").content
    base_b64 = _fill_template(template, _COMPLETE_MAIN, _COMPLETE_PROV)
    resp = client.post("/init-sheet/compose", json={
        "base_b64": base_b64,
        "volumes": [{"name": "zz_s6_vol01", "size_gib": "1", "vvset": "zz_s6_vvs"}],
        "hostsets": [{"name": "zz_s6_hs", "members": "esx1"}],
    })
    assert resp.status_code == 200, resp.text
    composed = resp.json()["content_b64"]
    assert base64.b64decode(composed)[:2] == b"PK"
    up = client.post("/init-sheet/upload", json={"content_b64": composed})
    assert up.status_code == 200, up.text
    # SPEC-006 R1: the runner learns the array from the sheet — hosts and users, never a password
    targets = up.json()["targets"]
    assert targets["array_host"] == _COMPLETE_PROV["targets"]["prov_array_host"]
    assert targets["array_user"] == "3paradm"
    assert not any("password" in k for k in targets)
    run = client.post("/runs/from-sheet", json={"token": up.json()["token"], "mode": "PROVISION_ONLY"})
    assert run.status_code == 200, run.text
    intent = client.get(f"/runs/{run.json()['run']['run_id']}").json()
    # the intent is not echoed with passwords; check through the objects palette shape instead
    assert intent["run"]["run_id"]
    bad = client.post("/init-sheet/compose", json={"base_b64": base64.b64encode(b"not a workbook").decode()})
    assert bad.status_code in (400, 422)


def test_upload_lists_the_replication_ports_to_set_up(tmp_path, monkeypatch):
    """SPEC-021 R1, seen live 2026-11-05: the review after upload named the peer but not the four port rows."""
    import base64

    monkeypatch.chdir(tmp_path)
    client = _client(tmp_path)
    base_b64 = _fill_template(client.get("/init-sheet/template").content, _COMPLETE_MAIN, _COMPLETE_PROV)
    rows = [{"array": a, "port": p, "ip": ip, "netmask": "255.255.254.0"}
            for a, p, ip in (("this", "0:4:4", "10.93.18.11"), ("this", "1:4:4", "10.93.18.13"),
                             ("peer", "0:1:1", "10.93.18.19"), ("peer", "1:1:1", "10.93.18.20"))]
    replication = {"fields": {"peer_host": "10.132.30.28", "peer_user": "3paradm", "peer_password": "pw"},
                   "rows": [{"vvset": "zz_rc_vvs", "peer_cpg": "SSD_r6", "mode": "sync"}]}
    for network, want in ((rows, ["this array 0:4:4 10.93.18.11", "this array 1:4:4 10.93.18.13",
                                  "peer 0:1:1 10.93.18.19", "peer 1:1:1 10.93.18.20"]), (None, [])):
        body = {"base_b64": base_b64, "replication": {**replication, **({"network": network} if network else {})}}
        composed = client.post("/init-sheet/compose", json=body).json()["content_b64"]
        up = client.post("/init-sheet/upload", json={"content_b64": composed})
        assert up.status_code == 200, up.text
        assert up.json()["replication_ports"] == want
        assert base64.b64decode(composed)[:2] == b"PK"


def test_upload_lists_the_snapshot_rows_for_the_review(tmp_path, monkeypatch):
    """SPEC-023 R9: the review needs to know the Snapshots tab is filled, to say so when the mode lacks the step."""
    monkeypatch.chdir(tmp_path)
    client = _client(tmp_path)
    base_b64 = _fill_template(client.get("/init-sheet/template").content, _COMPLETE_MAIN, _COMPLETE_PROV)
    # BL-60: a row that asks for a schedule names it (live 2026-11-17: the line did not say which schedule).
    rows = [{"source": "zz_sn_vvs", "snapshot_now": "yes", "every": "4", "unit": "hours", "expire_hours": "24"},
            {"source": "zz_sn_vol03", "kind": "volume", "snapshot_now": "yes", "expire_hours": "2", "read_only": "no"},
            {"source": "zz_snap_vvs", "every": "1", "unit": "hours", "expire_hours": "2", "schedule_name": "zz_snap_sched"}]
    for snapshots, want in ((rows, [("zz_sn_vvs: Snapshot now · schedule zz_sn_vvs_snap, every 4 hours from 00:00, every "
                                     "day, kept 24 hours, read-only"),
                                    "zz_sn_vol03: Snapshot now · kept 2 hours, read-write",
                                    "zz_snap_vvs: schedule zz_snap_sched, every hour, every day, kept 2 hours, read-only"]),
                            ([], [])):
        composed = client.post("/init-sheet/compose", json={"base_b64": base_b64, "snapshots": snapshots}).json()["content_b64"]
        up = client.post("/init-sheet/upload", json={"content_b64": composed})
        assert up.status_code == 200, up.text
        assert up.json()["snapshot_rows"] == want


_MIGRATION = {"fields": {"source_host": "192.0.2.10", "source_user": "lab-reader", "source_password": "src-secret-pw"},
              "rows": [{"host": "lab-host-01", "cpg": "SSD_r6", "type": "offline"}]}


def _upload_with_migration(client, migration: dict | None) -> tuple[str, str]:
    """Compose the complete sheet with the Migration tab as given, upload it: (hold token, response text)."""
    base_b64 = _fill_template(client.get("/init-sheet/template").content, _COMPLETE_MAIN, _COMPLETE_PROV)
    composed = client.post("/init-sheet/compose", json={"base_b64": base_b64, "migration": migration})
    assert composed.status_code == 200, composed.text
    up = client.post("/init-sheet/upload", json={"content_b64": composed.json()["content_b64"]})
    assert up.status_code == 200, up.text
    return up.json()["token"], up.text


def test_the_migration_tab_composes_and_uploads_without_echoing_the_source_password(tmp_path, monkeypatch):
    """SPEC-027 R1/R2: the session runner can fill the tab; the held sheet keeps the source password and
    the response never shows it."""
    monkeypatch.chdir(tmp_path)
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    client = TestClient(create_app(OnboardingService(Settings(), store, InMemoryEventBus())))
    token, text = _upload_with_migration(client, _MIGRATION)
    assert "src-secret-pw" not in text
    _item, intent = store.pop_pending_sheet(token)
    assert intent.migration.source.password.get_secret_value() == "src-secret-pw"
    assert [(h.host, h.type) for h in intent.migration.hosts] == [("lab-host-01", "offline")]


def test_a_migrate_run_is_refused_without_the_tab_and_while_the_step_is_not_built(tmp_path, monkeypatch):
    """SPEC-027 R3: minting a run with the Migration step from a workbook without the tab is a 422 with
    one sentence. With the tab it is still refused, with the not-built sentence, until the step exists."""
    monkeypatch.chdir(tmp_path)
    client = _client(tmp_path)
    for mode, steps in (("MIGRATE", []), ("CUSTOM", ["migrate", "verify"])):
        token, _text = _upload_with_migration(client, None)
        minted = client.post("/runs/from-sheet", json={"token": token, "mode": mode, "selected_steps": steps})
        assert minted.status_code == 422
        assert minted.json()["detail"] == (
            "The Migration step needs the workbook's 'Migration' tab (the source array and the hosts to migrate). "
            "Fill it in and upload again, or choose a mode without it."
        )
        token, _text = _upload_with_migration(client, _MIGRATION)
        minted = client.post("/runs/from-sheet", json={"token": token, "mode": mode, "selected_steps": steps})
        assert minted.status_code == 422
        assert minted.json()["detail"] == "The Migration step is not built yet. Choose a mode without it."
    # the tab does not stop any other mode
    token, _text = _upload_with_migration(client, _MIGRATION)
    assert client.post("/runs/from-sheet", json={"token": token, "mode": "PROVISION_ONLY"}).status_code == 200


# Owner, 2026-11-19: check a tab only when the run uses it. Until then a problem in any tab refused the
# upload, so a Full onboarding run could be stopped by a tab it never reads.
_BAD_REPLICATION_NETWORK = {
    "fields": {"peer_host": "10.132.30.28", "peer_user": "3paradm", "peer_password": "pw"},
    "rows": [{"vvset": "zz_rc_vvs", "peer_cpg": "SSD_r6", "mode": "sync"}],
    "network": [{"array": "this", "port": "0:4:4", "ip": "10.93.18.300", "netmask": "255.255.254.0"}],
}


def _upload_with(client, **tabs) -> object:
    base_b64 = _fill_template(client.get("/init-sheet/template").content, _COMPLETE_MAIN, _COMPLETE_PROV)
    composed = client.post("/init-sheet/compose", json={"base_b64": base_b64, **tabs})
    assert composed.status_code == 200, composed.text
    return client.post("/init-sheet/upload", json={"content_b64": composed.json()["content_b64"]})


def test_a_problem_in_a_tab_onboarding_does_not_use_is_listed_and_stops_only_a_run_that_uses_it(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client = _client(tmp_path)
    ok_volume = {"name": "CRV_Prod01", "size_gib": "1024"}
    cases = (
        ({"volumes": [ok_volume, {"name": "zz_bad+", "size_gib": "1"}]}, "Volume 'zz_bad+' — Name:", "PROVISION_ONLY"),
        ({"volumes": [ok_volume, {"name": "zz_big", "size_gib": str(1024 * 1024)}]},
         "more than the array can create in one volume", "BOTH"),
        ({"replication": _BAD_REPLICATION_NETWORK},
         "Replication network tab — row 'this 0:4:4': RCIP address '10.93.18.300' is not an IPv4 address.", "PROVISION_ONLY"),
    )
    for tabs, sentence, provisioning_mode in cases:
        up = _upload_with(client, **tabs)
        assert up.status_code == 200, up.text
        problems = up.json()["problems"]
        assert len(problems) == 1 and sentence in problems[0], problems
        token = up.json()["token"]
        runs_before = len(client.get("/runs").json()["runs"])

        refused = client.post("/runs/from-sheet", json={"token": token, "mode": provisioning_mode})
        assert refused.status_code == 422
        assert refused.json()["detail"] == problems[0]
        assert len(client.get("/runs").json()["runs"]) == runs_before
        custom = client.post("/runs/from-sheet", json={"token": token, "mode": "CUSTOM", "selected_steps": ["discover", "verify"]})
        assert custom.status_code == 422 and custom.json()["detail"] == problems[0]

        # the refusal kept the hold: the same upload still mints a Full onboarding run
        minted = client.post("/runs/from-sheet", json={"token": token, "mode": "FULL_ONBOARDING"})
        assert minted.status_code == 200, minted.text
        run_id = minted.json()["run"]["run_id"]
        # the rest of the sheet is still held: verify keeps the Provisioning tab's array account
        assert client.get(f"/runs/{run_id}").json()["array_credential"]["source"] == "provisioning"


def test_a_valid_sheet_lists_no_problem_and_an_initialisation_problem_still_refuses_the_upload(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    client = TestClient(create_app(OnboardingService(Settings(), store, InMemoryEventBus())))
    up = _upload_with(client)
    assert up.status_code == 200 and up.json()["problems"] == []
    assert store.pending_sheet_workbook(up.json()["token"]) is None   # held exactly as before

    template = client.get("/init-sheet/template").content
    no_serial = {k: v for k, v in _COMPLETE_MAIN.items() if k != "serial_number"}
    bad_volume = {**_COMPLETE_PROV, "volumes": [{"name": "zz_bad+", "size_gib": "1"}]}
    resp = client.post("/init-sheet/upload", json={"content_b64": _fill_template(template, no_serial, bad_volume)})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "Initialisation sheet did not parse: Missing required fields: Storage system serial number"


# ------------------------------------------------------------------ characterisation (create_app split)

_EXPECTED_OPENAPI_ROUTES: tuple[tuple[str, str, str], ...] = (
    ("get", "/health", "health_health_get"),
    ("get", "/app/profile", "app_profile_app_profile_get"),
    ("get", "/config", "get_config_config_get"),
    ("post", "/config", "set_config_config_post"),
    ("post", "/config/check", "config_check_config_check_post"),
    ("get", "/prereqs/firewall", "prereq_firewall_prereqs_firewall_get"),
    ("get", "/prereqs/firewall.txt", "prereq_firewall_txt_prereqs_firewall_txt_get"),
    ("get", "/prereqs/connectivity", "prereq_connectivity_prereqs_connectivity_get"),
    ("get", "/prereqs/proxy", "prereq_proxy_status_prereqs_proxy_get"),
    ("post", "/prereqs/proxy", "prereq_proxy_save_prereqs_proxy_post"),
    ("get", "/work-items/template", "work_item_template_work_items_template_get"),
    ("post", "/work-items/parse", "parse_work_items_work_items_parse_post"),
    ("get", "/init-sheet/template", "init_sheet_template_init_sheet_template_get"),
    ("post", "/init-sheet/compose", "init_sheet_compose_init_sheet_compose_post"),
    ("post", "/init-sheet/upload", "init_sheet_upload_init_sheet_upload_post"),
    ("get", "/runs", "list_runs_runs_get"),
    ("post", "/runs", "create_run_runs_post"),
    ("post", "/runs/from-sheet", "create_run_from_sheet_runs_from_sheet_post"),
    ("get", "/runs/{run_id}", "get_run_runs__run_id__get"),
    ("post", "/runs/{run_id}/provision", "run_provision_runs__run_id__provision_post"),
    ("post", "/runs/{run_id}/cloudinit", "run_cloudinit_runs__run_id__cloudinit_post"),
    ("post", "/runs/{run_id}/dscc", "run_dscc_runs__run_id__dscc_post"),
    ("post", "/runs/{run_id}/verify", "run_verify_runs__run_id__verify_post"),
    ("post", "/runs/{run_id}/asbuilt", "run_asbuilt_runs__run_id__asbuilt_post"),
    ("get", "/runs/{run_id}/asbuilt/download", "download_asbuilt_runs__run_id__asbuilt_download_get"),
    ("post", "/runs/{run_id}/complete", "complete_run_runs__run_id__complete_post"),
    ("post", "/runs/{run_id}/discover", "run_discover_runs__run_id__discover_post"),
    ("get", "/runs/{run_id}/ports", "array_ports_runs__run_id__ports_get"),
    ("post", "/runs/{run_id}/ports/preview", "run_ports_preview_runs__run_id__ports_preview_post"),
    ("post", "/runs/{run_id}/zoning/preview", "run_zoning_preview_runs__run_id__zoning_preview_post"),
    ("post", "/runs/{run_id}/zoning/plan", "run_zoning_plan_runs__run_id__zoning_plan_post"),
    ("post", "/zoning/render", "zoning_render_zoning_render_post"),
    ("get", "/runs/{run_id}/storage/preflight", "storage_preflight_runs__run_id__storage_preflight_get"),
    ("get", "/runs/{run_id}/storage/objects", "storage_objects_runs__run_id__storage_objects_get"),
    ("post", "/runs/{run_id}/storage/builder", "storage_builder_runs__run_id__storage_builder_post"),
    ("post", "/runs/{run_id}/storage/preview", "run_storage_preview_runs__run_id__storage_preview_post"),
    ("post", "/runs/{run_id}/storage/apply", "run_storage_apply_runs__run_id__storage_apply_post"),
    ("post", "/runs/{run_id}/storage/verify-paths", "run_storage_verify_paths_runs__run_id__storage_verify_paths_post"),
    ("post", "/runs/{run_id}/replication/preview", "run_replication_preview_runs__run_id__replication_preview_post"),
    ("post", "/runs/{run_id}/replication/link-check", "run_replication_link_check_runs__run_id__replication_link_check_post"),
    ("post", "/runs/{run_id}/replication/apply", "run_replication_apply_runs__run_id__replication_apply_post"),
    ("post", "/runs/{run_id}/replication/verify", "run_replication_verify_runs__run_id__replication_verify_post"),
    ("post", "/runs/{run_id}/replication/failover-test", "run_failover_test_runs__run_id__replication_failover_test_post"),
    ("get", "/runs/{run_id}/snapshots", "snapshots_tab_runs__run_id__snapshots_get"),
    ("post", "/runs/{run_id}/snapshots/preview", "run_snapshots_preview_runs__run_id__snapshots_preview_post"),
    ("post", "/runs/{run_id}/snapshots/apply", "run_snapshots_apply_runs__run_id__snapshots_apply_post"),
    ("post", "/runs/{run_id}/snapshots/verify", "run_snapshots_verify_runs__run_id__snapshots_verify_post"),
    ("get", "/runs/{run_id}/trust", "trusted_devices_runs__run_id__trust_get"),
    ("post", "/runs/{run_id}/trust/retrust", "retrust_device_runs__run_id__trust_retrust_post"),
    ("get", "/runs/{run_id}/events", "list_events_runs__run_id__events_get"),
    ("get", "/runs/{run_id}/stream", "stream_events_runs__run_id__stream_get"),
    ("get", "/runs/{run_id}/console/log", "console_log_runs__run_id__console_log_get"),
    ("get", "/runs/{run_id}/console/targets", "console_targets_runs__run_id__console_targets_get"),
    ("post", "/runs/{run_id}/console", "console_run_runs__run_id__console_post"),
    ("post", "/runs/{run_id}/console/terminal", "console_terminal_runs__run_id__console_terminal_post"),
    ("get", "/runs/{run_id}/console/stream", "console_stream_runs__run_id__console_stream_get"),
    ("post", "/browser/launch", "browser_launch_browser_launch_post"),
    ("post", "/tools/discovery/launch", "discovery_launch_tools_discovery_launch_post"),
    ("get", "/system/clock", "get_clock_system_clock_get"),
    ("post", "/system/clock/sync", "post_clock_sync_system_clock_sync_post"),
    ("post", "/preflight", "preflight_preflight_post"),
)

def test_both_build_profiles_serve_the_same_routes(monkeypatch):
    """Every path, method and operationId, in order, in both builds. The schemas themselves are pinned by
    the api-types gate step as a readable diff of frontend/generated/api.ts (ADR 0032)."""
    from typing import Any, cast

    specs: dict[str, dict] = {}
    for profile in ("full", "init-only"):
        monkeypatch.setenv("ALLETRA_PROFILE", profile)
        spec = create_app(cast(Any, object())).openapi()
        assert spec["info"] == {"title": "Alletra Onboard", "version": __version__}
        routes = tuple(
            (method, path, op["operationId"])
            for path, methods in spec["paths"].items()
            for method, op in methods.items()
        )
        assert routes == _EXPECTED_OPENAPI_ROUTES
        specs[profile] = spec
    assert specs["full"] == specs["init-only"]


def _response_body(resp) -> object:
    if resp.headers.get("content-type", "").startswith("application/json"):
        return resp.json()
    return resp.text


def _mock_service_failing(target: str, exc: BaseException):
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    svc = MagicMock()
    svc.get_run.return_value = SimpleNamespace(run_id="r1", serial_number="SN1")
    if target == "get_run":
        svc.get_run.side_effect = exc
    elif target == "console.run":
        async def _fail(*_args, **_kwargs):
            raise exc
        svc.console.run = _fail
    else:
        getattr(svc, target).side_effect = exc
    return svc


def _step_router_cases() -> tuple[tuple[str, str, dict | None, str], ...]:
    return (
        ("POST", "/runs/r1/provision", {}, "start_provision"),
        ("POST", "/runs/r1/verify", {}, "start_verify"),
        ("POST", "/runs/r1/discover", None, "start_discover"),
        ("POST", "/runs/r1/storage/apply", {}, "start_storage_apply"),
        ("POST", "/runs/r1/replication/apply", {}, "start_replication_apply"),
        ("POST", "/runs/r1/snapshots/apply", {}, "start_snapshots_apply"),
    )


def test_step_router_error_mappings_are_pinned():
    """Characterisation: pin exact status code and body for every error type across the six step routers."""
    from alletra_onboard.application.service import (
        RunBusyError,
        RunNotFoundError,
        StepPreconditionError,
    )
    from alletra_onboard.domain.approval import ApprovalError
    from alletra_onboard.domain.errors import DeviceError
    from alletra_onboard.domain.ports import StoredCredentialsUnreadableError

    expected = (
        (StepPreconditionError("missing prerequisite"), 409, {"detail": "missing prerequisite"}),
        (RunBusyError("r1"), 409, {"detail": "a step is already running for this run"}),
        (ApprovalError("approval spent"), 500, "Internal Server Error"),
        (DeviceError("array unreachable"), 500, "Internal Server Error"),
        (RunNotFoundError("no such intent"), 404, {"detail": "no such intent"}),
        (RunNotFoundError(""), 404, {"detail": "not found"}),
        (StoredCredentialsUnreadableError("key missing"), 409, {"detail": "key missing"}),
    )
    for method, path, payload, fn_name in _step_router_cases():
        for exc, status, body in expected:
            client = TestClient(create_app(_mock_service_failing(fn_name, exc)), raise_server_exceptions=False)
            resp = client.request(method, path, json=payload) if payload is not None else client.request(method, path)
            assert (resp.status_code, _response_body(resp)) == (status, body), (path, type(exc).__name__)
        # Missing run before step lookup is always 404 "run not found"
        missing = TestClient(create_app(_mock_service_failing("get_run", RunNotFoundError("r1"))),
                             raise_server_exceptions=False)
        resp = missing.request(method, path, json=payload) if payload is not None else missing.request(method, path)
        assert (resp.status_code, _response_body(resp)) == (404, {"detail": "run not found"})


def test_non_step_router_error_mappings_are_pinned(monkeypatch):
    """Characterisation: pin exact status code and body for representative routes in every non-step router."""
    from alletra_onboard.application.platform import clients as platform_clients
    from alletra_onboard.application.platform import prereqs as prereqs_mod
    from alletra_onboard.application.service import (
        DevicePinNotFoundError,
        PendingSheetNotFoundError,
        RunBusyError,
        RunNotFoundError,
        StepPreconditionError,
    )
    from alletra_onboard.domain.approval import ApprovalError
    from alletra_onboard.domain.errors import DeviceError
    from alletra_onboard.domain.ports import StoredCredentialsUnreadableError

    service_cases = (
        ("GET", "/runs/r1", None, "get_run", RunNotFoundError("r1"), 404, {"detail": "run not found"}),
        ("GET", "/runs/r1", None, "get_run", StoredCredentialsUnreadableError("key missing"), 409, {"detail": "key missing"}),
        ("GET", "/runs/r1", None, "get_run", DeviceError("array unreachable"), 500, "Internal Server Error"),
        ("POST", "/runs/from-sheet", {"token": "t", "mode": "FULL_ONBOARDING"}, "create_run_from_pending",
         PendingSheetNotFoundError("t"), 410,
         {"detail": "This uploaded sheet is no longer held — re-upload the Initialisation sheet."}),
        ("POST", "/runs/from-sheet", {"token": "t", "mode": "FULL_ONBOARDING"}, "create_run_from_pending",
         ValueError("bad mode"), 422, {"detail": "bad mode"}),
        ("POST", "/runs/from-sheet", {"token": "t", "mode": "FULL_ONBOARDING"}, "create_run_from_pending",
         ApprovalError("approval spent"), 500, "Internal Server Error"),
        ("GET", "/runs/r1/ports", None, "get_ports", RunNotFoundError("r1"), 404,
         {"detail": "this run has no provisioning sheet"}),
        ("GET", "/runs/r1/snapshots", None, "get_snapshots", RunNotFoundError("r1"), 404,
         {"detail": "this run has no provisioning sheet"}),
        ("POST", "/runs/r1/trust/retrust", {"kind": "ssh", "host": "10.0.0.1", "port": 22, "fingerprint": "SHA256:a"},
         "retrust_device", DevicePinNotFoundError("no pin"), 404, {"detail": "no pin"}),
        ("POST", "/runs/r1/trust/retrust", {"kind": "ssh", "host": "10.0.0.1", "port": 22, "fingerprint": "SHA256:a"},
         "retrust_device", StepPreconditionError("mismatch"), 409, {"detail": "mismatch"}),
        ("POST", "/runs/r1/trust/retrust", {"kind": "ssh", "host": "10.0.0.1", "port": 22, "fingerprint": "SHA256:a"},
         "retrust_device", DeviceError("array unreachable"), 500, "Internal Server Error"),
        ("GET", "/runs/r1/events", None, "get_run", RunNotFoundError("r1"), 404, {"detail": "run not found"}),
        ("GET", "/runs/r1/events", None, "list_events", StoredCredentialsUnreadableError("key missing"), 409,
         {"detail": "key missing"}),
        ("GET", "/runs/r1/events", None, "list_events", DeviceError("array unreachable"), 500, "Internal Server Error"),
        ("POST", "/runs/r1/console", {"command": "showsys", "target": "array"}, "console.run",
         StepPreconditionError("no credential"), 409, {"detail": "no credential"}),
        ("POST", "/runs/r1/console", {"command": "showsys", "target": "array"}, "console.run",
         RunBusyError("r1"), 500, "Internal Server Error"),
        ("POST", "/runs/r1/console", {"command": "showsys", "target": "array"}, "console.run",
         ApprovalError("approval spent"), 500, "Internal Server Error"),
        ("POST", "/runs/r1/console", {"command": "showsys", "target": "array"}, "console.run",
         DeviceError("array unreachable"), 500, "Internal Server Error"),
        ("POST", "/runs/r1/console", {"command": "showsys", "target": "array"}, "get_run",
         RunNotFoundError("r1"), 404, {"detail": "run not found"}),
    )
    for method, path, payload, target, exc, status, body in service_cases:
        client = TestClient(create_app(_mock_service_failing(target, exc)), raise_server_exceptions=False)
        resp = client.request(method, path, json=payload) if payload is not None else client.request(method, path)
        assert (resp.status_code, _response_body(resp)) == (status, body), (path, type(exc).__name__)

    # Sheets router: bad base64 -> 422
    sheets_client = TestClient(create_app(_mock_service_failing("get_run", RunNotFoundError("r1"))),
                               raise_server_exceptions=False)
    bad_b64 = sheets_client.post("/init-sheet/upload", json={"content_b64": "!!!not-base64!!!"})
    assert (bad_b64.status_code, _response_body(bad_b64)) == (422, {"detail": "Upload was not valid base64"})

    # Prereqs router: unhandled DeviceError -> 500
    monkeypatch.setattr(prereqs_mod, "rules_for", lambda _region: (_ for _ in ()).throw(DeviceError("offline")))
    prereq_resp = sheets_client.get("/prereqs/firewall")
    assert (prereq_resp.status_code, _response_body(prereq_resp)) == (500, "Internal Server Error")

    # System router: PermissionError -> 403; RuntimeError / DeviceError / ApprovalError -> 500 JSON detail
    for exc, status, body in (
        (PermissionError("admin required"), 403, {"detail": "admin required"}),
        (DeviceError("clock unreachable"), 500, {"detail": "clock unreachable"}),
        (ApprovalError("approval spent"), 500, {"detail": "approval spent"}),
    ):
        async def _sync_fail(_url=None, _exc=exc):
            raise _exc
        monkeypatch.setattr(platform_clients, "sync_clock", _sync_fail)
        sys_resp = sheets_client.post("/system/clock/sync")
        assert (sys_resp.status_code, _response_body(sys_resp)) == (status, body)



def test_the_init_only_profile_reads_only_the_initialisation_tab_as_before(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ALLETRA_PROFILE", "init-only")
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    client = TestClient(create_app(OnboardingService(Settings(), store, InMemoryEventBus())))
    monkeypatch.delenv("ALLETRA_PROFILE")
    full_template = client.get("/init-sheet/template").content
    monkeypatch.setenv("ALLETRA_PROFILE", "init-only")
    bad_volume = {**_COMPLETE_PROV, "volumes": [{"name": "zz_bad+", "size_gib": "1"}]}
    up = client.post("/init-sheet/upload", json={"content_b64": _fill_template(full_template, _COMPLETE_MAIN, bad_volume)})
    assert up.status_code == 200 and up.json()["problems"] == [] and up.json()["targets"] == {}
    token = up.json()["token"]
    assert store.pending_sheet_workbook(token) is None
    run = client.post("/runs/from-sheet", json={"token": token, "mode": "FULL_ONBOARDING"})
    assert run.status_code == 200, run.text
    assert store.get_provisioning_intent(run.json()["run"]["run_id"]) is None


def test_verify_and_asbuilt_use_the_sheets_array_credential(tmp_path, monkeypatch):
    """SPEC-008 R2/R3 through the API: a run minted from a complete sheet holds the Provisioning tab's
    array admin; Verify with `{}` uses it (the fake verify_fn sees the sheet's user/password) and
    GET /runs/{id} names the account without the password."""
    monkeypatch.chdir(tmp_path)
    seen: list[tuple[str, str]] = []
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(
        Settings(), store, InMemoryEventBus(),
        verify_fn=lambda item, u, p: (seen.append((u, p)), VerificationReport(reachable=True))[1],
    )
    client = TestClient(create_app(service))
    token = _upload_complete(client)
    run_id = client.post("/runs/from-sheet", json={"token": token, "mode": "PROVISION_ONLY"}).json()["run"]["run_id"]

    detail = client.get(f"/runs/{run_id}").json()
    assert detail["array_credential"]["available"] is True
    assert detail["array_credential"]["source"] == "provisioning"
    assert detail["array_credential"]["username"] == "3paradm"
    assert detail["array_credential"]["host"] == "10.64.154.225"
    assert "arraypw" not in client.get(f"/runs/{run_id}").text

    assert client.post(f"/runs/{run_id}/verify", json={}).status_code == 200
    assert seen == [("3paradm", "arraypw")]
    # an explicit pair overrides
    client.post(f"/runs/{run_id}/verify", json={"username": "other", "password": "rotated"})
    assert seen[-1] == ("other", "rotated")
    # the credential is in no event
    events = client.get(f"/runs/{run_id}/events").text
    assert "arraypw" not in events and "rotated" not in events


# ------------------------------------------------------------------ BL-52: the server checks the approval

def _wait_for(client, rid: str, event_types: tuple[str, ...], after: int) -> dict:
    import time

    for _ in range(500):
        events = client.get(f"/runs/{rid}/events").json()["events"]
        hits = [e for e in events[after:] if e["event_type"] in (*event_types, "step.crashed")]
        if hits:
            assert hits[-1]["event_type"] != "step.crashed", hits[-1]["message"]
            return hits[-1]
        time.sleep(0.01)
    raise AssertionError(f"no {'/'.join(event_types)} event")


def _approval_run(tmp_path, *, replication: bool = False):
    from alletra_onboard.domain.discovery import DiscoveryReport
    from alletra_onboard.domain.models import RunMode
    from alletra_onboard.domain.provisioning import ProvisioningIntent
    from alletra_onboard.domain.replication import ProtectionRequest, ReplicationIntent
    from alletra_onboard.domain.shared import EndpointCreds

    def creds(host):
        return EndpointCreds(host=host, username="u", password=SecretStr("p"))

    intent = ProvisioningIntent.from_simple(host_set_name="HS", array=creds("a"), vcenter=creds("vc"),
                                            switch_f1=creds("sw1"), switch_f2=creds("sw2"),
                                            name_prefix="V", size_gib=10, count=1)
    if replication:
        intent.replication = ReplicationIntent(peer=creds("b"), failover_test=False,
                                               protections=[ProtectionRequest(vvset="HS", peer_cpg="SSD_r6")])
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    item = ArrayWorkItem.model_validate(_work_item_payload())
    run = service.create_run(item, mode=RunMode.REPLICATE if replication else RunMode.PROVISION_ONLY,
                             provisioning_intent=intent)
    service.discovery_zoning.discovery[run.run_id] = DiscoveryReport()
    return service, run.run_id


def test_storage_apply_needs_the_plan_id_the_operator_ticked(tmp_path, monkeypatch):
    # The tick was only on the screen: any local caller could POST /storage/apply for a plan nobody
    # ticked. The body now names the plan; the server refuses without it and refuses a stale one.
    from alletra_onboard.application.provisioning import apply as storage_apply
    from alletra_onboard.application.provisioning import storage_provision as sp
    from alletra_onboard.domain.provisioning import (
        PlannedAction,
        ProvisioningPlan,
        ProvisioningResult,
    )

    monkeypatch.setattr(sp, "build_plan", lambda i, d, **kw: ProvisioningPlan(actions=[PlannedAction(kind="host", name="esx1", description="d")]))
    applied: list = []
    def fake_storage_apply(inputs, approval, **kw):
        assert approval.creds_for("storage", "A").host == "a"
        applied.append(1)
        return ProvisioningResult()

    monkeypatch.setattr(storage_apply, "apply_plan", fake_storage_apply)
    service, rid = _approval_run(tmp_path)
    with TestClient(create_app(service)) as client:
        def preview() -> str:
            after = len(client.get(f"/runs/{rid}/events").json()["events"])
            assert client.post(f"/runs/{rid}/storage/preview").status_code == 200
            return _wait_for(client, rid, ("storage.previewed",), after)["data"]["plan"]["plan_id"]

        first = preview()
        for body in (None, {}, {"approved_plan": None}, {"approved_plan": ""}):
            refused = client.post(f"/runs/{rid}/storage/apply", json=body)
            assert refused.status_code == 409 and refused.json()["detail"] == "Tick the approval for this plan first."
        second = preview()
        assert first and second and second != first
        refused = client.post(f"/runs/{rid}/storage/apply", json={"approved_plan": first})
        assert refused.status_code == 409
        assert refused.json()["detail"] == "The plan changed since it was approved. Review the new plan and tick again."
        assert applied == []

        after = len(client.get(f"/runs/{rid}/events").json()["events"])
        assert client.post(f"/runs/{rid}/storage/apply", json={"approved_plan": second}).status_code == 200
        _wait_for(client, rid, ("storage.applied",), after)
        assert applied == [1]


def test_replication_apply_needs_the_plan_id_the_operator_ticked(tmp_path, monkeypatch):
    from alletra_onboard.application.replication import apply as replication_apply
    from alletra_onboard.application.replication import plan as replication_plan
    from alletra_onboard.application.replication import read as replication_read
    from alletra_onboard.domain.replication import (
        ReplicationAction,
        ReplicationArrayView,
        ReplicationPlan,
        ReplicationReport,
        ReplicationResult,
    )

    monkeypatch.setattr(replication_read, "read_array", lambda creds, progress=None: ReplicationArrayView(host=creds.host, name=creds.host))
    monkeypatch.setattr(replication_plan, "check", lambda a, b, r: ReplicationReport(primary=a, peer=b))   # no RCIP partnership: no link gate
    monkeypatch.setattr(replication_plan, "build_plan", lambda report, r, i: ReplicationPlan(actions=[ReplicationAction(kind="group", name="HS_rcg")]))
    applied: list = []
    def fake_rep_apply(plan, prov, approval, **kw):
        assert approval.creds_for("rc_groups", "A").host == "a"
        assert approval.creds_for("rc_groups", "B").host == "b"
        applied.append(plan.plan_id)
        return ReplicationResult(groups_created=["HS_rcg"])

    monkeypatch.setattr(replication_apply, "apply_plan", fake_rep_apply)
    service, rid = _approval_run(tmp_path, replication=True)
    with TestClient(create_app(service)) as client:
        def preview() -> str:
            after = len(client.get(f"/runs/{rid}/events").json()["events"])
            assert client.post(f"/runs/{rid}/replication/preview").status_code == 200
            return _wait_for(client, rid, ("replication.previewed",), after)["data"]["plan"]["plan_id"]

        first = preview()
        for body in (None, {"accept_latency": True}, {"approved_plan": ""}):
            refused = client.post(f"/runs/{rid}/replication/apply", json=body)
            assert refused.status_code == 409 and refused.json()["detail"] == "Tick the approval for this plan first."
        second = preview()
        assert first and second and second != first
        refused = client.post(f"/runs/{rid}/replication/apply", json={"approved_plan": first})
        assert refused.status_code == 409
        assert refused.json()["detail"] == "The plan changed since it was approved. Review the new plan and tick again."
        assert applied == []

        after = len(client.get(f"/runs/{rid}/events").json()["events"])
        assert client.post(f"/runs/{rid}/replication/apply", json={"approved_plan": second}).status_code == 200
        _wait_for(client, rid, ("replication.applied",), after)
        assert applied == [second]
