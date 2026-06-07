---
title: "Service Offer Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi.md"
scraped_at: "2026-06-07T05:46:46.606623+00:00Z"
---

# Service Offer Management

This Document outlines the API contracts for service-registry in HPE Common Cloud Services

Version: v1beta1
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

Type: apiKey
In: header
Name: Authorization

## Download OpenAPI description

[Service Offer Management](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi.yaml)

## Service Catalog

CRUD operations for Service Offer

### Get Service Offers

 - [GET /service-catalog/v1beta1/service-offers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/service-offers/getserviceoffers.md): Get Service Offer list by filters applied

### Get Service Offer

 - [GET /service-catalog/v1beta1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/service-offers/getserviceoffer.md): Fetch service offer details for a ID

## Media

### Get All media for service offer

 - [GET /service-catalog/v1beta1/service-offers/{id}/media](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/media/paths/~1service-catalog~1v1beta1~1service-offers~1%7Bid%7D~1media/get.md)

### Get Single media for service offer

 - [GET /service-catalog/v1beta1/service-offers/{id}/media/{media-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/media/paths/~1service-catalog~1v1beta1~1service-offers~1%7Bid%7D~1media~1%7Bmedia-id%7D/get.md)

### Get overall media

 - [GET /service-catalog/v1beta1/media](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/media/paths/~1service-catalog~1v1beta1~1media/get.md)

## Service Offer Regions

### Get Service Offer Regions

 - [GET /service-catalog/v1beta1/service-offer-regions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/service-offer-regions/getserviceofferregions.md): Get all service offer regions list by filters applied

### Retrieve the service offer region details

 - [GET /service-catalog/v1beta1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/service-offer-regions/getserviceofferregion.md): Get Service Offer Region

## UI Management

### Get Featured Service Offers

 - [GET /service-catalog/v1beta1/featured-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/ui-management/getfeaturedservices.md): Get Featured Service Offers

### Get Service Offers for Catalog

 - [GET /service-catalog/v1beta1/service-catalog](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/ui-management/getservicecatalog.md): Get Service Offers for Catalog View

### Get Service Offer Details

 - [GET /service-catalog/v1beta1/detailed-service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/ui-management/getdetailedserviceoffer.md): Get Detailed Service Offer

### Get My Services

 - [GET /service-catalog/v1beta1/my-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/ui-management/getmyservices.md): Get data to populate My Services

### Get Recent Services

 - [GET /service-catalog/v1beta1/recent-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/ui-management/getrecentservices.md): Get data to populate Recent Services

## Cache Retrieve

### API to retrieve cache using keys/pattern

 - [POST /service-catalog/v1beta1/cache/retrieve](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/cache-retrieve/cacheretrieve.md): API to retrieve cache with specific keys and pattern

