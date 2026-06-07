---
title: "GLCP Audit Logs API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail.md"
scraped_at: "2026-06-07T06:13:42.223398+00:00Z"
---

# GLCP Audit Logs API

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

[GLCP Audit Logs API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail.yaml)

## UI-AuditLogs

### Get all audit logs of an application instance or workspace.

 - [GET /auditlogs/ui/v1/search](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/getauditlogs.md)

### Get additional detail of an audit log.

 - [GET /auditlogs/ui/v1/details](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/getauditlogdetails.md)

### Get all the application instance details.

 - [GET /auditlogs/ui/v1/applications](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/getapplications.md)

### Get the audit log configurations related to an application

 - [GET /auditlogs/ui/v1/{application-id}/configs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/getauditlogconfigs.md)

### Post external application audit logs specific configurations.

 - [POST /auditlogs/ui/v1/configs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/createauditlogconfigs.md)

### Update external application audit logs specific configurations.

 - [PUT /auditlogs/ui/v1/configs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/updateauditlogconfigs.md)

### Delete external application audit logs specific configurations.

 - [DELETE /auditligs/ui/v1/configs/{audit-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/deleteauditlogconfigs.md)

### Get the number of audit logs in the system for the current customer-id from given timestamp

 - [GET /auditlogs/ui/v1/count](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/getauditlogscount.md)

### Download audit logs in CSV or PDF format.

 - [GET /auditlogs/ui/v1/download](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/downloadauditlogs.md)

