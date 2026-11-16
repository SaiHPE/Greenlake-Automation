"""Every read-only capture the open designs need from the labrat arrays and the lab Linux host, in one
go. READ-ONLY: each script below only runs show / help / checkhealth / srstat commands, WSAPI GETs (with
its own login and logout) or, on the Linux host, `multipath -ll`. No prompts.

    .\\.venv\\Scripts\\python.exe lab\\labrat_captures.py              (all jobs)
    .\\.venv\\Scripts\\python.exe lab\\labrat_captures.py snap_D22U27  (only the jobs named)

Uses the jump box's .env (LAB_ARRAY_PW, LAB_DEFAULT_PW), like every lab script. Each job runs on its own;
one that fails (an array that does not answer) is reported and the next one runs. Everything goes in
~\\Downloads\\labrat_captures.zip: one folder per job with what that script saved, its console output,
and summary.txt.

Every array capture runs once per array, as its own job (snap_<TAG>, iscsi_vlan_<TAG>, ...), so an
array that does not answer costs only its own jobs. An array whose SSH port does not open within 5 s is
skipped and named in the summary.

| Arrays | D22U27 10.64.122.99, E18U31 10.64.154.190, VZ (CRV Vault Zone) 10.64.122.140, LZ 10.64.154.225 |
|---|---|

| Job | Script | Reads | For |
|---|---|---|---|
| snap_<TAG> | snap_capture.py | schedules, snapshots, createsched/createsv help | BL-21 snapshots |
| iscsi_vlan_<TAG> | iscsi_vlan_capture.py | iSCSI ports and their VLANs | BL-25 VLAN |
| peer_ports_<TAG> | peer_port_capture.py | FC port modes (E18U31 had two peer ports) | BL-26 peer ports |
| handover_<TAG> | handover_capture.py | alerts, capacity, System Reporter | BL-24 health report |
| unified_file_<TAG> | file_capture.py | File ports (D22U27 has four), file CLI help, WSAPI v3 file GETs | BL-28 Unified File |
| multipath | multipath_capture.py | `multipath -ll` on the lab Linux host 10.54.159.49 | BL-36 |
"""
import os
import shutil
import socket
import subprocess
import sys
import time

LAB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(LAB)
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
BUNDLE = os.path.join(DOWNLOADS, "labrat_captures")
ARRAYS = [("D22U27", "10.64.122.99"), ("E18U31", "10.64.154.190"), ("VZ", "10.64.122.140"), ("LZ", "10.64.154.225")]
LINUX_HOST = os.environ.get("LINUX_HOST", "10.54.159.49")
JOBS = []  # (job, script, extra environment, the folder the script writes under Downloads, address to check first)
for _tag, _addr in ARRAYS:
    _one = {"CAPTURE_ARRAYS": "%s=%s" % (_tag, _addr)}
    JOBS += [
        ("snap_" + _tag, "snap_capture.py", {"SNAP_HOST": _addr}, "snap_capture", _addr),
        ("iscsi_vlan_" + _tag, "iscsi_vlan_capture.py", _one, "iscsi_vlan_capture", _addr),
        ("peer_ports_" + _tag, "peer_port_capture.py", _one, "peer_port_capture", _addr),
        ("handover_" + _tag, "handover_capture.py", _one, "handover_capture", _addr),
        ("unified_file_" + _tag, "file_capture.py", _one, "file_capture", _addr),
    ]
JOBS.append(("multipath", "multipath_capture.py", {}, "multipath_capture", LINUX_HOST))
JOB_TIMEOUT_S = 20 * 60


def ssh_open(addr):
    try:
        socket.create_connection((addr, 22), timeout=5).close()
        return True
    except OSError:
        return False


def run(job, script, extra, folder):
    print("\n" + "=" * 70 + "\n%s: %s\n" % (job, script) + "=" * 70, flush=True)
    out_dir = os.path.join(BUNDLE, job)
    os.makedirs(out_dir)
    env = dict(os.environ, **extra)
    env.pop("RCIP_LAB_DIR", None)         # every script writes under Downloads, where this collects it
    started = time.time()
    try:
        proc = subprocess.run([sys.executable, "-u", os.path.join(LAB, script)], cwd=ROOT, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=JOB_TIMEOUT_S)
        text, code = proc.stdout.decode("utf-8", "replace"), proc.returncode
    except subprocess.TimeoutExpired as exc:
        text, code = (exc.stdout or b"").decode("utf-8", "replace") + "\n(stopped after %d min)" % (JOB_TIMEOUT_S // 60), "timeout"
    with open(os.path.join(out_dir, "console.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print("\n".join(text.splitlines()[-12:]))
    saved = os.path.join(DOWNLOADS, folder)
    copied = os.path.isdir(saved)
    if copied:
        shutil.copytree(saved, os.path.join(out_dir, folder))
    last = next((ln.strip() for ln in reversed(text.splitlines()) if ln.strip() and not ln.startswith("=")), "")
    return "%-20s exit %-7s %4ds  %s  | %s" % (job, code, time.time() - started,
                                             "saved" if copied else "NOTHING SAVED", last[:120])


def main():
    wanted = set(sys.argv[1:])
    unknown = wanted - {j[0] for j in JOBS}
    if unknown:
        sys.exit("No such job: %s. Jobs: %s" % (", ".join(sorted(unknown)), ", ".join(j[0] for j in JOBS)))
    if os.path.isdir(BUNDLE):
        shutil.rmtree(BUNDLE)
    os.makedirs(BUNDLE)
    lines, reachable = [], {}
    for job in JOBS:
        if wanted and job[0] not in wanted:
            continue
        addr = job[4]
        if addr not in reachable:
            reachable[addr] = ssh_open(addr)
        if not reachable[addr]:
            lines.append("%-20s skipped: %s does not answer on SSH port 22" % (job[0], addr))
            continue
        try:
            lines.append(run(*job[:4]))
        except Exception as exc:  # noqa: BLE001 - one job's trouble never stops the next
            lines.append("%-20s could not run: %s" % (job[0], exc))
    summary = "\n".join(lines)
    with open(os.path.join(BUNDLE, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summary + "\n")
    print("\n" + "=" * 70 + "\n" + summary)
    print("=" * 70 + "\nSend me %s" % shutil.make_archive(BUNDLE, "zip", BUNDLE))


if __name__ == "__main__":
    main()
