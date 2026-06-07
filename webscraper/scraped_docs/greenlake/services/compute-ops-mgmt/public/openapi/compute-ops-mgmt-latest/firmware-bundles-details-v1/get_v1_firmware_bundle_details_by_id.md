---
title: "GET /compute-ops-mgmt/v1/firmware-bundles/{id}/bundle-details"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/firmware-bundles-details-v1/get_v1_firmware_bundle_details_by_id.md"
scraped_at: "2026-06-07T06:15:01.535158+00:00Z"
---

# Get component details by firmware bundle ID

Retrieve component details by firmware bundle id

Endpoint: GET /compute-ops-mgmt/v1/firmware-bundles/{id}/bundle-details
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique Firmware bundle identifier

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `offset` (integer, required)
    Zero-based resource offset

  - `items` (array, required)

  - `items.id` (string, required)
    Unique identifier for the component category
    Example: "7c6dcb05-9c95-41f8-9819-f01c790b7716"

  - `items.type` (string, required)
    Type of the resource

  - `items.generation` (integer, required)
    Monotonically increasing update counter

  - `items.createdAt` (string, required)
    Time of bundle detail creation

  - `items.updatedAt` (string, required)
    Time of the last bundle detail update

  - `items.bundleId` (string)
    Bundle ID corresponding to the firmware bundle
    Example: "efa0f78b19144f69af9bf32c7a974cbd"

  - `items.category` (string)
    Category of the firmware component
    Example: "NETWORKING_ADAPTERS"

  - `items.categoryDetails` (array)
    Collection of the components in the category

  - `items.categoryDetails.Devices` (array)
    Collection of the components corresponding to the firmware component type.

  - `items.categoryDetails.Devices.Target` (string)
    Unique identifier for the device
    Example: "a6b1a447-382a-5a4f-14E4-168E103C339D"

  - `items.categoryDetails.Devices.DeviceName` (string)
    Name of the firmware component
    Example: "HPE Ethernet 10Gb 2-port 530SFP+ Adapter"

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

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


