"""Read-only SSH client for the array CLI — post-init verification (see docs/adr/0001).

Logs into the initialized array with the admin account and runs an allowlist of ``show*`` commands
to read the running config. It can ONLY run those commands — the path is structurally read-only, so
verification can never mutate the array.
"""

from __future__ import annotations

import re
import time

import structlog

from alletra_onboard.adapters import command_log, device_trust
from alletra_onboard.domain.errors import ArrayCliError

try:
    import paramiko
except ImportError:  # pragma: no cover - bundled in the .exe; optional for non-SSH runs
    paramiko = None

_log = structlog.get_logger(__name__)

# The ONLY commands this client may ever run. All read-only inspection commands — anything else is
# refused. `checkhealth` only inspects + reports (it never changes the array).
ALLOWED_COMMANDS = (
    # post-init config verification
    "showsys", "shownet", "showdate", "showversion",
    # array health + inventory verification / as-built (node memory + drive cages)
    "checkhealth", "showinventory", "showpd", "shownode", "showcage",
    # provisioning / SAN-discovery preflight (read-only — see the WSAPI provisioning plan)
    "showwsapi", "showcpg", "showspace", "showvv", "showvlun",
    "showhost", "showport", "showportdev", "showrcopy", "showtarget",
    "showhostset", "showvvset",
    # replication read (SPEC-016 R1): the RCIP links with their peer addresses
    "showrctransport",
    # SPEC-026: the array's alerts (read-only). System Reporter's srstatcpu, srstatport and srstatvv left
    # on 2026-11-19 with the as-built's performance figures (the owner's decision): nothing else read them.
    "showalert",
    # snapshot schedules (SPEC-023 R3). Its help (OS 10.5.x, 10.6.0) lists -all, -window and -sortcol,
    # all of which only change what is shown: no option acts.
    "showsched",
)
# Options that make an allowed command act instead of read. The name check alone let these through.
# `showtarget -rescan` makes the peer ports rescan for targets (HPE CLI reference, showtarget). When a
# captured `help` shows another such option, add it here with a test.
_ACTION_OPTIONS: dict[str, dict[str, str]] = {
    "showtarget": {"-rescan": "it makes the peer ports rescan for targets"},
}
# Shell metacharacters that could chain or redirect a second command, and Tcl's quoting and
# substitution characters: the array CLI is Tcl-based, so `showvv [removevv -f zz]` could run removevv,
# and `showtarget "-rescan"`, `{-rescan}` or `\-rescan` could send an option the check above never saw.
# No read the tool makes uses any of them, so the whole command is refused if one appears.
_FORBIDDEN_CHARS = set(";|&`$><\n\r\"'{}[]\\")

# SPEC-020 R2: the non-show commands, on an allowlist of their own. `checkrclink` starts and stops
# a link test between two Remote Copy ports, and `controlport rcip ping` pings from one; neither changes
# configuration. Only the link check calls `run_diagnostic`; the console prompt and `run()` keep the
# read allowlist above.
_NSP = r"\d{1,2}:\d{1,2}:\d{1,2}"
_IPV4 = r"(?:\d{1,3}\.){3}\d{1,3}"
_DIAGNOSTIC_FORMS = (
    re.compile(rf"^checkrclink startserver {_NSP} {_IPV4}$"),
    re.compile(rf"^checkrclink stopserver {_NSP}$"),
    re.compile(rf"^checkrclink startclient {_NSP} {_IPV4} (?P<time>\d+)$"),
    re.compile(rf"^checkrclink stopclient {_NSP}$"),
    # SPEC-020 R2a: a plain ping between the same two RCIP ports when checkrclink prints no latency number.
    # It sends ICMP echo only and changes nothing on the array.
    re.compile(rf"^controlport rcip ping -c (?P<count>\d+) {_IPV4} {_NSP}$"),
)
DIAGNOSTIC_TIME_RANGE = (300, 172800)       # the array's documented range for <time>
DIAGNOSTIC_PING_MAX = 20


def refusal(command: str) -> str | None:
    """Why this client would refuse `command`, or None when it may run."""
    if any(ch in command for ch in _FORBIDDEN_CHARS):
        return "refused: command contains a forbidden shell metacharacter"
    parts = command.split()
    base = parts[0] if parts else ""
    if base not in ALLOWED_COMMANDS:
        return f"refused: '{base}' is not a read-only show command"
    options = {p.lower() for p in parts[1:]}
    for option, what in _ACTION_OPTIONS.get(base, {}).items():
        if option in options:
            return f"refused: '{base} {option}' is not a read: {what}"
    return None


def diagnostic_refusal(command: str) -> str | None:
    """Why `run_diagnostic` would refuse `command`: anything but a well-formed checkrclink or RCIP ping."""
    if any(ch in command for ch in _FORBIDDEN_CHARS):
        return "refused: command contains a forbidden shell metacharacter"
    for form in _DIAGNOSTIC_FORMS:
        m = form.match(command)
        if m:
            if "time" in m.groupdict():
                lo, hi = DIAGNOSTIC_TIME_RANGE
                if not lo <= int(m.group("time")) <= hi:
                    return f"refused: checkrclink time must be {lo} to {hi} seconds"
            if "count" in m.groupdict() and not 1 <= int(m.group("count")) <= DIAGNOSTIC_PING_MAX:
                return f"refused: the ping count must be 1 to {DIAGNOSTIC_PING_MAX}"
            return None
    return ("refused: only 'checkrclink startserver <N:S:P> <addr>', 'stopserver <N:S:P>', "
            "'startclient <N:S:P> <addr> <secs>', 'stopclient <N:S:P>' and "
            "'controlport rcip ping -c <count> <addr> <N:S:P>' may run here")


class ArrayCliClient:
    def __init__(
        self, host: str, username: str, password: str, port: int = 22,
        timeout: float = 15.0, exec_timeout: float = 120.0,
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout            # connect timeout
        self.exec_timeout = exec_timeout  # per-command cap (checkhealth can take ~30s)
        self._client = None

    def connect(self) -> None:
        if paramiko is None:
            raise ArrayCliError("SSH support (paramiko) is not available in this build.")
        # ADR 0026: a fresh array has no known_hosts entry, so the run trusts its host key on first contact
        # and refuses a different one before the password is sent. The Remote Copy write client, the link
        # check and the console all connect here.
        try:
            client = device_trust.open_ssh(self.host, self.port, device="array", username=self.username,
                                           password=self.password, timeout=self.timeout)
        except device_trust.DeviceTrustError as exc:
            raise ArrayCliError(str(exc)) from exc
        except paramiko.AuthenticationException as exc:
            raise ArrayCliError(
                f"Login failed for {self.username}@{self.host} — check the admin username/password "
                "(the System Credential you set in DSCC)."
            ) from exc
        except Exception as exc:
            raise ArrayCliError(
                f"Could not reach the array at {self.host}:{self.port} ({type(exc).__name__}) — check "
                "it's powered on, on this subnet, and that SSH is enabled."
            ) from exc
        self._client = client

    def run(self, command: str, timeout: float | None = None) -> str:
        if self._client is None:
            raise ArrayCliError("not connected")
        started = time.monotonic()
        try:
            text = self._run(command, timeout)
        except ArrayCliError as exc:
            command_log.record(target=self.host, transport="ssh", command=command, started=started, ok=False,
                               result=str(exc), secrets=[self.password])
            raise
        failed = text.lstrip().lower().startswith("error")
        command_log.record(target=self.host, transport="ssh", command=command, started=started, ok=not failed,
                           result=text.strip().splitlines()[0] if failed else "ok", output=text,
                           secrets=[self.password])
        return text

    def _run(self, command: str, timeout: float | None) -> str:
        why = refusal(command)
        if why:
            raise ArrayCliError(why)
        return self._exec(command, timeout)

    def _exec(self, command: str, timeout: float | None) -> str:
        if self._client is None:
            raise ArrayCliError("not connected")
        try:
            _stdin, stdout, stderr = self._client.exec_command(command, timeout=timeout or self.exec_timeout)
            out = stdout.read().decode("utf-8", "replace")
            err = stderr.read().decode("utf-8", "replace")
        except Exception as exc:
            raise ArrayCliError(f"running '{command}' failed: {type(exc).__name__}") from exc
        return out if out.strip() else err

    def run_diagnostic(self, command: str, *, until: str | None = None, timeout: float | None = None) -> str:
        """SPEC-020 R2: one `checkrclink` subcommand. With `until` (a regex) the output is read as it
        arrives and the channel closed once the pattern appears or `timeout` passes — the client
        prints the latency first and then blocks for the whole test length."""
        if self._client is None:
            raise ArrayCliError("not connected")
        started = time.monotonic()
        why = diagnostic_refusal(command)
        if why:
            command_log.record(target=self.host, transport="ssh", command=command, started=started, ok=False,
                               result=why, secrets=[self.password])
            raise ArrayCliError(why)
        try:
            if until is None:
                text, result = self._exec(command, timeout), "ok"
            else:
                text, matched = self._exec_until(command, until, timeout)
                result = "stopped after the latency" if matched else f"no latency within {timeout or self.exec_timeout:g} s"
        except ArrayCliError as exc:
            command_log.record(target=self.host, transport="ssh", command=command, started=started, ok=False,
                               result=str(exc), secrets=[self.password])
            raise
        failed = text.lstrip().lower().startswith("error") or result.startswith("no latency")
        command_log.record(target=self.host, transport="ssh", command=command, started=started, ok=not failed,
                           result=text.strip().splitlines()[0] if text.lstrip().lower().startswith("error") else result,
                           output=text, secrets=[self.password])
        return text

    def _exec_until(self, command: str, until: str, timeout: float | None) -> tuple[str, bool]:
        pattern = re.compile(until, re.MULTILINE)
        deadline = time.monotonic() + (timeout or self.exec_timeout)
        chunks: list[bytes] = []
        matched = False
        transport = self._client.get_transport() if self._client is not None else None
        if transport is None:
            raise ArrayCliError("not connected")
        try:
            channel = transport.open_session()
            channel.settimeout(1.0)
            channel.exec_command(command)
            try:
                while time.monotonic() < deadline:
                    if channel.recv_ready():
                        chunks.append(channel.recv(65536))
                    elif channel.exit_status_ready():
                        chunks.append(channel.recv(65536))
                        matched = bool(pattern.search(b"".join(chunks).decode("utf-8", "replace")))
                        break
                    else:
                        time.sleep(0.2)
                    if pattern.search(b"".join(chunks).decode("utf-8", "replace")):
                        matched = True
                        break
            finally:
                channel.close()
        except Exception as exc:
            raise ArrayCliError(f"running '{command}' failed: {type(exc).__name__}") from exc
        return b"".join(chunks).decode("utf-8", "replace"), matched

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except device_trust.SSH_ERRORS as exc:
                _log.debug("array_ssh_close_failed", host=self.host, error=str(exc))
            self._client = None

    def __enter__(self) -> ArrayCliClient:
        self.connect()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()
