---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hotspots"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/devicetype4gethotspots.md"
scraped_at: "2026-06-07T06:14:25.141753+00:00Z"
---

# Get hotspots for HPE Alletra Storage MP B10000 storage system based on resourceType VOLUMES or VOLUME-SET and metricType LATENCY

Get the top hotspots segregated into read and write categories

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hotspots
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    SystemId of the HPE Alletra Storage MP B10000 storage system
    Example: "ABC239XFZ9"

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

  - `resource-type` (string)
    Query to select resource (volumes, volume-set) for analytics
    Enum: "VOLUMES", "VOLUME-SET"

  - `metric-type` (string)
    Query to select metric for which hotspot is to calculated
    Enum: "LATENCY"

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

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.customerId` (string)
    CustomerId

  - `items.endTime` (number)
    End time of the interval for which hotspots are calculated
    Example: 1669880791

  - `items.hotspots` (object,null)
    Contains the hotspots metrics per operation i.e., read and write

  - `items.hotspots.readHotspots` (array,null)
    Contains the list of hotspots metrics for read based on metricType

  - `items.hotspots.readHotspots.maxValue` (number)
    The max value for metricType and resourceType
    Example: 7.88

  - `items.hotspots.readHotspots.resourceId` (string)
    Id of the resource for which the metrics are listed
    Example: "34d6c72ba337757dde27e4a31971a46f"

  - `items.hotspots.readHotspots.resourceName` (string)
    Name of the resource for which the metrics are listed
    Example: "VV0081"

  - `items.hotspots.readHotspots.seriesData` (array,null)

  - `items.hotspots.readHotspots.seriesData.timestampMs` (number)
    Timestamp in epoch milliseconds for which the metrics are listed
    Example: 1669794420000

  - `items.hotspots.readHotspots.seriesData.value` (number)
    metric value for example latency value
    Example: 0.47

  - `items.hotspots.writeHotspots` (array,null)
    Contains the list of hotspots metrics for write based on metricType

  - `items.metricType` (string)
    Metric which is used to calculate hotspots
    Example: "latency"

  - `items.resourceType` (string)
    Resource for which hotspots is calculated
    Example: "volumes"

  - `items.startTime` (number)
    Start time of the interval for which hotspots are calculated
    Example: 1669794391

  - `items.systemId` (string)
    Serial number of the array
    Example: "ABC239XFZ9"

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


