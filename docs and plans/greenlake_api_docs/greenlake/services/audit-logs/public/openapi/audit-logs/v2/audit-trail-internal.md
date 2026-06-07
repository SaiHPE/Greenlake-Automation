---
title: "GLCP Audit Logs Internal API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2/audit-trail-internal.md"
scraped_at: "2026-06-07T05:46:43.284724+00:00Z"
---

# GLCP Audit Logs Internal API

The HPE GreenLake Audit Log Service offers a collection of RESTful APIs for publishing audit logs and querying both application-specific and overall platform logs.

Version: v2
License: HPE License

## Servers

```
http://audit-trail-svc.ccs-system.svc.cluster.local
```

## Download OpenAPI description

[GLCP Audit Logs Internal API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2/audit-trail-internal.yaml)

## UI-AuditLogs

### Get all audit logs of an application instance or workspace for report generation.

 - [POST /internal-audit-log/v2/logs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2/audit-trail-internal/ui-auditlogs/getauditlogs.md): API to get the audit logs of application instance or platform logs required for the export.
appSlug and applicationCustomerId are mandatory to get the application instance logs.
serviceOfferId and region are mandatory to get the service instance logs.
Audit logs can be filtered based on the following parameters:
- categories
- excludeCategories
- startTime
- endTime
- description
- username
- ipAddress
- workspaceName
- workspaceType
- target

Following are the additional filters that can be applied to external application audit logs:
- deviceType
- serverSerial
- serverName
- serverProductId

This API supports cursor based pagination to fetch the next set of audit logs.

