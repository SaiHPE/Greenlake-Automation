---
title: "Service Provision Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api.md"
scraped_at: "2026-06-07T06:13:39.100885+00:00Z"
---

# Service Provision Management

This Document outlines the API contracts for service-provision in HPE Common Cloud Services

Version: v1beta1
License: HPE End User License Agreement

## Servers

```
http://service-provision-svc.ccs-system.svc.cluster.local
```

## Download OpenAPI description

[Service Provision Management](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api.yaml)

## Service Provisions

### Get Service Provisions

 - [GET /service-catalog/v1beta1/service-provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api/service-provisions/getserviceprovisions.md): Get Service Provision list by filters applied

### Create Service Provision

 - [POST /service-catalog/v1beta1/service-provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api/service-provisions/postserviceprovision.md): Initial step to provision a service-offer in a region

### Get Service Provision

 - [GET /service-catalog/v1beta1/service-provisions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api/service-provisions/getserviceprovision.md): Fetch service provision details for an ID

### Unprovision and delete Service Provision entry

 - [DELETE /service-catalog/v1beta1/service-provisions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api/service-provisions/deleteserviceprovision.md): Unprovision and delete a specific service provision

### Retrigger Service provisioning in case it failed previously

 - [POST /service-catalog/v1beta1/service-provisions/{id}/retry](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api/service-provisions/retryserviceprovision.md): Retrigger Service provisioning in case it failed previously

### Retrigger Service Unprovisioning in case it failed previously

 - [POST /service-catalog/v1beta1/service-provisions/{id}/retry-unprovision](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api/service-provisions/retryserviceunprovision.md): Retrigger Service Unprovisioning in case it failed previously

### Retry Workspace Transfer

 - [POST /service-catalog/v1beta1/service-provisions/{id}/retry-workspace-transfer](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api/service-provisions/retryworkspacetransfer.md): Retry the workspace transfer for a given service provision ID

## Notifications

### Receive a Notification from an internal service conveying the response for a Service Provision request

 - [POST /service-catalog/v1beta1/notifications/provision-response](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api/notifications/postserviceprovisionresponse.md): Receive a Notification from an internal service conveying the response for a Service Provision request

