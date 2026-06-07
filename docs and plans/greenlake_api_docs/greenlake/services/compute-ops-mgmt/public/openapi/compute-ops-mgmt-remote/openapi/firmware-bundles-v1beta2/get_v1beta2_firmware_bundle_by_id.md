---
title: "GET /compute-ops-mgmt/v1beta2/firmware-bundles/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/firmware-bundles-v1beta2/get_v1beta2_firmware_bundle_by_id.md"
scraped_at: "2026-06-07T06:14:44.039247+00:00Z"
---

# Get a firmware bundle by ID

Retrieve the firmware bundle details by its id


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: GET /compute-ops-mgmt/v1beta2/firmware-bundles/{id}
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

  - `id` (string, required)
    Primary identifier for the firmware bundle given by the system

  - `type` (string, required)
    Type of the resource

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    Time of firmware bundle creation

  - `updatedAt` (string, required)
    Time of the last firmware bundle update

  - `resourceUri` (string)
    URI to the firmware bundle itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta2/firmware-bundles/9a16ec6d-8c71-4338-a58a-6564df331ba2"

  - `name` (string)
    Name given to the bundle usually based on the bundle type

  - `releaseDate` (string)
    The date on which bundle is published to the web

  - `releaseVersion` (string)
    Latest version which got released

  - `releaseNotes` (string)
    A HPE SW Center Page link which describes how the bundle can be downloaded and installed in the customer environment

  - `supportUrl` (string)
    An URL which points to HPE SW Center Page for this bundle

  - `enhancements` (string)
    A HPE SW Center Page link which describes the enhancements included in this bundle

  - `advisories` (string)
    The link to all the customer advisories released for this bundle

  - `supportedOsList` (array)
    The list of operating systems that this bundle supports

  - `isActive` (boolean)
    Indicates the status of bundle is active or not

  - `summary` (string)
    Gives the info about the issue that will be addressed by the bundle

  - `bundleType` (string)
    Bundle Type assigned based on the servers for which it is built for
    Enum: "BASE", "HOTFIX", "SUPPLEMENT", "PATCH"

  - `hotfixBaseUri` (string,null)
    URI to the hotfixbase itself (i.e. a self link)

  - `vmwareAddonInfo` (array,null)
    Details about addon and the location of the addon in RDA

  - `bundleNameFormat` (string)
    Indicates the format of the bundle name
    Example: "BUNDLE_3OCTET"

  - `bundleGeneration` (string)
    Server generations that the bundle has support for

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


