---
title: "GET /subscriptions/v1alpha1/subscriptions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi/subscriptions-v1alpha1/getsubscriptionsv1alpha1.md"
scraped_at: "2026-06-07T06:16:24.027805+00:00Z"
---

# Get subscriptions of a workspace (deprecated)

Get subscriptions managed in a workspace. Pass filters to limit results based on conditional expressions. NOTE: You need to have the view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 40 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

Endpoint: GET /subscriptions/v1alpha1/subscriptions
Version: latest
Security: Bearer

## Query parameters:

  - `filter` (string)
    Filter expressions consisting of simple comparison operations joined by logical operators.
    Example: "key eq 'MHNBAP0001' and key in 'PAYHAH3YJE6THY, E91A7FDFE04D44C339'"

  - `sort` (string)
    A comma separated list of sort expressions. A sort expression is a property name optionally followed by a direction indicator asc or desc. Default is ascending order.
    Example: "key, quote desc"

  - `select` (array)
    A comma separated list of select properties to return in the response. By default, all properties are returned.
    Example: "id,key"

  - `limit` (integer)
    Specifies the number of results to be returned. The default value is 2000.

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from. Default value is 0.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique identifier for the subscription.
    Example: "b49bf6d2-02b4-4735-9ae5-f88834af9b7e"

  - `items.key` (string)
    The subscription key.
    Example: "BAASOAAg95"

  - `items.quantity` (string)
    Total quantity of the subscription.
    Example: 10

  - `items.evaluationType` (string)
    The type of license.
    Enum: "EVAL", "ALPHA", "NONE"

  - `items.productSku` (string)
    The product stock keeping unit (SKU).
    Example: "ROTO1AAE"

  - `items.productDescription` (string)
    A description of the product stock keeping unit.
    Example: "HPE GreenLake for Block Storage 3 Year(s)"

  - `items.quote` (string)
    A unique number that identifies an order and all its attached subscriptions.
    Example: "quote1"

  - `items.po` (string)
    The purchase order number.
    Example: "POAQE451"

  - `items.contract` (string)
    Example: "V16BMAAS"

  - `items.endUserName` (string)
    The customer name to which the subscription belongs.
    Example: "ACCUTECH DATA SUPPLIES, INC."

  - `items.orderClass` (string)
    The ordering system source.
    Example: "class1"

  - `items.aasType` (string)
    Defines the as a service (aaS) type. For example, infrastructure as a service (IAAS).
    Enum: "IAAS"

  - `items.appointment` (object)

  - `items.appointment.subscriptionStart` (string)
    Start date of the subscription.
    Example: "2023-02-10T00:00:00.000Z"

  - `items.appointment.subscriptionEnd` (string)
    End date of the subscription.
    Example: "2023-02-10T00:00:00.000Z"

  - `items.appointment.delayedActivation` (string)
    Delayed activation date of the subscription.
    Example: "2023-02-10T00:00:00.000Z"

  - `count` (integer, required)
    Number of items returned.
    Example: 20

  - `offset` (integer)
    Zero-based resource offset.

  - `total` (integer)
    Total number of items in the collection that match the filter query, if one was provided in the request otherwise total number of items for a given resource.
    Example: 100

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


