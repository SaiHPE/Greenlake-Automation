# Greenlake-Automation

Automation for onboarding **HPE Alletra MP B10000** storage arrays into **HPE GreenLake + DSCC**.

## 👉 The app lives here

**[`Provisioning_Automation/alletra_onboard/`](Provisioning_Automation/alletra_onboard/)** — the
operator web app (`onboard ui`) and CLI that drive all three onboarding steps:

- **A** — GreenLake REST (register device, assign to Data Services, subscribe, verify)
- **B** — the on-array Cloud Connectivity Wizard (Playwright)
- **C** — the DSCC "Set Up System" wizard (Playwright)

Start with its **[README](Provisioning_Automation/alletra_onboard/README.md)** — it covers
setup, the jump-box ↔ laptop sync model, how to run the web app, and the current open issues.

## Other folders

| Folder | What it is |
|---|---|
| `alletra-ui-capture-kit-extracted/` | recon tooling for capturing Playwright wizard locators (stale partial copy; the live capture scripts are under the app's `scripts/`) |
| `docs and plans/` | GreenLake API docs and planning notes |
| `webscraper/` | scraped GreenLake API reference |
