"""Brocade Fabric OS (FOS) SSH client for SAN zoning — reads, plus ADDITIVE staged writes only.

Reads the live fabric to build the zoning report + plan (ADR 0004). The write surface (revised
2026-08-15, after the write-path mandate) is deliberately minimal and ADDITIVE-ONLY:

- `alicreate` / `zonecreate` / `cfgadd`, each validated against a strict per-verb REGEX (not a loose
  token check) — the shape, the object names and the WWPN format must all match, which doubles as
  FOS name validation for operator-typed aliases.
- `cfgsave` (via `cfgsave_defined`) — commits the transaction to the DEFINED configuration only.
  Measured live on FOS 9.2.2: the confirmation prompt renders even on a no-pty exec channel, a piped
  answer is consumed, and a canceled save exits 248 — so the answer is piped and the exit status is
  checked, and callers must STILL verify via `cfgshow` that the objects landed.
- `cfgtransabort` (own method, never part of a command list) — rolls back this tool's OWN
  uncommitted transaction after a mid-sequence failure. It cannot touch committed config.

**There is no delete and no activation.** No `*delete`/`cfgremove`/`cfgclear` verb matches any write
pattern, and `cfgenable` — which REPLACES the effective config fabric-wide and auto-aborts other
admins' transactions — is excluded by design: activation is always a human action (standing mandate).

The name-server reads (`nsshow` = local, `nscamshow` = fabric-wide) map an unzoned-but-online host
WWPN to its fabric — which the array cannot see, because FC name-server *queries* are zone-filtered
(soft zoning, FC-GS) while FLOGI/registration is not. `alishow` gives the array ports' existing
aliases. See ADR 0004.
"""

from __future__ import annotations

import re
import time

try:
    import paramiko
except ImportError:  # pragma: no cover - bundled in the .exe
    paramiko = None

ALLOWED_READ = (
    "cfgshow", "zoneshow", "alishow", "nsshow", "nscamshow", "nsallshow", "fabricshow", "switchshow",
    "cfgtransshow",
)
_FORBIDDEN_CHARS = set(";|&`$><\n\r")

# FOS zone-object names: start with a letter, then letters/digits/underscore/hyphen, max 64 chars.
_NAME = r"[A-Za-z][A-Za-z0-9_-]{0,63}"
_WWPN = r"(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}"
# The ONLY writable command shapes. `;` is a zone-member separator INSIDE the quoted argument of
# these exact forms — everywhere else it stays a forbidden metacharacter.
ALLOWED_WRITE = {
    "alicreate": re.compile(rf'^alicreate "({_NAME})","({_WWPN})"$'),
    "zonecreate": re.compile(rf'^zonecreate "({_NAME})","({_NAME});({_NAME})"$'),
    "cfgadd": re.compile(rf'^cfgadd "({_NAME})","({_NAME}(?:;{_NAME})*)"$'),
}


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

    # ------------------------------------------------------------------ staged writes (additive only)

    def write(self, command: str) -> str:
        """Run ONE additive zoning command (`alicreate`/`zonecreate`/`cfgadd`), validated against the
        strict shape patterns. These commands are silent on success (measured: exit 0, no output), so
        ANY output or a non-zero exit is a refusal by the switch and raises with FOS's own words."""
        verb = command.split()[0] if command.split() else ""
        pattern = ALLOWED_WRITE.get(verb)
        if pattern is None:
            raise BrocadeRefused(f"refused: '{verb}' is not an allowed additive zoning command")
        if not pattern.match(command):
            raise BrocadeRefused(
                f"refused: '{verb}' arguments do not match the required shape "
                "(FOS object names start with a letter; letters/digits/_/- only, max 64 chars)"
            )
        status, out = self._exec_status(command)
        if status != 0 or out.strip():
            raise BrocadeError(f"the switch refused '{command}': {out.strip() or f'exit {status}'}")
        return out

    def cfgsave_defined(self) -> str:
        """Commit the open transaction to the DEFINED configuration only — never activates anything.
        Answers the confirmation prompt with 'y' via stdin (measured on FOS 9.2.2: the prompt renders
        on a plain exec channel; a canceled save exits 248). The caller must still verify via
        `cfgshow` that the objects are present in the defined config — never trust this alone."""
        status, out = self._exec_status("cfgsave", stdin_data="y\n")
        low = out.lower()
        if status != 0 or "operation cancel" in low:
            raise BrocadeError(f"cfgsave did not commit (exit {status}): {out.strip()}")
        return out

    def cfgtransabort(self) -> str:
        """Roll back this session's OWN uncommitted zoning transaction (after a mid-sequence failure).
        Discards unsaved work only — it cannot delete anything from the committed configuration."""
        status, out = self._exec_status("cfgtransabort")
        return out

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

    def _exec_status(self, command: str, stdin_data: str | None = None) -> tuple[int, str]:
        """Run a command and return (exit_status, combined output). `stdin_data` pre-answers an
        interactive prompt (cfgsave) — written immediately so the command never blocks on a read."""
        if self._client is None:
            raise BrocadeError("not connected")
        try:
            transport = self._client.get_transport()
            chan = transport.open_session()
            chan.settimeout(self.exec_timeout)
            chan.exec_command(command)
            if stdin_data:
                chan.sendall(stdin_data.encode())
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
