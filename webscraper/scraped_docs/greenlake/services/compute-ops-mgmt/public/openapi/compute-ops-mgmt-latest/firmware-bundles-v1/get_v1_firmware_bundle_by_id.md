---
title: "GET /compute-ops-mgmt/v1/firmware-bundles/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/firmware-bundles-v1/get_v1_firmware_bundle_by_id.md"
scraped_at: "2026-06-07T06:15:01.426098+00:00Z"
---

# Get a firmware bundle by ID

Retrieve the firmware bundle details by its id

Endpoint: GET /compute-ops-mgmt/v1/firmware-bundles/{id}
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

  - `id` (string)
    Primary identifier for the firmware bundle given by the system
    Example: "275a59f78916400a761e4bf8c6958934"

  - `type` (string)
    Type of the resource

  - `generation` (integer)
    Monotonically increasing update counter

  - `name` (string)
    Name given to the bundle usually based on the bundle type
    Example: "Gen10 Service Pack for ProLiant"

  - `resourceUri` (string)
    URI to the firmware bundle itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1/firmware-bundles/275a59f78916400a761e4bf8c6958934"

  - `description` (string)
    A brief description of the bundle
    Example: "Gen10/Gen10 Plus Service Pack for ProLiant (SPP) is a comprehensive systems software and firmware update solution"

  - `createdAt` (string)
    Time of firmware bundle creation
    Example: "2023-08-24T02:08:58.675535Z"

  - `updatedAt` (string)
    Time of the last firmware bundle update
    Example: "2023-08-24T02:08:58.675535Z"

  - `releaseDate` (string)
    The date on which bundle is published to the web
    Example: "2023-09-12T00:00:00+00:00"

  - `summary` (string)
    Gives the information about the issue that will be addressed by the bundle
    Example: "Gen10/Gen10 Plus SPP 2023.09.00.00 release supersedes Gen10/Gen10 Plus SPP 2023.03.00.00 and includes support for Red Hat Enterprise Linux 9.2, RHEL 8.8 and SLES15 SP5."

  - `bundleType` (string)
    Bundle Type assigned based on the servers for which it is built for
    Enum: "BASE", "PATCH", "HOTFIX", "SUPPLEMENT"

  - `platformFamily` (string)
    Platform family of the server
    Enum: "PROLIANT"

  - `baseBundleUri` (string,null)
    URI of the base bundle

  - `releaseVersion` (string)
    Latest version which got released
    Example: "2023.09.00.00"

  - `enhancements` (string)
    A HPE SW Center Page link which describes the enhancements included in this bundle
    Example: "Gen10/Gen10 Plus SPP 2023.09.00.00 includes support for the following OS Versions Red Hat Enterprise Linux 8.8 Red Hat Enterprise Linux 9.2 SUSE Linux Enterprise Server 15 SP5"

  - `advisories` (string)
    The link to all the customer advisories released for this bundle
    Example: "http://auth-essn-pro-sitebuilder.its.hpecorp.net/us/en/enterprise/servers/products/service_pack/spp_test/index.aspx?version=gen10.2023.09.00.00"

  - `supportedOsList` (array)
    The list of operating systems that this bundle supports
    Example: "Microsoft Windows Server 2022, Red Hat Enterprise Linux 9, VMware ESXi 8.0"

  - `isActive` (boolean)
    Indicates the status of bundle is active or not

  - `releaseNotes` (string)
    A HPE SW Center Page link which describes how the bundle can be downloaded and installed in the customer environment
    Example: "Gen10/Gen10 Plus SPP 2023.09.00.00 includes support."

  - `supportUrl` (string)
    An URL which points to HPE SW Center Page for this bundle
    Example: "http://auth-essn-pro-sitebuilder.its.hpecorp.net/us/en/enterprise/servers/products/service_pack/spp_test/index.aspx?version=gen10.2023.09.00.00"

  - `displayName` (string)
    SPP bundle name
    Example: "SPP 2023.09.00.00 (12 Sep 2023)"

  - `vmwareAddonInfo` (array,null)
    Details about vmware addon and the location of the vmware addon in RDA

  - `bundleNameFormat` (string)
    Indicates the format of the bundle name
    Example: "BUNDLE_4OCTET"

  - `bundleGeneration` (string)
    Server generations that the bundle has support for
    Example: "BUNDLE_GEN_10"

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


