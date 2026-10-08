# SPEC-019 — Console: the live command log, and a read-only prompt

**Status:** APPROVED 2026-10-08 (operator: "this would work"; no full shell) — not implemented
**ADRs:** [0001](../adr/0001-post-init-verification-via-ssh-cli.md) (the prompt runs the read-only
client and nothing else) · [0013](../adr/0013-one-array-credential-per-run.md) (the run's credential,
never typed) · [0012](../adr/0012-no-switch-writes-the-tool-emits-a-command-set.md) unaffected
**Owner:** `adapters/array/cli_client.py` + `wsapi_client.py` (emit hook), `application/runs/coordinator.py`
(`command.executed` event + `command_log` artifact), `api/app.py` (`POST /runs/{id}/console`),
`frontend/src/ui/ConsolePane.tsx` (xterm.js), `application/documents/asbuilt.py` (evidence appendix)

## 1. Problem

Every step says what it did in our words ("Reading 10.64.122.99: system, RCIP ports…"). The engineer
sees neither the command that ran nor the array's own output, so "read-only" is a claim rather than
something visible, the evidence we keep asking the operator to paste back is thrown away, and a quick
`showvlun -a -host X` needs PuTTY and a second password prompt.

## 2. Requirements

**R1 — Every command the tool runs is an event.** The SSH client (`ArrayCliClient.run`) and the WSAPI
client emit `command.executed` with: target (array name/host, or vCenter/switch), transport (`ssh` /
`wsapi` / `vcenter` / `fos`), the command or `METHOD /path`, started-at, duration, result (exit/HTTP
status or the array's error), and the output (text; WSAPI bodies as JSON). Output is capped at 64 KB
per command with a `… (N KB truncated)` tail. **Passwords never appear**: WSAPI login bodies and any
value equal to a credential the run holds are redacted before the event is built.

**R2 — Durable and in the as-built.** Events are appended to the run's `command_log` artifact
(ordered, append-only). The as-built gains an appendix *Commands run on the array* (SSH + WSAPI writes,
not the full output) so the customer document shows what touched the array.

**R3 — The read-only prompt.** `POST /runs/{id}/console {"command": "showvlun -a -host ESX1"}` runs
the command through the run's `ArrayCliClient` (ADR 0001 allowlist, same metacharacter refusal) with
the run's array credential, and emits R1's event like any tool read. A command not on the allowlist
is refused with: *"The console runs the tool's read-only commands (show…, checkhealth). Changes go
through a plan you approve, or through your own SSH session — Open terminal."* Nothing on the write
client (ADR 0015) is ever reachable from here. A `--peer` prefix (or a target selector in the UI) runs
the same read on the Replication tab's peer array when the run has one.

**R4 — The pane.** A collapsible console at the bottom of every step, built on `@xterm/xterm` (+ fit,
search). Lines: `HH:MM:SS  <target> (<transport>)  <command>  <duration>  <result>` then the output,
dimmed. A text input below with history (↑/↓), *Run*, and a target selector (A / peer). Buttons:
*Copy*, *Download .txt* (the whole log), *Open terminal* (R5). Live via the existing SSE stream;
history reloaded from the artifact on refresh.

**R5 — Open terminal.** Launches the system terminal with `ssh <user>@<array>` prefilled, like the
Discovery Tool launcher — no password is passed. For everything the prompt refuses.

**R6 — Off by default in the runner's assertions,** on for evidence: `session.ps1` downloads the log
per run into the session folder (replaces the hand-pasted `show*` scripts).

## 3. Non-goals

A general shell or PTY to the array (webssh / wetty / ttyd style) — rejected with the design above;
any command outside the read allowlist; switch or vCenter prompts (reads there stay the tool's own);
line editing inside xterm (the input field is a plain field).

## 4. Verification

Unit: the SSH client emits one event per `run()` with the command, duration and capped output; the
WSAPI client emits per call with the body redacted; the console route refuses `removevv`, `setrcopygroup`,
`createvv`, anything with `;`/`|`, and accepts `showvv -showcols Name,VSize_MB`; the artifact round-trips
and reloads in order. Live: open the pane during a Discovery on labrat and read the real `showport` text;
type `showrcopy groups zz_rc_vvs_rcg` on the peer target.

## 5. Size

Emit hooks + redaction (~120 lines), route + artifact (~80), xterm pane (~250), as-built appendix (~40),
~15 unit tests; `@xterm/xterm` + two addons in `frontend/package.json` (pure JS, bundled by Vite into
`frontend/dist`, which the exe already ships). After the first live replication apply.
