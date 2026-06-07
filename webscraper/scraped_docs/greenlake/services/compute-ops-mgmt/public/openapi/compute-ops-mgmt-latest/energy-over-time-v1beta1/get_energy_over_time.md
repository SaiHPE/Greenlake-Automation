---
title: "GET /compute-ops-mgmt/v1beta1/energy-over-time"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/energy-over-time-v1beta1/get_energy_over_time.md"
scraped_at: "2026-06-07T06:15:00.480461+00:00Z"
---

# Retrieve energy usage over time

Retrieve energy consumption, carbon emissions and cost statistics over a time interval.

Endpoint: GET /compute-ops-mgmt/v1beta1/energy-over-time
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

  - `filter-tags` (string)
    Limit the resources operated on by tags or return only the subset of resources that match all the filter tags.

  - `resource-uri` (string)
    URI of the resource for which energy data is to be retrieved.
This can be a server, filter or group URI.

  - `projection-days` (integer)
    Deprecated, use the end-date parameter with a future date instead. Number of days for projected data from today. Used when fetching projection data.
The maximum supported projection days is 180.
    Example: 30

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `kwh` (object)
    Energy consumption data in kilowatt-hours (kWh).

  - `kwh.sums` (object)
    Total energy consumption data.

  - `kwh.sums.collected` (number)
    Collected energy consumption (kWh).
    Example: 555

  - `kwh.sums.projected` (number)
    Projected energy consumption (kWh).
    Example: 75

  - `kwh.sums.total` (number)
    Total energy consumption (collected + projected) in kWh.
    Example: 630

  - `kwh.averages` (object)
    Average energy consumption data per day for the given date range.

  - `kwh.averages.collected` (number)
    Average collected energy consumption (kWh).
    Example: 185

  - `kwh.averages.projected` (number)
    Average projected energy consumption (kWh).
    Example: 20

  - `kwh.min` (object)
    Minimum energy consumption (kWh).

  - `kwh.min.value` (number)
    Minimum energy consumption value in kWh.
    Example: 0.655

  - `kwh.min.time` (string)
    Timestamp when the minimum energy consumption was recorded.
    Example: "2025-02-01T11:00:00"

  - `kwh.max` (object)
    Maximum energy consumption (kWh).

  - `kwh.max.value` (number)
    Maximum energy consumption value in kWh.
    Example: 123

  - `kwh.max.time` (string)
    Timestamp when the maximum energy consumption was recorded.
    Example: "2025-02-01T15:00:00"

  - `co2eKg` (object)
    Carbon emissions data in kilograms of CO2 equivalent (kgCO2e).

  - `co2eKg.sums` (object)
    Total carbon emissions data.

  - `co2eKg.sums.collected` (number)
    Collected carbon emissions (kgCO2e).
    Example: 1332

  - `co2eKg.sums.projected` (number)
    Projected carbon emissions (kgCO2e).
    Example: 135

  - `co2eKg.sums.total` (number)
    Total carbon emissions (collected + projected) in kgCO2e.
    Example: 1467

  - `co2eKg.averages` (object)
    Average carbon emissions per day for the given date range.

  - `co2eKg.averages.collected` (number)
    Average collected carbon emissions (kgCO2e).
    Example: 444

  - `co2eKg.averages.projected` (number)
    Average projected carbon emissions (kgCO2e).
    Example: 60

  - `co2eKg.min` (object)
    Minimum carbon emissions (kgCO2e).

  - `co2eKg.min.value` (number)
    Minimum carbon emissions value in kgCO2e.
    Example: 10.5

  - `co2eKg.min.time` (string)
    Timestamp when the minimum carbon emissions were recorded.
    Example: "2025-02-01T11:00:00"

  - `co2eKg.max` (object)
    Maximum carbon emissions (kgCO2e).

  - `co2eKg.max.value` (number)
    Maximum carbon emissions value in kgCO2e.
    Example: 456

  - `co2eKg.max.time` (string)
    Timestamp when the maximum carbon emissions were recorded.
    Example: "2025-02-01T15:00:00"

  - `cost` (object)
    Energy cost in USD.

  - `cost.sums` (object)
    Total energy cost data.

  - `cost.sums.collected` (number)
    Collected energy cost.
    Example: 2109

  - `cost.sums.projected` (number)
    Projected energy cost.
    Example: 195

  - `cost.sums.total` (number)
    Total energy cost (collected + projected).
    Example: 2304

  - `cost.averages` (object)
    Average energy cost per day for the given date range.

  - `cost.averages.collected` (number)
    Average collected energy cost.
    Example: 703

  - `cost.averages.projected` (number)
    Average projected energy cost.
    Example: 65

  - `cost.min` (object)
    Minimum energy cost.

  - `cost.min.value` (number)
    Minimum energy cost value in USD.
    Example: 5.25

  - `cost.min.time` (string)
    Timestamp when the minimum energy cost was recorded.
    Example: "2025-02-01T11:00:00"

  - `cost.max` (object)
    Maximum energy cost.

  - `cost.max.value` (number)
    Maximum energy cost value in USD.
    Example: 789

  - `cost.max.time` (string)
    Timestamp when the maximum energy cost was recorded.
    Example: "2025-02-01T15:00:00"

  - `intervalsCollected` (array)
    Collected energy data at specific time intervals.

  - `intervalsCollected.time` (string)
    Timestamp of the collected data.
    Example: "2025-02-01T00:00:00Z"

  - `intervalsCollected.kwh` (number)
    Energy consumption at this time interval (kWh).
    Example: 123

  - `intervalsCollected.co2eKg` (number)
    Carbon emissions at this time interval (kgCO2e).
    Example: 456

  - `intervalsCollected.cost` (number)
    Cost of energy at this time interval (USD).
    Example: 789

  - `intervalsCollected.serverCount` (integer)
    Number of servers for which energy data is available.
    Example: 10

  - `intervalsProjected` (array)
    Projected energy data at future time intervals.

  - `intervalsProjected.time` (string)
    Timestamp of the projected data.
    Example: "2025-05-01T00:00:00Z"

  - `intervalsProjected.kwh` (number)
    Projected energy consumption at this time interval (kWh).
    Example: 15

  - `intervalsProjected.kwhConfidenceInterval` (array)
    Lower and upper bounds of the projected energy consumption.
    Example: [10,20]

  - `intervalsProjected.co2eKg` (number)
    Projected carbon emissions at this time interval (kgCO2e).
    Example: 35

  - `intervalsProjected.co2eKgConfidenceInterval` (array)
    Lower and upper bounds of the projected carbon emissions.
    Example: [30,40]

  - `intervalsProjected.cost` (number)
    Projected cost of energy at this time interval (USD).
    Example: 55

  - `intervalsProjected.costConfidenceInterval` (array)
    Lower and upper bounds of the projected energy cost.
    Example: [50,60]

  - `intervalsProjected.serverCount` (integer)
    Number of servers considered in this projection.
    Example: 10

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


