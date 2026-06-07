---
title: "GLCP Audit Logs API - Async Operations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-async-operations.md"
scraped_at: "2026-06-07T05:46:43.781469+00:00Z"
---

# GLCP Audit Logs API - Async Operations

APIs to get the audit log async operation status.

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

[GLCP Audit Logs API - Async Operations](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-async-operations.yaml)

## Async Operations

APIs to get the audit log async operation status.

### Get the list of async operations.

 - [GET /audit-log/v2beta1/async-operations](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-async-operations/async-operations/getasyncoperations.md): This endpoint retrieves the list of asynchronous audit log publish operations related to a specific workspace. Users can filter the operations based on their status using the filter query parameter.
A valid service identity workspace-scoped access token is required to access this API.

Rate limits:
- 1,000 requests per minute

### Get the status of the audit log publish operation.

 - [GET /audit-log/v2beta1/async-operations/{operation-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-async-operations/async-operations/getasyncoperationstatus.md): This endpoint retrieves the status of an asynchronous audit log publish operation.
The operation-id is the unique identifier returned when the audit log was published.
A valid service identity token is required to access this API.

Rate limits:
- 1,000 requests per minute

