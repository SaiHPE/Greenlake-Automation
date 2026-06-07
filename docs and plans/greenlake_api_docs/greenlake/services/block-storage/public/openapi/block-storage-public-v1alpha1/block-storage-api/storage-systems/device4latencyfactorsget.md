---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/latency-factors"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/storage-systems/device4latencyfactorsget.md"
scraped_at: "2026-06-07T06:14:33.877671+00:00Z"
---

# Get system level latency factors

Get system level latency factors of system identified by {systemId}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/latency-factors
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `time-interval-min` (integer, required)
    Time interval granularity in minutes
    Enum: 5, 60, 1440

  - `range` (string)
    range will define start and end time in which query has to be made.
    Example: "startTime eq 1605063600 and endTime eq 1605186000"

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

  - `items.customerId` (string)
    Customer identifier

  - `items.endTime` (integer)
    End time of the interval for which latency factors are determined
    Example: 1669880791

  - `items.latencyBands` (object,null)

  - `items.latencyBands.read` (array)

  - `items.latencyBands.read.endTime` (number)
    Timestamp
    Example: 1669880791

  - `items.latencyBands.read.startTime` (number)
    Timestamp
    Example: 1669880791

  - `items.latencyBands.read.topFactors` (array)
    Top latency factors

  - `items.latencyBands.write` (array,null)

  - `items.startTime` (integer)
    Start time of the interval for which latency factors are determined
    Example: 1669794391

  - `items.systemFactorsMetrics` (array,null)

  - `items.systemFactorsMetrics.cpuBusy` (number)
    CPU busy percentage
    Example: 2.47

  - `items.systemFactorsMetrics.dackSsd` (number)
    Delayed ack percentage
    Example: 2.47

  - `items.systemFactorsMetrics.pdSsdAvgBusy` (number)
    PD average busy percentage
    Example: 2.47

  - `items.systemFactorsMetrics.readCacheMiss` (number)
    Read cache miss percentage
    Example: 2.47

  - `items.systemFactorsMetrics.timestamp` (integer)
    Timestamp
    Example: 1669880791

  - `items.systemFactorsMetrics.writeCacheMiss` (number)
    Write cache miss percentage
    Example: 2.47

  - `items.systemId` (string)
    System identifier

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


