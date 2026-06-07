---
title: "Service Registry"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta2/service_registry_v1beta2_nbapi.md"
scraped_at: "2026-06-07T06:13:43.805258+00:00Z"
---

# Service Registry

This Document outlines the API contracts for service-registry in HPE Common Cloud Services

Version: v1beta2
License: HPE End User License Agreement

## Servers

```
https://localhost:5000
```

```
https://polaris-default-user-api.ccs.arubathena.com
```

```
https://hoku-default-user-api.ccs.arubathena.com
```

## Security

### bearerAuth

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Service Registry](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta2/service_registry_v1beta2_nbapi.yaml)

## Provisions

### Get workspace services with provisions

 - [GET /service-catalog/v1beta2/provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta2/service_registry_v1beta2_nbapi/provisions/getmyprovisions.md): Retrieves all services with their provisions for the authenticated user's workspace

## Org Provisions

### Get Organization Provisions

 - [GET /service-catalog/v1beta2/org-provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta2/service_registry_v1beta2_nbapi/org-provisions/getorgprovisions.md): Retrieve list of workspaces with their service offers and provisions at organization level. If parent workspace returns child workspaces with parent. For child workspaces returns only the child workspace.

