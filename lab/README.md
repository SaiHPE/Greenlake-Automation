# Lab scripts

Scripts that drive the app against the real lab arrays, run on a lab jump box after
`scripts/push_jumpbox_test.sh` (README, *A live run on a jump box*). They are not part of the app,
the release zip or the lint gate. Each one says at the top what it reads and what it changes.

**Before running one:** book the lab, read its header, and put the lab passwords in the jump box's
`.env` once (`LAB_ARRAY_PW`, `LAB_DEFAULT_PW`; read by `rc_failover_lab.lab_secret()`). Never write a
password into a script. Results go to `~\Downloads\<name>.zip`.

**Writing a new one:** copy the closest script below, import `rc_failover_lab as fl` for SSH, the
app API and saving evidence, keep it free of prompts, give everything it creates a `zz_<initials>_`
prefix, and remove all of it at the end.

| Script | What it checks | Changes the arrays? |
|---|---|---|
| `ui_live_lab.py` | Every page of the app at 1366 and 1080 wide, on a run with real discovery, zoning, plans, verify and as-built (BL-43) | No |
| `ui_provision_lab.py` | The Provision storage page creates objects through its own buttons, then removes them (BL-43) | Yes, `zz_ui_*` on D22U27, removed at the end |
| `rc_peer_ready.py` | Whether the peer array can be the replication partner of D22U27 | No |
| `rcip_pair_capture.py` | The Alletra MP 10.132.30.121 + Primera 10.132.30.28 pair before replication setup: planned RCIP ports today (role, link, hosts on them), licences, Remote Copy state, CLI help of the setup commands (BL-41) | No |
| `rcip_setup_lab.py` | `setup`: RCIP addresses on the Alletra (0:4:4/1:4:4), ping, startrcopy, a target each way, links Up; `undo`: reverses every change from its journal; `undo-setup`: reverses only the partnership, so the tool can set it up again (BL-41) | Yes, both arrays; `undo` restores them |
| `rcip_pair_lab.py` | The app's Replication steps (preview, link check, apply, verify, failover test, as-built) on the Alletra MP -> Primera pair, then its removal sets (BL-41) | Yes, `zz_rc_*` on both arrays, removed at the end |
| `rcip_tool_lab.py` | From a pair with no partnership (after `rcip_setup_lab.py undo-setup`): the tool sets up the RCIP ports and the partnership from the Replication network tab, then groups, link check, verify, failover test, as-built; pastes the run's merged removal set and checks the pair is back at the start (BL-41) | Yes, both arrays; removed at the end |
| `rc_find_fabric.py` | Which vCenter and FC switches a lab host uses | No |
| `rc_console_lab.py` | The command console and its refusal of write commands (SPEC-019) | No |
| `rc_link_lab.py` | The replication link check between the pair (SPEC-020) | No |
| `rc_link_solo_lab.py` | The link check's real output on one array, server and client on its two RCIP ports | No |
| `rc_preset_lab.py` | The "Provision, then replicate" preset end to end with a real host | Yes, `zz_rc_*` on both arrays, removed at the end |
| `rc_async_lab.py` | Periodic (async) replication through the app's own modules | Yes, see its header |
| `rc_failover_lab.py` | The failover test (SPEC-017); also the shared helper module every script imports | Yes, the test group |
| `rc_async_failover_lab.py` | The failover test in periodic mode | Yes, see its header |
| `rc_option1.py`, `rc_rebuild.py`, `rc_sheet.py` | Helpers the failover scripts call: pause and restore the lab's Sync groups, compose the test sheet | Yes, run by the scripts above |
| `spec014.ps1` / `spec014.cmd` | Agentless host discovery (SPEC-014) from one workbook | No |

`archive/` keeps one-off explorations from the replication work (BL-20). They are not maintained.
