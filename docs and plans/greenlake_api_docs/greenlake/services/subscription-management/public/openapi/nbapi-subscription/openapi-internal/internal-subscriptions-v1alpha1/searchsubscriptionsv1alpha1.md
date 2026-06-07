---
title: "POST /internal-subscriptions/v1alpha1/subscriptions/search"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/internal-subscriptions-v1alpha1/searchsubscriptionsv1alpha1.md"
scraped_at: "2026-06-07T06:15:53.237319+00:00Z"
---

# Search Subscriptions

Search for subscriptions based on the provided criteria and returns a paginated list.

Endpoint: POST /internal-subscriptions/v1alpha1/subscriptions/search
Version: latest
Security: Bearer

## Header parameters:

  - `CCS-Platform-Customer-Id` (string, required)
    The platform customer ID.

  - `CCS-Transaction-Id` (string, required)
    A unique identifier for the transaction, used for tracing.

## Query parameters:

  - `limit` (integer)
    Specifies the number of results to be returned. The default value is 10.

  - `offset` (integer)
    Specifies the offset.

  - `next` (string)
    Specifies the information needed to retrieve the next page of results.

## Request fields (application/json):

  - `searchText` (string)
    The search query string.

## Response 200 fields (application/json):

  - `pagination` (object)

  - `pagination.totalCount` (integer)
    The total number of subscriptions matching the search criteria.

  - `pagination.offset` (integer)
    The offset of the current page of results.

  - `pagination.countPerPage` (integer)
    The maximum number of items per page.

  - `pagination.next` (string)
    Token for retrieving the next page of results.

  - `items` (array)

  - `items.index` (string)
    Name of the search index containing the document.

  - `items.id` (string)
    Unique identifier of the search hit.

  - `items.score` (number)
    Score from the search engine.

  - `items.routing` (string)
    Shard routing key used to direct the query to the correct partition.

  - `items.source` (object)

  - `items.source.id` (string)
    Resource ID of the device.

  - `items.source.serialNumber` (string)
    Serial number of the device.

  - `items.source.macAddress` (string)
    Mac address of the device.

  - `items.source.deviceType` (string)
    The type of the device.

  - `items.source.model` (string)
    Model of the device.

  - `items.source.tags` (object)
    Tags assigned to the device.

  - `items.source.name` (string)
    Name of the device.

  - `items.source.secondaryName` (string)
    Secondary name of the device.

  - `items.highlight` (object)

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

  - `errorDetail` (array)

  - `errorDetail.type` (string, required)
    The type of error details.

  - `errorDetail.issues` (array, required)
    An array of bad request issues.

  - `errorDetail.issues.source` (string)
    The source of the error.

  - `errorDetail.issues.subject` (string)
    The specific issue key.

  - `errorDetail.issues.description` (string)
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
    Additional key value pairs.

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
    Additional key value pairs.

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
    Additional key value pairs.

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


