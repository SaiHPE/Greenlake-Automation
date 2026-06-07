---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-connectors"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/shelves/devicetype4enclosureconnectorlist.md"
scraped_at: "2026-06-07T06:15:58.036778+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Enclosure Connectors identified by {enclosureId}

Get details of HPE Alletra Storage MP B10000 Enclosure Connectors identified by {enclosureId}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-connectors
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `enclosureId` (string, required)
    UID of the enclosure
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter enclosure resource by Key.
    Example: "systemWWN eq 2FF70002AC018D94"

  - `sort` (string)
    oData query to sort enclosure resource by Key.
    Example: "systemWWN desc"

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
    Unique Identifier of the resource. Filter
    Example: "id"

  - `items.type` (string, required)
    Resource Type for the enclosure connector
    Example: "type1"

  - `items.associatedLinks` (array,null)
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

  - `items.connector` (integer,null)
    Connector on slot on IOM in Cage for connection

  - `items.currentSpeed` (string,null)
    Current speed of connection
    Example: "currentSpeed"

  - `items.customerId` (string,null)
    customerId
    Example: "string"

  - `items.disabled` (string,null)
    Disabled for connection
    Example: "disabled"

  - `items.displayname` (string,null)
    Name to be used for display purposes
    Example: "display name"

  - `items.domain` (string,null)
    Domain that the resource belongs to

  - `items.elementStatusCode` (object,null)

  - `items.elementStatusCode.default` (string,null)
    Text in the default language

  - `items.elementStatusCode.key` (string,null)
    Key of the message in the i18n catalog

  - `items.enclosureCardId` (integer,null)
    ID of the enclosure card

  - `items.enclosureCardPciUid` (string,null)
    UID of the enclosure card PCI card
    Example: "PCIUID"

  - `items.enclosureCardUid` (string,null)
    Unique Identifier of the enclosure card
    Example: "CardUID"

  - `items.enclosureId` (integer,null)
    ID of the enclosure

  - `items.enclosureName` (string,null)
    Name of the enclosure.
    Example: "name"

  - `items.enclosureUid` (string,null)
    Unique Identifier of the enclosure
    Example: "uid"

  - `items.generation` (integer,null)
    generation Filter, Sort

  - `items.ipv4Address` (string,null)
    ip v4 address of connection
    Example: "ipv4"

  - `items.ipv6Address` (string,null)
    ip v6 address of connection
    Example: "ipv6"

  - `items.label` (string,null)
    Connection label
    Example: "label"

  - `items.linkSpeed` (string,null)
    Link speed for connection
    Example: "speed"

  - `items.locate` (string,null)
    Locate for connection
    Example: "locate"

  - `items.macAddress` (string,null)
    mac address of connection
    Example: "mac"

  - `items.nodePort` (object,null)
    It includes node number, slot number, and port number

  - `items.nodePort.node` (integer,null)
    Example: 1

  - `items.nodePort.port` (integer,null)
    Example: 1

  - `items.nodePort.slot` (integer,null)
    Example: 1

  - `items.resourceUri` (string,null)
    resourceUri for detailed enclosure connector object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/enclosures/9c3c4f29a82fd8d632ff379116fa0b8f/enclosure-connectors/8621946048c1cb24bdfc57e9b3b460ac"

  - `items.slot` (integer,null)
    Slot on IOM in Cage for connection

  - `items.systemId` (string)
    Id of the array
    Example: "4UW0004156"

  - `items.typeConnection` (string,null)
    Type of connection
    Example: "External"

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


