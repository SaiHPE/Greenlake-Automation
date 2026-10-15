---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/jbofioms"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/jbofioms/devicetype7getjbofioms.md"
scraped_at: "2026-06-07T06:16:09.802887+00:00Z"
---

# Get all JBOF IOMs of a HPE Alletra Storage MP X10000 system

Get all JBOF IOMs of a HPE Alletra Storage MP X10000 system

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/jbofioms
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the storage system
    Example: "2a0df0fe6f7dc7bb16000000000000000000004817"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `filter` (string)
    Lucene query to filter JBOF IOMs by Key.
    Example: "id eq 2a0df0fe6f7dc7bb16000000000000000000004007"

  - `sort` (string)
    Data query to sort JBOF IOM resource by Key.
    Example: "id desc"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier of the Storage system JBOF IOM. Filter, Sort
    Example: "default.jbofiom-0"

  - `items.type` (string, required)
    Type of the resource.
    Example: "jbofiom"

  - `items.apiVersion` (string,null)
    API version of the resource.
    Example: "sc.hpe.com/v1"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.clusterId` (string,null)
    The unique identifier of the resource to which the JBOF IOM belongs.
    Example: "123abcd4-5e67-890f-g123-4hi5j67kl8m9"

  - `items.clusterRef` (string,null)
    The URI of the resource to which the JBOF IOM belongs.
    Example: "/api/sc.hpe.com/v1/default/jbofioms/jbofiom-0"

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the resource belongs
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string,null)
    Customer ID for the Storage system JBOF IOM. Filter, Sort
    Example: "ab1c23456d78901e23fghijk456lm7no"

  - `items.enclosureId` (string,null)
    Unique ID of the enclosure that contains this JBOF IOM.
    Example: "123abcd4-5e67-890f-g123-4hi5j67kl8m9"

  - `items.enclosureRef` (string,null)
    The URI of the enclosure to which the JBOF IOM belongs.
    Example: "/api/sc.hpe.com/v1/default/jbofiom-1/Enclosure"

  - `items.enclosureSerialNumber` (string,null)
    Serial number of the enclosure that contains this JBOF IOM. Filter
    Example: "1AB234C5D6"

  - `items.generation` (integer,null)
    Generation. Filter, Sort
    Example: 1692945579

  - `items.ipAddresses` (array,null)
    List of IP Addresses.

  - `items.kind` (string,null)
    Kind of the resource.
    Example: "Jbofiom"

  - `items.location` (string,null)
    location of the resource in enclosure.
    Example: "0"

  - `items.partNumber` (string,null)
    The part number of the JBOF IOM. Filter

  - `items.resourceUri` (string,null)
    Link to the object URI

  - `items.serialNumber` (string,null)
    The serial number of the JBOF IOM. Filter, Sort
    Example: "AB1234C5D6"

  - `items.status` (object,null)
    The current status of the JBOF IOM resource.

  - `items.status.conditions` (array,null)
    Conditions representing recent changes to the state of the Storage system JBOF IOM resource.

  - `items.status.conditions.lastTransitionTime` (string,null)
    Time of the last event.
    Example: "2023-08-24T07:14:03Z"

  - `items.status.conditions.message` (string,null)
    Describes the transition state.
    Example: "Successfully created and assigned to the resource"

  - `items.status.conditions.observedGeneration` (integer,null)
    Observed Generation.
    Example: 2

  - `items.status.conditions.reason` (string,null)
    Contains a programmatic identifier indicating the reason for the condition's last transition.
    Example: "SuccessfulCreate"

  - `items.status.conditions.status` (string,null)
    Status of the event.
    Example: "True"

  - `items.status.conditions.type` (string)
    Type of condition.
    Example: "Assigned"

  - `items.status.faultLedState` (string,null)
    The current state of the Fault LED.
    Example: "Off"

  - `items.status.healthLedState` (string,null)
    The current state of the Health LED.
    Example: "Off"

  - `items.status.lastModifiedTime` (string,null)
    UTC Time at which the status of this Storage system JBOF IOM was last updated.
    Example: "2023-08-24T07:14:33Z"

  - `items.status.locatorLedState` (string,null)
    The current state of the Locator LED.
    Example: "Off"

  - `items.status.nics` (array,null)
    The status of the NICs in the IOM.

  - `items.status.nics.operationalState` (string,null)
    The current operational state of the IOM.
    Example: "Offline"

  - `items.status.nics.ports` (array,null)
    The status of the ports in this NIC.

  - `items.status.nics.ports.macAddress` (string,null)
    MAC Address
    Example: "AA:BB:CC:88:C9:E3"

  - `items.status.nics.ports.operationalState` (string,null)
    Operational state
    Example: "Offline"

  - `items.status.nics.slotNumber` (integer,null)
    The slot number of the NIC.

  - `items.status.pingsOutstanding` (integer,null)
    Outstanding Pings.
    Example: 3

  - `items.status.powerState` (string,null)
    Power state of the IOM.
    Example: "Off"

  - `items.status.ready` (boolean,null)
    Used to determine when a controller has brought its resource into compliance with the specification.
    Example: true

  - `items.status.sevenSegmentDisplay` (integer,null)
    The value to display on the three digit seven segment display.

  - `items.systemId` (string,null)
    Identifier of the Storage system to which the JBOF IOM belongs. Filter, Sort
    Example: "1AB234CDEF"

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


