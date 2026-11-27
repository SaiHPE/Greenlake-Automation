# Live validation: BL-66 opt-in Brocade SAN switch zoning apply (rack13 + SW-F1/SW-F2)

**Date:** 2026-11-27 · **Branch:** `feat/bl-66-brocade-zoning-apply` · **Head:** `0acdc165` · **ADR:** [ADR 0033](../adr/0033-opt-in-brocade-zoning-apply.md)

## Target hardware

- **Array:** `rack13-ARCUS` (`10.132.30.121`, serial `CZ2D2K014S`)
- **Fabric F1 switch (read-only during test):** `SAN6700R13U38` (`10.132.30.111`, FOS `v9.2.0b1`, cfg `rack13_F1_cfg`)
- **Fabric F2 switch (apply + removal + abort probe):** `SAN6700R13U40` (`10.132.30.112`, FOS `v9.2.0b1`, cfg `cfg1`)

## Driver and evidence

- **Script:** `lab/zoning_apply_lab.py` against the local app API (`http://127.0.0.1:8797`), using the rack13 initialisation workbook (`UI_SHEET`).
- **Evidence archive:** `~/Downloads/zoning_apply.zip` (pre/post `cfgshow` captures, `zoning-plan.json`, `zoning-render.json`, `zoning-apply-event.json`, `removal-output-10.132.30.112.json`, `report.txt`).

## Results (`21 pass, 0 fail`)

| Check | Result | Notes |
|---|---|---|
| 1. Pre-flight on SW-F1 and SW-F2 | PASS | Zero open transactions (`cfgtransshow`), zero `zz_za_*` objects; SW-F2 active effective cfg `cfg1` |
| 2. Upload, Discovery, Zoning plan, Render 1 test pair | PASS | Strictly verified `apply_fabrics` held only F2 (`even`), 2 `zz_za_*` aliases (`zz_za_eljr_hba2`, `zz_za_rack13_033`), and 1 `zz_za_*` zone (`zz_za_eljr_hba2_zz_za_rack13_033`) |
| 3. Wrong `approved_plan` refusal | PASS | `POST /runs/{id}/zoning/apply` returned HTTP `409` and sent zero switch writes |
| 4. Opt-in switch apply (`cfgenable "cfg1" -f`) | PASS | `zoning.applied` succeeded; live SW-F2 `cfgshow` confirmed `zz_za_eljr_hba2_zz_za_rack13_033` in **Effective configuration** with exact planned member WWPNs and no open transaction |
| 5. App-generated removal set | PASS | All 5 removal lines validated (`cfgremove`, `zonedelete`, 2× `alidelete`, `cfgenable "cfg1" -f`) and executed on SW-F2; zero `zz_za_*` traces, `Defined == Effective`, zero open transactions |
| 6. Live `cfgtransabort` across channels on one SSH session | PASS | Channel 1 ran uncommitted `alicreate "zz_za_abort_probe",...`; Channel 2 `cfgtransshow` confirmed active transaction token (`0x5446`); Channel 3 `cfgtransabort` cleared it (`There is no outstanding zoning transaction`); alias did not persist |
| 7. Guaranteed dual-switch `finally` sweep | PASS | Both SW-F1 and SW-F2 verified clean (`leftover=[]`, no open transaction) |
