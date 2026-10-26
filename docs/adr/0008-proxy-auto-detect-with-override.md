# The tool detects the environment's proxy (like the browser); it never hardcodes one

Every outbound call the tool makes (GreenLake REST, the connectivity pre-check, the launched DSCC/
cloudinit browser) must go through **whatever proxy the environment uses** — HPE's `hpeproxy.its…`,
a customer's Squid, or none. The tool **auto-detects the system proxy the way the browser does**, with
a **manual override** when detection is wrong/absent, and a **derived on-prem bypass** so array/vCenter
traffic is never tunnelled. **No proxy host is ever hardcoded.**

**Why this ADR.** Today the tool reads the proxy from **one place — the `HTTPS_PROXY` env var** — and
the connectivity check does a raw direct `open_connection`. On a proxy-only network (confirmed live:
direct = timeout, proxy `CONNECT` = `200`), that shows every HPE endpoint as blocked and GreenLake
fails, unless someone manually ran `setx HTTPS_PROXY`. The browser works because it resolves the
**system proxy (WinINET static + PAC/WPAD)**; the tool never did.

## Design

### 1. A `ProxyResolver` (backend) — effective proxy for a destination URL
Precedence, highest first:
1. **Manual override** — operator-entered `host:port` (optionally `user:pass@host:port`), stored in
   `.env` (`ALLETRA_PROXY`). Wins when set. This is the escape hatch when auto-detect is wrong/absent.
2. **Auto-detect the OS system proxy, per-URL** (Windows — the packaged target):
   - **Static** — WinINET `ProxyServer` / `ProxyOverride` via `urllib.request.getproxies_registry()`.
   - **PAC / WPAD** — `WinHttpGetProxyForUrl` via **ctypes → WinHTTP** (auto-detect WPAD *and* evaluate
     the WinINET `AutoConfigURL` PAC), per URL — exactly what the browser/.NET `GetSystemWebProxy` does.
     Native, **no new dependency**, no PyInstaller bloat.
   - **Env** — `HTTPS_PROXY`/`HTTP_PROXY` as a lower-priority input.
3. **None** → direct.

Returns `None` (direct) or a proxy URL. Non-Windows or nothing detected → env → direct, gracefully.
Resolution is per destination host (PAC can differ per URL) and cached within a run.

### 2. Bypass (`NO_PROXY`) — **derived, not hardcoded**
`{ localhost, 127.0.0.1, 169.254.* }` (link-local cloudinit) **plus the on-prem device IPs from the
run** — array mgmt IP, vCenter, both switches (from the Initialisation/Provisioning sheet) — **plus**
any operator-added subnets. On-prem targets are reached directly and must never tunnel out. (Today
only the array is bypassed, ad hoc; this makes the bypass a first-class, derived set.)

### 3. Apply the effective proxy uniformly
- **Connectivity pre-check** → proxy-aware: resolve per host; if a proxy applies, test it with an HTTP
  `CONNECT` tunnel (like the diagnostic that confirmed this); else direct. Report the path taken.
- **GreenLake httpx client** → pass `proxy=<resolved>` (resolved for `gl_base_url`); stop relying on
  `trust_env` alone.
- **Launched browser** → `--proxy-server=<resolved>` + `--proxy-bypass-list=<derived bypass>`.
- **WSAPI / array SSH** → the array is in the bypass set (unchanged behaviour, now derived).

### 4. UI (Prerequisites step)
Show the **detected** proxy ("Using system proxy `hpeproxy…:8080` (auto-detected)" / "No proxy —
direct"), an **editable manual-override** field, and **Re-test**. The connectivity table uses the
effective proxy, so a proxy-only site turns green.

### 5. Proxy authentication (407)
The live HPE proxy accepted an **anonymous `CONNECT`** (the diagnostic got `200` with no credentials),
so no auth is needed there. For proxies that return **407**, v1 surfaces "proxy requires
authentication" and accepts `user:pass@host:port` in the manual field (Basic). Integrated
Kerberos/NTLM (what the browser does transparently) is a **later enhancement**, noted not built.

## Considered options
- **Hardcode HPE's proxy** — rejected outright: breaks at every customer; the mistake this ADR exists to prevent.
- **Manual field only** — rejected as the default: works but forces every operator to know + type the
  proxy; auto-detect is what makes it "just work" like the browser. Kept as the override layer.
- **Status quo (`HTTPS_PROXY` env only)** — rejected: the current bug; nothing auto-detects it.
- **Add `pypac` for PAC** — rejected in favour of native ctypes/WinHTTP: no dependency, no packaging risk.

## Consequences
- One `ProxyResolver` is the single source of the effective proxy; nothing else reads `HTTPS_PROXY`
  directly. No proxy host is hardcoded anywhere.
- PAC/WPAD support is Windows-only (via WinHTTP) — fine, the packaged app is Windows-only; other OSes
  fall back to env → direct.
- The connectivity pre-check finally reflects reality (tests the path the tool will actually use).
- Related hardcoded-assumption audit items (region default, fabric-by-parity, VMware persona, bypass
  scope) are tracked separately — this ADR fixes the proxy one.

### Pitfall found in the field (fixed v0.9.1)

The WinHTTP proxy structs (`WINHTTP_CURRENT_USER_IE_PROXY_CONFIG`, `WINHTTP_PROXY_INFO`) return
strings that WinHTTP allocates and the caller must `GlobalFree`. Declaring those fields as `LPWSTR`
made ctypes **auto-convert them to a Python `str` on access**, losing the original pointer — and
`ctypes.cast(<that str>, c_void_p)` returns a pointer *into the Python object*, so `GlobalFree` then
corrupted the process heap (**STATUS_HEAP_CORRUPTION / 0xC0000374**). It only manifested on a machine
that actually **had a system proxy** (so the out-strings were non-null), which is why every unit test
and CI selftest passed while the packaged app hard-crashed at launch on the proxied customer box (the
serve path runs `apply_proxy_env()` before uvicorn prints — hence a black console, then the crash).
Rule: **WinHTTP out-strings are held as raw `c_void_p`**, read with `wstring_at`, and `GlobalFree`'d
by their real address — never as `LPWSTR`. Guarded by a struct-field regression test.
