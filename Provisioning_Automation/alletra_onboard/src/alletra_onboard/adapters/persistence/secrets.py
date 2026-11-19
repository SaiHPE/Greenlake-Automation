"""The secret fields of the state database, encrypted at rest (ADR 0027).

Only the secret values are sealed, each one as ``{"fernet": "<token>"}`` in place of the string, so
the rest of a stored work item or intent stays readable for support. The key is a Fernet key in a file
of its own next to the database, made on the first save. A value stored before this existed is a plain
string and is read as it is.
"""

from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from alletra_onboard.domain.ports import StoredCredentialsUnreadableError

KEY_FILE_NAME = "secrets.key"
SEALED = "fernet"

_create_lock = threading.Lock()


def _damaged(path: Path) -> StoredCredentialsUnreadableError:
    return StoredCredentialsUnreadableError(
        f"The key file that protects stored credentials ({path}) is damaged. Move it aside and upload "
        "the initialisation sheet again to start a new run."
    )


class SecretBox:
    def __init__(self, key_path: Path) -> None:
        self.key_path = key_path
        self._fernet: Fernet | None = None

    def seal(self, value: str) -> dict[str, str]:
        token = self._key(create=True).encrypt(value.encode("utf-8"))
        return {SEALED: token.decode("ascii")}

    def open(self, value: Any) -> Any:
        """The plain value of a stored secret: a sealed one decrypted, an older plain one as it is."""
        if not is_sealed(value):
            return value
        try:
            return self._key(create=False).decrypt(value[SEALED].encode("ascii")).decode("utf-8")
        except (InvalidToken, ValueError, UnicodeError) as exc:
            raise StoredCredentialsUnreadableError() from exc

    def _key(self, *, create: bool) -> Fernet:
        if self._fernet is not None:
            return self._fernet
        with _create_lock:
            if self._fernet is None:
                raw = self._read_key()
                if raw is None:
                    if not create:
                        raise StoredCredentialsUnreadableError()
                    raw = self._create_key()
                try:
                    self._fernet = Fernet(raw)
                except (ValueError, TypeError) as exc:
                    error = _damaged(self.key_path) if create else StoredCredentialsUnreadableError()
                    raise error from exc
        return self._fernet

    def _read_key(self) -> bytes | None:
        # A file another process has just created may still be empty for a moment.
        for _ in range(20):
            try:
                raw = self.key_path.read_bytes().strip()
            except FileNotFoundError:
                return None
            if raw:
                return raw
            time.sleep(0.05)
        return b""

    def _create_key(self) -> bytes:
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        try:
            fd = os.open(self.key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
        except FileExistsError:
            return self._read_key() or b""
        try:
            os.write(fd, key + b"\n")
            os.fsync(fd)
        finally:
            os.close(fd)
        if os.name == "posix":
            os.chmod(self.key_path, 0o600)
        return key


def is_sealed(value: Any) -> bool:
    return isinstance(value, dict) and isinstance(value.get(SEALED), str)
