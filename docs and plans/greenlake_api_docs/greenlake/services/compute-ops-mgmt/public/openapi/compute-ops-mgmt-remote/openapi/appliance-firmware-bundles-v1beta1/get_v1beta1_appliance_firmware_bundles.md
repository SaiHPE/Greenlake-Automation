---
title: "GET /compute-ops-mgmt/v1beta1/appliance-firmware-bundles"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/appliance-firmware-bundles-v1beta1/get_v1beta1_appliance_firmware_bundles.md"
scraped_at: "2026-06-07T06:14:41.347330+00:00Z"
---

# List all appliance firmware bundles

Retrieve the list of appliance firmware bundles

Endpoint: GET /compute-ops-mgmt/v1beta1/appliance-firmware-bundles
Version: latest
Security: Bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `sort` (string)
    The order in which to return the resources in the collection.

The value of the sort query parameter is a comma separated list of sort expressions. 
Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc 
(descending).

The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, 
and so on. If a direciton indicator is omitted the default direction is ascending.

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Server IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

Appliance firmware can be filtered by:
  - applianceVersion 
  - applianceType

The following examples are not an exhaustive list of all possible filtering options.

  - `displayAppliances` (boolean)
    Populate the applicableAppliances list in the response with all appliances which are eligible to be upgraded to that appliance firmware. This behavior is supported only when the request is provided with applianceType filter and limited to one appliance firmware bundle.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `offset` (integer, required)
    Zero-based resource offset

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

  - `items` (array, required)

  - `items.id` (string, required)
    Primary identifier for the appliance firmware bundle given by the system

  - `items.type` (string, required)
    Type of the resource

  - `items.applianceVersion` (string, required)
    Version of the OV appliance

  - `items.applianceType` (string, required)
    Type of appliance

  - `items.supportedUpgrades` (array, required)
    Supported list of upgrades for the current OV appliance

  - `items.createdAt` (string, required)
    Time of firmware bundle creation

  - `items.updatedAt` (string, required)
    Time of the last firmware bundle update

  - `items.rdaBundlePath` (string)
    Path where the bundle is stored in the RDA server
    Example: "/depot/volume/pub/OliveComputeUpdate/Ov8_50"

  - `items.ovaFileName` (string)
    Name of tha OVA file
    Example: "Update.bin"

  - `items.resourceUri` (string)
    URI to the firmware bundle itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta1/appliance-firmware-bundles/427275fcefef11ebaeaea25b204e9317"

  - `items.releaseDate` (string)
    Date of release of the selected firmware bundle

  - `items.milestone` (boolean)
    Flag that tells if the selected firmware version is a milestone version or not

  - `items.name` (string)
    Name of the appliance firmware bundle

  - `items.state` (string)
    State of the appliance firmware bundle

  - `items.releaseNotes` (string)
    A HPE SW Center Page link which describes how the bundle can be downloaded and installed in the customer environment

  - `items.size` (integer)
    Size of the appliance firmware bundle

  - `items.languages` (array)
    The list of languages that are supported

  - `items.synergyReleaseInfo` (string)
    URI to the release information

  - `items.features` (array)
    The list of features of the appliance firmware bundle

  - `items.applicableAppliances` (array)
    The list of appliances that can be updated to the latest firmware. This list will only be populated if the displayAppliances query parameter is set to true and the response is limited to one appliance firmware bundle.

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


