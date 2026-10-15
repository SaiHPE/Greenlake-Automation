---
title: "GET /flex/v1beta1/orders/transform"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1/order-data/getorderstransform.md"
scraped_at: "2026-06-07T06:16:40.891221+00:00Z"
---

# Get distinct transformative data for orders

This endpoint allows distinct transformative queries for orders.

A transform query applies a logical function to a resource set, such as aggregating by a element.

Pagination: This endpoint supports offset-based pagination using limit and offset parameters.

Endpoint: GET /flex/v1beta1/orders/transform
Version: v1beta1
Security: Bearer

## Query parameters:

  - `group-by` (string, required)
    Field to be grouped by. Will return unique results of that type.

Supported fields are:
  * sowId
  * customerName
  * billingAccountName
  * billingAccountId
  * partnerName

(partnerName is a unique combined set of resellerName and distributorName)
    Example: "partnerName"

  - `filter` (string)
    Filter expressions consisting of simple comparison operations joined by logical operators.

For the v1beta1 API, the following fields are supported for filtering under the ODATA specification:
  * billingAccountId
  * sowId
  * billingAccountName
  * customerName
  * resellerName
  * distributorName
  * partnerName

  - `sort` (string)
    Fields to be sorted by in the response.
The default sorting order is by the group-by field in ascending order.
The sort field must be one of the group-by fields, if given.
    Example: "partnerName desc"

  - `offset` (integer)
    Zero-based resource offset to start the response from.
    Example: 10

  - `limit` (integer)
    Number of entities to return with a maximum of 100.
    Example: 30

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.sowId` (string)
    The unique SOW ID.
    Example: "OPE-123456789"

  - `items.billingAccountId` (string)
    Unique billing account ID
    Example: "HP-123456789"

  - `items.billingAccountName` (string)
    Unique billing account name
    Example: "Hewlett Packard Enterprise Cloud Storage"

  - `items.customerName` (string)
    Unique customer name
    Example: "Some Company Inc."

  - `items.partnerName` (string)
    Unique partner name
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


