# Alletra Onboard

Operator automation for onboarding an HPE Alletra MP B10000 into HPE GreenLake + DSCC. This
glossary fixes the language of the domain so code, UI, and docs use the same words.

## Language

**Post-init verification**:
After the operator confirms the array is initialized (the DSCC Set Up System wizard submitted),
logging into the array directly to confirm its configuration is correct.

**On-array config**:
The array's actual running configuration, read from the array itself. This — not the cloud's
record — is what post-init verification checks.
_Avoid_: live config, applied config

**DSCC-applied config**:
The configuration the DSCC cloud console records as having pushed to the array. Distinct from
on-array config; the two can disagree (e.g. DSCC reports "applied" but the array didn't take a value).

**Array admin credential**:
The array's local superuser account (username + password, e.g. `3paradm`) used to log into the
array directly. The same account the operator registers as the DSCC System Credential.
_Avoid_: secret, DSCC credential

## Language — modes (decoupling)

**Mode**:
The operator-selected *slice* of the onboarding, chosen at the start: Full onboarding / Provision only
/ Both / Verify only / Custom. It determines which steps the wizard renders and the run executes — so
verification or provisioning can target an already-initialised array without re-running init. See ADR 0005.
_Avoid_: profile, workflow (a mode picks steps; it isn't itself a sequence)

**Step**:
One operator-facing unit of work (GreenLake registration, Cloud Connectivity, DSCC, Discovery, SAN
Zoning, Provision storage, Verify). Each has a stable key and a *kind* — `init`, `provision`, or
`verify`. A mode selects a set of steps; the step registry (`domain/workflow.py`) is their single
source of truth for identity and order.

**Initialisation sheet**:
The single workbook a customer fills for one array — filled *completely* (onboarding + provisioning
fields, all tabs), then reused across every Mode. The Mode chooses which parts of the sheet are
acted on; it never changes which sheet is used. One workbook = one array; the same complete sheet
drives full onboarding, provision-only, verify-only, or all at once.
_Avoid_: per-mode sheet (there is only one), profile

## Language — storage provisioning

**Provisioning intent**:
What the customer *wants done*, supplied on the **Provisioning tab** of the workbook: reach (array /
vCenter / both switch IPs + credentials, passwords included) plus what to create (host-set name, volume
name-prefix/size/count, CPG, thin-vs-reduce, optional VV-set). It carries only this — never environment facts.

**Discovery report**:
The run-time read an environment a provisioning run produces — array target ports + WWPNs, ESXi host
HBA WWPNs + OS (via vCenter), and the fabric nameserver view — with WWPNs normalised for matching. A
bundle of Discovered facts; the input to zoning and provisioning.

**Zoning report / remediation**:
The comparison of the *expected* odd/even zone set (computed from discovered array ports + host WWPNs)
against each fabric's *actual* active zoning. The *remediation* is the exact additive command sequence
(`alicreate` → `zonecreate` → `cfgadd` → `cfgenable`, never `cfgsave`-alone) to create the missing
zones — shown for explicit confirmation before any switch write. See ADR 0004.

**Discovered fact**:
Anything about the environment the automation *reads at run time* instead of asking for — array
target-port WWPNs, CPGs, existing hosts/volumes/VLUNs, host HBA WWPNs, available personas, the
`naa`↔VV mapping. Never placed in the sheet or hardcoded. See ADR 0002.

**CPG (Common Provisioning Group)**:
A provisioning *policy* (drive type + RAID layout) that volumes draw capacity from. It is not
capacity itself, and it must already exist before a volume can be created.
_Avoid_: pool (it's a recipe, not a bucket)

**Virtual volume (VV)**:
A logical block volume carved from a CPG — the only data layer a host sees.
_Avoid_: LUN (a VV is only a LUN once it's exported)

**Export (VLUN)**:
The association that presents a VV (or VV set) to a host (or host set), making it visible as a LUN.
"Export" is the act; "VLUN" is the resulting association.

**LUN**:
The number by which a host sees an exported VV. Distinct from the VV's own id.

**Host**:
The array's record of a physical server — its initiator ports (FC WWPNs / iSCSI IQNs) plus a
persona. Distinct from the physical server itself.
_Avoid_: server, node (a controller is the array's "node")

**Host set**:
A named group of Hosts (typically a cluster) so a VV can be exported to all of them at once.

**Persona**:
The host-type profile the array applies for SCSI/ALUA behaviour (e.g. the VMware persona).

**Zoning**:
Switch-level pairing of a host WWPN and an array target-port WWPN so the two can communicate.
Created on the SAN switch; *verifiable* from the array's fabric nameserver.

**ALUA path state (AO / ANO)**:
Active-Optimized vs Active-Non-Optimized — whether a path leads to the controller node that owns
the volume. Optimized paths carry I/O; non-optimized are standby until failover.

**Remote Copy group**:
The unit of replication — a consistency group of VVs mirrored to a target array, preserving
write order. Failover/failback (disaster recovery) act on the group.

**Device naa**:
The host-side identifier for a SAN disk. For this array family it deterministically encodes the
array system id and the VV id, so a host device maps back to its array volume.

## Language — platform control plane

**DSCC (Data Services Cloud Console)** — also **Data Ops Manager (DOM)**:
HPE's GreenLake *cloud* control plane: one public REST API that manages *many* arrays (provision,
replicate, snapshot, telemetry) from the cloud. Distinct from a single array's on-box WSAPI. See
ADR 0006.
_Avoid_: "the cloud" (name the plane); treating DSCC and WSAPI as interchangeable.

**Control plane**:
The surface a management operation is issued *through*. Three exist and each capability is *routed*
to one: the **cloud** plane (DSCC, multi-array), the **direct** plane (a single array's WSAPI/SSH),
and the **switch** (FC zoning). See ADR 0006.
_Avoid_: conflating the control plane with the array itself (the data plane).

**Protection policy**:
A **DSCC**-managed rule set that applies **snapshots** and/or **replication** (Remote Copy) to
volumes or volume-sets on a schedule, with retention — the cloud-native way to express snapshot + DR
*intent*. The direct-array equivalent is `createsv` / `createsched`.
_Avoid_: "backup".

**View** *(file — provisional)*:
On the file side, an exported access path to a file system (an SMB/NFS export with an attached
policy) — the file analogue of a block **Export (VLUN)**. Provisional: the file control plane is not
yet researched; refine after the file research pass.
_Avoid_: assuming it equals "share" (a view may front one or more shares/exports — confirm in file research).
