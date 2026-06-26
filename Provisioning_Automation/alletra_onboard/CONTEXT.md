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

## Language — storage provisioning (planned)

**Provisioning intent**:
What the customer *wants done*, supplied in the Initialisation sheet: reach (IPs + credentials) plus
what to create (volume names/sizes, which hosts or cluster, replication target, protocol). The sheet
carries only this — never environment facts.

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
