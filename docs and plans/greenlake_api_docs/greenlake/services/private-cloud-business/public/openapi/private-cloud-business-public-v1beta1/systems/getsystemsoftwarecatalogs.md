---
title: "GET /private-cloud-business/v1beta1/system-software-catalogs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/systems/getsystemsoftwarecatalogs.md"
scraped_at: "2026-06-07T06:15:38.255328+00:00Z"
---

# Get all System Software Catalogs.

Returns a list of all system software catalogs.
Use 'select' and 'filter' query parameters to customize the response returned by this API.
For example, to get the End User License Agreement (EULA) for catalog version 1.2.3.4, use '?select=eula&filter=version eq 1.2.3.4'. 
To get recommended systems for precheck to a given catalog version, use '?select=systemsWithUpdatePath&filter=version eq 1.2.3.4'.

Endpoint: GET /private-cloud-business/v1beta1/system-software-catalogs
Version: 1.1.0
Security: bearer

## Query parameters:

  - `select` (string)
    A list of properties in the items collection to include in the response.
    Example: "eula,systemsWithUpdatePath"

  - `filter` (string)
    The expression to filter responses.
The property names which are of type string should be passed in quotes('') and nested property names should be passed with "/" as the separator.
Filtering is supported with following properties:
 * eula
 * createdAt
 * customerId
 * generation
 * id
 * name
 * resourceUri
 * type
 * updatedAt
 * hypervisor/name
 * hypervisor/releaseDate
 * hypervisor/releaseNotesUrl
 * hypervisor/version
 * releaseDate
 * serverFirmware/name
 * serverFirmware/releaseDate
 * serverFirmware/releaseNotesUrl
 * serverFirmware/version
 * storageConnectionManager/name
 * storageConnectionManager/releaseDate
 * storageConnectionManager/releaseNotesUrl
 * storageConnectionManager/version
 * storageSoftware/name
 * storageSoftware/releaseDate
 * storageSoftware/releaseNotesUrl
 * storageSoftware/version
 * version
    Example: "hypervisor/name eq 'ESXi'"

  - `limit` (integer)
    Use limit in conjunction with offset for paging, e.g.: offset=30&&limit=10. Limit is the maximum number of items to include in the response.
    Example: 10

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    An identifier for the resource, usually a UUID.

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)

  - `items.updatedAt` (string, required)

  - `items.resourceUri` (string, required)
    The self reference for this resource.

  - `items.customerId` (string, required)
    The customer application identifier

  - `items.eula` (string)
    End User License Agreement for this software catalog

  - `items.systemsWithUpdatePath` (array)
    List of systems having update path to this software catalog

  - `items.systemsWithUpdatePath.hypervisorClusters` (array)

  - `items.systemsWithUpdatePath.hypervisorClusters.hypervisorClusterId` (string)
    Unique Identifier of the Hypervisor Cluster, usually a UUID.

  - `items.systemsWithUpdatePath.hypervisorClusters.hypervisorClusterName` (string)
    Name of the Hypervisor Cluster.

  - `items.systemsWithUpdatePath.id` (string)
    Unique Identifier of the system, usually a UUID.

  - `items.systemsWithUpdatePath.name` (string)
    Name of the system.

  - `items.name` (string)
    A system specified name for the resource.

  - `items.hypervisor` (object)
    Details of the hypervisor software.

  - `items.hypervisor.name` (string)
    Specific name of the software component

  - `items.hypervisor.releaseDate` (string)
    Release date of the software component

  - `items.hypervisor.releaseNotesUrl` (string)
    Uniform Resource Locator (URL) of Release Notes for the version of software component

  - `items.hypervisor.version` (string)
    Version number of the software component

  - `items.hypervisorManager` (object)
    Details of the hypervisor manager software.

  - `items.releaseDate` (string)
    Release date of the software catalog

  - `items.serverFirmware` (object)
    Details of the HPE Server Firmware.

  - `items.storageConnectionManager` (object)
    Details of the HPE Storage Connection Manager software.

  - `items.storageSoftware` (object)
    Details of the HPE Storage software.

  - `items.version` (string)
    Catalog version

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

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

## Response 404 fields (application/json):

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


