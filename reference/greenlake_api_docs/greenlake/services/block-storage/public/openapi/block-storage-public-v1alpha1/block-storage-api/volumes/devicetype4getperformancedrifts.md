---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/performance-drifts"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volumes/devicetype4getperformancedrifts.md"
scraped_at: "2026-06-07T06:14:38.906038+00:00Z"
---

# Get latency drifts of a volume for a give duration

Get latency drifts of a volume for a give duration.The minimum duration supported is 8 hours and a maximum duration of 2 days. Drifts are detected in both read and write latency metrics

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/performance-drifts
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
    Customer identification attribute
    Example: "fc5f41652a53497e88cdcebc715xxxxx"

  - `items.driftsDetected` (array,null)
    Drifts detected in the selected duration

  - `items.driftsDetected.actualEndTime` (number)
    Actual end time of the Drift.
    Example: 1669880791

  - `items.driftsDetected.actualStartTime` (number)
    Actual start time of the Drift.
    Example: 1669880791

  - `items.driftsDetected.avg90thPercentile` (number)
    90th quantile of latency
    Example: 0.98

  - `items.driftsDetected.driftBuckets` (array,null)
    IO size buckets in which drifts are observed

  - `items.driftsDetected.driftBuckets.bucketName` (number)
    Bucket name in which drifts are detected
    Example: 128

  - `items.driftsDetected.driftBuckets.bucketUnit` (string)
    Metric of the bucket in which drift is detected
    Example: "KiB"

  - `items.driftsDetected.endTime` (number)
    End time of the Drift
    Example: 1669880791

  - `items.driftsDetected.iotype` (string)
    Drift detected in operation type
    Example: "read"

  - `items.driftsDetected.latencyRangeUnit` (string)
    Metric of the latency range
    Example: "ms"

  - `items.driftsDetected.maxLatencyLowerRange` (number)
    Floor of the latency bucket
    Example: 6

  - `items.driftsDetected.maxLatencyUpperRange` (number)
    Ceiling of the latency bucket
    Example: 8

  - `items.driftsDetected.startTime` (number)
    Start time of the Drift
    Example: 1669880791

  - `items.driftsDetected.updated` (boolean)
    Specifies if the values are changed.

  - `items.endTime` (number)
    End time of the drift detection interval
    Example: 1669880791

  - `items.startTime` (number)
    Start time of the drift detection interval
    Example: 1669794391

  - `items.systemId` (string)
    Serial number of the array
    Example: "ABC239XFZ9"

  - `items.timeZone` (string)
    timezone
    Example: "Asia/Calcutta"

  - `items.volumeId` (string)
    This attributes represents volume identification
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


