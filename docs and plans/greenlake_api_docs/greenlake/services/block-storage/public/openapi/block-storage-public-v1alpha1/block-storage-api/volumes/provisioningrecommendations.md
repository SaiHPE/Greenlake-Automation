---
title: "POST /block-storage/v1alpha1/storage-systems/provisioning-recommendations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volumes/provisioningrecommendations.md"
scraped_at: "2026-06-07T06:14:39.000044+00:00Z"
---

# Produce a set of provisioning recommendations based on the provided input parameters.

Produce a set of provisioning recommendations based on the provided input parameters.

Endpoint: POST /block-storage/v1alpha1/storage-systems/provisioning-recommendations
Version: 1.0.0
Security: bearer

## Request fields (application/json):

  - `sizeMib` (integer, required)
    volume size requirement
    Example: 16384

  - `hostGroupId` (string,null)
    host group id
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

  - `productFamily` (string,null)
    Storage device type

## Response 202 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    uid of the array
    Example: "RTYTY123"

  - `items.capacityInfo` (object,null)
    Device capacity details

  - `items.capacityInfo.capacitySummary` (object,null)

  - `items.capacityInfo.capacitySummary.free` (integer,null)
    Total free capacity

  - `items.capacityInfo.capacitySummary.total` (integer,null)
    Total used capacity

  - `items.mgmtIp` (string)
    management Ip of the array
    Example: "1.2.3.4"

  - `items.name` (string)
    name of the array
    Example: "system_Name"

  - `items.productFamily` (string)
    Storage device type. Possible values: deviceType1 and deviceType2
    Example: "deviceType1"

  - `items.state` (string,null)
    For deviceType1 State derived from ports, enclosure, disk and node state for deviceType2 state is state reported by deviceType2 array
    Enum: "NORMAL", "DEGRADED", null

  - `items.systemWwn` (string)
    WWN of the array
    Example: "2FF70002AC018D94"

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

## Response 404 fields (application/json):

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


