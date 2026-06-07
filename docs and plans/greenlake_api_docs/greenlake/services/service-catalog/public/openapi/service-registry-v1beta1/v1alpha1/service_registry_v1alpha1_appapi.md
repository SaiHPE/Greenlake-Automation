---
title: "Service Offer Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi.md"
scraped_at: "2026-06-07T05:46:45.717753+00:00Z"
---

# Service Offer Management

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

[Service Offer Management](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi.yaml)

## Media

### Upload logo/screenshot

 - [POST /service-catalog/v1alpha1/service-offers/{id}/media](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/media/paths/~1service-catalog~1v1alpha1~1service-offers~1%7Bid%7D~1media/post.md)

### Get All media for service offer

 - [GET /service-catalog/v1alpha1/service-offers/{id}/media](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/media/paths/~1service-catalog~1v1alpha1~1service-offers~1%7Bid%7D~1media/get.md)

### Get Single media for service offer

 - [GET /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/media/paths/~1service-catalog~1v1alpha1~1service-offers~1%7Bid%7D~1media~1%7Bmedia-id%7D/get.md)

### Update media for service offer

 - [PUT /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/media/paths/~1service-catalog~1v1alpha1~1service-offers~1%7Bid%7D~1media~1%7Bmedia-id%7D/put.md)

### Partially update media for service offer

 - [PATCH /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/media/paths/~1service-catalog~1v1alpha1~1service-offers~1%7Bid%7D~1media~1%7Bmedia-id%7D/patch.md)

### Delete media for service offer

 - [DELETE /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/media/paths/~1service-catalog~1v1alpha1~1service-offers~1%7Bid%7D~1media~1%7Bmedia-id%7D/delete.md)

### Mark file upload status as UPLOADED

 - [POST /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}/uploaded](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/media/paths/~1service-catalog~1v1alpha1~1service-offers~1%7Bid%7D~1media~1%7Bmedia-id%7D~1uploaded/post.md)

### Get overall media

 - [GET /service-catalog/v1alpha1/media](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/media/paths/~1service-catalog~1v1alpha1~1media/get.md)

## Service Offers

### Get Service Offers

 - [GET /service-catalog/v1alpha1/service-offers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offers/getserviceoffers.md): Get Service Offer list by filters applied

### Create Service Offer

 - [POST /service-catalog/v1alpha1/service-offers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offers/createserviceoffer.md): Intial step to onboard a service

### Get Service Offer

 - [GET /service-catalog/v1alpha1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offers/getserviceoffer.md): Fetch service offer details for a ID

### Update Service Offer

 - [PUT /service-catalog/v1alpha1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offers/updateserviceoffer.md): Update the Service offer details

### Partially Update Service Offer

 - [PATCH /service-catalog/v1alpha1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offers/patchserviceoffer.md): Partially update service offer details

### Delete Service Offer

 - [DELETE /service-catalog/v1alpha1/service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offers/deleteserviceoffer.md): Delete a specific service offer

### Mark Service Offer onboarding as complete

 - [POST /service-catalog/v1alpha1/service-offers/{id}/onboarded](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offers/onboardserviceoffer.md): Service Offer onboard completion declared by the app-team

## Unredacted Service Offers

### Get Unredacted Service Offers

 - [GET /service-catalog/v1alpha1/unredacted-service-offers](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/unredacted-service-offers/getunredactedserviceoffers.md): Get Unredacted Service Offer list by filters applied

### Get Unredacted Service Offer

 - [GET /service-catalog/v1alpha1/unredacted-service-offers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/unredacted-service-offers/getunredactedserviceoffer.md): Get Unredacted Service Offer

## Service Offer Regions

### Get Service Offer Regions

 - [GET /service-catalog/v1alpha1/service-offer-regions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offer-regions/getserviceofferregions.md): Get all service offer regions list by filters applied

### Create Service Offer Region

 - [POST /service-catalog/v1alpha1/service-offer-regions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offer-regions/createserviceofferregion.md): Intial step to onboard a service offer region

### Retrieve the service offer region details

 - [GET /service-catalog/v1alpha1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offer-regions/getserviceofferregion.md): Get Service Offer Region

### Update Service Offer Region

 - [PUT /service-catalog/v1alpha1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offer-regions/updateserviceofferregion.md): Update the Service offer Region details

### Partially Update Service Offer Region

 - [PATCH /service-catalog/v1alpha1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offer-regions/pathcserviceofferregion.md): Partially Update the Service offer Region details

### Delete Service Offer Region

 - [DELETE /service-catalog/v1alpha1/service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offer-regions/deleteserviceofferregion.md): Delete a specific service offer region

### Mark Service Offer Region onboarding as complete

 - [POST /service-catalog/v1alpha1/service-offer-regions/{id}/onboarded](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/service-offer-regions/onboardserviceofferregion.md): Service Offer Region onboard completion declared by the app-team

## Unredacted Service Offer Regions

### Get Unredacted Service Offer Regions

 - [GET /service-catalog/v1alpha1/unredacted-service-offer-regions](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/unredacted-service-offer-regions/getunredactedserviceofferregions.md): Get all service offer regions list by filters applied

### Get Unredacted Service Offer Region

 - [GET /service-catalog/v1alpha1/unredacted-service-offer-regions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_appapi/unredacted-service-offer-regions/getunredactedserviceofferregion.md): Get Service Offer Region

