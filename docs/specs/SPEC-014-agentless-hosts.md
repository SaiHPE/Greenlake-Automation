# SPEC-014 — Agentless discovery of hosts not in vCenter (G-2)

**Status:** proposed 2026-09-17 — needs a DECISION before it is specified further (see §3)
**Findings addressed:** G-2 (Windows/Linux hosts are only sheet-declared — WWPNs typed by hand — or
named from the fabric name server; no OS, no multipathing, no confirmation the WWPN typed is the one
in the server)
**Owner:** new `adapters/hosts/` (WinRM, SSH), `domain/discovery.py` (`DiscoveredHost` fields),
`application/platform/init_sheet.py` (Hosts tab columns), `application/provisioning/discovery.py`

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
