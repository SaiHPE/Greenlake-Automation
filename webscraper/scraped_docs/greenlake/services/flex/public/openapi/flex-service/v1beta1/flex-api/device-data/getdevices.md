---
title: "GET /flex/v1beta1/devices"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1/flex-api/device-data/getdevices.md"
scraped_at: "2026-06-07T06:16:41.703381+00:00Z"
---

# Get and search for Device

This endpoint allows you to retrieve and search for devices.
You can filter, sort, and paginate the results.

Pagination: This endpoint supports offset-based pagination using limit and offset parameters.

Endpoint: GET /flex/v1beta1/devices
Version: v1beta1
Security: Bearer

## Query parameters:

  - `filter` (string)
    Filter expressions consisting of simple comparison operations joined by logical operators.

For the v1beta1 API, the following fields are supported for filtering under the ODATA specification:
  * id
  * macAddress
  * serialNumber
  * resourceId
  * partNumber
  * name
  * type
  * model
  * make
  * billingAccountName
  * billingTier

  - `select` (string)
    Comma separated list of fields to be returned in the response.
If not provided, all fields will be returned.

All fields are supported.
    Example: "serialNumber,type,make,orderEndDate,billingTier"

  - `sort` (string)
    Comma separated list of fields to be sorted by in the response.
The default sorting order is by resourceId in ascending order.
    Example: "resourceId,model asc"

  - `offset` (integer)
    Zero-based resource offset to start the response from.
    Example: 10

  - `limit` (integer)
    Number of entities to return with a maximum of 100.
    Example: 30

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    ID of the Device
    Example: "3b741a59-a22b-432f-b2cf-b72cc1a04c2d"

  - `items.macAddress` (string, required)
    MAC address of the device
    Example: "CA:35:DC:4F:5D:FE"

  - `items.serialNumber` (string, required)
    Serial number of the device
    Example: "CN134FD36"

  - `items.resourceId` (string, required)
    Unique resource ID of the device
    Example: "3b741a59-a22b-432f-b2cf-b72cc1a04c2d"

  - `items.partNumber` (string, required)
    Part number of the device
    Example: "JK130GT"

  - `items.deviceType` (string, required)
    The type of the device.
    Enum: "ALS", "AP", "BLE", "COMPUTE", "CONTROLLER", "DHCI_COMPUTE", "DHCI_STORAGE", "EINAR", "EINR", "GATEWAY", "IAP", "LTE_MODEM", "MC", "STORAGE", "SWITCH", "NW_THIRD_PARTY", "PCE", "SD_WAN_GW", "OPSRAMP_SAAS", "SD_SAAS", "SENSOR", "BRIDGES", "UNKNOWN"

  - `items.type` (string, required)
    type of resource
    Example: "flex/devices"

  - `items.createdAt` (string, required)
    Date of creation of the resource
    Example: "2023-01-01T00:00:00Z"

  - `items.updatedAt` (string, required)
    Date of last update of the resource
    Example: "2023-01-01T00:00:00Z"

  - `items.generation` (integer, required)
    Monotonically increasing update counter of the resource
    Example: 1

  - `items.model` (string, required)
    The model of the device.
    Example: "HPE Compute 6030X"

  - `items.make` (string, required)
    The maker of the device
    Example: "HPE"

  - `items.tags` (array)
    The tags associated with the device.

  - `items.tags.name` (string, required)
    Name of the tag
    Example: "category1"

  - `items.tags.value` (string, required)
    Value of the tag
    Example: "value1"

  - `items.name` (string)
    Name of the device
    Example: "custom-device-name"

  - `items.billingAccountName` (string)
    Name of the associated billing account
    Example: "Hewlett Packard Enterprises"

  - `items.billingTier` (string)
    Name of the associated distributor account
    Example: "HPE Distributions"

  - `count` (integer, required)

  - `total` (integer, required)

  - `offset` (integer, required)

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.issues` (array, required)
    An array of bad request issues.

  - `errorDetails.issues.source` (string, required)
    The source of the error.

  - `errorDetails.issues.subject` (string, required)
    The specific issue key.

  - `errorDetails.issues.description` (string)
    A brief explanation of the error.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key pairs.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key pairs.

## Response 422 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key pairs.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key pairs.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.retryAfterSeconds` (integer, required)


