---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/enclosures/devicetype7getenclosures.md"
scraped_at: "2026-06-07T06:16:09.015606+00:00Z"
---

# Get all enclosures of a HPE Alletra Storage MP X10000 system

Get all enclosures of a HPE Alletra Storage MP X10000 system

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures
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
    Lucene query to filter Enclosures by Key.
    Example: "id eq 2a0df0fe6f7dc7bb16000000000000000000004007"

  - `sort` (string)
    Data query to sort Enclosure resource by Key.
    Example: "id desc"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier of the Storage system Enclosure. Filter, Sort
    Example: "default.enclosure-0"

  - `items.type` (string, required)
    Type of the resource.
    Example: "enclosure"

  - `items.apiVersion` (string,null)
    API version of the resource.
    Example: "sc.hpe.com/v1"

  - `items.assemblySerialNumber` (string,null)
    The Assembly serial number of the Enclosure.
    Example: "FDBCVFU6578DGF"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.chassisType` (string,null)
    Identifies whether the Enclosure contains computer controllers or is a JBOF. Filter, Sort
    Example: "Node"

  - `items.clusterId` (string,null)
    The unique identifier of the Storage system to which the Enclosure belongs.
    Example: "123abcd4-5e67-890f-g123-4hi5j67kl8m9"

  - `items.clusterRef` (string,null)
    The URI of the Storage system to which the Enclosure belongs.
    Example: "/api/sc.hpe.com/v1/default/enclosures/enclosure-0"

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
    Customer ID for the Storage system Enclosure. Filter, Sort
    Example: "ab1c23456d78901e23fghijk456lm7no"

  - `items.generation` (integer,null)
    Generation. Filter, Sort
    Example: 1692945579

  - `items.kind` (string,null)
    Kind of the resource.
    Example: "Enclosure"

  - `items.partNumber` (string,null)
    The part number of the Enclosure. Filter

  - `items.resourceUri` (string,null)
    Link to the object URI

  - `items.serialNumber` (string,null)
    The serial number of the Enclosure. Filter, Sort
    Example: "AB1234C5D6"

  - `items.status` (object,null)
    The current status of the Enclosure resource.

  - `items.status.aggregateRawStorageCapacity` (integer,null)
    Aggregated Raw Storage capacity.
    Example: 120

  - `items.status.chassisSensors` (array,null)
    The collection of sensors within the Enclosure.

  - `items.status.chassisSensors.displayName` (string,null)
    The Display Name for the sensor.
    Example: "mockDisplayName"

  - `items.status.chassisSensors.enclosureSerial` (string,null)
    Unique identifier for the sensor.

  - `items.status.chassisSensors.iomSerial` (string,null)
    The location of the sensor within the Enclosure.
    Example: "mock"

  - `items.status.chassisSensors.name` (string,null)
    The name of the sensor.
    Example: "mockName"

  - `items.status.chassisSensors.sensorType` (string,null)
    The type of sensor.
    Example: "mokSensorType"

  - `items.status.chassisSensors.status` (string,null)
    The status of the sensor.
    Example: "OK"

  - `items.status.chassisSensors.value` (integer,null)
    The value of the sensor.

  - `items.status.conditions` (array,null)
    Conditions representing recent changes to the state of the Storage system Enclosure resource.

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

  - `items.status.disks` (array,null)
    The collection of disks that are occupying the Enclosure's disk slots.

  - `items.status.disks.capacity` (integer,null)
    The capacity of the disk in Bytes.

  - `items.status.disks.faultLed` (string,null)
    State of faultLED.
    Example: "On"

  - `items.status.disks.firmwareVersion` (string,null)
    Firmware version installed on disk.
    Example: "1.2"

  - `items.status.disks.modelNumber` (string,null)
    The model number of the disk.
    Example: "mock"

  - `items.status.disks.operationalState` (string,null)
    Operational State of disk.
    Example: "Offline"

  - `items.status.disks.position` (string,null)
    Position of disk.
    Example: "0"

  - `items.status.disks.serialNumber` (string,null)
    The serial number of the disk.
    Example: "mock"

  - `items.status.disks.state` (string,null)
    Current state of the disk.
    Example: "Offline"

  - `items.status.fanOverallStatus` (string,null)
    The overall status of the Enclosure's fans.
    Example: "Ok"

  - `items.status.ioModules` (array,null)
    The collection of IOMs within the Enclosure. IoModules details will get populated only for the Node enclosures and for JBOF enclosures it will be empty

  - `items.status.ioModules.name` (string,null)
    Name of IoModules.
    Example: "jbof-0"

  - `items.status.lastModifiedTime` (string,null)
    UTC Time at which the status of this Storage system Enclosure was last updated.
    Example: "2023-08-24T07:14:33Z"

  - `items.status.locatorLedState` (string,null)
    The desired state of the locator LED on the Enclosure.
    Example: "Off"

  - `items.status.logicalClusterSerialNumber` (string)
    10-digit identifier. This can serve as alternate Key for the resource. The value is fixed and immutable.
    Example: "ABGFDYRKJ1"

  - `items.status.psuOverallStatus` (string,null)
    The overall status of the power supplies in the Enclosure.
    Example: "Ok"

  - `items.status.ready` (boolean,null)
    Status.
    Example: true

  - `items.status.tempOverallStatus` (string,null)
    The overall status of the Enclosure's temperature.
    Example: "Ok"

  - `items.systemId` (string,null)
    Identifier of the Storage system to which the Enclosure belongs. Filter, Sort
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


