---
title: "GET /subscriptions/v1/auto-subscription-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi/auto-subscriptions-settings-v1/getautosubscriptionsv1.md"
scraped_at: "2026-06-07T06:16:24.834821+00:00Z"
---

# Get all configured auto-subscriptions settings

Get all configured auto-subscriptions settings in a workspace.  NOTE: You need to have the view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 25 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

Endpoint: GET /subscriptions/v1/auto-subscription-settings
Version: latest
Security: Bearer

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned.
    Example: 10

  - `items` (array, required)

  - `items.createdAt` (string, required)
    Time of auto-subscription creation.
    Example: "2024-02-07T11:20:35.290Z"

  - `items.id` (string, required)
    The unique identifier of the tenant.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `items.resourceUri` (string, required)
    URI to the auto-subscription.

  - `items.updatedAt` (string, required)
    Time of last auto-subscription update.
    Example: "2024-02-07T11:22:35.800Z"

  - `items.type` (string, required)
    Type of the resource
    Example: "subscriptions/auto-subscription-settings."

  - `items.generation` (integer)
    Monotonically increasing update counter.

  - `items.autoSubscriptionSettings` (array)

  - `items.autoSubscriptionSettings.deviceType` (string, required)
    Enum: "AP", "SWITCH", "GATEWAY", "STORAGE", "DHCI_STORAGE", "COMPUTE", "DHCI_COMPUTE", "NW_THIRD_PARTY", "PCE", "SD_WAN_GW", "OPSRAMP_SAAS", "SD_SAAS", "SENSOR", "BRIDGES", "BRIDGE"

  - `items.autoSubscriptionSettings.tier` (string, required)
    Enum: "FOUNDATION_AP", "ADVANCED_AP", "FOUNDATION_SWITCH", "ADVANCED_SWITCH", "FOUNDATION_GW", "ADVANCED_GW", "STANDARD_COMPUTE", "FOUNDATION_NW_THIRD_PARTY", "ADVANCED_NW_THIRD_PARTY", "ENHANCED_COMPUTE", "FOUNDATION_SENSOR", "FOUNDATION_SD_WAN", "ADVANCED_SD_WAN"

  - `items.tenantWorkspaceId` (string)
    The unique identifier of a tenant workspace.

  - `offset` (integer)
    Zero-based resource offset.

  - `total` (integer)
    Total number of items in the collection that match the filter query, if one was provided in the request otherwise total number of items for a given resource.
    Example: 50

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

  - `errorDetails.issues.source` (string)
    The source of the error.

  - `errorDetails.issues.subject` (string)
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


