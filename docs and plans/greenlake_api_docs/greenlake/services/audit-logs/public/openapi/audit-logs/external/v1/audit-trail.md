---
title: "HPE GreenLake API for Audit Logs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/external/v1/audit-trail.md"
scraped_at: "2026-06-07T05:46:47.569856+00:00Z"
---

# HPE GreenLake API for Audit Logs

The HPE GreenLake Audit Log Service offers a collection of RESTful APIs for publishing audit logs and querying both application-specific and overall platform logs.

Version: v1
License: HPE License

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### BearerAuth

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake API for Audit Logs](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/audit-logs/public/openapi/audit-logs/external/v1/audit-trail.yaml)

## Audit logs - v1

### Get all audit logs of an application or user.

 - [GET /audit-log/v1/logs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/external/v1/audit-trail/audit-logs-v1/getauditlogs.md): The audit logs can be filtered using a variety of parameters. Queries should be separated by and and can utilize eq, contains, and in operators to construct the final query. Each query should follow the format:
* key eq 'value' for equality operation.
* contains(key, 'value') for contains operation.
* key in ('value1', 'value2') for in operation.

| Filter parameter         | Supported Operators | Type                    | Example                                                                                         |
|--------------------------|---------------------|-------------------------|-------------------------------------------------------------------------------------------------|
| createdAt                | lt, ge              | RFC timestamp in string | createdAt ge '2024-02-16T07:54:55.0Z'                                                           |
| category                 | eq, in              | string                  | category eq 'User Management' category in ('Device Management', 'User Activity')                |
| description              | eq, contains        | string                  | contains(description, 'Logged in') description eq 'User test@test.com logged in via ping mode.' |
| additionalInfo/ipAddress | eq, contains        | IP string               | additionalInfo/ipAddress eq '192.168.12.12' contains(additionalInfo/ipAddress, '192.168')       |
| user/username            | eq, contains        | email in string         | user/username eq 'test@test.com' contains(user/username, '@gmail.com')                          |
| workspace/workspaceName  | eq, contains        | string                  | workspace/workspaceName eq 'Example workspace' contains(workspace/workspaceName, 'Example')     |
| application/id           | eq                  | UUID in string          | application/id eq '12312-123123-123123-123121'                                                  |
| region                   | eq                  | region code in string   | region eq 'us-west'                                                                             |
| hasDetails               | eq                  | boolean                 | hasDetails eq 'true'                                                                              |

### Get additional detail of an audit log.

 - [GET /audit-log/v1/logs/{id}/detail](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/external/v1/audit-trail/audit-logs-v1/getauditlogdetails.md)

