---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/service-ports"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4nodeserviceportslist.md"
scraped_at: "2026-06-07T06:16:17.892454+00:00Z"
---

# Get service ports for nodes of all storage systems of HPE Alletra Storage MP B10000 identified by {systemId}

Get service ports for nodes of all storage systems of HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/service-ports
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter systems by Key.
    Example: "ipv4address eq \"169.254.77.160\""

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    uid (Unique identifier) for the service port object
    Example: "f5306b97759d80aab4bb5dcdf28dfff3"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.associatedLinks` (array)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string)
    The cloud connectivity status of the system associated with this resource
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string,null)
    customerId
    Example: "string"

  - `items.domain` (string,null)
    domain of the service port object
    Example: "domain_name"

  - `items.generation` (integer,null)
    generation

  - `items.ipv4address` (string,null)
    ipv4address of the service port object Filter
    Example: "169.254.77.160"

  - `items.ipv6address` (string,null)
    ipv6address of the service port object Filter
    Example: "fe80::cbf3:360d:9ad:996a"

  - `items.ipv6vnetmask` (string,null)
    ipv6 net mask for the service port objectt
    Example: "64"

  - `items.mode` (string,null)
    mode for the service port object
    Example: "Service"

  - `items.name` (string,null)
    display name of the service port object
    Example: "Name_1"

  - `items.node` (string,null)
    node for the service port object
    Example: "0"

  - `items.resourceUri` (string,null)
    resourceUri for detailed service ports object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/nodes/0/serviceports"

  - `items.systemId` (string,null)
    SystemUid/serialNumber of the array.
    Example: "7CE751P312"

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response default fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


