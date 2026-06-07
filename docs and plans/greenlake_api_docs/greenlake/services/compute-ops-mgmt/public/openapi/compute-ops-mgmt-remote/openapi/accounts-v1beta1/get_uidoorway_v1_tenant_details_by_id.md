---
title: "GET /compute-ops-mgmt/v1beta1/accounts/{id}/tenants"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/accounts-v1beta1/get_uidoorway_v1_tenant_details_by_id.md"
scraped_at: "2026-06-07T06:14:39.798357+00:00Z"
---

# Get list of tenant accounts

Get list of tenant accounts for an MSP account

Endpoint: GET /compute-ops-mgmt/v1beta1/accounts/{id}/tenants
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Application customer ID

## Query parameters:

  - `fields[]` (array)
    Names of fields within the customers. Returns details of all customers for the application customer ID

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

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

  - `items` (array, required)
    Array of tenant account details in the page of the collection.

  - `items.id` (string)
    Primary identifier of a particular account
    Example: "0c3bed66f22211ee8c4e128da47d07ed"

  - `items.accountType` (string)
    The account type of a particular application customer ID.
    Enum: "UNKNOWN", "STANDALONE", "MSP", "TENANT", "BASIC_ORGANIZATION"

  - `items.applicationCustomerId` (string)
    Application customer Id (same as id)
    Example: "0c3bed66f22211ee8c4e128da47d07ed"

  - `items.platformCustomerId` (string)
    Workspace identifier
    Example: "567d21e6c08c11eeb7980ea2e11446eb"

  - `items.mspApplicationCustomerId` (string,null,string,null)
    Application customer Id of a MSP user (if accountType is TENANT)
    Example: "482788de186111ef8efeca97be113755"

  - `items.mspPlatformCustomerId` (string,null,string,null)
    Workspace identifier of a MSP user (if accountType is TENANT)
    Example: "482788de186111ef8efeca97be113755"

  - `items.name` (string)
    Name of the account user
    Example: "msp-test-com"

  - `items.description` (string)
    Description of the account

  - `items.createdAt` (string)
    Time of account creation.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `items.updatedAt` (string)
    Time of the last update to the account
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `items.generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `items.operationalMode` (string)
    Indicates inventory ownership
    Example: "DEFAULT"

  - `items.accountInfo` (object)
    Provides additional account information

  - `items.accountInfo.country` (string)

  - `items.accountInfo.createdAt` (string)

  - `items.accountInfo.updatedAt` (string)

  - `items.accountInfo.countryCode` (string)

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


