# Phase 3 acceptance checklist

The single manual verification pass for the UX redesign (ADR 0011: the frontend has no automated
tests; `tsc` and the production build gate every commit, and this checklist is executed once at the
end). Run it against a real backend. Record the date, build and outcome at the bottom.

Reference: [`mockups.html`](mockups.html) is the authority for layout and wording.

## A. Chrome — verify once, applies to every screen

- [ ] Header shows the **HPE Element** and the service name. **No HPE GreenLake lockup anywhere.**
- [ ] Header shows serial, mode and run status once a run exists; nothing stale before that.
- [ ] Rail groups steps under **Prepare / Initialize / Provision / Document**.
- [ ] Rail shows a status icon per step, and a result hint under completed steps
      (for example "4 ports · 6 adapters" after discovery).
- [ ] Steps not yet reachable are dimmed and not clickable; visited steps are clickable.
- [ ] **Previous step** is disabled on the first step and works everywhere else.
- [ ] **Cancel run** is disabled with no run; with a run it opens the confirmation
      ("Discard this run?" · Keep run / Discard run) and discarding returns to step 1.
- [ ] Every step header reads **"Step X of Y"**, with Y matching the number of rail entries.
- [ ] Status wording is only ever: Not started, Running, Action required, Complete, Failed.
- [ ] Every status shows an icon as well as colour; none rely on colour alone.
- [ ] Keyboard: Tab reaches every control, focus is clearly visible, Enter activates.
- [ ] No screen shows more than one spinner at a time.
- [ ] The word "health" appears nowhere in the interface.

## B. Per-mode walkthrough

Run each mode from a fresh start (Cancel run between modes). Confirm the rail contains exactly the
expected steps and that each screen matches its mockup.

### B1 Full onboarding
- [ ] Rail: Prerequisites, Initialisation sheet, Mode, GreenLake registration, Cloud Connectivity,
      DSCC setup, Verify configuration, As-built document, Finish.
- [ ] Prerequisites: recordings play; region selector updates the firewall list; **Test connectivity**
      populates a table with a summary count; proxy panel reflects the detected proxy.
- [ ] Initialisation sheet: template downloads; uploading a completed workbook shows
      "Workbook validated" and the parsed values; **Validate GreenLake credentials** reports a result.
- [ ] Mode: five options (one only, relabelled "Initialization", in the init-only build); selecting
      **Create run** mints the run and the header populates.
- [ ] GreenLake registration: **Dry run (no writes)** and **Register the array**; the button shows a
      busy state while running; activity lists each phase.
- [ ] Cloud Connectivity: an invalid address is rejected with guidance; values to be applied are
      listed; if the array waits for submission the **Action required** banner appears.
- [ ] DSCC setup: browser launches and reports attached; after the automation the **Action required**
      banner explains the credential step; **Mark DSCC complete** enables only then.
- [ ] Verify configuration: **title is "Verify configuration"**; credentials help text states the
      password is not stored; results table shows Match / Mismatch with a summary count.
- [ ] As-built document: cover fields default from the workbook; generation reports the file size;
      **Download document** returns a .docx that opens.
- [ ] Finish: summary, run timeline, and **Start a new deployment**.

### B2 Provision storage only
- [ ] Rail: Discovery, SAN zoning, Provision storage, Verify configuration, As-built, Finish.
- [ ] Discovery: empty state before running; afterwards, ports and hosts tables with fabric logins
      and summary counts.
- [ ] SAN zoning: one row per host with both fabrics; unverified hosts explained; the plan renders
      commands for the SAN team; nothing is written to a switch.
- [ ] Provision storage: builder loads the palette; **Build plan** lists actions with Create/Exists;
      the approval gate appears; **Create storage objects** applies and reports outcomes;
      **Verify paths** reports Live / Partial / No path without blocking.

### B3 Onboard, then provision
- [ ] Rail contains all eight run steps in registry order.

### B4 Verify only
- [ ] Rail: Verify configuration, As-built document, Finish only.

### B5 Custom
- [ ] Selecting zoning or provisioning without discovery shows the "Discovery is required" warning
      and blocks run creation.
- [ ] A custom selection produces exactly those steps in registry order.

## C. Resilience

- [ ] Reload the browser mid-run: the run is restored and the wizard resumes on the right step.
- [ ] Restart the application mid-run: discovery results and the as-built document are still
      available (they persist with the run).
- [ ] Restart the application after building a provisioning plan: **Create storage objects is not
      available** until the plan is rebuilt — the approval to write to the array does not survive a
      restart. Same after editing the composition, and after re-running discovery.
- [ ] Steps that use discovery state when the environment was last read; a run resumed more than
      twelve hours later shows the staleness warning naming the age.
- [ ] Stop the backend and trigger an action: the error appears in the step's error banner with a
      dismiss control, and the step stays usable.

## D. Sign-off

| | |
|---|---|
| Date | |
| Build / commit | |
| Executed by | |
| Result | |
| Defects raised | |
