---
title: "GLCP Audit Logs Internal API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail-internal.md"
scraped_at: "2026-06-07T05:46:42.900415+00:00Z"
---

# GLCP Audit Logs Internal API

The HPE GreenLake Audit Log Service offers a collection of RESTful APIs for publishing audit logs and querying both application-specific and overall platform logs.

Version: v1
License: HPE License

## Servers

```
https://hoku-default-user-api.ccs.arubathena.com
```

```
https://mira-default-user-api.ccs.arubathena.com
```

```
https://polaris-default-user-api.ccs.arubathena.com
```

```
https://pavo-default-user-api.ccs.arubathena.com
```

## Security

### BearerAuth

Type: http
Scheme: bearer
Bearer Format: JWT

### CookieAuth

Type: apiKey
In: cookie
Name: ccs-session

## Download OpenAPI description

[GLCP Audit Logs Internal API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail-internal.yaml)

## UI-AuditLogs

### Get all audit logs of an application instance or workspace for report generation.

 - [POST /auditlogs/internal/v1/logs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail-internal/ui-auditlogs/getauditlogs.md): API to get the audit logs of application instance or platform logs required for the export.
app_slug and application_customer_id are mandatory to get the application instance logs.
service_offer_id and region are mandatory to get the service instance logs.
Audit logs can be filtered based on the following parameters:
- categories
- exclude_categories
- start_time
- end_time
- description
- username
- ip_address
- workspace_name
- workspace_type
- target

Following are the additional filters that can be applied to external application audit logs:
- device_type
- server_serial
- server_name
- server_product_id

This API supports cursor based pagination to fetch the next set of audit logs.

