# The Initialization accelerator is a build *profile* of one codebase, not a fork

The onboarding-only flow is shipped as a **separate, restricted release — "Alletra MP Initialization"**
— for field engineers who only need to *initialise* an array, while the full block+file platform
stays the ongoing "enhancement" track. It is built from **one codebase** selected by a **baked build
flag `ALLETRA_PROFILE`** (`full`, default | `init-only`) — **not** a fork, and **not** a runtime toggle
in the full app. The full app is untouched (the flag defaults off).

## What `init-only` changes vs `full`

| | `full` (default) | `init-only` (the accelerator) |
|---|---|---|
| Sheet template | Initialisation + **Provisioning** + Prerequisites | Initialisation + Prerequisites (**no Provisioning tab**) |
| Upload validation | complete superset ([ADR 0005 rev](0005-decouple-onboarding-into-modes.md)) | **onboarding fields only** (`required_keys_for(FULL_ONBOARDING)`) |
| Mode chooser | all modes | **Initialization only** |
| Title | Alletra MP B10000 Onboarding | **Alletra MP Initialization** |

## Why a profile, not a fork or a runtime toggle

- **Not a fork** — a second codebase diverges immediately; every fix would need porting. The mode/step
  registry ([ADR 0005](0005-decouple-onboarding-into-modes.md)) and conditional sheet validation
  already scope behaviour, so a profile reuses all of it.
- **Not a runtime toggle** in the full app — the accelerator is a *distinct release for a different
  audience* (field engineers who must not see provisioning). It must ship as its own artifact with a
  restricted sheet, not a hidden switch.
- **The sheet had to change too, not just the mode.** Because [ADR 0005 (rev)](0005-decouple-onboarding-into-modes.md)
  makes the *full* app validate a **complete** sheet (incl. the Provisioning tab) *before* the mode is
  chosen, restricting the mode chooser alone would still block upload without provisioning creds. So
  `init-only` also reverts to onboarding-only sheet + validation — which is the pre-v0.5.0 behaviour.

## Wiring

- `config.alletra_profile` (env `ALLETRA_PROFILE`) + `init_only` / `app_title` properties.
- `GET /app/profile` → the UI reads it to brand the title and lock the mode to Initialization.
- `build_template_bytes(init_only=)` omits the Provisioning tab; `/init-sheet/upload` validates
  onboarding-only when init-only.
- The exe **bakes** the profile: `alletra_onboard.spec` writes `build_profile.txt` from build-time
  `ALLETRA_BUILD_PROFILE`; `app_main._apply_build_profile()` exports `ALLETRA_PROFILE` at startup.
- `scripts/build_exe.ps1 -Profile init-only` → `alletra-mp-initialization-win64.zip` (slim, prefers an
  installed Chrome/Edge); CI (`exe.yml`) builds + publishes it beside the full slim/offline artifacts.

## Considered options

- **Separate fork / repo** — rejected: divergence + double maintenance.
- **Runtime toggle inside the full app** — rejected: the accelerator is a restricted, separately
  branded *release*, not a setting a full-app operator could flip into provisioning.
- **Build profile (one codebase, baked flag)** — chosen.

## Consequences

- Two artifacts from one CI run; **the full app is verified unaffected** (default off — 130 tests pass,
  and a live drive of the default build shows the complete-sheet gate + all modes + title intact).
- Released in **v0.6.0** (commit `1cab539`).
- **Known cosmetic gap:** the exe/folder is still named `AlletraOnboard` in both builds — only the zip
  name + the in-app title distinguish the accelerator. Renaming the exe was deferred to keep the shared
  spec/build low-risk.
- **CI robustness:** the init-only build step runs after the full builds and is currently *fatal* — if
  it failed, it would block the release publish (the full app code is still fine). Making it non-fatal
  is an open option.
- **Deferred enhancements** (Panduranga's "enhancement to the existing tool" track — do NOT forget):
  1. **Prereq PROXY field** — the tool-not-using-proxy issue on the storage jump box. Add a UI proxy
     that writes `HTTPS_PROXY`/`HTTP_PROXY`/`NO_PROXY` to `.env` + `os.environ`, and make the
     connectivity test proxy-aware (test HTTPS *through* the proxy, bypass localhost/169.254.*).
  2. **Discovery FC + iSCSI port listing** — broaden `array_target_ports` (today FC-only, ready-only)
     to list **all** FC *and* iSCSI target ports with WWPN/IP + state, grouped in the UI. Needs
     `protocol`/`address` on `ArrayPort` and `fabric` optional (odd/even is FC-only).
