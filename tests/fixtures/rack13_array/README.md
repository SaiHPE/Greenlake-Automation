# rack13arcus array captures — 2026-09-13 00:07 (after provisioning run 2)

Read-only `show*` output from CZ2D2K014S (OS 10.5.55), captured over SSH from the jump box right after
the tool created `10.132.30.136`, `zz_t2_hs`, `zz_t2_vol01..03`, `zz_t2_vvs` and three exports.
Commands were fed on stdin, so the prompt shows no command echo; the file name is the command.

| file | command |
|---|---|
| showhost_d.txt | `showhost -d` (35 rows incl. unclaimed `-- --` logins) |
| showvv.txt | `showvv` (51 rows: system `.mgmtdata`/`.shared.*`/`admin`, snapshots indented as `vcopy`) |
| showvv_s_zz_t2.txt | `showvv -s zz_t2_*` |
| showvvset.txt / showvvset_none.txt | `showvvset` (9 sets, multi-line members, `test.Snapset` empty) / filtered miss |
| showhostset.txt | `showhostset` (6 sets) |
| showvlun_t.txt | `showvlun -t` (3 templates; `set:zz_t2_hs` is Type `host set`) |
| showvlun_a.txt | `showvlun -a` (12 active paths) |
| showcpg.txt | `showcpg` |
| showvv_listcols.txt | `showvv -listcols` + the rejection of `-showcols …UsrCPG,SnpCPG…` (12:33): this OS names the column `CPG` (C-1) |

Pinned by tests/unit/test_asbuilt_provisioned.py (SPEC-002).
