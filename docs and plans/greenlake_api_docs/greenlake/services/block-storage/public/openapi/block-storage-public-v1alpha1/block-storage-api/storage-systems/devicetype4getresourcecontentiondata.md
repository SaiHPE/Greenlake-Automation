---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/resource-contention"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/storage-systems/devicetype4getresourcecontentiondata.md"
scraped_at: "2026-06-07T06:14:33.804338+00:00Z"
---

# Get resource contention data for resources DISK and CPU for device-type4

Get the top volume contributors and timeseries data for disk and cpu resource contention

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/resource-contention
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

  - `resource-contention-type` (string)
    Indicates if resource contention has to be calculated for disk, cpu or both resources. If this field is not provided, resource contention is calculated for both resources
    Enum: "DISK", "CPU", "ALL"

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

  - `items.cpuContention` (object,null)
    Resource contention per resource response structure

  - `items.cpuContention.resourceMetricData` (array,null)

  - `items.cpuContention.resourceMetricData.timestampMs` (number)
    Timestamp in epoch milliseconds for which the metrics are listed
    Example: 1669794420000

  - `items.cpuContention.resourceMetricData.value` (number)
    metric value for disk/cpu
    Example: 0.47

  - `items.cpuContention.topContributors` (array,null)

  - `items.cpuContention.topContributors.appsetType` (string)
    Appset Type
    Example: "Oracle"

  - `items.cpuContention.topContributors.provType` (string)
    Provisioning Type
    Example: "tpvv"

  - `items.cpuContention.topContributors.readLatency` (number)
    Read Latency
    Example: 40.25

  - `items.cpuContention.topContributors.readThroughput` (number)
    Read Throughput
    Example: 17.25

  - `items.cpuContention.topContributors.totalIops` (number)
    Total Iops
    Example: 22.36

  - `items.cpuContention.topContributors.volumeName` (string)
    VolumeName
    Example: "VV-S2444-IOPS-1.0"

  - `items.cpuContention.topContributors.volumeStatus` (string)
    Volume Status
    Example: "Normal"

  - `items.cpuContention.topContributors.volumeUid` (string)
    VolumeId
    Example: "bdce8ba359c68370085e66bf2615c30d"

  - `items.cpuContention.topContributors.writeLatency` (number)
    Write Latency
    Example: 85.25

  - `items.cpuContention.topContributors.writeThroughput` (number)
    Write Throughput
    Example: 20.75

  - `items.customerId` (string)
    CustomerId
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.diskContention` (object,null)
    Resource contention per resource response structure

  - `items.endTime` (number)
    End time of the interval for which resource contention is computed
    Example: 1669880791

  - `items.iomRecommended` (boolean)
    Indicates if resource-contention is IOM based Storage CPU Contention
    Example: true

  - `items.startTime` (number)
    Start time of the interval for which resource contention is computed
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


