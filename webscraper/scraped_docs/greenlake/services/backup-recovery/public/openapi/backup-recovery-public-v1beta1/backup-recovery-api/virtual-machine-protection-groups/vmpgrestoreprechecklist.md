---
title: "POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/restore-pre-check"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgrestoreprechecklist.md"
scraped_at: "2026-06-07T06:14:06.363033+00:00Z"
---

# Restore pre-check of a virtual machine Protection Group from recovery points.

Validations and recovery point info of a virtual machine Protection Group.

Endpoint: POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/restore-pre-check
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Virtual Machine Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `resourceSummary` (object)
    Summary for dry run at individual resource level.

  - `resourceSummary.resourceInfo` (array)
    Summary for dry run at individual resource level.

  - `resourceSummary.resourceInfo.appType` (string)
    Type of the application to which the resource belongs.
    Enum: "VMWARE"

  - `resourceSummary.resourceInfo.clusterInfo` (object)

  - `resourceSummary.resourceInfo.clusterInfo.displayName` (string)
    A user-friendly name to identify the hypervisor cluster. This will always be same as name since add or update of hypervisor clusters are not supported when it is managed from a manager like vCenter.
    Example: "myesxcluster1"

  - `resourceSummary.resourceInfo.clusterInfo.id` (string)
    UUID string uniquely identifying the hypervisor cluster.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `resourceSummary.resourceInfo.clusterInfo.name` (string)
    Name of the cluster as reported by the hypervisor manager.
    Example: "myesxcluster1"

  - `resourceSummary.resourceInfo.clusterInfo.resourceUri` (string)
    The URI reference for this resource.

  - `resourceSummary.resourceInfo.clusterInfo.type` (string)
    The type of resource.

  - `resourceSummary.resourceInfo.datastoresInfo` (array)
    References to all datastores that hosts this resource.

  - `resourceSummary.resourceInfo.datastoresInfo.displayName` (string)
    A user friendly name to identify the datastore.
    Example: "Nimble-DS1"

  - `resourceSummary.resourceInfo.datastoresInfo.id` (string)
    UUID string uniquely identifying the datastore
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `resourceSummary.resourceInfo.datastoresInfo.name` (string)
    Name of the datastore as reported by the hypervisor manager.
    Example: "Nimble-DS2"

  - `resourceSummary.resourceInfo.errorMessage` (string)
    Error message if the VM or DS state is in Error state.

  - `resourceSummary.resourceInfo.hostInfo` (object)

  - `resourceSummary.resourceInfo.hostInfo.displayName` (string)
    A user-friendly name to identify the hypervisor host. This will always be same as name since add or update of hypervisor hosts is not supported when it is managed from a manager like vCenter.
    Example: "myESXi"

  - `resourceSummary.resourceInfo.hostInfo.id` (string)
    UUID string uniquely identifying the hypervisor host.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `resourceSummary.resourceInfo.hostInfo.name` (string)
    Name of the host as reported by the hypervisor manager.
    Example: "myESXi"

  - `resourceSummary.resourceInfo.recoveryPointInfo` (array)
    Recovery point information.

  - `resourceSummary.resourceInfo.recoveryPointInfo.backupGranularity` (string)
    Applicable only to backup copies. Specifies granularity at which the backup is created. The user can specify whether to create volume based backups or application Change Block Tracking (CBT) based backups.
    Enum: "VOLUME", "VMWARE_CBT"

  - `resourceSummary.resourceInfo.recoveryPointInfo.consistency` (string)
    Specifies whether this is crash consistent or application consistent recovery point.
    Enum: "CRASH", "APPLICATION"

  - `resourceSummary.resourceInfo.recoveryPointInfo.dataOrchestratorInfo` (array)

  - `resourceSummary.resourceInfo.recoveryPointInfo.dataOrchestratorInfo.id` (string)
    The id of the Data Orchestrator.

  - `resourceSummary.resourceInfo.recoveryPointInfo.dataOrchestratorInfo.resourceUri` (string)
    Example: "/backup-recovery/v1beta1/data-orchestrators/613a8115-00f4-4785-831f-f3b2183cdcb7"

  - `resourceSummary.resourceInfo.recoveryPointInfo.dataOrchestratorInfo.type` (string)
    Example: "backup-recovery/data-orchestrator"

  - `resourceSummary.resourceInfo.recoveryPointInfo.pointInTime` (string)
    Time in UTC at which the application backup
was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `resourceSummary.resourceInfo.recoveryPointInfo.recoveryPointId` (string)
    UUID string uniquely identifying the recovery point.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641yd"

  - `resourceSummary.resourceInfo.recoveryPointInfo.recoveryPointType` (string)
    The type of the recovery point.
    Enum: "SNAPSHOT", "BACKUP", "CLOUD_BACKUP"

  - `resourceSummary.resourceInfo.recoveryPointInfo.state` (string)
    The current state of the resource.
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING", "IN_USE"

  - `resourceSummary.resourceInfo.recoveryPointInfo.status` (string)
    status of the VM or DS.
    Enum: "OK", "ERROR"

  - `resourceSummary.resourceInfo.recoveryPointInfo.storageSystemInfo` (array)
    Information about storage system.

  - `resourceSummary.resourceInfo.recoveryPointInfo.storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `resourceSummary.resourceInfo.recoveryPointInfo.storageSystemInfo.name` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `resourceSummary.resourceInfo.recoveryPointInfo.storageSystemInfo.type` (string)
    Type of storage system.

  - `resourceSummary.resourceInfo.resourceId` (string)
    UUID string uniquely identifying the individual asset in the protection group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `resourceSummary.resourceInfo.resourceName` (string)
    Name of the VM or DS.

  - `resourceSummary.resourceInfo.storageSystemInfo` (object)
    Information about storage system where resource is created.

  - `resourceSummary.resourceInfo.storageSystemInfo.displayName` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `resourceSummary.resourceInfo.storageSystemInfo.resourceUri` (string)
    Reference to resource.

  - `summary` (object)
    Summary of the dry run at Protection Group level.

  - `summary.error` (string)
    Any Protection Group level error.

  - `summary.status` (string)
    status of the Protection Group.
    Enum: "OK", "ERROR"

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

## Response 409 fields (application/json):

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


