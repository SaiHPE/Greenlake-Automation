"""TCP and HTTP-CONNECT reachability probes for outbound HPE cloud endpoints (STANDARD L4)."""

from __future__ import annotations

import asyncio
import socket
from urllib.parse import urlparse


async def probe_tcp(host: str, port: int, timeout: float) -> tuple[bool, str]:
    """Direct TCP connect probe -> (reachable, operator-facing detail)."""
    try:
        future = asyncio.open_connection(host, port)
        _reader, writer = await asyncio.wait_for(future, timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except OSError:  # closing is best-effort
            return True, "reachable"
        return True, "reachable"
    except TimeoutError:
        return False, "timed out - the port is filtered or blocked"
    except socket.gaierror:
        return False, "DNS could not resolve the host"
    except OSError as exc:
        return False, f"blocked ({type(exc).__name__})"


async def probe_via_proxy(host: str, port: int, proxy_url: str, timeout: float) -> tuple[bool, str]:
    """Reachability THROUGH the proxy — an HTTP CONNECT tunnel, exactly how the tool's traffic goes."""
    parsed = urlparse(proxy_url)
    phost, pport = parsed.hostname or "", parsed.port or 8080
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(phost, pport), timeout=timeout)
    except (OSError, TimeoutError, ValueError):
        return False, f"proxy {phost}:{pport} not reachable"
    try:
        writer.write(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".encode())
        await writer.drain()
        line = (await asyncio.wait_for(reader.readline(), timeout=timeout)).decode("latin1", "replace").strip()
        if "407" in line:
            return False, "proxy requires authentication (407)"
        ok = " 200 " in f" {line} " or "200 connection" in line.lower()
        return ok, ("reachable via proxy" if ok else f"proxy said: {line}")
    except (OSError, TimeoutError, ValueError) as exc:
        return False, f"proxy error ({type(exc).__name__})"
    finally:
        writer.close()
