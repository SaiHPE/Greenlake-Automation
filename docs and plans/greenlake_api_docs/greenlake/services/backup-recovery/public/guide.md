---
title: "HPE GreenLake for Backup and Recovery Developer Guide"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/guide.md"
scraped_at: "2026-06-07T06:13:21.834304+00:00Z"
---

# HPE GreenLake for Backup and Recovery Developer Guide

Backup and Recovery service supports protecting and recovering on-premise applications like VMware virtual machines, MS SQL databases and Block Storage Volumes through REST APIs directly. The following sections give examples of the commonly required endpoints for protection and recovery and the sequence in which they are generally exercised.

## Prerequisites

### Endpoints

Endpoints are the host URLs that you submit your API requests to. Backup and Recovery has unique endpoints in specific regions. Use the following list to identify your application endpoint.

- US West: [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)
- EU West : [https://eu-west.api.greenlake.hpe.com](https://eu-west.api.greenlake.hpe.com)
- EU Central: [https://eu-central.api.greenlake.hpe.com](https://eu-central.api.greenlake.hpe.com)
- AP NorthEast: [https://ap-northeast.api.greenlake.hpe.com](https://ap-northeast.api.greenlake.hpe.com)


## Making It All Work

### General Guidelines

- For an asynchronous operation returning http status as 201 or 202, the location header of the asynchronous API response contains the tasks URI to track the progress of the operation.


### Setting up the required on-premises components

#### Activating a Data Orchestrator

A Data Orchestrator can be activated by providing an Activation Code (retrieved by completing the first-run-wizard post deployment of the Data Orchestrator) to the following API:


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/data-orchestrators
```

Payload:


```payload
{
  "activationCode": "90d8db77-d956-493f-9a13-1a9dd84cd785",
  "displayName": "string"
}
```

The endpoint [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com) is the endpoint for the US West application. If you are using Backup and Recovery in a different region, replace the endpoint with the endpoint the corresponding region.

#### Listing a Data Orchestrator


```request
GET https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/data-orchestrators/{id}
```

The response contains details of the Data Orchestrator properties. Some of the important ones are:

- Connection State
- ID
- Network Address
- Display Name


#### Deploying the Protection Store Gateway

Protection Store Gateways are the virtual appliances that are deployed and managed from the service to be used as backup targets. Use the Backup and Recovery UI to deploy a Protection Store Gateway VM.
API support for deploying the Protection Store Gateway will be available soon.

#### Registering a StoreOnce

To use a physical StoreOnce device as a backup target with the Backup and Recovery service, the StoreOnce needs to be registered. The following is a sample registration REST API:


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/storeonces
```

Payload:


```request
{
  "credentials": {
    "password": "string",
    "username": "string"
  },
  "description": "string",
  "name": "string",
  "networkAddress": "string",
  "serialNumber": "string"
}
```

#### Registration of on-premises infrastructure

For protecting on-premises assets, the on-premises infrastructure must be registered with the service. This can include VMware vCenter or a Windows Application Server running
Microsoft SQL. For protecting HPE Array Volumes, the supported HPE arrays need to be onboarded to GreenLake Cloud Platform.

#### Registering a new hypervisor manager

To register a hypervisor manager (vCenter) with the Backup and Recovery service, you need to provide credentials, network address/FQDN, and a Data Orchestrator ID.


```curl
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1alpha1/hypervisor-managers
```

Payload:


```payload
{
  "credentials": {
    "password": "string",
    "username": "string"
  },
  "dataOrchestratorId": "8b4c14a6-3cd5-4907-97c4-cf44c5b642e5",
  "description": "string",
  "displayName": "myvcenter1",
  "hypervisorManagerType": "VMWARE_VCENTER",
  "networkAddress": "192.168.0.1"
}
```

#### Registering a Microsoft SQL Server Application Host


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/application-hosts
```

Payload:


```payload
{
  "credentials": {
    "password": "string",
    "username": "string"
  },
  "description": "string",
  "name": "host123.hpe.com",
  "networkAddress": "192.168.0.1",
  "platform": "WINDOWS",
  "virtual": true
}
```

### Protection Groups

A Protection Group is a Backup and Recovery feature that enables you to group a set of resources that require a similar level of protection. Using Protection Groups makes it easier to administer protection tasks and to ensure protection compliance. There are two types of Protection Groups: automatic and custom.

Backup and Recovery supports Protection Groups for the following applications:

- **VMWare**
Protection Groups can be created with the following VMware entities:
  - Virtual Machine folders
  - Storage folders (datastores)
  - vVol containers
  - Storage Replication group
- **MSSQL**
Protection groups can be created with any of the following resources:
  - MSSQL Instance
  - Availability Group
- **HPE Array Volumes**
You can create Protection Groups with HPE Array Volumes.


#### Creating a Virtual Machine Protection Group


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/virtual-machine-protection-groups
```

Payload:


```payload
{
  "assets": [
    {
      "id": "string",
      "type": "virtualization/datastore"
    }
  ],
  "assetsCategory": "VVOL_VMS",
  "description": "string",
  "dynamicMemberFilter": {
    "members": [
      {
        "name": "Tag name",
        "type": "string"
      }
    ]
  },
  "name": "myProtectionGroup",
  "nativeAppInfo": {
    "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
    "type": "VMWARE_FOLDER"
  },
  "vmProtectionGroupType": "NATIVE"
}
```

**Note**: The List of Virtual Machines needed to create the Protection Group, can be obtained via below API:


```request
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines
```

#### Creating a MSSQL Database Protection Group


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/mssql-database-protection-groups
```

Payload:


```payload
{
  "excludeSystemDatabases": true,
  "id": "string",
  "type": "MSSQL_INSTANCE",
  "uid": "string",
  "description": "string",
  "members": [
    {
      "resourceUri": "string"
    }
  ],
  "name": "My-Test-PG",
  "nativeAppInfo": {
    "excludeSystemDatabases": true,
    "id": "string",
    "type": "MSSQL_INSTANCE",
    "uid": "string"
  },
  "protectionGroupType": "NATIVE"
}
```

**Note**: The List of Databases needed to create a MSSQL Database Protection Group, can be obtained via below API:


```request
GET https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/mssql-databases
```

#### Creating a Volume Protection Group


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/volume-protection-groups
```

Payload:


```payload
{
  "description": "string",
  "nativeGroupInfo": {
    "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
    "name": "volume protection native group."
  },
  "storageSystemInfo": {
    "id": "6a38acc7-e470-4ed7-b141-ca9509672dac"
  },
  "volumeProtectionGroupType": "NATIVE"
}
```

### Protection Policies

A Protection Policy is a collection of protection rules that defines the creation and life-cycle management of the protection backups. Protection polices include:

- The type of backups to create, which can be storage array based snapshots, on-premises backups, AWS snapshots, or cloud backups (HPE managed cloud backups)
- The destination of the backup (on-premises protection store or cloud protection store)
- The frequency and start time of the backup creation
- The backup expiration time


#### Creating a Protection Policy

The following is an example of Protection Policy creation using the API:


```curl
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/protection-policies
```

Payload:


```payload
{
  "description": "Protection Policy protecting Finance department's Virtual Machines or datastores.",
  "name": "Gold-Protection-Policy",
  "protections": [
    {
      "applicationType": "VMWARE",
      "protectionStoreId": "2a1172be-4281-44f9-848b-9c3f86378b13",
      "schedules": [
        {
          "expireAfter": {
            "unit": "HOURS",
            "value": 1
          },
          "lockFor": {
            "unit": "HOURS",
            "value": 1
          },
          "name": "Hourly snapshot schedule",
          "namePattern": {
            "format": "Test_{SourceAssetName}_Copy_{DateFormat}"
          },
          "postScriptInfo": {
            "hostId": "string",
            "params": "string",
            "path": "string",
            "timeoutInSeconds": 0
          },
          "preScriptInfo": {
            "hostId": "string",
            "params": "string",
            "path": "string",
            "timeoutInSeconds": 0
          },
          "schedule": {
            "activeTime": {
              "activeFromTime": "16:15",
              "activeUntilTime": "20:15"
            },
            "recurrence": "BY_MINUTES",
            "repeatInterval": {
              "every": 0,
              "on": [
                0
              ]
            },
            "startTime": "16:35"
          },
          "scheduleId": 0,
          "sourceProtectionScheduleId": 0,
          "verify": true
        }
      ],
      "type": "SNAPSHOT"
    }
  ]
}
```

#### Protecting assets and Protection Groups using Protection Jobs

An individual asset or a Protection Group can be protected by creating a Protection Job. A Protection Job associates a Protection Policy with an asset or a Protection Group.

#### Protecting a Virtual Machine Protection Group


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/protection-jobs
```

Payload:


```payload
{
  "assetInfo": {
    "id": "d0e48314-730a-11ea-b496-48452098762c",
    "type": "backup-recovery/virtual-machine-protection-group"
  },
  "effectiveFromDateTime": "2020-03-03T05:03:08.902Z",
  "overrides": {
    "protections": [
      {
        "id": "2a1172be-4281-44f9-848b-9c3f86378b13",
        "protectionStoreId": "2a1172be-4281-44f9-848b-9c3f86378b13",
        "schedules": [
          {
            "backupGranularity": "VOLUME",
            "consistency": "APPLICATION",
            "continueProtectionPostFailover": true,
            "createSnapshotOnFailure": true,
            "expireAfter": {
              "unit": "HOURS",
              "value": 1
            },
            "lockFor": {
              "unit": "HOURS",
              "value": 1
            },
            "namePattern": {
              "format": "Test_{SourceAssetName}_Copy_{DateFormat}"
            },
            "postScriptInfo": {
              "params": "string"
            },
            "preScriptInfo": {
              "params": "string"
            },
            "scheduleId": 0,
            "verify": true,
            "vmwareOptions": {
              "includeRdmDisks": true
            }
          }
        ]
      }
    ]
  },
  "protectionPolicyId": "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"
}
```

#### Protecting a MSSQL Database Protection Group


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/protection-jobs
```

Payload:


```payload
{
  "assetInfo": {
    "id": "d0e48314-730a-11ea-b496-48452098762c",
    "type": "backup-recovery/mssql-database-protection-group"
  },
  "effectiveFromDateTime": "2020-03-03T05:03:08.902Z",
  "overrides": {
    "protections": [
      {
        "id": "2a1172be-4281-44f9-848b-9c3f86378b13",
        "protectionStoreId": "2a1172be-4281-44f9-848b-9c3f86378b13",
        "schedules": [
          {
            "backupGranularity": "VOLUME",
            "consistency": "APPLICATION",
            "continueProtectionPostFailover": true,
            "createSnapshotOnFailure": true,
            "expireAfter": {
              "unit": "HOURS",
              "value": 1
            },
            "lockFor": {
              "unit": "HOURS",
              "value": 1
            },
            "namePattern": {
              "format": "Test_{SourceAssetName}_Copy_{DateFormat}"
            },
            "postScriptInfo": {
              "params": "string"
            },
            "preScriptInfo": {
              "params": "string"
            },
            "scheduleId": 0,
            "verify": true,
            "vmwareOptions": {
              "includeRdmDisks": true
            }
          }
        ]
      }
    ]
  },
  "protectionPolicyId": "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"
}
```

#### Protecting a Volume Protection Group


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/protection-jobs
```

Payload:


```payload
{
  "assetInfo": {
    "id": "d0e48314-730a-11ea-b496-48452098762c",
    "type": "backup-recovery/volume-protection-group"
  },
  "effectiveFromDateTime": "2020-03-03T05:03:08.902Z",
  "overrides": {
    "protections": [
      {
        "id": "2a1172be-4281-44f9-848b-9c3f86378b13",
        "protectionStoreId": "2a1172be-4281-44f9-848b-9c3f86378b13",
        "schedules": [
          {
            "backupGranularity": "VOLUME",
            "consistency": "APPLICATION",
            "continueProtectionPostFailover": true,
            "createSnapshotOnFailure": true,
            "expireAfter": {
              "unit": "HOURS",
              "value": 1
            },
            "lockFor": {
              "unit": "HOURS",
              "value": 1
            },
            "namePattern": {
              "format": "Test_{SourceAssetName}_Copy_{DateFormat}"
            },
            "postScriptInfo": {
              "params": "string"
            },
            "preScriptInfo": {
              "params": "string"
            },
            "scheduleId": 0,
            "verify": true,
            "vmwareOptions": {
              "includeRdmDisks": true
            }
          }
        ]
      }
    ]
  },
  "protectionPolicyId": "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"
}
```

#### Recovering a Virtual Machine

A virtual machine can be recovered from a backup or a snapshot copy.


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/virtual-machines/{id}/restore
```

Payload:


```payload
{
  "backupId": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
  "restoreType": "PARENT",
  "targetVmInfo": {
    "appInfo": {
      "vmware": {
        "datacenterId": "string",
        "datastoreId": "string",
        "resourcePoolId": "string"
      }
    },
    "clusterId": "string",
    "description": "string",
    "folderId": "string",
    "hostId": "string",
    "hypervisorManagerId": "string",
    "name": "vm-1-windows",
    "powerOn": true,
    "storageInfo": {
      "storageSystemId": "string"
    },
    "vmHardwareCustomization": {
      "networkAdapters": [
        {
          "name": "string",
          "networkDetails": {
            "connectAtPowerOn": true,
            "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"
          }
        }
      ]
    }
  }
}
```

**Note**: Granular recovery of virtual disks and files is also supported

#### Recovering a MSSQL database from a backup


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/mssql-databases/{db-id}/restore
```

Payload:


```payload
{
  "backupId": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
  "recoveryMode": "WITH_RECOVERY",
  "restoreType": "PARENT",
  "restoreUntil": "2020-03-03T06:03:08.902Z",
  "restoreWithTailLog": false,
  "targetDatabaseInfo": {
    "databaseFilePaths": [
      {
        "newPath": "string",
        "originalPath": "string"
      }
    ],
    "instanceId": "string"
  }
}
```

**Note**: Point in Time Recovery based on MSSQL Transaction Log Backups is also supported

#### Recover a Volume Protection Group from a backup


```request
POST https://us-west.api.greenlake.hpe.com/backup-recovery/v1beta1/volume-protection-groups/{id}/restore
```

Payload:


```payload
{
  "individualBackupIds": [
    "string"
  ],
  "individualSnapshotIds": [
    "string"
  ],
  "restoreType": "PARENT",
  "targetStorageSystemId": "6a38acc7-e470-4ed7-b141-ca9509672dac",
  "vpgBackupId": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
}
```