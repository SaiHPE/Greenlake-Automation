---
title: "Compute Ops Management Scope Based Access Control (SBAC) - Enhanced IAM"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/authz/com_enhanced_iam_sbac.md"
scraped_at: "2026-06-07T05:45:59.384491+00:00Z"
---

# Compute Ops Management Scope Based Access Control (SBAC) - Enhanced IAM

HPE GreenLake has [scope groups](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&docLocale=en_US&page=GUID-3AEC80EA-D68A-4E02-BCE9-BCA921F636FE.html) that can be used to implement SBAC in Compute Ops Management.

A *scope resource* is a "type" of resource that Compute Ops Management uses to limit access​.

The scope resource available in Compute Ops Management is saved filters. You can use saved filters to restrict access to servers in Compute Ops Management. When configured, access to the *compute.server.edit* permission is restricted.

## Steps to use SBAC

1. In Compute Ops Management, create a saved filter with scope based access control enabled.
  1. [API endpoint to create a saved filter](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/create_filter/)
    1. Ensure when creating this that the field for enabling scope based access control is set.
  2. [User guide entry for creating a saved filter](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00004003en_us&page=compute_cr_saved_filter.html)
2. In HPE GreenLake, configure a scope group.
  1. Configure the Compute Ops Management scope resource created in the previous step with a scope group.
    1. [HPE GreenLake documentation about creating a scope group](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-A6EF8DF6-CE78-4E4B-B185-7DBD553C75FB.html)
3. After the previous steps are completed, you can apply the scope resource to a role.