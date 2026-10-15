---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/capacity-forecast"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/storage-systems/devicetype4systemcapacityforecastget.md"
scraped_at: "2026-06-07T06:14:33.578254+00:00Z"
---

# Get latest capacity trend data and forecasted data

Get latest capacity trend data and forecasted data

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/capacity-forecast
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `start-time` (integer)
    Start time from which forecasted data is needed
    Example: 1591601529000

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier for the resource.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.type` (string, required)
    type
    Example: "Type of the resource"

  - `items.confidenceLevel` (number,null)
    Confidence level represents the level of certainity or probability of a forecast made by a model
    Example: 90

  - `items.customerId` (string,null)
    CustomerId of the user
    Example: "string"

  - `items.forecasted` (array,null)

  - `items.forecasted.maxUsedMiB` (number,null)
    Forecasted maximum used capacity in MiB
    Example: 4

  - `items.forecasted.minUsedMiB` (number,null)
    Forecasted minimum used capacity in MiB
    Example: 4

  - `items.forecasted.timestampMs` (integer,null)
    Epoch timestamp in milliseconds
    Example: 1605063600

  - `items.forecasted.totalMiB` (number,null)
    Forecasted total capacity in MiB.
    Example: 4

  - `items.forecasted.usedMiB` (number,null)
    Forecasted used capacity in MiB
    Example: 4

  - `items.historic` (array,null)

  - `items.historic.totalMiB` (number,null)
    Total capacity in MiB
    Example: 4

  - `items.historic.usedMiB` (number,null)
    Used capacity in MiB
    Example: 4

  - `items.message` (string,null)
    A message to describe why forecast data is not available
    Example: "No data available"

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response default fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


