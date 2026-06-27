"""Brocade Fabric OS (FOS) SSH client for SAN zoning — read + additive write.

Reads the live fabric (cfgshow / alishow / nsshow / fabricshow) to verify zoning, and — on explicit
operator confirmation only — applies *additive* zoning to extend the active config WITHOUT disrupting
the hundreds of unrelated zones on the shared production fabric. See ADR 0004.

Safety, enforced structurally:
- An **allowlist** of read commands and a **separate allowlist of additive write commands**. Nothing
  destructive is reachable (no cfgremove / zonedelete / alidelete / cfgclear / cfgdisable / cfgcreate).
- Shell metacharacters are rejected (no command chaining/redirection).
- **Activation is `cfgenable`, never `cfgsave`-alone.** `cfgsave` alone only commits the *Defined*
  config and leaves Effective/Defined inconsistent (the central live-fabric pitfall — deep-research
  verified). `cfgsave` is therefore NOT in the write allowlist; the apply path ends with `cfgenable`.
"""

from __future__ import annotations

try:
    import paramiko
except ImportError:  # pragma: no cover - bundled in the .exe
    paramiko = None

# Read-only fabric inspection.
ALLOWED_READ = (
    "cfgshow", "zoneshow", "alishow", "nsshow", "fabricshow", "switchshow", "nscamshow",
)
# Additive zoning only — these EXTEND the active config; none remove/replace anything.
# cfgenable activates AND persists; cfgsave-alone is deliberately excluded (see module docstring).
ALLOWED_WRITE = (
    "alicreate", "aliadd", "zonecreate", "zoneadd", "cfgadd", "cfgenable",
)
_FORBIDDEN_CHARS = set(";|&`$><\n\r")


class BrocadeError(Exception):
    """Couldn't connect, authenticate, or run a command on the switch."""


class BrocadeRefused(BrocadeError):
    """A command was refused by the allowlist / metacharacter guard (never sent to the switch)."""


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

    # ------------------------------------------------------------------ reads

    def read(self, command: str) -> str:
        self._guard(command, ALLOWED_READ)
        return self._exec(command)

    def cfgshow(self) -> str:
        return self.read("cfgshow")

    def alishow(self) -> str:
        return self.read("alishow")

    def nsshow(self) -> str:
        return self.read("nsshow")

    def fabricshow(self) -> str:
        return self.read("fabricshow")

    # ------------------------------------------------------------------ additive writes (confirmed)

    def apply(self, commands: list[str]) -> list[tuple[str, str]]:
        """Run an ordered list of additive zoning commands, confirming any prompts. STOPS on the first
        error. Returns [(command, output), …]. Caller must have previewed + confirmed these exact lines.
        """
        results: list[tuple[str, str]] = []
        for command in commands:
            self._guard(command, ALLOWED_WRITE)
            out = self._exec(command, confirm=True)
            results.append((command, out))
            if _looks_like_error(out):
                raise BrocadeError(f"Switch rejected '{command}': {out.strip()[:300]}")
        return results

    # ------------------------------------------------------------------ internals

    def _guard(self, command: str, allowed: tuple[str, ...]) -> None:
        if any(ch in command for ch in _FORBIDDEN_CHARS):
            raise BrocadeRefused("refused: command contains a forbidden shell metacharacter")
        base = command.split()[0] if command.split() else ""
        if base not in allowed:
            raise BrocadeRefused(f"refused: '{base}' is not an allowed {'write' if allowed is ALLOWED_WRITE else 'read'} command")

    def _exec(self, command: str, *, confirm: bool = False) -> str:
        if self._client is None:
            raise BrocadeError("not connected")
        try:
            stdin, stdout, stderr = self._client.exec_command(command, timeout=self.exec_timeout)
            if confirm:
                # FOS prompts e.g. cfgenable: "Do you want to enable …? (yes, y, no, n): [no]".
                # Feed an affirmative; harmless for commands that don't prompt.
                try:
                    stdin.write("yes\n")
                    stdin.flush()
                    stdin.channel.shutdown_write()
                except Exception:  # noqa: BLE001 - some commands close stdin first
                    pass
            out = stdout.read().decode("utf-8", "replace")
            err = stderr.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            raise BrocadeError(f"running '{command}' failed: {type(exc).__name__}") from exc
        return out if out.strip() else err


def _looks_like_error(output: str) -> bool:
    low = output.lower()
    return any(token in low for token in ("error", "invalid", "not found", "failed", "duplicate"))
