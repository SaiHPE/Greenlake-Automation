---
title: "GET /compute-ops-mgmt/v1/appliance-firmware-bundles/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/appliance-firmware-bundles-v1/get_v1_appliance_firmware_bundle_by_id.md"
scraped_at: "2026-06-07T06:14:41.353288+00:00Z"
---

# Get an appliance firmware bundle by ID

Retrieve the appliance firmware bundle details by its id

Endpoint: GET /compute-ops-mgmt/v1/appliance-firmware-bundles/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique Appliance firmware bundle identifier

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `id` (string)
    Primary identifier for the appliance firmware bundle given by the system
    Example: "427275fcefef11ebaeaea25b204e9317"

  - `type` (string)
    Type of the resource

  - `rdaBundlePath` (string)
    Path where the bundle is stored in the RDA server
    Example: "/depot/volume/pub/OliveComputeUpdate/Ov8_50"

  - `ovaFileName` (string)
    Name of tha OVA file
    Example: "Update.bin"

  - `resourceUri` (string)
    URI to the firmware bundle itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1/appliance-firmware-bundles/427275fcefef11ebaeaea25b204e9317"

  - `applianceVersion` (string)
    Version of the OV appliance

  - `applianceType` (string)
    Type of appliance

  - `releaseDate` (string)
    Date of release of the selected firmware bundle

  - `milestone` (boolean)
    Flag that tells if the selected firmware version is a milestone version or not

  - `name` (string)
    Name of the appliance firmware bundle

  - `state` (string)
    State of the appliance firmware bundle

  - `releaseNotes` (string)
    A HPE SW Center Page link which describes how the bundle can be downloaded and installed in the customer environment

  - `size` (integer)
    Size of the appliance firmware bundle

  - `languages` (array)
    The list of languages that are supported

  - `synergyReleaseInfo` (string)
    URI to the release information

  - `features` (array)
    The list of features of the appliance firmware bundle

  - `supportedUpgrades` (array)
    Supported list of upgrades for the current OV appliance

  - `applicableAppliances` (array)
    The list of appliances that can be updated to the latest firmware. This list will only be populated if the displayAppliances query parameter is set to true and the response is limited to one appliance firmware bundle.

  - `createdAt` (string)
    Time of firmware bundle creation

  - `updatedAt` (string)
    Time of the last firmware bundle update

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


