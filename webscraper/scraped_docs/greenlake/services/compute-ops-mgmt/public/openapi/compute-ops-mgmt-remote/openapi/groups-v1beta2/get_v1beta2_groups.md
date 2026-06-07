---
title: "GET /compute-ops/v1beta2/groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/groups-v1beta2/get_v1beta2_groups.md"
scraped_at: "2026-06-07T06:14:46.217660+00:00Z"
---

# List all groups

Get the list of a user's groups.

Endpoint: GET /compute-ops/v1beta2/groups
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

Groups can be filtered by:
  - autoAddServerTags
  - autoFwUpdateOnAdd
  - createdAt
  - description
  - generation
  - groupComplianceStatus
  - id
  - name
  - platformFamily
  - serverPolicies
  - serverSettingsUris
  - updatedAt


The following examples are not an exhaustive list of all possible filtering options.

  - `sort` (string)
    The order in which to return the resources in the collection.

The value of the sort query parameter is a comma separated list of sort expressions. 
Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc 
(descending).

The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, 
and so on. If a direciton indicator is omitted the default direction is ascending.

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

  - `items.id` (string, required)
    Primary identifier for the group given by the system

  - `items.type` (string, required)
    Type of the resource

  - `items.generation` (integer, required)
    Monotonically increasing update counter

  - `items.createdAt` (string, required)
    Time of group creation

  - `items.updatedAt` (string, required)
    Time of the last group update

  - `items.resourceUri` (string)
    URI to the group itself (i.e. a self link)
    Example: "/compute-ops/v1beta2/groups/0e7f516c-0829-4135-83d6-09ce844ddd9d"

  - `items.name` (string)
    Name for the group given by the user
    Example: "Production Group"

  - `items.description` (string,null,string,null)
    Example: "All prod servers"

  - `items.autoFwUpdateOnAdd` (boolean)
    Enabled automatic firmware updates to the configured baseline when a server is added to a group

  - `items.groupComplianceStatus` (string)
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

  - `items.serverSettingsUris` (array)
    URIs for group server settings
    Example: ["/compute-ops/v1beta1/server-settings/00000000-0000-0000-0000-800000000001"]

  - `items.platformFamily` (string,string)
    Platform family of all servers in this group. There are no restrictions for groups and all supported server types are allowed. This optional attribute will be set to a default value of "ANY", to indicate that any server platform family can be in this group, regardless of the value passed in.

For management of OneView appliance groups, please use the v1beta3 API.
    Enum: "ANY", "PROLIANT", "OVE_APPLIANCE_SYNERGY", "OVE_APPLIANCE_VM"

  - `items.devicesUri` (string)
    Example: "/compute-ops/v1beta2/groups/6081a383-b9e5-45e3-8371-1e0ba7b72068/devices"

  - `items.devices` (array)

  - `items.devices.id` (string, required)
    Primary identifier for the device given by the system

  - `items.devices.resourceUri` (string)
    URI to the device itself (i.e. a self link)
    Example: "/compute-ops/v1beta2/groups/6081a383-b9e5-45e3-8371-1e0ba7b72068/devices/873357-P04+WKQ82425HD"

  - `items.devices.serial` (string)

  - `items.devices.productId` (string)

  - `items.devices.eTag` (string)

  - `items.devices.serverId` (string)

  - `items.devices.serverUri` (string)
    Example: "/api/compute/v1/servers/873357-P04+WKQ82425HD"

  - `items.devices.state` (string)
    An enumeration.
    Enum: "ASSIGNED", "FAILED", "ACTIVE", "QUARANTINE", "APPLYING_FIRMWARE", "APPLYING_SCHEMA", "APPLYING_OS"

  - `items.devices.groupId` (string)

  - `items.devices.subscriptionState` (string)
    Subscription state.
    Enum: "REQUIRED", "SUBSCRIBED", "EXPIRED"

  - `items.devices.subscriptionTier` (string)
    Subscription tier.
    Enum: "ENHANCED"

  - `items.serverPolicies` (object)
    Stores policy settings for server group actions

  - `items.serverPolicies.onServerAdd` (object)
    Policies to be applied when a server is added to a group

  - `items.serverPolicies.onServerAdd.firmwareUpdate` (boolean)
    Enabled automatic firmware updates to the configured baseline when a server is added to a group

  - `items.serverPolicies.onServerAdd.biosApplySettings` (boolean)
    Enable automatic application of BIOS settings when a server is added to a group.

  - `items.serverPolicies.onServerAdd.biosFactoryReset` (boolean)
    When 'biosApplySettings' is enabled, reset the server BIOS to its factory default configuration when a server is added to a group.

  - `items.serverPolicies.onServerAdd.iloApplySettings` (boolean)
    Enable automatic application of iLO settings when a server is added to a group. A server group must have HPE pre-defined iLO settngs to allow the auto apply of iLO settings.

  - `items.serverPolicies.onServerAdd.storageConfiguration` (boolean)
    When server is added to the group, the OS volume will be created immediately if the server is activated or when the server is activated at a later time.

  - `items.serverPolicies.onServerAdd.storageVolumeDeletion` (boolean)
    When server is added to the group, any existing internal storage configuration will be erased prior to creating the new OS volume if the server is activated or when the server is activated at a later time.

  - `items.serverPolicies.onServerAdd.storageVolumeName` (string)
    When a server is added to the group, associate a name with the created volume if the server is activated or when the server is activated at a later time.

  - `items.serverPolicies.onServerAdd.externalStorageConfiguration` (boolean)
    When a server is added to the group, apply the external storage configuration immediately if the server is activated or when the server is activated at a later time.

  - `items.serverPolicies.onServerAdd.osImageSettings` (boolean)
    When a server is added to the group, install the operating system image immediately if the server is activated or when the server is activated at a later time.

  - `items.serverPolicies.onServerAdd.osCompletionTimeoutMin` (integer)
    When a server is added to the group and automatic install of operating system is enabled, this property sets the amount of time (in minutes) the operating system installation will be allowed to continue before it times out. The timeout specified is applicable for each individual server in the group.

  - `items.serverPolicies.onServerAdd.firmwareDowngrade` (boolean)
    Deprecated, prefer using onSettingsApply.firmwareDowngrade instead. Allow downgrade of firmware when firmware update is performed on server addition to a group. Valid only when firmware update is set to true

  - `items.serverPolicies.onSettingsApply` (object)
    Policies to be applied on server group actions

  - `items.serverPolicies.onSettingsApply.firmwareDowngrade` (boolean)
    Allow or forbid downgrade of a firmware when firmware update is performed.

  - `items.autoAddServerTags` (object,null,object,null)
    A case insensitive tag that can be associated with a group to automatically add servers to the group. A group can have a maximum of one tag and multiple groups can not have the same tag.

When a server is onboarded or has its tags changed, the server's tags will be checked against the group's autoAddServerTags.  If at least one of the server tags matches one group's autoAddServerTags, the server will be placed into the associated group. Once a server has been connected, the server becomes ineligible for automatically being placed into groups, even if it is later disconnected.

If a server's tags match more than one group, it will not be put into any group.

If a server is in a group, any further tag changes will not move it to another group.  If the server was added to a group but has been removed, is not in any group, and still has not been activated, changing the server tags will automatically assign it to the matching group.

Tags can contain any alphaneumeric characters, any Unicode space separators, and the following characters: _ . : = + - @. An example of one of these tags can be seen in the sample request on this page.
    Example: {"Department":"Development - Texas"}

  - `items.groupMeta` (any)

  - `items.groupCompliance` (object)
    Overall summary compliance state

  - `items.groupCompliance.summary` (string)
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

  - `items.groupCompliance.firmware` (object)

  - `items.groupCompliance.firmware.status` (string)
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

  - `items.groupCompliance.firmware.statusReason` (string)

  - `items.groupCompliance.iloSettings` (object)

  - `total` (integer)
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


