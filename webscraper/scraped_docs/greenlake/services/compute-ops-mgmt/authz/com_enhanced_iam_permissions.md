---
title: "Compute Ops Management Permissions - Enhanced IAM"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/authz/com_enhanced_iam_permissions.md"
scraped_at: "2026-06-07T05:45:59.435103+00:00Z"
---

# Compute Ops Management Permissions - Enhanced IAM

This page lists the enhanced IAM permissions associated with Compute Ops Management, along with which built-in roles contain the permission and whether or not the permission is affected by granular scoping. To read more about granular scoping see [Compute Ops Management Scope Based Access Control (SBAC) - Enhanced IAM](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/authz/com_v2_sbac/).

## Built-in roles

There are three built-in roles for Compute Ops Management: Viewer, operator, and administrator. Each role has a pre-defined
set of permissions.

| Permission | Description | Viewer | Operator | Administrator | Supports granular scoping |
|  --- | --- | --- | --- | --- | --- |
| compute-ops-mgmt.appliance.create | Create an appliance. |  |  | X |  |
| compute-ops-mgmt.appliance.delete | Delete an appliance. |  |  | X |  |
| compute-ops-mgmt.appliance.read | View appliance information. | X | X | X |  |
| compute-ops-mgmt.appliance.update | Perform actions that affect appliances. |  | X | X |  |
| compute-ops-mgmt.appliance.use | Use an appliance. |  | X | X |  |
| compute-ops-mgmt.approval.policy.create | Create an approval policy. |  |  | X |  |
| compute-ops-mgmt.approval.policy.delete | Delete an approval policy. |  |  | X |  |
| compute-ops-mgmt.approval.policy.read | View approval policy information. | X | X | X |  |
| compute-ops-mgmt.approval.policy.update | Update an approval policy. |  |  | X |  |
| compute-ops-mgmt.approval.request.approve | Approve or decline an approval request. |  | X | X |  |
| compute-ops-mgmt.approval.request.read | View approval request information. | X | X | X |  |
| compute-ops-mgmt.async-operation.read | View async operation information. | X | X | X |  |
| compute-ops-mgmt.filter.create | Create a filter. |  |  | X |  |
| compute-ops-mgmt.filter.delete | Delete a filter. |  |  | X |  |
| compute-ops-mgmt.filter.manage-scope | Configure scope based access control enabled saved filters. |  |  | X |  |
| compute-ops-mgmt.filter.read | View filter information. | X | X | X |  |
| compute-ops-mgmt.filter.update | Update a filter. |  | X | X |  |
| compute-ops-mgmt.group.create | Create a group. |  |  | X |  |
| compute-ops-mgmt.group.delete | Delete a group. |  |  | X |  |
| compute-ops-mgmt.group.read | View group information. | X | X | X |  |
| compute-ops-mgmt.group.update | Update a group. |  |  | X |  |
| compute-ops-mgmt.group.use | Change devices associated with a group. |  | X | X |  |
| compute-ops-mgmt.schedule.create | Create a schedule. |  |  | X |  |
| compute-ops-mgmt.schedule.delete | Delete a schedule. |  |  | X |  |
| compute-ops-mgmt.schedule.read | View schedule information. | X | X | X |  |
| compute-ops-mgmt.schedule.update | Update a schedule. |  | X | X |  |
| compute-ops-mgmt.server.read | View server and general application information. | X | X | X |  |
| compute-ops-mgmt.server.update | Perform actions that affect servers. |  | X | X | X |
| compute-ops-mgmt.setting.create | Create a setting. |  |  | X |  |
| compute-ops-mgmt.setting.delete | Delete a setting. |  |  | X |  |
| compute-ops-mgmt.setting.read | View setting information. | X | X | X |  |
| compute-ops-mgmt.setting.update | Update a setting. |  |  | X |  |
| compute-ops-mgmt.setting.use | Change settings associated with a group. |  | X | X |  |
| compute-ops-mgmt.webhook.create | Create a webhook. |  |  | X |  |
| compute-ops-mgmt.webhook.delete | Delete a webhook. |  |  | X |  |
| compute-ops-mgmt.webhook.read | View webhook information. | X | X | X |  |
| compute-ops-mgmt.webhook.update | Update a webhook. |  |  | X |  |


## Using Compute Ops Management permissions

If none of the built-in roles provide the set of permissions needed, a custom role can be created and assigned any set of permissions.

To create a custom role, or view the permissions associated with built-in roles, use the HPE GreenLake Roles & permissions page. Read more about this process in the [HPE GreenLake user role documentation](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-1066A7AF-9361-4771-8535-9AD48B0DE9A6.html).

To assign a role, use the HPE GreenLake Workspace identity & access page. Read more about this process in the [HPE GreenLake assign roles documentation](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-8585957F-463B-4DA6-BCD2-8D18F2CF2CC5.html).