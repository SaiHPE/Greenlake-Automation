---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/sustainability-metrics"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4enclosurepowerssustainability.md"
scraped_at: "2026-06-07T06:16:05.159026+00:00Z"
---

# Get details of sustainability metrics of enclosure and system power supplies in Watts on storage system identified by {systemid}

Get details of sustainability metrics of enclosure and system power supplies in Watts on storage system identified by {systemid}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/sustainability-metrics
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `range` (string)
    range will define start and end time in which query has to be made.
    Example: "startTime eq 1605063600 and endTime eq 1605186000"

  - `time-interval-min` (integer)
    It defines granularity in minutes.
    Enum: 5, 60, 1440, 10080

  - `group-by` (string)
    groupBy will define comma separated groupby parameters
    Example: "VV_NAME,HOST_NAME,LUN,deviceName"

  - `metric-type` (string)
    metricType will define comma separated metrics
    Example: "IOPS,LATENCY,THROUGHPUT,IOSIZE,QLEN,AVG_BUSY,powerConsumption"

  - `filter` (string)
    filter will define objects to be filtered
    Example: "vvname in (vvname1,vvname2,vvname3) ,deviceName in (cage1)"

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

  - `items.customerId` (string,null)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.endTime` (integer,null)
    end time of history data
    Example: 1185586324

  - `items.energyConsumption` (number,null)
    Energy consumption of the storage system over the specified time interval, measured in kilowatt-hours (kWh).
    Example: 16.53

  - `items.historyData` (object,null)
    sustainability history data

  - `items.historyData.powerConsumption` (array,null)

  - `items.historyData.powerConsumption.chartLegendId` (string,null)
    Id to display chart legend, gives information about groupby and filtered objects
    Example: "VV_NAME-vvname1:HOST_NAME-host:LUN-lun"

  - `items.historyData.powerConsumption.timeseriesData` (object,null)
    Timeseries data for particular metric type

  - `items.historyData.powerConsumption.timeseriesData.total` (integer,null)
    total number of series data
    Example: 1

  - `items.startTime` (integer,null)
    start time of history data
    Example: 1825951613

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


