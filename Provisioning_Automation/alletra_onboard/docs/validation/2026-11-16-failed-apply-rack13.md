# Live validation: a failed apply keeps its undo (BL-45), the Console refuses `showtarget -rescan` (BL-46), rack13-ARCUS, 2026-11-16

Run from the developer's Mac on the training network, `test/bl-45-46-live` 30a1b8aa (both fixes),
app from source (`onboard api`, UI built from the same commit), driven by `lab/failed_apply_lab.py`
with `FA_SHEET` = the rack13 initialisation workbook and `FA_HOST=10.132.30.136`. Run `aa3d93c5`,
23:06–23:08 IST. **Wrote to rack13-ARCUS and removed everything it wrote.**

**Outcome: 21 PASS, 0 FAIL.** The apply stopped at the second volume, which the array refused; the
error named it; the removal set was exactly the three objects made before it, in paste order; the page
showed the failure, the count and the undo at 1366 and 1080 wide; after *Rebuild plan* the made
objects read *Exists*, the undo stayed on the page and the approval tick was clear; the as-built
carried the error and the removal lines; the failed apply's own removal set left the array as it was.
The Console refused `showtarget -rescan` on screen and over the API, recorded the refusal and sent
nothing; `showtarget` still ran.

## Environment

| | |
|---|---|
| Array | rack13-ARCUS · CZ2D2K014S · 10.132.30.121 · OS 10.6.0 |
| vCenter, switches | from the rack13 workbook (read for discovery only) |
| Host | `10.132.30.136` (ESXi, FC `10005CED8C5312A8`/`A9`). Not on the array before the run, and not zoned on both fabrics, so no export could have been made even if one had been asked for |

Sheet composed through `POST /init-sheet/compose`: host set `zz_bl45_hs` with `10.132.30.136`;
volumes `zz_bl45_vol01` (1 GiB tpvv, SSD_r6) and `zz_bl45_vol02` (1 PiB tpvv, SSD_r6) in
`zz_bl45_vvs`; no export. Mode *Provision only*.

## What happened

| Step | Result |
|---|---|
| Build plan | host `10.132.30.136`, `zz_bl45_hs`, both volumes and `zz_bl45_vvs`: *create*; 0 blockers. Notes: the host is not reachable on both fabrics, so exports would wait (none asked for) |
| Create | Writes: `POST /hosts` (10.132.30.136, both WWNs, persona 8), `POST /hostsets` zz_bl45_hs, `POST /volumes` zz_bl45_vol01 (1024 MiB), `POST /volumes` zz_bl45_vol02 (1073741824 MiB) — refused: *HTTP 400 code 28, client request contains value that is too large* |
| Result | `storage.apply.failed`, *Stopped while creating volume zz_bl45_vol02: …*; created: the host, the host set, zz_bl45_vol01; removal set `removevv -f zz_bl45_vol01`, `removehostset -f zz_bl45_hs`, `removehost 10.132.30.136` |
| Page (1366, 1080) | *Creation reported an error*, the message, *3 objects were created before it stopped; the removal set below undoes them*; primary *Rebuild plan*, no *Create*; step list *stopped during create* |
| Rebuild plan | host, host set, zz_bl45_vol01 *Exists (was create)*; zz_bl45_vol02 and the set *Create*; *Undo what this run created — 3 removal commands*; tick clear |
| Console (BL-46) | typed `showtarget -rescan`: refused on screen; command log: *refused: 'showtarget -rescan' is not a read: it makes the peer ports rescan for targets (console)*, nothing sent. API: refused; `showtarget` ran (*No targets configured*) |
| As-built | provisioning section: *Provisioning stopped with an error*, the three removal lines |
| Removal | the failed apply's own set over SSH: *Removing VV zz_bl45_vol01*, then the host set and the host without a message; afterwards `showhost 10.132.30.136` *no hosts listed*, `showvv zz_bl45*` *no vv listed*, `showhostset zz_bl45*` *No host set listed* |

## Earlier attempts the same evening

- Run `e64d7d24`: the script waited for *Continue with N zoned hosts* on SAN zoning; no host was zoned
  on rack13, so the button never came. Stopped before *Build plan*; nothing written. The script now
  opens Provision storage from the step list.
- Run `769d5b0b`: 17 PASS, 4 FAIL. The script assumed the host was already on the array; it was not,
  so the apply made it and the removal set rightly removed it. All four FAILs were that assumption;
  the product did what this record describes. The script now reads from the plan whether the host is
  new. Everything removed by the run's own set; `showhost 10.132.30.136` *no hosts listed* afterwards.

## Seen, not changed

- The array's reason appears twice in the message (*value that is too large: Bad request (HTTP 400) 28
  - client request contains value that is too large*): the WSAPI client's error wording, before BL-45.
- The tool accepts a 1 PiB volume on the sheet and in the plan; only the array refuses it. A size
  check before the plan would be kinder, and is a separate item.

Evidence: `~/Downloads/failed_apply.zip` (this run) and `failed_apply-run1-2026-11-16.zip` (run
`769d5b0b`) on the developer's Mac: report, API events, command log, screenshots, as-built.
