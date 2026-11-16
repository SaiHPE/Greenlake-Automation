# The platform is a hybrid control plane: DSCC/GreenLake cloud API primary, direct-array WSAPI for depth

The full-scope automation (initialize → discover → connect → provision → replicate/DR → report →
document, across Alletra MP **block** and **file** — see [SCOPE.md](../SCOPE.md)) is built on **two
control surfaces, routed per capability**:

- **Cloud (primary):** the HPE **GreenLake Data Services Cloud Console (DSCC / Data Ops Manager)**
  public REST API — a *multi-array* plane. One OAuth login orchestrates provisioning, replication,
  snapshots, and telemetry across every onboarded array.
- **Direct (depth):** a single array's **WSAPI** (HTTPS on :443) — for provisioning depth and
  anything the cloud plane doesn't expose. Reuses the existing `python-3parclient` / array-SSH
  clients as this tier.
- **Out-of-band:** FC **zoning** stays on the switch (Brocade FOS additive `cfgadd` → `cfgenable`)
  — unchanged from [ADR 0004](0004-auto-remediate-san-zoning.md).

**Neither cloud nor direct is the sole path.** A deep-research pass (2026-07-02, 104 agents / 22
primary HPE sources / 19 verified claims) confirmed both as first-class and **refuted** both
"everything is one cloud endpoint/token" and "DR is CLI-only." So the platform routes each capability
to whichever surface supports it, behind one abstraction.

## Why (verified findings)

- **DSCC is a genuine public REST cloud control plane.** Auth = OAuth2 **client-credentials** →
  short-lived bearer token; writes are **asynchronous** (`202 Accepted` + `taskURI`, then poll the
  task to a terminal state). Documented block resource model: `storage-systems`, `storage-pools`,
  `host-initiator-groups`, `host-initiators`, `volumes`, `volume-sets`, `protection-templates`,
  `tasks` (`/api/v1/<group>/<resources>`). **Replication** (Remote Copy as *protection policies*),
  **snapshots**, and **latency/IOPS/throughput telemetry** are all cloud-exposed.
- **WSAPI is proven first-class direct.** HPE's own CSI driver provisions the Alletra MP B10000
  straight over WSAPI on :443 and only falls back to SSH for *legacy 3PAR*. Our lab array is
  **live-verified** at WSAPI **v1.15.0, `/api/v1`, :443**, OS 10.5.51 — trust that over the
  docs (which were inconclusive on v1 vs v3).
- **Two coexisting cloud surfaces** (HPE is mid-migration):
  - *legacy/native* — region-specific base URLs (`us1|eu1|jp1|uk1.data.cloud.hpe.com`),
    ~120-minute token, async under `/api/v1/tasks/{id}`.
  - *newer/unified* — `global.api.greenlake.hpe.com`, **15-minute** token, async under
    `/data-services/v1beta1/async-operations`.
  Our onboarding (Component A) already uses the **global** surface + the `sso.common.cloud.hpe.com`
  token endpoint.

## Design

- **A control-plane client abstraction** hides the three moving parts the two cloud surfaces differ
  on: **base URL** (regional vs global), **token lifetime** (120 vs 15 min → refresh proactively),
  and the **async path** (`/tasks` vs `/async-operations`). One interface, swappable backend.
- **Capability routing:** every capability declares its surface — *cloud-preferred* (discover /
  provision / replicate / snapshot / report → DSCC where entitled, WSAPI fallback for depth),
  *direct-only* (low-level array ops WSAPI/SSH), *switch* (FC zoning), *host* (pre-zoning WWPN
  capture / multipathing). The router picks per capability + per entitlement, not per run.
- **Discovery-first stays** ([ADR 0002](0002-provisioning-driven-by-discovery.md)): the platform
  reads the environment, never hand-typed data — the operator's "it must be automatic."

## Considered options

- **Pure cloud (DSCC only)** — rejected: B10000 cloud coverage is *partially inferred* (the resource
  model is documented for 9K/6K/Primera/Nimble; B10000 onboards to DSCC but exact per-endpoint
  schemas — a `deviceType` discriminator — need live confirmation), WSAPI exposes depth the cloud may
  not, and **workspace entitlements vary** (a client may lack File / DR / Block-Manager scopes).
- **Pure direct (WSAPI/SSH per array)** — rejected: no multi-array orchestration, no cloud-native
  replication/telemetry, and it reinvents what DSCC already gives. This is the *current tool's*
  ceiling and the thing this ADR moves beyond.
- **Hybrid, routed per capability** — chosen.

## Consequences

- **Build-ready now** (verified): block provisioning, cloud auth + async model, Brocade zoning,
  block replication modes, DSCC telemetry.
- **NOT yet specifiable** — needs a targeted research pass and/or teammate input before building:
  the **File control plane** (GL4F / Alletra MP Unified File — the single biggest gap, half of
  [SCOPE.md](../SCOPE.md)); **DR failover/failback** trigger API + **Peer Persistence / Quorum
  Witness** mechanics; **Cisco MDS** zoning (only Brocade verified); **Ethernet VLAN/LAN**
  automation; **InfoSight** telemetry specifics; **as-built / HLD / LLD** doc generation.
- **Entitlements are the gate.** What our workspace's GreenLake API client is licensed and RBAC-scoped
  for decides how much rides on the cloud plane vs. direct array — confirm with the account team.
- **Migration path for the existing tool:** today's block provisioning is *direct WSAPI* (Phase 2).
  Under this ADR it becomes the "direct" tier beneath the new DSCC cloud client; nothing already
  shipped is thrown away — the cloud client is added *above* it and preferred where entitled.

## Sources (deep research, 2026-07-02)

- HPE DSCC public REST API — getting started: <https://developer.hpe.com/blog/getting-started-with-the-hpe-data-services-cloud-console-public-rest-api/>
- DSCC developer home: <https://developer.hpe.com/greenlake/data-services-cloud-console/home/>
- DSCC block resources via Ansible: <https://developer.hpe.com/blog/creating-dscc-block-storage-resources-using-dscc-ansible-playbooks/>
- Alletra MP B10000 CSI driver (WSAPI direct on :443): <https://scod.hpedev.io/csi_driver/container_storage_provider/hpe_alletra_storage_mp_b10000/index.html>
- Block replication protection policies (DSCC): HPE doc `sd00003451`
- Data Ops Manager performance/telemetry (DSCC): HPE doc `sd00005943`
- Brocade FOS advanced zoning (`cfgadd`/`cfgenable`): <https://techdocs.broadcom.com/us/en/fibre-channel-networking/fabric-os/fabric-os-administration/9-1-x/Administering-Advanced-Zoning-AG/v26770788/v26770854.html>
