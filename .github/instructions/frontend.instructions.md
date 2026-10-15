---
applyTo: "Provisioning_Automation/alletra_onboard/frontend/**"
---
# Frontend (React + Grommet, HPE Design System)

- Edit `frontend/src` only. Never edit or commit `frontend/dist`; it is rebuilt after merge.
- Follow `docs/UX-GUIDELINES.md` (app folder): one `h1` per page, step pages built on `ui/StepShell`
  with the footer actions, `StatusLine` for the step's state, `Section` for folded detail, sentence
  case, plain operator language with no ADR, SPEC or version numbers on screen.
- A step's progress comes from `ui/useStepState` and the run's events; do not keep a second copy of
  step state in a component. Step lists and modes come from `/app/profile`, never a hardcoded list.
- Any action that writes to an array needs an explicit confirmation tick before its button works.
- Check with `npm run typecheck`. Look at the change at 1366 x 768 and 1080 x 720 and attach
  screenshots to the pull request.
- Mockups for new screens go in `frontend/mockups` (`npm run mockups`), reviewed before building.
