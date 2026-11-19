# Live validation: schema versions, stored credentials encrypted, pending sheets expire (BL-65), rack13-ARCUS, 2026-11-19

Run from the developer's Mac, branch `debt/a-credentials-and-schema` (fd4f2a39), app from source on
`127.0.0.1:8781` with its own state database in a fresh folder, under the lab lock. Array, vCenter and
switches from the rack13 initialisation workbooks, read by the app's parser (`fl.sheet_targets`); no
password, key or subscription key printed or saved. 20:50–21:10 IST. **`failed_apply_lab.py` wrote to
rack13-ARCUS and removed everything it wrote;** everything else was read-only. The demo pair's checks
(`demo_prep.py check`, `demo_objects.py check`) were all READY before and after.

| Check | Result |
|---|---|
| `lab/failed_apply_lab.py` (run `028736a1`) | **27 PASS, 0 FAIL** |
| `lab/ui_live_lab.py`, read-only (run `6fe5be3c`) | **23 PASS, 0 FAIL** |
| Initialisation screens in headless Chrome, `..._COMPLETE.xlsx`: upload, *Full onboarding*, *Create run · 5 steps*, the GreenLake registration page (run `9439fe24`; *Register the array* not pressed) | Every page opened, no script error. `GET /runs/{id}` returns the work item (subscription key masked) and the array credential |
| The run's stored work item read back by the store, compared in code with the workbook | serial, subscription key, array, vCenter and both switch passwords: all equal |
| Plain text in the database (`state.db` rows and the `state.db`/`-wal` files, every secret of both workbooks, GreenLake client secret included) | **none found**; 33 sealed values. `secrets.key` made next to the database, mode 0600 |
| App restarted on the same database | all 3 runs and their credentials load; *Verify* on run `6fe5be3c` with no password sent: `verify.completed`, the same result as before the restart |
| A copy of `demo-2026-11-18.db` (plain-text rows, no `user_version`) opened by the app | its run, its work item and its credential load over the API; `user_version` 0 → 1; no key file made; the original's three files unchanged (SHA-256) |
| Copies of `demo-2026-11-18.db`, `demo-2026-11-19.db` and `rehearsal.db` loaded by the old store (main @ 8f89125c) and by this one | every run, event, command, device pin, artifact, work item and intent loads identically, secrets included (compared as digests); originals unchanged |

Not seen live: a database whose key is missing or from another computer (unit tests only), the 24-hour
expiry of an uploaded sheet (unit tests only), and Windows (`%LOCALAPPDATA%` and file permissions).
