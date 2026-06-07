---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/performance-histogram"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4getperformancehistogram.md"
scraped_at: "2026-06-07T06:14:28.947279+00:00Z"
---

# Get histogram buckets distribution of I/Os of a volume for a given duration.

Get the I/O size histogram for a volume over the specified duration. The buckets query parameter must contain one or more of: Size512B, Size1k, Size2k, Size4k, Size8k, Size16k, Size32k, Size64k, Size128k, Size256k, Size512k, Size1m, Size2m

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/performance-histogram
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID(volumeuid) of the storage system
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

## Query parameters:

  - `range` (string)
    range will define start and end time in which query has to be made.
    Example: "startTime eq 1605063600 and endTime eq 1605186000"

  - `time-interval-min` (integer)
    It defines granularity in minutes.
    Enum: 5, 60, 1440, 10080

  - `io-type` (string)
    Indicates if histogram metrics to be calculated for read or write.
    Enum: "read", "write"

  - `buckets` (string)
    Comma separated buckets list. Following values are supported:  Size512B, Size1k, Size2k, Size4k, Size8k, Size16k, Size32k, Size64k, Size128k, Size256k, Size512k, Size1m, Size2m

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
    Id specific to the customer

  - `items.deviceType` (string,null)
    device type
    Enum: "devicetype1", "devicetype2", "devicetype4", "devicetype7"

  - `items.endTime` (number)
    End time for volume histogram data
    Example: 1669880791

  - `items.sizeHistogramData` (object,null)
    Size histogram data structure

  - `items.sizeHistogramData.aggs` (object,null)
    Aggregated results of histogram size bucktes

  - `items.sizeHistogramData.aggs.avgPercentages` (object,null)
    Average percentage of performance histogram

  - `items.sizeHistogramData.aggs.avgPercentages.read` (array,null)
    List of histogram size buckets and respective average percentage of I/O throughout the interval

  - `items.sizeHistogramData.aggs.avgPercentages.read.name` (string)
    Name of the histogram bucket
    Example: "2K"

  - `items.sizeHistogramData.aggs.avgPercentages.read.percentage` (number,null)
    Average Percentage of I/O happened in size bucket throughout the interval
    Example: 20

  - `items.sizeHistogramData.aggs.avgPercentages.write` (array,null)
    List of histogram size buckets and respective average percentage of I/O throughout the interval

  - `items.sizeHistogramData.seriesData` (array,null)
    Size histogram data structure

  - `items.sizeHistogramData.seriesData.readBuckets` (array,null)
    Histogram data of io buckets

  - `items.sizeHistogramData.seriesData.readBuckets.percentage` (number)
    Percentage of I/O in respective histogram bucket
    Example: 20

  - `items.sizeHistogramData.seriesData.readBuckets.value` (number)
    Number of I/Os in respective histogram bucket
    Example: 1151

  - `items.sizeHistogramData.seriesData.timestamp` (number)
    Timestamp in epoch milliseconds for which the metrics are listed
    Example: 1669794420000

  - `items.sizeHistogramData.seriesData.writeBuckets` (array,null)
    Histogram data of io buckets

  - `items.startTime` (number)
    Start time for volume histogram data
    Example: 1669794391

  - `items.systemId` (string,null)
    system ID

  - `items.volumeId` (string,null)
    volume ID

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


