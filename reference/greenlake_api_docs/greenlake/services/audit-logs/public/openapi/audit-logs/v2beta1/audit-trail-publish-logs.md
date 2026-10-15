---
title: "Audit Logs API - Publish Logs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-publish-logs.md"
scraped_at: "2026-06-07T06:13:42.621928+00:00Z"
---

# Audit Logs API - Publish Logs

APIs to publish the service and platform audit logs.

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

[Audit Logs API - Publish Logs](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-publish-logs.yaml)

## Publish Logs

APIs to publish the service and platform audit logs.

### Publish an audit log event.

 - [POST /audit-log/v2beta1/logs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-publish-logs/publish-logs/publishserviceauditlog.md): This API facilitates the publication of audit logs by external and internal services that are part of the HPE GreenLake platform. 
It accepts detailed information regarding the audit log event, encompassing the service name, category, description, username, IP address, and any supplementary data. This operation is asynchronous, and the status of the publish operation can be monitored at the URI specified in the Location Response Header.
All the onboarded service offers on the GreenLake Platform must include the serviceOffer details in the audit log payload. Other core services that are part of the GreenLake platform can skip this field or set the serviceOffer.id to 00000000-0000-0000-0000-000000000000

A valid Service Identity workspace-scoped access token is required. For logs not tied to a workspace, use a token scoped to the Audit trail Undercloud workspace ID.

Rate Limits:

 - 3,000 requests per minute per service.
 - 9,000 requests per minute overall.

