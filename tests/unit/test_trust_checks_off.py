"""LESSONS 43 and ADR 0026: every place the tool turns a certificate or host-key check off says why at the
site (a `# TRUST-OFF:` comment) and is listed here. A new one fails this test until it carries a reason
and someone has added it below, which means reading why the others are allowed first.

Found by reading the code's syntax, not its text, so a docstring or comment that mentions a setting is
not a site.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "alletra_onboard"

# (file under src/alletra_onboard, enclosing function, what is turned off): the reason, in short.
# The whole reason is at the site and in ADR 0026.
UNCHECKED_ON_PURPOSE = {
    ("adapters/browser/cloudinit_wizard.py", "CloudinitWizardAdapter.run", "ignore_https_errors=True"):
        "the link-local setup wizard: same cable, no password typed, no certificate to record yet",
    ("adapters/array/wsapi_client.py", "WsapiReader.connect", "secure=False"):
        "a self-signed array certificate; every connection checks the pinned SHA-256 instead",
    ("adapters/device_trust.py", "probe_tls", "check_hostname=False"):
        "the probe only reads the certificate to compare it with the pin; nothing is sent",
    ("adapters/device_trust.py", "probe_tls", "verify_mode=CERT_NONE"):
        "the probe only reads the certificate to compare it with the pin; nothing is sent",
    ("adapters/device_trust.py", "pinned_context", "check_hostname=False"):
        "vCenter's own certificate; every handshake is compared with the pin instead",
    ("adapters/device_trust.py", "pinned_context", "verify_mode=CERT_NONE"):
        "vCenter's own certificate; every handshake is compared with the pin instead",
    ("adapters/hosts/windows_winrm.py", "WindowsHostClient._session_for", 'server_cert_validation="ignore"'):
        "WinRM over NTLM: the password is never sent, 5985 is encrypted, the client only reads",
}

_OFF_KEYWORDS = {
    ("ignore_https_errors", True), ("secure", False), ("verify", False), ("disableSslCertValidation", True),
    ("server_cert_validation", "ignore"),
}
_OFF_NAMES = {"AutoAddPolicy", "WarningPolicy", "_create_unverified_context"}
_REASON_WINDOW = 6   # lines above the site the TRUST-OFF comment may start on


def _show(arg: str, value: object) -> str:
    return f'{arg}="{value}"' if isinstance(value, str) else f"{arg}={value}"


class _Finder(ast.NodeVisitor):
    def __init__(self) -> None:
        self.scope: list[str] = []
        self.sites: list[tuple[str, str, int]] = []   # (function, what, line)

    def _enter(self, node) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_ClassDef = visit_FunctionDef = visit_AsyncFunctionDef = _enter

    def _add(self, what: str, node: ast.AST) -> None:
        self.sites.append((".".join(self.scope), what, node.lineno))

    def visit_keyword(self, node: ast.keyword) -> None:
        if isinstance(node.value, ast.Constant) and (node.arg, node.value.value) in _OFF_KEYWORDS:
            self._add(_show(node.arg, node.value.value), node.value)
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        for key, value in zip(node.keys, node.values):
            if (isinstance(key, ast.Constant) and isinstance(value, ast.Constant)
                    and (key.value, value.value) in _OFF_KEYWORDS):
                self._add(_show(key.value, value.value), key)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if not isinstance(target, ast.Attribute):
                continue
            if target.attr == "check_hostname" and isinstance(node.value, ast.Constant) and node.value.value is False:
                self._add("check_hostname=False", node)
            if target.attr == "verify_mode" and "CERT_NONE" in ast.unparse(node.value):
                self._add("verify_mode=CERT_NONE", node)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in _OFF_NAMES:
            self._add(node.attr, node)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in _OFF_NAMES:
            self._add(node.id, node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and "--ignore-certificate-errors" in node.value:
            self._add("--ignore-certificate-errors", node)


def _sites() -> dict[tuple[str, str, str], str]:
    """Every site in the source -> the reason written at it ('' when there is none)."""
    found: dict[tuple[str, str, str], str] = {}
    for path in sorted(SRC.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        finder = _Finder()
        finder.visit(ast.parse(text))
        for function, what, line in finder.sites:
            window = lines[max(0, line - 1 - _REASON_WINDOW):line]
            reason = next((w.split("TRUST-OFF:", 1)[1].strip() for w in reversed(window) if "# TRUST-OFF:" in w), "")
            found[(path.relative_to(SRC).as_posix(), function, what)] = reason
    return found


def test_every_check_turned_off_carries_its_reason_at_the_site():
    missing = [site for site, reason in _sites().items() if len(reason) < 20]
    assert not missing, (
        f"A certificate or host-key check is turned off without a reason: {missing}. Write `# TRUST-OFF: "
        "<why>` at the site (LESSONS 43, ADR 0026), or check the device's key through adapters/device_trust.py.")


def test_the_sites_are_exactly_the_ones_listed():
    found = set(_sites())
    assert found == set(UNCHECKED_ON_PURPOSE), (
        f"new: {sorted(found - set(UNCHECKED_ON_PURPOSE))}; gone: {sorted(set(UNCHECKED_ON_PURPOSE) - found)}. "
        "A new site needs its reason at the site and a line in UNCHECKED_ON_PURPOSE; a removed one, its line removed.")


def test_the_finder_sees_each_way_of_turning_a_check_off():
    sample = """
import paramiko, ssl
def f(client, ctx, s):
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s.get(url, verify=False)
    Session(url, server_cert_validation="ignore")
    opts = {"server_cert_validation": "ignore"}
    launch(args=["--ignore-certificate-errors"])
    ssl._create_unverified_context()
"""
    finder = _Finder()
    finder.visit(ast.parse(sample))
    assert {what for _, what, _ in finder.sites} == {
        "AutoAddPolicy", "check_hostname=False", "verify_mode=CERT_NONE", "verify=False",
        'server_cert_validation="ignore"', "--ignore-certificate-errors", "_create_unverified_context"}
