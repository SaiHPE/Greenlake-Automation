"""SPEC-020 on ONE array while the peer (E18U31) is degraded: the real checkrclink output format and the
tool's sequence, with the test server on D22U27's second RCIP port and the client on its first.
Starts and stops a test process; changes no configuration. No prompts.

    python lab\\rc_link_solo_lab.py

1. reads showport -rcip on D22U27 (two RCIP ports)
2. by hand, saving every answer: stopserver (nothing running), startserver on port 2 toward port 1's
   address, startclient on port 1 toward port 2's address (read until the latency), stopclient,
   stopserver, stopserver again
3. the same through the product's _check_pair (what the app runs)
Writes PASS/FAIL lines to report.txt; everything goes in ~\\Downloads\\rc_link_solo.zip.
"""
import json
import os
import shutil
import time
import traceback

import rc_failover_lab as fl

from alletra_onboard.adapters.array.cli_client import ArrayCliClient, ArrayCliError
from alletra_onboard.application.replication import link_check
from alletra_onboard.domain.replication import LinkPair

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "rc_link_solo")
fl.OUT = OUT
ARRAY_PW = fl.lab_secret("LAB_ARRAY_PW")
P_HOST = "10.64.122.99"
RESULTS = []


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def rcip_ports(cli):
    ports = []
    for line in cli.run("showport -rcip").splitlines():
        t = line.split()
        if len(t) >= 4 and t[0].count(":") == 2 and t[3].count(".") == 3:
            ports.append((t[0], t[3]))
    return ports


def say(label, text):
    first = (text.strip().splitlines() or ["(no output)"])[0]
    print("  %s -> %s" % (label, first[:120]))
    fl.save(label.replace(" ", "_").replace(":", "-") + ".txt", text)
    return text


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    try:
        fl.ssh(P_HOST, ARRAY_PW).close()
    except Exception as exc:  # noqa: BLE001
        check("D22U27 reachable over SSH", False, "%s: %s" % (type(exc).__name__, exc))
        return
    cli = ArrayCliClient(P_HOST, "3paradm", ARRAY_PW)
    cli.connect()
    ports = []
    try:
        ports = rcip_ports(cli)
        fl.save("showport_rcip.txt", cli.run("showport -rcip"))
        if not check("D22U27 has two RCIP ports with addresses", len(ports) >= 2, str(ports)):
            return
        (p1, ip1), (p2, ip2) = ports[0], ports[1]
        print("client side %s %s  ->  server side %s %s" % (p1, ip1, p2, ip2))

        fl.banner("By hand: the six commands, every answer saved")
        t = say("1 stopserver nothing running", cli.run_diagnostic("checkrclink stopserver %s" % p2))
        t = say("2 startserver", cli.run_diagnostic("checkrclink startserver %s %s" % (p2, ip1)))
        check("startserver answers 'Starting Server'", "starting server" in t.lower(), t.strip().splitlines()[0] if t.strip() else "(no output)")
        time.sleep(2)
        t0 = time.time()
        t = say("3 startclient until latency", cli.run_diagnostic("checkrclink startclient %s %s 600" % (p1, ip2),
                                                                  until=link_check.UNTIL, timeout=link_check.LATENCY_WAIT_S))
        took = time.time() - t0
        latency, lost = link_check.parse_client_output(t)
        check("the client printed the latency within %.0f s" % took, latency is not None, "latency %s ms, pings lost %s %%" % (latency, lost))
        check("the client was read in under 2 minutes (not the 600 s test)", took < 150, "%.0f s" % took)
        t = say("4 stopclient", cli.run_diagnostic("checkrclink stopclient %s" % p1))
        t = say("5 stopserver", cli.run_diagnostic("checkrclink stopserver %s" % p2))
        t = say("6 stopserver again", cli.run_diagnostic("checkrclink stopserver %s" % p2))
        check("read the saved answers: 1 and 6 should say nothing was running, 4 and 5 that it stopped", True)

        fl.banner("Through the product: _check_pair on the same array")
        said = []
        pair = LinkPair(nsp_a=p1, ip_a=ip1, nsp_b=p2, ip_b=ip2)
        result = link_check._check_pair(pair, cli, cli, "D22U27", "D22U27(server)", 600, said.append)
        fl.save("check_pair_result.json", result.model_dump_json(indent=2))
        check("_check_pair measured the pair", result.status == "measured" and result.latency_ms is not None,
              result.detail or "latency %s ms, pings lost %s %%" % (result.latency_ms, result.pings_lost_pct))
        check("progress lines in order", said == ["Starting the test server on D22U27(server) %s" % p2,
                                                  "Measuring latency D22U27 %s → %s …" % (p1, ip2),
                                                  "Stopping the client on D22U27", "Stopping the server on D22U27(server)"], json.dumps(said))
        t = say("7 stopserver after check_pair", cli.run_diagnostic("checkrclink stopserver %s" % p2))
        t = say("8 stopclient after check_pair", cli.run_diagnostic("checkrclink stopclient %s" % p1))
        with_bad = None
        try:
            cli.run_diagnostic("checkrclink startclient %s %s 60" % (p1, ip2))
        except ArrayCliError as exc:
            with_bad = str(exc)
        check("a 60 s client is refused by the tool before reaching the array", bool(with_bad and "300 to 172800" in with_bad), with_bad or "ran")
    except Exception as exc:  # noqa: BLE001
        check("stopped: %s" % exc, False)
        fl.save("error.txt", traceback.format_exc())
        if len(ports) >= 2:
            for cmd in ("checkrclink stopclient %s" % ports[0][0], "checkrclink stopserver %s" % ports[1][0]):
                try:
                    say("cleanup " + cmd.split()[1], cli.run_diagnostic(cmd))
                except Exception:  # noqa: BLE001
                    pass
    finally:
        cli.close()


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
            fl.save("report.txt", "\n".join(RESULTS + ["", "%d PASS, %d FAIL" % (len(RESULTS) - fails, fails)]))
            fl.banner("%d PASS, %d FAIL. Send me %s" % (len(RESULTS) - fails, fails, shutil.make_archive(OUT, "zip", OUT)))
