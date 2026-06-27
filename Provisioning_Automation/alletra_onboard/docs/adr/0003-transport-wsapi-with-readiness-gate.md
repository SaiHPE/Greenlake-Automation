# Provisioning transport: WSAPI primary, behind a readiness gate; SSH for the gaps

Storage provisioning (host / volume / LUN / snapshot / replication) is driven through the array's
**WSAPI (`/api/v1`)** — for both the create operations and the structured reads that back them. WSAPI
is gated by a **readiness check**: before any write, a cheap `GET /system`; if it returns `503`
(`code 68 "system services required for operation are not ready"`) or times out, the tool **stops
with a clear operator message** ("the array's WSAPI isn't ready — check `checkhealth` and retry")
rather than half-completing a run. **SSH stays first-class** for the things WSAPI can't do or for when
WSAPI is down: the fabric nameserver / zoning verification (`showportdev ns`), the read-only config +
health verification we already ship, and discovery/diagnostics on any array.

## Evidence (two live arrays, same OS 10.5.51 / WSAPI 1.15.0)

- **LZ array (`10.64.154.225`), degraded** — critical over-temperature, degraded cage, iLO warnings,
  `showwsapi -d` System Resource Usage 96. WSAPI `showwsapi` = Active, port 443 reachable, but auth
  returned `503 code 68` and then hung. Restarting WSAPI did not help — the backing services
  (System Manager) couldn't reach "ready."
- **VZ array (`10.64.122.140`), healthy** — WSAPI auth OK; `system / cpgs / volumes / volumesets /
  hosts / hostsets / vluns / ports / remotecopygroups / remotecopytargets / tasks` all returned 200
  with full JSON. Identical software to LZ.

So WSAPI viability tracks **array health, not configuration** — which makes the readiness gate
mandatory, not optional.

## Considered options

- **SSH-only (reads + writes)** — rejected as the default: the create commands are interactive
  (e.g. `createvlun` confirmation prompts) and their text needs parsing; WSAPI is prompt-free and
  returns structured objects + idempotency codes. (SSH writes remain a possible fallback.)
- **WSAPI-only, no gate** — rejected: degraded/initialising arrays exist (the LZ array proves it),
  and a run that hangs mid-provision is worse than one that refuses up front.
- **WSAPI primary + readiness gate + SSH for the gaps** — chosen.

## Consequences

- Adds **`python-3parclient >= 4.2.14`** (wraps WSAPI auth/sessions/version quirks) as the write-path
  client. **The `>= 4.2.14` floor is mandatory for the Alletra MP** (verified 2026-06-26): earlier
  releases POST to `/credentials` instead of `/api/v1/credentials` and fail to authenticate to the
  B10000 (Launchpad bug #2128677). The SDK officially supports firmware 10.4.0+ (our 10.5.51 is in).
  Call create methods with **keyword args** — the SDK signature has drifted (`createHost` gained `nqn`).
- Idempotency reasons the write path must catch as warnings: **`EXISTENT_HOST`** (host), **`EXISTENT_SV`**
  ("Volume Exists already" — *not* `EXISTENT_VV`), **`EXISTENT_VLUN`** (export), **`EXISTENT_PATH`** (a
  WWN already belongs to another host). Use `findHost(wwn=...)` for lookup-before-create.
- A **readiness preflight** wraps the client; the existing **health check (`checkhealth`)** becomes a
  natural pre-provisioning gate — a degraded array is surfaced before any write is attempted.
- **SSH is not removed**: zoning verification (`showportdev ns`), config/health verification, and
  all discovery stay on SSH; it is also the fallback to *read/report* when WSAPI is unavailable.
- WSAPI object shapes are version-stable JSON, so the discovery/parse logic for the write path is
  not calibration-sensitive the way `show*` text is (see ADR 0002).
- The healthy VZ array (`10.64.122.140`) is a clean WSAPI write-test target (no hosts/vluns, CPG
  `SSD_r6`, ~29 TiB free) — coordinate writes with Panduranga and clean up after.
