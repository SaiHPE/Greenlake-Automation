# SPEC-009 — Discovery says whose hosts these are

**Status:** implemented 2026-09-15 (rc.20); **seen live 2026-09-16** — the screenshot confirmed R1–R4 and found D-7/D-8/D-9, fixed rc.25 (§5)
**Findings addressed:** D-2 (`vmenode` filed as unidentified), D-3 (RCIP *Available* with link offline),
D-4 (names-free count omits hosts), D-5 (other teams' hosts at the same weight as this run's), D-6 (array
vocabulary + explanatory paragraphs instead of a legend and a status column)
**Owner:** `domain/discovery.py` (`DiscoveredHost`), `application/provisioning/discovery.py`
(`assemble_hosts`), `application/provisioning/preflight.py` (`_names_check`), `frontend/src/steps/DiscoveryStep.tsx`

## 1. Problem

On rack13arcus Discovery lists 20-odd servers: three the run is about (the vCenter ESXi hosts), eleven
HPE VME nodes and a handful of Windows and unclaimed FC logins that belong to other teams. They are
grouped by **operating system**, which answers a question nobody asked, and it misfiles: `vmenode` is a
named array host object whose persona (Generic-ALUA) reports no OS, so it lands under *Unidentified
hosts — add them to the sheet if you need them named*. Then three more tables repeat the same servers
from each source's point of view (*ESXi hosts* by adapter, *Hosts known to the array*, *Unclaimed
logins*), each with a paragraph explaining the array's vocabulary. Elsewhere on the page an RCIP port
reads *Available — cabled and capable* in one column and *offline* in the next, and the readiness check
counts *5 name(s) free* while the run will also create a host.

## 2. Requirements

**R1 — Identity is not OS.** `DiscoveredHost.identified` is true when any source gave the server a
name (vCenter, an array host object, the sheet, or an IQN node name) and false only when the name is
the initiator id itself. OS is a column, never a section. A named host with an unreported OS reads
*OS: not reported*, not *Unidentified*.

**R2 — Every host says whether this run is about it.** `DiscoveredHost.in_run` is true when the
sheet's vCenter reports it, the sheet declares it, or its name (or array name) is a member of one of
the sheet's host sets. Discovery renders **two tables in this order**: *Hosts in this run (N)* and
*Other hosts on this array (M)* — the second collapsed by default past ten rows, never omitted (a
shared array's other tenants are exactly what the operator must not touch).

**R3 — One table shape, one legend.** Both tables have the same columns: Host (with *on the array:
<name>* when it differs), OS, Initiators (WWPN/IQN, each with the array ports it is logged into),
Seen by the array (*Logged in (odd, even)* / *Not logged in*), Array host object (the name, or *none
yet — provisioning creates one*). One legend line under the tables explains the four statuses. The
per-source tables (*ESXi hosts* by adapter, *Hosts known to the array*) are gone: everything they
showed is in these columns, so `DiscoveredHost` also carries `persona` and `os_text` (the array's
persona and vCenter's version string) and `ports` (initiator → n:s:p).

**R4 — RCIP state agrees with its link.** One status per row: *Configured* (role rcip), *Available*
(no configuration, link ready), *Not cabled* (no configuration, link not ready). The description no
longer claims *cabled and capable* for every unconfigured port.

**R5 — The names check counts what the run creates.** *"3 object name(s) free: 2 volumes, 1 VV set.
Hosts named in the sheet: 2 (1 already on the array)."* A host already on the array is expected, never
a clash warning; volume/set clashes stay a warning as today.

## 3. Acceptance

- `tests/unit/test_storage_services.py`: `identified` false only for an initiator-id name; `in_run`
  from vCenter / sheet / host-set member; `ports`/`persona`/`os_text` carried; `_names_check` detail
  counts hosts separately and does not warn on an existing host.
- Frontend: `tsc` clean. Live: one screenshot of Discovery on rack13arcus showing the two tables
  (`.136`, `.47`, `.86` in the first; `vmenode` in the second with *OS: not reported* and its array
  name) and the RCIP table.

## 5. Amendment — rc.25 (2026-09-16), from the first screenshot

- **R1a** Within the vCenter source the host name is the identity: a second HBA of the same host joins
  the first row even when no array host object carries both WWPNs (D-7: `.136`, `.47`, `.86` listed twice).
- **R1b** A persona comes only from a named array host object; the nameless bucket's `--` is not one (D-8).
- **R3a** *none yet — provisioning creates one* only on in-run rows; other tenants' rows read *none yet* (D-9).

## 4. Out of scope

Reading the fabric name server's OS string in Discovery (would make switch credentials a discovery
prerequisite — see the note at the `assemble_hosts` call site); D-4's vCenter host count before
discovery (vCenter hosts are counted by Discovery itself).
