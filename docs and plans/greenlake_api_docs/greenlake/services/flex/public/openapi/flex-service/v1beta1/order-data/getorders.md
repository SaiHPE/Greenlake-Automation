---
title: "GET /flex/v1beta1/orders"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/flex-service/v1beta1/order-data/getorders.md"
scraped_at: "2026-06-07T06:16:40.793560+00:00Z"
---

# Get and search for orders

This endpoint allows you to retrieve and search for orders.
You can filter, sort, and paginate the results.

Pagination: This endpoint supports offset-based pagination using limit and offset parameters.

Endpoint: GET /flex/v1beta1/orders
Version: v1beta1
Security: Bearer

## Query parameters:

  - `filter` (string)
    Filter expressions consisting of simple comparison operations joined by logical operators.

For the v1beta1 API, the following fields are supported for filtering under the ODATA specification:
  * id
  * billingAccountId
  * sowId
  * billingAccountName
  * customerName
  * resellerName
  * partnerName
  * distributorName
  * isFlexPartner

  - `select` (string)
    Comma separated list of fields to be returned in the response.
If not provided, all fields will be returned.

All fields are supported.
    Example: "resellerName,billingAccountName,orderEndDate"

  - `sort` (string)
    Comma separated list of fields to be sorted by in the response.
The default sorting order is by orderEndDate in ascending order.
    Example: "orderEndDate asc"

  - `offset` (integer)
    Zero-based resource offset to start the response from.
    Example: 10

  - `limit` (integer)
    Number of entities to return with a maximum of 100.
    Example: 30

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique ID of the order.
    Example: "3b741a59-a22b-432f-b2cf-b72cc1a04c2d"

  - `items.createdAt` (string, required)
    Date of creation of the resource
    Example: "2023-01-01T00:00:00Z"

  - `items.updatedAt` (string, required)
    Date of last update of the resource
    Example: "2023-01-01T00:00:00Z"

  - `items.type` (string, required)
    The type of resource.
    Example: "flex/orders"

  - `items.generation` (integer, required)
    Monotonically increasing update counter of the resource
    Example: 1

  - `items.billingAccountId` (string, required)
    Unique ID of the billing account
    Example: "HP-APJ-0012345678"

  - `items.sowId` (string, required)
    Unique ID of Start of Work (SOW) billing order
    Example: "OPE-0011261086"

  - `items.billingAccountName` (string, required)
    Name of the billing account
    Example: "Hewlett Packard Enterprise Cloud Storage"

  - `items.orderStartDate` (string, required)
    Date of order creation
    Example: "2025-01-01T00:00:00Z"

  - `items.orderEndDate` (string, required)
    Date of order expiration
    Example: "2035-01-01T00:00:00Z"

  - `items.customerName` (string, required)
    Name of the customer
    Example: "Some Company Inc."

  - `items.resellerName` (string)
    Name of the reseller
    Example: "1st Street Resellers"

  - `items.distributorName` (string)
    Name of the distributor
    Example: "HPE Distributions"

  - `items.partnerName` (string)
    Name of partnered vendor
    Example: "Friendly Reseller LLC"

  - `items.isFlexPartner` (boolean)
    Whether the order is a Flex Partner order
    Example: true

  - `count` (integer, required)
    The number of returned items.

  - `total` (integer, required)
    The total number of items in the collection that match the filter query, if one was provided in the request.

  - `offset` (integer, required)
    The offset of the returned page.

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


