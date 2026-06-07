---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/headroom-contribution"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/devicetype4getheadroomcontribution.md"
scraped_at: "2026-06-07T06:14:25.122798+00:00Z"
---

# Get Top headroom contribution by volumes/Apps for device-type4

Get Top headroom contribution by volumes/Apps for device-type4

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/headroom-contribution
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

  - `resource-type` (string)
    Query to select resource (volumes, volume-set) for getting Headroom Contributors
    Enum: "VOLUMES", "VOLUME-SET"

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

  - `items.averageHeadroomUtilization` (object,null)

  - `items.averageHeadroomUtilization.system` (object,null)

  - `items.averageHeadroomUtilization.system.headroom` (number)
    headroom utilized on system
    Example: 12.29

  - `items.averageHeadroomUtilization.system.headroomUtilised` (string)
    headroom utilized in terms of Low/Medium/High
    Example: "High"

  - `items.customerId` (string)
    id specific to the customer

  - `items.endTime` (number)
    endTime refers to last/ending period of the interval for which contributors are fetched
    Example: 1669880791

  - `items.headroomContribution` (object)

  - `items.headroomContribution.resources` (array,null)

  - `items.headroomContribution.resources.resourceName` (string,null)
    Name of the resource
    Example: "test-volume"

  - `items.headroomContribution.resources.seriesData` (array,null)

  - `items.headroomContribution.resources.seriesData.headroom` (number)
    headroom utilized on resource
    Example: 12.29

  - `items.headroomContribution.resources.seriesData.headroomPct` (number,null)
    headroom percentage contribution from resource on system
    Example: 20

  - `items.headroomContribution.resources.seriesData.headroomUtilized` (string)
    headroom utilized in terms of Low/Medium/High
    Example: "High"

  - `items.headroomContribution.resources.seriesData.timestampMs` (number)
    timestamp for which the metrics are present
    Example: 1669794420000

  - `items.remaining` (array,null)

  - `items.resourceType` (string)
    Resource type - volumes

  - `items.startTime` (number)
    startTime refers to starting period of the interval for which contributors are fetched
    Example: 1669794391

  - `items.systemId` (string,null)
    Serial Number of the array
    Example: "7CEFVC12"

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


