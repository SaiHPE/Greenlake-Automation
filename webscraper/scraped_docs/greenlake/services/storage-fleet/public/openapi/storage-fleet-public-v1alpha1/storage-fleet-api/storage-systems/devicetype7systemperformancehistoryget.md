---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/performance-history"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7systemperformancehistoryget.md"
scraped_at: "2026-06-07T06:16:13.999071+00:00Z"
---

# Get performance trend data for a HPE Alletra Storage MP X10000 system

Get performance trend data for a HPE Alletra Storage MP X10000 system

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/performance-history
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the storage system
    Example: "2a0df0fe6f7dc7bb16000000000000000000004817"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `range` (string)
    range will define start and end time in which query has to be made.
    Example: "startTime eq 1605063600 and endTime eq 1605186000"

  - `time-interval-min` (integer)
    It defines granularity in minutes.
    Enum: 5, 60, 1440, 10080

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

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the resource belongs
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cp"

  - `items.endTime` (integer,null)
    end time of history data
    Example: 162564271

  - `items.historyData` (object,null)

  - `items.historyData.dataTransferred` (object,null)

  - `items.historyData.dataTransferred.seriesData` (array,null)

  - `items.historyData.dataTransferred.seriesData.timestampMs` (integer,null)
    Epoch timestamp
    Example: 1605063600

  - `items.historyData.dataTransferred.seriesData.totalBytesRead` (number,null)
    Total number of bytes read in KiB
    Example: 1332

  - `items.historyData.dataTransferred.seriesData.totalBytesWritten` (number,null)
    Total number of bytes written in KiB
    Example: 13324

  - `items.historyData.dataTransferred.total` (integer,null)
    Count of series data
    Example: 1

  - `items.historyData.s3RequestCount` (object,null)

  - `items.historyData.serviceTime` (object,null)

  - `items.startTime` (integer,null)
    start time of history data
    Example: 1625556314

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


