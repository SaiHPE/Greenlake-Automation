---
title: "PATCH /compute-ops-mgmt/v1beta2/servers/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/servers-v1beta2/patch_v1beta2_server_by_id.md"
scraped_at: "2026-06-07T06:14:53.545347+00:00Z"
---

# Patch a server

Partially update a Server specified by its id

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


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: PATCH /compute-ops-mgmt/v1beta2/servers/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique Server identifier

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed.

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Request fields (application/merge-patch+json):

  - `appliance` (object)
    Associated secure gateway for the server.

  - `appliance.applianceId` (any)
    Unique identifier of the secure gateway.

  - `autoIloFwUpdate` (boolean)
    To opt in for automatic iLO-only firmware update

  - `hardware` (object)
    Server hardware details

  - `hardware.bmc` (object)
    Baseboard Management Controller details.

  - `hardware.bmc.userDefined` (object)
    User defined BMC details.

  - `hardware.bmc.userDefined.host` (string)
    IP address of the BMC.

  - `hardware.bmc.userDefined.username` (string)
    Username used to access the BMC.

  - `hardware.bmc.userDefined.password` (string)
    Password used to access the BMC.

  - `hardware.bmc.userDefined.certificateFingerprint` (string)
    Certificate fingerprint of the BMC.

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the server given by the system

  - `type` (string, required)
    Type of the resource

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    Time of server creation

  - `updatedAt` (string, required)
    Time of the last server update

  - `name` (string)
    Name given to resource
    Example: "myServer"

  - `resourceUri` (string)
    URI to the server itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta2/servers/875765-S01+1M512501AB"

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

  - `hardware.platform` (any)

  - `hardware.formFactor` (any)

  - `hardware.bmc` (object,null)
    iLO BMC details

  - `hardware.bmc.mac` (string)

  - `hardware.bmc.ip` (string)

  - `hardware.bmc.hostname` (string)

  - `hardware.bmc.license` (any)

  - `hardware.bmc.userDefined` (object,null)
    User defined properties for a credential via secure gateway connection

  - `hardware.bmc.userDefined.host` (string)
    IP address of the BMC

  - `hardware.bmc.userDefined.username` (string)
    Username used to access the BMC

  - `hardware.bmc.userDefined.password` (string)
    Password used to access the BMC

  - `hardware.bmc.userDefined.certificateFingerprint` (string)
    Certificate fingerprint of the BMC

  - `hardware.memoryMb` (any)

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

  - `firmwareInventory` (array,null)
    Firmware Inventory

  - `firmwareInventory.name` (string)

  - `firmwareInventory.version` (string)

  - `firmwareInventory.deviceContext` (string)

  - `softwareInventory` (array,null)
    Software Inventory

  - `firmwareBundleUri` (string,null)

  - `lastFirmwareUpdate` (object,null)
    Details of the last firmware update

  - `lastFirmwareUpdate.status` (string)
    Status of the last firmware update
    Enum: "OK", "FAILED"

  - `lastFirmwareUpdate.attemptedAt` (string)
    Date in which the last firmware update job was attempted

  - `lastFirmwareUpdate.firmwareInventoryUpdates` (array)
    List of the components updated by the last firmware update

  - `lastFirmwareUpdate.firmwareInventoryUpdates.name` (string)
    Name of the firmware component that was updated

  - `lastFirmwareUpdate.firmwareInventoryUpdates.version` (string)
    Version of the firmware that the component was updated to

  - `lastFirmwareUpdate.firmwareInventoryUpdates.status` (string)
    Status of the firmware update
    Enum: "OK", "FAILED"

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

## Response 415 fields (application/json):

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


