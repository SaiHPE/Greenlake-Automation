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
