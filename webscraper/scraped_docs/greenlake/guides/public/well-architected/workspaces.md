---
title: "GreenLake Workspace Architecture Best Practices"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/guides/public/well-architected/workspaces.md"
scraped_at: "2026-06-07T05:46:17.530151+00:00Z"
---

# GreenLake Workspace Architecture Best Practices

GreenLake offers multiple workspace architecture patterns that support organizational hierarchies, simplify identity governance, and keep service operations flexible. This guide helps you choose the right workspace architecture model, plan your rollout, and migrate to the best practices described in this guide. This guide does not provide detailed step-by-step instructions, but references user guide sections where appropriate for more information.

![Workspace overview diagram](/assets/workspace-side-by-side-basic.2fde33b620a3078417d37daee5bae61e0a41e71ba2be44ace04ff8aaed42f02a.583bf996.png)

## How to Use This Guide

- Start with **Workspace Architecture Guide** to learn best practices for workspace design, including when to consolidate or separate services, proven design principles, and service compatibility guidance.
- Review **Identity Governance Essentials** for domain claiming, SSO, SCIM, and role assignment implementation.
- Use **Migration Paths** when ready to align existing workspaces with these best practices.


| Section | Purpose |
|  --- | --- |
| [Workspace Architecture Guide](/docs/greenlake/guides/public/well-architected/workspaces/workspace-architecture-guide) | Apply workspace design best practices: consolidation vs separation strategies, design principles, and service compatibility guidance. |
| [Identity Governance Essentials](/docs/greenlake/guides/public/well-architected/workspaces/identity-governance) | Implement domain claiming, SSO, SCIM, and role assignment across your hierarchy. |
| [Migration Paths](/docs/greenlake/guides/public/well-architected/workspaces/workspaces-migration-paths) | Choose the right onboarding or migration approach for your current estate. |


## Why Adopt the Best Practices Hierarchy?

Organizations that separate governance from execution gain:

- **Clear ownership**: Domains, identity providers, and lifecycle controls stay in the
organization parent so member workspace teams can focus on service operations.
- **Policy isolation**: Production, non-production, and sensitive services can live in
different workspaces with the right policies and guardrails.
- **Risk reduction**: Incidents in one workspace do not spill into others, limiting the
blast radius of operational issues.
- **Quota flexibility**: Service quotas and API rate limits remain local to each
workspace, avoiding contention across teams.
- **Operating model fit**: Central, decentralized, or hybrid teams can each adopt a
structure that matches their governance needs.


These outcomes align with the Identity Governance capabilities of GreenLake, which provide user and
group directories, centralized SSO authentication policies, and SCIM-based provisioning across the
organization.

## Where to Find Procedural Details

These best practices focus on why and when. For "how" tasks such as claiming a DNS
domain, configuring SSO authentication policies, or editing scope groups, follow the
**GreenLake Organization and Enhanced IAM Management** user guide. The guide lives
in the HPE Support Center and remains the authoritative source for clicks and API calls.

## Next Steps

1. Confirm which services you operate today and whether they require tenant-level
aggregation.
2. Decide if you will adopt the enterprise hierarchy, MSP hierarchy, or both.
3. Continue to [Workspace Architecture Guide](/docs/greenlake/guides/public/well-architected/workspaces/workspace-architecture-guide) for workspace design best practices.