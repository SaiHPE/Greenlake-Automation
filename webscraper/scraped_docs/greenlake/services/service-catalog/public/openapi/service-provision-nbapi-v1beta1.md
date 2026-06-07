---
title: "Service provision management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1.md"
scraped_at: "2026-06-07T05:46:37.064891+00:00Z"
---

# Service provision management

The API reference documentation for endpoints related to service provision management.

Version: v1beta1
License: HPE End User License Agreement

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### bearerAuth

Type: apiKey
In: header
Name: Authorization

## Download OpenAPI description

[Service provision management](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/index.yaml)

## Service Provision

### Get service provisions

 - [GET /service-catalog/v1beta1/service-provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service-provision/getserviceprovisions.md): Retrieve a list of service provisions by applying filters.
A service offer provides a distinct set of functionalities that can be independently identified and assigned access. Service offers are typically associated with roles and permissions, commerce, metering, quote-to-cash, and trial evaluations.
A service provision occurs when a service offer is provisioned (added) to a workspace.
Pagination: This endpoint supports cursor-based pagination using the next query parameter. Provide the cursor in the next query parameter to retrieve the next page.

### Create a service provision

 - [POST /service-catalog/v1beta1/service-provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service-provision/postserviceprovision.md): The initial step to provision a service offer in a region. A service offer provides a distinct set of functionalities that can be independently identified and assigned access. Service offers are typically associated with roles and permissions, commerce, metering, quote-to-cash, and trial evaluations.You need to supply the following in the request body. serviceOfferId-From Service offer management use the Get service offers endpoint to find service offer IDs.region-From Service offer management use the Get service offer regions endpoint to find region codes.

### Get service provision

 - [GET /service-catalog/v1beta1/service-provisions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service-provision/getserviceprovision.md): Fetch service provision details for an ID.

### Delete a service provision

 - [DELETE /service-catalog/v1beta1/service-provisions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service-provision/deleteserviceprovision.md): Delete a specific service provision.

### Retrigger service provisioning

 - [POST /service-catalog/v1beta1/service-provisions/{id}/retry](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service-provision/retryserviceprovision.md): Retrigger service provisioning if it has failed.

### Retrigger service deletion

 - [POST /service-catalog/v1beta1/service-provisions/{id}/retry-unprovision](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service-provision/retryserviceunprovision.md): Retrigger service deletion in case it failed.

