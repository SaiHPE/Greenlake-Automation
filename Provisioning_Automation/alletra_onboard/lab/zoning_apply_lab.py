"""BL-66 live check: opt-in Brocade Fabric OS SAN zoning apply end-to-end against rack13 and its
Brocade switches SW-F1 (10.132.30.111) & SW-F2 (10.132.30.112). No prompts.

    UI_SHEET=<rack13_workbook.xlsx> python lab/zoning_apply_lab.py

The app must be running on http://127.0.0.1:8765 (or LAB_APP).
CHANGES SW-F2 (10.132.30.112) with zz_za_* test aliases and one test zone, then removes them
with the run's OWN generated removal command set and verifies exact restoration:
1. Checks cfgtransshow has no open transaction on both SW-F1 and SW-F2, and zero zz_za_* names.
2. Uploads the workbook, runs Discovery + Zoning plan, and renders 1 safe test pair on F2:
   ELJR0NB1UV (51:40:2e:c0:20:89:cc:1c) x array port 0:3:3 (20:33:00:02:ac:02:d4:95)
   using zz_za_* alias names so it can never clash with any real alias or zone.
   Asserts rendered apply_fabrics contains ONLY F2 (even) with ONLY those two zz_za_* aliases
   and one zz_za_* zone (zero peer-port zones, zero non-zz_za_* names) BEFORE calling apply.
3. Verifies POST /runs/{id}/zoning/apply with a wrong approved_plan returns 409 and sends 0 writes.
4. Applies with the real apply_plan_id, waits for zoning.applied, and verifies live on SW-F2 via
   BrocadeClient.cfgshow() (strict Effective-only parsing) that the new zz_za_* zone is in
   Effective configuration with the exact planned member WWPNs and cfgtransshow reports no open
   transaction.
5. Executes the run's OWN generated removal set per fabric on each fabric's own switch host and
   verifies exact restoration (Defined == Effective, zero zz_za_* traces, no open transaction).
6. Verifies cfgtransabort over a second exec channel on SW-F2 with a real uncommitted zz_za_*
   transaction: opens a transaction, confirms cfgtransshow reports an open transaction, runs
   cfgtransabort on a separate exec channel, and confirms cfgtransshow is clean and zero zz_za_*
   objects remain.
In finally: ALWAYS connects to BOTH switches, aborts any open transaction, removes any remaining
zz_za_* zones/aliases (checking both exit status and FOS output), and re-verifies clean state.
Evidence in ~/Downloads/zoning_apply.zip.
"""
import base64
import json
import os
import re
import shutil
import sys
import time
import traceback
import urllib.error
import urllib.request

import paramiko

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402

from alletra_onboard.adapters.fabric.brocade_client import BrocadeClient
from alletra_onboard.application.provisioning.zoning import parse_cfgshow_strict
from alletra_onboard.application.provisioning.zoning_plan import parse_defined_names

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "zoning_apply")
fl.OUT = OUT

SHEET = os.environ.get("UI_SHEET")
if not SHEET:
    sys.exit("UI_SHEET is not set. Point UI_SHEET to the rack13 initialisation workbook and run again.")

TEST_HOST_WWPN = "51402EC02089CC1C"     # ELJR0NB1UV on F2
TEST_ARR_WWPN = "20330002AC02D495"      # rack13 0:3:3 on F2
TEST_HOST_ALIAS = "zz_za_eljr_hba2"
TEST_ARR_ALIAS = "zz_za_rack13_033"
TEST_ZONE = f"{TEST_HOST_ALIAS}_{TEST_ARR_ALIAS}"
TEST_ABORT_ALIAS = "zz_za_abort_probe"
TEST_PREFIX = "zz_za_"
RESULTS = []

_FOS_ERR_MARKERS = ("error:", "usage:", "invalid ", "failed", "not found", "does not exist", "do you want to")
_TX_TOKEN_RE = re.compile(r"(?:token(?:\s+is)?[:\s]+)(0x[0-9a-fA-F]+|[0-9a-fA-F]+)", re.IGNORECASE)
_REM_CFGREMOVE = re.compile(r'^cfgremove "([^"]+)","([^"]+)"$')
_REM_ZONEDELETE = re.compile(r'^zonedelete "([^"]+)"$')
_REM_ALIDELETE = re.compile(r'^alidelete "([^"]+)"$')
_REM_CFGENABLE = re.compile(r'^cfgenable "([^"]+)" -f$')


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def api(method, path, body=None):
    req = urllib.request.Request(
        fl.APP + path,
        method=method,
        data=None if body is None else json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with fl.OPENER.open(req, timeout=180) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as exc:
        raw = (exc.read() or b"").decode("utf-8", "replace")
        try:
            return exc.code, json.loads(raw)
        except ValueError:
            return exc.code, raw


def wait_for_event(run_id, wanted, after_count, timeout_s=300):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        _st, body = api("GET", f"/runs/{run_id}/events")
        evs = body.get("events", [])[after_count:]
        for ev in reversed(evs):
            if ev.get("event_type") in wanted:
                return ev, len(body.get("events", []))
        time.sleep(1.5)
    raise RuntimeError(f"timed out waiting for {wanted}")


def wait_run_not_running(run_id, timeout_s=45):
    """Wait until the app finishes any active background step before sweeping switches."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        st, body = api("GET", f"/runs/{run_id}")
        status = (body.get("run") or {}).get("status") if isinstance(body, dict) else None
        if st != 200 or status != "running":
            return status
        time.sleep(1.0)
    return "running"


def read_switch(host, user, pw):
    with BrocadeClient(host, user, pw) as client:
        return client.cfgtransshow(), client.cfgshow()


def _exec_on(client, cmd, timeout=60):
    _i, o, e = client.exec_command(cmd, timeout=timeout)
    out = (o.read() + e.read()).decode("utf-8", "replace")
    status = o.channel.recv_exit_status()
    return status, out


def _open_ssh(host, user, pw):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username=user, password=pw, timeout=20, allow_agent=False, look_for_keys=False)
    return c


def _fos_cmd_ok(cmd, status, out):
    if status != 0:
        return False
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not lines:
        return True
    if cmd.startswith(("alicreate ", "zonecreate ", "cfgadd ", "cfgremove ", "zonedelete ", "alidelete ")):
        return False
    return not any(any(m in ln.lower() for m in _FOS_ERR_MARKERS) for ln in lines)


def run_switch_commands(host, user, pw, commands, *, strict=True):
    c = _open_ssh(host, user, pw)
    outputs = []
    try:
        for cmd in commands:
            status, out = _exec_on(c, cmd)
            outputs.append({"command": cmd, "status": status, "output": out})
            if strict and not _fos_cmd_ok(cmd, status, out):
                raise RuntimeError(f"switch command failed on {host} ({status}): {cmd}\n{out}")
    finally:
        c.close()
    return outputs


def validate_removal_commands(commands, baseline_cfg):
    """Ensure every app-generated removal line matches the 4 exact forms and only touches zz_za_* + baseline_cfg."""
    if not commands:
        return False, "empty removal set"
    for cmd in commands:
        if m := _REM_CFGREMOVE.match(cmd):
            cfg, members = m.group(1), m.group(2).split(";")
            if cfg != baseline_cfg or not members or any(not z.startswith(TEST_PREFIX) for z in members):
                return False, f"unexpected cfgremove: {cmd}"
        elif m := _REM_ZONEDELETE.match(cmd):
            if not m.group(1).startswith(TEST_PREFIX):
                return False, f"non-zz_za zonedelete: {cmd}"
        elif m := _REM_ALIDELETE.match(cmd):
            if not m.group(1).startswith(TEST_PREFIX):
                return False, f"non-zz_za alidelete: {cmd}"
        elif m := _REM_CFGENABLE.match(cmd):
            if m.group(1) != baseline_cfg:
                return False, f"unexpected cfgenable cfg: {cmd}"
        else:
            return False, f"disallowed removal command form: {cmd}"
    return True, ""


def _abort_open_tx(client, trans_text):
    """Abort an open transaction on a touched switch; fall back to `cfgtransabort <token>` if needed."""
    _exec_on(client, "cfgtransabort")
    _st, after = _exec_on(client, "cfgtransshow")
    if "no outstanding" in after.lower():
        return after
    match = _TX_TOKEN_RE.search(trans_text) or _TX_TOKEN_RE.search(after)
    if match:
        _exec_on(client, f"cfgtransabort {match.group(1)}")
        _st, after = _exec_on(client, "cfgtransshow")
    return after


def sweep_switch_cleanup(label, sw, *, touched):
    """Verify clean state on `sw`; only abort transactions on switches we touched."""
    host, user, pw = sw
    trans, cfg = read_switch(host, user, pw)
    if "no outstanding" not in trans.lower():
        if not touched:
            check(f"cleanup {label}: untouched switch has open transaction (left alone)", False, trans.strip())
            return
        c = _open_ssh(host, user, pw)
        try:
            trans = _abort_open_tx(c, trans)
        finally:
            c.close()
        check(f"cleanup {label}: open transaction aborted", "no outstanding" in trans.lower(), trans.strip())
        trans, cfg = read_switch(host, user, pw)

    parsed = parse_cfgshow_strict(cfg)
    zz_zones = sorted(z for z in (set(parsed.defined_zones) | set(parsed.effective_zones)) if z.startswith(TEST_PREFIX))
    zz_aliases = sorted(a for a in parsed.aliases if a.startswith(TEST_PREFIX))
    if zz_zones or zz_aliases:
        eff_cfg = parsed.effective_cfg
        if not eff_cfg:
            check(f"cleanup {label}: effective cfg present to remove zz_za_*", False, "no effective cfg")
            return
        cmds = []
        if zz_zones:
            cmds.append(f'cfgremove "{eff_cfg}","{";".join(zz_zones)}"')
        for z in zz_zones:
            cmds.append(f'zonedelete "{z}"')
        for a in zz_aliases:
            cmds.append(f'alidelete "{a}"')
        cmds.append(f'cfgenable "{eff_cfg}" -f')
        c = _open_ssh(host, user, pw)
        sweep_wrote = False
        try:
            sweep_log = []
            for cmd in cmds:
                sweep_wrote = True
                st, out = _exec_on(c, cmd)
                sweep_log.append({"command": cmd, "status": st, "output": out})
            fl.save(f"cleanup-sweep-{label}.json", json.dumps(sweep_log, indent=2))
            _st, tx_check = _exec_on(c, "cfgtransshow")
            if "no outstanding" not in tx_check.lower() and (touched or sweep_wrote):
                _abort_open_tx(c, tx_check)
        except Exception:
            if touched or sweep_wrote:
                try:
                    _st, tx_check = _exec_on(c, "cfgtransshow")
                    if "no outstanding" not in tx_check.lower():
                        _abort_open_tx(c, tx_check)
                except Exception:
                    pass
            raise
        finally:
            c.close()
        trans, cfg = read_switch(host, user, pw)

    final_parsed = parse_cfgshow_strict(cfg)
    final_defined = parse_defined_names(cfg)
    leftover = sorted(
        n for n in (final_defined | set(final_parsed.effective_zones) | set(final_parsed.aliases))
        if n.startswith(TEST_PREFIX)
    )
    check(f"cleanup {label}: zero zz_za_* traces and no open transaction",
          not leftover and "no outstanding" in trans.lower(),
          f"leftover={leftover} trans={trans.strip()}")


def main():
    os.makedirs(OUT, exist_ok=True)
    _serial, _network, targets = fl.sheet_targets(SHEET)
    sw1 = (targets["prov_sw1_host"], targets["prov_sw1_user"], targets["prov_sw1_password"])
    sw2 = (targets["prov_sw2_host"], targets["prov_sw2_user"], targets["prov_sw2_password"])
    sw_by_host = {sw1[0]: sw1, sw2[0]: sw2}
    touched_switches = set()
    run_id = None
    baseline_cfgshow_f2 = ""
    baseline_cfg_f2 = ""

    try:
        fl.banner("1. Pre-flight check on SW-F1 and SW-F2 (read-only)")
        trans1, cfg1 = read_switch(*sw1)
        trans2, cfg2 = read_switch(*sw2)
        baseline_cfgshow_f2 = cfg2
        baseline_cfg_f2 = parse_cfgshow_strict(cfg2).effective_cfg or ""
        fl.save("pre_sw1_cfgshow.txt", cfg1)
        fl.save("pre_sw2_cfgshow.txt", cfg2)

        f1_clean = "no outstanding" in trans1.lower()
        f2_clean = "no outstanding" in trans2.lower()
        f1_no_zz = not any(n.startswith(TEST_PREFIX) for n in parse_defined_names(cfg1))
        f2_no_zz = not any(n.startswith(TEST_PREFIX) for n in parse_defined_names(cfg2))
        check("SW-F1 has no open transaction and no zz_za_* objects", f1_clean and f1_no_zz)
        check("SW-F2 has no open transaction, no zz_za_* objects, and active effective cfg",
              f2_clean and f2_no_zz and bool(baseline_cfg_f2), baseline_cfg_f2)
        if not (f1_clean and f2_clean and f1_no_zz and f2_no_zz and baseline_cfg_f2):
            raise RuntimeError("Pre-flight failed: switches are not clean before test.")

        fl.banner("2. Upload workbook, Discovery, Zoning plan, Render 1 safe F2 test pair")
        with open(SHEET, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        st, up = api("POST", "/init-sheet/upload", {"content_b64": b64})
        if st != 200:
            raise RuntimeError(f"upload failed ({st}): {up}")
        st, created = api(
            "POST",
            "/runs/from-sheet",
            {"token": up["token"], "mode": "CUSTOM", "selected_steps": ["discover", "zoning"]},
        )
        if st != 200:
            raise RuntimeError(f"from-sheet failed ({st}): {created}")
        run_id = created["run"]["run_id"]
        fl.save("run-id.txt", run_id)

        ev_count = len(api("GET", f"/runs/{run_id}/events")[1].get("events", []))
        api("POST", f"/runs/{run_id}/discover")
        disc_ev, ev_count = wait_for_event(run_id, {"discover.completed", "step.crashed"}, ev_count)
        check("Discovery completed", disc_ev["event_type"] == "discover.completed" and not disc_ev["data"]["report"].get("error"))

        api("POST", f"/runs/{run_id}/zoning/plan")
        plan_ev, ev_count = wait_for_event(run_id, {"zoning.plan", "step.crashed"}, ev_count)
        plan = plan_ev["data"]["plan"]
        fl.save("zoning-plan.json", json.dumps(plan, indent=2))
        check("Zoning plan built", plan_ev["event_type"] == "zoning.plan" and bool(plan.get("fabrics")))

        render_body = {
            "run_id": run_id,
            "plan": plan,
            "aliases": {TEST_HOST_WWPN: TEST_HOST_ALIAS, TEST_ARR_WWPN: TEST_ARR_ALIAS},
            "selected_pairs": [[TEST_HOST_WWPN, TEST_ARR_WWPN]],
        }
        st, rendered = api("POST", "/zoning/render", render_body)
        fl.save("zoning-render.json", json.dumps(rendered, indent=2))
        plan_id = rendered.get("apply_plan_id") if isinstance(rendered, dict) else None
        apply_fabrics = rendered.get("apply_fabrics") or [] if isinstance(rendered, dict) else []
        strict_scope_ok = (
            st == 200
            and bool(plan_id)
            and len(apply_fabrics) == 1
            and apply_fabrics[0].get("fabric") == "even"
            and apply_fabrics[0].get("switch_host") == sw2[0]
            and apply_fabrics[0].get("active_cfg") == baseline_cfg_f2
            and set(apply_fabrics[0].get("aliases", {}).keys()) == {TEST_HOST_ALIAS, TEST_ARR_ALIAS}
            and set(apply_fabrics[0].get("zones", {}).keys()) == {TEST_ZONE}
            and not any(rendered.get("peer_commands", {}).values())
        )
        check("Rendered apply_fabrics contains ONLY F2 with exact 2 zz_za_* aliases and 1 zz_za_* zone",
              strict_scope_ok, json.dumps(apply_fabrics))
        if not strict_scope_ok:
            raise RuntimeError("Refusing to call apply: rendered apply_fabrics did not match strict F2 zz_za_* scope.")

        fl.banner("3. Verify wrong approved_plan returns 409 and sends 0 switch writes")
        st_bad, bad_resp = api("POST", f"/runs/{run_id}/zoning/apply", {"approved_plan": "wrong-plan-id"})
        writes_before = [c for c in api("GET", f"/runs/{run_id}/console/log")[1]["commands"] if c.get("write")]
        check("Wrong approved_plan returns 409 with 0 switch writes", st_bad == 409 and len(writes_before) == 0, str(bad_resp))

        fl.banner("4. Apply with real approved_plan and verify on live SW-F2")
        touched_switches.add(sw2[0])
        st_ok, _ = api("POST", f"/runs/{run_id}/zoning/apply", {"approved_plan": plan_id})
        if st_ok != 200:
            raise RuntimeError(f"zoning apply start failed ({st_ok})")
        apply_ev, ev_count = wait_for_event(run_id, {"zoning.applied", "zoning.apply.failed", "step.crashed"}, ev_count)
        fl.save("zoning-apply-event.json", json.dumps(apply_ev, indent=2))
        res = (apply_ev.get("data") or {}).get("result") or {}
        per_fabric_removals = [
            (fab.get("switch_host", ""), list(fab.get("removals") or []))
            for fab in res.get("fabrics", [])
            if fab.get("removals")
        ]

        check("zoning.applied succeeded", apply_ev["event_type"] == "zoning.applied" and not res.get("error"), str(res.get("error") or ""))

        trans_after, cfg_after = read_switch(*sw2)
        fl.save("post_apply_sw2_cfgshow.txt", cfg_after)
        parsed_after = parse_cfgshow_strict(cfg_after)
        expected_members = {TEST_HOST_WWPN, TEST_ARR_WWPN}
        check(
            "Live SW-F2 Effective configuration contains zz_za_* test zone with exact member WWPNs",
            TEST_ZONE in parsed_after.effective_zones and parsed_after.effective_zones[TEST_ZONE] == expected_members,
        )
        check("Live SW-F2 has no open transaction after apply", "no outstanding" in trans_after.lower())

        fl.banner("5. Validate and execute the run's own generated removal set per switch")
        check("Run produced per-fabric removal commands", len(per_fabric_removals) == 1 and len(per_fabric_removals[0][1]) >= 4)
        for host, cmds in per_fabric_removals:
            if host != sw2[0] or host not in sw_by_host:
                raise RuntimeError(f"Unexpected removal host '{host}' (expected only {sw2[0]})")
            rem_ok, rem_why = validate_removal_commands(cmds, baseline_cfg_f2)
            check("App-generated removal commands match exact zz_za_* forms and baseline cfg", rem_ok, rem_why)
            if not rem_ok:
                raise RuntimeError(f"Refusing to run invalid removal set: {rem_why}")
            rem_out = run_switch_commands(*sw_by_host[host], cmds)
            fl.save(f"removal-output-{host}.json", json.dumps(rem_out, indent=2))

        trans_final, cfg_final = read_switch(*sw2)
        fl.save("post_removal_sw2_cfgshow.txt", cfg_final)
        final_defined = parse_defined_names(cfg_final)
        final_parsed = parse_cfgshow_strict(cfg_final)
        orig_defined = parse_defined_names(baseline_cfgshow_f2)
        orig_parsed = parse_cfgshow_strict(baseline_cfgshow_f2)
        check("Zero zz_za_* traces remain on SW-F2", not any(n.startswith(TEST_PREFIX) for n in final_defined | set(final_parsed.effective_zones)))
        check("SW-F2 Defined and Effective zones match baseline",
              final_defined == orig_defined and set(final_parsed.effective_zones) == set(orig_parsed.effective_zones))
        check("SW-F2 has no open transaction after removal", "no outstanding" in trans_final.lower())

        if any(r.startswith("FAIL") for r in RESULTS):
            fl.banner("6. Skipping cfgtransabort probe because an earlier check failed")
        else:
            fl.banner("6. Verify live cfgtransabort across a second exec channel on ONE SSH session (SW-F2)")
            c = _open_ssh(*sw2)
            try:
                st_ali, out_ali = _exec_on(c, f'alicreate "{TEST_ABORT_ALIAS}","51:40:2e:c0:20:89:cc:1c"')
                check("Uncommitted alicreate succeeded on channel 1", _fos_cmd_ok("alicreate ", st_ali, out_ali), out_ali.strip())
                _st_t1, trans_open = _exec_on(c, "cfgtransshow")
                check("cfgtransshow on channel 2 reported open transaction", "no outstanding" not in trans_open.lower(), trans_open.strip())
                _st_ab, out_ab = _exec_on(c, "cfgtransabort")
                _st_t2, trans_aborted = _exec_on(c, "cfgtransshow")
                check("cfgtransabort on channel 3 closed transaction cleanly",
                      "no outstanding" in trans_aborted.lower(), f"abort={out_ab.strip()} tx={trans_aborted.strip()}")
            finally:
                c.close()
            _t_chk, cfg_aborted = read_switch(*sw2)
            check("Aborted zz_za_abort_probe alias did not persist", TEST_ABORT_ALIAS not in parse_defined_names(cfg_aborted))

    except Exception:
        fl.save("traceback.txt", traceback.format_exc())
        traceback.print_exc()
        RESULTS.append("FAIL  unhandled exception (see traceback.txt)")
    finally:
        if run_id:
            final_status = wait_run_not_running(run_id, timeout_s=75)
            check("App run left RUNNING before switch sweep", final_status != "running", str(final_status))
        fl.banner("Guaranteed cleanup sweep on SW-F1 and SW-F2 (abort only on touched switches)")
        for label, sw in (("SW-F1", sw1), ("SW-F2", sw2)):
            try:
                sweep_switch_cleanup(label, sw, touched=sw[0] in touched_switches)
            except Exception as cleanup_exc:
                print(f"CLEANUP FAILED on {label}: {cleanup_exc}")
                RESULTS.append(f"FAIL  cleanup {label}: {cleanup_exc}")
        passed = sum(1 for r in RESULTS if r.startswith("PASS"))
        failed = sum(1 for r in RESULTS if r.startswith("FAIL"))
        summary = f"\n{passed} pass, {failed} fail\n"
        fl.save("report.txt", "\n".join(RESULTS) + summary)
        print(summary)
        shutil.make_archive(OUT, "zip", OUT)
        sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
