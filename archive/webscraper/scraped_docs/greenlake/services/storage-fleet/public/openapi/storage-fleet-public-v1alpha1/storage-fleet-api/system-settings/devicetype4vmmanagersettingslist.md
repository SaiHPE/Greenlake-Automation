---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4vmmanagersettingslist.md"
scraped_at: "2026-06-07T06:16:20.156010+00:00Z"
---

# Get vCenter settings for an HPE Alletra Storage MP B10000 storage system

Get vCenter settings for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Unique identifier of the vcenter settings.
    Example: "c0e4e72b-c9d3-54a4-312f-4ec0f8da498a"

  - `items.type` (string, required)
    The type of resource.
    Example: "vm-manager-settings"

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

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1ce"

  - `items.description` (string,null)
    Vcenter description
    Example: "sample vcenter description"

  - `items.friendlyCert` (object,null)
    Certificate detail in readable format

  - `items.friendlyCert.issuedTo` (string,null)
    Name of the certificate issued to
    Example: "15.213.64.88"

  - `items.friendlyCert.issuer` (string,null)
    Name of Certificate issued to
    Example: "CA"

  - `items.friendlyCert.validFrom` (object,null)
    The validity of the certificates

  - `items.friendlyCert.validFrom.ms` (integer,null)
    Epoch time in milliseconds
    Example: 1591601529000

  - `items.friendlyCert.validFrom.tz` (string,null)
    Time zone name
    Example: "Local"

  - `items.friendlyCert.validUntil` (object,null)
    The validity of the certificates

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627540916540

  - `items.inetaddress` (string,null)
    Address of the vcenter.
    Example: "18.218.214.244"

  - `items.name` (string,null)
    Name of vcenter.
    Example: "sample_vc_name"

  - `items.port` (integer,null)
    port number of vcenter.
    Example: 443

  - `items.resourceUri` (string,null)
    resourceUri for detailed vcenter setting object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE809P009/vm-manager-settings/centerid123"

  - `items.status` (object,null)
    Status of the vcenter setting

  - `items.status.default` (string,null)
    Default status value
    Example: "Ok"

  - `items.status.key` (string,null)
    Status key of vcenter
    Example: "VMPERF_FAILED"

  - `items.systemId` (string)
    SystemID of the array
    Example: "7CE809P009"

  - `items.username` (string,null)
    User of the vcenter configured
    Example: "SysAdmin@machine.local"

  - `items.vmManagerType` (string,null)
    Type of the vmmanager settings.
    Example: "hyperV"

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


