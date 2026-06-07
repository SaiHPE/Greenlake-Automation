---
title: "GET /compute-ops-mgmt/v1beta1/energy-by-entity"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/energy-by-entity-v1beta1/get_energy_by_entity.md"
scraped_at: "2026-06-07T06:15:00.429633+00:00Z"
---

# Retrieve energy usage by entity

Retrieve energy consumption, CO2 emissions and cost details per entity.

Endpoint: GET /compute-ops-mgmt/v1beta1/energy-by-entity
Version: latest
Security: Bearer

## Query parameters:

  - `start-date` (string, required)
    Start date for energy data retrieval. This can be a date in the past or future, but must be within 180 days from today.

  - `sample-size` (string, required)
    The data sample size to be used in the API response.
    Enum: "1_DAY", "1_HOUR", "5_MINS"

  - `end-date` (string)
    End date for energy data retrieval. This can be a date in the past or future, but must be within 180 days from today.

  - `aggregate-by` (string)
    Aggregation level for energy consumption data.
    Enum: "SERVER", "SERVER_MODEL", "SERVER_GENERATION", "SERVER_PROCESSOR", "SERVER_LOCATION", "SERVER_TAG_VALUES"

  - `excluded-servers` (boolean)
    When it is set to true, the response will have details of servers which do not have energy data available.
    Example: true

  - `resource-uri` (string)
    URI of the resource for which energy data is to be retrieved.
This can be a server, filter or group URI.

  - `filter` (string)
    Limit the resources operated on by an endpoint or return only the subset of resources that match the filter.

NOTE: The filter query parameter must use URL encoding.

  - `filter-tags` (string)
    Limit the resources operated on by tags or return only the subset of resources that match all the filter tags.

  - `aggregation-tag-names` (string)
    Comma-separated names of the tags to be used for aggregation. A maximum of 3 tags can be specified. Only applicable when aggregating by SERVER_TAG_VALUES.

  - `sort` (string)
    The order in which to return the resources in the collection.
Sort expression is a property name, followed by asc (ascending) or desc (descending).

Default sort order: co2eKg/collected asc

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `projection-days` (integer)
    Deprecated, use the end-date parameter with a future date instead. Number of days for projected data from today. Used when fetching projection data.
The maximum supported projection days is 180.
    Example: 30

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `count` (integer)
    Number of items in the response.
    Example: 2

  - `offset` (integer)
    Offset of the returned items.

  - `total` (integer)
    Total number of items available.
    Example: 2

  - `excluded` (integer)
    Number of excluded servers for which energy data is not available.

  - `kwhSums` (object)
    Total energy consumption data.

  - `kwhSums.collected` (number)
    Collected energy consumption (kWh).
    Example: 444

  - `kwhSums.projected` (number)
    Projected energy consumption (kWh).
    Example: 432

  - `kwhSums.total` (number)
    Total energy consumption (collected + projected) in kWh.
    Example: 876

  - `co2eKgSums` (object)
    Total carbon emissions data.

  - `co2eKgSums.collected` (number)
    Collected carbon emissions (kgCO2e).
    Example: 1110

  - `co2eKgSums.projected` (number)
    Projected carbon emissions (kgCO2e).
    Example: 1986

  - `co2eKgSums.total` (number)
    Total carbon emissions (collected + projected) in kgCO2e.
    Example: 3096

  - `costSums` (object)
    Total energy cost data.

  - `costSums.collected` (number)
    Collected energy cost (USD).
    Example: 1776

  - `costSums.projected` (number)
    Projected energy cost (USD).
    Example: 1320

  - `costSums.total` (number)
    Total energy cost (collected + projected) in USD.
    Example: 3096

  - `items` (array)
    List of individual entity energy data.

  - `items.id` (string)
    Unique identifier of the entity
    Example: "ABCDEF-B21+MXQLABC"

  - `items.name` (string)
    Name of the entity
    Example: "server-ABC"

  - `items.type` (string)
    Type of entity
    Example: "SERVER"

  - `items.serverCount` (integer)
    Number of servers for this entity.
    Example: 5

  - `items.entityDetails` (any)

  - `items.kwh` (object)
    Energy consumption data in kWh.

  - `items.kwh.collected` (number)
    Collected energy consumption.
    Example: 123

  - `items.kwh.projected` (number)
    Projected energy consumption.
    Example: 321

  - `items.kwh.total` (number)
    Total energy consumption (collected + projected).
    Example: 654

  - `items.kwh.min` (number)
    Minimum energy consumption
    Example: 12

  - `items.kwh.max` (number)
    Maximum energy consumption
    Example: 123

  - `items.kwh.average` (number)
    Average energy consumption
    Example: 65.4

  - `items.kwh.percents` (object)
    The percentage of energy consumption compared to the respective attribute in kwhSums.

  - `items.kwh.percents.collected` (number)
    Percentage of collected energy consumption.
    Example: 14.04

  - `items.kwh.percents.projected` (number)
    Percentage of projected energy consumption.
    Example: 36.64

  - `items.kwh.percents.total` (number)
    Percentage of total energy consumption.
    Example: 35.66

  - `items.co2eKg` (object)
    Carbon emissions data in kgCO2e.

  - `items.co2eKg.collected` (number)
    Collected carbon emissions.
    Example: 456

  - `items.co2eKg.projected` (number)
    Projected carbon emissions.
    Example: 654

  - `items.co2eKg.total` (number)
    Total carbon emissions (collected + projected).
    Example: 654

  - `items.co2eKg.min` (number)
    Minimum carbon emissions
    Example: 45

  - `items.co2eKg.max` (number)
    Maximum carbon emissions
    Example: 456

  - `items.co2eKg.average` (number)
    Average carbon emissions
    Example: 123.4

  - `items.co2eKg.percents` (object)
    The percentage of carbon emissions compared to the respective attribute in co2eKgSums.

  - `items.co2eKg.percents.collected` (number)
    Percentage of collected carbon emissions.
    Example: 41.08

  - `items.co2eKg.percents.projected` (number)
    Percentage of projected carbon emissions.
    Example: 21.12

  - `items.co2eKg.percents.total` (number)
    Percentage of total carbon emissions.
    Example: 35.66

  - `items.cost` (object)
    Energy cost data in USD.

  - `items.cost.collected` (number)
    Collected energy cost.
    Example: 789

  - `items.cost.projected` (number)
    Projected energy cost.
    Example: 987

  - `items.cost.total` (number)
    Total energy cost (collected + projected).
    Example: 654

  - `items.cost.min` (number)
    Minimum energy cost
    Example: 78

  - `items.cost.max` (number)
    Maximum energy cost
    Example: 789

  - `items.cost.average` (number)
    Average energy cost
    Example: 123.4

  - `items.cost.percents` (object)
    The percentage of cost compared to the respective attribute in costSums.

  - `items.cost.percents.collected` (number)
    Percentage of collected energy cost.
    Example: 25.48

  - `items.cost.percents.projected` (number)
    Percentage of projected energy cost.
    Example: 31.88

  - `items.cost.percents.total` (number)
    Percentage of total energy cost.
    Example: 35.66

  - `items.status` (string)
    Represents whether data is available for the server.
If data is available, the status will show "COMPLETE". 
If data is not fully available, the status will show "PARTIAL".
    Example: "COMPLETE"

  - `items.statusReason` (string)
    The reason for the current status.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 406 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error


