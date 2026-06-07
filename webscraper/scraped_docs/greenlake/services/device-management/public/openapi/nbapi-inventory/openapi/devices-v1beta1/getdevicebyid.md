---
title: "GET /devices/v1beta1/devices/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1beta1/getdevicebyid.md"
scraped_at: "2026-06-07T06:15:19.467475+00:00Z"
---

# Get device information (deprecated)

Get details on a specific device by passing its resourceId. NOTE: You need  view permissions for device management to invoke this API. Rate limits are enforced on this API. 40 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

Endpoint: GET /devices/v1beta1/devices/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique identifier (uuid) of the device.

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier of the device.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `partNumber` (string, required)
    Identifier of the a device component or part.
    Example: "BHD31D9J"

  - `serialNumber` (string, required)
    The serial number of the device.
    Example: "AX17PR347J"

  - `type` (string, required)
    The type of the resource.
    Example: "devices/device"

  - `macAddress` (string)
    The media access control (MAC) address of the device
    Example: "21:01:18:21:12:22"

  - `deviceType` (string)
    The category (type) the device belongs to.
    Enum: "ALS", "AP", "BLE", "COMPUTE", "CONTROLLER", "DHCI_COMPUTE", "DHCI_STORAGE", "EINAR", "EINR", "GATEWAY", "IAP", "LTE_MODEM", "MC", "STORAGE", "SWITCH", "NW_THIRD_PARTY", "PCE", "SD_WAN_GW", "OPSRAMP_SAAS", "SD_SAAS", "SENSOR", "BRIDGES", "UNKNOWN"

  - `assignedState` (string)
    The current assignment state of the device.
- ASSIGNED_TO_ACTIVATE_CONFIG—The device was moved to the custom activate configuration.
- ASSIGNED_TO_DEDICATED_PLATFORM—The device is used in a dedicated platform workspace.
- ASSIGNED_TO_SERVICE—The device is assigned to a service.
- UNASSIGNED—The device is available for service provisioning.
    Enum: "ASSIGNED_TO_ACTIVATE_CONFIG", "ASSIGNED_TO_DEDICATED_PLATFORM", "ASSIGNED_TO_SERVICE", "UNASSIGNED"

  - `createdAt` (string)
    Date and time the device was created in UTC.
    Example: "2024-02-13T09:00:22.920Z"

  - `updatedAt` (string)
    Date and time the device was last updated in UTC.
    Example: "2024-02-13T19:30:32.920Z"

  - `model` (string)
    Hardware model of the device
    Example: "COMPUTE"

  - `archived` (boolean)
    A boolean that indicates whether the device has been archived or not. Archived devices are no longer in service.

  - `deviceName` (string)
    Hostname of the device
    Example: "iLO Hostname"

  - `secondaryName` (string)
    Secondary hostname of the device
    Example: "OS Hostname"

  - `application` (object)

  - `application.id` (string, required)
    Identifier of the application provisioned on the device
    Example: "0892c36d-40df-4f26-923b-76b5d213b420"

  - `application.resourceUri` (string, required)
    URI to the application
    Example: "/service-catalog/v1beta1/service-managers/0892c36d-40df-4f26-923b-76b5d213b420"

  - `region` (string)
    The region of the application the device is provisioned in
    Example: "us-west"

  - `tags` (object)

  - `subscription` (array)

  - `subscription.id` (string, required)
    Unique identifier of the subscription assigned to the device
    Example: "3292c36d-30ef-4f26-823b-76b5d213b670"

  - `subscription.resourceUri` (string, required)
    URI to the the subscription
    Example: "/subscriptions/v1beta1/subscriptions/3292c36d-30ef-4f26-823b-76b5d213b670"

  - `subscription.key` (string)
    The unique identifier of a subscription.
    Example: "SIEIAASTEST018ID"

  - `subscription.tier` (string)
    Tier of the assigned subscription
    Enum: "BASIC_AP", "BASIC_SWITCH", "SPECIAL", "FOUNDATION_70XX", "ADVANCE_70XX", "FOUNDATION_7005", "ADVANCE_7005", "FOUNDATION_72XX", "ADVANCE_72XX", "ADVANCE_90XX_SEC", "FOUNDATION_BASE_90XX_SEC", "FOUNDATION_90XX_SEC", "SDWAN_SECURITY", "DEVICE_PROFILING", "VGW_500M", "VGW_2G", "VGW_4G", "ANALYTICS", "NETWORK_ACCESS_CONTROL", "FOUNDATION_AP", "ADVANCED_AP", "BRIDGE", "FOUNDATION_BRIDGE", "FOUNDATION_WLAN_GW", "FOUNDATION_SWITCH_6100", "FOUNDATION_SWITCH_6200", "FOUNDATION_SWITCH_6300", "FOUNDATION_SWITCH_6400", "FOUNDATION_SWITCH_8400", "FOUNDATION_SWITCH_8XXX_9XXX_10XXX", "ADVANCED_SWITCH_6100", "ADVANCED_SWITCH_6200", "ADVANCED_SWITCH_6300", "ADVANCED_SWITCH_6400", "ADVANCED_SWITCH_8400", "ADVANCED_SWITCH_8XXX_9XXX_10XXX", "ADVANCED_PROLIANT", "FOUNDATION_PROLIANT", "STANDARD_PROLIANT", "ENHANCED_PROLIANT", "FOUNDATION_SDFLEX", "STANDARD_SDFLEX", "ENHANCED_SDFLEX", "FOUNDATION_EDGELINE", "STANDARD_EDGELINE", "ENHANCED_EDGELINE", "FOUNDATION_VM_BACKUP", "STANDARD_VM_BACKUP", "ENHANCED_VM_BACKUP", "FOUNDATION_ZERTO", "FOUNDATION_ZERTO_LEGACY", "NO_TIER_ZERTO", "FOUNDATION_SFM", "STANDARD_OVOPSMGMT", "ENHANCED_OVOPSMGMT", "FOUNDATION_ALLETRA", "STANDARD_ALLETRA", "ENHANCED_ALLETRA", "ADVANCED_ALLETRA_4K", "STANDARD_ALLETRA_4K", "ENHANCED_ALLETRA_4K", "MCP_BAAS", "MCV_BAAS", "MCB_BAAS", "BCP_BAAS", "BCV_BAAS", "BCB_BAAS", "GPP_BAAS", "GPV_BAAS", "GPB_BAAS", "GPP_HCIAAS", "GPB_HCIAAS", "GPV_HCIAAS", "EVP_HCIAAS", "EVB_HCIAAS", "EPP_HCIAAS", "EPB_HCIAAS", "BCP_HCIAAS", "BCV_HCIAAS", "BCB_HCIAAS", "AFP_HCIAAS", "AFB_HCIAAS", "AFV_HCIAAS", "HFP_HCIAAS", "HFB_HCIAAS", "HFV_HCIAAS", "FOUNDATION_BLOCK_STORAGE", "FOUNDATION_HCI_MANAGER", "FOUNDATION_CARE_EMBEDDED", "FOUNDATION_CARE_PLUS_EMBEDDED", "FOUNDATION_NW_THIRD_PARTY", "ADVANCED_NW_THIRD_PARTY", "WLAN_ADVANCED_90XX_SEC", "WLAN_ADVANCED_92XX_SEC", "FOUNDATION_92XX_SEC", "ADVANCED_92XX_SEC", "WLAN_ADVANCED_90XX_70XX", "WLAN_ADVANCED_92XX_72XX", "WLAN_ADVANCED_91XX", "WLAN_ADVANCED_91XX_SEC", "FOUNDATION_91XX", "FOUNDATION_91XX_SEC", "ADVANCED_91XX", "ADVANCED_91XX_SEC", "SMALL_VM_BACKUP", "MEDIUM_VM_BACKUP", "LARGE_VM_BACKUP", "XLARGE_VM_BACKUP", "PRIVATE_CLOUD_ENTERPRISE", "STA", "STB", "STC", "ES", "PR", "ET", "ST", "FOUNDATION_MLDE", "FOUNDATION_SENSOR_CLOUD", "FOUNDATION_SENSOR_LTE", "FOUNDATION_ZEBRA_AGENT_CLOUD", "FOUNDATION_AGENT_CLOUD", "SDWAN_FO_EC_HUB", "SDWAN_AD_EC_HUB", "FOUNDATION_STORAGE", "FOUNDATION_EZMERAL_K8S", "ONPREM_SERVICE", "FOUNDATION_SUPER_COMPUTING", "HPE_ALLETRA_STORAGE_MP_B10000_SOFTWARE_AND_SUPPORT_SAAS", "CENTRAL_OPSRAMP_EXTENSION", "OPSRAMP_INTEGRATIONS", "UNKNOWN"

  - `subscription.startDate` (string)
    The date and time the subscription was created in UTC.
    Example: "2024-02-13T09:00:22.920Z"

  - `subscription.endDate` (string)
    The date and time the subscription was last updated in UTC.
    Example: "2024-02-13T19:30:32.920Z"

  - `tenantWorkspaceId` (string)
    The unique identifier of the tenant workspace belonging to an MSP. This field is populated only for MSP-owned inventory tenants (the MSP owns the devices and subscriptions and also manages the workspace on behalf of their customers).
    Example: "3292c36d-30ef-4f26-823b-76b5d213b670"

  - `location` (object)

  - `location.id` (string, required)
    Identifier of the location of the device
    Example: "57f2b22e-7923-497b-8120-fd2b94579f13"

  - `location.resourceUri` (string, required)
    URI to the location of the device
    Example: "/locations/v1beta1/locations/57f2b22e-7923-497b-8120-fd2b94579f13"

  - `location.city` (string)
    City of the location
    Example: "New York"

  - `location.state` (string)
    State of the location
    Example: "NY"

  - `location.country` (string)
    Country of the location
    Example: "USA"

  - `location.latitude` (number)
    Latitude coordinate
    Example: 40.7128

  - `location.longitude` (number)
    Longitude coordinate
    Example: -74.006

  - `location.postalCode` (string)
    Postal code of the location
    Example: 10001

  - `location.locationName` (string)
    Name of the location
    Example: "Main Office"

  - `location.streetAddress` (string)
    Street address of the location
    Example: "123 Main St"

  - `location.locationSource` (string)
    Source of the location information
    Example: "GPS"

  - `warranty` (object)
    The warranty information for the device.

  - `warranty.country` (string)

  - `warranty.currentSupportLevel` (object)
    The support levels are ranked to differentiate and display the support provided to customers.

  - `warranty.currentSupportLevel.serviceLevel` (string)
    The value used for differentiation.

  - `warranty.currentSupportLevel.serviceLevelRank` (integer)
    The rank of the support level. The lower the rank, the better the level.

  - `warranty.currentSupportLevel.contractLevel` (string)
    Sub-categorizes the support level for display to the customer.

  - `warranty.currentSupportLevel.contractLevelRank` (integer)
    The rank of the contract level within the support level. The lower the rank, the better the level.

  - `warranty.currentSupportLevel.startDate` (integer)
    The start date of the support level.

  - `warranty.currentSupportLevel.endDate` (integer)
    The end date of the support level.

  - `warranty.supportLevels` (array)

  - `dedicatedPlatformWorkspace` (object)

  - `dedicatedPlatformWorkspace.id` (string, required)
    Unique identifier of the dedicated platform workspace
    Example: "a482ff61-1e0e-4818-920b-4cbc017208ee"

  - `contact` (object)
    The contact details associated with the device.
Depending on the contact type, only the relevant fields will be populated.
- WORKSPACE-USER—The contact is a workspace user. In this case, the id and resourceUri fields are populated to reference the workspace user identity.
- NON-WORKSPACE-USER—The contact is not a workspace user. In this case, the email, firstName, lastName, and phoneNumber fields are provided for direct contact information.

  - `contact.type` (string)
    Indicates if the contact is a workspace user or not.
    Enum: "WORKSPACE-USER", "NON-WORKSPACE-USER"

  - `contact.email` (string)
    The email address of the contact.
    Example: "nonworkspace.user@gmail.com"

  - `contact.firstName` (string)
    The first name of the contact.
    Example: "John"

  - `contact.lastName` (string)
    The last name of the contact.
    Example: "Doe"

  - `contact.phoneNumber` (string)
    The phone number for the contact.
    Example: "+1-555-123-4567"

  - `contact.id` (string)
    The unique identifier of the workspace user contact.
    Example: "4a2e4102-5c05-4713-8fc8-4e82f9704e53"

  - `contact.resourceUri` (string)
    Resource URI for the workspace user contact.
    Example: "/identity/v1/users/4a2e4102-5c05-4713-8fc8-4e82f9704e53"

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `badRequestErrorDetails` (array)

  - `badRequestErrorDetails.type` (string, required)
    The type of error details.

  - `badRequestErrorDetails.issues` (array, required)
    An array of request issues.

  - `badRequestErrorDetails.issues.source` (string)
    The part of the request with an issue.

  - `badRequestErrorDetails.issues.subject` (string)
    The issue key.

  - `badRequestErrorDetails.issues.description` (string)
    An explanation of the issue.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 422 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `serverErrorDetails` (array)

  - `serverErrorDetails.type` (string, required)

  - `serverErrorDetails.retryAfterSeconds` (integer, required)


