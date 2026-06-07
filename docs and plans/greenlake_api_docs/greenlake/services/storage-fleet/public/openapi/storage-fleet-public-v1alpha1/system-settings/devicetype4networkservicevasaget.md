---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4networkservicevasaget.md"
scraped_at: "2026-06-07T06:16:05.780170+00:00Z"
---

# Get VASA Network-Service details for a storage system Primera / Alletra 9K

Get VASA Network-Service details for a storage system Primera / Alletra 9K

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa
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

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Unique Identifier of the resource
    Example: "8be9321600cbf18e9c8c96bb3217f610"

  - `items.type` (string, required)
    The type of resource.
    Example: "vasa-settings"

  - `items.certDetails` (array,null)
    A list of certificates associated with the VASA service

  - `items.certDetails.retainFlag` (boolean,null)
    Flag of the vasa certificate
    Example: true

  - `items.certDetails.subject` (string,null)
    Subject of the vasa certificate
    Example: "VASA CERTIFICATE"

  - `items.certDetails.thumbprint` (string,null)
    Thumbprint of the vasa certificate
    Example: "afiuqnfiqf"

  - `items.certDetails.vcGuid` (string,null)
    vcGuid of the vasa certificate
    Example: "0983rhifh9q83rh9"

  - `items.certMgmt` (object,null)
    Certificate management mode of the VASA Provider

  - `items.certMgmt.default` (string,null)
    Text in the default language
    Example: "server"

  - `items.certMgmt.key` (string,null)
    Key of the message
    Example: "VASA_CERTMGMT_MODE-1"

  - `items.certSubject` (string,null)
    Certificate subject of the VASA Provider
    Example: "Unknown"

  - `items.certThumbprint` (string,null)
    Certificate thumbprint of the VASA Provider
    Example: "Unknown"

  - `items.cfgList` (array,null)
    A list of key/value pairs describing the configuration of the VASA service

  - `items.cfgList.key` (string,null)
    Key of the vasa configuration
    Example: "VASA_CPG_MODE-1"

  - `items.cfgList.value` (string,null)
    Value of the vasa key configuration
    Example: "VASA_CPG_VALUE"

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
    Example: "fc5f41652a53497e88cdcebc715cc1xz"

  - `items.enabled` (boolean,null)
    Indicates if the service status is enabled or not

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627538867363

  - `items.httpsEnabled` (boolean,null)
    Indicates if the vasa https state is enabled or not
    Example: true

  - `items.httpsPort` (integer,null)
    Vasa https port number
    Example: 9997

  - `items.memUsageMiB` (integer,null)
    Memory usage of the VASA provider
    Example: 134

  - `items.moreUris` (array,null)
    List of VASA Service URLs

  - `items.moreUris.isValid` (integer,null)
    Specifies whether VASA Service URL is valid or not
    Example: 1

  - `items.moreUris.node` (integer,null)
    Specifies the nodeId of the VASA service URL. Applicable from HPE Alletra Storage MP B10000 10.5.0 OS version and later.
    Example: 1

  - `items.moreUris.uri` (string,null)
    VASA Service URL
    Example: "https://xppa6614.in.rdlabs.hpecorp.net:9997/vasa"

  - `items.moreUris.uriStatus` (string,null)
    The status of VASA service at the URL level. Applicable from HPE Alletra Storage MP B10000 10.4.2 OS version and later.
    Example: "Running"

  - `items.serverName` (string,null)
    Name of the vasa server
    Example: "xppa6614.in.rdlabs.hpecorp.net"

  - `items.serviceStatus` (string,null)
    The status of VASA service.

  - `items.systemId` (string,null)
    SystemId of the storage system
    Example: "4UW0001540"

  - `items.systemWwn` (string,null)
    WWN of the array
    Example: "2FF70002AC018D94"

  - `items.version` (string,null)
    Version of the VASA provider
    Example: "4.0.9.1"

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


