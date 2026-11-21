# Documentation map

Everything under `docs/`, separated into **living truth**, **decisions and specifications**, and
**evidence, workpackets and history**. When a document and the code disagree, the code is right.

Start outside `docs/` if you are brand new:
- [`AGENTS.md`](../../../AGENTS.md) — hard rules, folder layout and commands for people and agents.
- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) — access, setup, branch/PR flow, `scripts/check.py` and lab runs.
- [`README.md`](../README.md) — operator walkthrough, jump-box setup, `.exe` builds and releasing.
- [`CONTEXT.md`](../CONTEXT.md) — domain vocabulary (mode, build profile, fabric, command set, virtual volume, export, approval, trusted device).

---

## 1. Living documents (read these — current truth)

Kept up to date with `main` and checked by `scripts/check.py` where applicable.

| Document | What it is |
|---|---|
| [`DEVELOPER-HANDBOOK.html`](DEVELOPER-HANDBOOK.html) | One-stop guide for developers — open in a browser. |
| [`STANDARD.md`](STANDARD.md) | The engineering standard enforced by `scripts/check.py` and `quality/ceilings.toml`. |
| [`design/HLD.md`](design/HLD.md) | High-level design: arc42 headings, C4 diagrams, write gates and ADR index. |
| [`design/LLD.md`](design/LLD.md) | Low-level design: state machines, approvals, persistence, TLS/pins and error contracts. |
| [`SCOPE.md`](SCOPE.md) | Canonical nine-area scope, what is live-verified and what waits on lab hardware. |
| [`UX-GUIDELINES.md`](UX-GUIDELINES.md) | UI wording, layout and confirmation rules (HPE Design System). |
| [`LESSONS.md`](LESSONS.md) | Incident-to-rule register: past bugs and the test or check each one left behind. |

---

## 2. Decisions and specifications

Authoritative design records for why the system works the way it does and what each feature must do.

| Folder | Contents |
|---|---|
| [`adr/`](adr/) | Architecture decision records: transport planes, safety rules, SSH write policy, device trust, encryption at rest, least privilege, typed events and the gate. |
| [`specs/`](specs/) | Feature specifications: acceptance rules for provisioning, zoning, path verification, replication, failover, Console, snapshots, iSCSI VLANs, peer ports, handover, migration, Unified File and RCFC. |

---

## 3. Evidence, workpackets and history

Lab evidence, build workpackets and historical records. Open-item workpackets (such as pending
lab-run plans) remain active reference until their GitHub issue closes; research memos, past UX
audits and pre-app runbooks are kept for history rather than current instructions.

| Path | Contents |
|---|---|
| [`validation/`](validation/) | Live lab validation records and evidence summaries. |
| [`workpackets/`](workpackets/) | Completed and open-item build workpackets (active reference while their GitHub issue is open). |
| [`research/`](research/) | Pre-design research memos written before ADRs and specs. |
| [`ux/`](ux/) | UI audit findings, checklists, zoning redesign notes and static mockups. |
| [`runbooks/`](runbooks/) | Historical pre-app manual runbooks (superseded by the app workflow in [`../README.md`](../README.md)). |
| [`TRACKER.md`](TRACKER.md) | Append-only history log of past `BL-NN` IDs and closed issues (closed issues get a *Closed* row). Open work lives in [github.hpe.com issues](https://github.hpe.com/g-sai-roopesh/greenlake-automation/issues). |
