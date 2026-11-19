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
_Avoid_: profile (that is the **build profile** — a different thing), workflow (a mode picks steps; it isn't itself a sequence)

**Build profile**:
A *compile-time* selector — `ALLETRA_PROFILE` = `full` (default) | `init-only` — baked into a release to
choose which slice of the one codebase that artifact exposes: the whole platform, or the **Initialization
accelerator**. It fixes the sheet, the mode chooser, and the title before the app even runs. Distinct
from a **Mode** (a *runtime* operator choice within a build). See ADR 0007.
_Avoid_: mode (a build profile is chosen at build time, not by the operator)

**Initialization accelerator** ("Alletra MP Initialization"):
The `init-only` **build profile** released as a separate, restricted app for field engineers — onboarding
only (GreenLake → Cloud Connectivity → DSCC → verify), an onboarding-only sheet (no Provisioning tab), and
the mode chooser locked to Initialization. Same codebase as the full app. See ADR 0007.

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
What the customer *wants done* on one array: the **reach** (array / vCenter / both switch IPs +
credentials, passwords included) plus what to create — a **list of volumes**, each with its own name,
size, provisioning type (thin/reduce), CPG, and optional VV-set membership, and **one or more host-sets**
with their selected member hosts. **Heterogeneous**: the volumes need not share size, type, or CPG. It
carries only this — never environment facts.
_Note_: the Provisioning tab currently expresses only the simple case — one name-prefix/size/count → N
identical volumes into one host-set, via a `from_simple` shortcut; Stage 2 redesigns the tab to express
the full plural shape above.
_Avoid_: the old flat "one host-set name + one volume prefix/size/count" model (that was `VolumeSpec`, now removed).

**Discovery report**:
The run-time read an environment a provisioning run produces — array target ports + WWPNs, ESXi host
HBA WWPNs + OS (via vCenter), and the fabric nameserver view — with WWPNs normalised for matching. A
bundle of Discovered facts; the input to zoning and provisioning.

**Ideal subset**:
The clean subset we curate *out of the messy lab* to work with — the hosts that are powered on and
correctly zoned to the array (logged in on the expected fabric(s)), pruned of the noise (offline /
unzoned / half-zoned hosts, storage & peer ports). Not new hardware — a curated *view* of the messy
lab. Discovery classifies every host's HBAs by fabric + login state; the operator selects the good
ones (the dropdown builder). Serves as the tier-2 green validation set for provisioning now, and the
known-good reference for the zoning **command set** (the tool never writes to the switch — ADR 0012).
_Avoid_: treating it as a separate "ideal lab" (it's a subset of the messy one).

**Fabric (odd / even)**:
Which of the two SAN switches a port is cabled to. The operator DECLARES it in the sheet —
`switch_f1` = the **odd / F1** switch, `switch_f2` = the **even / F2** switch — and the tool assigns
every port (host + storage) to the fabric of whichever declared switch's name server sees it.
Port-number parity (odd `P`=1/3, even `P`=2/4) is only a **cross-check**; a mismatch is flagged. Works
only when the two switches are *separate* fabrics — a meshed lab collapses the split. See ADR 0004.
_Avoid_: treating fabric as a property of the port number alone (the switch cabling is the truth).

**Zoning plan** (current map + builder):
Two things: (1) the **current-connection map** — per host WWPN, the storage port WWPN(s) + `n:s:p` it
is actually logged into (`showhost` + `showport`), host WWPN ↔ storage WWPN, both sides; and (2) the
**operator-selected builder** — per host WWPN a parity-filtered dropdown of same-fabric storage ports
the operator *selects*, which the tool turns into the **command set**. **The tool never writes to the
switch.** See ADR 0004 and ADR 0012.
_Avoid_: "remediation" (the tool produces a plan; it does not create zones), "auto-pair" (the operator selects), "staging" (see **Command set**).

**Command set**:
The zoning step's deliverable: the exact, correctly-ordered `alicreate` → `zonecreate` → `cfgadd` →
`cfgenable` text for this fabric, which a **consultant reviews and applies by hand**. It is the
product of the zoning step, not a preview of something the tool will then do — the tool has no
ability to run it. `cfgenable` is presented separately from the additive commands, because activating
the configuration is a scheduled SAN-team act and not part of the paste. See ADR 0012.
_Avoid_: "staging" / "apply" (both imply the tool executes it; it does not), "preview" (it is the deliverable, not a rehearsal).

**Unclaimed login**:
A WWPN **logged into an array target port but claimed by no Host record** — `showhost -d` prints it
with `--` in the Id/Name/Persona columns. It is a real login: the port is cabled, zoned and active,
and the array can see it. It simply is not yet anybody's named Host. This is the *normal* state of a
freshly zoned server before provisioning creates its Host, so on a greenfield array every server
starts here. Unclaimed logins are authoritative for **fabric** lookup, and must never appear in a
list of host *names*.
_Avoid_: reading it as "not zoned" (a login is proof of zoning); treating it as a Host (nobody can name it).

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
Created on the SAN switch; *verifiable* from the array's fabric nameserver. Provisioning *consumes*
zoning (reads which host WWPN is logged into which array port); it does not *produce* it.

**Path verification**:
After the array-side export, reading the array back (`showvlun` + `showhost`) to confirm the exported
LUN is reachable over the host's actually-logged-in WWPNs, per fabric — e.g. "host X: 2/2 HBAs logged
in, LUN live on both fabrics" vs "0 paths — not zoned". Read-only; it *consumes* zoning, never creates
it, and it stops at the array (the ESXi-side datastore is a separate, out-of-scope step).
_Avoid_: conflating with **Post-init verification** (that checks onboarding config, not the data path).

**ALUA path state (AO / ANO)**:
Active-Optimized vs Active-Non-Optimized — whether a path leads to the controller node that owns
the volume. Optimized paths carry I/O; non-optimized are standby until failover.

**iSCSI VLAN interface** (VLAN-tagged iSCSI address):
An extra IPv4 address on an array iSCSI port, carried on one VLAN tag (1 to 4094): port, VLAN,
address, netmask, optional gateway. Not the port's **untagged address** (its base address, the one
`showport -iscsi` prints), which the tool never changes: `showport -iscsivlans` lists that one as
VLAN `untagged`, and a `controliscsiport` line without `-vlan` acts on it. The sheet's *iSCSI network*
tab asks for interfaces; the *Array ports* step plans them (SPEC-024).
_Avoid_: "VLAN" alone for the interface (a VLAN is the network; the interface is one port's address on it).

**Array ports (step)**:
The step between Discovery and SAN Zoning that sets the array's own ports up from the sheet, one
section per kind: the iSCSI VLAN interfaces (SPEC-024) and the peer ports (SPEC-025). It comes before
zoning because the zoning check is what sees an iSCSI host's login on the new address, and the peer
ports' zones use the WWPN read after the change. The switch side is a sentence for the network team
or a command set for the SAN team; the tool never writes a switch.

**Peer port**:
An FC port of the array in connection mode `peer` (`showport -par` Connmode `peer`, `showport` Type
`peer`, mode `initiator`): it logs in to the fabric as an initiator so a data migration can read a
source array through it. It has WWNs of its own (`0202` where a host-mode port has `0002`). Judged
by Type and Connmode, never by its Label: on D22U27 three host ports are labelled "peer". The tool
offers only `free` FC ports with no login and no export (SPEC-025).
_Avoid_: calling an IP port in mode `peer` (RCIP or the node interconnect) a peer port.

**Remote Copy group**:
The unit of replication — a consistency group of VVs mirrored to a target array, preserving
write order. Failover/failback (disaster recovery) act on the group.

**Source array** (migration):
The 3PAR, Primera or Alletra 9000 whose hosts and volumes move to this run's array, named on the
workbook's *Migration* tab. A read-only step credential: the tool only reads it, never writes to it.
This run's array is the **destination**. See SPEC-027, ADR 0020.
_Avoid_: peer array (that is the replication partner), second run (a migration is one run)

**Peer Motion**:
HPE's data migration, run from the destination array's own UI or DSCC over FC peer ports zoned to
the source's host ports. It does the import; the tool reads both arrays, checks they are ready and
hands the import over.

**Snapshot schedule**:
A task the array runs by itself on a cron (minute, hour, day of week, in the array's own time zone).
The tool's schedules always run `createsv` of one volume set or volume, and every snapshot they take
expires after *Keep for*. A schedule keeps running after the run that made it, until someone removes
it (`removesched`). WSAPI has no schedule resource: the tool reads schedules with `showsched` and
writes one only through the snapshot-schedule SSH client (ADR 0016). The snapshot taken now is
separate: one read-only `<volume>.initial` per volume, over WSAPI.
_Avoid_: "protection policy" (DSCC's object, ADR 0016 option B); "backup".

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

**Array subscription**:
The array's registration and entitlement state with HPE GreenLake. Until it completes, the array
refuses *data-path configuration* — creating a virtual volume fails with "Array has not yet completed
the subscription process". An array can be powered on, healthy, reachable over WSAPI, with normal
drives and free capacity in its CPGs, and still create nothing, because subscription is a separate
gate from hardware readiness.
_Avoid_: "initialization" (that is the array's own network setup — a prerequisite of subscription,
not the same thing); "licensing" (its failure mode is a hard refusal to configure, not a warning).

**Protection policy**:
A **DSCC**-managed rule set that applies **snapshots** and/or **replication** (Remote Copy) to
volumes or volume-sets on a schedule, with retention — the cloud-native way to express snapshot + DR
*intent*. The direct-array equivalent is `createsv` / `createsched`.
_Avoid_: "backup".

**File service** *(Unified File, SPEC-028)*:
The array's NFS service, one per array, running on each controller node (OS 10.5 and later). The
tool reads it over the array's WSAPI v3 and never turns it on or off. `normal` is the word a node
prints when its file service runs.
_Avoid_: "File Persona" (the 3PAR name; its commands have no help on a B10000).

**File port**:
An Ethernet host port in File mode (`showport` Type `file`), listed by `showport -file`. It sits on
the same n:s:p as an iSCSI port, so only the array's own Type tells them apart. Moving a port into or
out of File mode (`controlport config file`) reboots the array; the tool never does it.

**File system**:
Capacity for shares, with data reduction on or off. One share per file system on a B10000.

**Client group**:
The list of clients that may mount a share, each with its access (`rw` or `ro`) and options. The
array calls it a *file share setting*; on screen and on the sheet it is a client group. A client of
`*` is any host that can reach the File ports.

**File share**:
An NFS export of a folder in a file system, served on one File port, mounted as
`<File port address>:/file/<file system>/<share>`. Its clients are its client group's.
_Avoid_: "view" (the provisional word before the file research; on a B10000 the word is *share*).

**As-built (document)**:
The per-deployment record produced as the **final step** — the array's *actual initialised
configuration* (identity, hardware, capacity, network, inventory, health), read **read-only** from the
array's own `show*` / `checkhealth` and rendered into HPE's Word template (its cover page, HPE Graphik
fonts, and Table 01 preserved). An engagement **deliverable**, not a live monitoring view.
_Avoid_: confusing it with **Post-init verification** (that *checks* the config against the sheet; the
as-built *documents* what the array actually has).

**Narrative fields (as-built)**:
The values the template asks for in prose that the array cannot know, so an operator supplies them:
**customer name**, **site/location**, **application/workload** (what runs on the array, e.g. "VMware
vSphere cluster") and **purpose** (why block storage is used here). All optional and all captured
twice — as workbook columns filled up front, and as editable fields in the As-built step, where the
step's value wins. An unfilled one leaves its `<placeholder>` visible in the document and raises a
**warning**; it never blocks generation.
_Avoid_: treating these as array facts — nothing in `show*` output can produce them.

**As-built warning**:
Something that did not fill: a template **section heading** that could not be found (so its content
is absent from the document), or a `<placeholder>` still present in the finished text. The document
is **always produced** — an operator in the field would rather hand over a partial document than be
blocked — so warnings are the mechanism that stops an incomplete as-built reaching a customer
unnoticed. Section headings are matched by **intent** ("contains inventory"), never by exact string:
HPE renamed "Alletra Inventory" to "HPE GreenLake for Block hardware Inventory" between template
revisions, and the exact match silently dropped the entire inventory section.
_Avoid_: reading a generated document as complete without checking its warnings.

**Status at handover**:
What the array says about itself when the as-built is generated (SPEC-026): its **New alerts** (from
`showalert -d`) and its capacity in use (`showsys -space`). A section of the as-built (*Array status at
handover*) and a block on the As-built page; read-only. Each alert of severity Major, Critical or Fatal
is an as-built warning. *Before this run* says whether an alert first occurred before the run was
created (its `Time` is the latest occurrence), using the array's clock (`showdate`) for its time zone.
No performance figures: the owner removed them on 2026-11-19.
_Avoid_: "health" on screen (write *status*); "open alerts" (the read gives the array's New alerts
only); reading an idle baseline as the array's capability.

## Language — proxy / connectivity

**System proxy**:
The proxy the OS (and browser) uses, resolved *per destination URL* from WinINET static settings +
PAC/WPAD auto-config. The tool **auto-detects** this — it never hardcodes a proxy — so it works in any
environment. See ADR 0008.

**Effective proxy**:
The proxy the tool actually uses for a given outbound call: the **manual override** if the operator set
one, else the auto-detected **system proxy**, else none (direct). Produced by the `ProxyResolver`.
_Avoid_: "the proxy" (be specific — override vs system vs none).

**Proxy bypass** (NO_PROXY):
The hosts/subnets reached **directly**, never through the proxy — `localhost`, the cloudinit link-local
`169.254.*`, and the **on-prem device IPs from the run** (array / vCenter / switches). Derived from the
sheet, not hardcoded. See ADR 0008.

**Trusted device** (trust on first contact):
An on-site device (the array and its Remote Copy peer, vCenter, a SAN switch, a Linux host) whose SSH
host key or TLS certificate the run recorded the first time it connected to it. Later connections
compare against that **pin**; a different key stops the step before the password is sent, until the
operator **re-trusts** the device on the run overview. Pins last one run. Cloud endpoints are never
pinned: their certificates are checked against certificate authorities. See ADR 0026.
_Avoid_: "known hosts" (the jump box keeps none), "accepting the certificate" (nothing is accepted
blindly).
