"""Initialisation live check: the screens and the stored credentials of an initialisation run, on a
running app. Run it after every change to prove initialising an array still works. No prompts.

    INIT_SHEET=<workbook> python lab/init_walk_lab.py        (the app already running on this machine)

READ-ONLY on GreenLake, the array, vCenter and the switches: it never registers, connects, fills a
wizard, verifies or generates. It only moves between pages. What it does change is local to the app:
the upload writes the workbook's GreenLake client id and secret to the app's .env (every upload does),
and each preset leaves one run in the app's database (two more with the restart check).

Environment:
  INIT_SHEET        the filled initialisation workbook (default
                    ~/Downloads/Initialisation_sheet_rack13arcus_COMPLETE.xlsx). Read only through the
                    app's own parser; nothing from it is printed.
  LAB_APP           the running app (default http://127.0.0.1:8765)
  INIT_OUT          evidence folder (default ~/Downloads/init_walk); zipped next to it as <folder>.zip
  INIT_PRESET       init = the initialisation run alone (the "Full onboarding" card; "Initialization" in
                    the init-only build); full = the whole chain (the "Onboard, then provision" card:
                    the same initialisation steps, then provisioning, whose pages are not opened here).
                    Unset = both in the full build, init alone in the init-only build.
  INIT_DB           the app's state database (default STATE_DATABASE_PATH, else .alletra_onboard/state.db
                    in the app folder); INIT_ENV its .env (default the app folder's). The app is local,
                    so the stored secrets are compared with the workbook's here, in code.
  INIT_RESTART_CMD  optional. A command that starts the app again and writes its process id to
                    INIT_PID_FILE. When set, the script stops the process named in INIT_PID_FILE, runs the
                    command, and checks the runs and their credentials still load.

1. the app answers, serves this checkout's step registry and this checkout's bundle
2. per preset, in a headless browser: Prerequisites (no clock warning, waiting as long as the clock
   check can take), the workbook upload, the Mode page and its cards, Create run, then every
   initialisation page in the rail, Run overview and Finish. Each page: one h1 with its own title, no
   script error, no console error, no failed request to the app, no "undefined" / "NaN". A font or a
   recording on an HPE site that does not load, and the favicon the app does not ship, are said in a
   note and not counted.
3. nothing was started: the buttons pressed are recorded in the browser and none is on the deny-list
   (DENY_NAMES, DENY_WORDS); the only writes sent to the app are the upload and the run creation; the
   run has no device command
4. the run's stored work item equals the workbook's, subscription key included, and the GreenLake
   client id and secret are in the app's .env. Printed as True / False only.
5. with INIT_RESTART_CMD: a workbook is uploaded and held, the app is restarted, the runs and their
   credentials still load, and the held workbook still makes a run.
Writes PASS/FAIL lines to report.txt, a screenshot per page, and ends with "N pass, M fail". The exit
code is 1 when anything failed.
"""
import base64
import glob
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_failover_lab as fl

SHEET = os.path.expanduser(os.environ.get("INIT_SHEET") or "~/Downloads/Initialisation_sheet_rack13arcus_COMPLETE.xlsx")
OUT = os.path.expanduser(os.environ.get("INIT_OUT") or os.path.join("~", "Downloads", "init_walk"))
fl.OUT = OUT
DB = os.path.expanduser(os.environ.get("INIT_DB") or os.environ.get("STATE_DATABASE_PATH")
                        or os.path.join(fl.ROOT, ".alletra_onboard", "state.db"))
ENV = os.path.expanduser(os.environ.get("INIT_ENV") or os.path.join(fl.ROOT, ".env"))
RESTART_CMD, PID_FILE = os.environ.get("INIT_RESTART_CMD"), os.environ.get("INIT_PID_FILE")

# A preset is a mode of the step registry; the page names its card (frontend/src/modes.ts).
PRESET_MODES = {"init": "FULL_ONBOARDING", "full": "BOTH"}
MODE_CARDS = {"FULL_ONBOARDING": "Full onboarding", "BOTH": "Onboard, then provision"}
INIT_ONLY_CARD = "Initialization"
RAIL_FRAME = ("Prerequisites", "Initialisation sheet", "Mode")
# Buttons this walk must never press: each starts work on GreenLake, the array, DSCC or this machine.
DENY_NAMES = (
    "Register the array", "Check without writing", "Fill in and connect", "Launch the HPE Discovery Tool",
    "Run DSCC automation", "Launch the DSCC browser", "Mark DSCC complete", "Sync system clock",
    "Verify configuration", "Verify again", "Generate document", "Generate again", "Mark run complete",
    "Start a new run", "Cancel run", "Validate GreenLake credentials", "Test connectivity", "Save and retest",
    "Use a different credential", "Open terminal", "Run",
)
# ... and any button whose name begins with one of these words ("Create run" is the one this walk presses).
DENY_WORDS = re.compile(r"(regist|start|apply|sync|launch|generate|mark|trust|save|create(?! run\b))", re.IGNORECASE)
WRITES_EXPECTED = ["POST /init-sheet/upload", "POST /runs/from-sheet"]
CLOCK_WAIT_S = 45            # the clock check tries three time sources, 10 s each
BAD = re.compile(r"\bundefined\b|\bNaN\b|\[object Object\]")
RECORD_PRESSES = """
document.addEventListener('click', (e) => {
  const el = e.target instanceof Element ? e.target.closest('button, a, [role=button], [role=radio], input, label') : null;
  if (el) window.initWalkPressed((el.getAttribute('aria-label') || el.innerText || el.value || '').trim().split('\\n')[0]);
}, true);
"""
RESULTS, NOTES = [], []


def check(what, ok, detail=""):
    line = f"{'PASS' if ok else 'FAIL'}  {what}{' - ' + detail if detail else ''}"
    print(line, flush=True)
    RESULTS.append(line)
    return ok


def note(text):
    """Said, kept in the report, never counted."""
    print("note  " + text, flush=True)
    NOTES.append("note  " + text)


def same(what, ok):
    """A comparison that involves a secret: the answer only."""
    return check(what, bool(ok), str(bool(ok)))


def denied(name):
    flat = " ".join(name.split())
    return flat.lower() in {d.lower() for d in DENY_NAMES} or bool(DENY_WORDS.match(flat))


def api(method, path, body=None):
    req = urllib.request.Request(fl.APP + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with fl.OPENER.open(req, timeout=120) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as exc:
        return exc.code, (exc.read() or b"").decode("utf-8", "replace")


def app_up():
    try:
        fl.get("/app/profile")
        return True
    except Exception:  # noqa: BLE001
        return False


def wait_until(done, seconds):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if done():
            return True
        time.sleep(1)
    return False


def served_registry(profile):
    """The profile must carry the step registry of this checkout (AGENTS rule 5): the UI renders from it."""
    from alletra_onboard.domain.workflow import STEP_REGISTRY, mode_steps

    steps = [(s["key"], s["label"], s["kind"], s["phase"]) for s in profile["steps"]]
    code = [(s.key, s.label, s.kind, s.phase.value) for s in STEP_REGISTRY]
    modes = {mode.value: list(keys) for mode, keys in mode_steps().items()}
    check("/app/profile serves this checkout's step registry and modes", steps == code and profile["modes"] == modes,
          f"{len(steps)} steps, {len(profile['modes'])} modes")


def served_bundle():
    """The bundle the app serves must be the one in this checkout (LESSONS 13)."""
    with open(os.path.join(fl.ROOT, "frontend", "dist", "index.html"), encoding="utf-8") as f:
        local = re.search(r"assets/index-[^\"']+\.js", f.read())
    served = re.search(r"assets/index-[^\"']+\.js", fl.get("/").decode("utf-8", "replace"))
    check("the app serves this checkout's bundle", bool(local and served and local.group(0) == served.group(0)),
          f"{served.group(0) if served else None} / {local.group(0) if local else None}")


def read_sheet(init_only):
    """The workbook as the app's upload reads it in this build. Its values stay in this process."""
    from alletra_onboard.application.platform.init_sheet import parse_upload, parse_workbook_bytes
    from alletra_onboard.domain.workflow import RunMode

    with open(SHEET, "rb") as f:
        raw = f.read()
    if init_only:
        return raw, parse_workbook_bytes(raw, mode=RunMode.FULL_ONBOARDING), []
    parsed, problems = parse_upload(raw)
    return raw, parsed, problems


def presets_for(profile):
    asked = (os.environ.get("INIT_PRESET") or "both").strip().lower()
    if asked not in ("init", "full", "both"):
        check("INIT_PRESET is init, full or unset", False, asked)
        return []
    if profile["init_only"]:
        if asked == "full":
            check("INIT_PRESET=full fits this build", False, "this build initialises only: it has the init preset alone")
            return []
        return ["init"]
    return ["init", "full"] if asked == "both" else [asked]


def mode_keys(profile, mode):
    chosen = set(profile["modes"][mode])
    return [s["key"] for s in profile["steps"] if s["key"] in chosen]


def browser(pw):
    for channel in (None, "msedge", "chrome"):  # bundled Chromium, else Edge (Windows), else Chrome
        try:
            return pw.chromium.launch(channel=channel) if channel else pw.chromium.launch()
        except Exception:  # noqa: BLE001
            continue
    raise RuntimeError("no browser: install Playwright's Chromium, Edge or Chrome")


def walk(b, preset, profile, parsed):
    """One preset in a fresh browser profile. Returns the id of the run it created, or None."""
    mode = PRESET_MODES[preset]
    tag = f"[{preset}] "
    card = INIT_ONLY_CARD if profile["init_only"] else MODE_CARDS[mode]
    labels = {s["key"]: s["label"] for s in profile["steps"]}
    run_keys = mode_keys(profile, mode)
    init_track = [k for k in run_keys if k in set(profile["modes"]["FULL_ONBOARDING"])]
    serial = parsed.work_item.serial_number
    errors, console, failed, writes, pressed, outside = [], [], [], [], [], []
    seen = [0, 0, 0]
    shots = [0]

    context = b.new_context(viewport={"width": 1366, "height": 768})
    context.expose_function("initWalkPressed", lambda name: pressed.append(name))
    context.add_init_script(RECORD_PRESSES)
    page = context.new_page()
    page.on("pageerror", lambda e: errors.append(str(e).splitlines()[0][:200]))

    def to_app(url):
        return url.startswith(fl.APP + "/")

    def on_console(m):
        if m.type != "error":
            return
        url = (m.location or {}).get("url", "")
        missing = m.text.startswith("Failed to load resource")
        if missing and url and not to_app(url):
            # a font or a recording on an HPE site that this machine cannot load is not the app's error
            outside.append((urlsplit(url).netloc, m.text[:120]))
        elif missing and urlsplit(url).path == "/favicon.ico":
            outside.append(("the app's /favicon.ico, which it does not ship", m.text[:120]))
        else:
            console.append(f"{(m.text.splitlines() or [''])[0][:200]} [{urlsplit(url).path}]")

    page.on("console", on_console)

    def on_request(r):
        if to_app(r.url) and r.method not in ("GET", "HEAD", "OPTIONS"):
            writes.append(f"{r.method} {urlsplit(r.url).path}")

    def on_failed(r):
        # a reload drops the run's event stream and whatever was still loading: not a failure
        if to_app(r.url) and "ERR_ABORTED" not in (r.failure or ""):
            failed.append(f"{r.method} {urlsplit(r.url).path} ({r.failure})")

    def on_response(r):
        if to_app(r.url) and r.status >= 400:
            failed.append(f"{r.request.method} {urlsplit(r.url).path} -> HTTP {r.status}")

    page.on("request", on_request)
    page.on("requestfailed", on_failed)
    page.on("response", on_response)

    def fresh():
        """What went wrong since the last page, as one phrase ('' when nothing did)."""
        parts = []
        for i, (name, items) in enumerate((("script error", errors), ("console error", console), ("failed request", failed))):
            new, seen[i] = items[seen[i]:], len(items)
            if new:
                parts.append(f"{len(new)} {name}{'' if len(new) == 1 else 's'}: {new[0]}")
        return "; ".join(parts)

    def look(name, title):
        try:
            page.locator("h1").first.wait_for(timeout=10000)
        except Exception:  # noqa: BLE001
            pass
        page.wait_for_timeout(1500)
        shots[0] += 1
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        page.screenshot(path=os.path.join(OUT, f"{preset}-{shots[0]:02d}-{slug}.png"), full_page=True)
        h1 = [t.strip() for t in page.locator("h1").all_inner_texts()]
        titles = [title] if isinstance(title, str) else list(title)
        bad = sorted(set(BAD.findall(page.locator("body").inner_text())))
        wrong = fresh()
        ok = len(h1) == 1 and h1[0].lower() in [t.lower() for t in titles] and not bad and not wrong
        detail = f"h1={h1}{' bad=' + ','.join(bad) if bad else ''}{'; ' + wrong if wrong else ''}"
        return check(tag + f"page {name}", ok, detail)

    def press(words):
        """A button by the words its name starts with. Refuses anything on the deny-list before the click."""
        button = page.get_by_role("button", name=re.compile("^" + re.escape(words))).first
        name = button.inner_text(timeout=10000).strip().split("\n")[0]
        if denied(name):
            raise RuntimeError(f"refused to press '{name}': it is on the deny-list")
        button.click(timeout=10000)
        return name

    run_id = None
    try:
        page.goto(fl.APP + "/")
        page.locator("h1").first.wait_for(timeout=30000)
        # Prerequisites: the clock row answers on its own, after up to three time sources.
        row = page.get_by_text(re.compile(r"In sync \(|Could not reach a time source|Off by about")).first
        try:
            row.wait_for(timeout=CLOCK_WAIT_S * 1000)
            clock = row.inner_text().strip().split("\n")[0]
        except Exception:  # noqa: BLE001
            clock = ""
        check(tag + "the page title is the build's", page.title() == profile["title"], page.title())
        look("Prerequisites", "Prerequisites")
        clock_off = bool(re.search(r"Off by about|seconds off|Clock needs a sync", page.locator("body").inner_text()))
        check(tag + "Prerequisites shows no clock warning", bool(clock) and not clock_off,
              clock or f"the clock row gave no answer in {CLOCK_WAIT_S} s")

        if clock_off:
            press("Continue without syncing")
        else:
            press("Continue to")
        look("Initialisation sheet", "Initialisation sheet")
        page.set_input_files("input[type=file]", SHEET)
        page.get_by_text("What the workbook holds").first.wait_for(timeout=60000)
        read = page.get_by_text("Workbook read for").first.inner_text(timeout=10000)
        same(tag + "the workbook uploads and the page names its array", serial in read)
        look("Initialisation sheet, uploaded", "Initialisation sheet")

        press("Continue to")
        look("Mode", "What do you want to do?")
        radios = page.get_by_role("radiogroup").get_by_role("radio")
        cards = [t.strip().split("\n")[0] for t in radios.all_inner_texts()]
        expected = 1 if profile["init_only"] else len(profile["modes"]) + 1   # every served mode, and Custom
        check(tag + "the Mode page shows this build's presets", len(cards) == expected and card in cards,
              f"{len(cards)} cards: {', '.join(cards)}")
        choice = page.get_by_role("radio", name=re.compile("^" + re.escape(card))).first
        if choice.get_attribute("aria-disabled") == "true":
            check(tag + f"the '{card}' card can be chosen", False, choice.inner_text().replace("\n", " ")[:200])
            return None
        choice.click(timeout=10000)
        page.wait_for_timeout(500)
        with page.expect_response(lambda r: urlsplit(r.url).path == "/runs/from-sheet", timeout=30000) as answer:
            create = press("Create run")
        made = answer.value
        run_id = made.json()["run"]["run_id"] if made.status == 200 else None
        if not check(tag + f"the run is created from the '{card}' card", bool(run_id),
                     run_id or f"HTTP {made.status}: {' '.join(made.text().split())[:300]}"):
            look("Mode, run not created", "What do you want to do?")
            return None
        check(tag + "Create run counts the preset's steps", f"{len(run_keys)} step" in create, create)
        try:
            page.wait_for_function("localStorage.getItem('alletra.runId')", timeout=15000)
        except Exception:  # noqa: BLE001 - judged on the next line
            pass
        check(tag + "the browser keeps the run, so a reload opens it again",
              page.evaluate("localStorage.getItem('alletra.runId')") == run_id)
        look(f"{labels[run_keys[0]]}, right after Create run", labels[run_keys[0]])

        # go on with the run the server made, whatever the page kept: the pages after are judged on their own
        page.evaluate("id => localStorage.setItem('alletra.runId', id)", run_id)
        page.reload()  # a restored run makes every step of the rail navigable
        rail = page.get_by_role("navigation", name="Steps of this run")
        rail.get_by_label("Run overview").first.wait_for(timeout=30000)
        page.wait_for_timeout(1500)
        names = rail.locator("[aria-label]").evaluate_all("els => els.map(e => e.getAttribute('aria-label'))")
        shown = [n.split(":")[0] for n in names if ":" in n]
        check(tag + "the rail lists the steps /app/profile gives this preset",
              shown == [*RAIL_FRAME, *(labels[k] for k in run_keys), "Finish"], ", ".join(shown))
        fresh()  # the reload itself is judged by the pages that follow

        try:
            rail.get_by_label("Run overview").first.click(timeout=10000)
            look("Run overview", serial)
        except Exception as exc:  # noqa: BLE001
            check(tag + "page Run overview", False, "could not open it: " + str(exc).splitlines()[0][:160])
        for key in init_track:
            try:
                rail.get_by_label(re.compile(f"^{re.escape(labels[key])}:")).first.click(timeout=10000)
            except Exception as exc:  # noqa: BLE001
                check(tag + f"page {labels[key]}", False, "could not open it: " + str(exc).splitlines()[0][:160])
                continue
            look(labels[key], labels[key])
        try:
            rail.get_by_label(re.compile(r"^Finish\b")).first.click(timeout=10000)
            look("Finish", ("Finish", "Done"))
        except Exception as exc:  # noqa: BLE001
            check(tag + "page Finish", False, "could not open it: " + str(exc).splitlines()[0][:160])
        page.wait_for_timeout(2000)
        late = fresh()
        check(tag + "nothing went wrong after the last page", not late, late)
    except Exception as exc:  # noqa: BLE001
        check(tag + "the walk ran to its end", False, str(exc).splitlines()[0][:200])
        fl.save(f"error-{preset}.txt", traceback.format_exc())
        try:
            page.screenshot(path=os.path.join(OUT, f"{preset}-stopped.png"), full_page=True)
        except Exception:  # noqa: BLE001
            pass
    finally:
        context.close()
        refused = [n for n in pressed if denied(n)]
        check(tag + "no button on the deny-list was pressed", not refused,
              "pressed: " + (" | ".join(refused) if refused else " | ".join(pressed)))
        check(tag + "the only writes sent to the app are the upload and the run creation",
              writes == WRITES_EXPECTED[:len(writes)] and (run_id is None or writes == WRITES_EXPECTED), ", ".join(writes))
        fl.save(f"walk-{preset}.json", json.dumps({
            "run_id": run_id, "mode": mode, "card": card, "pressed": pressed, "writes": writes,
            "script_errors": errors, "console_errors": console, "failed_requests": failed,
            "not_counted": [list(o) for o in outside]}, indent=2))
        if outside:
            note(f"{tag}{len(outside)} resources did not load and are not counted: "
                 + ", ".join(sorted({where for where, _text in outside})))
    return run_id


def differing(a, b, path=""):
    """The names of the fields where two JSON values differ. Names only: a value may be a secret."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for key in sorted(set(a) | set(b)):
            out += differing(a.get(key), b.get(key), (path + "." if path else "") + key)
        return out
    return [] if a == b else [path or "(all)"]


def run_loads(tag, run_id, mode, parsed):
    """Over the API: the run, its work item (secrets masked by the app) and the GreenLake settings."""
    status, detail = api("GET", f"/runs/{run_id}")
    if not check(tag + "the run loads over the API", status == 200 and isinstance(detail, dict), f"HTTP {status}"):
        return
    run = detail["run"]
    check(tag + "the run has the preset's mode and no step running", run.get("mode") == mode and run.get("status") != "running",
          f"{run.get('mode')}, {run.get('status')}")
    item = detail.get("work_item")
    fields = differing(item, json.loads(parsed.work_item.model_dump_json())) if item else ["work item missing"]
    check(tag + "its work item equals the workbook's, secrets masked", not fields, "differs in: " + ", ".join(fields) if fields else "")
    status, config = api("GET", "/config")
    values = config.get("values", {}) if isinstance(config, dict) else {}
    same(tag + "the app holds the workbook's GreenLake client id and a client secret",
         status == 200 and isinstance(config, dict) and config.get("configured") and bool(parsed.gl_client_id)
         and values.get("GL_CLIENT_ID") == parsed.gl_client_id)


def nothing_started(tag, run_id):
    status, log = api("GET", f"/runs/{run_id}/console/log")
    commands = log.get("commands", []) if isinstance(log, dict) else None
    status_e, ev = api("GET", f"/runs/{run_id}/events")
    kinds = [e["event_type"] for e in ev.get("events", [])] if isinstance(ev, dict) else None
    fl.save(f"events-{run_id[:8]}.json", json.dumps(kinds, indent=2))
    check(tag + "the run sent no command to a device and holds only its creation",
          commands == [] and kinds is not None and set(kinds) <= {"run.created"},
          f"HTTP {status}/{status_e}, {None if commands is None else len(commands)} commands, events: {kinds}")


def stored(tag, run_id, parsed):
    """The app's own store and .env against the workbook, secrets included. Answers only."""
    from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
    from alletra_onboard.application.platform.configuring import read_env

    if not check(tag + "the app's database is at INIT_DB", os.path.isfile(DB), DB):
        return
    store = SqliteRunStore(Path(DB))
    try:
        item = store.get_work_item(run_id)
        intent = store.get_provisioning_intent(run_id)
    except Exception as exc:  # noqa: BLE001 - the message may quote a stored value
        check(tag + "the stored credentials open", False, type(exc).__name__)
        return
    if not same(tag + "the run's work item is stored", item is not None):
        return
    same(tag + "stored work item equals the workbook's, every field", item == parsed.work_item)
    same(tag + "stored subscription key equals the workbook's", bool(parsed.work_item.subscription_key.get_secret_value())
         and item.subscription_key.get_secret_value() == parsed.work_item.subscription_key.get_secret_value())
    if parsed.work_item.dscc_setup.password is not None:
        same(tag + "stored DSCC array password equals the workbook's", item.dscc_setup.password is not None
             and item.dscc_setup.password.get_secret_value() == parsed.work_item.dscc_setup.password.get_secret_value())
    if intent is not None and parsed.provisioning_intent is not None:
        want = parsed.provisioning_intent
        same(tag + "stored array, vCenter and switch passwords equal the workbook's", all(
            getattr(intent, name).password.get_secret_value() == getattr(want, name).password.get_secret_value()
            for name in ("array", "vcenter", "switch_f1", "switch_f2")))
    values = read_env(Path(ENV))
    same(tag + "GreenLake client id in the app's .env equals the workbook's",
         bool(parsed.gl_client_id) and values.get("GL_CLIENT_ID") == parsed.gl_client_id)
    same(tag + "GreenLake client secret in the app's .env equals the workbook's",
         bool(parsed.gl_client_secret) and values.get("GL_CLIENT_SECRET") == parsed.gl_client_secret)


def reopens(b, tag, run_id, profile, mode):
    """After the restart the run opens in a new browser on the page of its first step."""
    labels = {s["key"]: s["label"] for s in profile["steps"]}
    first = labels[mode_keys(profile, mode)[0]]
    what = tag + f"the run opens in the browser on {first}"
    context = b.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e).splitlines()[0][:200]))
    try:
        page.goto(fl.APP + "/")
        page.evaluate("id => localStorage.setItem('alletra.runId', id)", run_id)
        page.reload()
        rail = page.get_by_role("navigation", name="Steps of this run")
        rail.get_by_label("Run overview").first.wait_for(timeout=30000)
        page.wait_for_timeout(1500)
        page.screenshot(path=os.path.join(OUT, f"restart-{run_id[:8]}.png"), full_page=True)
        h1 = [t.strip() for t in page.locator("h1").all_inner_texts()]
        check(what, [t.lower() for t in h1] == [first.lower()] and not errors, f"h1={h1}{' ' + errors[0] if errors else ''}")
    except Exception as exc:  # noqa: BLE001
        check(what, False, str(exc).splitlines()[0][:200])
    finally:
        context.close()


def restart(b, raw, parsed, profile, runs):
    """Optional (INIT_RESTART_CMD): what is stored must survive the app stopping and starting."""
    tag = "[restart] "
    if not check(tag + "INIT_PID_FILE names the running app's pid file", bool(PID_FILE) and os.path.isfile(os.path.expanduser(PID_FILE)),
                 str(PID_FILE)):
        return
    status, up = api("POST", "/init-sheet/upload", {"content_b64": base64.b64encode(raw).decode("ascii")})
    token = up.get("token") if isinstance(up, dict) else None
    same(tag + "a workbook is uploaded and held before the restart", status == 200 and bool(token))
    with open(os.path.expanduser(PID_FILE), encoding="utf-8") as f:
        pid = int(f.read().strip())
    os.kill(pid, signal.SIGTERM)
    if not check(tag + f"the app stops (process {pid} from the pid file)", wait_until(lambda: not app_up(), 30)):
        return
    detach = {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)} if os.name == "nt" else {"start_new_session": True}
    with open(os.path.join(OUT, "app-restart.log"), "ab") as log:
        subprocess.Popen(RESTART_CMD, shell=True, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **detach)
    if not check(tag + "the app answers again after INIT_RESTART_CMD", wait_until(app_up, 120)):
        return
    again = json.loads(fl.get("/app/profile"))
    check(tag + "it is the same build", (again["profile"], again["steps"], again["modes"]) == (profile["profile"], profile["steps"], profile["modes"]),
          again["profile"])
    for preset, run_id in runs:
        run_loads(tag + f"{preset} run: ", run_id, PRESET_MODES[preset], parsed)
        stored(tag + f"{preset} run: ", run_id, parsed)
        reopens(b, tag + f"{preset} run: ", run_id, profile, PRESET_MODES[preset])
    if token:
        status, made = api("POST", "/runs/from-sheet", {"token": token, "mode": "FULL_ONBOARDING", "selected_steps": []})
        held = made["run"]["run_id"] if status == 200 and isinstance(made, dict) else None
        check(tag + "the workbook held before the restart makes a run after it", bool(held), held or f"HTTP {status}")
        if held:
            stored(tag + "held run: ", held, parsed)


def main():
    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, "*")):  # only what an earlier run of this script wrote
        if re.fullmatch(r"(init|full|restart)-.*\.png|(walk|events)-.*\.json|error-.*\.txt|report\.txt|script_stopped\.txt|app-restart\.log",
                        os.path.basename(old)):
            os.remove(old)
    if os.path.exists(OUT + ".zip"):
        os.remove(OUT + ".zip")

    fl.banner(f"1. The app on {fl.APP}")
    try:
        profile = json.loads(fl.get("/app/profile"))
    except Exception as exc:  # noqa: BLE001
        check("the app answers and serves /app/profile", False, f"{str(exc).splitlines()[0][:160]}: start the app, or set LAB_APP")
        return
    check("the app answers and serves /app/profile", True,
          f"profile {profile['profile']}, init_only {profile['init_only']}, {profile['title']}")
    served_registry(profile)
    served_bundle()
    try:
        raw, parsed, problems = read_sheet(profile["init_only"])
    except Exception as exc:  # noqa: BLE001
        check("the workbook reads with the app's own parser", False, f"{type(exc).__name__}: {str(exc).splitlines()[0][:200]}")
        return
    check("the workbook reads with the app's own parser", True,
          f"{len(problems)} problem{'' if len(problems) == 1 else 's'} in tabs an initialisation run does not use")
    same("the workbook holds a subscription key and a GreenLake client id and secret",
         parsed.work_item.subscription_key.get_secret_value() and parsed.gl_client_id and parsed.gl_client_secret)

    from playwright.sync_api import sync_playwright

    runs = []
    with sync_playwright() as pw:
        b = browser(pw)
        for preset in presets_for(profile):
            fl.banner(f"2. The {preset} preset, in a headless browser")
            run_id = walk(b, preset, profile, parsed)
            if not run_id:
                continue
            runs.append((preset, run_id))
            fl.banner(f"3-4. The {preset} run {run_id}: nothing started, and what is stored")
            nothing_started(f"[{preset}] ", run_id)
            run_loads(f"[{preset}] ", run_id, PRESET_MODES[preset], parsed)
            stored(f"[{preset}] ", run_id, parsed)
        if RESTART_CMD:
            fl.banner("5. Restart: what is stored survives the app stopping and starting")
            restart(b, raw, parsed, profile, runs)
        else:
            note("the restart check was not run: INIT_RESTART_CMD is not set")
        b.close()


if __name__ == "__main__":
    started = time.time()
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        check("the script ran to its end", False, f"{type(exc).__name__}: {(str(exc).splitlines() or [''])[0][:200]}")
        if os.path.isdir(OUT):
            fl.save("script_stopped.txt", traceback.format_exc())
    fails = sum(1 for r in RESULTS if r.startswith("FAIL"))
    count = f"{len(RESULTS) - fails} pass, {fails} fail"
    if os.path.isdir(OUT):
        fl.save("report.txt", "\n".join(RESULTS + NOTES + ["", count]))
        fl.banner(f"Took {time.time() - started:.0f} s. Evidence: {shutil.make_archive(OUT, 'zip', OUT)}")
    print(count)
    sys.exit(1 if fails else 0)
