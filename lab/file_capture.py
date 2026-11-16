"""What the lab array's file side looks like, before the tool reads it (BL-28). READ-ONLY, no prompts.

    .\\.venv\\Scripts\\python.exe lab\\file_capture.py

Changes nothing on any array. Logs in as 3paradm with LAB_ARRAY_PW from .env to each array in
CAPTURE_ARRAYS="TAG=address[,TAG=address]" (default D22U27=10.64.122.99, the array with four File ports).
1. Over SSH, show and help only (a guard refuses any other first word):
       showversion, showsys, showport, showport -file, shownet
       help, help help, help -sub, help show       the CLI's command index, in the forms it may take
       help controlport, help showport              the file commands the research note names
       help showfs, help showfpg, help showvfs, help showfshare, help showfstore,
       help showfileservice, help showfilesystem, help showfileshare
                                                    guesses: the old 3PAR File Persona names, and names
                                                    shaped like the WSAPI v3 resources
       help <name> for each file-like command name the help answers above mention (at most 25)
   "No help" or "command not found" answers are saved too: they say whether a file CLI exists.
2. WSAPI v1 (https://<address>/api/v1): POST /credentials, GET /system, GET /wsapiconfiguration,
   DELETE /credentials/<key>.
3. WSAPI v3: POST /api/v3/credentials {"user", "password"}, GET /api/v3/fileservice,
   /api/v3/filesystems, /api/v3/filesharesettings, /api/v3/fileshares, DELETE /api/v3/credentials/<token>.
   Every status is saved, 401 and 404 included: a 404 says the array does not serve that resource.
   When the login is refused the four GETs still go out, without a session, so 401 against 404
   still shows whether the path exists.
4. Prints per array: OS, File ports and their state, which v3 file resources answered, the file
   service flag, and how many file systems, client groups (share settings) and shares there are.
The only POST and DELETE are the logins and logouts, in their own functions; the HTTP helper
refuses every method but GET.

Unconfirmed, so the script records what the array does:
- The v3 port. The research note cites https://<array>/api/v3 (443); a runbook note of 2026-06-26
  says /api/v3 is on 8080. The script logs in on 443 first and tries 8080 only when 443 does not
  answer or answers the login with 404.
- The v3 session. ADR 0021 expects a cookie; v1 returns {"key"} for the X-HP3PAR-WSAPI-SessionKey
  header. The script sends back what the login returned (its cookies, and a body key in that header).
  wsapi_v3_login.json keeps the login answer's header names and body field names, values redacted.
- The v3 logout path: /credentials/<token>, as the work packet writes it; token = the body key,
  else the first cookie's value.
- Whether "help -sub" and "help show" are listing forms of the CLI's help.

Output: RCIP_LAB_DIR (default ~/Downloads)/file_capture/<TAG>/, and file_capture.zip beside it.
Per array: <command>.txt per SSH command ("# command" on line 1), wsapi_v1_<name>.json and
wsapi_v3_<name>.json per answer as {"request", "port", "status", "headers", "body"} (status null =
nothing answered), and _index.txt (line counts, every request and its status). report.txt at the top.

Fixtures: copy <TAG>/ to tests/fixtures/unified_file/<TAG>/ (D22U27: tests/fixtures/unified_file/D22U27/).
Before committing, scrub user names and every address that is not a lab address (a share setting's
client list can name real hosts), and look for session keys, cookies and passwords: the script
redacts the ones it knows and checks the folder for them, but read the files anyway.
"""
import json
import os
import re
import shutil
import ssl
import sys
import traceback
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl  # noqa: E402

USER = "3paradm"
BASE = os.environ.get("RCIP_LAB_DIR") or os.path.join(os.path.expanduser("~"), "Downloads")
OUT = os.path.join(BASE, "file_capture")
fl.OUT = OUT
ARRAYS = [tuple(x.strip().split("=", 1)) for x in
          (os.environ.get("CAPTURE_ARRAYS") or "D22U27=10.64.122.99").split(",") if x.strip()]
if not ARRAYS or any(len(a) != 2 or not a[1] for a in ARRAYS):
    sys.exit('CAPTURE_ARRAYS must read TAG=address[,TAG=address], for example D22U27=10.64.122.99')
READS = ["showversion", "showsys", "showport", "showport -file", "shownet"]
HELP_INDEX = ["help", "help help", "help -sub", "help show"]
HELP_NAMED = ["help controlport", "help showport"]
HELP_GUESSED = ["help showfs", "help showfpg", "help showvfs", "help showfshare", "help showfstore",
                "help showfileservice", "help showfilesystem", "help showfileshare"]
FILE_LIKE = re.compile(r"^(?:show|create|set|remove|start|stop|grow|control|check|stat|hist)"
                       r"[a-z]*(?:file|fs|fpg|fshare|fstore)[a-z]*$")
MAX_FOLLOW = 25
V1_GETS = ["/system", "/wsapiconfiguration"]
V3_GETS = ["/fileservice", "/filesystems", "/filesharesettings", "/fileshares"]
V3_PORTS = [443, 8080]
SAFE_CLI = re.compile(r"^[A-Za-z0-9 ,:._-]+$")
NSP = re.compile(r"^\d+:\d+:\d+$")
TAG_OK = re.compile(r"^[A-Za-z0-9_-]+$")
RESULTS = []

_CTX = ssl.create_default_context()
_CTX.check_hostname, _CTX.verify_mode = False, ssl.CERT_NONE
# No proxy: the arrays are on the lab management network.
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=_CTX))


def note(text):
    print("      " + text)
    RESULTS.append("      " + text)


def check(what, ok, detail=""):
    line = "%s  %s%s" % ("PASS" if ok else "FAIL", what, (" - " + detail) if detail else "")
    print(line)
    RESULTS.append(line)
    return ok


def file_name(cmd):
    return cmd.replace(" -", "_").replace(" ", "_").replace(",", "_").replace(":", "") + ".txt"


# ---- SSH: show and help only ----------------------------------------------------------------------

def cli(c, cmd):
    """One read on the array. The first word must be show* or help, with no shell or Tcl characters."""
    words = cmd.split()
    if not words or not (words[0].startswith("show") or words[0] == "help") or not SAFE_CLI.match(cmd):
        raise ValueError("refused, not a show or help command: %r" % cmd)
    try:
        return fl.run(c, cmd)
    except Exception as exc:  # noqa: BLE001
        return "ERROR %r" % exc


def file_like_names(texts, done):
    """Command names in help answers that look like file commands, not yet asked about."""
    found = []
    for text in texts:
        for word in text.split():
            word = word.strip(",.;:()[]'\"`").lower()
            if len(word) <= 30 and FILE_LIKE.match(word) and "help " + word not in done and word not in found:
                found.append(word)
    return found[:MAX_FOLLOW]


# ---- HTTPS: GET only, plus the session login and logout -------------------------------------------

def _send(req, timeout):
    """(status, headers, body bytes) of one request; status None when nothing answered."""
    try:
        with OPENER.open(req, timeout=timeout) as r:
            return r.status, r.headers, r.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read()
    except Exception as exc:  # noqa: BLE001 - no answer is a fact to record
        return None, None, repr(exc).encode()


def session_headers(session):
    h = {"Accept": "application/json"}
    if session and session.get("key"):
        h["X-HP3PAR-WSAPI-SessionKey"] = session["key"]
    if session and session.get("cookies"):
        h["Cookie"] = "; ".join(session["cookies"])
    return h


def request(method, base, path, session):
    """The only helper for reads: it refuses every method but GET."""
    if method != "GET":
        raise ValueError("refused: %s %s; this capture only reads" % (method, path))
    req = urllib.request.Request(base + path, method="GET", headers=session_headers(session))
    return _send(req, 60)


def login(base, password):
    """POST <base>/credentials. Returns the answer and the session (None unless the login was accepted)."""
    body = json.dumps({"user": USER, "password": password}).encode()
    req = urllib.request.Request(base + "/credentials", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    answer = _send(req, 30)
    status, headers, raw = answer
    if status not in (200, 201):
        return answer, None
    try:
        data = json.loads(raw)
    except ValueError:
        data = {}
    key = data.get("key") if isinstance(data, dict) else None
    key = str(key) if key not in (None, "") else None
    cookies = [c.split(";", 1)[0].strip() for c in (headers.get_all("Set-Cookie") or [])] if headers else []
    if not key and not cookies:
        return answer, None
    return answer, {"key": key, "cookies": cookies}


def logout(base, session):
    """DELETE <base>/credentials/<token>. A failed logout is recorded; the session times out on its own."""
    token = session.get("key") or session["cookies"][0].partition("=")[2]
    req = urllib.request.Request(base + "/credentials/" + urllib.parse.quote(token, safe=""), method="DELETE",
                                 headers=session_headers(session))
    return _send(req, 30)


def secrets_of(session):
    if not session:
        return []
    return [s for s in [session.get("key")] + [c.partition("=")[2] for c in session.get("cookies", [])] if s]


def forms(secret):
    """The secret as written, and as json.dumps escapes it."""
    return {secret, json.dumps(secret)[1:-1]} if secret else set()


def scrub(text, secrets):
    for s in secrets:
        for form in forms(s):
            text = text.replace(form, "<redacted>")
    return text


def header_list(headers, secrets):
    out = []
    for k, v in (headers.items() if headers else []):
        if k.lower() == "set-cookie":
            name, _, rest = v.partition("=")
            v = "%s=<redacted>;%s" % (name, rest.partition(";")[2])
        out.append([k, scrub(v, secrets)])
    return out


def body_of(raw, status):
    if status is None:
        return raw.decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except ValueError:
        return raw.decode("utf-8", "replace")[:50000]


class Recorder:
    """Saves every HTTP answer of one array and keeps its status for the index and the summary."""

    def __init__(self, password):
        self.password = password
        self.secrets = [password]
        self.log = []
        self.status = {}

    def save(self, fname, method, shown_path, port, answer, names_only=False):
        status, headers, raw = answer
        body = body_of(raw, status)
        if names_only and status in (200, 201) and isinstance(body, dict):
            body = {k: "<redacted %s>" % type(v).__name__ for k, v in body.items()}
        record = {"request": "%s %s" % (method, shown_path), "port": port, "status": status,
                  "headers": header_list(headers, self.secrets), "body": body}
        fl.save(fname, scrub(json.dumps(record, indent=1), self.secrets) + "\n")
        self.status[shown_path] = status
        self.log.append("%-6s %-36s port %-4s %s" % (method, shown_path, port,
                                                     status if status is not None else "no answer: " + body[:120]))
        return body


# ---- one array ---------------------------------------------------------------------------------

def capture_cli(tag, host, password):
    fl.banner("%s %s: CLI over SSH (show and help only)" % (tag, host))
    raw = {}
    try:
        c = fl.ssh(host, password)
    except Exception as exc:  # noqa: BLE001
        check("%s SSH login" % tag, False, repr(exc))
        return raw

    def read(cmd):
        raw[cmd] = cli(c, cmd)
        fl.save(file_name(cmd), "# %s\n%s" % (cmd, scrub(raw[cmd], [password])))
        note("%-24s %d line(s)" % (cmd, len(raw[cmd].splitlines())))

    try:
        for cmd in READS + HELP_INDEX + HELP_NAMED + HELP_GUESSED:
            read(cmd)
        for name in file_like_names([raw[k] for k in HELP_INDEX + HELP_NAMED + HELP_GUESSED], raw):
            read("help " + name)
    finally:
        c.close()
    return raw


def capture_v1(host, rec):
    base = "https://%s/api/v1" % host
    answer, session = login(base, rec.password)
    rec.secrets += secrets_of(session)
    rec.save("wsapi_v1_login.json", "POST", "/api/v1/credentials", 443, answer, names_only=True)
    data = {}
    for path in V1_GETS:
        data[path] = rec.save("wsapi_v1_%s.json" % path.strip("/"), "GET", "/api/v1" + path, 443,
                              request("GET", base, path, session))
    if session:
        rec.save("wsapi_v1_logout.json", "DELETE", "/api/v1/credentials/<key>", 443, logout(base, session))
    return session is not None, data


def capture_v3(host, rec):
    tried, chosen, session = [], None, None
    for port in V3_PORTS:
        base = "https://%s%s/api/v3" % (host, "" if port == 443 else ":%d" % port)
        answer, session = login(base, rec.password)
        rec.secrets += secrets_of(session)
        rec.save("wsapi_v3_login%s.json" % ("" if port == 443 else "_%d" % port), "POST", "/api/v3/credentials",
                 port, answer, names_only=True)
        tried.append((port, base, answer[0]))
        if answer[0] is not None and answer[0] != 404:
            chosen = (port, base)
            break
    if chosen is None:
        answered = [(p, b) for p, b, s in tried if s is not None]
        chosen = answered[0] if answered else None
    data = {}
    if chosen is None:
        note("WSAPI v3: nothing answered on port %s; the file GETs were not sent" % " or ".join(str(p) for p in V3_PORTS))
        return None, False, data
    port, base = chosen
    for path in V3_GETS:
        data[path] = rec.save("wsapi_v3_%s.json" % path.strip("/"), "GET", "/api/v3" + path, port,
                              request("GET", base, path, session))
    if session:
        rec.save("wsapi_v3_logout.json", "DELETE", "/api/v3/credentials/<token>", port, logout(base, session))
    return port, session is not None, data


def count(body):
    if isinstance(body, list):
        return len(body)
    if isinstance(body, dict):
        if isinstance(body.get("members"), list):
            return len(body["members"])
        if isinstance(body.get("total"), int):
            return body["total"]
    return "?"


def summarise(tag, raw, rec, v1_ok, v3_port, v3_ok, v3):
    fl.banner("%s: what it says" % tag)
    note("OS: " + next((ln.strip() for ln in raw.get("showversion", "").splitlines()
                        if ln.startswith("Release version")), "?"))
    typed = [ln.split() for ln in raw.get("showport", "").splitlines()]
    typed = [p for p in typed if len(p) >= 6 and NSP.match(p[0]) and p[5] == "file"]
    note("showport Type file: %d %s" % (len(typed), ", ".join("%s %s" % (p[0], p[2]) for p in typed)))
    rows = [ln.split() for ln in raw.get("showport -file", "").splitlines()]
    rows = [p for p in rows if len(p) >= 12 and NSP.match(p[0])]
    for p in rows:
        note("File port %s state %-9s %-18s gateway %s VLAN %s MTU %s link %s failover %s"
             % (p[0], p[2], p[3], p[5], p[6], p[7], p[10], " ".join(p[11:])))
    if not rows:
        note("showport -file: " + (raw.get("showport -file", "").strip().splitlines() or ["(empty)"])[0][:120])
    real_help = sorted(k for k, v in raw.items() if k.startswith("help ") and "SYNTAX" in v)
    note("help answers with a SYNTAX section: " + (", ".join(real_help) or "none"))
    note("v1 login: %s" % ("accepted" if v1_ok else "refused or no answer"))
    note("v3 port: %s, login %s" % (v3_port or "none", "accepted" if v3_ok else "refused or no answer"))
    for path in V3_GETS:
        s = rec.status.get("/api/v3" + path)
        note("GET /api/v3%-18s %s" % (path, "no answer" if s is None else "HTTP %s" % s))
    svc = v3.get("/fileservice")
    if isinstance(svc, dict) and "isFileServiceEnabled" in svc:
        note("file service enabled: %s" % svc["isFileServiceEnabled"])
    for path, label in (("/filesystems", "file systems"), ("/filesharesettings", "client groups (share settings)"),
                        ("/fileshares", "shares")):
        if rec.status.get("/api/v3" + path) == 200:
            note("%s: %s" % (label, count(v3.get(path))))
    check("%s showport -file read" % tag, bool(raw.get("showport -file", "").strip()))
    check("%s WSAPI v1 login" % tag, v1_ok)


def capture(tag, host, password):
    if not TAG_OK.match(tag):
        check("array tag %r" % tag, False, "use letters, digits, _ or -")
        return
    fl.OUT = os.path.join(OUT, tag)
    raw = capture_cli(tag, host, password)
    fl.banner("%s: WSAPI v1 and v3 (GET only, plus login and logout)" % tag)
    rec = Recorder(password)
    v1_ok, _ = capture_v1(host, rec)
    v3_port, v3_ok, v3 = capture_v3(host, rec)
    for line in rec.log:
        note(line)
    index = ["%-24s %5d lines" % (cmd, len(text.splitlines())) for cmd, text in raw.items()]
    fl.save("_index.txt", "\n".join(index + [""] + rec.log) + "\n")
    summarise(tag, raw, rec, v1_ok, v3_port, v3_ok, v3)
    leaks = []
    for name in sorted(os.listdir(fl.OUT)):
        with open(os.path.join(fl.OUT, name), encoding="utf-8") as f:
            text = f.read()
        if any(form in text for s in rec.secrets for form in forms(s)):
            leaks.append(name)
    check("%s no password, session key or cookie in the saved files" % tag, not leaks, ", ".join(leaks))


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    password = fl.lab_secret("LAB_ARRAY_PW")
    for tag, host in ARRAYS:
        capture(tag, host, password)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        if os.path.isdir(OUT):
            fl.OUT = OUT
            fl.save("script_stopped.txt", traceback.format_exc())
        raise
    finally:
        if os.path.isdir(OUT):
            fl.OUT = OUT
            fails = sum(1 for r in RESULTS if r.startswith("FAIL"))
            fl.save("report.txt", "\n".join(RESULTS + ["", "%d FAIL" % fails]))
            fl.banner("Done, %d FAIL. Send me %s" % (fails, shutil.make_archive(OUT, "zip", OUT)))
