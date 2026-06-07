---
title: "Audit Logs API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-config.md"
scraped_at: "2026-06-07T06:13:42.276875+00:00Z"
---

# Audit Logs API

The HPE GreenLake Audit Log Service offers a collection of RESTful APIs for publishing, modifying, deleting and querying configurations.

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

[Audit Logs API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-config.yaml)

## Audit trail configurations

APIs to manage audit trail configurations for service offers.

### Get the unified audit configurations for the given list of service offer IDs.

 - [GET /audit-log/v2beta1/configs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-config/audit-trail-configurations/getauditconfigs.md): Up to 5 service offer Ids can be passed in the query parameter. This API accepts valid 1.x tokens.

### Create external service audit configurations.

 - [POST /audit-log/v2beta1/configs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-config/audit-trail-configurations/createauditconfigs.md): This API helps to create audit configurations. This API accepts valid 1.x tokens.

### Update service audit configurations.

 - [PUT /audit-log/v2beta1/configs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-config/audit-trail-configurations/updateauditconfigs.md): This API accepts valid 1.x tokens.

### Delete external service offer audit configurations.

 - [DELETE /audit-log/v2beta1/configs](https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-config/audit-trail-configurations/deleteauditconfigs.md): This API accepts valid 1.x tokens.

