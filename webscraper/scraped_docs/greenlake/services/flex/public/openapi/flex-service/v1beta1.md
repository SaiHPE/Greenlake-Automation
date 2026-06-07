---
title: "HPE Flex Solutions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1.md"
scraped_at: "2026-06-07T05:46:45.560045+00:00Z"
---

# HPE Flex Solutions

This is the API reference document for the HPE Flex Solutions data service.
It provides endpoints to view and manage Flex device and orders solutions.


Version: v1beta1
License: HPE License

## Servers

```
https://us-west.api.greenlake.hpe.com
```

## Security

### Bearer

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE Flex Solutions](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1/index.yaml)

## Order Data

### Get and search for orders

 - [GET /flex/v1beta1/orders](https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1/order-data/getorders.md): This endpoint allows you to retrieve and search for orders.
You can filter, sort, and paginate the results.

Pagination: This endpoint supports offset-based pagination using limit and offset parameters.

### Get distinct transformative data for orders

 - [GET /flex/v1beta1/orders/transform](https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1/order-data/getorderstransform.md): This endpoint allows distinct transformative queries for orders.

A transform query applies a logical function to a resource set, such as aggregating by a element.

Pagination: This endpoint supports offset-based pagination using limit and offset parameters.

## Device Data

### Get and search for Device

 - [GET /flex/v1beta1/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1/device-data/getdevices.md): This endpoint allows you to retrieve and search for devices.
You can filter, sort, and paginate the results.

Pagination: This endpoint supports offset-based pagination using limit and offset parameters.

### Get a single device by device resource ID

 - [GET /flex/v1beta1/devices/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1/device-data/getdevice.md): This endpoint allows you to retrieve a device by device resourceID.

