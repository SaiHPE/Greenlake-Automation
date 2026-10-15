---
title: "GET /flex/v1beta1/devices/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1/device-data/getdevice.md"
scraped_at: "2026-06-07T06:16:40.976125+00:00Z"
---

# Get a single device by device resource ID

This endpoint allows you to retrieve a device by device resourceID.

Endpoint: GET /flex/v1beta1/devices/{id}
Version: v1beta1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique identifier (UUID) of the device resource.

## Response 200 fields (application/json):

  - `id` (string, required)
    ID of the Device
    Example: "3b741a59-a22b-432f-b2cf-b72cc1a04c2d"

  - `macAddress` (string, required)
    MAC address of the device
    Example: "CA:35:DC:4F:5D:FE"

  - `serialNumber` (string, required)
    Serial number of the device
    Example: "CN134FD36"

  - `resourceId` (string, required)
    Unique resource ID of the device
    Example: "3b741a59-a22b-432f-b2cf-b72cc1a04c2d"

  - `partNumber` (string, required)
    Part number of the device
    Example: "JK130GT"

  - `deviceType` (string, required)
    The type of the device.
    Enum: "ALS", "AP", "BLE", "COMPUTE", "CONTROLLER", "DHCI_COMPUTE", "DHCI_STORAGE", "EINAR", "EINR", "GATEWAY", "IAP", "LTE_MODEM", "MC", "STORAGE", "SWITCH", "NW_THIRD_PARTY", "PCE", "SD_WAN_GW", "OPSRAMP_SAAS", "SD_SAAS", "SENSOR", "BRIDGES", "UNKNOWN"

  - `type` (string, required)
    type of resource
    Example: "flex/devices"

  - `createdAt` (string, required)
    Date of creation of the resource
    Example: "2023-01-01T00:00:00Z"

  - `updatedAt` (string, required)
    Date of last update of the resource
    Example: "2023-01-01T00:00:00Z"

  - `generation` (integer, required)
    Monotonically increasing update counter of the resource
    Example: 1

  - `model` (string, required)
    The model of the device.
    Example: "HPE Compute 6030X"

  - `make` (string, required)
    The maker of the device
    Example: "HPE"

  - `tags` (array)
    The tags associated with the device.

  - `tags.name` (string, required)
    Name of the tag
    Example: "category1"

  - `tags.value` (string, required)
    Value of the tag
    Example: "value1"

  - `name` (string)
    Name of the device
    Example: "custom-device-name"

  - `billingAccountName` (string)
    Name of the associated billing account
    Example: "Hewlett Packard Enterprises"

  - `billingTier` (string)
    Name of the associated distributor account
    Example: "HPE Distributions"

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


