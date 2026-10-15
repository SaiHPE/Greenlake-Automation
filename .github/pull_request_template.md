<!-- Title: "BL-NN: what this changes, in plain words". It becomes the commit message on main. -->

## What and why

Closes #<!-- issue number -->

<!-- What changes for the operator or the code, and why. Two or three sentences. -->

## Check output

<!-- Paste the block from: .venv/bin/python scripts/check.py  (Windows: .venv\Scripts\python scripts\check.py) -->

```
```

## Live run

- [ ] Run live on a lab jump box: <!-- script, jump box, date, result zip, PASS/FAIL count -->
- [ ] Not run live yet: this is **built, pending live run** (say what still needs a live run)
- [ ] Not needed: no change reaches an array, switch, vCenter or GreenLake

## Before asking for review

- [ ] One tracker item (`BL-NN`) per pull request, branched from an up-to-date `main`
- [ ] No change under `frontend/dist` (it is rebuilt after merge)
- [ ] UI change: screenshots at 1366 x 768 attached below
- [ ] A new array, switch or vCenter command: added to the read-only allowlist with a test, or this is a WSAPI write that the operator approves first
- [ ] Docs that describe the changed behaviour are updated (README, SCOPE, an ADR or SPEC if it is a decision)
- [ ] No password, token, customer name or customer address in code, fixtures or screenshots
