---
title: "GET /compute-ops-mgmt/v1/servers/{id}/alerts"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/servers-v1/get_v1_server_alerts.md"
scraped_at: "2026-06-07T06:14:52.295737+00:00Z"
---

# List all alerts for a server

Retrieve alert data for a Server specified by the id of the server

Endpoint: GET /compute-ops-mgmt/v1/servers/{id}/alerts
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique Server identifier

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

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

Servers can be filtered by:
  - autoIloFwUpdate
  - biosFamily
  - createdAt
  - deviceClaimType
  - firmwareBundleUri
  - hardware and all nested properties
  - host and all nested properties
  - id
  - lastFirmwareUpdate and all nested properties
  - lastFullInventoryCollectionAt
  - lastFullInventoryCollectionPowerState
  - lastServerLogCollectionAt
  - managedBy
  - name †
  - oneview and all nested properties
  - platformFamily
  - processorVendor
  - resourceUri
  - serverGeneration
  - state and all nested properties

† When searching for a server using the name filter, you must supply the serial number of the server, not the hostname.  To filter by hostname use host/hostname instead of name

The following examples are not an exhaustive list of all possible filtering options.

  - `select` (string)
    Limit the properties of the resource returned in a successful response.  When applied to
write operations, select controls only the properties that are returned, not which
properties are operated on. All properties are returned if the select parameter is omitted.

The value of the select query parameter is a comma separated list of properties to include
in the response. Nested properties use / as a separator, e.g. select=interfaces/name
selects the name property within an interfaces object.

For operations that return paginated collections, select operates on the resources in
the collection. The pagination properties like count and items are always included even
when select is specified.

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

  - `items.id` (string, required)
    Primary identifier for the alert given by the system

  - `items.type` (string, required)
    Type of the resource

  - `items.generation` (integer, required)
    Monotonically increasing update counter

  - `items.createdAt` (string, required)
    Time of alert creation

  - `items.updatedAt` (string, required)
    Time of the last alert update

  - `items.serverId` (string)
    ID of the server to which this alert is associated

  - `items.severity` (string)
    Enum: "OK", "WARNING", "CRITICAL", "UNKNOWN", "NOT_PRESENT", "REDUNDANT", "NON_REDUNDANT"

  - `items.description` (string)

  - `items.resolution` (string)

  - `items.message` (string)

  - `items.timestamp` (string)

  - `items.category` (string)

  - `items.serviceEvent` (boolean)

  - `items.serviceNowIncident` (object)
    ServiceNow incident details. This data will only be available when a ServiceNow incident is created for a service event.

  - `items.serviceNowIncident.id` (string)
    ID of the ServiceNow incident
    Example: "INC0010008"

  - `items.serviceNowIncident.url` (string)
    URL of the ServiceNow incident
    Example: "https://example.service-now.com/api/now/import/u_demo_incident_inbound_api"

  - `items.serviceNowIncident.state` (string)
    State of the ServiceNow incident
    Enum: "CREATION_SUCCESS", "CREATION_IN_PROGRESS", "CREATION_FAILED"

  - `items.caseId` (integer)
    ID of the automatically created HPE Support Case. This will be available only when a HPE Support Case is created for a service event.
    Example: 9815373940

  - `items.caseUrl` (string)
    URL of the automatically created HPE Support Case. This will be available only when a HPE Support Case is created for a service event.
    Example: "https://example.hpe.com/portal/site/hpsc/scm/caseDetails?caseID=9815373940"

  - `total` (integer, required)
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


