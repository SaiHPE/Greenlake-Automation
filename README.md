# Greenlake-Automation

End-to-end onboarding automation for **HPE Alletra Storage MP B10000** into HPE GreenLake and Data Services Cloud Console (DSCC).

## What's here

| File | Description |
|---|---|
| `AUTOMATION_PLAN.md` | Full Python implementation plan — 3 components (GreenLake REST / Connectivity Wizard / DSCC Setup) + orchestrator, module layout, build milestones |
| `FEASIBILITY.md` | Deep-research feasibility report — REST vs GUI-only step mapping, API endpoint details, screenshot evidence, open items |

## Architecture (TL;DR)

Three components, run in order **A → B → C** per array:

```
A) GreenLake REST (headless)    — register + subscribe + assign via platform REST API
B) Connectivity Wizard (Playwright) — drive on-array cloudinit UI (link-local, no auth)
C) DSCC Setup (Playwright)      — drive Setup Service wizard (attach logged-in session)
```

Running A first eliminates the `fail-prov-no-device` / `fail-prov-no-rule` error loop seen when the array phones home before it's registered.

## Stack

Python · `httpx` · `tenacity` · `pydantic` · `playwright` · `typer` · `rich`

## Status

Planning complete. Implementation starts at Milestone 1 (auth + smoke test).
See `AUTOMATION_PLAN.md §8` for the full milestone list.
