---
title: "Service Registry"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1.md"
scraped_at: "2026-06-07T05:46:38.060610+00:00Z"
---

# Service Registry

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

[Service Registry](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1.yaml)

## Service Catalog

CRUD operations for Service Offer

### Get Service Offers

 - [GET /service-catalog/v1beta1/service-offers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1/service-offers/getserviceoffers.md): Get Service Offer list by filters applied

### Get Service Offer

 - [GET /service-catalog/v1beta1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1/service-offers/getserviceoffer.md): Fetch service offer details for a ID

## Service Offer Regions

### Get Service Offer Regions

 - [GET /service-catalog/v1beta1/service-offer-regions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1/service-offer-regions/getserviceofferregions.md): Get all service offer regions list by filters applied

### Retrieve the service offer region details

 - [GET /service-catalog/v1beta1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1/service-offer-regions/getserviceofferregion.md): Get Service Offer Region

## UI Management

### Get Featured Service Offers

 - [GET /service-catalog/v1beta1/featured-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1/ui-management/getfeaturedservices.md): Get Featured Service Offers

### Get Service Offers for Catalog

 - [GET /service-catalog/v1beta1/service-catalog](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1/ui-management/getservicecatalog.md): Get Service Offers for Catalog View

### Get Service Offer Details

 - [GET /service-catalog/v1beta1/detailed-service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1/ui-management/getdetailedserviceoffer.md): Get Detailed Service Offer

### Get My Services

 - [GET /service-catalog/v1beta1/my-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1/ui-management/getmyservices.md): Get data to populate My Services

### Get Recent Services

 - [GET /service-catalog/v1beta1/recent-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1/ui-management/getrecentservices.md): Get data to populate Recent Services

