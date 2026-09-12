# Lessons register

What the v0.13.0 cycle (bounded-context refactor + HPE Design System redesign + live-array
validation) taught us, written as rules so the same mistake is not made twice. Each entry states
the rule, then the incident that earned it. Append new lessons; do not rewrite history.

Related: [ARCHITECTURE.md](ARCHITECTURE.md) · [UX-GUIDELINES.md](UX-GUIDELINES.md) ·
[adr/](adr/) · [ux/CHECKLIST.md](ux/CHECKLIST.md)

---

## Driving devices and their browsers

**1. Wait FOR positive proof of readiness — never for the absence of a bad sign.**
The rc.2 wizard fix waited for the "Initializing your system" spinner text to be *absent*. At goto
time a single-page app has rendered *nothing*, and a blank page has no spinner text either — the
wait concluded ready instantly and the run died on the same timeout it was meant to fix, confirmed
on live retest. Blank ≈ absent. Readiness means a known screen's own text is visible
(`CLOUDINIT_TEXT["ready"]`).

**2. Budget for device boot states, and show liveness while waiting.**
The array sits in "Initializing your system" for minutes on first boot — a state no release had
ever handled, so every one of them failed ~42 seconds in while the array was working normally.
Poll patiently (minutes, not seconds) and emit a progress line about once a minute so the operator
sees a deliberate wait, not a hang.

**3. A timeout must say what it was waiting for; an unknown screen must quote itself.**
"Browser automation did not complete" left the operator with only a screenshot. The handler was
*discarding* rich diagnostics: our own guard messages and Playwright's "waiting for <locator>"
line. Once relayed, the very next live failure named its locator and the fix took minutes. The
ready-wait timeout goes further and quotes the page text, so a screen we have never seen
identifies itself in the Progress log.

**4. Diagnose remote failures by matching event timestamps against the code's wait constants.**
Start 10:00:39 → fail 10:01:21 = 42 s ≈ 5 s (welcome wait) + 30 s (EULA wait) + overhead. That
arithmetic identified the exact code path with zero hardware access — twice. Operators' timelines
are traces; read them as such.

**5. Normalise the natural form of operator input at intake; never let a downstream validator
reject what a person would reasonably type.**
The wizard rejects `http://proxy…` ("Value must be valid IPv4 or domain name"), but a URL is
exactly how proxies appear in browser settings and `HTTP_PROXY`. `NetworkConfig` now strips the
scheme and relocates an embedded port. Because normalisation runs on model validation, records
already stored heal themselves on load — prefer that placement over fixing it at the point of use.

## State and safety

**6. A result may be durable; an approval must not outlive its inputs or its process.**
Making the previewed provisioning plan durable (C7) silently removed the gate on the ONLY step
that writes to a customer array: a plan approved before a restart, a composition edit, or a
re-discovery still authorised an apply — and `apply_plan` recomputes from current inputs, so what
got created could differ from what was approved. The plan is now held with the exact discovery it
was built from and withdrawn when any of the three change. Ask of every cached value: is this a
*result* or an *authorisation*?

**7. The one action that writes to customer equipment takes an explicit authorisation.**
The redesign quietly reduced "create storage objects" to a single click while double-confirming
the far less consequential "discard run". Confirmation weight must scale with consequence, not
with how easy the dialog is to build.

**8. A durable snapshot needs a visible age.**
Discovery persisting across restarts is what lets an engagement resume — and also what lets a run
reopened days later provision hosts from week-old WWPNs. The steps that act on the snapshot now
state when the environment was last read and warn past twelve hours. If you persist it, date it
where it is used.

**9. Anything you persist needs bounded retention.** The as-built document (hundreds of KB per
run) accumulated forever; artifacts now keep only the most recent runs. Decide the bound when you
add the table, not when the disk fills.

**10. An invariant must cover every statement inside it.** "This step never changes run status"
was broken by a store write sitting *outside* the try/except that enforced it — a failure there
would have flipped a finished run to failed via the crash guard. When you add a line to a guarded
block, check it is actually inside the guard.

## Verification

**11. Passing tests + clean typecheck + your own probing is not a review.**
Two independent reviewers over the final diff found one critical backend regression and five
operator-trapping UI dead-ends that 184 green tests, tsc, and my own live DOM assertions had all
missed. For code with no automated tests (this frontend, by decision), independent review of the
diff *is* the safety net — schedule it before every merge, not as a favour.

**12. Drive the running application; reading code lies by omission.**
The forbidden word "health" surviving in the UI, the SSE-derived rail states, and the operator
dead-ends were all found (or proven) by starting the app and asserting on the live DOM — not by
reading the sources that "obviously" handled them.

**13. Before trusting any UI observation, verify WHICH bundle the browser loaded.**
Twice in one cycle: my own smoke test asserted against a stale cached bundle, and the operator
reported bugs against the old UI while running the new executable. Compare the loaded script hash
against what the server serves before believing anything the page shows.

**14. Same-origin upgrades require an explicit cache policy.**
Every release serves from `127.0.0.1:8765`; with no `Cache-Control`, browsers kept the previous
`index.html` *and* its old hashed bundle indefinitely. Serve the entry document `no-cache` and the
content-hashed assets `immutable`. Any locally-served SPA that upgrades in place needs this.

**15. Validate on hardware via release candidates; keep the stable number clean.**
Four RCs each surfaced a real defect no test or review had caught — one predating the refactor by
months. Tag candidates as semver pre-releases (the workflow marks `-rc.N` `--prerelease`) so a
review build never presents itself as the current stable download, and the final number lands on
the commit that actually survived hardware.

**16. After renaming packages, verify everything that references modules by STRING.**
`collect_submodules` in the PyInstaller spec, `__file__`-relative resource paths (`parents[2]`),
frozen-build lookups, and the `.github` guidance tree all bind by name at build/read time, not
import time. Build and smoke-test the packaged executable locally before tagging — a rename that
imports cleanly can still ship a broken exe.
Addendum (v0.14.0-rc.1): **a guarded optional import is a packaging blind spot** — every exe ever
shipped lacked a working WSAPI SDK because `try: import hpe3parclient` swallowed a frozen-only
failure (`eventlet` dynamically imports dnspython; PyInstaller's analysis can't see it), and no
packaged feature touched WSAPI until the preflight found it on hardware. Two rules follow: give
every guarded optional import a **capability flag the API serves** (`/app/profile
capabilities.wsapi_sdk` + the captured import error) so one localhost request proves any build,
and check that flag on the locally built exe as part of cutting every release.

## Refactoring discipline

**17. One mechanical move per commit, with the test suite as referee.**
The 733-line god-object, the domain split, and two package renames landed as eleven commits, each
green. The one deliberate behaviour change (a served label) was called out as such in its commit.
Mixing a move with a change is how refactors break things invisibly.

**18. Prove "dead" before deleting, and protect deliberate differences from deduplication.**
Every deleted module was grep-verified unreferenced first. And the near-duplicate credential gates
were *deliberately* different (`GL_MEMBER_WORKSPACE_ID` vs `GL_TOKEN_URL`) — merging them for
tidiness would have changed behaviour. Two similar functions are only duplicates if their
differences are accidents; check before unifying, and comment the survivor.

**19. A single source of truth pays for itself immediately.**
When the design system's "never say health" rule surfaced, the step label had exactly one
definition — served from `domain/workflow.py` — because Phase 2 had killed the hand-synced
frontend mirror. One line fixed every surface. Every hand-maintained mirror is a future
inconsistency with a deadline.

## Working with the design system, and the repo

**20. The shipped tokens are ground truth; the marketing site needs a real browser.**
design-system.hpe.design is a client-rendered SPA — plain fetchers, raw HTML and the GitHub source
all return an empty shell; only driving its client router in a browser read it. Meanwhile the
authoritative *values* were already installed in `node_modules/hpe-design-tokens`. Read guidance
from the site, values from the package — and expect real corrections (retired GreenLake badge,
"never say health", primary buttons are `#008567` not brand green).

**21. Sanitise lab data before anything reaches the public repository.**
The mockups originally carried real lab management, switch and gateway IPs. The blanket `*.html`
gitignore exists precisely because captured UI leaks; the committed copies use documentation-range
`192.0.2.x` addresses, with a narrow gitignore exception rather than a force-add. Treat every
screenshot, capture and mockup as containing secrets until checked.

**22. Design on mockups, implement against sign-off.**
Fifteen screens were iterated as throwaway HTML — including a full professional-register copy
revision — before any component was written, and implementation then copied the approved wording
verbatim. Changing a sentence in a mockup costs nothing; changing it across thirteen components
does not. Where shipped behaviour forces a divergence from the mockup (Cloud Connectivity submits
for a reason), record the divergence explicitly.

## Diagnosing a system you can only see through someone else's terminal

**23. Reproduce the reported symptom yourself — its error message is usually the diagnosis.**
A lab array was reported as "SSD drives have old firmware, can't create a base VV", and days went
into drive firmware, enclosure FRU data and a 3.4 GB OS upgrade. One command settled it:
`createvv -tpvv SSD_r6 zz_test 1g` → *"Array has not yet completed the subscription process."* Not
firmware, not the cage — a GreenLake subscription gate. Nobody had run the command the complaint was
about. Before accepting anyone's diagnosis, execute the failing operation and read what the system
says about itself.

**24. Alerts persist; state does not. Check the timestamps before believing either.**
`checkhealth` reported all twelve drives `Failed (Replace Drive, Unsupported Cage)`; `showpd -s`
reported all twelve `normal`. `showalert -d` resolved it: every alert was timestamped four days
earlier, from a fault that had been repaired and never cleared. A team had been working from that
text ever since. An alert records an event; a state command records now. When they disagree the
timestamps decide — and clearing alerts is part of finishing a repair.

**25. When a transfer reports success but the artifact is wrong, split the path before theorising.**
`scp` reported 3456 MB transferred; 204800 bytes landed — twice, at identical size, for a 3.4 GB and
a 39 MB file. Two plausible hypotheses (a file-size `ulimit`, a full filesystem) were both wrong and
both cost a round trip. What settled it was `dd if=/dev/zero of=… bs=1M count=50`: 52 MB written
locally at 1.6 GB/s, no network involved, proving the destination innocent and the transport guilty
in one step. Prefer the experiment that halves the problem over the hypothesis that explains it.

**26. Quote what the tool printed; label what you concluded.**
Arguing that a node's admin port was uncabled, I wrote "nobody has physically looked at the LED" —
which no output supported and which asserted something about people I cannot observe. The defensible
version was narrower and stronger: two checks four hours apart still failing, zero packets ever on
that interface, `eth0 DOWN` holding a self-assigned link-local address. Findings get quoted;
inferences get named as inferences. The narrow claim is the one that survives being challenged.

**27. A liveness probe must treat any structured response as alive.**
Our recon script declared WSAPI down because unauthenticated `GET /api` returned
`403 {"code": 6, "desc": "invalid session key"}` — a service answering in its own protocol, which is
proof of life. The array's own `showwsapi` said `Enabled Active`. Only a connection failure means
dead. This is lesson 1 wearing different clothes: the probe asserted one specific success shape
instead of distinguishing *answered* from *did not answer*.

**28. An adapter that translates to a vendor API cannot be validated by a fake.**
`ensure_volume` had sent `{"tdvv": true, "compression": true}` for data-reduction volumes since the
day it was written, and every test passed — because every test used a fake WSAPI that accepted
whatever it was handed. The real array rejects it twice over: `tdvv` is the legacy 3PAR spelling
(`code 78 … required: tpvv,reduce`) and `compression` is not a field on that API at all
(`code 42 unrecognized name`). Fakes prove our code calls what we think it calls; only the endpoint
proves that is what it wants. Every vendor-API adapter needs one live probe, with the accepted body
recorded in a test so nobody restores the plausible-looking wrong one.
Corollary: the failure was identical at 1 GiB and 16 GiB, which refuted the "compressed volumes have
a 16 GiB minimum" theory outright. When two very different inputs fail the same way, the input is not
the variable — read the error text instead of pattern-matching it to a known constraint.

**29. Read the SDK function you depend on; "find" may be spelled "create".**
`ensure_host` leaned on python-3parclient's `findHost()` for WWN ownership — which does not query
anything: it runs `createhost <uuid> <wwn>` over the SDK's *own* SSH channel (never configured by
our client), parses "already used by host", and deletes its probe host. On our client it always
raised; a broad `except → None` made every WWN look unowned; the reconcile path then re-added an
already-present WWN, the array answered `EXISTENT_PATH` (it does so even against the *same* host),
and a conflict-swallow reported `exists` while silently dropping the new WWN — three defects
stacked so the failure looked like success. The unit stub had faithfully implemented `findHost` as
a working query, so every test was green; only the live zz_probe lifecycle caught it. Fixes worth
generalising: derive state from a read you already trust (`getHosts` → FCPaths), never from a
helper you haven't read; make the stub model the vendor's real surface (the fixed stub has **no**
`findHost`, so the trap cannot re-hide); and treat a conflict-swallow as a claim — it is only safe
if the request provably contains nothing the server could legitimately conflict on.

---

## When a decision lives only in a code comment

**30. A capability that no document authorises will still ship, and its own operator will not know it is there.**
ADR 0004 decided the tool never writes to a SAN switch. `CONTEXT.md` said the same in the glossary.
Neither was ever amended. A write path shipped anyway in v0.14.0/v0.15.0 on a verbal mandate recorded
in a docstring (`zoning_stage.py:2`) and an assistant's memory file, and nowhere else: `ALLOWED_WRITE`
came back to `brocade_client.py:47` while ADR 0004 line 98 still asserted it had been removed, and
`POST /zoning/stage` was added ungated. On 2026-08-31 the operator drove it against a live production
fabric and it created a zone and ran `cfgsave`. Two days later, reviewing that same session, **he
stated the tool had not written anything and that he had pasted the commands himself** — his SSH
transcript contains only `cfgshow`, `cfgtransshow` and `alishow`. His belief was consistent with every
document in the repository; only the code disagreed, and the code is what ran. A verbal mandate is not
a decision until it lands in the ADR and the glossary. Until then it is drift, and the person operating
the tool is the last to find out.

**31. "It never activates" is not the same promise as "it never writes" — say which one you mean.**
The staging design was scrupulous about the first: `cfgenable` was stripped from the batch AND absent
from the write allowlist, two independent guards, verified before the live run. It said nothing about
the second, and the operator heard the safety language and concluded the tool could not touch the
switch at all. The UI reinforced it by rendering `cfgenable <cfg>` in the same monospace block, weight
and colour as the four commands that had just executed, so the screen showed no boundary between what
the tool did and what a human must do. When a step both writes and withholds, the writing needs naming
at least as loudly as the withholding.

**32. A gate on intent-to-do is not a gate on done.**
`ZONING_OK = ("verified-proper", "staged")` let a staged-but-unactivated zone unlock provisioning.
Staging writes to the *defined* configuration; only `cfgenable` makes zoning real. On 2026-08-31 host
`10.132.30.86` was staged, the gate opened, and path verification then correctly reported `no_path`
for it, because that host still had no route to the array. The gate and the verifier disagreed and the
verifier was right. Gate on the observable end state — the host is logged in — never on the fact that
somebody asked for it.

**33. A fallback source is not a second source. If the fabric can see it, the plan must list it.**
The zoning plan took its host list from vCenter and consulted the switches' name servers only when
vCenter returned nothing. On 2026-09-12, rack13arcus: vCenter answered with three ESXi hosts, so the
plan showed three ESXi hosts — while the declared switches' own `nsshow` held a Windows server's
unzoned HBA (`51:40:2e:c0:20:89:cc:1e`, the very host the test existed to zone) and a Linux server's
two HBAs (`HN:localhost.localdomain OS:Linux`, one per fabric, unzoned on both). The Hosts-tab row the
operator had typed for the Windows host never reached the plan either. The step could not zone any of
them, and nothing on the screen said so: the hosts were simply absent. A mixed estate — Windows and
Linux beside a vCenter — is the customer case, not the exception. Every source that can see an
initiator contributes to the list (vCenter, the sheet, the array's logins, the declared switches'
local name servers); the source is shown on each row, and a later source may only fill a name an
earlier one left empty. `test_rack13_zoning_candidates_are_the_union_of_every_source` pins it to
the live captures.

**34. The data the operator asks for is usually already in the output you parsed and discarded.**
"Zoned to which host? By which zone?" — the zone name was in the `cfgshow` the plan had read to decide
`already_zoned`, and the plan kept only the boolean. "Why is `.86` offered on F2?" — `nscamshow`
prints `Switch entry for 32` above the entry and `fabricshow` names domain 32; the plan kept only the
WWPN. Each answer cost the operator a second SSH session and a paste into chat. When a parser reduces
a rich record to a flag, keep the identifying field beside the flag (`zone_names`, `placed_on_switch`,
`switch_name`, `fabric_name`): the screen can then show its evidence instead of asking to be trusted.
