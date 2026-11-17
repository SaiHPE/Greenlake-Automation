# `multipath -ll`: two lab captures, and samples from published documents (BL-36)

**Lab capture.** `rhel89_lab_2026-11-16_not_set_up.txt`: the lab Linux host 10.54.159.49 (RHEL 8.9,
hostname `localhost.localdomain`), 2026-11-16 13:48 EST, as root over SSH from the labrat jump box, the
read-only commands of `lab/multipath_capture.py` typed by hand (`multipath -ll`, `cat
/sys/module/dm_multipath/initstate`, `hostname`, plus `ls -l /etc/multipath.conf` and `lsmod | grep -i
multipath`), stderr and stdout together, each with its exit status. The *not set up* case: no
`/etc/multipath.conf`, the DM multipath driver not loaded, `multipath -ll` exits 1. The login banner
is left out. (The script's own login failed that day only because it was given the wrong password.)

**Lab capture, the tool's own read.** `rhel89_lab_2026-11-17_tool_read/`: the tool's own
`LinuxHostClient` as root on 10.54.159.49, 2026-11-17, via `lab/labrat_captures.py multipath` (which
runs `lab/multipath_capture.py`); result state `not_set_up`. Each `<key>.txt` is `# <command>`, `# exit
<N>`, then stdout (the client does not keep stderr): `multipath -ll`, `sudo -n multipath -ll` and the
initstate read all exit 1. `summary.txt` is the summary the tool made of them, `report.txt` the script's
report. Its first check still has its old name, *multipath -ll listed*; it means the read was permitted
(the state was not `not_permitted`), which is what the check is called now. Data only, copied as saved;
the run's console log is left out (it named a folder on the jump box).

**Documented samples, NOT lab captures:**

No lab Linux host has multipath set up with an Alletra volume presented (the one Linux host read so
far, 2026-10-05, had no `/etc/multipath.conf` and dm-multipath not loaded). Until one exists, the
Linux multipath parser is pinned to the output printed in these documents. Each file is the command's
output only (the `# multipath -ll` prompt line removed), copied from the document's text on
2026-11-16. Column spacing is as the document's text gives it.

| File | Source |
|---|---|
| `hpe_primera_rhel_guide_p67_documented_sample.txt` | *HPE Primera Red Hat Enterprise Linux Implementation Guide*, part 20-PRI600-RHIG-ED4, edition 4, October 2021, page 67, step 4 of *Provisioning storage and host LUN discovery*. One 3PARdata VV, 4 paths, all `active ready running`. <https://support.hpe.com/hpesc/public/docDisplay?docId=a00088902en_us> |
| `hpe_primera_rhel_guide_p76_documented_sample.txt` | The same guide, page 76, the example before removing LUN 2. One 3PARdata VV named by its WWID, 4 paths. The header line ends in a space, as in the document. |
| `suse_sles15sp6_storage_guide_documented_sample.txt` | *SUSE Linux Enterprise Server 15 SP6 Storage Administration Guide*, section 18.14.2 *Interpreting multipath I/O status* (`multipathd show topology`, which the guide says has the same format as `multipath -ll`). The guide's callout numbers are removed. A NetApp device with a user-friendly name and two path groups: it must NOT be counted as an Alletra device. <https://documentation.suse.com/sles/15-SP6/html/SLES-all/cha-multipath.html#sec-multipath-best-practice-status> |

**Replace these with a real capture.** `lab/multipath_capture.py` logs in to the lab Linux host with
the app's own read-only client and saves what `multipath -ll` (and `sudo -n multipath -ll`) printed,
with exit codes. Once a Linux host has an Alletra volume presented over two fabrics, run it, scrub the
output (no customer names or addresses), save it here as `<host>_<date>_multipath_ll.txt`, and point
`tests/unit/test_host_reads.py` at it. Path states other than `active ready running` (a failed path,
a path whose device is gone, a check still pending, a map that lost every path) have no sample yet; the
tests for those use device objects, or single lines written in the test and marked there as synthetic.
