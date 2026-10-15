---
title: "GET /compute-ops-mgmt/v1beta1/settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/settings-v1beta1/get_v1beta1_settings.md"
scraped_at: "2026-06-07T06:14:51.196398+00:00Z"
---

# List all device settings

Get the list of a user's device settings

Endpoint: GET /compute-ops-mgmt/v1beta1/settings
Version: latest
Security: Bearer

## Query parameters:

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Device IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

Settings can be filtered by:
- category
- description
- name
- settings

The following examples are not an exhaustive list of all possible filtering options.

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

  - `items.id` (string)
    Primary identifier for the setting given by the system

  - `items.name` (string)
    The display name for the setting

  - `items.description` (string,null,string,null)
    The description for the setting

  - `items.category` (string)
    The category to which the settings data applies.

The available server settings categories are:
* BIOS - BIOS configuration
* EXTERNAL_STORAGE - storage configured in HPE GreenLake for Data Services Cloud Console (DSCC)
* FIRMWARE - firmware configuration
* ILO - iLO security configuration
* OS - operating system
* STORAGE - internal storage configuration

The available OneView VM appliance settings categories are:
* OVE_APPLIANCE_SETTINGS_ANY - appliance configuration
* OVE_SERVER_TEMPLATES_VM - server profile templates
* OVE_SOFTWARE_VM - OneView appliance software

The available OneView Synergy appliance settings categories are:
* OVE_APPLIANCE_SETTINGS_ANY - appliance configuration
* OVE_APPLIANCE_SETTINGS_SYNERGY - synergy-specific appliance configuration
* OVE_SERVER_TEMPLATES_SYNERGY - server profile templates
* OVE_SOFTWARE_SYNERGY - OneView Synergy appliance software
    Enum: "BIOS", "EXTERNAL_STORAGE", "FIRMWARE", "ILO", "OS", "STORAGE", "OVE_APPLIANCE_SETTINGS_ANY", "OVE_APPLIANCE_SETTINGS_SYNERGY", "OVE_SERVER_TEMPLATES_SYNERGY", "OVE_SERVER_TEMPLATES_VM", "OVE_SOFTWARE_VM", "OVE_SOFTWARE_SYNERGY"

  - `items.settings` (object)
    Configuration data corresponding to the specified category

  - `items.settings.GEN10` (any)

  - `items.settings.GEN11` (any)

  - `items.settings.GEN12` (any)

  - `items.settings.DEFAULT` (any)

  - `items.generation` (integer)
    Monotonically increasing update counter

  - `items.resourceUri` (string)
    URI to the settings itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta1/settings/a2fdaf7a-4933-4c47-bfe0-891f0a83dc6e"

  - `items.type` (string)
    Type of the resource

  - `items.createdAt` (string)
    Time of settings creation

  - `items.updatedAt` (string)
    Time of the last settings update

  - `total` (integer)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

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


