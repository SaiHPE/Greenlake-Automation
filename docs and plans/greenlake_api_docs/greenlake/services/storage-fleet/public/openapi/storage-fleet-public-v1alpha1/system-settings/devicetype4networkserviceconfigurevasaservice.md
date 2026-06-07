---
title: "POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa/{vasaId}/services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4networkserviceconfigurevasaservice.md"
scraped_at: "2026-06-07T06:16:06.329767+00:00Z"
---

# Configures vasa service for the specified id.

Enables, disable, updates the cert management mode for VASA services on an HPE Alletra Storage MP B10000 storage system. It also provides the ability to configure the batch parameters for VASA services and set up the second VASA Provider (VP) on a HPE Alletra Storage MP B10000 storage system from OS version 10.5.0 and later.

Endpoint: POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa/{vasaId}/services
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `vasaId` (string, required)
    ID of the VASA service
    Example: "a9c455bf98fc1a6bdb90b824e3ac20b8"

## Request fields (application/json):

  - `certMgmt` (string,null)
    Specify the cert mode for vasa provider, supports values server, locked_client or multi_vc. multi_vc is supported from OS version 10.4.0 and Vasa version 5.0.0.0
    Example: "server"

  - `cfgList` (array,null)
    A list of key/value pairs describing the configuration of the VASA service. This is supported from OS version 10.5.0 and vasa version 5.0.0.0 onwards.

  - `cfgList.key` (string,null)
    vasa batch size parameters:
- maxConcurrentRequestsPerSession: Specifies the maximum concurrent VASA requests supported per session. 
- maxBindVirtualVolume: Specifies the maximum batch size of bindVirtualVolume API. BindVirtualVolume call returns details about protocol endpoint virtual volume(vVols) are bound to.
- maxSnapshotVirtualVolume: Specifies the maximum batch size of snapshotVirtualVolume API. SnapshotVirtualVolume call creates a consistent snapshot of a given virtual volume(vVol) on the specified storage container.
- maxQueryVirtualVolumeInfo: Specifies the maximum batch size of queryVirtualVolumeInfo API. QueryVirtualVolumeInfo call returns virtual volume(vVol) information for a given set of vVol objects. 
- maxUnbindVirtualVolume: Specifies the maximum batch size of unbindVirtualVolume API. UnbindVirtualVolume call unbinds the virtual volume(vVol) from its ESXi host, after finishing remaining I/O requests.
- maxUpdateVirtualVolumeMetdataEx: Specifies the maximum batch size of updateVirtualVolumeMetdataEx API. UpdateVirtualVolumeMetdataEx call updates the stored metadata of multiple virtual volume(vVols) in a storage container. 
- maxSpaceStatsForVirtualVolume: Specifies the maximum batch size of spaceStatsForVirtualVolume API. SpaceStatsForVirtualVolume call reports space usage and related information for the specified set of virtual volume(vVols).
- maxGetTaskUpdateEx: Specifies the maximum batch size of getTaskUpdateEx API. GetTaskUpdateEx call returns task update from array of specific task IDs.
    Enum: "maxConcurrentRequestsPerSession", "maxBindVirtualVolume", "maxSnapshotVirtualVolume", "maxQueryVirtualVolumeInfo", "maxUnbindVirtualVolume", "maxUpdateVirtualVolumeMetdataEx", "maxSpaceStatsForVirtualVolume", "maxGetTaskUpdateEx"

  - `cfgList.value` (string,null)
    value of the vasa batch size parameter:
- maxConcurrentRequestsPerSession: Value can be in the range of 0 to 8. The default value is 4.
- maxBindVirtualVolume: Value can be in the range of 0 to 1024. The default value is 16.
- maxSnapshotVirtualVolume: Value can be in the range of 0 to 1024. The default value is 16.
- maxQueryVirtualVolumeInfo: Value can be in the range of 0 to 1024. The default value is 16.
- maxUnbindVirtualVolume: Value can be in the range of 0 to 1024. The default value is 16.
- maxUpdateVirtualVolumeMetdataEx: Value can be in the range of 0 to 1024. The default value is 16.
- maxSpaceStatsForVirtualVolume: Value can be in the range of 0 to 1024. The default value is 16.
- maxGetTaskUpdateEx: Value can be in the range of 0 to 1024. The default value is 16.
    Example: "16"

  - `nodeId` (string,null)
    Secondary VASA Provider Node. Specifies the node id for which vasa service is to be configured. This will be non-network master node. After associating the second VASA Provider (VP) to the specific node then this information is used to start second instance of the VP to achieve VPHA. This configuration will provide high availability of the connection between storage device and vSphere client and minimize service downtime during failures. Applicable for HPE Alletra Storage MP B10000 storage system with 10.5.0 version and later.
    Example: "0"

  - `vasaStateEnabled` (boolean,null)
    Specify the status of vasa service.
    Example: true

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


