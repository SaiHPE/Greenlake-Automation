# SPEC-014 — Discovery of the sheet's hosts: serial, WWPN, IQN, per OS (G-2)

**Status:** APPROVED 2026-09-21 (field request at the zoning/provisioning demo). R1–R3, R5, R6, R7
live-verified (CRV VZ 2026-09-25, rack13 2026-09-28). R4 (Linux) built — pending live run (no Linux host).
**Findings addressed:** G-2 (Windows/Linux hosts are only sheet-declared — WWPNs typed by hand — or
named from the fabric name server; no OS, no multipathing, no confirmation the WWPN typed is the one
in the server)
**Owner:** new `adapters/hosts/` (WinRM, SSH), `domain/discovery.py` (`DiscoveredHost` fields),
`application/platform/init_sheet.py` (Hosts tab columns), `application/provisioning/discovery.py`

## 0. The request (2026-09-21)

For every host on the sheet's Hosts tab — **even when its WWPN/IQN is not typed** — discovery fetches
its **serial number**, **FC WWPNs** and (if not FC) **iSCSI IQN**, and displays them **per OS**.
Decisions taken: per-host *Login username / password* columns on the Hosts tab (blank = do not log
in); no Linux host on rack13, so the Linux read ships *built — pending live run*.

### Requirements

- **R1 — no sheet host is dropped.** A Hosts-tab row with a name (and optionally IP) but no WWPN/IQN is
  a lookup request, not a parse error. Discovery resolves it, in order: vCenter host of that name or
  IP → array host object of that name → array iSCSI login from that IP → then by short name
  (`esx01` = `esx01.lab.local`, either way round; never an IP) the vCenter host, the array host
  object, an IQN's node name. A short name that fits two or more hosts is refused (*"not found
  uniquely — … fits 2 vCenter hosts (…)"*), never guessed. Found: its initiators are filled in and
  it provisions under the name vCenter/the array already use (the array refuses a second host
  object for a WWN it holds). Not found (vCenter unreachable says so rather than "not in vCenter"):
  it is still listed (source `sheet`, warning *"not found — … add its WWPN/IQN"*), a
  discovery note names it, and the provisioning plan notes it as not planned. A Host sets member
  or host export typed with the sheet's name follows the host to its planned name (plan note
  *"sheet host 'X' is the same server as 'Y' …"*); a member nothing names is noted, not dropped
  silently (4a53429).
- **R2 — ESXi via vCenter:** serial number (`hardware.systemInfo.serialNumber`, fallback
  `otherIdentifyingInfo` SerialNumberTag/ServiceTag) and iSCSI IQNs (`InternetScsiHba.iScsiName`)
  per host, joined on the IQN like any initiator. Enrichment only: its failure is a note.
- **R3 — display per OS:** *Hosts in this run* is one table per OS (ESXi / Windows / Linux / HPE VME /
  OS not reported) with a Serial number column; the Host cell says how a sheet host was found.
- **R4 — Linux (slice 2):** SSH with the row's login, read-only: `/sys/class/dmi/id/product_serial`,
  `/sys/class/fc_host/host*/port_name`, `/etc/iscsi/initiatorname.iscsi`, `/etc/os-release`,
  `multipath -ll`.
- **R5 — Windows (slice 3):** WinRM with the row's login, read-only: `Win32_BIOS.SerialNumber`,
  `Get-InitiatorPort` (FC + iSCSI), OS caption, MPIO feature.
- **R6 — typed vs read:** a WWPN typed on the sheet that the server's own read does not report is a
  plan **blocker** (slices 2–3).
- **R7 — secrets:** host passwords are held per run like array/switch passwords (ADR 0013), never in
  events or `GET /runs/{id}`.

### Slices

1. R1–R3 (no new adapter, no sheet column) — **built 2026-09-21; R1 array half seen live 2026-09-25**
   on the CRV VZ array (10.64.122.140, offline bundle + `ui-smoke/spec014.ps1`, 14 PASS / 1 FAIL): a
   no-ID row `CRV_VZ_DL360G11D24U25` → *found on the array as host …* with both WWPNs; a row nothing
   finds stays listed with its warning **and** the discovery note (fix 3407a33); discovery reads 12
   ports while vCenter times out. Re-run 2026-09-25 (21 PASS / 1 FAIL / 3 SKIP, runs `883be91e`,
   `081f3385`): an unresolved row reads *"vCenter was not reached, so it could not be checked"* when
   vCenter timed out (5673327), and a sheet FQDN `CRV_VZ_DL360G11D24U25.spec014.local` → *found on the
   array as host CRV_VZ_DL360G11D24U25 (short-name match)* with both WWPNs (e47c3e0). Planning under
   the array's name and the ambiguous-short-name refusal are unit-tested only. **R2 seen live on
   rack13 2026-09-28** (`spec014.ps1`, 36 PASS / 1 FAIL / 3 SKIP, run `540ce636`): vCenter returned an
   identity for all 3 ESXi hosts; a no-ID row resolved *found in vCenter as 10.132.30.47* with serial
   `CN763604C4`, both WWPNs and its iSCSI IQN; a Host sets member typed with the sheet name was planned
   under the vCenter name (4a53429); the array / short-name / not-found paths repeated VZ's result;
   no password in any run detail or event (R7). R3 (per-OS tables) seen in a screenshot on VZ.
2. Sheet login columns + Linux SSH (R4, R6, R7) — **built 2026-09-23, pending live run** (no Linux
   host on rack13; parsers pinned to RHEL 9-shaped output). `adapters/hosts/linux_ssh.py` runs a fixed
   keyed command set (`cat` of sysfs/`/etc` files, `hostname`, `multipath -ll`; `sudo -n` only for
   serial and multipath). An OS left blank with a login is tried as Linux; a Windows or ESXi row with
   a login is not logged in (note says why). A failed login is a note, never the step's error.
3. Windows WinRM (R5) — **built 2026-09-24, pending live run**. `adapters/hosts/windows_winrm.py`
   (new dependency `pywinrm`): NTLM on HTTP 5985 (message-encrypted), HTTPS 5986 if 5985 is closed,
   `proxy=None` so an on-prem host never goes through the lab proxy (ADR 0008). Fixed keyed
   PowerShell reads emitting JSON: `Win32_BIOS.SerialNumber`, `Win32_OperatingSystem`,
   `Get-InitiatorPort` (FC vs iSCSI told apart by address shape, not ConnectionType), MPIO feature
   state + `Get-MSDSMSupportedHW` 3PARdata claim + `Get-Disk` 3PARdata count. Live target
   `arcus-win137` (10.132.30.137); needs a local administrator login and 5985/5986 open from the jump box.
   2026-09-28 rack13 (run `11a1d15f`): WinRM answered but refused `administrator` (*login failed …
   check the Hosts tab login*) — the failure path is live (a note, the host stays listed, no password
   echoed). **R5 read seen live the same day** with the tool's own client: `arcus-win137` is the rack13
   jump box itself (10.132.30.137 = `ELJR0NB1UV`, domain-joined); `ELJR0NB1UV\Administrator` returned
   Windows Server 2022 Datacenter, serial `SGH640WFT7`, FC WWPNs `51402EC02089CC1C`/`…CC1E` (the two
   typed by hand in S-4), iSCSI IQN `iqn.1991-05.com.microsoft:eljr0nb1uv…`, *MPIO Installed; 3PARdata
   VV claimed by MSDSM*. The bare name failed because a domain-joined server does not map it to the
   local account; the login error now says so. **R5 + R6 live through the app 2026-09-28**
   (`spec014.ps1` 40 PASS / 0 FAIL / 2 SKIP, runs `211592b2`, `1b0cab96`; evidence
   `docs/validation/evidence-2026-09-28-spec014-rack13-run2-report.md`): a no-ID Windows row with
   `ELJR0NB1UV\Administrator` → *read from the server over WINRM* with the serial, both WWPNs, IQN and
   MPIO above; the same row with a typed WWPN `1000000000000001` → plan blocker *"sheet WWPN(s)
   1000000000000001 not on the server — 10.132.30.137 reports 51402EC02089CC1C, 51402EC02089CC1E"*. The
   run before it failed the login because the composed sheet had turned the password into an Excel
   formula / stripped its spaces — fixed for every credential field (1cfa22e).

### Addendum 2026-09-28 — how a found host reaches the plan

A review for one layer deciding a host fact and the next assuming another (LESSONS 41) found five
cases; all fixed with tests, none seen to misfire live:

- A read-found row plans under the name the array or vCenter already uses for its WWPN/IQN, as the
  other lookups already did (e083406).
- A sheet OS left blank takes the OS the server reported, so a Linux host is not created with the
  VMware persona (486dfa8). A typed IQN is compared without case (486dfa8).
- `os = vme` is read over SSH and maps to Generic-ALUA (e083406).
- An iSCSI-only host the array already has is planned even when the sheet named it first
  (`ProvisionableHost.on_array`); an existing host with a persona this tool cannot create (e.g.
  Generic) is no longer refused at apply — the persona is checked on create only (ffdf900).
- R6 is also a zoning-plan note, not only a provisioning blocker: a typed WWPN the server lacks would
  otherwise be zoned (ffdf900). A planned host with no OS from any source is noted (VMware persona
  assumed), not blocked — field decision.

The sections below are the original deferral analysis, kept for the record.

## 1. Problem

A Windows or Linux server gets to the array today by one of two routes: the operator types its WWPNs
on the sheet's Hosts tab (S-4: `arcus-win137`, one WWPN mistyped would be zoned against nothing —
the parser refuses obvious mistakes, not plausible ones), or the fabric name server happens to carry
its `HN:` symbol. Neither route tells the tool the OS (so the persona is a guess), whether MPIO is
installed, or whether the WWPN on the sheet is actually in the server.

## 2. What it would do

Per Hosts-tab row with an address and a credential: log in **read-only**, once, and read
- Windows (WinRM, `Get-InitiatorPort`, `Get-WindowsFeature Multipath-IO`, `mpclaim -s -d`,
  `Get-ComputerInfo` OS caption) → WWPNs, MPIO installed/claimed, OS → persona `WindowsServer`.
- Linux (SSH, `/sys/class/fc_host/*/port_name`, `multipath -ll`, `/etc/os-release`) → WWPNs,
  multipath paths, OS → persona `Generic-ALUA` / RHEL / SLES as the array names them.

Then: a typed WWPN that the server does not have is a **blocker** (not a warning); the persona comes
from the OS, not the operator; path verification (SPEC-013's pattern) gains the host's own multipath
view.

## 3. The decision this needs

1. **Credentials on the sheet.** The Hosts tab would gain *Login username / password* per host —
   a third class of secret (after array and switch), held per run like the others (ADR 0013). Is a
   field engineer going to have local admin on a customer's Windows host at deployment time?
   Experience says: often not. If the answer is "usually not", G-2 stays a *nice to have* and the
   typed-WWPN route stays the product, with the fabric name server as the cross-check it already is.
2. **WinRM reachability from the jump box.** 5985/5986 open from the jump box to customer hosts is
   a firewall conversation. The prerequisites page would list it; it may be the reason the feature is
   skipped on most sites.
3. **Scope of OS.** Windows + RHEL/SLES covers the field. AIX/HP-UX/Solaris are out.

## 4. Recommendation

Do not build until one real deployment has produced the need: a wrongly typed WWPN or a wrong
persona that the current cross-checks (fabric NS symbol, array login) did not catch. The tool's
existing answer — *unidentified initiators are shown by WWPN; name them on the sheet if you intend
to zone them* (D-2) — has held on every session so far. Keep G-2 in SCOPE.md area 2 as priority 2,
status *deferred — needs a field case*.

## 5. If approved anyway — size

Two adapters (~150 lines each, pywinrm + paramiko already bundled for paramiko), sheet columns +
parser (~40), discovery join (~40), UI rows, prerequisites entry, tests with captured fixtures.
Two releases (Linux first — SSH is already in the bundle).
