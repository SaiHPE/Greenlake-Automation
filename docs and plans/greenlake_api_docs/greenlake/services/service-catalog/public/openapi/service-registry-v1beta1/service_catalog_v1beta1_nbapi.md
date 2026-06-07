---
title: "Service offer management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi.md"
scraped_at: "2026-06-07T05:46:38.109423+00:00Z"
---

# Service offer management

The API reference documentation for endpoints related to service offer management.

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

[Service offer management](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi.yaml)

## Service offers

### Get service offers

 - [GET /service-catalog/v1beta1/service-offers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/service-offers/getserviceoffers.md): Retrieve a list of service offers by applying filters. 
A service offer provides a distinct set of functionality that can be independently identified and assigned access.
Pagination: This API supports cursor-based pagination. Provide the cursor in the next query parameter to retrieve the next page.

### Get a service offer

 - [GET /service-catalog/v1beta1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/service-offers/getserviceoffer.md): Retrieve detailed information about a specific service offer by supplying its unique identifier in the request path.
To obtain valid service offer IDs, use the Get service offers endpoint to list available offers.

## Service offer regions

### Get service offer regions

 - [GET /service-catalog/v1beta1/service-offer-regions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/service-offer-regions/getserviceofferregions.md): Retrieve a list of service offer regions by applying filters.
Each service offer region represents a service offer provisioned in a specific region.
Pagination: This API supports cursor-based pagination. Provide the cursor in the next query parameter to retrieve the next page.

### Get service offer region

 - [GET /service-catalog/v1beta1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/service-offer-regions/getserviceofferregion.md): Retrieve detailed information about a specific service offer region by providing its unique identifier in the request path.
To obtain valid service offer region IDs, use the Get service offer regions endpoint to list available regions.

## UI Management

### Get Service Offers for Catalog

 - [GET /service-catalog/v1beta1/service-catalog](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/ui-management/getservicecatalog.md): Get Service Offers for Catalog View

### Get Featured Service Offers

 - [GET /service-catalog/v1beta1/featured-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/ui-management/getfeaturedservices.md): Get Featured Service Offers

### Get Service Offer Details

 - [GET /service-catalog/v1beta1/detailed-service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/ui-management/getdetailedserviceoffer.md): Get Detailed Service Offer

### Get My Services

 - [GET /service-catalog/v1beta1/my-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/ui-management/getmyservices.md): Get data to populate My Services

### Get Recent Services

 - [GET /service-catalog/v1beta1/recent-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/ui-management/getrecentservices.md): Get data to populate Recent Services

### Get Recent Services

 - [GET /service-catalog/v1beta2/recent-services](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/ui-management/getrecentservicesv2.md): Get data to populate Recent Services V2

