---
title: "GET /compute-ops-mgmt/v1beta1/appliance-firmware-bundles/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/appliance-firmware-bundles-v1beta1/get_v1beta1_appliance_firmware_bundle_by_id.md"
scraped_at: "2026-06-07T06:14:41.444076+00:00Z"
---

# Get an appliance firmware bundle by ID

Retrieve the appliance firmware bundle details by its id

Endpoint: GET /compute-ops-mgmt/v1beta1/appliance-firmware-bundles/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique Appliance firmware bundle identifier

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the appliance firmware bundle given by the system

  - `type` (string, required)
    Type of the resource

  - `applianceVersion` (string, required)
    Version of the OV appliance

  - `applianceType` (string, required)
    Type of appliance

  - `supportedUpgrades` (array, required)
    Supported list of upgrades for the current OV appliance

  - `createdAt` (string, required)
    Time of firmware bundle creation

  - `updatedAt` (string, required)
    Time of the last firmware bundle update

  - `rdaBundlePath` (string)
    Path where the bundle is stored in the RDA server
    Example: "/depot/volume/pub/OliveComputeUpdate/Ov8_50"

  - `ovaFileName` (string)
    Name of tha OVA file
    Example: "Update.bin"

  - `resourceUri` (string)
    URI to the firmware bundle itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta1/appliance-firmware-bundles/427275fcefef11ebaeaea25b204e9317"

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

  - `applicableAppliances` (array)
    The list of appliances that can be updated to the latest firmware. This list will only be populated if the displayAppliances query parameter is set to true and the response is limited to one appliance firmware bundle.

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


