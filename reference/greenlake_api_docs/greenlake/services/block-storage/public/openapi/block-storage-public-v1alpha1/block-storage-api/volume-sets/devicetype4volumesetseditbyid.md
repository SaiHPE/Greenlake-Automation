---
title: "PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/devicetype4volumesetseditbyid.md"
scraped_at: "2026-06-07T06:14:34.682041+00:00Z"
---

# Edit applicationset identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

Edit applicationset identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Request fields (application/json):

  - `addMembers` (array,null)
    Members to add to application set
    Example: ["vol1","vol2"]

  - `appSetBusinessUnit` (string,null)
    App set business unit
    Example: "HPE"

  - `appSetComments` (string,null)
    App set comments
    Example: "Edit appset"

  - `appSetName` (string,null)
    App set name
    Example: "Appset_134"

  - `appSetType` (string,null)
    Application set type. Not applicable for OS Version 10.4.0 and above.
    Enum: "ORACLE_DATA", "ORACLE_LOG", "MICROSOFT_EXCHANGE", "MICROSOFT_EXCHANGE_LOG", "MICROSOFT_SQL_SERVER", "MICROSOFT_SQL_SERVER_LOG", "VIRTUAL_SERVER_VMWARE_ESXI_STORAGE", "VIRTUAL_SERVER_HYPER_V_STORAGE", "VIRTUAL_DESKTOP_VMWARE_ESXI_STORAGE", "VIRTUAL_DESKTOP_HYPER_V_STORAGE", "SHAREPOINT", "FILE_SERVER", "VME", "SAP_HANA", "VEEAM_BACKUP_REPOSITORY", "OTHER", "CUSTOM"

  - `customAppType` (string,null)
    App set name for Custom workloads when appSetType=CUSTOM
    Example: "CustomWorkload_123"

  - `editAppSetQosConfigInput` (object,null)
    Edit QoS Configuration Input (Applicable for OS version 10.4.0 and later)

  - `editAppSetQosConfigInput.action` (string, required)
    QoS Action
    Enum: "ADD_QOS", "EDIT_QOS", "REMOVE_QOS"

  - `editAppSetQosConfigInput.bandwidthMaxLimit` (number,null)
    The maximum bandwidth limit permitted for the volume set associated with this policy. The bandwidth maximum limit must be between 0 and 9,007,199,254,740,991 KB/s. Pass -1 to unset the parameter
    Example: 100

  - `editAppSetQosConfigInput.enable` (boolean,null)
    Enabling of QoS Configuration
    Example: true

  - `editAppSetQosConfigInput.enableSrAlert` (boolean,null)
    Sets the SR alert with the criterion name as the vvset name based on the max limits being set on the QoS parameters. If provided true, the SR alert criterion will be created or updated based on updated parameters. If provided false, the SR Alert criterion will be deleted if present. If enableSrAlert is not specified and the SR Alert criterion is already present for the volume set, the SR Alert criterion will be retained based on the updated QoS parameters.

  - `editAppSetQosConfigInput.iopsMaxLimit` (number,null)
    The maximum IOPS limit permitted for the volume set associated with this policy. The IOPS maximum limit must be between 0 and 2,147,483,647 IO/s. Pass -1 to unset the parameter
    Example: 1

  - `editAppSetQosConfigInput.perTb` (boolean,null)
    Sets the maximum IOPS limit or/and bandwidth limit for QoS throttling based on the number of terabytes configured for the volumes in the volume set on which QoS rule is configured.  By default, this option is off. Once per_tb is set, it cannot be unset (Applicable for storage systems with OS versions that are 10.4.0 or higher but below 10.5.0).
    Example: true

  - `ransomware` (boolean,null)
    This attribute enables/disables ransomware detection on the volume set. Both the existing volumes in the volume set as well as the volumes which get added in future in to this volume set will have this ransomware setting. If no input is provided, the existing ransomware setting on the volume set would stay. This applies to the HPE Alletra Storage MP B10000 systems running OS version 10.5.0 and later.
    Example: true

  - `removeMembers` (array,null)
    Members to remove from application set
    Example: ["vol1","vol2"]

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

## Response 404 fields (application/json):

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


