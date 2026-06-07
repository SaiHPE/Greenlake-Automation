---
title: "PATCH /subscriptions/v1/auto-subscription-settings/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/auto-subscriptions-settings-v1/updateautosubscriptionsv1.md"
scraped_at: "2026-06-07T06:16:23.365790+00:00Z"
---

# Update the configured auto-subscriptions settings of a workspace

Update the configured auto-subscriptions managed in a workspace.  In the payload, you can pass a list of deviceType and tier combinations to be updated or created. If the combination of deviceType and tier is already configured, it is updated. Otherwise, the combination is created. If you need to remove settings for one or more combination of deviceType and tier, pass tier as null for the required deviceType. NOTE: You need to have the edit permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 25 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

Endpoint: PATCH /subscriptions/v1/auto-subscription-settings/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique identifier of the auto subscription settings.

## Request fields (application/merge-patch+json):

  - `autoSubscriptionSettings` (array)

  - `autoSubscriptionSettings.deviceType` (string, required)
    Enum: "AP", "SWITCH", "GATEWAY", "STORAGE", "DHCI_STORAGE", "COMPUTE", "DHCI_COMPUTE", "NW_THIRD_PARTY", "PCE", "SD_WAN_GW", "OPSRAMP_SAAS", "SD_SAAS", "SENSOR", "BRIDGES"

  - `autoSubscriptionSettings.tier` (string, required)
    Enum: "FOUNDATION_AP", "ADVANCED_AP", "FOUNDATION_SWITCH", "ADVANCED_SWITCH", "FOUNDATION_GW", "ADVANCED_GW", "STANDARD_COMPUTE", "FOUNDATION_NW_THIRD_PARTY", "ADVANCED_NW_THIRD_PARTY", "ENHANCED_COMPUTE", "FOUNDATION_SENSOR", "FOUNDATION_SD_WAN", "ADVANCED_SD_WAN"

## Response 200 fields (application/json):

  - `createdAt` (string, required)
    The time of auto-subscription creation.
    Example: "2024-02-07T11:20:35.290Z"

  - `id` (string, required)
    The unique identifier of the auto-subscription.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `resourceUri` (string, required)
    URI to the auto-subscription.

  - `updatedAt` (string, required)
    The time of last auto-subscription update.
    Example: "2024-02-07T11:22:35.800Z"

  - `type` (string, required)
    The type of the resource.
    Example: "subscriptions/auto-subscription-settings"

  - `generation` (integer)
    Monotonically increasing update counter.

  - `autoSubscriptionSettings` (array)

  - `autoSubscriptionSettings.deviceType` (string, required)
    Enum: "AP", "SWITCH", "GATEWAY", "STORAGE", "DHCI_STORAGE", "COMPUTE", "DHCI_COMPUTE", "NW_THIRD_PARTY", "PCE", "SD_WAN_GW", "OPSRAMP_SAAS", "SD_SAAS", "SENSOR", "BRIDGES", "BRIDGE"

  - `autoSubscriptionSettings.tier` (string, required)
    Enum: "FOUNDATION_AP", "ADVANCED_AP", "FOUNDATION_SWITCH", "ADVANCED_SWITCH", "FOUNDATION_GW", "ADVANCED_GW", "STANDARD_COMPUTE", "FOUNDATION_NW_THIRD_PARTY", "ADVANCED_NW_THIRD_PARTY", "ENHANCED_COMPUTE", "FOUNDATION_SENSOR", "FOUNDATION_SD_WAN", "ADVANCED_SD_WAN"

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


