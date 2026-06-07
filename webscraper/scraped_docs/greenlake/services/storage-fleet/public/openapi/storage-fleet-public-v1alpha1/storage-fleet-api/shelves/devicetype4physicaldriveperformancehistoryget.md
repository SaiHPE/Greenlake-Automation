---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/physicaldrives-performance"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4physicaldriveperformancehistoryget.md"
scraped_at: "2026-06-07T06:16:12.578781+00:00Z"
---

# Get details of performance metrics of physical drives on storage system identified by {systemid}

Get details of performance metrics of physical drives on storage system identified by {systemid}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/physicaldrives-performance
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `report-type` (string)
    parameter will be set to report type requested. For api users, set parameter as ApiUser
    Example: "Canned,Custom,Def,ApiUser"

  - `range` (string)
    range will define start and end time in which query has to be made.
    Example: "startTime eq 1605063600 and endTime eq 1605186000"

  - `time-interval-min` (integer)
    It defines granularity in minutes.
    Enum: 5, 60, 1440, 10080

  - `compare-by` (string)
    compareBy will define top and compare metrics for which query has to be made. Allowed values: readIops, writeIops, totalIops, readThroughput, writeThroughput, totalThroughput, readLatency, writeLatency, totalLatency, readIosize, writeIosize, totalIosize, totalQlen, avgBusy
    Example: "top eq 5 and metrics eq readIops"

  - `group-by` (string)
    groupBy will define comma separated groupBy parameters. Allowed value: pdId. By default, groupBy will be set to pdId.
    Example: "pdId"

  - `metric-type` (string)
    metricType will define comma separated metrics
    Example: "IOPS,LATENCY,THROUGHPUT,IOSIZE,QLEN,AVG_BUSY"

  - `filter` (string)
    filter will define objects to be filtered. Filterable columns are: * pdId - id of the physical drive
    Example: "pdId in (1,2)"

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
    Cloud connectivity status of the system to which the resource belongs.
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string,null)
    customerId
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.endTime` (integer,null)
    end time of history data
    Example: 162564271

  - `items.historyData` (object,null)
    performance history data

  - `items.historyData.avgbusyMetricsDataPerct` (array,null)

  - `items.historyData.avgbusyMetricsDataPerct.chartLegendId` (string,null)
    Id to display chart legend, gives information about groupby and filtered objects
    Example: "VV_NAME-vvname1:HOST_NAME-host:LUN-lun"

  - `items.historyData.avgbusyMetricsDataPerct.timeseriesData` (object,null)
    Timeseries data for particular metric type

  - `items.historyData.avgbusyMetricsDataPerct.timeseriesData.total` (integer,null)
    total number of series data
    Example: 1

  - `items.historyData.iopsMetricsData` (array,null)

  - `items.historyData.ioszMetricsDataKbs` (array,null)

  - `items.historyData.latencyMetricsDataMs` (array,null)

  - `items.historyData.qlenMetricsData` (array,null)

  - `items.historyData.throughputMetricsDataKbps` (array,null)

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


