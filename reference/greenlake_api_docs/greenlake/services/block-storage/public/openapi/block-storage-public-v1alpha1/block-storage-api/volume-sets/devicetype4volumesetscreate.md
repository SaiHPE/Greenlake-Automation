---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/devicetype4volumesetscreate.md"
scraped_at: "2026-06-07T06:14:33.860866+00:00Z"
---

# Create Application Set for an HPE Alletra Storage MP B10000 storage system

Create Application Set for an HPE Alletra Storage MP B10000 storage system

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `appSetName` (string, required)
    App set name
    Example: "Appset_134"

  - `appSetType` (string,null, required)
    application type
    Enum: "ORACLE_DATA", "ORACLE_LOG", "MICROSOFT_EXCHANGE", "MICROSOFT_EXCHANGE_LOG", "MICROSOFT_SQL_SERVER", "MICROSOFT_SQL_SERVER_LOG", "VIRTUAL_SERVER_VMWARE_ESXI_STORAGE", "VIRTUAL_SERVER_HYPER_V_STORAGE", "VIRTUAL_DESKTOP_VMWARE_ESXI_STORAGE", "VIRTUAL_DESKTOP_HYPER_V_STORAGE", "SHAREPOINT", "FILE_SERVER", "VME", "SAP_HANA", "VEEAM_BACKUP_REPOSITORY", "OTHER", "CUSTOM"

  - `appSetBusinessUnit` (string,null)
    App set business unit
    Example: "HPE"

  - `appSetComments` (string,null)
    App set comments
    Example: "Edit appset"

  - `createAppSetQosConfigInput` (object,null)
    Create QoS Configuration Input (Applicable for OS version 10.4.0 and later)

  - `createAppSetQosConfigInput.bandwidthMaxLimit` (number,null)
    The maximum bandwidth limit permitted for the volume set associated with this policy. The bandwidth maximum limit must be between 0 and 9,007,199,254,740,991 KB/s. Pass -1 to unset the parameter
    Example: 100

  - `createAppSetQosConfigInput.enable` (boolean,null)
    Enabling of QoS Configuration
    Example: true

  - `createAppSetQosConfigInput.enableSrAlert` (boolean,null)
    Sets the SR alert with the criterion name as the vvset name based on the max limits being set on the QoS parameters. If provided true, the SR alert criterion will be created or updated based on updated parameters. If provided false, the SR Alert criterion will be deleted if present. If enableSrAlert is not specified and the SR Alert criterion is already present for the volume set, the SR Alert criterion will be retained based on the updated QoS parameters.

  - `createAppSetQosConfigInput.iopsMaxLimit` (number,null)
    The maximum IOPS limit permitted for the volume set associated with this policy. The IOPS maximum limit must be between 0 and 2,147,483,647 IO/s. Pass -1 to unset the parameter
    Example: 1

  - `createAppSetQosConfigInput.perTb` (boolean,null)
    Sets the maximum IOPS limit or/and bandwidth limit for QoS throttling based on the number of terabytes configured for the volumes in the volume set on which QoS rule is configured.  By default, this option is off. Once per_tb is set, it cannot be unset (Applicable for storage systems with OS versions that are 10.4.0 or higher but below 10.5.0).
    Example: true

  - `customAppType` (string,null)
    App set name for Custom workloads when appSetType=CUSTOM
    Example: "CustomWorkload_123"

  - `members` (array,null)
    volumes list
    Example: ["vol1","vol2"]

  - `ransomware` (boolean,null)
    This attribute enables/disables ransomware detection on the volume set. Both the existing volumes in the volume set as well as the volumes which get added in future in to this volume set will have this ransomware setting. By Default, it is set to false. This applies to the HPE Alletra Storage MP B10000 systems running OS version 10.5.0 and later.

## Response 202 fields (application/json):

  - `taskUri` (string, required)
    Task URI which can be used to monitor the status of the operation.
    Example: "/rest/vega/v1/tasks/4969a568-6fed-4915-bcd5-e4566a75e00c"

  - `message` (string)
    Task Message.
    Example: "Successfully submitted"

  - `status` (string)
    Status of the task.
    Example: "SUBMITTED"

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


