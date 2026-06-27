# Runbook — Provision Alletra MP B10000 storage to VMware ESXi (Fibre Channel)

Present storage from an HPE Alletra MP B10000 to ESXi hosts over FC: **host → volume → export**,
with the **volume-set / host-set** pattern for clusters. Each step lists the **array CLI** command
(the manual runbook) and the **WSAPI `/api/v1`** call / `python-3parclient` method (what the tool
automates). Calibrated against the live Landing-Zone array.

> Sources (HPE official docs, by ID — not committed here): VMware ESXi Implementation Guide
> (`sd00002428`), CLI installation & reference (`sd00002409`), vSphere 8 deployment considerations
> (`a00136180`), WSAPI Developer Guide v1 (`sd00003946`), Remote Copy with the CLI (`sd00002425`);
> plus the `python-3parclient` tutorial.

## This array (verified live, 2026-06-22)

| Thing | Value |
|---|---|
| System | `MPB10K-E24U21-LZ`, mgmt `10.64.154.225`, OS `10.5.51` |
| Admin | `3paradm` (the DSCC System Credential) |
| CPG (pool) | **`SSD_r6`** exists; ~25.6 TiB usable free (`showspace`) |
| WSAPI | **Enabled**, `https://10.64.154.225/api/v1`, **port 443**, v1.15.0 (`showwsapi`) |
| FC target ports | `0:3:1–4` / `1:3:1–4`, WWPNs `…02F629` — currently **`loss_sync`** (not yet cabled/zoned) |
| Protocol / persona | FC, **persona 11 (VMware)** |

## Mental model

```
CPG (pool/recipe) ──► Volume (VV) ──► export (VLUN) ──► Host (WWNs + persona 11)
        every step references a thing that must already exist; sets just batch the joins
VV set ─┘                         └─ host set
```

---

## Prerequisites the tool verifies (design-locked in the provisioning grill)

The customer / SAN team provides these; the tool's preflight **verifies** them and refuses to proceed
if a hard one is missing. It never creates zones or alters the fabric. All reach info comes from the
Initialisation sheet — intent + reach only (ADR 0002).

**Reach (from the sheet):**
- Array mgmt IP + admin credential — SSH (22) and WSAPI (443, proxy-bypassed for the internal IP).
- vCenter IP + credential — the primary host-discovery path.

**Array readiness (transport = WSAPI primary, SSH fallback — ADR 0003):**
- WSAPI enabled **and ready**: `GET /system` returns 200. On 503/timeout, fall back to SSH for
  reads/report and **stop before any write** ("WSAPI not ready — check `checkhealth`, then retry").
- Array health surfaced via `checkhealth`; critical findings and `showwsapi -d` *System Resource
  Usage* **> 90** are **warned** (operator decides) — they don't silently block.
- A **CPG** exists with free capacity (discovered).
- FC **target ports** in `target` mode and `ready` (discovered).

**SAN zoning — the tool discovers, reports, and (on confirm) remediates — ADR 0004:**
- *Physical cabling* (host HBA → switch, array port → switch) is the **customer prerequisite** — the
  tool can't cable; it only zones ports that are cabled and logged into the fabric.
- The tool reads **both Brocade fabrics** (Switch 1 / odd / F1, Switch 2 / even / F2 — IPs+creds from
  the sheet), and **reports** the current zoning vs the best practice (*odd port → odd switch, even →
  even*). On **operator confirmation** it **creates the missing zones** — additive-only:
  `alicreate` → `zonecreate` → `cfgadd` → `cfgenable` → `cfgsave`; it never removes or replaces an
  existing zone/config (the active config is shared production).
- It **re-verifies** with `cfgshow` (zone present) **and** the array `showportdev ns` (the host's WWPNs
  now log in on the target ports). A host with only one visible path is flagged (no redundancy).
- The customer supplies the **HBA** in the sheet, not the ports; the tool discovers the array ports
  (`showport`) and host WWPNs (vCenter) and computes the expected odd/even zoning itself.

**Host side (ESXi for v1; Windows / Linux deferred):**
- ESXi hosts reachable via **vCenter** (primary) or **ESXi SSH** (fallback — *enabling SSH on each
  ESXi host is a stated prerequisite*).
- FC HBAs installed + linked (discovered); persona = **VMware** (confirm via `showhost -listpersona`).

**Inputs (sheet — intent + reach):** array + vCenter creds/IPs; target hosts / cluster; volume spec
(names / sizes / count); CPG (or auto-pick); protocol (FC).

## Phase 0 — Read-only preflight (safe to run any time)

All `show*`; already in the SSH client allowlist. Run before any write.

| Check | Command | Pass condition |
|---|---|---|
| WSAPI up | `showwsapi` | `Enabled / Active`, note the `/api/v1` URL + port |
| Pool exists | `showcpg` | the target CPG (`SSD_r6`) is listed |
| Capacity | `showspace` | `UsableFree` ≥ what you'll provision |
| FC ports live | `showport` | the target FC ports show `ready` (not `loss_sync`) |
| Zoning visible | `showportdev ns <n:s:p>` | the host's WWPNs appear on the target port |
| Existing state | `showhost`, `showvv`, `showvlun -a` | baseline before changes |

If `showport` is `loss_sync` or `showportdev ns` errors → **Phase 1/zoning isn't done yet**; stop.

---

## Phase 1 — SAN zoning + ESXi discovery (substrate; switch + host side)

WSAPI cannot do this part — it's switch and host side. This is the engineer/runbook step.

1. **Cable** host HBA ports ↔ array FC target ports, across **two fabrics** (A/B) for no single
   point of failure.
2. **Collect host WWPNs + OS** ("ESXi discovery"):
   - PowerCLI (best — one vCenter, all hosts):
     ```powershell
     Connect-VIServer <vcenter>          # e.g. CRV-LZ-VC 10.54.154.226
     Get-VMHost | Get-VMHostHBA -Type FibreChannel |
       Select VMHost, Device,
         @{N='WWPN';E={('{0:x}' -f $_.PortWorldWideName) -replace '(..)(?=.)','$1:'}}
     ```
   - or per host over SSH: `esxcli storage san fc list` (Port Name = WWPN, Port State, Speed).
3. **Zone** `{host HBA WWPN, array target WWPN}` on each fabric switch (Brocade `zonecreate`/
   `cfgsave`, Cisco/SN3700B equivalent). Array port WWPN encodes its N:S:P as
   `2<node><slot><port>0002AC<sysid>` (here `…02F629`).
4. **Verify from the array** (read-only): `showport` → ports now `ready`; `showportdev ns <n:s:p>`
   → the host WWPNs are visible. Only then proceed.

Record, per host: name, 2+ WWPNs (dual fabric), ESXi version. (This fills the "Hosts details" sheet.)

---

## Phase 2 — Host creation

Persona **11 = VMware** (required for ESXi; sets ALUA presentation for round-robin multipath).

```
cli% showhost -listpersona                                  # confirm 11 = VMware on this OS
cli% createhost -persona 11 -os "VMware ESXi" LZ-ESXi-01 <wwpn1> <wwpn2>
```
For a cluster, group the hosts into a **host set**:
```
cli% createhostset LZ-Cluster                               # create the set
cli% createhostset -add LZ-Cluster LZ-ESXi-01 LZ-ESXi-02 LZ-ESXi-03
```

**WSAPI / SDK**
- `POST /api/v1/hosts` — `{ "name": "LZ-ESXi-01", "FCWWNs": ["<wwpn1>","<wwpn2>"], "persona": 11,
  "descriptors": { "os": "VMware ESXi" } }` → `createHost()`
- `POST /api/v1/hostsets` — `{ "name": "LZ-Cluster", "setmembers": ["LZ-ESXi-01", ...] }` →
  `createHostSet()`

Verify: `showhost` / `showhost -d` (WWNs listed, persona 11).
Idempotency: an existing host returns `EXISTENT_HOST` → treat as a warning, not a failure.

---

## Phase 3 — Volume creation

On the all-flash B10000, use **`-reduce`** (thin + dedup + compress) for datastores; `-tpvv` is the
thin-only alternative.

```
cli% createvv -reduce SSD_r6 LZ-ds01 2t                     # one 2 TiB reduced volume
cli% createvv -reduce -cnt 4 SSD_r6 LZ-ds.0 2t              # four: LZ-ds.0 .. LZ-ds.3
```
Group them into a **VV set** for one-shot export:
```
cli% createvvset LZ-datastores
cli% createvvset -add LZ-datastores LZ-ds.0 LZ-ds.1 LZ-ds.2 LZ-ds.3
```

**WSAPI / SDK**
- `POST /api/v1/volumes` — `{ "name": "LZ-ds01", "cpg": "SSD_r6", "sizeMiB": 2097152,
  "reduce": true }` → `createVolume()`  *(use `"tpvv": true` instead of `reduce` for thin-only)*
- `POST /api/v1/volumesets` — `{ "name": "LZ-datastores", "setmembers": ["LZ-ds.0", ...] }` →
  `createVolumeSet()`

Verify: `showvv` (Prov = `dds`/`tpvv`, state `normal`).

---

## Phase 4 — Mapping / assignment (the VLUN export)

A VLUN joins a volume (or VV set) to a host (or host set). Four template types, lowest→highest
priority: **port presents** → **host sees** → **host set** → **matched set**.

**Recommended for a cluster** — export the whole VV set to the whole host set, auto LUN IDs
(consistent across all hosts):
```
cli% createvlun set:LZ-datastores auto set:LZ-Cluster
```
Single volume to a single host on an explicit LUN:
```
cli% createvlun LZ-ds01 0 LZ-ESXi-01
```

| Template | CLI shape | Visible to |
|---|---|---|
| host sees | `createvlun <vv> <lun> <host>` | any of that host's WWNs |
| host set | `createvlun <vv\|set:vvset> <lun> set:<hostset>` | all hosts in the set |
| matched set | `createvlun <vv> <lun> <n:s:p> <host>` | host's WWNs **only on that port** |
| port presents | `createvlun <vv> <lun> <n:s:p>` | any initiator on the port |

`<LUN>` accepts `auto` (system-assigned). Use `-f` to force when a VV is already exported.

**WSAPI / SDK**
- `POST /api/v1/vluns` — `{ "volumeName": "LZ-ds01", "hostname": "LZ-ESXi-01", "autoLun": true }`
  (or `"lun": 0`) → `createVLUN()`. For **set-based** matched exports, pass the `set:` names if the
  WSAPI build accepts them, otherwise iterate the set members — confirm against the WSAPI guide
  (`sd00003946`); the CLI `set:`/`set:` form above is the reliable cluster path.

Verify: `showvlun -a`.
Idempotency: re-export of the same VV returns `EXISTENT_VLUN` → warning, not failure.

---

## Phase 5 — Discover + multipath on ESXi

1. **Rescan** so the host sees the new LUN: vSphere *Host → Configure → Storage Adapters → Rescan*,
   or `esxcli storage core adapter rescan --all`.
2. **Multipath = round robin.** ESXi **7.0U3+** ships the correct default
   (`VMW_SATP_ALUA` / `VMW_PSP_RR`) for `3PARdata VV` devices — nothing to do. Older ESXi needs a
   custom SATP rule:
   ```
   esxcli storage nmp satp rule add -s VMW_SATP_ALUA -P VMW_PSP_RR -O iops=1 \
     -c tpgs_on -V 3PARdata -M VV -e "HPE Custom FC ALUA Rule"
   ```
3. **Confirm** the device: `esxcli storage nmp device list` →
   `naa.60002ac…`, `Storage Array Type: VMW_SATP_ALUA`, `Path Selection Policy: VMW_PSP_RR`,
   multiple Working Paths.
4. Create the **VMFS datastore** on the new device.

---

## Phase 6 — Verify (read-only; reuse the SSH verification client)

| Where | Command | Confirms |
|---|---|---|
| Array | `showhost` | host defined, persona 11, all WWNs |
| Array | `showvv` | volumes created in `SSD_r6`, state normal |
| Array | `showvlun -a` | exports present, expected LUN IDs |
| Array | `showportdev ns <n:s:p>` | host still zoned/visible |
| ESXi | `esxcli storage nmp device list` | round-robin ALUA, multiple paths |

---

## Replication (later — out of scope until a target exists)

`showrcopy` on this array = "not configured". Standing up Remote Copy needs a **second array**, **RC
links** (RCIP/RCFC), and a defined **RC target** — none of which WSAPI creates. Once they exist:
`creatercopygroup` → `admitrcopyvv` → `startrcopygroup` (CLI), or the `createRemoteCopyGroup` /
`addVolumeToRemoteCopyGroup` / `startRemoteCopy` WSAPI calls. See `sd00002425`.

---

## Safety posture for the automation (important)

Everything in the tool today is read-only / operator-gated. This runbook is the **first write path**
to production storage, so the provisioning module must:
- **Preflight** with Phase 0 (`show*`) and refuse to write if the substrate isn't ready.
- **Dry-run → preview → confirm** before issuing any create (show exactly what will be created).
- Be **idempotent**: treat `EXISTENT_HOST` / `EXISTENT_SV` / `EXISTENT_VLUN` as warnings (note: the
  volume-exists reason is **`EXISTENT_SV`** "Volume Exists already", *not* `EXISTENT_VV` — verified).
- **Never** issue `removevlun` / `removevv` from the tool — teardown stays manual (see the ESXi guide
  "Removing volumes": detach on ESXi first, then `removevlun`, then `removevv`, then rescan).

## Per-run inputs the tool will need (the parameters this runbook leaves open)

- Protocol: **FC** (this runbook) — vs iSCSI/NVMe (different host-create + discovery).
- Host/cluster: host names + WWPNs (from Phase 1) + cluster (host-set) name.
- Volumes: names, size, count, provisioning (`reduce` vs `tpvv`), CPG (`SSD_r6`), optional VV-set name.
- Export: per-host LUNs vs set-to-set with `auto` LUN.

---

## Calibration notes from the live lab (2026-06-25)

Captured with `scripts/discovery/discover_array.py` (SSH) + `discover_esxi_ssh.py` (esxcli). The LZ
array is **fully provisioned**, which makes it the calibration target for the discovery/verify
parsers — and a real test of the idempotent design.

**Live inventory (steady state):**
- 3 ESXi hosts in host set **`CRVLZ_Hostset`**, persona **VMware (11)**. U26 = Emulex SN1700E
  (`lpfc`), U27 = QLogic SN1700Q (`qlnativefc`); ESXi **8.0 U3** (build 25205845). FC only.
- 4 tpvv volumes in CPG `SSD_r6`: `CRV_LZ_Infra`/`Prod1`/`Test` (10 TiB) + `CRV_LZ_ESXi_Backup`
  (1 TiB), exported to the host set as **LUNs 1–4** over FC target ports `0:3:1/2` + `1:3:1/2`
  (state `ready`; `showportdev ns` confirms each host WWPN per port — zoning verified array-side).
- Replication group **`LZ_RcopyGroup1`** → target **`MPB10K-D24U21-VZ`**, mode **Periodic**, role
  Primary, currently **Stopped** with the RC links **Down** / target `failed`. The `rcpy.*` entries
  in `showvv` are RC internal snapshots.

**Parser facts (use these when building discovery/verify):**
- **`naa` ↔ VV is deterministic:** `naa.60002ac0` `00000000` `000000<VVid>` `<systemID>` — last 8
  hex = array system id (`0002f629` here), the byte before = the VV id. So an ESXi disk maps to its
  array volume with no guessing (e.g. `…000000030002f629` = vv 3 = `CRV_LZ_Infra`).
- **Normalize WWPNs before matching:** ESXi reports colon-separated lowercase
  (`10:00:5c:ed:…`); the array (`showhost`, `showportdev`) is colon-less uppercase (`10005CED…`).
- **`vmhba0` and `vmhba64` are the same physical port** (Second-Level-LUN-ID alias, same WWPN) —
  dedupe by WWPN.
- **Multipath needs no action:** every `3PARdata`/`VV` device is `VMW_SATP_ALUA` + `VMW_PSP_RR`
  (round-robin) by default on ESXi 8.0 U3 — confirming "7.0U3+ default" above; no custom SATP rule.
- **`esxcli` sizes are in MB.**

**Idempotency check (validated by the lab):** because hosts/volumes/VLUNs already exist here,
re-running `createhost`/`createvv`/`createvlun` must detect `EXISTENT_HOST` / `EXISTENT_SV` /
`EXISTENT_VLUN` and report a warning — never fail or duplicate.

---

## Verified build facts (deep research, 2026-06-26 — cited, adversarially checked)

A 106-agent research pass verified the core write path against HPE / Brocade / VMware primary sources
(24 of 25 claims confirmed by 3-vote adversarial check). The confirmations, the **corrections** to our
assumptions, and what stayed unverified:

**SDK / WSAPI transport**
- Use **`python-3parclient >= 4.2.14`** (NOT 4.2.0) — earlier versions POST to `/credentials` instead
  of `/api/v1/credentials` and **fail to authenticate to the B10000** (Launchpad bug #2128677). The SDK
  officially supports Alletra MP firmware **10.4.0+** (our 10.5.51 is covered). Confirms `/api/v1` on
  443 is correct; `/api/v3` on 8080 is a *newer additional* endpoint, not an older 3PAR one.
- Call all create methods with **keyword arguments** — the SDK master has drifted (`createHost` gained
  an `nqn` param before `optional`); positional calls will break on upgrade.

**Host (Phase 2)** — `createHost(name, FCWwns=[...], optional={'persona': 11, 'descriptors': {...}})`:
**one** host definition carrying **all** of a host's FC WWNs (VMware **Persona 11 / ALUA**), then export
VLUNs to that single definition for multipath/failover. Idempotency: **`EXISTENT_HOST`** (do
`findHost(wwn=...)` first); **`EXISTENT_PATH`** if a WWN already belongs to another host.
[sd00002428 GUID-D93E3A75]

**Volume (Phase 3)** — `createVolume(name, cpgName, sizeMiB, optional={'tpvv': True})`. **Correction:**
the already-exists reason is **`EXISTENT_SV`** ("Volume Exists already"), *not* `EXISTENT_VV`. Data
reduction = inline dedup (per-CPG, 16 KiB pages) + compression (per-VV, Zstandard). [sd00003946]

**ESXi (Phase 5)** — ALUA (optimized = owning node); policy **`VMW_SATP_ALUA` + `VMW_PSP_RR` (iops=1)**,
matched by vendor `3PARdata` / model `VV`. On **ESXi 7.0U3+ (so our 8.0U3) the built-in default rule is
sufficient — do NOT add a custom SATP rule** (it's a tuning option only). Rescan registers new VLUNs
before the VMFS datastore. [sd00002428 GUID-43B8814C; VMware KB 2069356]

**Brocade zoning (Phase 4) — SAFETY-CRITICAL** — edit **additively** (`cfgadd "cfg","member;…"`), then
**`cfgEnable`** to ACTIVATE (cfgEnable activates *and* persists to all switches). **`cfgSave` ALONE only
commits the *Defined* config — it does NOT activate, and explicitly leaves the *Effective* and *Defined*
configs inconsistent** (divergent zoning on a fabric merge / HA failover). So the auto-zone sequence is
`alicreate → zonecreate → cfgadd → cfgEnable` — never `cfgSave`-alone as the "apply" step.
[Broadcom FOS Admin Guide; FOS `cfgSave` reference] → folded into ADR 0004.

**Not independently verified by the research (treat as open; we hold lab data for most):**
- Discovery shapes (`GET /ports`, `showport`, WWPN `node:slot:port` encoding, host↔array WWPN
  normalization) — *we have these from our live probes (VZ WSAPI `ports[0]` JSON + the `…0002F629`
  encoding) and the calibration notes above.*
- Brocade read-only inspection (`cfgshow`/`zoneshow`/`alishow`/`nsshow`) + naming + odd/even mapping —
  *we have the `cfgshow` format + naming from Panduranga's PuTTY capture (ADR 0004, san-zoning memory).*
- VLUN template types + auto/explicit LUN + the `EXISTENT_VLUN` reason — *CLI ref + SDK, not 3-voted.*
- WSAPI readiness (`503 code 68`) detection — *empirical only (ADR 0003 readiness gate).*
- Snapshot / Remote Copy / DR — entirely unverified; defer to `sd00002425/26` when we build those phases.
