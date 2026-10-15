"""Can 10.64.154.190 be the replication peer of D22U27? READ-ONLY, no prompts.

    python lab\\rc_peer_ready.py
    $env:RC_PEER_PW='<peer 3paradm password>'; python lab\\rc_peer_ready.py   (if the lab set a new one)

1. logs in to the peer (RC_PEER_PW if set, then LAB_ARRAY_PW, then LAB_DEFAULT_PW from .env) and D22U27;
   if the peer refuses, records what its SSH and WSAPI answer, without a login
2. saves what replication needs from both: system, OS, licences, WSAPI, RCIP ports, Remote Copy
   targets, links and groups, CPGs
3. runs the app's own replication read and check on the pair (what the Replication step would say)
Writes PASS/FAIL lines and a verdict to report.txt; everything goes in ~\\Downloads\\rc_peer.zip.
"""
import json
import os
import shutil
import socket
import ssl
import traceback
import urllib.error
import urllib.request

import paramiko

import rc_failover_lab as fl

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "rc_peer")
fl.OUT = OUT
P_HOST, S_HOST = "10.64.122.99", "10.64.154.190"
TRIED = [(n, os.environ.get(n) if n == "RC_PEER_PW" else fl.lab_secret(n)) for n in ("RC_PEER_PW", "LAB_ARRAY_PW", "LAB_DEFAULT_PW")]
PASSWORDS = [pw for _n, pw in TRIED if pw]
READS = ["showsys -d", "showversion", "showlicense", "showwsapi", "showport -rcip", "showrctransport -rcip",
         "showrcopy", "showrcopy links", "showrcopy targets", "showcpg", "showvvset"]
RESULTS = []


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def note(text):
    print("      " + text)
    RESULTS.append("      " + text)


def pw_label(pw):
    """The variable a password came from, so the report never shows the password itself."""
    return next((n for n, v in TRIED if v == pw), "?")


def login(host):
    for pw in PASSWORDS:
        try:
            return fl.ssh(host, pw), pw
        except paramiko.AuthenticationException as exc:
            note("%s with %s: %s %s" % (host, pw_label(pw), type(exc).__name__, exc))
    return None, None


def why_refused(host):
    """What the peer answers without logging in: SSH server, login methods, banner, and whether WSAPI listens."""
    try:
        t = paramiko.Transport(socket.create_connection((host, 22), timeout=10))
    except OSError as exc:
        note("SSH port 22: %r" % exc)
        return
    try:
        t.start_client(timeout=20)
        note("SSH server: %s" % t.remote_version)
        try:
            t.auth_none("3paradm")
            allowed = ["none"]
        except paramiko.BadAuthenticationType as exc:
            allowed = exc.allowed_types
        except paramiko.SSHException as exc:
            allowed = [repr(exc)]
        note("SSH login methods offered to 3paradm: %s" % ", ".join(allowed))
        banner = t.get_banner()
        if banner:
            note("SSH banner: %s" % banner.decode("utf-8", "replace").strip()[:300])
    except paramiko.SSHException as exc:
        note("SSH handshake: %r" % exc)
    finally:
        t.close()
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))
    for url in ("https://%s/api/v1" % host, "https://%s:8080/api/v1" % host, "https://%s/" % host):
        try:
            with opener.open(url, timeout=15) as r:
                note("%s: HTTP %s %s" % (url, r.status, r.read(200).decode("utf-8", "replace").replace("\n", " ")))
        except urllib.error.HTTPError as exc:
            note("%s: HTTP %s" % (url, exc.code))
        except Exception as exc:  # noqa: BLE001
            note("%s: %r" % (url, exc))


def dump(c, tag):
    raw = {}
    for cmd in READS:
        try:
            raw[cmd] = fl.run(c, cmd)
        except Exception as exc:  # noqa: BLE001
            raw[cmd] = "ERROR %r" % exc
        fl.save("%s-%s.txt" % (tag, cmd.replace(" ", "_").replace("-", "")), raw[cmd])
    return raw


def an_existing_set(view):
    """A volume set on D22U27 whose volumes are in no Remote Copy group, to stand in for a Replication row."""
    in_rc = {v.local_name for g in view.groups for v in g.volumes}
    for name, members in sorted(view.vvsets.items()):
        if not name.startswith(("zz_", "RCP_", "RH")) and members and not set(members) & in_rc:
            return name
    return None


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    from alletra_onboard.application.replication.plan import check as rc_check, find_partnership
    from alletra_onboard.application.replication.read import read_array
    from alletra_onboard.domain.replication import ProtectionRequest, ReplicationIntent
    from alletra_onboard.domain.shared import EndpointCreds

    fl.banner("1. Logins")
    s, s_pw = login(S_HOST)
    if not check("log in to the peer %s as 3paradm" % S_HOST, s is not None,
                 "password %s" % pw_label(s_pw) if s else "no password tried works: %s" % ", ".join(map(pw_label, PASSWORDS))):
        why_refused(S_HOST)
        return
    p, p_pw = login(P_HOST)
    if not check("log in to D22U27 %s" % P_HOST, p is not None):
        return

    fl.banner("2. What both arrays have")
    raw_s, raw_p = dump(s, "peer"), dump(p, "D22U27")
    s.close()
    p.close()
    lic = raw_s["showlicense"].lower()
    check("peer licence includes Remote Copy", "remote copy" in lic, "see peer-showlicense.txt")
    check("peer WSAPI is enabled", "enabled" in raw_s["showwsapi"].lower(), raw_s["showwsapi"].strip().splitlines()[-1][:120])

    peer = read_array(EndpointCreds(host=S_HOST, username="3paradm", password=s_pw))
    prim = read_array(EndpointCreds(host=P_HOST, username="3paradm", password=p_pw))
    for name, v in (("peer", peer), ("D22U27", prim)):
        fl.save("%s-view.json" % name, v.model_dump_json(indent=2))
    if not check("the app reads the peer", not peer.read_error, peer.read_error or ""):
        return
    check("the app reads D22U27", not prim.read_error, prim.read_error or "")
    note("peer: %s, serial %s, OS %s" % (peer.name, peer.serial, peer.os_version))
    note("peer CPGs (free MiB): %s" % ", ".join("%s %s" % (k, v) for k, v in sorted(peer.cpg_free_mib.items())))
    ready = [r for r in peer.rcip_ports if r.ip and r.ip not in ("-", "0.0.0.0")]
    check("peer has RCIP ports with an address", bool(ready), "; ".join("%s %s %s" % (r.nsp, r.state, r.ip) for r in peer.rcip_ports) or "none")
    check("Remote Copy is started on the peer", peer.rc_started, "status %s" % (peer.rc_status or "unknown"))
    check("Remote Copy is started on D22U27", prim.rc_started, "status %s" % (prim.rc_status or "unknown"))
    note("D22U27 targets: %s" % ("; ".join("%s (%s, %s)" % (t.name, t.type, t.status) for t in prim.targets) or "none"))
    note("D22U27 links: %s" % ("; ".join("%s %s %s %s" % (l.target, l.nsp, l.address, l.status) for l in prim.links) or "none"))
    note("peer targets: %s" % ("; ".join("%s (%s, %s)" % (t.name, t.type, t.status) for t in peer.targets) or "none"))
    note("peer groups: %d" % len(peer.groups))

    fl.banner("3. The app's replication check on the pair")
    pair = find_partnership(prim, peer)
    if check("partnership between D22U27 and the peer", pair is not None,
             "none: neither array has a target whose links point at the other's RCIP addresses" if pair is None else ""):
        note("target on D22U27 '%s', on the peer '%s'; links up %d/%d and %d/%d" % (
            pair.target_on_primary, pair.target_on_peer, pair.links_primary_up, pair.links_primary_total,
            pair.links_peer_up, pair.links_peer_total))
        check("at least 2 links Up each way", pair.links_primary_up >= 2 and pair.links_peer_up >= 2)
    vvset = an_existing_set(prim)
    cpg = "SSD_r6" if "SSD_r6" in peer.cpg_free_mib else next(iter(sorted(peer.cpg_free_mib)), "SSD_r6")
    check("peer has CPG %s" % cpg, cpg in peer.cpg_free_mib, "the Replication tab names the peer CPG")
    if vvset:
        intent = ReplicationIntent(peer=EndpointCreds(host=S_HOST, username="3paradm", password=s_pw), rtt_ms=1,
                                   protections=[ProtectionRequest(vvset=vvset, peer_cpg=cpg, mode="sync", rpo_minutes=None)])
        report = rc_check(prim, peer, intent)
        fl.save("check.json", report.model_dump_json(indent=2))
        check("the Replication step's check has no blocking finding (sample row: %s, sync)" % vvset, not report.findings)
        for f in report.findings:
            note("finding: " + f)
    else:
        note("no volume set on D22U27 outside Remote Copy to try a sample row with; the check above is the pair only")


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        if os.path.isdir(OUT):
            fl.save("script_stopped.txt", traceback.format_exc())
        raise
    finally:
        if os.path.isdir(OUT):
            fails = sum(1 for r in RESULTS if r.startswith("FAIL"))
            verdict = ("USABLE: the tool can configure replication to this peer now." if fails == 0 else
                       "NOT YET: see the FAIL lines above.")
            fl.save("report.txt", "\n".join(RESULTS + ["", verdict, "%d FAIL" % fails]))
            fl.banner("%s Send me %s" % (verdict, shutil.make_archive(OUT, "zip", OUT)))
