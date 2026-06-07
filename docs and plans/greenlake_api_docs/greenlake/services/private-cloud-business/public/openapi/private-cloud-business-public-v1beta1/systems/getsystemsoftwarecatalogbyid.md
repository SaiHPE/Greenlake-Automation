---
title: "GET /private-cloud-business/v1beta1/system-software-catalogs/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/systems/getsystemsoftwarecatalogbyid.md"
scraped_at: "2026-06-07T06:15:38.438869+00:00Z"
---

# Get the System Software Catalog with specified id.

Returns the system software catalog for the specified id.
Includes versions of the catalog and all constituent software components along with the End User License Agreement
and a list of systems with update path to the corresponding catalog version.

Endpoint: GET /private-cloud-business/v1beta1/system-software-catalogs/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)

## Query parameters:

  - `select` (string)
    A list of properties in the items collection to include in the response.
    Example: "eula,systemsWithUpdatePath"

## Response 200 fields (application/json):

  - `id` (string, required)
    An identifier for the resource, usually a UUID.

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)

  - `updatedAt` (string, required)

  - `resourceUri` (string, required)
    The self reference for this resource.

  - `customerId` (string, required)
    The customer application identifier

  - `eula` (string)
    End User License Agreement for this software catalog

  - `systemsWithUpdatePath` (array)
    List of systems having update path to this software catalog

  - `systemsWithUpdatePath.hypervisorClusters` (array)

  - `systemsWithUpdatePath.hypervisorClusters.hypervisorClusterId` (string)
    Unique Identifier of the Hypervisor Cluster, usually a UUID.

  - `systemsWithUpdatePath.hypervisorClusters.hypervisorClusterName` (string)
    Name of the Hypervisor Cluster.

  - `systemsWithUpdatePath.id` (string)
    Unique Identifier of the system, usually a UUID.

  - `systemsWithUpdatePath.name` (string)
    Name of the system.

  - `name` (string)
    A system specified name for the resource.

  - `hypervisor` (object)
    Details of the hypervisor software.

  - `hypervisor.name` (string)
    Specific name of the software component

  - `hypervisor.releaseDate` (string)
    Release date of the software component

  - `hypervisor.releaseNotesUrl` (string)
    Uniform Resource Locator (URL) of Release Notes for the version of software component

  - `hypervisor.version` (string)
    Version number of the software component

  - `hypervisorManager` (object)
    Details of the hypervisor manager software.

  - `releaseDate` (string)
    Release date of the software catalog

  - `serverFirmware` (object)
    Details of the HPE Server Firmware.

  - `storageConnectionManager` (object)
    Details of the HPE Storage Connection Manager software.

  - `storageSoftware` (object)
    Details of the HPE Storage software.

  - `version` (string)
    Catalog version

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


