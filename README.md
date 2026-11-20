# Greenlake-Automation

Automation for deploying **HPE Alletra Storage MP B10000** arrays: onboarding into HPE GreenLake and
DSCC, host and fabric discovery, SAN-zoning command sets, block provisioning, Remote Copy
replication with a failover test, verification and the as-built document. Operators run it as a
local web app on a Windows jump box next to the array.

## Where things are

| Path | What it is |
|---|---|
| [`Provisioning_Automation/alletra_onboard/`](Provisioning_Automation/alletra_onboard/) | **The app.** Its [README](Provisioning_Automation/alletra_onboard/README.md) covers setup, running it, the branch and pull request flow, lab runs and releases. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | **New to the team? Start here:** access, setup, how work flows from an issue to a merged pull request, lab runs. |
| [`AGENTS.md`](AGENTS.md) | Rules, layout and commands for everyone working here, people and coding agents alike. Read it first. |
| [`reference/greenlake_api_docs/`](reference/greenlake_api_docs/) | Offline mirror of the GreenLake developer portal (start at `reference/greenlake_api_docs/greenlake/services.md`). |
| [`archive/`](archive/) | Old plans and tools kept for history; not used by the app. |
| `.github/` | Pull request template, code owners, area rules for coding agents, dormant workflows. |

Open work is tracked as [issues on github.hpe.com](https://github.hpe.com/g-sai-roopesh/greenlake-automation/issues).
