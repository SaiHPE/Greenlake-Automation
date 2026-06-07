---
title: "GET /block-storage/v1alpha1/host-initiators/{hostId}/storage-performance-history"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostvolumeperformancehistoryget.md"
scraped_at: "2026-06-07T06:14:23.134947+00:00Z"
---

# Get the volume performance history data associated with a host identified by {uid}

Get the volume performance history data associated with a host identified by {uid}

Endpoint: GET /block-storage/v1alpha1/host-initiators/{hostId}/storage-performance-history
Version: 1.0.0
Security: bearer

## Path parameters:

  - `hostId` (string, required)
    Id of the Host.
    Example: "2b09e744496246859fde6c132b2091d3"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "latencyMetricsDataMs"

  - `range` (string)
    range will define start and end time in which query has to be made.
    Example: "startTime eq 1605063600 and endTime eq 1605186000"

  - `time-interval-min` (integer)
    It defines granularity in minutes.
    Enum: 5, 60, 1440, 10080

  - `top-volumes-count` (integer)
    The number of top volumes to return. Defaults to 5.
    Example: 5

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    ID of the resource
    Example: "e66ed5ce8d35961481a48b4f78bb06b4"

  - `items.type` (string, required)
    type
    Example: "Type of the resource"

  - `items.customerId` (string,null)
    customerId
    Example: "string"

  - `items.hostVolumePerfTrendData` (object,null)
    Performance history data for given time range and granularily for a volume

  - `items.hostVolumePerfTrendData.iopsMetricsData` (array,null)

  - `items.hostVolumePerfTrendData.iopsMetricsData.historicalData` (object,null)
    Timeseries data for particular metric type

  - `items.hostVolumePerfTrendData.iopsMetricsData.historicalData.total` (integer,null)
    count of series data
    Example: 1

  - `items.hostVolumePerfTrendData.iopsMetricsData.id` (string)
    The id of the volume
    Example: "60002AC0000000000000001B00025BB2"

  - `items.hostVolumePerfTrendData.iopsMetricsData.systemId` (string,null)
    The id of the system
    Example: "SGH014XGSP"

  - `items.hostVolumePerfTrendData.iopsMetricsData.volumeName` (string,null)
    The name of the volume
    Example: "test-vv"

  - `items.hostVolumePerfTrendData.latencyMetricsDataMs` (array,null)

  - `items.hostVolumePerfTrendData.throughputMetricsDataKbps` (array,null)

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


