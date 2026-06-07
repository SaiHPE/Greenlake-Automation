---
title: "GET /compute-ops-mgmt/v1/servers/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/servers-v1/get_v1_server_by_id.md"
scraped_at: "2026-06-07T06:14:51.894301+00:00Z"
---

# Get a server

Retrieve data for a Server specified by its id

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

Endpoint: GET /compute-ops-mgmt/v1/servers/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique Server identifier

## Query parameters:

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

  - `id` (string)
    Primary identifier for the server given by the system

  - `name` (string)
    Name given to resource
    Example: "myServer"

  - `type` (string)
    Type of the resource

  - `resourceUri` (string)
    URI to the server itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1/servers/875765-S01+1M512501AB"

  - `generation` (integer)
    Monotonically increasing update counter

  - `createdAt` (string)
    Time of server creation

  - `updatedAt` (string)
    Time of the last server update

  - `platformFamily` (any)

  - `serverGeneration` (string)
    Server Hardware Generation
    Enum: "GEN_8", "GEN_9", "GEN_10", "GEN_11", "GEN_12", "UNKNOWN"

  - `hardware` (object)
    Server hardware details

  - `hardware.serialNumber` (string)

  - `hardware.model` (string,null)

  - `hardware.uuid` (string,null)

  - `hardware.productId` (string)

  - `hardware.powerState` (string)
    This will be a mix of power states and reset types.
    Enum: "UNKNOWN", "ON", "OFF", "POWERING_ON", "POWERING_OFF", "RESET"

  - `hardware.indicatorLed` (string)
    Enum: "UNKNOWN", "LIT", "BLINKING", "OFF"

  - `hardware.health` (object,null)
    Server health details

  - `hardware.health.summary` (string)
    Calculated summary of the overall health
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.fans` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.fanRedundancy` (string)
    Redundancy state
    Enum: "NON_REDUNDANT", "REDUNDANT", "FAILED_REDUNDANT", "NOT_PRESENT", "UNKNOWN"

  - `hardware.health.liquidCooling` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.liquidCoolingRedundancy` (string)
    Redundancy state
    Enum: "NON_REDUNDANT", "REDUNDANT", "FAILED_REDUNDANT", "NOT_PRESENT", "UNKNOWN"

  - `hardware.health.memory` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.network` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.powerSupplies` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.powerSupplyRedundancy` (string)
    Redundancy state
    Enum: "NON_REDUNDANT", "REDUNDANT", "FAILED_REDUNDANT", "NOT_PRESENT", "UNKNOWN"

  - `hardware.health.processor` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.storage` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.temperature` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.bios` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.smartStorage` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.healthLED` (string)
    Health state
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.health.airFilter` (string)
    Health state of the air filter
    Enum: "UNKNOWN", "OK", "WARNING", "CRITICAL", "READY", "NOT_PRESENT"

  - `hardware.platform` (any)

  - `hardware.formFactor` (any)

  - `hardware.bmc` (object,null)
    iLO BMC details

  - `hardware.bmc.mac` (string)

  - `hardware.bmc.ip` (string)

  - `hardware.bmc.hostname` (string)

  - `hardware.bmc.license` (any)

  - `hardware.bmc.version` (any)

  - `hardware.bmc.userDefined` (object,null)
    User defined properties for a credential via secure gateway connection

  - `hardware.bmc.userDefined.host` (string)
    IP address or the BMC

  - `hardware.bmc.userDefined.username` (string)
    Username used to access the BMC

  - `hardware.bmc.userDefined.password` (string)
    Password used to access the BMC

  - `hardware.bmc.userDefined.certificateFingerprint` (string)
    Certificate fingerprint of the BMC

  - `hardware.memoryMb` (any)

  - `hardware.manufacturer` (string)
    Manufacturer of the server hardware

  - `state` (object)
    Server connectivity state

  - `state.managed` (boolean)

  - `state.connected` (boolean)

  - `state.connectedModifiedAt` (string,null)

  - `state.subscriptionState` (string)
    Subscription State
    Enum: "REQUIRED", "SUBSCRIBED", "EXPIRED"

  - `state.subscriptionTier` (any)

  - `state.subscriptionExpiresAt` (string,null)
    Subscription validity end date

  - `state.subscriptionKey` (string,null)
    GreenLake subscription licence key assigned to the server
    Example: "ABCDE12345F"

  - `firmwareInventory` (array,null)
    Firmware Inventory

  - `firmwareInventory.name` (string)

  - `firmwareInventory.deviceContext` (string)

  - `softwareInventory` (array,null)
    Software Inventory

  - `firmwareBundleUri` (string,null)

  - `lastFirmwareUpdate` (object,null)
    Details of the last firmware update

  - `lastFirmwareUpdate.status` (string)
    Status of the last firmware update
    Enum: "OK", "FAILED", "SKIPPED", "NOT_UPDATED"

  - `lastFirmwareUpdate.attemptedAt` (string)
    Date on which the last firmware update job was attempted
    Example: "2024-06-01T10:00:00.000000+00:00"

  - `lastFirmwareUpdate.attemptedBaselineUri` (string,null)
    URI of the firmware baseline used in the last firmware update attempt
    Example: "/compute-ops-mgmt/v1/firmware-bundles/abc123"

  - `lastFirmwareUpdate.installSwDrivers` (boolean,null)
    Whether software drivers were included in the firmware update

  - `lastFirmwareUpdate.downgrade` (boolean,null)
    Whether a firmware downgrade was permitted in the update

  - `lastFirmwareUpdate.powerOff` (boolean,null)
    Whether the server was powered off after the firmware update completed

  - `lastFirmwareUpdate.completedAt` (string,null)
    Date on which the last firmware update completed
    Example: "2024-06-01T10:45:00.000000+00:00"

  - `lastFirmwareUpdate.bundleUpdateMethod` (string,null)
    Method used to apply the firmware bundle
    Enum: "Update", "Stage"

  - `lastFirmwareUpdate.firmwareInventoryUpdates` (array)
    List of the components updated by the last firmware update

  - `lastFirmwareUpdate.firmwareInventoryUpdates.name` (string)
    Name of the firmware component that was updated

  - `lastFirmwareUpdate.firmwareInventoryUpdates.version` (string)
    Version of the firmware that the component was updated to

  - `lastFirmwareUpdate.firmwareInventoryUpdates.status` (string)
    Status of the firmware update
    Enum: "OK", "FAILED", "SKIPPED", "NOT_UPDATED"

  - `tags` (object,null)
    Extra identifiers a server
    Example: {"location":"San Jose"}

  - `processorVendor` (string,null)
    Type and brand of processor
    Example: "Intel(R) Xeon(R) Silver 4114 CPU @ 2.20GHz"

  - `biosFamily` (string,null)
    Bios version

  - `host` (object,null)
    host details

  - `host.osName` (string,null)

  - `host.osVersion` (string,null)

  - `host.osDescription` (string,null)

  - `host.osType` (integer,null)

  - `autoIloFwUpdate` (boolean)
    To opt in for automatic iLO-only firmware update

  - `oneview` (object,null)
    Details of the OneView managed server

  - `oneview.applianceUri` (string)

  - `oneview.maintenanceMode` (boolean)
    True if the server is in maintenance mode, false otherwise

  - `oneview.name` (string)
    Name of the server in OneView

  - `oneview.state` (string)
    Current resource state of the server hardware

  - `lastFullInventoryCollectionAt` (any)

  - `lastFullInventoryCollectionPowerState` (string)
    Power state of the server when the complete inventory is collected

  - `deviceClaimType` (string,null)
    Method by which the server was claimed and added to the system
    Enum: "ZTP", "MANUAL", "MAGICLINK", "UNKNOWN"

  - `connectionType` (string,null)
    How the server connects to Compute Ops Management.
    Enum: "DIRECT", "ONEVIEW", "GATEWAY", "CREDENTIAL"

  - `managedBy` (string,null)
    Name of a third-party system that manages this server, if applicable (e.g. "Nutanix"). Null if the server is not managed by a known third-party system.
    Example: "Nutanix"

  - `lastServerLogCollectionAt` (string,null)
    Timestamp of the last server log (AHS) collection
    Example: "2024-06-01T12:00:00.000000+00:00"

  - `appliance` (object,null)
    Details of the appliance (OneView or Secure Gateway) through which this server is connected. Null values when the server connects directly.

  - `appliance.applianceUri` (string,null)
    URI of the appliance resource through which the server is connected. For OneView-connected servers this references an /compute-ops-mgmt/v1beta1/appliances/oneview+{id} resource; for gateway-connected servers it references an /compute-ops-mgmt/v1beta1/appliances/gateway+{id} resource.
    Example: "/compute-ops-mgmt/v1beta1/appliances/oneview+47f4ca46-462d-47fc-9458-a2d97db49a0c"

  - `appliance.applianceId` (string,null)
    UUID of the appliance through which the server is connected
    Example: "47f4ca46-462d-47fc-9458-a2d97db49a0c"

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

## Response 404 fields (application/json):

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


