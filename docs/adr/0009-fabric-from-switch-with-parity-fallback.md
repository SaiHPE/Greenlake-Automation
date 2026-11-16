# FC fabric is derived from the switch a port attaches to, with card-port parity as the fallback

Discovery assigns every array FC target port to one of the two SAN fabrics (`odd`/`even`). That label
drives the core zoning check — "is each host logged in on **both** fabrics?" — so getting the
port→fabric mapping right is load-bearing.

**Decision:** derive a port's fabric from the **switch it physically attaches to** (via
`showportdev fcfabric <n:s:p>`), and fall back to **card-port parity** (odd `card_port` → `odd`
fabric, even → `even`) whenever the switch can't be resolved. Overrides and fallbacks are always
surfaced as discovery notes — never silently applied.

## Why this ADR

The original heuristic was **parity alone**: `fabric = "odd" if card_port % 2 else "even"`. That is a
correct assumption *only* for standard dual-fabric cabling (each node's odd ports to fabric A, even to
fabric B). It cannot see a **miscabled** port — if an even port is physically patched into the odd
fabric, parity still calls it "even", and a host that is actually single-fabric is reported as
correctly dual-fabric zoned. The physical truth is which switch a port lands on, and the array already
knows it (`showportdev fcfabric`). This was audit item #3.

## Calibrated against the live fabric

We captured `showportdev fcfabric` for every FC port on the lab Primera A630 (a busy shared Brocade
fabric) before designing this. Finding: the four host ports resolved cleanly to **two switches** —
`…:3` ports → `SW6600_Q5U38_F2`, `…:4` ports → `SW6600_Q5U39_F1` — i.e. the switch grouping and parity
**agree** on this array (parity is correct *here*). So the switch derivation is primarily a
**robustness upgrade** (it catches the case parity can't), not a bug fix for the current environment.
That calibration is why the design must be *conservative*: it should reproduce parity exactly when they
agree, and only diverge with an explanation.

## Design

`resolve_port_fabrics(fc_ports, switch_by_label)` (pure, in `application/storage/discovery.py`):

- **Probe only `ready` ports.** A `loss_sync`/down port isn't attached to a fabric, so
  `showportdev fcfabric` yields nothing — probing it only wastes an SSH round-trip. (On the Alletra MP
  225 today, all host ports are `loss_sync`, so every port falls back to parity — exactly the pre-#3
  behaviour, which is the safe floor.)
- **Exactly two attach-switches ⇒ those *are* the two fabrics.** Map each switch to a slot, preferring
  the slot its own ports' parity implies (so labels stay stable when cabling is standard), and
  **override** parity for any port whose switch disagrees — with a `non-standard cabling` note. If both
  switches sit at the same parity (parity can't name them), assign by stable switch-name order and note it.
- **Anything else (0 / 1 / >2 switches) ⇒ card-port parity**, the documented default. `>2` and the
  genuine single-fabric case (both parities on one switch) are noted; a plain "no data" case (all ports
  down) is silent because parity is the expected default there.
- The resolved switch is stored on `ArrayPort.fabric_switch` and shown in the Discovery UI next to the
  fabric, so the operator can see *why* a port is on a given fabric.

## Considered alternatives

- **Trust the full `fcfabric` switch *set* (the whole mesh view) as the fabric identity** — rejected as
  fragile: on the live array the per-port "fabric view" counts drifted (26 vs 27 switches) across an
  E-Port-connected mesh, so set-equality is noisy. The **attach switch** (the port's own F-Port) is a
  single, unambiguous datum and was clean in calibration.
- **Replace parity entirely with the switch** — rejected: `fcfabric` is empty for down ports and for an
  array whose SAN is offline (the 225 right now). Parity must remain the fallback so discovery never
  loses the fabric label.
- **Keep parity only (status quo)** — rejected: it silently mislabels miscabled ports, which defeats
  the zoning verification the tool exists to provide.

## Consequences

- On standard cabling the result is **identical to parity**, now with the switch shown — zero behaviour
  change, added transparency.
- Miscabling is **caught and explained** instead of passing silently.
- Discovery makes up to one extra `showportdev fcfabric` SSH call per *ready* FC port (typically 4–8);
  acceptable for a once-per-array run, and skipped entirely for down ports.
- `showportdev` was already on the read-only CLI allowlist, so this stays structurally read-only.
- The remaining hardcoded-assumption audit items (region default — done in 0008-era work; VMware
  persona — done) are tracked separately; this ADR closes the fabric one.
