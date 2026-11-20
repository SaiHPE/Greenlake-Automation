"""SPEC-028 R1-R2: read the array's file side.

The parsers are pure. Pinned to `tests/fixtures/unified_file/`: `rack13/` (rack13-ARCUS, OS 10.6.0,
WSAPI v3 2.6.0, no File ports, a stopped service and empty collections) and `d22u27/`
(AlletraMP_D22U27, OS 10.5.0, WSAPI v3 2.5.0, four File ports, the service on, three file systems,
client groups and shares). The fixtures READMEs list the facts each parser rests on.

`read_file_report` is the one read: the run's read-only SSH session for `showsys`, and a GET-only
WSAPI v3 client (ADR 0021) for the four collections. It never raises for the file side: what went
wrong is one of R2's sentences in `FileReport.notes`, and block storage is never affected.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from alletra_onboard.domain.array_parse import (
    parse_file_ports,
    parse_showsys,
    parse_showversion,
)
from alletra_onboard.domain.discovery import EthernetPort
from alletra_onboard.domain.errors import (
    WsapiV3Error,
    WsapiV3LoginRefused,
    WsapiV3TrustError,
)
from alletra_onboard.domain.unified_file import (
    ClientGroup,
    ClientRule,
    FileCapacity,
    FileNodeStatus,
    FilePortStatus,
    FileReport,
    FileService,
    FileShareRecord,
    FileSystemRecord,
)

#: The array's whole answer to `showport -file` when it has no File port.
NO_PORT_INFORMATION = "There is no specified port information"


class UnexpectedAnswer(ValueError):
    """An answer in a shape no capture has shown. Never read as "nothing there": the caller says it
    could not read the file side (SPEC-028 R2) instead of showing an empty one."""


def _members(body: Any, resource: str) -> dict[str, dict[str, Any]]:
    """A v3 collection is `{"version", "arraySerialNumber", "members": {<uid>: record}}`. An empty one
    has `"members": {}`: a map, not a list."""
    members = body.get("members") if isinstance(body, dict) else None
    if not isinstance(members, dict) or not all(isinstance(r, dict) for r in members.values()):
        raise UnexpectedAnswer(f"GET /api/v3/{resource}: the answer has no members map")
    return members


def _records[T](body: Any, resource: str, build: Callable[[str, dict[str, Any]], T]) -> list[T]:
    """Each member through `build(uid, record)`, in the array's order. A record missing a field the
    model needs is refused as a whole answer, never skipped."""
    out: list[T] = []
    for key, rec in _members(body, resource).items():
        try:
            out.append(build(str(rec.get("uid") or key), rec))
        except (KeyError, TypeError, AttributeError, ValidationError) as exc:
            raise UnexpectedAnswer(f"GET /api/v3/{resource}: {exc!r}") from exc
    return out


def parse_array_serial(body: Any) -> str:
    """The serial a v3 collection names (`arraySerialNumber`), "" when it names none. It is the serial
    `showsys` prints, so a read can be checked to be of the run's own array."""
    serial = body.get("arraySerialNumber") if isinstance(body, dict) else None
    return serial if isinstance(serial, str) else ""


def _capacity(cap: dict[str, Any]) -> FileCapacity:
    return FileCapacity(
        total=cap["totalCapacity"], used=cap["usedCapacity"], available=cap["availableCapacity"],
        limit_percentage=cap.get("limitPercentage"), file_systems=cap.get("numberOfFileSystems"),
        file_shares=cap.get("numberOfFileShares"),
    )


def _node(summary: dict[str, Any]) -> FileNodeStatus:
    return FileNodeStatus(
        node=summary["nodeNum"], status=summary["fileserviceStatus"],
        ports=[FilePortStatus(configured=p["isFilePortConfigured"], online=p["isFilePortOnline"],
                              mtu=p.get("mtu", 0))
               for p in summary.get("portStatus") or []],
    )


def _service(uid: str, rec: dict[str, Any]) -> FileService:
    cap = rec.get("capacitySummary")
    return FileService(
        uid=uid,
        enabled=rec["isFileServiceEnabled"],
        name=(rec.get("displayname") or {}).get("default", ""),
        system_wwn=rec.get("systemWWN", ""),
        domain=rec.get("domain", ""),
        ransomware_check=rec.get("enabledRansomwareCheck"),
        nodes=[_node(n) for n in rec["fileServiceSummary"]],
        capacity=_capacity(cap) if isinstance(cap, dict) else None,
    )


def parse_fileservice(body: Any) -> FileService | None:
    """`GET /api/v3/fileservice` -> the file service, None when the collection is empty. There is one
    per array, so a second member is refused rather than one of them picked."""
    services = _records(body, "fileservice", _service)
    if len(services) > 1:
        raise UnexpectedAnswer(f"GET /api/v3/fileservice: {len(services)} file services, expected one")
    return services[0] if services else None


def _clients(info: list[dict[str, Any]]) -> list[ClientRule]:
    return [ClientRule(address=c["ipaddress"], access=c["access"], options=c.get("options", ""))
            for c in info]


def _file_system(uid: str, rec: dict[str, Any]) -> FileSystemRecord:
    return FileSystemRecord(
        uid=uid, id=rec.get("id"), name=rec["name"], state=rec["state"],
        size_mib=rec["sizeInMiB"], vv_size_mib=rec.get("vvSizeInMiB"), reduce=rec["reduce"],
        prov=rec.get("prov", ""), share_count=rec["sharecount"], owner_node=rec["fsmaster"],
        volumes=[m["vvname"] for m in (rec.get("volumemembers") or {}).values()],
    )


def _client_group(uid: str, rec: dict[str, Any]) -> ClientGroup:
    return ClientGroup(
        uid=uid, id=rec.get("id"), name=rec["name"], state=rec["state"],
        clients=_clients(rec["clientInfo"]), host_count=rec.get("hostCount"),
        share_count=rec.get("sharecount"),
    )


def _share(uid: str, rec: dict[str, Any]) -> FileShareRecord:
    return FileShareRecord(
        uid=uid, id=rec.get("id"), name=rec["name"], state=rec["state"],
        file_system=rec["filesystem"]["name"], client_group=rec["sharesettings"]["name"],
        mount_path=rec["mountpath"], protocols=list(rec["protocol"]), host_ip=rec.get("hostip", ""),
    )


def parse_filesystems(body: Any) -> list[FileSystemRecord]:
    """`GET /api/v3/filesystems` -> one record per member, in the array's order."""
    return _records(body, "filesystems", _file_system)


def parse_sharesettings(body: Any) -> list[ClientGroup]:
    """`GET /api/v3/filesharesettings` -> one client group per member, in the array's order."""
    return _records(body, "filesharesettings", _client_group)


def parse_fileshares(body: Any) -> list[FileShareRecord]:
    """`GET /api/v3/fileshares` -> one record per member, in the array's order."""
    return _records(body, "fileshares", _share)


def parse_showport_file(text: str) -> list[EthernetPort]:
    """`showport -file` -> the File ports, through `parse_file_ports` (one reader for one fact).
    The array's *"There is no specified port information."* means none. Any other answer without
    a port row is refused: an error or an empty reply is not "no File ports"."""
    ports = parse_file_ports(text)
    if ports or NO_PORT_INFORMATION in (text or ""):
        return ports
    raise UnexpectedAnswer("showport -file: neither a File port nor the array's no-port answer")


def parse_help_syntax(text: str) -> list[str]:
    """The SYNTAX section of a CLI help answer, one form per line, whitespace trimmed. The file
    commands print one line each; a preamble such as *"The syntax for ... can be one of the
    following:"* is left out."""
    forms: list[str] = []
    inside = False
    for line in (text or "").splitlines():
        if line.strip() == "SYNTAX":
            inside = True
        elif inside and line[:1] not in (" ", "\t", ""):
            break
        elif inside and line.strip() and not line.strip().startswith("The syntax for"):
            forms.append(" ".join(line.split()))
    return forms


# ---- SPEC-028 R2: what Discovery says when there is nothing to read ---------------------------------

#: R2's sentences, word for word. Each is a note, never an error that stops Discovery.
OS_TOO_OLD = "This array runs OS {version}. File shares need OS 10.5 or later."
NO_ANSWER = "The array did not answer on its file API, so only the File ports are shown."
SESSION_REFUSED = (
    "The array's file API turned down the tool's session, so only the File ports are shown. "
    "Block storage is not affected; send the console log to the tool team."
)
OTHER_ARRAY = (
    "The file API at this address belongs to array {found}, not to this run's array {expected}, so "
    "file details are not shown. Check the array address in the workbook."
)
SERVICE_OFF = (
    "The file service is off on this array. Turn it on in the array's UI before shares can be made."
)
#: Not one of R2's cases: an HTTP status other than 200, 401 or 403, or an answer in a shape no
#: capture has shown (`UnexpectedAnswer`). In R2's form; the console log has the call and its answer.
UNREADABLE = (
    "The array's file API gave an answer the tool could not read, so only the File ports are shown. "
    "Block storage is not affected; send the console log to the tool team."
)
#: In OTHER_ARRAY's place of a serial: a collection that names none, or a `showsys` that printed none.
NO_SERIAL = "(no serial given)"

#: The four collections of R1, in the order they are read.
V3_READS = ("fileservice", "filesystems", "filesharesettings", "fileshares")
_FILE_OS = (10, 5)
_SESSION_STATUS = (401, 403)


def file_os(os_version: str) -> bool | None:
    """True from OS 10.5 (the first with Unified File), False below it, None when the version was
    not read."""
    numbers = [int(n) for n in re.findall(r"\d+", os_version or "")[:2]]
    if len(numbers) < 2:
        return None
    return tuple(numbers) >= _FILE_OS


class _NotRead(Exception):
    def __init__(self, note: str) -> None:
        super().__init__(note)
        self.note = note


def _same_serial(a: str, b: str) -> bool:
    return bool(a.strip()) and a.strip().upper() == b.strip().upper()


def _run_serial(cli) -> str:
    try:
        return parse_showsys(cli.run("showsys")).get("serial", "")
    except Exception:  # a serial that cannot be read cannot match: the read is refused
        return ""


def _other_array(body: Any, expected: str) -> str:
    """OTHER_ARRAY's sentence when a collection does not name the run's array, else ""."""
    found = parse_array_serial(body)
    if _same_serial(found, expected):
        return ""
    return OTHER_ARRAY.format(found=found or NO_SERIAL, expected=expected or NO_SERIAL)


def _read_collections(v3, expected: str) -> dict[str, Any]:
    """The four GETs in one session, each checked to name the run's array before the next is sent.
    Another array's answer is refused at once and its body never reaches the command log. The
    session is deleted on the way out, whatever happens."""

    def withhold(answer) -> str:
        if answer.status != 200 or not _other_array(answer.body, expected):
            return ""
        found = parse_array_serial(answer.body) or NO_SERIAL
        return f"(not recorded: the answer names array {found}, not this run's array {expected or NO_SERIAL})"

    try:
        with v3:
            bodies: dict[str, Any] = {}
            for resource in V3_READS:
                answer = v3.get(f"/{resource}", withhold=withhold)
                if answer.status in _SESSION_STATUS:
                    raise _NotRead(SESSION_REFUSED)
                if answer.status != 200:
                    raise _NotRead(UNREADABLE)
                refused = _other_array(answer.body, expected)
                if refused:
                    raise _NotRead(refused)
                bodies[resource] = answer.body
            return bodies
    except WsapiV3TrustError as exc:
        raise _NotRead(str(exc)) from exc   # the certificate sentence itself, never "did not answer"
    except WsapiV3Error as exc:
        raise _NotRead(NO_ANSWER) from exc
    except WsapiV3LoginRefused as exc:
        note = SESSION_REFUSED if exc.answer.status in _SESSION_STATUS else UNREADABLE
        raise _NotRead(note) from exc


def read_file_report(cli, v3, os_version: str, file_ports: list[EthernetPort]) -> FileReport | None:
    """SPEC-028 R1-R2: the file side of the run's array, or None when there is nothing to show.

    `cli` is the run's read-only SSH session (it runs `showsys`); `v3` an unopened WSAPI v3 client,
    whose session this opens and always deletes; `os_version` is what `showversion` printed and
    `file_ports` what `showport -file` listed (read once, by the caller).

    Whether anything is shown is decided by the File ports and `isFileServiceEnabled`, never by
    whether v3 answered: rack13-ARCUS has no File ports and answers all four GETs with a stopped
    service, and shows nothing. With no File ports the file API is read only when the OS is known
    to be 10.5 or later, and anything but a running service read from the run's own array shows
    nothing. With File ports, each failure is one of R2's sentences and nothing read is kept.
    """
    capable = file_os(os_version)
    if capable is False or (capable is None and not file_ports):
        if capable is False and file_ports:
            return FileReport(os_version=os_version, notes=[OS_TOO_OLD.format(version=os_version)])
        return None
    expected = _run_serial(cli)
    report = FileReport(os_version=os_version, array_serial=expected)
    try:
        bodies = _read_collections(v3, expected)
        try:
            service = parse_fileservice(bodies["fileservice"])
            systems = parse_filesystems(bodies["filesystems"])
            groups = parse_sharesettings(bodies["filesharesettings"])
            shares = parse_fileshares(bodies["fileshares"])
        except UnexpectedAnswer as exc:
            raise _NotRead(UNREADABLE) from exc
    except _NotRead as exc:
        if not file_ports:
            return None
        report.notes.append(exc.note)
        return report
    if not file_ports and not (service and service.enabled):
        return None
    report.service, report.file_systems, report.client_groups, report.shares = service, systems, groups, shares
    if service is None or not service.enabled:
        report.notes.append(SERVICE_OFF)
    return report


def read_file_side(cli, v3, os_version: str, showport_file: str) -> tuple[list[EthernetPort], FileReport | None]:
    """The File ports from a `showport -file` answer, then `read_file_report`, by Discovery's rules.
    An answer that is neither a port list nor the no-port answer raises `UnexpectedAnswer`, except
    below OS 10.5, which has no File view: there it is read as nothing about file."""
    try:
        ports = parse_showport_file(showport_file)
    except UnexpectedAnswer:
        if file_os(os_version) is False:
            return [], None
        raise
    return ports, read_file_report(cli, v3, os_version, ports)


def read_array_file(cli, v3) -> tuple[list[EthernetPort], FileReport | None]:
    """`showversion` and `showport -file` on an open session, then `read_file_side`."""
    return read_file_side(cli, v3, parse_showversion(cli.run("showversion")), cli.run("showport -file"))

