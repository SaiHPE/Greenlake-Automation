---
title: "IAM Resource Quotas | HPE GreenLake"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/iam/iam-quotas.md"
scraped_at: "2026-06-07T06:13:19.794839+00:00Z"
---

# IAM Resource Quotas

HPE GreenLake enforces resource quotas to maintain optimal platform performance, security, and reliability across all customer environments. These predefined limits establish the maximum number of resources you can create within your HPE GreenLake organization or workspace while ensuring consistent service delivery and system stability as your usage scales.

## Resource Quota Management Strategies

To maximize efficiency within the established quotas, consider implementing these best practices:

- **Workspace Distribution:** Strategically allocate resources across multiple workspaces and organizations to optimize quota utilization
- **User Group Structure Optimization:** Design user groups to balance membership and minimize redundancy
- **Regular Maintenance:** Implement periodic reviews to identify and remove inactive users and unused resources
- **Hierarchical Planning:** Structure your organization and workspace architecture with quota limitations in mind


While per organization quota increases are not currently available, the HPE GreenLake team continuously evaluates quota limits based on customer feedback. If your business requirements exceed current quotas, please submit detailed information through the Feedback feature in the HPE GreenLake console.

## Current IAM Quotas

| Resource Type | Maximum Limit |
|  --- | --- |
| Users per organization | 5500 |
| User groups per organization | 200 |
| Members (users) per user group | 200 |
| User groups per user | 200 |
| Workspaces per organization | 25 |
| Domain claim requests per organization | 100 |
| Domains per organization | 20 |
| SSO profiles per organization | 20 |
| SSO routing rules | 20 |
| Domains per SSO profile | 1 |
| Domains per SSO routing rule | 1 |
| Roles per workspace (1) | 100 |
| Role assignments per user per workspace | 50 |
| Scope Groups per workspace | 500 |
| Scopes per scope group | 500 |
| Scope groups per role assignment | 10 |
| Workspace (tenant) groups per role assignment | 10 |
| Role assignments per user group per workspace | 50 |
| Permissions per custom role | 1000 |


**Notes**:

(1) Roles per workspace in addition to the global predefined roles.