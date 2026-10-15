---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/latency-annotations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volumes/devicetype4getvolumelatencyannotations.md"
scraped_at: "2026-06-07T06:14:38.914978+00:00Z"
---

# Get volume latency annotations for device-type4

Get the high latency points to be annotated segregated into read and write categories

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/latency-annotations
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    SystemId of the HPE Alletra Storage MP B10000 storage system
    Example: "ABC239XFZ9"

  - `volumeId` (string, required)
    VolumeId of the device-type4 storage system
    Example: "60002AC000000000000005B200029834"

## Query parameters:

  - `time-interval-min` (integer, required)
    Time interval granularity in minutes
    Enum: 5, 60, 1440

  - `range` (string, required)
    Specifies the time period for which hotspot metrics are to be calculated. Both startTime and endTime should be specified
    Example: "startTime eq 1605063600 and endTime eq 1605186000"

  - `operation-type` (string)
    Indicates if hotspots metrics to be calculated for read, write or both operations. If this field is not provided, hotspots are calculated for both operations
    Enum: "READ", "WRITE", "ALL"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    ID of the resource

  - `items.type` (string, required)
    Type of the resource

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.customerId` (string)
    CustomerId
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.endTime` (number)
    End time of the interval for which annotated points are returned
    Example: 1669880791

  - `items.latencyAnnotations` (object,null)
    Volume latency annotations response structure

  - `items.latencyAnnotations.read` (array,null)

  - `items.latencyAnnotations.read.latencyQtl90` (number)
    Value of 90th quantile of time histogram
    Example: 6.21

  - `items.latencyAnnotations.read.maxRange` (string)
    Maximum range of values in time histogram
    Example: "6ms-8ms"

  - `items.latencyAnnotations.read.timestampMs` (number)
    Timestamp in milliseconds
    Example: 1669880791

  - `items.latencyAnnotations.write` (array,null)

  - `items.startTime` (number)
    Start time of the interval for which annotated points are selected
    Example: 1669794391

  - `items.systemId` (string)
    Serial number of the array
    Example: "ABC239XFZ9"

  - `items.volumeId` (string)
    VolumeId
    Example: "60002AC000000000000005B200029834"

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


