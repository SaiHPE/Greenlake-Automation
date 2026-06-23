"""Read-only SSH client for the array CLI — post-init verification (see docs/adr/0001).

Logs into the initialized array with the admin account and runs an allowlist of ``show*`` commands
to read the running config. It can ONLY run those commands — the path is structurally read-only, so
verification can never mutate the array.
"""

from __future__ import annotations

try:
    import paramiko
except ImportError:  # pragma: no cover - bundled in the .exe; optional for non-SSH runs
    paramiko = None

# The ONLY commands this client may ever run. All read-only `show*` — anything else is refused.
ALLOWED_COMMANDS = (
    # post-init config verification
    "showsys", "shownet", "showdate", "showversion",
    # provisioning / SAN-discovery preflight (read-only — see the WSAPI provisioning plan)
    "showwsapi", "showcpg", "showspace", "showvv", "showvlun",
    "showhost", "showport", "showportdev", "showrcopy", "showtarget",
)
# Shell metacharacters that could chain or redirect a second command — never present in a legit
# show* invocation, so we reject the whole command if any appear (defence in depth on top of the
# base-command allowlist).
_FORBIDDEN_CHARS = set(";|&`$><\n\r")


class ArrayCliError(Exception):
    """Couldn't connect, authenticate, or run a command on the array."""


class ArrayCliClient:
    def __init__(self, host: str, username: str, password: str, port: int = 22, timeout: float = 15.0) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self._client = None

    def connect(self) -> None:
        if paramiko is None:
            raise ArrayCliError("SSH support (paramiko) is not available in this build.")
        client = paramiko.SSHClient()
        # Fresh array — no known_hosts to pin against (accepted; local mgmt network). See the ADR.
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                allow_agent=False,
                look_for_keys=False,
            )
        except paramiko.AuthenticationException as exc:
            raise ArrayCliError(
                f"Login failed for {self.username}@{self.host} — check the admin username/password "
                "(the System Credential you set in DSCC)."
            ) from exc
        except Exception as exc:  # noqa: BLE001 - socket/timeout/SSH errors
            raise ArrayCliError(
                f"Could not reach the array at {self.host}:{self.port} ({type(exc).__name__}) — check "
                "it's powered on, on this subnet, and that SSH is enabled."
            ) from exc
        self._client = client

    def run(self, command: str) -> str:
        if self._client is None:
            raise ArrayCliError("not connected")
        if any(ch in command for ch in _FORBIDDEN_CHARS):
            raise ArrayCliError("refused: command contains a forbidden shell metacharacter")
        parts = command.split()
        base = parts[0] if parts else ""
        if base not in ALLOWED_COMMANDS:
            raise ArrayCliError(f"refused: '{base}' is not a read-only show command")
        try:
            _stdin, stdout, stderr = self._client.exec_command(command, timeout=self.timeout)
            out = stdout.read().decode("utf-8", "replace")
            err = stderr.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            raise ArrayCliError(f"running '{command}' failed: {type(exc).__name__}") from exc
        return out if out.strip() else err

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001
                pass
            self._client = None

    def __enter__(self) -> "ArrayCliClient":
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
