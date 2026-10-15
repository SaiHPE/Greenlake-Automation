---
title: "Audit Logs API - Fetch Audit Logs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs-public/v2beta1/audit-trail-fetch-v2beta1.md"
scraped_at: "2026-06-07T06:13:42.898098+00:00Z"
---

# Audit Logs API - Fetch Audit Logs

APIs to retrieve audit logs of one or more services.

Version: v2beta1
License: HPE License

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### Bearer

Personal access token compliant with RFC8725 issued by the HPE GreenLake platform.

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Audit Logs API - Fetch Audit Logs](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/audit-logs/public/openapi/audit-logs-public/v2beta1/audit-trail-fetch-v2beta1.yaml)

## Fetch Audit Logs

Retrieves audit logs of one or more services.

### Retrieves audit logs of one or more services.

 - [GET /audit-log/v2beta1/logs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs-public/v2beta1/audit-trail-fetch-v2beta1/fetch-audit-logs/getauditlogs.md): The audit logs can be filtered using a variety of parameters. Queries should be separated by and and can utilize eq, contains, and in operators to construct the final query. Each query should follow the format:
 * key eq 'value' for equality operation.
 * contains(key, 'value') for contains operation.
 * key in ('value1', 'value2') for in operation.

| Filter Parameter | Supported Operators | Type                | Example |
|-----------------------|-------------------------|--------------------------|--------------|
| createdAt         | lt, ge              | RFC timestamp (string)   | createdAt ge '2024-02-16T07:54:55.0Z' |
| category          | eq, in              | string                   | category eq 'User Management'category in ('Device Management', 'User Activity') |
| description       | eq, contains        | string                   | contains(description, 'Logged in')description eq 'User test@test.com logged in via ping mode.' |
| ipAddress         | eq, contains        | IP string                | ipAddress eq '192.168.12.12'contains(ipAddress, '192.168') |
| username          | eq, contains        | email (string)           | username eq 'test@test.com'contains(username, '@gmail.com') |
| workspace/name    | eq, contains        | string                   | workspace/name eq 'Example workspace'contains(workspace/name, 'Example') |
| workspace/type    | eq                    | string                   | workspace/type eq 'TENANT'workspace/type eq 'MSP' |
| serviceOffer/id   | eq, in              | UUID (string)            | serviceOffer/id eq '902fa943-dcfc-432c-a92c-3a3a454923d9'serviceOffer/id in ('902fa943-dcfc-432c-a92c-3a3a454923d9', '00000000-0000-0000-0000-000000000000') |
| region            | eq                    | region code (string)     | region eq 'us-west' |
| hasDetails        | eq                    | boolean                  | hasDetails eq 'true' |

 Note: Maximum five serviceOffer/id can be passed in the filter. If no serviceOffer/id is passed, only platform audit logs will be fetched.
 Note: Maximum five serviceOffer/id can be passed in the filter. If no serviceOffer/id is passed, only HPE GreenLake Platform Audit logs will be fetched.

 The API supports pagination and sorting options to efficiently retrieve large datasets

 Rate limits:
 - 100 requests per minute per user.
 - 300 requests per minute overall.

### Get a specific audit log.

 - [GET /audit-log/v2beta1/logs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs-public/v2beta1/audit-trail-fetch-v2beta1/fetch-audit-logs/getauditlog.md)

### Get a specific audit log details.

 - [GET /audit-log/v2beta1/logs/{id}/details](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs-public/v2beta1/audit-trail-fetch-v2beta1/fetch-audit-logs/getauditlogdetails.md)

