---
title: "GET /internal-subscriptions/v1/subscriptions/group"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/internal-subscriptions-v1/getsubscriptionsgroupbyv1.md"
scraped_at: "2026-06-07T06:15:53.008023+00:00Z"
---

# Retrieve subscription data grouped by subscription tier or device type

Fetch subscription data grouped by subscription tier or device type within a workspace. This API allows users to organize subscriptions based on the provided grouping criteria.

Endpoint: GET /internal-subscriptions/v1/subscriptions/group
Version: latest
Security: Bearer

## Query parameters:

  - `groupBy` (string, required)
    Specifies the field to group subscriptions by.
    Enum: "tier", "deviceType"

  - `subscription-type` (array)
    List of subscription types to filter the results by. If not provided, all subscription types will be included.
    Enum: "CENTRAL_AP", "CENTRAL_SWITCH", "CENTRAL_CONTROLLER", "CENTRAL_GW", "SERVICE", "CENTRAL_STORAGE", "CENTRAL_COMPUTE", "CENTRAL_BRIDGE", "SUPPORT", "CENTRAL_NW_THIRD_PARTY", "PRIVATE_CLOUD_ENTERPRISE", "OPSRAMP", "UXI_SENSOR_CLOUD", "UXI_SENSOR_LTE", "UXI_AGENT_CLOUD", "UXI_ZEBRA_AGENT_CLOUD", "MLDE", "DEDICATED_SERVICE", "SUPER_COMPUTING", "ZERTO_LEGACY", "UNKNOWN"

## Response 200 fields (application/json):

  - `count` (integer)
    The number of items returned.

  - `total` (integer)
    The total number of items.

  - `items` (array)
    List of subscription properties grouped by the input query parameters.

  - `items.tier` (string)
    Tier of the subscription.
    Enum: "BASIC_AP", "BASIC_SWITCH", "SPECIAL", "FOUNDATION_70XX", "ADVANCE_70XX", "FOUNDATION_7005", "ADVANCE_7005", "FOUNDATION_72XX", "ADVANCE_72XX", "ADVANCE_90XX_SEC", "FOUNDATION_BASE_90XX_SEC", "FOUNDATION_90XX_SEC", "SDWAN_SECURITY", "DEVICE_PROFILING", "VGW_500M", "VGW_2G", "VGW_4G", "ANALYTICS", "NETWORK_ACCESS_CONTROL", "FOUNDATION_AP", "ADVANCED_AP", "BRIDGE", "FOUNDATION_BRIDGE", "FOUNDATION_WLAN_GW", "FOUNDATION_SWITCH_6100", "FOUNDATION_SWITCH_6200", "FOUNDATION_SWITCH_6300", "FOUNDATION_SWITCH_6400", "FOUNDATION_SWITCH_8400", "FOUNDATION_SWITCH_8XXX_9XXX_10XXX", "ADVANCED_SWITCH_6100", "ADVANCED_SWITCH_6200", "ADVANCED_SWITCH_6300", "ADVANCED_SWITCH_6400", "ADVANCED_SWITCH_8400", "ADVANCED_SWITCH_8XXX_9XXX_10XXX", "ADVANCED_PROLIANT", "FOUNDATION_PROLIANT", "STANDARD_PROLIANT", "ENHANCED_PROLIANT", "FOUNDATION_SDFLEX", "STANDARD_SDFLEX", "ENHANCED_SDFLEX", "FOUNDATION_EDGELINE", "STANDARD_EDGELINE", "ENHANCED_EDGELINE", "FOUNDATION_VM_BACKUP", "STANDARD_VM_BACKUP", "ENHANCED_VM_BACKUP", "FOUNDATION_ZERTO", "FOUNDATION_ZERTO_LEGACY", "NO_TIER_ZERTO", "FOUNDATION_SFM", "STANDARD_OVOPSMGMT", "ENHANCED_OVOPSMGMT", "FOUNDATION_ALLETRA", "STANDARD_ALLETRA", "ENHANCED_ALLETRA", "ADVANCED_ALLETRA_4K", "STANDARD_ALLETRA_4K", "ENHANCED_ALLETRA_4K", "MCP_BAAS", "MCV_BAAS", "MCB_BAAS", "BCP_BAAS", "BCV_BAAS", "BCB_BAAS", "GPP_BAAS", "GPV_BAAS", "GPB_BAAS", "GPP_HCIAAS", "GPB_HCIAAS", "GPV_HCIAAS", "EVP_HCIAAS", "EVB_HCIAAS", "EPP_HCIAAS", "EPB_HCIAAS", "BCP_HCIAAS", "BCV_HCIAAS", "BCB_HCIAAS", "AFP_HCIAAS", "AFB_HCIAAS", "AFV_HCIAAS", "HFP_HCIAAS", "HFB_HCIAAS", "HFV_HCIAAS", "FOUNDATION_BLOCK_STORAGE", "FOUNDATION_HCI_MANAGER", "FOUNDATION_CARE_EMBEDDED", "FOUNDATION_CARE_PLUS_EMBEDDED", "FOUNDATION_NW_THIRD_PARTY", "ADVANCED_NW_THIRD_PARTY", "WLAN_ADVANCED_90XX_SEC", "WLAN_ADVANCED_92XX_SEC", "FOUNDATION_92XX_SEC", "ADVANCED_92XX_SEC", "WLAN_ADVANCED_90XX_70XX", "WLAN_ADVANCED_92XX_72XX", "WLAN_ADVANCED_91XX", "WLAN_ADVANCED_91XX_SEC", "FOUNDATION_91XX", "FOUNDATION_91XX_SEC", "ADVANCED_91XX", "ADVANCED_91XX_SEC", "SMALL_VM_BACKUP", "MEDIUM_VM_BACKUP", "LARGE_VM_BACKUP", "XLARGE_VM_BACKUP", "PRIVATE_CLOUD_ENTERPRISE", "STA", "STB", "STC", "ES", "PR", "ET", "ST", "FOUNDATION_MLDE", "FOUNDATION_SENSOR_CLOUD", "FOUNDATION_SENSOR_LTE", "FOUNDATION_ZEBRA_AGENT_CLOUD", "FOUNDATION_AGENT_CLOUD", "SDWAN_FO_EC_HUB", "SDWAN_AD_EC_HUB", "FOUNDATION_STORAGE", "FOUNDATION_EZMERAL_K8S", "ONPREM_SERVICE", "FOUNDATION_SUPER_COMPUTING", "HPE_ALLETRA_STORAGE_MP_B10000_SOFTWARE_AND_SUPPORT_SAAS", "CENTRAL_OPSRAMP_EXTENSION", "UNKNOWN"

  - `items.tierDescription` (string)
    Description of the subscription tier.

  - `items.externalDeviceType` (string)
    The external device type.
    Enum: "AP", "SWITCH", "GATEWAY", "STORAGE", "DHCI_STORAGE", "COMPUTE", "DHCI_COMPUTE", "NW_THIRD_PARTY", "PCE", "SD_WAN_GW", "OPSRAMP_SAAS", "SD_SAAS", "SENSOR", "BRIDGE", "MLDE_SAAS", "SC_SAAS", "DR_SAAS", "EC_V"

  - `items.deviceType` (string)
    The device type.
    Enum: "ALS", "AP", "BLE", "COMPUTE", "CONTROLLER", "DHCI_COMPUTE", "DHCI_STORAGE", "EINAR", "EINR", "GATEWAY", "IAP", "LTE_MODEM", "MC", "STORAGE", "SWITCH", "NW_THIRD_PARTY", "PCE", "SD_WAN_GW", "OPSRAMP_SAAS", "SD_SAAS", "SENSOR", "BRIDGE", "MLDE_SAAS", "SC_SAAS", "DR_SAAS", "EC_V", "UNKNOWN"

  - `items.subscriptionType` (string)
    Type of the subscription.
    Enum: "CENTRAL_AP", "CENTRAL_SWITCH", "CENTRAL_CONTROLLER", "CENTRAL_GW", "SERVICE", "CENTRAL_STORAGE", "CENTRAL_COMPUTE", "CENTRAL_BRIDGE", "SUPPORT", "CENTRAL_NW_THIRD_PARTY", "PRIVATE_CLOUD_ENTERPRISE", "OPSRAMP", "UXI_SENSOR_CLOUD", "UXI_SENSOR_LTE", "UXI_AGENT_CLOUD", "UXI_ZEBRA_AGENT_CLOUD", "MLDE", "DEDICATED_SERVICE", "SUPER_COMPUTING", "ZERTO_LEGACY", "UNKNOWN"

  - `items.count` (integer)
    The subscription tier count.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetail` (array)

  - `errorDetail.type` (string, required)
    The type of error details.

  - `errorDetail.issues` (array, required)
    An array of bad request issues.

  - `errorDetail.issues.source` (string)
    The source of the error.

  - `errorDetail.issues.subject` (string)
    The specific issue key.

  - `errorDetail.issues.description` (string)
    A brief explanation of the error.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.retryAfterSeconds` (integer, required)


