---
title: "GET /compute-ops-mgmt/v1beta1/accounts/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/accounts-v1beta1/get_accounts.md"
scraped_at: "2026-06-07T06:14:57.383276+00:00Z"
---

# Get account details

Retrieve account details by ID.

Endpoint: GET /compute-ops-mgmt/v1beta1/accounts/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Application Customer ID

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `id` (string)
    Primary identifier of a particular account
    Example: "0c3bed66f22211ee8c4e128da47d07ed"

  - `accountType` (string)
    The account type of a particular application customer ID.
    Enum: "UNKNOWN", "STANDALONE", "MSP", "TENANT", "BASIC_ORGANIZATION"

  - `applicationCustomerId` (string)
    Application customer Id (same as id)
    Example: "0c3bed66f22211ee8c4e128da47d07ed"

  - `platformCustomerId` (string)
    Workspace identifier
    Example: "567d21e6c08c11eeb7980ea2e11446eb"

  - `mspApplicationCustomerId` (string,null)
    Application customer Id of a MSP user (if accountType is TENANT)
    Example: "482788de186111ef8efeca97be113755"

  - `mspPlatformCustomerId` (string,null)
    Workspace identifier of a MSP user (if accountType is TENANT)
    Example: "482788de186111ef8efeca97be113755"

  - `name` (string)
    Name of the account user
    Example: "msp-test-com"

  - `description` (string)
    Description of the account

  - `createdAt` (string)
    Time of account creation.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `updatedAt` (string)
    Time of the last update to the account
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `operationalMode` (string)
    Indicates inventory ownership
    Example: "DEFAULT"

  - `accountInfo` (object)
    Provides additional account information

  - `accountInfo.country` (string)

  - `accountInfo.createdAt` (string)

  - `accountInfo.updatedAt` (string)

  - `accountInfo.countryCode` (string)

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


