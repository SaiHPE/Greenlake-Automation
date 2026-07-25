"""Parse the read-only ``asbuilt_array.py`` dump (``show*`` + ``checkhealth``) into ``AsBuiltData``.

Calibrated against a live HPE Alletra MP B10000 (OS 10.5.51) dump. The dump is a sequence of
``===== $ <cmd> =====`` blocks; ``split_sections`` splits it, then per-field extractors read the
relevant block. Extractors use ``str.split()`` (whitespace-agnostic) so they tolerate column spacing.
"""

from __future__ import annotations

import re

from alletra_onboard.application.asbuilt import AsBuiltData

_NSP = re.compile(r"^\d+:\d+:\d+$")
_IPV4 = re.compile(r"^\d+\.\d+\.\d+\.\d+$")


def split_sections(dump: str) -> dict[str, str]:
    """Split the dump into {command: output} on its ``===== $ <cmd> =====`` markers."""
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in (dump or "").splitlines():
        m = re.match(r"^=+\s*\$\s*(.+?)\s*=+\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip("\n")
            current, buf = m.group(1).strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip("\n")
    return sections


def _kv(text: str, key: str) -> str:
    """Value of a ``Key : Value`` line (first match where the line starts with ``key``)."""
    for line in text.splitlines():
        if line.strip().startswith(key) and ":" in line:
            return line.split(":", 1)[1].strip()
    return ""


def _net(sec: dict[str, str]) -> dict[str, str]:
    net = sec.get("shownet", "")
    ip = mask = ""
    for line in net.splitlines():
        p = line.split()
        if p and _IPV4.match(p[0]):
            ip, mask = p[0], (p[1] if len(p) > 1 else "")
            break
    return {
        "ip": ip,
        "mask": mask,
        "gateway": _kv(net, "Default IPv4 route"),
        "ntp": _kv(net, "NTP server"),
        "dns": ", ".join(_kv(net, "DNS server").split()),
    }


def _cache(sec: dict[str, str]) -> str:
    total = 0
    for line in sec.get("shownode", "").splitlines():
        p = line.split()
        if len(p) >= 6 and p[0].isdigit():
            try:
                total += int(p[5])  # Mem(MiB) column
            except ValueError:
                pass
    return f"{round(total / 1024)} GiB (node memory, all nodes)" if total else ""


def _cages(sec: dict[str, str]) -> str:
    names = [p[1] for line in sec.get("showcage", "").splitlines()
             if (p := line.split()) and len(p) >= 2 and p[0].isdigit() and p[1] != "total"]
    return f"{len(names)} ({', '.join(names)})" if names else ""


def _disks(sec: dict[str, str]) -> str:
    count, cap = 0, ""
    for line in sec.get("showpd", "").splitlines():
        p = line.split()
        if len(p) >= 3 and p[0].isdigit() and p[1] != "total" and p[2] == "SSD":
            count += 1
            cap = p[-1]  # Capacity(GB)
    if not count:
        return ""
    size = f"{int(cap) / 1000:.2f} TB" if cap.isdigit() else (f"{cap} GB" if cap else "")
    return f"{count} x {size} NVMe SSD".replace("  ", " ").strip()


def _raw_capacity(sec: dict[str, str]) -> str:
    lines = sec.get("showsys -d", "").splitlines()
    for i, line in enumerate(lines):
        if "Raw System Capacity" in line:
            for follow in lines[i:i + 6]:
                if "Total Capacity" in follow and ":" in follow:
                    mib = follow.split(":", 1)[1].strip()
                    if mib.isdigit():
                        return f"{int(mib) / 1024 / 1024:.1f} TiB ({int(mib):,} MiB)"
    return ""


def _raid(sec: dict[str, str]) -> str:
    out = []
    for line in sec.get("showcpg", "").splitlines():
        p = line.split()
        if len(p) >= 2 and p[0].isdigit() and p[1] != "total":
            m = re.search(r"_r(\d+)", p[1], re.I)
            out.append(f"RAID {m.group(1)} ({p[1]})" if m else p[1])
    return "; ".join(out)


def _host_ports(sec: dict[str, str]) -> str:
    fc = []
    for line in sec.get("showport", "").splitlines():
        p = line.split()
        if len(p) >= 7 and _NSP.match(p[0]) and p[1] == "target" and p[6] == "FC":
            fc.append((p[0], p[2]))
    if not fc:
        return ""
    speed = ""
    m = re.search(r"(\d+Gbps)", sec.get("showport -par", ""))
    if m:
        speed = m.group(1)
    ready = [nsp for nsp, st in fc if st == "ready"]
    other = [nsp for nsp, st in fc if st != "ready"]
    parts = [f"{len(fc)} x {speed or 'FC'} FC target"]
    if ready:
        parts.append(f"ready: {', '.join(ready)}")
    if other:
        parts.append(f"not-ready: {', '.join(other)}")
    return "; ".join(parts)


def _os_version(sec: dict[str, str]) -> str:
    m = re.search(r"Release version\s+(\S+)", sec.get("showversion", ""))
    return m.group(1) if m else ""


def parse_checkhealth(text: str) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str, str]]]:
    """Split `checkhealth -svc -detail` into two tables for the doc:
    summary rows (Component, Description, Qty) and detail rows (Component, Identifier, Description,
    Resolution). Anchored on the two header lines; the last token of a detail row is the Resolution,
    the first two are Component + single-token Identifier."""
    summary: list[tuple[str, str, str]] = []
    detail: list[tuple[str, str, str, str]] = []
    mode: str | None = None
    for line in (text or "").splitlines():
        if "Summary Description" in line and "Qty" in line:
            mode = "sum"
            continue
        if "Identifier" in line and "Resolution" in line:
            mode = "det"
            continue
        stripped = line.strip()
        if not stripped or set(stripped) <= set("- "):  # blank / separator
            continue
        p = line.split()
        if p[0].isdigit() and "total" in line:          # the "N total M" footer
            mode = None
            continue
        if mode == "sum" and p[-1].isdigit() and not p[0].isdigit():
            summary.append((p[0], " ".join(p[1:-1]), p[-1]))
        elif mode == "det" and len(p) >= 4 and not p[0].isdigit():
            detail.append((p[0], p[1], " ".join(p[2:-1]), p[-1]))
    return summary, detail


def _columns(header: str, data_lines: list[str]) -> tuple[list[str], list[list[str]]]:
    """Slice a fixed-width block by the header's column token positions. The first column is anchored
    at index 0 (so a value left of its right-aligned header — e.g. the array-id row — isn't clipped)."""
    tokens = [m.start() for m in re.finditer(r"\S+", header)]
    if not tokens:
        return [], []
    starts = [0] + tokens[1:]
    ends = tokens[1:] + [None]

    def cut(line: str) -> list[str]:
        return [(line[a:b] if b is not None else line[a:]).strip() for a, b in zip(starts, ends)]

    headers = [h.strip("-").strip() for h in cut(header)]
    rows = [cut(line) for line in data_lines]
    return headers, [r for r in rows if any(c for c in r)]


def parse_inventory(text: str) -> list[tuple[str, list[str], list[list[str]]]]:
    """Split ``showinventory`` into its sub-sections -> [(title, headers, rows)]. A dash-wrapped line
    ("----Midplane----") is a section title; the next block's first line is the column header, the rest
    are data (footer "N total" rows dropped). Each block is sliced fixed-width via ``_columns``."""
    out: list[tuple[str, list[str], list[list[str]]]] = []
    title = ""
    block: list[str] = []

    def flush() -> None:
        nonlocal block
        data = [ln for ln in block[1:] if ln.strip() and not re.match(r"^\s*\d+\s+total", ln)]
        if block and data:
            headers, rows = _columns(block[0], data)
            if headers and rows:
                out.append((title, headers, rows))
        block = []

    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if stripped.startswith("-"):          # a title ("----Midplane----") or a plain separator
            label = re.split(r"-{2,}", stripped.strip("-"))[0].strip()  # drop trailing dash-runs/units
            if label:
                title = label
            flush()
            continue
        block.append(line)
    flush()
    return out


def parse_asbuilt(dump: str) -> AsBuiltData:
    """Parse a full ``asbuilt_array.py`` dump into ``AsBuiltData`` (inventory + checkhealth verbatim)."""
    sec = split_sections(dump)
    sysd = sec.get("showsys -d", "")
    net = _net(sec)
    return AsBuiltData(
        name=_kv(sysd, "System Name"),
        model=_kv(sysd, "System Model"),
        serial_no=_kv(sysd, "Serial Number"),
        controller_nodes=_kv(sysd, "Number of Nodes"),
        os_version=_os_version(sec),
        drive_cages=_cages(sec),
        cache_gb=_cache(sec),
        nvme_ssd_disks=_disks(sec),
        raw_capacity=_raw_capacity(sec),
        raid=_raid(sec),
        host_ports=_host_ports(sec),
        mgmt_ip=net["ip"],
        netmask=net["mask"],
        gateway=net["gateway"],
        ntp=net["ntp"],
        dns=net["dns"],
        inventory=sec.get("showinventory", ""),
        checkhealth=sec.get("checkhealth -svc -detail", ""),
    )
