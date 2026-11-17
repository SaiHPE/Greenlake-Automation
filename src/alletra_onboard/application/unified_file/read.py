"""SPEC-028 R1: read the array's file side. Pure parsers, no I/O.

Pinned to `tests/fixtures/unified_file/`: `rack13/` (rack13-ARCUS, OS 10.6.0, WSAPI v3 2.6.0, no
File ports, a stopped service and empty collections) and `d22u27/` (AlletraMP_D22U27, OS 10.5.0,
WSAPI v3 2.5.0, four File ports, the service on, three file systems, client groups and shares). The
fixtures READMEs list the facts each parser rests on. The v3 client and `read_file_report` come in
later steps of work packet BL-28.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from alletra_onboard.application.provisioning.discovery import parse_file_ports
from alletra_onboard.domain.discovery import EthernetPort
from alletra_onboard.domain.unified_file import (
    ClientGroup,
    ClientRule,
    FileCapacity,
    FileNodeStatus,
    FilePortStatus,
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
    """`showport -file` -> the File ports, through Discovery's own `parse_file_ports` (one reader for
    one fact). The array's *"There is no specified port information."* means none. Any other answer
    without a port row is refused: an error or an empty reply is not "no File ports"."""
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
