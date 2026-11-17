"""Unified File models (SPEC-028 R1): what the array's own WSAPI v3 says about its NFS file service.

No I/O. Each field names the WSAPI v3 key it is read from, and every key here appears in a capture
(`tests/fixtures/unified_file/`): rack13-ARCUS (OS 10.6.0, service off, nothing in it) and
AlletraMP_D22U27 (OS 10.5.0, service on, three file systems, client groups and shares). A field
only one of them sends is optional, and None means the array did not say.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

#: `fileserviceStatus` of a node whose file service runs (D22U27). A stopped one says "stopped".
NODE_RUNNING = "normal"

#: The array's file CLI, each form exactly as the SYNTAX line of its own help prints it (D22U27,
#: OS 10.5.0; the same text on E18U31 10.5.60 and VZ 10.5.51; the show forms also on rack13 10.6.0).
#: Text for the removal set and the operator (SPEC-028 R10). The tool runs none of them, and none is
#: in an SSH allowlist (ADR 0021 items 1 and 5).
FILE_CLI_SYNTAX: dict[str, str] = {
    "showfileservice": "showfileservice [options]",
    "showfilesystem": "showfilesystem [name]",
    "showfileshare": "showfileshare [<filesystem_name> [<share_name>]]",
    "showsharesetting": "showsharesetting [sharesetting_name]",
    "createfilesystem": "createfilesystem [-tpvv|-reduce] <name> <size>[g|G|t|T]",
    "createsharesetting":
        "createsharesetting [-add <ipaddr_list>? <options for host access>] sharesetting_name",
    "createfileshare": "createfileshare [options] <filesystem_name> <share_name>",
    "removefileshare": "removefileshare [options] <filesystem_name> <share_name>",
    "removefilesystem": "removefilesystem [options] <name>",
    "removesharesetting": "removesharesetting <sharesetting_name>",
}


class FilePortStatus(BaseModel):
    """One entry of a node's `portStatus` list. The array gives no port id here (two entries per
    node on both arrays captured), so the File ports themselves come from `showport -file`."""

    configured: bool        # isFilePortConfigured
    online: bool            # isFilePortOnline
    mtu: int = 0            # mtu: 0 when the port is not configured


class FileNodeStatus(BaseModel):
    """One entry of `fileServiceSummary`: the file service on one controller node."""

    node: int               # nodeNum
    status: str             # fileserviceStatus: NODE_RUNNING, or "stopped" when the service is off
    ports: list[FilePortStatus] = Field(default_factory=list)   # portStatus, in the array's order


class FileCapacity(BaseModel):
    """`capacitySummary`, in MiB: on D22U27 `usedCapacity` is the sum of the file systems'
    `vvSizeInMiB`. OS 10.5.0 sends only the first three fields; 10.6.0 sends all six."""

    total: int                          # totalCapacity
    used: int                           # usedCapacity
    available: int                      # availableCapacity
    limit_percentage: int | None = None  # limitPercentage
    file_systems: int | None = None      # numberOfFileSystems
    file_shares: int | None = None       # numberOfFileShares


class FileService(BaseModel):
    """The one member of `GET /api/v3/fileservice`: the array's file service, present (and stopped)
    even on an array with no File ports."""

    uid: str                            # uid, also the members key
    enabled: bool                       # isFileServiceEnabled
    name: str = ""                      # displayname.default: "File Service on <system WWN>"
    system_wwn: str = ""                # systemWWN
    domain: str = ""                    # domain: "" when the service is in no domain
    ransomware_check: bool | None = None  # enabledRansomwareCheck (10.6.0 only)
    nodes: list[FileNodeStatus] = Field(default_factory=list)  # fileServiceSummary
    capacity: FileCapacity | None = None                        # capacitySummary

    @property
    def running(self) -> bool:
        """On, with at least one node, and every node running."""
        return self.enabled and bool(self.nodes) and all(n.status == NODE_RUNNING for n in self.nodes)


class ClientRule(BaseModel):
    """One entry of a client group's `clientInfo`: who may mount, and how."""

    address: str            # ipaddress: an address, a subnet, or "*" for any client
    access: str             # access: "rw" | "ro"
    options: str = ""       # options, as the array prints them ("root_squash" on D22U27)


class FileSystemRecord(BaseModel):
    """One member of `GET /api/v3/filesystems`."""

    uid: str                            # uid, also the members key
    id: int | None = None               # id
    name: str                           # name
    state: str                          # state: "STATE_NORMAL"
    size_mib: int                       # sizeInMiB: the usable size
    vv_size_mib: int | None = None      # vvSizeInMiB: the volume under it (128 MiB more on D22U27)
    reduce: bool                        # reduce: data reduction (prov "tdvv"), else prov "tpvv"
    prov: str = ""                      # prov
    share_count: int                    # sharecount
    owner_node: int                     # fsmaster
    volumes: list[str] = Field(default_factory=list)   # volumemembers[].vvname: the VV under it


class ClientGroup(BaseModel):
    """One member of `GET /api/v3/filesharesettings`: the array's *file share setting*, the list of
    clients that may mount a share."""

    uid: str                            # uid, also the members key
    id: int | None = None               # id
    name: str                           # name
    state: str                          # state
    clients: list[ClientRule] = Field(default_factory=list)   # clientInfo
    host_count: int | None = None       # hostCount
    share_count: int | None = None      # sharecount


class FileShareRecord(BaseModel):
    """One member of `GET /api/v3/fileshares`. Its clients are its client group's: the record
    repeats them, and the group is the one source read (lesson 41)."""

    uid: str                            # uid, also the members key
    id: int | None = None               # id
    name: str                           # name
    state: str                          # state
    file_system: str                    # filesystem.name
    client_group: str                   # sharesettings.name
    mount_path: str                     # mountpath: "/file/<file system>/<share>"
    protocols: list[str] = Field(default_factory=list)   # protocol: ["NFS"]
    host_ip: str = ""                   # hostip: the File port address the share is served on


class FileReport(BaseModel):
    """SPEC-028 R1: the file side of the run's own array, read over its WSAPI v3 (Discovery's
    `DiscoveryReport.file`; the as-built and Verify read it again when they run).

    The File ports are not in here. They are read once, from `showport -file`, and kept where
    Discovery has always kept them (`DiscoveryReport.file_ports`, lesson 41: one source per fact).
    That also keeps this module free of `domain/discovery.py`, which imports it.

    `service` is None when the file API was not read, did not answer, turned the session down, or
    named another array; `notes` then says which, in SPEC-028 R2's sentence. Nothing read from
    another array is kept: the records are empty whenever the serials disagree."""

    os_version: str = ""                # showversion "Release version"
    array_serial: str = ""              # the serial showsys prints; every collection named it
    service: FileService | None = None  # GET /api/v3/fileservice
    file_systems: list[FileSystemRecord] = Field(default_factory=list)   # GET /api/v3/filesystems
    client_groups: list[ClientGroup] = Field(default_factory=list)       # GET /api/v3/filesharesettings
    shares: list[FileShareRecord] = Field(default_factory=list)          # GET /api/v3/fileshares
    notes: list[str] = Field(default_factory=list)                       # R2, one sentence each

    def clients_of(self, share: FileShareRecord) -> list[ClientRule]:
        """A share's clients, read from its client group by name. The share record repeats them;
        the group is the one source (lesson 41). [] when the group is not in the read."""
        group = next((g for g in self.client_groups if g.name == share.client_group), None)
        return list(group.clients) if group else []
