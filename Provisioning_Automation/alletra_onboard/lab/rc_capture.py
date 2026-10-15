import getpass, os, re, sys, json
import paramiko

OUT = sys.argv[1]
ARRAYS = [("D22U27", "10.64.122.99"), ("E18U31", "10.64.154.190")]
USER = "3paradm"
WSAPI_GETS = ["/remotecopy", "/remotecopygroups", "/remotecopygroups/rcopy_async_test", "/remotecopylinks"]
READS = [
    "showsys", "showsys -d", "showversion", "showversion -a", "shownet",
    "showport", "showport -rcip", "showport -iscsi", "showrctransport -rcip",
    "showrcopy", "showrcopy -d", "showrcopy links", "showrcopy targets", "showrcopy groups",
    "showrcopy -d groups", "showrcopy groups rcopy_async_test", "showrcopy -qw targets",
    "showvvset", "showcpg", "showsched", "showtask", "srstatrcvv -hourly",
]
HELP = [
    "startrcopy", "controlport", "creatercopytarget", "admitrcopylink", "dismissrcopylink",
    "removercopytarget", "creatercopygroup", "setrcopygroup", "admitrcopyvv", "startrcopygroup",
    "stoprcopygroup", "dismissrcopyvv", "removercopygroup", "syncrcopy", "showrcopy",
    "showrctransport", "srstatrcvv",
]
COMMANDS = READS + ["help " + c for c in HELP]


def read_only(cmd):
    base = cmd.split()[0]
    return (base.startswith("show") or base in ("srstatrcvv", "help")) and not re.search(r"[;|&`$<>]", cmd)


def capture(label, host, pw):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username=USER, password=pw, timeout=20, allow_agent=False, look_for_keys=False)
    folder = os.path.join(OUT, label)
    os.makedirs(folder, exist_ok=True)
    index = []
    for cmd in COMMANDS:
        if not read_only(cmd):
            raise SystemExit("refused (not read-only): " + cmd)
        try:
            _i, o, e = c.exec_command(cmd, timeout=180)
            text = o.read().decode("utf-8", "replace")
            err = e.read().decode("utf-8", "replace")
        except Exception as exc:
            text, err = "", "ERROR " + type(exc).__name__ + ": " + str(exc)
        name = re.sub(r"[^A-Za-z0-9]+", "_", cmd).strip("_") + ".txt"
        with open(os.path.join(folder, name), "w", encoding="utf-8", newline="\n") as f:
            f.write("# " + cmd + "\n" + text + (("\n# stderr\n" + err) if err.strip() else ""))
        index.append("%-45s %6d lines%s" % (cmd, text.count("\n"), "  (stderr)" if err.strip() else ""))
        print(label, "|", index[-1])
    c.close()
    with open(os.path.join(folder, "_index.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(index) + "\n")


def capture_wsapi(label, host, pw):
    folder = os.path.join(OUT, label, "wsapi")
    os.makedirs(folder, exist_ok=True)
    try:
        from hpe3parclient.client import HPE3ParClient
    except ImportError:
        print(label, "| wsapi: hpe3parclient not importable, skipped")
        return
    client = HPE3ParClient("https://%s:443/api/v1" % host, secure=False, timeout=30, suppress_ssl_warnings=True)
    try:
        client.login(USER, pw)
    except Exception as exc:
        print(label, "| wsapi login: %s %s" % (type(exc).__name__, exc))
        return
    try:
        with open(os.path.join(folder, "version.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(client.getWsApiVersion(), f, indent=2, sort_keys=True)
        for path in WSAPI_GETS:
            name = re.sub(r"[^A-Za-z0-9]+", "_", path).strip("_") + ".json"
            try:
                _resp, body = client.http.get(path)
                payload, note = body, ""
            except Exception as exc:
                payload, note = {"error": type(exc).__name__, "detail": str(exc)}, "  (error)"
            with open(os.path.join(folder, name), "w", encoding="utf-8", newline="\n") as f:
                json.dump(payload, f, indent=2, sort_keys=True, default=str)
            print(label, "| wsapi GET %-45s -> %s%s" % (path, name, note))
    finally:
        try:
            client.logout()
        except Exception:
            pass


pw = getpass.getpass("3paradm password for both arrays: ")
for label, host in ARRAYS:
    for attempt in (1, 2):
        try:
            capture(label, host, pw)
            capture_wsapi(label, host, pw)
            break
        except paramiko.AuthenticationException:
            pw = getpass.getpass("Login failed on %s - password for %s: " % (host, label))
        except Exception as exc:
            print("%s (%s): %s %s" % (label, host, type(exc).__name__, exc))
            break
print("Saved under", OUT)
