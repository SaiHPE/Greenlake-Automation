---
title: "GET /compute-ops/v1beta1/server-settings/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/server-settings-v1beta1/get_v1beta1_server_settings_by_id.md"
scraped_at: "2026-06-07T06:14:50.751458+00:00Z"
---

# Get a server-settings item by ID

Get a specific server-settings item by server-settings id.

Endpoint: GET /compute-ops/v1beta1/server-settings/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the server-settings given by the system

  - `type` (string, required)
    Type of the resource

  - `name` (string, required)
    The display name for the server-settings item

  - `category` (string, required)
    The category to which the settings data applies.

The available server settings categories are:
* BIOS - BIOS configuration
* EXTERNAL_STORAGE - storage configured in HPE GreenLake for Data Services Cloud Console (DSCC)
* FIRMWARE - firmware configuration
* ILO - iLO security configuration
* OS - operating system
* STORAGE - internal storage configuration
    Enum: "FIRMWARE", "BIOS", "STORAGE", "OS", "EXTERNAL_STORAGE", "ILO"

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    Time of server-settings creation

  - `updatedAt` (string, required)
    Time of the last server-settings update

  - `description` (string,null)
    Server settings description

  - `platformFamily` (string)
    Server platform family to which this server setting applies. There are no restrictions for server settings and all supported server types are allowed. This optional attribute will be set to a default value of "ANY", to indicate that any server platform family can be in the group(s) which are associated with this server setting, regardless of the value passed in.
    Enum: "ANY", "PROLIANT"

  - `settings` (object)
    Configuration data corresponding to the specified category

  - `settings.GEN10` (any)

  - `settings.GEN11` (any)

  - `settings.GEN12` (any)

  - `settings.DEFAULT` (any)

  - `resourceUri` (string)
    URI to the server-settings itself (i.e. a self link)
    Example: "/compute-ops/v1beta1/server-settings/a2fdaf7a-4933-4c47-bfe0-891f0a83dc6e"

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


