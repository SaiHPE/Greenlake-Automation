---
title: "GET /compute-ops-mgmt/v1beta1/server-locations/{location_id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/server-locations-v1beta1/get_v1beta1_server_locations.md"
scraped_at: "2026-06-07T06:14:50.138550+00:00Z"
---

# Get location details

Get location details with id of the servers associated with the location.
 The associted servers for the location includes both direct connect and OneView managed servers.

Endpoint: GET /compute-ops-mgmt/v1beta1/server-locations/{location_id}
Version: latest
Security: Bearer

## Path parameters:

  - `location_id` (string, required)
    Location ID

## Response 200 fields (application/json):

  - `id` (string)
    Unique server-location identifier.
    Example: "36e00ac2-16fb-4dd5-8495-7e6df82fc15e"

  - `type` (string)
    The type of the resource.

  - `generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `createdAt` (string)
    Time of the server-location's creation in UTC.
    Example: "2023-12-25T01:04:21.799937+00:00"

  - `updatedAt` (string)
    Time of the server-location's last update in UTC.
    Example: "2023-12-25T01:06:30.799489+00:00"

  - `resourceUri` (string)
    The URI of this resource.
    Example: "/compute-ops-mgmt/v1beta1/server-locations/b870f080-6448-48c5-b23a-d04f2d489174"

  - `servers` (array)
    List of ids of servers assigned to server-location
    Example: ["177751-Y66+89177751666","320888-H80+89320888180"]

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

## Response 404 fields (application/json):

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

## Response 415 fields (application/json):

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


