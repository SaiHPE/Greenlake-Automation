"""Brocade Fabric OS (FOS) SSH client for SAN zoning — STRICTLY READ-ONLY.

Reads the live fabric to build the zoning report + plan. **This client cannot write to a switch.**
Every command goes through `_guard`, which rejects shell metacharacters and anything outside
`ALLOWED_READ`, so there is no verb here that creates, deletes, commits or activates zoning — not
`alicreate`, not `cfgsave`, not `cfgenable`. The zoning step's deliverable is the *command set*,
which a consultant reviews and applies by hand (ADR 0012).

An additive write surface (`alicreate`/`zonecreate`/`cfgadd` + `cfgsave`) existed here in v0.14.0
and v0.15.0 and was removed. It worked — it created a zone on a live production fabric on
2026-08-31 — but no ADR or glossary entry ever authorised it, and only Brocade FOS was ever tested
while Cisco MDS needs entirely different verbs. Applying zoning is the SAN team's act, on their
schedule, in their dialect. See docs/adr/0012 and docs/validation/2026-08-31-rack13arcus-live-test.md.

The name-server reads (`nsshow` = local, `nscamshow` = fabric-wide) map an unzoned-but-online host
WWPN to its fabric — which the array cannot see, because FC name-server *queries* are zone-filtered
(soft zoning, FC-GS) while FLOGI/registration is not. `alishow` gives the array ports' existing
aliases. See ADR 0004.
"""

from __future__ import annotations

import time

try:
    import paramiko
except ImportError:  # pragma: no cover - bundled in the .exe
    paramiko = None

ALLOWED_READ = (
    "cfgshow", "zoneshow", "alishow", "nsshow", "nscamshow", "nsallshow", "fabricshow", "switchshow",
    "cfgtransshow",
)
# `;` stays forbidden everywhere: with no write verbs there is no command whose quoted argument
# legitimately contains one.
_FORBIDDEN_CHARS = set(";|&`$><\n\r")


class BrocadeError(Exception):
    """Couldn't connect, authenticate, or run a command on the switch."""


class BrocadeRefused(BrocadeError):
    """A command was refused by the read-only allowlist / metacharacter guard (never sent)."""


class BrocadeClient:
    def __init__(
        self, host: str, username: str, password: str, port: int = 22,
        timeout: float = 20.0, exec_timeout: float = 60.0,
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.exec_timeout = exec_timeout
        self._client = None

    # ------------------------------------------------------------------ lifecycle

    def connect(self) -> None:
        if paramiko is None:
            raise BrocadeError("SSH support (paramiko) is not available in this build.")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                self.host, port=self.port, username=self.username, password=self.password,
                timeout=self.timeout, allow_agent=False, look_for_keys=False,
            )
        except paramiko.AuthenticationException as exc:
            raise BrocadeError(f"Login failed for {self.username}@{self.host} — check the switch credentials.") from exc
        except Exception as exc:  # noqa: BLE001
            raise BrocadeError(
                f"Could not reach the switch at {self.host}:{self.port} ({type(exc).__name__})."
            ) from exc
        self._client = client

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001
                pass
            self._client = None

    def __enter__(self) -> "BrocadeClient":
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # ------------------------------------------------------------------ reads (read-only)

    def read(self, command: str) -> str:
        self._guard(command)
        return self._exec(command)

    def cfgshow(self) -> str:
        return self.read("cfgshow")

    def alishow(self) -> str:
        return self.read("alishow")

    def nsshow(self) -> str:
        return self.read("nsshow")

    def nscamshow(self) -> str:
        return self.read("nscamshow")

    def fabricshow(self) -> str:
        return self.read("fabricshow")

    def cfgtransshow(self) -> str:
        return self.read("cfgtransshow")

    # ------------------------------------------------------------------ internals

    def _guard(self, command: str) -> None:
        if any(ch in command for ch in _FORBIDDEN_CHARS):
            raise BrocadeRefused("refused: command contains a forbidden shell metacharacter")
        base = command.split()[0] if command.split() else ""
        if base not in ALLOWED_READ:
            raise BrocadeRefused(f"refused: '{base}' is not an allowed read-only command")

    def _exec(self, command: str) -> str:
        _status, out = self._exec_status(command)
        return out

    def _exec_status(self, command: str) -> tuple[int, str]:
        """Run a read command and return (exit_status, combined output).

        Nothing is ever written to the channel's stdin. FOS prompts interactively for confirmation on
        its config-changing verbs, so a client that cannot answer a prompt cannot complete one even if
        a write verb were somehow reintroduced — the command would hang and time out rather than
        silently commit. That is deliberate belt-and-braces behind `_guard` (ADR 0012)."""
        if self._client is None:
            raise BrocadeError("not connected")
        try:
            transport = self._client.get_transport()
            chan = transport.open_session()
            chan.settimeout(self.exec_timeout)
            chan.exec_command(command)
            buf = bytearray()
            deadline = time.monotonic() + self.exec_timeout
            while time.monotonic() < deadline:
                while chan.recv_ready():
                    buf.extend(chan.recv(65536))
                while chan.recv_stderr_ready():
                    buf.extend(chan.recv_stderr(65536))
                if chan.exit_status_ready() and not chan.recv_ready() and not chan.recv_stderr_ready():
                    break
                time.sleep(0.1)
            else:
                chan.close()
                raise BrocadeError(f"'{command}' did not complete within {self.exec_timeout:.0f}s")
            status = chan.recv_exit_status()
            chan.close()
        except BrocadeError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise BrocadeError(f"running '{command}' failed: {type(exc).__name__}") from exc
        return status, buf.decode("utf-8", "replace")
