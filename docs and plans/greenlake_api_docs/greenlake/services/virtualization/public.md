---
title: "HPE GreenLake for Virtualization"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public.md"
scraped_at: "2026-06-07T05:46:15.929238+00:00Z"
---

# HPE GreenLake for Virtualization

This page provides an introduction and quick start guide for the Virtualization API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

The HPE GreenLake for Virtualization API provides management of virtual machines
and other virtual resources in public clouds and on-premises systems.

The API allows you to:

- Manage virtual machines in the private cloud like VMware
- Manage virtual machines in the public cloud like AWS and Azure
- Register and manage datastores.
- Migrate virtual machines to another cluster or datastore


### Features

The Virtualization APIs are broadly classified into the following categories:

- Life cycle management of virtual machines in the private cloud (VMware)
- Life cycle management of virtual machines in the public cloud (AWS and Azure)
- Datastore management
- VM migration


## Developer guide

The HPE GreenLake for Virtualization API provides management of virtual machines
and other virtual resources in public clouds and on-premises systems.

The prerequisites section covers the endpoints, authentication, authorization, and required permissions for each API category. The Making it all work section provides step-by-step code samples for deploying and managing virtual machines in both private and public clouds, as well as datastore management and VM migration.

### Prerequisites

#### Endpoints

Endpoints are the host URLs that you will submit your API requests to.
Private Cloud Business Edition has unique endpoints in specific regions.
Use the following list to identify your application endpoint.

- US West: [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)
- EU West: [https://eu-west.api.greenlake.hpe.com](https://eu-west.api.greenlake.hpe.com)
- EU Central: [https://eu-central.api.greenlake.hpe.com](https://eu-central.api.greenlake.hpe.com)
- AP NorthEast: [https://ap-northeast.api.greenlake.hpe.com](https://ap-northeast.api.greenlake.hpe.com)


#### Authentication

The Private Cloud Business Edition API uses an access token for authentication. Instructions
for obtaining an access token can be found on the [Authentication](/docs/greenlake/guides/public/authentication/authentication)
page.

The HTTP Authorization request header is used to provide the access token in
all API requests as a Bearer token.

- `Authorization:Bearer <access token>`


#### Authorization

All API requests are authorized using permissions. The user owning the access
token must have the required permissions assigned for the resources being accessed
in order to be authorized. The required permissions are documented in the
following guide pages.

#### URIs and permissions

##### Life cycle management of virtual machines in the private cloud (VMware)

The private cloud APIs can be used to manage virtual machines in the private cloud.

###### URIs

- `/virtualization/v1beta1/hypervisor-managers`
- `/virtualization/v1beta1/hypervisor-managers/{id}`
- `/virtualization/v1beta1/hypervisor-clusters`
- `/virtualization/v1beta1/hypervisor-clusters/{id}`
- `/virtualization/v1beta1/hypervisor-hosts`
- `/virtualization/v1beta1/hypervisor-hosts/{id}`
- `/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-folders`
- `/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-folders/{id}`
- `/virtualization/v1beta1/virtual-machines`
- `/virtualization/v1beta1/virtual-machines/{id}`
- `/virtualization/v1beta1/virtual-machines/{id}/power-off`
- `/virtualization/v1beta1/virtual-machines/{id}/power-on`
- `/virtualization/v1beta1/virtual-machines/{id}/reset`
- `/virtualization/v1beta1/virtual-machines/{id}/shutdown-guest-os`
- `/virtualization/v1beta1/virtual-machines/{id}/restart-guest-os`
- `/virtualization/v1beta1/virtual-machines/{id}/update-hardware`
- `/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images`
- `/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images/{id}`


###### Permissions

- `data-services.datastore.read`
- `data-services.hci-cluster.read`
- `data-services.hypervisor-cluster.read`
- `data-services.hypervisor-folder.read`
- `data-services.hypervisor-host.read`
- `data-services.hypervisor-manager.read`
- `data-services.hypervisor-resource-pool.read`
- `data-services.virtual-machine.read`
- `data-services.vm-provisioning-policy.read`
- `data-services.vm-provisioning-policy.apply`
- `data-services.protection-job.create`
- `data-services.protection-policy.read`
- `data-services.virtual-machine.create`
- `data-services.virtual-machine.delete`
- `data-services.virtual-machine.update`
- `data-services.virtual-machine.power-on`
- `data-services.virtual-machine.power-off`
- `data-services.virtual-machine.update`
- `data-services.virtual-machine.storageprofile-update`
- `data-services.task.read`
- `data-services.hypervisor-library-images.read`


##### Life cycle management of virtual machines in the public cloud (AWS and Azure)

The public cloud APIs can be used to manage virtual machines in the public cloud.

###### URIs

- `/virtualization/v1beta1/csp-machine-images`
- `/virtualization/v1beta1/csp-machine-images/{id}`
- `/virtualization/v1beta1/csp-machine-instance-types`
- `/virtualization/v1beta1/csp-machine-instance-types/{id}`
- `/virtualization/v1beta1/csp-machine-instances`
- `/virtualization/v1beta1/csp-machine-instances/{id}`
- `/virtualization/v1beta1/csp-machine-instances/{id}/power-off`
- `/virtualization/v1beta1/csp-machine-instances/{id}/power-on`


###### Permissions

- `data-services.csp-machine-image.read`
- `data-services.csp-machine-instance-type.read`
- `data-services.csp-machine-instance.create`
- `data-services.csp-machine-instance.terminate`
- `data-services.csp-machine-instance.power-on`
- `data-services.csp-machine-instance.power-off`


##### Datastore management

Allows the registration and management of datastores.

###### URIs

- `/virtualization/v1beta1/datastores`
- `/virtualization/v1beta1/datastores/{id}`


###### Permissions

- `data-services.datastore.read`
- `data-services.datastore.create`
- `data-services.hci-cluster.read`
- `data-services.hypervisor-cluster.read`
- `data-services.hypervisor-folder.read`
- `data-services.hypervisor-host.read`
- `data-services.hypervisor-manager.read`
- `data-services.hypervisor-resource-pool.read`
- `data-services.storage-pool.read`
- `data-services.virtual-machine.read`
- `data-services.vm-provisioning-policy.read`
- `data-services.vm-provisioning-policy.apply`
- `data-services.protection-job.create`
- `data-services.virtual-machine-protection-group.create`
- `data-services.virtual-machine-protection-group.read`
- `data-services.task.read`
- `data-services.datastore.delete`
- `data-services.protection-policy.read`
- `data-services.storage-system.read`


##### VM migration

Allows migration of virtual machines to another cluster or datastore.

###### URIs

- `/virtualization/v1beta1/virtual-machines/migrate`


###### Permissions

- `data-services.datastore.read`
- `data-services.hci-cluster.read`
- `data-services.hypervisor-cluster.read`
- `data-services.hypervisor-manager.read`
- `data-services.hypervisor-resource-pool.read`
- `data-services.virtual-machine.read`
- `data-services.virtual-machine.relocate`
- `data-services.vm-provisioning-policy.read`
- `data-services.virtual-machine-snapshot.read`
- `data-services.protection-job.delete`


### Making it all work

#### Deploy a virtual machine in the private cloud

To deploy a virtual machine in the private cloud:

- List and select the hypervisor cluster `id` for the chosen hypervisor-manager
- List and select the datastore `id` for the selected hypervisor cluster
- List the hypervisor library images on the hypervisor manager and select image `id` to deploy
- Call the deploy virtual machine API with the selected resources and wait for the task to get complete
- List the virtual machines on the hypervisor manager to confirm that the virtual machine is created


##### List hypervisor clusters

Get all clusters across registered hypervisor managers and select the cluster `id` to deploy.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/hypervisor-clusters
```


```json
{
  "count": 1,
  "items": [
    {
      "appInfo": {
        "vmware": {
          "datacenterInfo": {
            "id": "16245bf7-2b35-5580-86a6-620faa5b5403",
            "moref": "datacenter-2",
            "name": "core-team-dc"
          },
          "moref": "domain-c8"
        }
      },
      "clusterPerfMetricInfo": {
        "cpuCapacityInMhz": 0,
        "cpuUsageInMhz": 0,
        "memorySizeInBytes": 0,
        "memoryUsageInMb": 0,
        "totalStorageInBytes": 0,
        "usedStorageInBytes": 0
      },
      "clusterType": "ESX_CLUSTER",
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "string",
      "displayName": "myesxcluster1",
      "generation": 0,
      "hciClusterUuid": "string",
      "hypervisorHosts": [
        {
          "displayName": "myESXi",
          "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
          "name": "myESXi",
          "resourceUri": "string",
          "type": "string"
        }
      ],
      "hypervisorManagerInfo": {
        "displayName": "myvcenter1",
        "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
        "name": "vcenter123.hpe.com",
        "resourceUri": "string",
        "type": "string"
      },
      "id": "555666a6-3cd5-4907-97c4-cf44c5b641e4",
      "name": "myesxcluster1",
      "networksInfo": [
        "network-2053",
        "network-1005"
      ],
      "resourceUri": "/virtualization/v1beta1/hypervisor-clusters/{cluster-id}",
      "services": [
        "hci-manager",
        "backup-and-recovery"
      ],
      "state": "OK",
      "stateReason": "string",
      "status": "OK",
      "type": "string",
      "updatedAt": "2019-08-24T14:15:22Z"
    }
  ],
  "offset": 0,
  "total": 1
}
```

##### List datastores

Get all datastores for the registered hypervisor managers and select a datastore in the destination cluster.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/datastores
```


```json
{
  "count": 1,
  "items": [
    {
      "allowedOperations": [
        "DATASTORE_CREATE",
        "DATASTORE_DELETE"
      ],
      "appType": "VMWARE",
      "capacityFree": 76534,
      "capacityInBytes": 2407653459860,
      "capacityUncommitted": 653422,
      "clusterInfo": {
        "displayName": "myesxcluster1",
        "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
        "name": "myesxcluster1",
        "resourceUri": "string",
        "type": "string"
      },
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "string",
      "datacentersInfo": [
        {
          "id": "16245bf7-2b35-5580-86a6-620faa5b5403",
          "moref": "datacenter-2",
          "name": "core-team-dc"
        }
      ],
      "datastoreClassification": "PROTECTION_STORE_GATEWAY",
      "datastoreType": "VMFS",
      "displayName": "Nimble-DS1",
      "folderInfo": {...},
      "generation": 0,
      "hciClusterUuid": "754f63f7-1016-40ec-9b8f-610f978b9aec",
      "hostsInfo": [
        {
          "displayName": "myESXi",
          "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
          "name": "myESXi",
          "resourceUri": "string",
          "type": "string"
        }
      ],
      "hypervisorManagerInfo": {
        "displayName": "myvcenter1",
        "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
        "name": "vcenter123.hpe.com",
        "resourceUri": "string",
        "type": "string"
      },
      "id": "888c14a6-3cd5-4907-97c4-cf44c5b641e4",
      "moref": "datastore-1234",
      "name": "Nimble-DS2",
      ...
      ...
      "state": "OK",
      "stateReason": "string",
      "status": "OK",
      "type": "string",
      "uid": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
      "updatedAt": "2019-08-24T14:15:22Z",
      "vmCount": 120,
      "vmProtectionGroupsInfo": [..],
      "volumesInfo": [..]
      ]
    }
  ],
  "offset": 0,
  "total": 1
}
```

##### List hypervisor library images

Get all virtual machine images from the hypervisor library.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/hypervisor-managers
```


```json
{
  "count": 1,
  "items": [
    {
      "createdAt": "2022-02-04T07:43:27Z",
      "customerId": "90299b6c06aa283091cd4a89298b5471",
      "description": "This is a sample virtual machine image description",
      "displayName": "CentOS.ova",
      "fileType": "OVF",
      "generation": 0,
      "hypervisorManagerInfo": {
        "displayName": "myvcenter1",
        "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
        "name": "vcenter123.hpe.com",
        "resourceUri": "string",
        "type": "string"
      },
      "id": "22233328-d128-519c-a2ac-a4932ff2109b",
      "libraryName": "LibraryImages",
      "name": "Centos.ova",
      "resourceUri": "The URI reference for this resource.",
      "size": 15344,
      "subscribed": false,
      "type": "HypervisorLibraryImages",
      "uid": "9476c228-d128-519c-a2ac-a4932ff2109b",
      "updatedAt": "2022-02-04T08:43:27Z"
    }
  ],
  "offset": 0,
  "total": 1
}
```

##### Deploy a virtual machine

Deploy a virtual machine in the private cloud with the selected image from the hypervisor image library.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines
```

Payload:


```json
{
  "destination": {
    "clusterId": "555666a6-3cd5-4907-97c4-cf44c5b641e4",
  },
  "imageSource": {
    "imageId": "22233328-d128-519c-a2ac-a4932ff2109b",
    "imageName": "Centos.ova",
    "imageSourceType": "HYPERVISOR_IMAGE_LIBRARY"
  },
  "storageConfig": {
    "defaultDatastoreId": "888c14a6-3cd5-4907-97c4-cf44c5b641e4",
    "provisioningType": "THIN"
  },
  "vmConfig": {
    "acceptEula": true,
    "annotation": "test virtual machine",
    "name": "testVM",
    "numberOfVms": 1,
    "powerOn": true,
  },
}
```


```bash header
HTTP/2 202
location: /data-services/v1beta1/async-operations/8e594a77-3809-4620-be52-74270abdf60b
```

If there are errors in the input parameters, the request immediately fails with a 4XX error and the details of the failure.

If the request is accepted with a 202 response and subsequently the deploy virtual machine async operation fails for any reason, the details of the failure are captured in the async operation obtained by querying the URI in the `location` header. Take corrective actions as needed and rerun the operation.

##### Deploy a virtual machine on a specified host and virtual machine folder

Select a folder and host on the registered hypervisor manager.

List all hosts on the registered hypervisor manager:


```bash
https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/hypervisor-hosts
```

List the folder on the specified hypervisor manager (`hypervisor-id`).


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/folders/
```

Specify the `folder_id` and `host_id` for the virtual machine deploy payload.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines
```

Payload:


```json
{
  "destination": {
    "folderId": "string",
    "hostId": "string",
  },
  "imageSource": {
    "imageId": "22233328-d128-519c-a2ac-a4932ff2109b",
    "imageName": "Centos.ova",
    "imageSourceType": "HYPERVISOR_IMAGE_LIBRARY"
  },
  "storageConfig": {
    "defaultDatastoreId": "888c14a6-3cd5-4907-97c4-cf44c5b641e4",
    "provisioningType": "THIN"
  },
  "vmConfig": {
    "acceptEula": true,
    "annotation": "test virtual machine",
    "name": "testVM",
    "numberOfVms": 1,
    "powerOn": true,
  },
}
```

##### Deploy a virtual machine with provisioning policy

List provisioning policies:


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/vm-provisioning-policies
```

Select a provisioning policy and append `vmPolicy` in the payload for virtual machine deployment.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines
```

Payload:


```json
{
  "destination": {
    "clusterId": "555666a6-3cd5-4907-97c4-cf44c5b641e4",
  },
  "imageSource": {
    "imageId": "22233328-d128-519c-a2ac-a4932ff2109b",
    "imageName": "Centos.ova",
    "imageSourceType": "HYPERVISOR_IMAGE_LIBRARY"
  },
  "storageConfig": {
    "defaultDatastoreId": "888c14a6-3cd5-4907-97c4-cf44c5b641e4",
    "provisioningType": "THIN"
  },
  "vmConfig": {
    "acceptEula": true,
    "annotation": "test virtual machine",
    "name": "testVM",
    "numberOfVms": 1,
    "powerOn": true,
  },
  "vmPolicy": [
  {
    "id": "12345678-3cd5-4907-97c4-cf44c5b641e4",
    "type": "VM_PROTECTION_POLICY"
  }
]
}
```

##### Listing the virtual machines

List all virtual machines on the destination hypervisor manager.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines?filter="hypervisorManagerInfo/id eq 9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"
```


```json
{
  "count": 1,
  "items": [
    {
      "allowedOperations": [
        "VIRTUAL_MACHINE_POWER_ON",
        "VIRTUAL_MACHINE_POWER_OFF"
      ],
      "appInfo": {
        "vmware": {
          "datacenterInfo": {
            "id": "16245bf7-2b35-5580-86a6-620faa5b5403",
            "moref": "datacenter-2",
            "name": "core-team-dc"
          },
          "datastoresInfo": [
            {
              "displayName": "Nimble-DS1",
              "id": "888c14a6-3cd5-4907-97c4-cf44c5b641e4",
              "name": "Nimble-DS2",
              "resourceUri": "string",
              "type": "string"
            }
          ],
          "moref": "vm-21",
          ...
        }
      },
      "appType": "VMWARE",
      "capacityInBytes": 2407653459860,
      "clusterInfo": {
        "displayName": "myesxcluster1",
        "id": "555666a6-3cd5-4907-97c4-cf44c5b641e4",
        "name": "myesxcluster1",
        "resourceUri": "string",
        "type": "string"
      },
      "computeInfo": {...},
      "createdAt": "2019-08-24T14:15:22Z",
      ...
      "hypervisorManagerInfo": {
        "displayName": "myvcenter1",
        "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
        "name": "vcenter123.hpe.com",
        "resourceUri": "string",
        "type": "string"
      },
      "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
      "name": "testVM",
      "networkAdapters": [
        ...
      ],
      "networkAddress": "string",
      "powerState": "POWERED_ON",
      ...
      "vclsVm": false,
      "virtualDisks": [
        ...
        ...
      ],
      "volumesInfo": [
        {
          ...
          ...
        }
      ]
    }
  ],
  "offset": 0,
  "total": 1
}
```

##### Power operations on virtual machines

Power off a virtual machine.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines/{id}/power-off
```


```bash header
HTTP/2 202
location: /data-services/v1beta1/async-operations/822594a77-3809-4620-be52-74270abdf60b
```

If there are errors in the input parameters, the request immediately fails with a 4XX error and the details of the failure.

Similarly, other power operations are performed by providing the virtual machine identifier `id`.

Power on a virtual machine.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines/{id}/power-on
```

Reset a virtual machine.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines/{id}/reset
```

Reboot a guest operating system.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines/{id}/restart-guest-os
```

Gracefully shutdown a guest operating system.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines/{id}/shutdown-guest-os
```

##### Edit a virtual machine

You can edit compute settings, virtual network interfaces, and virtual disks for private cloud virtual machines using this API.

Private cloud virtual machines must be ==powered off== to edit them.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines/{id}/update-hardware
```

Sample payload to modify virtual CPU, virtual memory, virtual network interfaces, and virtual disks.


```json
{
  "cpuMemConfig": {
    "cpu": {
      "numOfCpus": 8,
      "numOfCoresPerSocket": 4
    },
    "memory": {
      "memoryInMb": 32768
    }
  },
  "networkAdapters": [
    {
      "operation": "ADD",
      "networkDetails": {
        "name": "VM Network",
        "type": "STANDARD_PORT_GROUP"
      },
      "connectAtPowerOn": true,
      "type": "VMXNET3"
    },
    {
      "operation": "DELETE",
      "name": "Network adapter 3"
    }
  ],
  "virtualDisks": [
    {
      "operation": "EDIT",
      "diskConfig": {
        "id": "532ded6c-21d2-59cf-8a1e-4fcab371759c",
        "capacityInMb": 16384
      }
    },
    {
      "operation": "ADD",
      "diskConfig": {
        "type": "SCSI",
        "capacityInMb": 10240
      }
    }
  ]
}
```

This operation results in an asynchronous task returned in the response header.


```bash header
HTTP/2 202
location: /data-services/v1beta1/async-operations/{id}
```

From the returned response headers, use the `location` value to query for task completion state.


```bash
POST https://us-west.api.greenlake.hpe.com/data-services/v1beta1/async-operations/{id}
```


```json
{
   "associatedResources" : [],
   "createdAt" : "2024-05-01T19:28:37.065215852Z",
   "customerId" : "a3f60ff294db11ec9c3862726d3162bb",
   "displayName" : "Reconfigure virtual machine testVM",
   "endedAt" : "2024-05-01T19:29:01.500105076Z",
   "error" : null,
   "estimatedRunningDurationMinutes" : 0,
   "generation" : 21,
   "groups" : [
      {
         "id" : "a3f60ff294db11ec9c3862726d3162bb",
         "name" : "Default Group"
      }
   ],
   "hasChildOperations" : true,
   "healthStatus" : "OK",
   "id" : "d33e9083-cf1e-48f0-893b-b6eb322bc469",
   "logMessages" : [
      {
         "message" : "Task created",
         "timestamp" : "2024-05-01T19:28:37.065230061Z"
      },
      {
         "message" : "Task is running",
         "timestamp" : "2024-05-01T19:28:37.065232485Z"
      },
      {
         "message" : "Reconfigure CPU/Memory",
         "timestamp" : "2024-05-01T19:28:38.144990563Z"
      },
      {
         "message" : "Reconfigure CPU/Memory operation is completed",
         "timestamp" : "2024-05-01T19:28:41.305955879Z"
      },
      {
         "message" : "Adding network adapter of type: 'VMXNET3'",
         "timestamp" : "2024-05-01T19:28:41.643070059Z"
      },
      {
         "message" : "Adding network adapter of type: 'VMXNET3' is completed.",
         "timestamp" : "2024-05-01T19:28:48.50165466Z"
      },
      {
         "message" : "Deleting network adapter: 'Network adapter 3'",
         "timestamp" : "2024-05-01T19:28:48.717448654Z"
      },
      {
         "message" : "Deleting network adapter: 'Network adapter 3' is completed.",
         "timestamp" : "2024-05-01T19:28:52.925057333Z"
      },
      {
         "message" : "Initiating storage config modification",
         "timestamp" : "2024-05-01T19:28:52.952910871Z"
      },
      {
         "message" : "Editing disk: 'Hard disk 2'",
         "timestamp" : "2024-05-01T19:28:52.980078543Z"
      },
      {
         "message" : "Editing disk: 'Hard disk 2' is complete.",
         "timestamp" : "2024-05-01T19:28:58.07319753Z"
      },
      {
         "message" : "Adding disk of type: 'SCSI'",
         "timestamp" : "2024-05-01T19:28:58.10115551Z"
      },
      {
         "message" : "Adding disk of type: 'SCSI' is complete.",
         "timestamp" : "2024-05-01T19:29:01.442511292Z"
      },
      {
         "message" : "Storage config modification complete.",
         "timestamp" : "2024-05-01T19:29:01.469091726Z"
      },
      {
         "message" : "Reconfigure operation is completed",
         "timestamp" : "2024-05-01T19:29:01.500113112Z"
      },
      {
         "message" : "Task succeeded",
         "timestamp" : "2024-05-01T19:29:01.500118995Z"
      }
   ],
   "name" : "Reconfigure virtual machine testVM",
   "parent" : null,
   "progressPercent" : 100,
   "recommendations" : [],
   "resourceUri" : "/data-services/v1beta1/async-operations/d33e9083-cf1e-48f0-893b-b6eb322bc469",
   "rootOperation" : {
      "id" : "d33e9083-cf1e-48f0-893b-b6eb322bc469",
      "name" : "",
      "resourceUri" : "/data-services/v1beta1/async-operations/d33e9083-cf1e-48f0-893b-b6eb322bc469",
      "type" : "task"
   },
   "services" : [
      "private-cloud-business-edition"
   ],
   "sourceResourceUri" : "/virtualization/v1beta1/virtual-machines/c6f1518f-3e71-5770-978d-fe8773aff178",
   "startedAt" : "2024-05-01T19:28:37.065217665Z",
   "state" : "SUCCEEDED",
   "subtreeOperationCount" : 8,
   "suggestedPollingIntervalSeconds" : 30,
   "type" : "task",
   "updatedAt" : "2024-05-01T19:29:02.626590335Z",
   "userId" : "user@example.com"
}
```

Query the virtual machine to validate that the hardware settings were applied to the virtual machine.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines/{id}
```


```json
{
   "allowedOperations" : [...],
   "appInfo" : {... },
   "appType" : "VMWARE",
   "capacityInBytes" : 214748364800,
   "clusterInfo" : {...},
   "computeInfo" : {
      "memorySizeInMib" : "32768",
      "numCpuCores" : 8,
      "numCpuThreads" : 32
   },
   "createdAt" : "2024-02-23T03:23:14.73Z",
   "customerId" : "a3f60ff294db11ec9c3862726d3162bb",
   "displayName" : "testVM",
   ...
   "id" : "c6f1518f-3e71-5770-978d-fe8773aff178",
   "name" : "testVM",
   "networkAdapters" : [
      {
         "macAddress" : "00:50:56:ac:9a:b9",
         "macAddressType" : "AUTOMATIC",
         "name" : "Network adapter 1",
         "networkDetails" : {
            "connectAtPowerOn" : true,
            "displayName" : "VM Network",
            "id" : "network-2765",
            "name" : "VM Network",
            "resourceUri" : "",
            "state" : "AVAILABLE",
            "type" : "virtualization/hypervisor-network"
         }
      },
      {
         "macAddress" : "00:50:56:ac:e7:c8",
         "macAddressType" : "AUTOMATIC",
         "name" : "Network adapter 2",
         "networkDetails" : {
            "connectAtPowerOn" : true,
            "displayName" : "VM Network",
            "id" : "network-2765",
            "name" : "VM Network",
            "resourceUri" : "",
            "state" : "AVAILABLE",
            "type" : "virtualization/hypervisor-network"
         }
      }
   ],
   "powerState" : "POWERED_OFF",
   "protected" : false,
   "resourceUri" : "/virtualization/v1beta1/virtual-machines/c6f1518f-3e71-5770-978d-fe8773aff178",
   "services" : [
      "hci-manager"
   ],
   "state" : "OK",
   "stateReason" : "OK",
   "status" : "OK",
   "type" : "virtualization/virtual-machine",
   "uid" : "502cb164-c353-7ec4-9cd2-3aa3587e0196",
   "updatedAt" : "2024-05-01T20:15:16Z",
   "vclsVm" : false,
   "virtualDisks" : [
      {
         "appInfo" : {
            "vmware" : {
               "datastoreInfo" : {...},
               "diskUuidEnabled" : false,
               "type" : "VVOL"
            }
         },
         "capacityInBytes" : 68719476736,
         "filePath" : "[HPE-VVOL-d1dc4dd83fff5fc9aa43267cf1ccd4cf] rfc4122.6aceca6c-e364-47b7-b31b-59ed0a908046/testVM.vmdk",
         "id" : "bba54195-067c-586a-8f1b-9d4fe8aed146",
         "name" : "Hard disk 1",
         "uid" : "6000C29c-8c47-7959-b858-727c131b73b5"
      },
      {
         "appInfo" : {
            "vmware" : {
               "datastoreInfo" : {...},
               "diskUuidEnabled" : false,
               "type" : "VVOL"
            }
         },
         "capacityInBytes" : 17179869184,
         "filePath" : "[HPE-VVOL-d1dc4dd83fff5fc9aa43267cf1ccd4cf] rfc4122.6aceca6c-e364-47b7-b31b-59ed0a908046/testVM_1.vmdk",
         "id" : "532ded6c-21d2-59cf-8a1e-4fcab371759c",
         "name" : "Hard disk 2",
         "uid" : "6000C290-65dd-8998-24be-e14c80634b08"
      },
      {
         "appInfo" : {
            "vmware" : {
               "datastoreInfo" : {...},
               "diskUuidEnabled" : false,
               "type" : "VVOL"
            }
         },
         "capacityInBytes" : 10737418240,
         "filePath" : "[HPE-VVOL-d1dc4dd83fff5fc9aa43267cf1ccd4cf] rfc4122.6aceca6c-e364-47b7-b31b-59ed0a908046/testVM_2.vmdk",
         "id" : "7d19cdae-f90e-515e-909d-e793e1ba6d11",
         "name" : "Hard disk 3",
         "uid" : "6000C299-5271-0538-d2b6-69d23def4a42"
      },
      {
         "appInfo" : {
            "vmware" : {
               "datastoreInfo" : {...},
               "diskUuidEnabled" : false,
               "type" : "VVOL"
            }
         },
         "capacityInBytes" : 107374182400,
         "filePath" : "[HPE-VVOL-d1dc4dd83fff5fc9aa43267cf1ccd4cf] rfc4122.6aceca6c-e364-47b7-b31b-59ed0a908046/testVM_3.vmdk",
         "id" : "121a0b3c-9209-5b49-87af-69a0cf27ce6a",
         "name" : "Hard disk 4",
         "uid" : "6000C297-fe32-7488-fd24-7417f85c614d"
      },
      {
         "appInfo" : {
            "vmware" : {
               "datastoreInfo" : {...},
               "diskUuidEnabled" : false,
               "type" : "VVOL"
            }
         },
         "capacityInBytes" : 10737418240,
         "filePath" : "[HPE-VVOL-d1dc4dd83fff5fc9aa43267cf1ccd4cf] rfc4122.6aceca6c-e364-47b7-b31b-59ed0a908046/testVM_4.vmdk",
         "id" : "6c88dbf0-6504-50f8-848a-b52376c57c7e",
         "name" : "Hard disk 5",
         "uid" : "6000C292-b36e-fd90-5881-a3649d67ad87"
      }
   ],
   "vmClassification" : "",
   "vmConfigPath" : "[HPE-VVOL-d1dc4dd83fff5fc9aa43267cf1ccd4cf] rfc4122.6aceca6c-e364-47b7-b31b-59ed0a908046/testVM.vmx",
   "vmPerfMetricInfo" : {},
   "vmProtectionGroupsInfo" : null,
   "volumesInfo" : []
}
```

##### Delete a virtual machine

Delete a virtual machine specified by its `id`.


```bash
DELETE https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines/{id}
```


```bash header
HTTP/2 202
location: /data-services/v1beta1/async-operations/82222594a77-3809-4620-be52-74270abdf666
```

If there are any errors in input parameters, the request immediately fails with a 4XX error and the details of the failure.

#### Life cycle management of virtual machines in the public cloud (AWS and Azure)

##### List CSP machine images

Returns a list of cloud service provider (CSP) machine images based on the query parameters for paging, filtering, and sorting.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/csp-machine-images
```


```json
{
  "count": 0,
  "offset": 0,
  "total": 0,
  "items": [
    {
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "string",
      "generation": 0,
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "string",
      "resourceUri": "string",
      "type": "string",
      "updatedAt": "2019-08-24T14:15:22Z",
      "consoleUri": "string",
      "cspInfo": {
        "architecture": "x86_64",
        "blockDeviceMappings": [
          {
            "deviceName": "string",
            "ebs": {
              "deleteOnTermination": true,
              "encrypted": false,
              "snapshotId": "snap-0ed3f0f331ab4cbc7",
              "volumeSize": 8,
              "volumeType": "standard"
            }
          }
        ],
        "description": "string",
        "enaSupport": true,
        "hypervisor": "xen",
        "id": "ami-0000025f7c02a13b2",
        "imageType": "machine",
        "location": "amazon/amzn-ami-hvm-2018.03.0.20200716.0-x86_64-ebs",
        "ownerAlias": "amazon",
        "ownerId": "137112412989",
        "platformDetails": "Linux/UNIX",
        "public": true,
        "region": "eu-west-3",
        "rootDeviceName": "/dev/sda1",
        "rootDeviceType": "ebs",
        "sriovNetSupport": "simple",
        "state": "available",
        "usageOperation": "RunInstances",
        "virtualizationType": "hvm"
      },
      "cspType": "AWS"
    }
  ]
}
```

##### Get a CSP machine image

Returns details of a specified cloud service provider (CSP) machine image.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/csp-machine-images/{id}
```


```json
{
  "createdAt": "2019-08-24T14:15:22Z",
  "customerId": "string",
  "generation": 0,
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "name": "string",
  "resourceUri": "string",
  "type": "string",
  "updatedAt": "2019-08-24T14:15:22Z",
  "consoleUri": "string",
  "cspInfo": {
    "architecture": "x86_64",
    "blockDeviceMappings": [
      {
        "deviceName": "string",
        "ebs": {
          "deleteOnTermination": true,
          "encrypted": false,
          "snapshotId": "snap-0ed3f0f331ab4cbc7",
          "volumeSize": 8,
          "volumeType": "standard"
        }
      }
    ],
    "description": "string",
    "enaSupport": true,
    "hypervisor": "xen",
    "id": "ami-0000025f7c02a13b2",
    "imageType": "machine",
    "location": "amazon/amzn-ami-hvm-2018.03.0.20200716.0-x86_64-ebs",
    "ownerAlias": "amazon",
    "ownerId": "137112412989",
    "platformDetails": "Linux/UNIX",
    "public": true,
    "region": "eu-west-3",
    "rootDeviceName": "/dev/sda1",
    "rootDeviceType": "ebs",
    "sriovNetSupport": "simple",
    "state": "available",
    "usageOperation": "RunInstances",
    "virtualizationType": "hvm"
  },
  "cspType": "AWS"
}
```

##### List CSP machine instance types

Returns a list of cloud service provider (CSP) machine instance types based on the query parameters for paging, filtering, and sorting.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/csp-machine-instance-types
```


```json
{
  "count": 0,
  "offset": 0,
  "total": 0,
  "items": [
    {
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "string",
      "generation": 0,
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "string",
      "resourceUri": "string",
      "type": "string",
      "updatedAt": "2019-08-24T14:15:22Z",
      "consoleUri": "string",
      "cspInfo": {
        "autoRecoverySupported": true,
        "bareMetal": true,
        "burstablePerformanceSupported": false,
        "currentGeneration": true,
        "dedicatedHostsSupported": true,
        "ebsInfo": {
          "ebsOptimizedInfo": {
            "baselineBandwidthInMbps": 19000,
            "baselineIops": 80000,
            "baselineThroughputInMbps": 2375,
            "maximumBandwidthInMbps": 19000,
            "maximumIops": 80000,
            "maximumThroughputInMbps": 2375
          },
          "ebsOptimizedSupport": "default",
          "encryptionSupport": "supported",
          "nvmeSupport": "required"
        },
        "freeTierEligible": true,
        "hibernationSupported": false,
        "hypervisor": "xen",
        "instanceStorageSupported": false,
        "instanceType": "t2.2xlarge",
        "memoryInfo": {
          "sizeInMiB": 393216
        },
        "networkInfo": {
          "defaultNetworkCardIndex": 0,
          "efaSupported": false,
          "enaSupport": "required",
          "ipv4AddressesPerInterface": 50,
          "ipv6AddressesPerInterface": 50,
          "ipv6Supported": true,
          "maximumNetworkCards": 1,
          "maximumNetworkInterfaces": 15,
          "networkCards": {
            "maximumNetworkInterfaces": 15,
            "networkCardIndex": 0,
            "networkPerformance": "25 Gigabit"
          },
          "networkPerformance": "25 Gigabit"
        },
        "placementGroupInfo": {
          "supportedStrategies": [
            "cluster",
            "partition",
            "spread"
          ]
        },
        "processorInfo": {
          "supportedArchitectures": [
            "x86_64",
            "arm64",
            "i386"
          ],
          "sustainedClockSpeedInGhz": 3.1
        },
        "region": "eu-west-3",
        "supportedRootDeviceTypes": [
          "ebs",
          "instance-store"
        ],
        "supportedUsageClasses": [
          "on-demand",
          "spot"
        ],
        "supportedVirtualizationTypes": [
          "hvm"
        ],
        "vCpuInfo": {
          "defaultCores": 48,
          "defaultThreadsPerCore": 2,
          "defaultVcpus": 96
        }
      },
      "cspType": "AWS"
    }
  ]
}
```

##### Get a CSP machine instance type

Returns details of a specified cloud service provider (CSP) machine instance type.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/csp-machine-instance-types/{id}
```


```json
{
  "createdAt": "2019-08-24T14:15:22Z",
  "customerId": "string",
  "generation": 0,
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "name": "string",
  "resourceUri": "string",
  "type": "string",
  "updatedAt": "2019-08-24T14:15:22Z",
  "consoleUri": "string",
  "cspInfo": {
    "autoRecoverySupported": true,
    "bareMetal": true,
    "burstablePerformanceSupported": false,
    "currentGeneration": true,
    "dedicatedHostsSupported": true,
    "ebsInfo": {
      "ebsOptimizedInfo": {
        "baselineBandwidthInMbps": 19000,
        "baselineIops": 80000,
        "baselineThroughputInMbps": 2375,
        "maximumBandwidthInMbps": 19000,
        "maximumIops": 80000,
        "maximumThroughputInMbps": 2375
      },
      "ebsOptimizedSupport": "default",
      "encryptionSupport": "supported",
      "nvmeSupport": "required"
    },
    "freeTierEligible": true,
    "hibernationSupported": false,
    "hypervisor": "xen",
    "instanceStorageSupported": false,
    "instanceType": "t2.2xlarge",
    "memoryInfo": {
      "sizeInMiB": 393216
    },
    "networkInfo": {
      "defaultNetworkCardIndex": 0,
      "efaSupported": false,
      "enaSupport": "required",
      "ipv4AddressesPerInterface": 50,
      "ipv6AddressesPerInterface": 50,
      "ipv6Supported": true,
      "maximumNetworkCards": 1,
      "maximumNetworkInterfaces": 15,
      "networkCards": {
        "maximumNetworkInterfaces": 15,
        "networkCardIndex": 0,
        "networkPerformance": "25 Gigabit"
      },
      "networkPerformance": "25 Gigabit"
    },
    "placementGroupInfo": {
      "supportedStrategies": [
        "cluster",
        "partition",
        "spread"
      ]
    },
    "processorInfo": {
      "supportedArchitectures": [
        "x86_64",
        "arm64",
        "i386"
      ],
      "sustainedClockSpeedInGhz": 3.1
    },
    "region": "eu-west-3",
    "supportedRootDeviceTypes": [
      "ebs",
      "instance-store"
    ],
    "supportedUsageClasses": [
      "on-demand",
      "spot"
    ],
    "supportedVirtualizationTypes": [
      "hvm"
    ],
    "vCpuInfo": {
      "defaultCores": 48,
      "defaultThreadsPerCore": 2,
      "defaultVcpus": 96
    }
  },
  "cspType": "AWS"
}
```

##### Create a CSP machine instance

Create a CSP machine instance


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/csp-machine-instances
```

Payload:


```bash
{
  "accountId": "a652f894-1cc6-52c2-9540-490671081fd6",
  "cspMachineInstanceInfo": {
    "imageId": "a0f63b61-ef7b-5326-bf18-74d1f937102a",
    "instanceType": "t2.micro",
    "region": "us-west-2"
  },
  "cspType": "AWS",
  "keyPairName": "HPE_DSCC_KeyPair",
  "name": "HPE_CSP_VM"
}
```


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/754f4c67-5537-2436-67ac-91365adef67d
```

##### Terminate a CSP machine instance

Deletes the cloud service provider (CSP) machine instance.


```bash
DELETE https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/csp-machine-instances/{id}
```


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/754f4c67-5537-2436-67ac-91365adef67d
```

##### Power off CSP machine instance

Powers off the cloud service provider (CSP) machine instance.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/csp-machine-instances/{id}/power-off
```


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/754f4c67-5537-2436-67ac-91365adef67d
```

##### Power on CSP machine instance

Powers on cloud service provider (CSP) machine instance.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/csp-machine-instances/{id}/power-on
```


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/754f4c67-5537-2436-67ac-91365adef67d
```

#### Datastore management

##### Get all datastores for registered hypervisor managers

Get all datastores for registered hypervisor managers.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/datastores
```


```json
{
  "count": 0,
  "items": [
    {
      "allowedOperations": [
        "DATASTORE_CREATE",
        "DATASTORE_DELETE"
      ],
      "appType": "VMWARE",
      "capacityFree": 76534,
      "capacityInBytes": 2407653459860,
      "capacityUncommitted": 653422,
      "clusterInfo": {
        "displayName": "myesxcluster1",
        "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
        "name": "myesxcluster1",
        "resourceUri": "string",
        "type": "string"
      },
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "string",
      "datacentersInfo": [
        {
          "id": "16245bf7-2b35-5580-86a6-620faa5b5403",
          "moref": "datacenter-2",
          "name": "core-team-dc"
        }
      ],
      "datastoreClassification": "PROTECTION_STORE_GATEWAY",
      "datastoreType": "VMFS",
      "displayName": "Nimble-DS1",
      "folderInfo": {
        "displayName": "myVmFolder",
        "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
        "name": "myVmFolder",
        "resourceUri": "string",
        "type": "string"
      },
      "generation": 0,
      "hciClusterUuid": "754f63f7-1016-40ec-9b8f-610f978b9aec",
      "hostsInfo": [
        {
          "displayName": "myESXi",
          "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
          "name": "myESXi",
          "resourceUri": "string",
          "type": "string"
        }
      ],
      "hypervisorManagerInfo": {
        "displayName": "myvcenter1",
        "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
        "name": "vcenter123.hpe.com",
        "resourceUri": "string",
        "type": "string"
      },
      "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
      "moref": "datastore-1234",
      "name": "Nimble-DS2",
      "protectionJobInfo": {
        "id": "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4",
        "name": "string",
        "protectionPolicyInfo": {
          "id": "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4",
          "name": "Gold-Protection-Policy",
          "resourceUri": "string",
          "type": "string"
        },
        "resourceUri": "string",
        "type": "string"
      },
      "protectionPolicyAppliedAtInfo": {
        "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
        "name": "ProtectionPolicy1",
        "resourceUri": "string",
        "type": "DATASTORE"
      },
      "protectionStatus": "PROTECTED",
      "provisioningPolicyInfo": {
        "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
        "name": "ProvisioningPolicy1",
        "resourceUri": "string",
        "type": "string"
      },
      "recoveryPointsExist": true,
      "replicationInfo": {
        "id": "string",
        "name": "string",
        "partnerDetails": [
          {
            "id": "string",
            "mode": "SYNCHRONOUS",
            "name": "string",
            "systemWwn": "string",
            "vendorName": "NIMBLE"
          }
        ],
        "resourceUri": "/storage-fleet/v1/storage-systems/{uuid}/volume-sets",
        "type": "storage-fleet/volume-set"
      },
      "resourceUri": "/virtualization/v1beta1/datastores/{datastore-id}",
      "services": [
        "hci-manager",
        "backup-and-recovery"
      ],
      "state": "OK",
      "stateReason": "string",
      "status": "OK",
      "type": "string",
      "uid": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
      "updatedAt": "2019-08-24T14:15:22Z",
      "vmCount": 120,
      "vmProtectionGroupsInfo": [
        {
          "id": "1b738651-da9f-4c85-88c1-70dbfe1976681",
          "name": "myProtectionGroup",
          "resourceUri": "string",
          "type": "string"
        }
      ],
      "volumesInfo": [
        {
          "displayName": "string",
          "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
          "name": "Volume1",
          "resourceUri": "string",
          "scsiIdentifier": "1b738651-da9f-4c85-88c1-70dbfe1976681",
          "sizeInBytes": 2407653459860,
          "storageFolderInfo": {
            "displayName": "string",
            "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
            "name": "string",
            "resourceUri": "string",
            "type": "string"
          },
          "storagePoolInfo": {
            "displayName": "string",
            "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
            "name": "string",
            "resourceUri": "string",
            "type": "string"
          },
          "storageSystemInfo": {
            "displayName": "my-dev-3par1.ind.hpecorp.net",
            "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
            "managed": true,
            "name": "atlas-dev-3par1.ind.hpecorp.net",
            "resourceUri": "string",
            "serialNumber": "AF-10122",
            "type": "ALLETRA_9000",
            "vendorName": "hpe"
          },
          "type": "string",
          "volumeSetInfo": {
            "displayName": "string",
            "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
            "name": "string",
            "resourceUri": "string",
            "type": "string"
          }
        }
      ]
    }
  ],
  "offset": 0,
  "total": 0
}
```

##### Get a datastore

Returns details for the specified datastore.


```bash
GET https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/datastores/{id}
```


```json
{
  "allowedOperations": [
    "DATASTORE_CREATE",
    "DATASTORE_DELETE"
  ],
  "appType": "VMWARE",
  "capacityFree": 76534,
  "capacityInBytes": 2407653459860,
  "capacityUncommitted": 653422,
  "clusterInfo": {
    "displayName": "myesxcluster1",
    "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
    "name": "myesxcluster1",
    "resourceUri": "string",
    "type": "string"
  },
  "createdAt": "2019-08-24T14:15:22Z",
  "customerId": "string",
  "datacentersInfo": [
    {
      "id": "16245bf7-2b35-5580-86a6-620faa5b5403",
      "moref": "datacenter-2",
      "name": "core-team-dc"
    }
  ],
  "datastoreClassification": "PROTECTION_STORE_GATEWAY",
  "datastoreType": "VMFS",
  "displayName": "Nimble-DS1",
  "folderInfo": {
    "displayName": "myVmFolder",
    "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
    "name": "myVmFolder",
    "resourceUri": "string",
    "type": "string"
  },
  "generation": 0,
  "hciClusterUuid": "754f63f7-1016-40ec-9b8f-610f978b9aec",
  "hostsInfo": [
    {
      "displayName": "myESXi",
      "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
      "name": "myESXi",
      "resourceUri": "string",
      "type": "string"
    }
  ],
  "hypervisorManagerInfo": {
    "displayName": "myvcenter1",
    "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
    "name": "vcenter123.hpe.com",
    "resourceUri": "string",
    "type": "string"
  },
  "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
  "moref": "datastore-1234",
  "name": "Nimble-DS2",
  "protectionJobInfo": {
    "id": "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4",
    "name": "string",
    "protectionPolicyInfo": {
      "id": "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4",
      "name": "Gold-Protection-Policy",
      "resourceUri": "string",
      "type": "string"
    },
    "resourceUri": "string",
    "type": "string"
  },
  "protectionPolicyAppliedAtInfo": {
    "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
    "name": "ProtectionPolicy1",
    "resourceUri": "string",
    "type": "DATASTORE"
  },
  "protectionStatus": "PROTECTED",
  "provisioningPolicyInfo": {
    "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
    "name": "ProvisioningPolicy1",
    "resourceUri": "string",
    "type": "string"
  },
  "recoveryPointsExist": true,
  "replicationInfo": {
    "id": "string",
    "name": "string",
    "partnerDetails": [
      {
        "id": "string",
        "mode": "SYNCHRONOUS",
        "name": "string",
        "systemWwn": "string",
        "vendorName": "NIMBLE"
      }
    ],
    "resourceUri": "/storage-fleet/v1/storage-systems/{uuid}/volume-sets",
    "type": "storage-fleet/volume-set"
  },
  "resourceUri": "/virtualization/v1beta1/datastores/{datastore-id}",
  "services": [
    "hci-manager",
    "backup-and-recovery"
  ],
  "state": "OK",
  "stateReason": "string",
  "status": "OK",
  "type": "string",
  "uid": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
  "updatedAt": "2019-08-24T14:15:22Z",
  "vmCount": 120,
  "vmProtectionGroupsInfo": [
    {
      "id": "1b738651-da9f-4c85-88c1-70dbfe1976681",
      "name": "myProtectionGroup",
      "resourceUri": "string",
      "type": "string"
    }
  ],
  "volumesInfo": [
    {
      "displayName": "string",
      "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
      "name": "Volume1",
      "resourceUri": "string",
      "scsiIdentifier": "1b738651-da9f-4c85-88c1-70dbfe1976681",
      "sizeInBytes": 2407653459860,
      "storageFolderInfo": {
        "displayName": "string",
        "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
        "name": "string",
        "resourceUri": "string",
        "type": "string"
      },
      "storagePoolInfo": {
        "displayName": "string",
        "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
        "name": "string",
        "resourceUri": "string",
        "type": "string"
      },
      "storageSystemInfo": {
        "displayName": "my-dev-3par1.ind.hpecorp.net",
        "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
        "managed": true,
        "name": "atlas-dev-3par1.ind.hpecorp.net",
        "resourceUri": "string",
        "serialNumber": "AF-10122",
        "type": "ALLETRA_9000",
        "vendorName": "hpe"
      },
      "type": "string",
      "volumeSetInfo": {
        "displayName": "string",
        "id": "6a38acc7-e470-4ed7-b141-ca9509672dac",
        "name": "string",
        "resourceUri": "string",
        "type": "string"
      }
    }
  ]
}
```

##### Create a datastore

Create a datastore


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/datastores
```

Payload:


```bash
{
  "datastoreType": "VMFS",
  "name": "string",
  "provisioningPolicyId": "c226de0b-daf0-435d-a1d4-8dbc697e0066",
  "sizeInBytes": 0,
  "storageSystemId": "82fa5c8f-b188-4241-b1a7-66c08561dbc1",
  "targetHypervisorClusterId": "4019c72a-faa8-43fa-89cb-2dcaf55f0d8a"
}
```


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/754f4c67-5537-2436-67ac-91365adef67d
```

#### Migrate virtual machines

Migrate virtual machines to another cluster or datastore.


```bash
POST https://us-west.api.greenlake.hpe.com/virtualization/v1beta1/virtual-machines/migrate
```

Payload:


```bash
{
  "hypervisorManagerId": "string",
  "targetDatastoreId": "string",
  "targetHypervisorClusterId": "string"
}
```


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/754f4c67-5537-2436-67ac-91365adef67d
```