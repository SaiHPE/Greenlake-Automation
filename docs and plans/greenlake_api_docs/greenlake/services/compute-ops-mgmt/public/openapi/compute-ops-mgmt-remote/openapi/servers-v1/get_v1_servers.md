---
title: "GET /compute-ops-mgmt/v1/servers"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/servers-v1/get_v1_servers.md"
scraped_at: "2026-06-07T06:14:51.595400+00:00Z"
---

# List all servers

Retrieve data for all Servers

Servers without a valid subscription will not return the following:
  - hardware.health
  - hardware.memoryMb
  - hardware.formFactor
  - hardware.bmc
  - hardware.platform
  - hardware.powerState
  - hardware.indicatorLed
  - firmwareInventory
  - softwareInventory
  - lastFirmwareUpdate
  - host
  - firmwareBundleUri
  - tags
  - originIp
  - biosFamily
  - storageInventory
  - processorVendor
  - autoIloFwupdate
  - serverGeneration
  - connectionType
  - oneview

Endpoint: GET /compute-ops-mgmt/v1/servers
Version: latest
Security: Bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Server IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

Servers can be filtered by:
  - autoIloFwUpdate
  - biosFamily
  - createdAt
  - deviceClaimType
  - firmwareBundleUri
  - hardware and all nested properties
  - host and all nested properties
  - id
  - lastFirmwareUpdate and all nested properties
  - lastFullInventoryCollectionAt
  - lastFullInventoryCollectionPowerState
  - lastServerLogCollectionAt
  - managedBy
  - name †
  - oneview and all nested properties
  - platformFamily
  - processorVendor
  - resourceUri
  - serverGeneration
  - state and all nested properties

† When searching for a server using the name filter, you must supply the serial number of the server, not the hostname.  To filter by hostname use host/hostname instead of name

The following examples are not an exhaustive list of all possible filtering options.

  - `select` (string)
    Limit the properties of the resource returned in a successful response.  When applied to
write operations, select controls only the properties that are returned, not which
properties are operated on. All properties are returned if the select parameter is omitted.

The value of the select query parameter is a comma separated list of properties to include
in the response. Nested properties use / as a separator, e.g. select=interfaces/name
selects the name property within an interfaces object.

For operations that return paginated collections, select operates on the resources in
the collection. The pagination properties like count and items are always included even
when select is specified.

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

  - `items.id` (string)
    Primary identifier for the server given by the system

  - `items.name` (string)
    Name given to resource
    Example: "myServer"

  - `items.type` (string)
    Type of the resource

  - `items.resourceUri` (string)
    URI to the server itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1/servers/875765-S01+1M512501AB"

  - `items.generation` (integer)
    Monotonically increasing update counter

  - `items.createdAt` (string)
    Time of server creation

  - `items.updatedAt` (string)
    Time of the last server update

  - `items.platformFamily` (any)

  - `items.serverGeneration` (string,string)
    Server Hardware Generation
    Enum: "GEN_8", "GEN_9", "GEN_10", "GEN_11", "GEN_12", "UNKNOWN"

  - `items.hardware` (object)
    Server hardware details

  - `items.hardware.serialNumber` (string)

  - `items.hardware.model` (string,null,string,null)

  - `items.hardware.uuid` (string,null,string,null)

  - `items.hardware.productId` (string)

  - `items.hardware.powerState` (string)
    This will be a mix of power states and reset types.
    Enum: "UNKNOWN", "ON", "OFF", "POWERING_ON", "POWERING_OFF", "RESET"

  - `items.hardware.indicatorLed` (string)
    Enum: "UNKNOWN", "LIT", "BLINKING", "OFF"

  - `items.hardware.health` (object,null,object,null)
    Server health details

  - `items.hardware.health.summary` (string)
    Calculated summary of the overall health
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.fans` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.fanRedundancy` (string)
    Redundancy state
    Enum: "NON_REDUNDANT", "REDUNDANT", "FAILED_REDUNDANT", "NOT_PRESENT", "UNKNOWN"

  - `items.hardware.health.liquidCooling` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.liquidCoolingRedundancy` (string)
    Redundancy state
    Enum: "NON_REDUNDANT", "REDUNDANT", "FAILED_REDUNDANT", "NOT_PRESENT", "UNKNOWN"

  - `items.hardware.health.memory` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.network` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.powerSupplies` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.powerSupplyRedundancy` (string)
    Redundancy state
    Enum: "NON_REDUNDANT", "REDUNDANT", "FAILED_REDUNDANT", "NOT_PRESENT", "UNKNOWN"

  - `items.hardware.health.processor` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.storage` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.temperature` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.bios` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.smartStorage` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.healthLED` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.health.airFilter` (string)
    Health state of the air filter
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `items.hardware.platform` (any)

  - `items.hardware.formFactor` (any)

  - `items.hardware.bmc` (object,null,object,null)
    iLO BMC details

  - `items.hardware.bmc.mac` (string)

  - `items.hardware.bmc.ip` (string)

  - `items.hardware.bmc.hostname` (string)

  - `items.hardware.bmc.license` (any)

  - `items.hardware.bmc.version` (any)

  - `items.hardware.bmc.userDefined` (object,null,object,null)
    User defined properties for a credential via secure gateway connection

  - `items.hardware.bmc.userDefined.host` (string)
    IP address or the BMC

  - `items.hardware.bmc.userDefined.username` (string)
    Username used to access the BMC

  - `items.hardware.bmc.userDefined.password` (string)
    Password used to access the BMC

  - `items.hardware.bmc.userDefined.certificateFingerprint` (string)
    Certificate fingerprint of the BMC

  - `items.hardware.memoryMb` (any)

  - `items.hardware.manufacturer` (string)
    Manufacturer of the server hardware

  - `items.state` (object)
    Server connectivity state

  - `items.state.managed` (boolean)

  - `items.state.connected` (boolean)

  - `items.state.connectedModifiedAt` (string,null,string,null)

  - `items.state.subscriptionState` (string)
    Subscription State
    Enum: "REQUIRED", "SUBSCRIBED", "EXPIRED"

  - `items.state.subscriptionTier` (any)

  - `items.state.subscriptionExpiresAt` (string,null,string,null)
    Subscription validity end date

  - `items.state.subscriptionKey` (string,null,string,null)
    GreenLake subscription licence key assigned to the server
    Example: "ABCDE12345F"

  - `items.firmwareInventory` (array,null,array,null)
    Firmware Inventory

  - `items.firmwareInventory.name` (string)

  - `items.firmwareInventory.deviceContext` (string)

  - `items.softwareInventory` (array,null,array,null)
    Software Inventory

  - `items.firmwareBundleUri` (string,null,string,null)

  - `items.lastFirmwareUpdate` (object,null,object,null)
    Details of the last firmware update

  - `items.lastFirmwareUpdate.status` (string)
    Status of the last firmware update
    Enum: "OK", "FAILED", "SKIPPED", "NOT_UPDATED"

  - `items.lastFirmwareUpdate.attemptedAt` (string)
    Date on which the last firmware update job was attempted
    Example: "2024-06-01T10:00:00.000000+00:00"

  - `items.lastFirmwareUpdate.attemptedBaselineUri` (string,null,string,null)
    URI of the firmware baseline used in the last firmware update attempt
    Example: "/compute-ops-mgmt/v1/firmware-bundles/abc123"

  - `items.lastFirmwareUpdate.installSwDrivers` (boolean,null,boolean,null)
    Whether software drivers were included in the firmware update

  - `items.lastFirmwareUpdate.downgrade` (boolean,null,boolean,null)
    Whether a firmware downgrade was permitted in the update

  - `items.lastFirmwareUpdate.powerOff` (boolean,null,boolean,null)
    Whether the server was powered off after the firmware update completed

  - `items.lastFirmwareUpdate.completedAt` (string,null,string,null)
    Date on which the last firmware update completed
    Example: "2024-06-01T10:45:00.000000+00:00"

  - `items.lastFirmwareUpdate.bundleUpdateMethod` (string,null,string,null)
    Method used to apply the firmware bundle
    Enum: "Update", "Stage"

  - `items.lastFirmwareUpdate.firmwareInventoryUpdates` (array)
    List of the components updated by the last firmware update

  - `items.lastFirmwareUpdate.firmwareInventoryUpdates.name` (string)
    Name of the firmware component that was updated

  - `items.lastFirmwareUpdate.firmwareInventoryUpdates.version` (string)
    Version of the firmware that the component was updated to

  - `items.lastFirmwareUpdate.firmwareInventoryUpdates.status` (string)
    Status of the firmware update
    Enum: "OK", "FAILED", "SKIPPED", "NOT_UPDATED"

  - `items.tags` (object,null,object,null)
    Extra identifiers a server
    Example: {"location":"San Jose"}

  - `items.processorVendor` (string,null,string,null)
    Type and brand of processor
    Example: "Intel(R) Xeon(R) Silver 4114 CPU @ 2.20GHz"

  - `items.biosFamily` (string,null,string,null)
    Bios version

  - `items.host` (object,null,object,null)
    host details

  - `items.host.osName` (string,null,string,null)

  - `items.host.osVersion` (string,null,string,null)

  - `items.host.osDescription` (string,null,string,null)

  - `items.host.osType` (integer,null,integer,null)

  - `items.autoIloFwUpdate` (boolean)
    To opt in for automatic iLO-only firmware update

  - `items.oneview` (object,null,object,null)
    Details of the OneView managed server

  - `items.oneview.applianceUri` (string)

  - `items.oneview.maintenanceMode` (boolean)
    True if the server is in maintenance mode, false otherwise

  - `items.oneview.name` (string)
    Name of the server in OneView

  - `items.oneview.state` (string)
    Current resource state of the server hardware

  - `items.lastFullInventoryCollectionAt` (any)

  - `items.lastFullInventoryCollectionPowerState` (string)
    Power state of the server when the complete inventory is collected

  - `items.deviceClaimType` (string,null,string,null)
    Method by which the server was claimed and added to the system
    Enum: "ZTP", "MANUAL", "MAGICLINK", "UNKNOWN"

  - `items.connectionType` (string,null,string,null)
    How the server connects to Compute Ops Management.
    Enum: "DIRECT", "ONEVIEW", "GATEWAY", "CREDENTIAL"

  - `items.managedBy` (string,null,string,null)
    Name of a third-party system that manages this server, if applicable (e.g. "Nutanix"). Null if the server is not managed by a known third-party system.
    Example: "Nutanix"

  - `items.lastServerLogCollectionAt` (string,null,string,null)
    Timestamp of the last server log (AHS) collection
    Example: "2024-06-01T12:00:00.000000+00:00"

  - `items.appliance` (object,null,object,null)
    Details of the appliance (OneView or Secure Gateway) through which this server is connected. Null values when the server connects directly.

  - `items.appliance.applianceUri` (string,null,string,null)
    URI of the appliance resource through which the server is connected. For OneView-connected servers this references an /compute-ops-mgmt/v1beta1/appliances/oneview+{id} resource; for gateway-connected servers it references an /compute-ops-mgmt/v1beta1/appliances/gateway+{id} resource.
    Example: "/compute-ops-mgmt/v1beta1/appliances/oneview+47f4ca46-462d-47fc-9458-a2d97db49a0c"

  - `items.appliance.applianceId` (string,null,string,null)
    UUID of the appliance through which the server is connected
    Example: "47f4ca46-462d-47fc-9458-a2d97db49a0c"

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


