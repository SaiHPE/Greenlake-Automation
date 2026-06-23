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
- Be **idempotent**: treat `EXISTENT_HOST` / `EXISTENT_VV` / `EXISTENT_VLUN` as warnings.
- **Never** issue `removevlun` / `removevv` from the tool — teardown stays manual (see the ESXi guide
  "Removing volumes": detach on ESXi first, then `removevlun`, then `removevv`, then rescan).

## Per-run inputs the tool will need (the parameters this runbook leaves open)

- Protocol: **FC** (this runbook) — vs iSCSI/NVMe (different host-create + discovery).
- Host/cluster: host names + WWPNs (from Phase 1) + cluster (host-set) name.
- Volumes: names, size, count, provisioning (`reduce` vs `tpvv`), CPG (`SSD_r6`), optional VV-set name.
- Export: per-host LUNs vs set-to-set with `auto` LUN.
