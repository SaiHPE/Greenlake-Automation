---
title: "External Events For Service Provision"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_external_events.md"
scraped_at: "2026-06-07T05:46:36.102850+00:00Z"
---

# External Events For Service Provision

Version: 1.0.0

## Download OpenAPI description

[External Events For Service Provision](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_external_events.yaml)

## Other

### Service offer provision event

 - [POST Service Offer Provision](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_external_events/webhooks/paths/service%20offer%20provision/post.md): A notification is sent when a service offer has been successfully provisioned in a region for a workspace.Event type—com.hpe.greenlake.service-provision.v1.serviceprovision.provisioned

### Service offer unprovision event

 - [POST Service Offer Unprovision](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_external_events/webhooks/paths/service%20offer%20unprovision/post.md): A notification is sent when a service offer provisioning has been removed from a region for a workspace.Event type—com.hpe.greenlake.service-provision.v1.serviceprovision.unprovision

### Service provision workspace transfer event

 - [POST Service Provision Workspace Transfer](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_external_events/webhooks/paths/service%20provision%20workspace%20transfer/post.md): We will not be raising this internal event. Services need to query the service provision to get the list of service provision entries for this workspace based on the WORKSPACE_TYPE_TRANSFER_INTERNAL event.Event type—com.hpe.greenlake.service-provision.v1.serviceprovision.workspace.transfer

