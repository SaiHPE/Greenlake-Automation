---
title: "GET /compute-ops-mgmt/v1beta1/oneview-server-templates/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/oneview-server-templates-v1beta1/get_v1beta1_oneview_server_templates_by_templateid.md"
scraped_at: "2026-06-07T06:14:49.227546+00:00Z"
---

# Get a OneView server template by template id

Get a specific OneView server template by template id.

Endpoint: GET /compute-ops-mgmt/v1beta1/oneview-server-templates/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique identifier of OneView server template

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `createdAt` (string)
    Time of OneView server template creation

  - `description` (string)
    Description of the oneview server template
    Example: "Server profile template"

  - `id` (string)
    Primary identifier for the OneView server template given by system

  - `applianceId` (string)
    Primary identifier for the appliance where OneView server template is created

  - `applianceName` (string)
    Name of the appliance where OneView server template is created
    Example: "devcat-dhcp-cent77-53"

  - `name` (string)
    Name of OneView server template
    Example: "Server_profile_template"

  - `uri` (string)
    URI of the server template in the OneView
    Example: "/rest/server-profile-templates/a56e80bc-6ee4-4414-82e7-36dc7f79a62e"

  - `attributes` (object)
    Representation of the OneView server-profile-template REST resource

  - `status` (string)
    Health status of the resource
    Example: "OK"

  - `state` (string,null)
    Current state of the resource

  - `subscription` (string,null)
    Subscription of the source appliance

  - `type` (string)
    Type of the resource

  - `updatedAt` (string)
    Time of last server template modified

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


