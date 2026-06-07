---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-connectors/{enclosureConnectorId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosureconnectorsgetbyid.md"
scraped_at: "2026-06-07T06:16:11.680642+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Enclosure Connector identified by {enclosureId} and {enclosureConnectorId}

Get details of HPE Alletra Storage MP B10000 Enclosure Connector identified by {enclosureId} and {enclosureConnectorId}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-connectors/{enclosureConnectorId}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `enclosureId` (string, required)
    UID of the enclosure
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `enclosureConnectorId` (string, required)
    UID of the enclosure connector
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Identifier of the resource
    Example: "uid"

  - `type` (string, required)
    Type of connection
    Example: "type1"

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string)
    The cloud connectivity status of the system associated with this resource
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `connector` (integer,null)
    Connector on slot on IOM in Cage for connection

  - `currentSpeed` (string,null)
    Current speed of connection
    Example: "currentSpeed"

  - `customerId` (string,null)
    customerId
    Example: "string"

  - `disabled` (string,null)
    Disabled for connection
    Example: "disabled"

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "display name"

  - `domain` (string,null)
    Domain that the resource belongs to

  - `elementStatusCode` (object,null)

  - `elementStatusCode.default` (string,null)
    Text in the default language

  - `elementStatusCode.key` (string,null)
    Key of the message in the i18n catalog

  - `enclosureCardId` (integer,null)
    ID of the enclosure card

  - `enclosureCardPciUid` (string,null)
    UID of the enclosure card PCI card
    Example: "PCIUID"

  - `enclosureCardUid` (string,null)
    Unique Identifier of the enclosure card
    Example: "CardUID"

  - `enclosureId` (integer,null)
    ID of the enclosure

  - `enclosureName` (string,null)
    Name of the enclosure.
    Example: "name"

  - `enclosureUid` (string,null)
    Unique Identifier of the enclosure.
    Example: "uid"

  - `generation` (integer,null)
    generation

  - `ipv4Address` (string,null)
    ip v4 address of connection
    Example: "ipv4"

  - `ipv6Address` (string,null)
    ip v6 address of connection
    Example: "ipv6"

  - `label` (string,null)
    Connection label
    Example: "label"

  - `linkSpeed` (string,null)
    Link speed for connection
    Example: "speed"

  - `locate` (string,null)
    Locate for connection
    Example: "locate"

  - `macAddress` (string,null)
    mac address of connection
    Example: "mac"

  - `nodePort` (object,null)
    It includes node number, slot number, and port number

  - `nodePort.node` (integer,null)
    Example: 1

  - `nodePort.port` (integer,null)
    Example: 1

  - `nodePort.slot` (integer,null)
    Example: 1

  - `resourceUri` (string,null)
    resourceUri for detailed enclosure connector object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/enclosures/9c3c4f29a82fd8d632ff379116fa0b8f/enclosure-connectors/8621946048c1cb24bdfc57e9b3b460ac"

  - `slot` (integer,null)
    Slot on IOM in Cage for connection

  - `systemId` (string)
    Id of the array
    Example: "4UW0004156"

  - `typeConnection` (string,null)
    Type of connection
    Example: "External"

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


