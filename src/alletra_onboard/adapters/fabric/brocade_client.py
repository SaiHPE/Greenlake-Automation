"""Brocade Fabric OS (FOS) SSH client for SAN zoning — READ-ONLY.

Reads the live fabric to build the zoning report + the read-only zoning PLAN (ADR 0004, revised
2026-07-03): the tool VERIFIES zoning and produces the exact additive command sequence for the SAN
team to apply by hand. **It never writes to the switch.** Only an allowlist of read/inspection
commands is reachable, and shell metacharacters are rejected — there is deliberately no write path.

The name-server reads (`nsshow` = local, `nscamshow` = fabric-wide) map an unzoned-but-online host
WWPN to its fabric — which the array cannot see, because FC name-server *queries* are zone-filtered
(soft zoning, FC-GS) while FLOGI/registration is not. `alishow` gives the array ports' existing
aliases. See ADR 0004.
"""

from __future__ import annotations

try:
    import paramiko
except ImportError:  # pragma: no cover - bundled in the .exe
    paramiko = None

# Read-only fabric inspection ONLY. There is intentionally NO write allowlist (no alicreate /
# zonecreate / cfgadd / cfgenable / cfgsave / *delete): the tool does not modify the fabric.
ALLOWED_READ = (
    "cfgshow", "zoneshow", "alishow", "nsshow", "nscamshow", "nsallshow", "fabricshow", "switchshow",
)
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

    # ------------------------------------------------------------------ internals

    def _guard(self, command: str) -> None:
        if any(ch in command for ch in _FORBIDDEN_CHARS):
            raise BrocadeRefused("refused: command contains a forbidden shell metacharacter")
        base = command.split()[0] if command.split() else ""
        if base not in ALLOWED_READ:
            raise BrocadeRefused(f"refused: '{base}' is not an allowed read-only command")

    def _exec(self, command: str) -> str:
        if self._client is None:
            raise BrocadeError("not connected")
        try:
            _stdin, stdout, stderr = self._client.exec_command(command, timeout=self.exec_timeout)
            out = stdout.read().decode("utf-8", "replace")
            err = stderr.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            raise BrocadeError(f"running '{command}' failed: {type(exc).__name__}") from exc
        return out if out.strip() else err
