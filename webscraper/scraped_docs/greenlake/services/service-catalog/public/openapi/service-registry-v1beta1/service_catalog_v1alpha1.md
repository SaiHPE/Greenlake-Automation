---
title: "Service Registry"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1.md"
scraped_at: "2026-06-07T06:13:39.820134+00:00Z"
---

# Service Registry

This Document outlines the API contracts for service-registry in HPE Common Cloud Services

Version: v1alpha1
License: HPE End User License Agreement

## Servers

```
http://localhost:5000
```

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

[Service Registry](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1.yaml)

## Service Catalog

CRUD operations for Service Offer

### Get Service Offers

 - [GET /service-catalog/v1alpha1/service-offers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offers/getserviceoffers.md): Get Service Offer list by filters applied

### Create Service Offer

 - [POST /service-catalog/v1alpha1/service-offers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offers/createserviceoffer.md): Intial step to onboard a service

### Get Service Offer

 - [GET /service-catalog/v1alpha1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offers/getserviceoffer.md): Fetch service offer details for a ID

### Update Service Offer

 - [PUT /service-catalog/v1alpha1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offers/updateserviceoffer.md): Update the Service offer details

### Partially Update Service Offer

 - [PATCH /service-catalog/v1alpha1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offers/patchserviceoffer.md): Partially update service offer details

### Delete Service Offer

 - [DELETE /service-catalog/v1alpha1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offers/deleteserviceoffer.md): Delete a specific service offer

### Mark Service Offer onboarding as complete

 - [POST /service-catalog/v1alpha1/service-offers/{id}/onboarded](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offers/onboardserviceoffer.md): Service Offer onboard completion declared by the app-team

### Publish Service Offer

 - [POST /service-catalog/v1alpha1/service-offers/{id}/publish](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offers/publishserviceoffer.md): Service Offer published to Service-Catalog by the GLP-admin or TAC-admin

### Hide Service Offer

 - [POST /service-catalog/v1alpha1/service-offers/{id}/hide](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offers/hideserviceoffer.md): Service Offer Hidden to Service-Catalog by the GLP-admin or TAC-admin

## Service Catalog

CRUD operations for Service Offer Regions

### Get Service Offer Regions

 - [GET /service-catalog/v1alpha1/service-offer-regions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offer-regions/getserviceofferregions.md): Get all service offer regions list by filters applied

### Create Service Offer Region

 - [POST /service-catalog/v1alpha1/service-offer-regions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offer-regions/createserviceofferregion.md): Intial step to onboard a service offer region

### Retrieve the service offer region details

 - [GET /service-catalog/v1alpha1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offer-regions/getserviceofferregion.md): Get Service Offer Region

### Update Service Offer Region

 - [PUT /service-catalog/v1alpha1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offer-regions/updateserviceofferregion.md): Update the Service offer Region details

### Partially Update Service Offer Region

 - [PATCH /service-catalog/v1alpha1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offer-regions/pathcserviceofferregion.md): Partially Update the Service offer Region details

### Delete Service Offer Region

 - [DELETE /service-catalog/v1alpha1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offer-regions/deleteserviceofferregion.md): Delete a specific service offer region

### Mark Service Offer Region onboarding as complete

 - [POST /service-catalog/v1alpha1/service-offer-regions/{id}/onboarded](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/service-offer-regions/onboardserviceofferregion.md): Service Offer Region onboard completion declared by the app-team

## Service Catalog

Get Unredacted Service Offers

### Get Unredacted Service Offers

 - [GET /service-catalog/v1alpha1/unredacted-service-offers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/unredacted-service-offers/getunredactedserviceoffers.md): Get Unredacted Service Offer list by filters applied

### Get Unredacted Service Offer

 - [GET /service-catalog/v1alpha1/unredacted-service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/unredacted-service-offers/getunredactedserviceoffer.md): Get Unredacted Service Offer

## Service Catalog

Get Unredacted Service Offer Regions

### Get Unredacted Service Offer Regions

 - [GET /service-catalog/v1alpha1/unredacted-service-offer-regions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/unredacted-service-offer-regions/getunredactedserviceofferregions.md): Get all service offer regions list by filters applied

### Get Unredacted Service Offer Region

 - [GET /service-catalog/v1alpha1/unredacted-service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/unredacted-service-offer-regions/getunredactedserviceofferregion.md): Get Service Offer Region

## UI Management

UI-triggered operations for service catalog

### Get Service Offers for Catalog

 - [GET /service-catalog/v1alpha1/service-catalog](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/ui-management/getservicecatalog.md): Get Service Offers for Catalog View

### Get Featured Service Offers

 - [GET /service-catalog/v1alpha1/featured-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/ui-management/getfeaturedservices.md): Get Featured Service Offers

### Get Service Offer Details

 - [GET /service-catalog/v1alpha1/detailed-service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/ui-management/getdetailedserviceoffer.md): Get Detailed Service Offer

### Get My Services

 - [GET /service-catalog/v1alpha1/my-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/ui-management/getmyservices.md): Get data to populate My Services

