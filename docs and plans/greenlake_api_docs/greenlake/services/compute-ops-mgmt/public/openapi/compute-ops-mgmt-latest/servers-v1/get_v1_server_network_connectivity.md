---
title: "GET /compute-ops-mgmt/v1/servers/{id}/tor-port-mappings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_server_network_connectivity.md"
scraped_at: "2026-06-07T06:15:10.893713+00:00Z"
---

# List of adapter to switch port mappings for a server

Retrieve network connectivity of adapter port to connected switch port for a server specified by the id of the server

Endpoint: GET /compute-ops-mgmt/v1/servers/{id}/tor-port-mappings
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique Server identifier
    Example: "P06760-B21+2M212504P8"

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

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
    Primary identifier for the port mapping data given by system

  - `items.type` (string, required)
    Type of the resource

  - `items.generation` (integer, required)
    Monotonically increasing update counter

  - `items.createdAt` (string, required)
    Time of port connectivity information created

  - `items.updatedAt` (string, required)
    Time of port connectivity information updated

  - `items.serverId` (string)
    ID of the server to which this port is associated

  - `items.portMac` (string)
    Server adapter port macaddress

  - `items.clientState` (any)

  - `items.portLastConnectedAt` (string)
    Date and time at which the active traffic was observed last time

  - `items.portConnectivityState` (any)

  - `items.switchPortAdminState` (any)

  - `items.switchPortLinkStatus` (any)

  - `items.switchPort` (string)
    Switch port where server adapter port is connected

  - `items.switchPortSpeed` (string)
    Speed configured on switch port

  - `items.switchPortNativeVlan` (string)
    Native vlan configured on switch port

  - `items.switchPortVlans` (string)
    Vlans configured on siwtch port

  - `items.switchName` (string)
    Switch name

  - `items.switchModel` (string)
    Switch model

  - `items.switchSerialNumber` (string)
    Switch serial number

  - `items.switchStatus` (any)

  - `items.switchSite` (string)
    Site name of the switch

  - `items.switchGroupName` (string)
    Gorup name of the switch

  - `items.switchFwVersion` (string)
    Switch firmware version

  - `items.switchIpAddress` (string)
    Switch IP address

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


