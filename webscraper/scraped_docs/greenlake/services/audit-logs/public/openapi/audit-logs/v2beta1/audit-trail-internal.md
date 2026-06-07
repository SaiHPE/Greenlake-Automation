---
title: "GLCP Audit Logs Internal API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-internal.md"
scraped_at: "2026-06-07T05:46:43.781314+00:00Z"
---

# GLCP Audit Logs Internal API

The HPE GreenLake Audit Log Service offers a collection of RESTful APIs for publishing audit logs, configuring audit settings, and querying both service-specific and overall platform logs.

Version: v2beta1
License: HPE License

## Servers

```
http://audit-trail-svc.ccs-system.svc.cluster.local
```

## Download OpenAPI description

[GLCP Audit Logs Internal API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-internal.yaml)

## Fetch Audit logs

Retrieves audit logs of one or more services.

### Retrieves audit logs of one or more services.

 - [POST /audit-log/v2beta1/logs-search](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-internal/fetch-audit-logs/getauditlogs.md): This API facilitates to search and retrieve audit logs for one or more services based on a flexible filters. It supports filtering by service offer ID, region, time range, and many other fields. 
- To retrieve the logs of HPE GreenLake service the region field is not required. Use 00000000-0000-0000-0000-000000000000 as the service offer ID.
- For external services such as Computes Ops Manager, Aruba central and others specifying a valid region is required along with service offer id.

This API supports cursor based pagination to fetch the next set of audit logs.

Rate limits:
- 100 requests per minute per user.
- 300 requests per minute overall.

