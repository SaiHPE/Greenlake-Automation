---
title: "POST /compute-ops/v1beta2/groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/groups-v1beta2/create_v1beta2_group.md"
scraped_at: "2026-06-07T06:14:46.220493+00:00Z"
---

# Create a group

Create a group for a specific user.

To create a OneView appliance group, please use the v1beta3 API.

Endpoint: POST /compute-ops/v1beta2/groups
Version: latest
Security: Bearer

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/json' in order for the request to be performed.

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Request fields (application/json):

  - `name` (string, required)
    Example: "Production Group"

  - `description` (string)
    Example: "All prod servers"

  - `autoFwUpdateOnAdd` (boolean)
    Enable automatic firmware updates to the configured baseline when a server is added to a group, This is equivalent to firmwareUpdate under serverPolicies. The value must be same if both are provided

  - `platformFamily` (string)
    Platform family of all servers in this group. There are no restrictions for groups and all supported server types are allowed. This optional attribute will be set to a default value of "ANY", to indicate that any server platform family can be in this group, regardless of the value passed in.
    Enum: "ANY", "PROLIANT"

  - `serverSettingsUris` (array)
    URIs for group server settings
    Example: ["/compute-ops/v1beta1/server-settings/00000000-0000-0000-0000-800000000001"]

  - `data` (object)

  - `serverPolicies` (object)
    Stores policy settings for server group actions

  - `serverPolicies.onServerAdd` (object)
    Policies to be applied when a server is added to a group

  - `serverPolicies.onServerAdd.firmwareUpdate` (boolean)
    Enable automatic firmware updates to the configured baseline when a server is added to a group, This is equivalent to autoFwUpdateOnAdd. The value must be same if both are provided

  - `serverPolicies.onServerAdd.biosApplySettings` (boolean)
    Enable automatic application of BIOS settings when a server is added to a group.

  - `serverPolicies.onServerAdd.biosFactoryReset` (boolean)
    When 'biosApplySettings' is enabled, reset the server BIOS to its factory default configuration when a server is added to a group.

  - `serverPolicies.onServerAdd.iloApplySettings` (boolean)
    Enable automatic application of iLO settings when a server is added to a group. A server group must have HPE pre-defined iLO settngs to allow the auto apply of iLO settings.

  - `serverPolicies.onServerAdd.storageConfiguration` (boolean)
    When server is added to the group, the OS volume will be created immediately if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.storageVolumeDeletion` (boolean)
    When server is added to the group, any existing internal storage configuration will be erased prior to creating the new OS volume if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.storageVolumeName` (string)
    When a server is added to the group, associate a name with the created volume if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.externalStorageConfiguration` (boolean)
    When a server is added to the group, apply the external storage configuration immediately if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.osImageSettings` (boolean)
    When a server is added to the group, install the operating system image immediately if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.osCompletionTimeoutMin` (integer)
    When a server is added to the group and automatic install of operating system is enabled, this property sets the amount of time (in minutes) the operating system installation will be allowed to continue before it times out. The timeout specified is applicable for each individual server in the group.

  - `serverPolicies.onServerAdd.firmwareDowngrade` (boolean)
    Deprecated, prefer using onSettingsApply.firmwareDowngrade instead. Allow downgrade of firmware when firmware update is performed on server addition to a group. Valid only when firmware update is set to true

  - `serverPolicies.onSettingsApply` (object)
    Policies to be applied on server group actions

  - `serverPolicies.onSettingsApply.firmwareDowngrade` (boolean)
    Allow or forbid downgrade of a firmware when firmware update is performed.

  - `autoAddServerTags` (object)
    A case insensitive tag that can be associated with a group to automatically add servers to the group. A group can have a maximum of one tag and multiple groups can not have the same tag.

When a server is onboarded or has its tags changed, the server's tags will be checked against the group's autoAddServerTags.  If at least one of the server tags matches one group's autoAddServerTags, the server will be placed into the associated group. Once a server has been connected, the server becomes ineligible for automatically being placed into groups, even if it is later disconnected.

If a server's tags match more than one group, it will not be put into any group.

If a server is in a group, any further tag changes will not move it to another group.  If the server was added to a group but has been removed, is not in any group, and still has not been activated, changing the server tags will automatically assign it to the matching group.

Tags can contain any alphaneumeric characters, any Unicode space separators, and the following characters: _ . : = + - @. An example of one of these tags can be seen in the sample request on this page.
    Example: {"Department":"Development - Texas"}

## Response 201 fields (application/json):

  - `id` (string, required)
    Primary identifier for the group given by the system

  - `type` (string, required)
    Type of the resource

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    Time of group creation

  - `updatedAt` (string, required)
    Time of the last group update

  - `resourceUri` (string)
    URI to the group itself (i.e. a self link)
    Example: "/compute-ops/v1beta2/groups/0e7f516c-0829-4135-83d6-09ce844ddd9d"

  - `name` (string)
    Name for the group given by the user
    Example: "Production Group"

  - `description` (string,null)
    Example: "All prod servers"

  - `autoFwUpdateOnAdd` (boolean)
    Enabled automatic firmware updates to the configured baseline when a server is added to a group

  - `groupComplianceStatus` (string)
    This state defines the compliance status of a device.
If all devices in a group are COMPLIANT, the group state will be compliant.
If a group contains devices that are COMPLIANT or UNKNOWN, the UNKNOWN state
overrides the COMPLIANT state and the group state will be UNKNOWN.
If a group contains devices that are NOT_COMPLIANT, COMPLIANT, or UNKNOWN
the NOT_COMPLIANT state will override the COMPLIANT and UNKNOWN states, so
the group state will be NOT_COMPLIANT. Finally, the NOT_APPLICABLE state
overrides all others so if a device in a group is NOT_APPLICABLE or if the
group has no devices, the group state will be NOT_APPLICABLE.
    Enum: "COMPLIANT", "NOT_COMPLIANT", "UNKNOWN", "NOT_APPLICABLE"

  - `serverSettingsUris` (array)
    URIs for group server settings
    Example: ["/compute-ops/v1beta1/server-settings/00000000-0000-0000-0000-800000000001"]

  - `platformFamily` (string)
    Platform family of all servers in this group. There are no restrictions for groups and all supported server types are allowed. This optional attribute will be set to a default value of "ANY", to indicate that any server platform family can be in this group, regardless of the value passed in.

For management of OneView appliance groups, please use the v1beta3 API.
    Enum: "ANY", "PROLIANT", "OVE_APPLIANCE_SYNERGY", "OVE_APPLIANCE_VM"

  - `devicesUri` (string)
    Example: "/compute-ops/v1beta2/groups/6081a383-b9e5-45e3-8371-1e0ba7b72068/devices"

  - `devices` (array)

  - `devices.id` (string, required)
    Primary identifier for the device given by the system

  - `devices.resourceUri` (string)
    URI to the device itself (i.e. a self link)
    Example: "/compute-ops/v1beta2/groups/6081a383-b9e5-45e3-8371-1e0ba7b72068/devices/873357-P04+WKQ82425HD"

  - `devices.serial` (string)

  - `devices.productId` (string)

  - `devices.eTag` (string)

  - `devices.serverId` (string)

  - `devices.serverUri` (string)
    Example: "/api/compute/v1/servers/873357-P04+WKQ82425HD"

  - `devices.state` (string)
    An enumeration.
    Enum: "ASSIGNED", "FAILED", "ACTIVE", "QUARANTINE", "APPLYING_FIRMWARE", "APPLYING_SCHEMA", "APPLYING_OS"

  - `devices.groupId` (string)

  - `devices.subscriptionState` (string)
    Subscription state.
    Enum: "REQUIRED", "SUBSCRIBED", "EXPIRED"

  - `devices.subscriptionTier` (string)
    Subscription tier.
    Enum: "ENHANCED"

  - `serverPolicies` (object)
    Stores policy settings for server group actions

  - `serverPolicies.onServerAdd` (object)
    Policies to be applied when a server is added to a group

  - `serverPolicies.onServerAdd.firmwareUpdate` (boolean)
    Enabled automatic firmware updates to the configured baseline when a server is added to a group

  - `serverPolicies.onServerAdd.biosApplySettings` (boolean)
    Enable automatic application of BIOS settings when a server is added to a group.

  - `serverPolicies.onServerAdd.biosFactoryReset` (boolean)
    When 'biosApplySettings' is enabled, reset the server BIOS to its factory default configuration when a server is added to a group.

  - `serverPolicies.onServerAdd.iloApplySettings` (boolean)
    Enable automatic application of iLO settings when a server is added to a group. A server group must have HPE pre-defined iLO settngs to allow the auto apply of iLO settings.

  - `serverPolicies.onServerAdd.storageConfiguration` (boolean)
    When server is added to the group, the OS volume will be created immediately if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.storageVolumeDeletion` (boolean)
    When server is added to the group, any existing internal storage configuration will be erased prior to creating the new OS volume if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.storageVolumeName` (string)
    When a server is added to the group, associate a name with the created volume if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.externalStorageConfiguration` (boolean)
    When a server is added to the group, apply the external storage configuration immediately if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.osImageSettings` (boolean)
    When a server is added to the group, install the operating system image immediately if the server is activated or when the server is activated at a later time.

  - `serverPolicies.onServerAdd.osCompletionTimeoutMin` (integer)
    When a server is added to the group and automatic install of operating system is enabled, this property sets the amount of time (in minutes) the operating system installation will be allowed to continue before it times out. The timeout specified is applicable for each individual server in the group.

  - `serverPolicies.onServerAdd.firmwareDowngrade` (boolean)
    Deprecated, prefer using onSettingsApply.firmwareDowngrade instead. Allow downgrade of firmware when firmware update is performed on server addition to a group. Valid only when firmware update is set to true

  - `serverPolicies.onSettingsApply` (object)
    Policies to be applied on server group actions

  - `serverPolicies.onSettingsApply.firmwareDowngrade` (boolean)
    Allow or forbid downgrade of a firmware when firmware update is performed.

  - `autoAddServerTags` (object,null)
    A case insensitive tag that can be associated with a group to automatically add servers to the group. A group can have a maximum of one tag and multiple groups can not have the same tag.

When a server is onboarded or has its tags changed, the server's tags will be checked against the group's autoAddServerTags.  If at least one of the server tags matches one group's autoAddServerTags, the server will be placed into the associated group. Once a server has been connected, the server becomes ineligible for automatically being placed into groups, even if it is later disconnected.

If a server's tags match more than one group, it will not be put into any group.

If a server is in a group, any further tag changes will not move it to another group.  If the server was added to a group but has been removed, is not in any group, and still has not been activated, changing the server tags will automatically assign it to the matching group.

Tags can contain any alphaneumeric characters, any Unicode space separators, and the following characters: _ . : = + - @. An example of one of these tags can be seen in the sample request on this page.
    Example: {"Department":"Development - Texas"}

  - `groupMeta` (any)

  - `groupCompliance` (object)
    Overall summary compliance state

  - `groupCompliance.summary` (string)
    This state defines the compliance status of a device.
If all devices in a group are COMPLIANT, the group state will be compliant.
If a group contains devices that are COMPLIANT or UNKNOWN, the UNKNOWN state
overrides the COMPLIANT state and the group state will be UNKNOWN.
If a group contains devices that are NOT_COMPLIANT, COMPLIANT, or UNKNOWN
the NOT_COMPLIANT state will override the COMPLIANT and UNKNOWN states, so
the group state will be NOT_COMPLIANT. Finally, the NOT_APPLICABLE state
overrides all others so if a device in a group is NOT_APPLICABLE or if the
group has no devices, the group state will be NOT_APPLICABLE.
    Enum: "COMPLIANT", "NOT_COMPLIANT", "UNKNOWN", "NOT_APPLICABLE"

  - `groupCompliance.firmware` (object)

  - `groupCompliance.firmware.status` (string)
    This state defines the compliance status of a device.
If all devices in a group are COMPLIANT, the group state will be compliant.
If a group contains devices that are COMPLIANT or UNKNOWN, the UNKNOWN state
overrides the COMPLIANT state and the group state will be UNKNOWN.
If a group contains devices that are NOT_COMPLIANT, COMPLIANT, or UNKNOWN
the NOT_COMPLIANT state will override the COMPLIANT and UNKNOWN states, so
the group state will be NOT_COMPLIANT. Finally, the NOT_APPLICABLE state
overrides all others so if a device in a group is NOT_APPLICABLE or if the
group has no devices, the group state will be NOT_APPLICABLE.
    Enum: "COMPLIANT", "NOT_COMPLIANT", "UNKNOWN", "NOT_APPLICABLE"

  - `groupCompliance.firmware.statusReason` (string)

  - `groupCompliance.iloSettings` (object)

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

## Response 409 fields (application/json):

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


