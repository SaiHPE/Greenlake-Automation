# Research — Status and performance report at handover (SCOPE area 8, BL-24)

**Date:** 2026-11-16 · **Status:** research; decision proposed in [ADR 0019](../adr/0019-handover-report-from-the-array.md),
requirements in [SPEC-026](../specs/SPEC-026-handover-status-and-performance.md), build brief in
[workpackets/BL-24.md](../workpackets/BL-24.md)
**Question:** after deployment, what status and performance report should the tool hand to the field
engineer and the customer, and where should it read it from?
**Sources:** the offline GreenLake API mirror (`reference/greenlake_api_docs/greenlake/`, scraped
2026-06-07), the tool's code at `b7006373`, the live captures in `tests/fixtures/`, the installed
`python-3parclient` 4.5, and four public pages read 2026-11-16 (§7). No array, switch, vCenter or
GreenLake call was made for this note.

## 1. What the tool already reports

| Read | Where | What it gives today |
|---|---|---|
| `checkhealth -svc -detail` | Verify (status table, SPEC-011) and as-built (two tables) | the array's own component check, summary and detail rows |
| `showinventory -csvtable`, `shownode`, `showcage`, `showpd` | as-built | hardware inventory, drive count, raw capacity |
| `showcpg`, `showsys -d`, `showversion` | as-built Table 01 | capacity per CPG, identity, OS |
| `showrcopy` (+ `checkrclink`) | Replication, as-built | link state, group state, last sync, link latency |

Not read today: **alerts** (`showalert` is not on the allowlist), **any performance counter**, and
anything from DSCC beyond the onboarding wizard. SCOPE area 8 marks *health and performance
reporting* not started.

LESSONS 24 matters here: on a lab array `checkhealth` listed twelve failed drives that `showpd`
showed normal; `showalert -d` settled it by its timestamps (four days old, repaired, never cleared).
An alert list without timestamps misleads; a handover report must carry them.

## 2. The four candidate sources

### 2.1 The array itself, over the read-only SSH client (System Reporter CLI)

- **What it gives.** `showalert` (alerts with state, severity, time, message). System Reporter
  (`srstat*` commands) keeps history on the array: 5-minute samples (`-hires`, kept 12 h by default
  in a report), hourly and daily, with `-summary min,avg,max,<N>%` and `-btsecs`/`-etsecs` windows.
  **Confirmed on Alletra MP OS 10.5.0**: `srstatrcvv -hourly` and `help srstatrcvv` were captured
  live on AlletraMP_D22U27 (`tests/fixtures/rc_pair/D22U27/srstatrcvv_hourly.txt`,
  `tests/fixtures/rc_pair/help/help_srstatrcvv.txt`): the options above, "AUTHORITY: Any role in
  the system", and a report that ends normally (it does not stream). The other report commands
  (`srstatcpu`, `srstatport`, `srstatvv`, `srstatpd`) follow the same family on 3PAR and Primera;
  **their presence and columns on 10.5.0 are unconfirmed** until `help` and one run of each are
  captured.
- **Auth.** The run's one array credential (ADR 0013). Nothing new to ask the operator.
- **Rate limits.** None; each report is one SSH command. `checkhealth` already takes ~30 s; a
  24-hour hires summary is expected to be faster (unconfirmed, time it in the capture).
- **Right after onboarding.** System Reporter records from the moment the array runs, so there is
  history from initialization onwards. The capture shows the catch: a lab array with no workload
  reports `0.0` in every column for a full day. At handover the array usually carries no host I/O
  yet, so the figures are an **idle baseline**, not a measure of what the array can do. The report
  must say so in words.
- **Offline / jump box.** Works with no internet: the jump box sits next to the array.
- **Read-only (rule 3).** `showalert` is a `show` command. `srstat*` commands only query the
  System Reporter database; the writes in that family have other names (`setsr`, `startsr`,
  `stopsr`, `createsralertcrit`, `removesralertcrit`, `setsralertcrit`), which an exact base-name
  allowlist never matches. `stat*` live samplers (`statvv`, `statport`, `statcpu`) are **not**
  proposed: without `-iter` they never end, which the current `run()` would turn into a hang.

### 2.2 The array's WSAPI (System Reporter over REST, onboard exporter)

- `python-3parclient` reaches System Reporter over WSAPI at
  `systemreporter/vstime/cpgstatistics/<hourly|daily>` (`client.py`, `getCPGStatData`). Whether
  WSAPI 1.15 on Alletra MP serves `/systemreporter/*` is **unconfirmed** (the BL-38 WSAPI capture
  did not ask). Trap: `getCPGStatData` catches every exception and returns all zeros, so a failed
  read looks like an idle array. LESSONS 29 says read the SDK function before depending on it; this
  one must not be used.
- The B10000 has an **onboard Prometheus exporter** from release 10.4 (hpe-storage.github.io,
  §7): HTTPS on 443, path `/metrics`, basic auth, "enabled by a storage administrator in the array
  UI", scraped no more often than every 30 s, gauges per disk, port, QoS, VLUN and volume (IOPS,
  bytes/s, latency), **no capacity metrics**. It gives the current rate only, no history, and it is
  off unless someone turns it on. Turning it on is a configuration change the tool will not make
  (rule 3). Useful later as an extra source when the customer has enabled it.

### 2.3 DSCC / Data Ops Manager REST APIs (GreenLake regional endpoints)

From the mirror (all `v1alpha1`, first published 2026-01/02 per the Storage Fleet changelog):

| Need | Endpoint (B10000 = `devtype4`) | Fields that matter |
|---|---|---|
| Overall state | `GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}` | `overallState` (`NORMAL`, `DEGRADED`), `overallStateDescription` ("Degraded Resources: disks, nodes"), `commonResourceAttributes.cloudState` (`CONNECTED`), `onlineNodes`, `softwareVersions` |
| Call-home to HPE | `GET …/devtype4-storage-systems/{systemId}/telemetry` | `connectivityStatus`, `rolledUpStatus`, `transferStatus`, `lastFileTransferTime`, `lastSuccessfulConnectivityTestTime` (each `NORMAL`/`FAILED`/`DISABLED`/`NOT_APPLICABLE`) |
| Performance now | `GET …/{systemId}/performance-statistics` | `iops`, `latency`, `throughput`, each `avgOfLatest`, `avgOf1hour`, `avgOf8hours`, `avgOf1day` |
| CPU and cache | `GET …/{systemId}/component-performance-statistics` | `cpuPercentage`, `cachePercentage` with the same four averages |
| Performance history | `GET …/{systemId}/performance-history?range=startTime eq … and endTime eq …&time-interval-min=5\|60\|1440\|10080` | `historyData.iopsMetricsData`, `latencyMetricsDataMs`, `throughputMetricsDataKbps`, `ioszMetricsData`, `qlenMetricsData`; **the series' inner shape is not documented** |
| Capacity | `GET …/{systemId}/capacity-summary`, `…/capacity-history` (1440 or 10080 min) | `capacitySummary.free`, `failed`, data reduction, dedup and compression ratios |
| Port, drive, node, Remote Copy link figures | `…/{systemId}/ports-performance`, `…/{systemId}/physicaldrives-performance`, `…/{systemId}/nodes/{nodeId}/component-performance-statistics`, `…/{systemId}/remotecopylinks-performance` | per component |
| Analytics | `GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hotspots`, `headroom-contribution`, `latency-factors`, `resource-contention`, `capacity-forecast`, `capacity-timeuntilfull`; per volume `performance-history`, `performance-drifts`, `performance-histogram` | forecasts and contention |
| Alerts (DSCC issues) | `GET /data-services/v1beta1/issues` | active issues (`state = "CREATED"`): `severity`, `name`, `body`, `recommendation`, `lastOccurredAt`, `occurrenceCount`, `relatedResources`, `sourceResourceId` |

- **Auth.** OAuth2 client credentials, the same kind of personal API client the tool already uses
  for onboarding: a client made for "HPE GreenLake Cloud Platform" reaches "Data Services" APIs
  (authentication guide). The token inherits the **user's** permissions; these reads need
  `storage-fleet.storage-system.read`, `storage-fleet.system-settings.read` (telemetry is under
  system settings) and `data-services.issue.read`. Whether the onboarding user holds them is the
  workspace-entitlement question SCOPE already lists as a gatekeeper. **Unconfirmed** for our
  workspace.
- **Base URL.** Regional, not global: `https://{us-west|eu-west|eu-central|ap-northeast}.api.greenlake.hpe.com`.
  These names match the GreenLake region ids the onboarding step already gets from the service
  catalog, so the host can be built from the run's region. A Verify-only run has no region today.
- **System id.** The list describes `id` as "SystemWWN/UUID string" but its example is
  serial-shaped (`7CE751P312`), and the list carries `manufacturing.serialNumber` (filterable) and
  `systemWwn`. Which one a B10000's `systemId` is, is **unconfirmed**; list
  `devtype4-storage-systems`, match on `manufacturing.serialNumber`, and use the `id` it returns.
- **Rate limits.** Per API client; a `429` with `ratelimit-limit`, `ratelimit-remaining`,
  `rateLimit-reset` headers (rate-limiting guide). No per-endpoint numbers are published (the guide's
  `100` is an example). The tool's token buckets cover this with a new `storage_fleet_read` family.
- **Right after onboarding.** DSCC can only hold data from the moment the array first connected,
  and `commonResourceAttributes.errMessage` shows DSCC may stop monitoring a system. How long after
  *Set Up System* the performance and capacity series fill is **unconfirmed** (no published lag).
  Capacity history is daily at its finest. At handover, DSCC history is likely empty or a few
  hours long.
- **Offline / jump box.** Needs the jump box to reach the regional host through the proxy (ADR
  0008); the regional host is not on the tool's firewall list today.
- **Read-only (rule 3).** All the calls above are `GET`. The same families carry writes (system
  settings `PUT`, locate `POST`), so a client must expose GETs only.

### 2.4 InfoSight

- No public InfoSight API was found for storage arrays. The HPE Developer platforms page (read
  2026-11-16) lists HPE Alletra, Alletra Storage MP B10000 and X10000, 3PAR and Primera, and Nimble,
  but no InfoSight entry; the GreenLake API catalog (mirror) has no InfoSight service. The InfoSight
  portal is a sign-in web application.
- For the B10000, the analytics HPE describes as InfoSight-style (hotspots, headroom, latency
  factors, contention, forecasts) appear as DSCC Block Storage endpoints (§2.3). *Inference, not a
  quoted statement*: InfoSight for this array is reached through DSCC, not through its own API.
- GreenLake **Wellness** (`GET https://global.api.greenlake.hpe.com/wellness/v2/events`,
  permission `ccs.wellness-dashboard.view`) returns wellness events with `asset.serialNumber`,
  `condition.severity` (`critical`, `warning`, `notice`) and `causes.recommendation`. Its glossary
  names Alletra 9000/6000/5000 as products; **whether B10000 events appear there is unconfirmed**.
- Verdict: InfoSight is not a source for the tool today. Revisit if HPE publishes an API.

## 3. Comparison

| | Array SSH (System Reporter) | Array WSAPI / onboard exporter | DSCC REST | InfoSight |
|---|---|---|---|---|
| Alerts | `showalert`, with timestamps | not looked at | `issues` (DSCC's view) | none |
| Performance history | yes, since the array started | WSAPI SR unconfirmed; exporter has none | yes, since it connected; shape partly undocumented | none |
| Call-home / cloud state | no | no | yes (`telemetry`, `cloudState`) | none |
| New credential or permission | none | none (exporter: must be enabled) | Data Services read roles, regional host, region | n/a |
| Works with no internet | yes | yes | no | no |
| Live-proven on our arrays | `srstatrcvv` captured on 10.5.0 | no | no call ever made | n/a |
| Read-only guarantee | the allowlist, by base name | GETs | GETs, same families carry writes | n/a |

## 4. What a handover report should contain

What a field engineer hands over is evidence that the array is in a clean state and a reference
point for later. From the sources the tool can trust today:

1. **Status at handover**: when it was read; the array's `checkhealth` result (already in the
   document); **open alerts** with severity, time and message, and which of them are older than the
   run; a single sentence verdict (*no open alerts* / *N open alerts, the oldest from …*).
2. **Capacity at handover**: total, used and free, and data reduction where the array reports it.
3. **Performance baseline**: over the last 24 hours (or since the array started, if less), per
   controller node CPU, per host port IOPS, throughput and service time, and the whole array's
   volume IOPS and latency, each as average, 95th percentile and maximum. With a sentence that the
   array carried no host workload when it was read, when the IOPS are near zero.
4. **Remote Copy** (only when the run replicated): `srstatrcvv` per group, local and remote service
   time and RPO, next to SPEC-020's link latency.
5. **What HPE's cloud sees** (later slice): DSCC's overall state, cloud connection and call-home
   status. This is the one item the array cannot say for itself and that support depends on.

## 5. Recommendation

**First slice: read it from the array, over the read-only SSH client, inside the as-built step.**
Add `showalert` and four `srstat*` report commands to the read allowlist (said plainly, with tests),
and a new as-built section *Array status and performance at handover* after the `checkhealth`
section. The As-built step page shows a short *Status at handover* summary from the same read. No
new step and no registry change: the as-built step already runs last in every mode, already reads the
array, and the document is the deliverable. Verify configuration is unchanged in slice 1 (its
*Array status* table stays the place to act on `checkhealth`).

Why not DSCC first: it needs permissions nobody has confirmed for our client, a region the
Verify-only mode does not have, a regional host outside the firewall list, a series shape the
docs leave open, and it has less history than the array at handover. It is the right second slice
for the one thing only the cloud knows (cloud connection and call-home), once one read-only probe
on the lab workspace has answered the open questions in §6.

## 6. Open questions for the owner

1. Do the onboarding API client's user roles include Data Services read
   (`storage-fleet.storage-system.read`, `storage-fleet.system-settings.read`,
   `data-services.issue.read`)? One read-only `GET devtype4-storage-systems` on the lab workspace
   answers it (needs your go-ahead).
2. Baseline window: 24 hours before the as-built (proposed), or from the start of the run?
3. Should open alerts of severity *Major* or worse raise an as-built warning (proposed: yes, a
   warning, never a block), or only be listed?
4. Should the tool tell the operator how to acknowledge or clear old alerts (`setalert`, `removealert`)
   as text to copy, never run (proposed: name the commands, the tool runs neither)?
5. Is a later *re-run with workload* in scope (the same report a few days after go-live, as a
   Verify-only run)? It would make the performance part meaningful.

## 7. Public pages read (2026-11-16)

- HPE Developer, platforms: <https://developer.hpe.com/platforms> (no InfoSight entry).
- HPE Developer, Data Services Cloud Console: <https://developer.hpe.com/greenlake/data-services-cloud-console/home/>
  (public REST API, OAuth through GreenLake; no rate limits or telemetry detail on the page).
- HPE Storage Array Exporter for Prometheus: <https://hpe-storage.github.io/array-exporter/>
  ("The B10000 platform from release 10.4 has its own onboard exporter").
- Onboard exporter: <https://hpe-storage.github.io/array-exporter/onboard/> (HTTPS 443 `/metrics`,
  basic auth, enabled in the array UI, 30 s throttle, "does not provide any capacity metrics").
- Offline mirror (scraped 2026-06-07): `services/storage-fleet/public.md`,
  `services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-systems/devicetype4*.md`,
  `…/system-settings/devicetype4telemetryget.md`, `services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/*`,
  `services/data-services/public.md` and `…/issues/listissues.md`, `services/wellness/public.md`
  and `…/events/getallevents.md`, `guides/public/authentication/authentication.md`,
  `guides/public/rate-limiting/rate-limiting.md`.
