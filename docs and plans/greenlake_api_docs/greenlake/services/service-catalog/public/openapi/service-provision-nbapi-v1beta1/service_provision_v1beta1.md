---
title: "Service Provision"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1.md"
scraped_at: "2026-06-07T05:46:36.196329+00:00Z"
---

# Service Provision

This Document outlines the API contracts for service-provision in HPE Common Cloud Services

Version: v1beta1
License: HPE End User License Agreement

## Servers

```
https://polaris-default-user-api.ccs.arubathena.com
```

```
https://hoku-default-user-api.ccs.arubathena.com
```

## Security

### bearerAuth

Type: apiKey
In: header
Name: Authorization

## Download OpenAPI description

[Service Provision](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1.yaml)

## Service Provisions

CRUD operations for Service Provision

### Get Service Provisions

 - [GET /service-catalog/v1beta1/service-provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1/service-provisions/getserviceprovisions.md): Get Service Provision list by filters applied

### Create Service Provision

 - [POST /service-catalog/v1beta1/service-provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1/service-provisions/postserviceprovision.md): Initial step to provision a service-offer in a region

### Get Service Provision

 - [GET /service-catalog/v1beta1/service-provisions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1/service-provisions/getserviceprovision.md): Fetch service provision details for an ID

### Unprovision and delete Service Provision entry

 - [DELETE /service-catalog/v1beta1/service-provisions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1/service-provisions/deleteserviceprovision.md): Unprovision and delete a specific service provision

### Retrigger Service provisioning in case it failed previously

 - [POST /service-catalog/v1beta1/service-provisions/{id}/retry](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1/service-provisions/retryserviceprovision.md): Retrigger Service provisioning in case it failed previously

### Retrigger Service Unprovisioning in case it failed previously

 - [POST /service-catalog/v1beta1/service-provisions/{id}/retry-unprovision](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1/service-provisions/retryserviceunprovision.md): Retrigger Service Unprovisioning in case it failed previously

### Retry Workspace Transfer

 - [POST /service-catalog/v1beta1/service-provisions/{id}/retry-workspace-transfer](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1/service-provisions/retryworkspacetransfer.md): Retry the workspace transfer for a given service provision ID

