---
title: "Service Manager Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1.md"
scraped_at: "2026-06-07T05:46:35.344283+00:00Z"
---

# Service Manager Management

The HPE GreenLake for Service Catalog service offers a collection of RESTful APIs to fetch, provision service managers and to delete a service manager provisioned in a workspace.

Version: v1beta1
License: HPE End User License Agreement

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### bearerAuth

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Service Manager Management](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/@v1beta1/index.yaml)

## Service Manager

APIs to get service managers for the user's workspace.

### Get service managers (deprecated)

 - [GET /service-catalog/v1beta1/service-managers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager/get_service_managers.md): Get a list of available service managers.

### Get a specific service manager (deprecated)

 - [GET /service-catalog/v1beta1/service-managers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager/get_service_manager.md): Retrieve details for a specific service manager by passing the service manager ID.

### Get service managers by region (deprecated)

 - [GET /service-catalog/v1beta1/per-region-service-managers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager/per_region_service_managers.md): Retrieve a list of available service managers categorized by region.

### Get service managers deployed in a specific region. (deprecated)

 - [GET /service-catalog/v1beta1/per-region-service-managers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager/service_managers_for_a_region.md): Retrieve a list of service managers deployed to a particular region.

## Service Manager Provision

APIs to provision, un-provision and get the service manager provisioned.

### Provision a service manager in a given region (deprecated)

 - [POST /service-catalog/v1beta1/service-manager-provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager-provision/create_service_manager_provision.md): Provision a service manager deployed in a region. Provisioning of a service manager is an async process and you can monitor the  provisionStatus field to know the current status.

### Get service manager provisions (deprecated)

 - [GET /service-catalog/v1beta1/service-manager-provisions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager-provision/get_service_manager_provisions.md): Retrieve a list of all service manager provision entries.

### Get a specific service manager provision entry (deprecated)

 - [GET /service-catalog/v1beta1/service-manager-provisions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager-provision/get_service_manager_provision.md): Retrieve details for a specific service manager provision entry using the ID for the entry.

### Delete a service manager provision entry (deprecated)

 - [DELETE /service-catalog/v1beta1/service-manager-provisions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager-provision/delete_service_manager_provision.md): Delete a service manager provision entry.

