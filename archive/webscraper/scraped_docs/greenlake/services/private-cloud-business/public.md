---
title: "HPE GreenLake for Private Cloud Business Edition"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public.md"
scraped_at: "2026-06-07T06:13:28.790964+00:00Z"
---

# HPE GreenLake for Private Cloud Business Edition

This page provides an introduction and quick start guide for the Private Cloud Business Edition API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

HPE GreenLake for Private Cloud Business Edition provides global lifecycle
management of infrastructure and virtualization resources.

The API allows you to:

- View detailed inventory of systems, and the software information for all hypervisor clusters and servers in each of them
- Perform full-stack software update of one or more hypervisor clusters in a system
- Add an empty hypervisor cluster to a system
- View details of provisioning policies
- Add, update, and delete provisioning policies


### Features

The Private Cloud Business Edition APIs are broadly classified into the following categories:

- Inventory management
- Software update
- Infrastructure expansion
- Provisioning policies


## Developer guide

This HPE GreenLake for Private Cloud Business Edition API provides global lifecycle
management of infrastructure and virtualization resources. The API follows the HPE GreenLake API standard.

The details below describe how to gain access to the API and use its features.

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

#### Inventory management

The inventory management API can be used to list the inventory of systems, hypervisor clusters and their software information, and servers.

##### URIs

- `/private-cloud-business/v1beta1/systems`
- `/private-cloud-business/v1beta1/systems/{id}`
- `/private-cloud-business/v1beta1/systems/{id}/servers`
- `/private-cloud-business/v1beta1/systems/{systemId}/servers/{serverId}`


##### Permissions

- `data-services.storage-system.read`
- `data-services.controller.read`
- `data-services.hypervisor-manager.read`
- `data-services.hypervisor-cluster.read`
- `data-services.hypervisor-host.read`
- `data-services.hci-server.read`
- `data-services.hci-cluster.read`


#### Software update

The software update API allows you to perform a full-stack software update of the storage operating system and the hypervisor and server firmware on Private Cloud Business systems. At present, these APIs are supported for HPE Alletra dHCI systems only.

API operations that can be completed immediately or within a few seconds (usually less than a minute) return the response synchronously with `200 OK` response. Other API operations return the `202 Accepted` response code and a `Location` header containing the URI of the asynchronous operation that can be used to track progress.

##### URIs

- `/private-cloud-business/v1beta1/systems/{id}/software-prechecks`
- `/private-cloud-business/v1beta1/systems/{id}/software-update`
- `/private-cloud-business/v1beta1/systems/{id}/software-update-resume`
- `/private-cloud-business/v1beta1/systems/{id}/software-version-refresh`
- `/private-cloud-business/v1beta1/system-software-catalogs`
- `/private-cloud-business/v1beta1/system-software-catalogs/{id}`


##### Permissions

- `data-services.storage-system.read`
- `data-services.controller.read`
- `data-services.hypervisor-manager.read`
- `data-services.hypervisor-cluster.read`
- `data-services.hypervisor-host.read`
- `data-services.hci-server.read`
- `data-services.hci-cluster.read`
- `data-services.hci-cluster.update`


#### Infrastructure expansion

##### URIs

- `/private-cloud-business/v1beta1/systems/{id}/add-hypervisor-cluster`


##### Permissions

- `data-services.storage-system.read`
- `data-services.controller.read`
- `data-services.hypervisor-manager.read`
- `data-services.hypervisor-cluster.read`
- `data-services.hypervisor-host.read`
- `data-services.hci-server.read`
- `data-services.hci-cluster.read`
- `data-services.hci-cluster.update`


#### Provisioning policies

The provisioning policies API allows you to list, create, update, and delete provisioning policies.

##### URIs

- `/private-cloud-business/v1beta1/vm-provisioning-policies`
- `/private-cloud-business/v1beta1/vm-provisioning-policies/{id}`


##### Permissions

- `data-services.vm-provisioning-policy.read`
- `data-services.vm-provisioning-policy.apply`


### Making it all work

This section provides code samples of API requests and payloads for the various features of the Private Cloud Business Edition API.

#### Inventory management

##### List systems

You can list the systems and their properties like id, name, hypervisor clusters and their software information by submitting the following request. Since this operation can return a lot of information and can take time, it is recommended to use the filter query parameter to return only the required information. Use offset and limit for pagination and to limit the number of system records returned. See the API specification for more details.


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/systems
```

Sample response:


```json
{
  "items": [
    {
      "associatedResourceCounts": {},
      "computeUsage": {},
      "configAnalysisStatus": {},
      "health": {},
      "hypervisorClusters": [],
      "location": {},
      "softwareInfo": {},
      "stackType": "DHCI",
      "state": "OFFLINE",
      "storageSystem": {},
      "storageUsage": {},
      "systemVms": [],
      "createdAt": "2023-08-24T14:15:22Z",
      "customerId": "string",
      "generation": 0,
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "group-sjc-array2002",
      "resourceUri": "/private-cloud-business/v1beta1/systems/497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "type": "cluster",
      "updatedAt": "2023-08-24T14:15:22Z"
    },
    {
      "associatedResourceCounts": {},
      "computeUsage": {},
      "configAnalysisStatus": {},
      "health": {},
      "hypervisorClusters": [],
      "location": {},
      "softwareInfo": {},
      "stackType": "DHCI",
      "state": "OFFLINE",
      "storageSystem": {},
      "storageUsage": {},
      "systemVms": [],
      "createdAt": "2023-10-24T08:10:45Z",
      "customerId": "string",
      "generation": 0,
      "id": "354d4acd-6276-4993-bfeb-53cb497f6eca",
      "name": "group-sjc-array2072",
      "resourceUri": "/private-cloud-business/v1beta1/systems/354d4acd-6276-4993-bfeb-53cb497f6eca",
      "type": "cluster",
      "updatedAt": "2023-010-24T08:10:45Z"
    }
  ],
  "count": 2,
  "offset": 0,
  "total": 2
}
```

##### Get a system

You can get information about a system identified by `id` with its properties like name, hypervisor clusters, and their software information by submitting the following request. Since this operation can take time to get all properties of the system, it is recommended to use the filter query parameter to get only the required properties. See the API specification for more details.


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/systems/{id}
```

Sample response:


```json
{
      "associatedResourceCounts": {},
      "computeUsage": {},
      "configAnalysisStatus": {},
      "health": {},
      "hypervisorClusters": [],
      "location": {},
      "softwareInfo": {},
      "stackType": "DHCI",
      "state": "OFFLINE",
      "storageSystem": {},
      "storageUsage": {},
      "systemVms": [],
      "createdAt": "2023-08-24T14:15:22Z",
      "customerId": "string",
      "generation": 0,
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "group-sjc-array2002",
      "resourceUri": "/private-cloud-business/v1beta1/systems/497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "type": "cluster",
      "updatedAt": "2023-08-24T14:15:22Z"
    }
```

##### List servers in a system

List all servers in the system identified by `id`.


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/systems/{id}/servers`
```

Sample response:


```json
{
   "count" : 2,
   "items" : [
      {
         "customerId" : "aeb7487a336f11ec9ad0c2951b4ee305",
         "generation" : 2192,
         "health" : {
            "agentlessManagementService" : "READY",
            "biosOrHardwareHealth" : "OK",
            "fanHealth" : "OK",
            "fanRedundancy" : "REDUNDANT",
            "hbLastUpdateTimestamp" : "Fri Feb 16 03:56:27 2024",
            "memoryHealth" : "OK",
            "networkHealth" : "OK",
            "overallServerHealth" : "OK",
            "powerState" : "",
            "powerSuppliesHealth" : "OK",
            "powerSuppliesRedundancy" : "REDUNDANT",
            "processorHealth" : "OK",
            "smartStorageBatteryHealth" : "OK",
            "storageHealth" : "OK",
            "temperaturesHealth" : "OK"
         },
         "hypervisorHost" : {
            "ResourceUri" : "/api/v1/hypervisor-hosts/7b5e492e-f2fa-53f2-a6d1-e190ff37ad24",
            "hypervisorClusterId" : "eb379b89-e9de-5bb4-8025-6bf6e281f8a9",
            "hypervisorClusterName" : "cxo-array22-c1",
            "hypervisorHostIp" : "172.21.0.42",
            "id" : "7b5e492e-f2fa-53f2-a6d1-e190ff37ad24",
            "name" : "172.21.0.42",
            "type" : "HYPERVISOR_TYPE_ESXI"
         },
         "id" : "218491aa-fbbe-57a6-9d11-28186ecde366",
         "iloFirmwareVersion" : "iLO 5 v2.72",
         "iloNetworkInfo" : {
            "gateway" : "172.21.0.1",
            "iloHostname" : "172.21.0.44",
            "iloIp" : "172.21.0.44",
            "network" : "",
            "subnetMask" : "255.255.0.0"
         },
         "iloState" : "ENABLED",
         "iloStatus" : "OK",
         "indicatorLedStatus" : "OFF",
         "memoryGib" : "128",
         "model" : "ProLiant DL360 Gen10",
         "name" : "172.21.0.42",
         "ncmVersion" : "7.0.2-700014",
         "onPremUniqueID" : "39373638-3935-584d-5130-313930354d42",
         "powerState" : "ON",
         "processorCount" : "2",
         "processorModel" : "Intel(R) Xeon(R) Gold 6130 CPU @ 2.10GHz",
         "resourceUri" : "/private-cloud-business/v1beta1/systems/38f54df0-99b1-564e-8ce9-924fe1269451/servers/218491aa-fbbe-57a6-9d11-28186ecde366",
         "serialNumber" : "MXQ01905MB",
         "systemId" : "38f54df0-99b1-564e-8ce9-924fe1269451"
      },
      {
         "customerId" : "aeb7487a336f11ec9ad0c2951b4ee305",
         "generation" : 2192,
         "health" : {
            "agentlessManagementService" : "READY",
            "biosOrHardwareHealth" : "OK",
            "fanHealth" : "OK",
            "fanRedundancy" : "REDUNDANT",
            "hbLastUpdateTimestamp" : "Fri Feb 16 03:56:21 2024",
            "memoryHealth" : "OK",
            "networkHealth" : "OK",
            "overallServerHealth" : "OK",
            "powerState" : "",
            "powerSuppliesHealth" : "OK",
            "powerSuppliesRedundancy" : "REDUNDANT",
            "processorHealth" : "OK",
            "smartStorageBatteryHealth" : "OK",
            "storageHealth" : "OK",
            "temperaturesHealth" : "OK"
         },
         "hypervisorHost" : {
            "ResourceUri" : "/api/v1/hypervisor-hosts/76ca52d8-60c4-514e-88e2-777e72815a73",
            "hypervisorClusterId" : "f93e118a-58d6-5282-9ead-0d2bc3461a5d",
            "hypervisorClusterName" : "cxo-array22-c2",
            "hypervisorHostIp" : "172.21.0.43",
            "id" : "76ca52d8-60c4-514e-88e2-777e72815a73",
            "name" : "172.21.0.43",
            "type" : "HYPERVISOR_TYPE_ESXI"
         },
         "id" : "a25e698b-c880-5166-8f1b-498432e5a1ef",
         "iloFirmwareVersion" : "iLO 5 v2.72",
         "iloNetworkInfo" : {
            "gateway" : "172.21.0.1",
            "iloHostname" : "172.21.0.45",
            "iloIp" : "172.21.0.45",
            "network" : "",
            "subnetMask" : "255.255.0.0"
         },
         "iloState" : "ENABLED",
         "iloStatus" : "OK",
         "indicatorLedStatus" : "OFF",
         "memoryGib" : "128",
         "model" : "ProLiant DL360 Gen10",
         "name" : "172.21.0.43",
         "ncmVersion" : "7.0.2-700014",
         "onPremUniqueID" : "39373638-3935-584d-5130-313930354d43",
         "powerState" : "ON",
         "processorCount" : "2",
         "processorModel" : "Intel(R) Xeon(R) Gold 6130 CPU @ 2.10GHz",
         "resourceUri" : "/private-cloud-business/v1beta1/systems/38f54df0-99b1-564e-8ce9-924fe1269451/servers/a25e698b-c880-5166-8f1b-498432e5a1ef",
         "serialNumber" : "MXQ01905MC",
         "systemId" : "38f54df0-99b1-564e-8ce9-924fe1269451"
      }
   ],
   "offset" : 0,
   "total" : 2
}
```

##### Get a server in a system

Get the server identified by `serverId` in the system identified by `systemId`.


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/systems/{systemId}/servers/{serverId}
```

Sample response:


```json
{
   "customerId" : "aeb7487a336f11ec9ad0c2951b4ee305",
   "generation" : 2192,
   "health" : {
      "agentlessManagementService" : "READY",
      "biosOrHardwareHealth" : "OK",
      "fanHealth" : "OK",
      "fanRedundancy" : "REDUNDANT",
      "hbLastUpdateTimestamp" : "Fri Feb 16 03:56:21 2024",
      "memoryHealth" : "OK",
      "networkHealth" : "OK",
      "overallServerHealth" : "OK",
      "powerState" : "",
      "powerSuppliesHealth" : "OK",
      "powerSuppliesRedundancy" : "REDUNDANT",
      "processorHealth" : "OK",
      "smartStorageBatteryHealth" : "OK",
      "storageHealth" : "OK",
      "temperaturesHealth" : "OK"
   },
   "hypervisorHost" : {
      "ResourceUri" : "/api/v1/hypervisor-hosts/76ca52d8-60c4-514e-88e2-777e72815a73",
      "hypervisorClusterId" : "f93e118a-58d6-5282-9ead-0d2bc3461a5d",
      "hypervisorClusterName" : "cxo-array22-c2",
      "hypervisorHostIp" : "172.21.0.43",
      "id" : "76ca52d8-60c4-514e-88e2-777e72815a73",
      "name" : "172.21.0.43",
      "type" : "HYPERVISOR_TYPE_ESXI"
   },
   "id" : "a25e698b-c880-5166-8f1b-498432e5a1ef",
   "iloFirmwareVersion" : "iLO 5 v2.72",
   "iloNetworkInfo" : {
      "gateway" : "172.21.0.1",
      "iloHostname" : "172.21.0.45",
      "iloIp" : "172.21.0.45",
      "network" : "",
      "subnetMask" : "255.255.0.0"
   },
   "iloState" : "ENABLED",
   "iloStatus" : "OK",
   "indicatorLedStatus" : "OFF",
   "memoryGib" : "128",
   "model" : "ProLiant DL360 Gen10",
   "name" : "172.21.0.43",
   "ncmVersion" : "7.0.2-700014",
   "onPremUniqueID" : "39373638-3935-584d-5130-313930354d43",
   "powerState" : "ON",
   "processorCount" : "2",
   "processorModel" : "Intel(R) Xeon(R) Gold 6130 CPU @ 2.10GHz",
   "resourceUri" : "/private-cloud-business/v1beta1/systems/38f54df0-99b1-564e-8ce9-924fe1269451/servers/a25e698b-c880-5166-8f1b-498432e5a1ef",
   "serialNumber" : "MXQ01905MC",
   "systemId" : "38f54df0-99b1-564e-8ce9-924fe1269451"
}
```

#### Software update

##### Initiate software update prechecks on one or more hypervisor clusters in a system

Software update prechecks are a set of checks run on a given system to check its readiness for software update to a given catalog version. Submit this request to initiate software update prechecks on one or more hypervisor clusters in a system.

Though this is a system-level operation, software prechecks are targeted towards hypervisor clusters in the system. To submit this request, you need the system id, catalog version, and a list of hypervisor cluster ids. If you intend to run software update prechecks on all hypervisor clusters in the system and they all have the same catalog version as an available software catalog, then you can skip the hypervisor cluster ids.

Use the "Get a system" operation explained earlier to get the software information for each hypervisor cluster in the system.

The `softwareInfo` property of the system captures the software information of all hypervisor clusters in the system.
The nested property `softwareInfo.hypervisorClusters` is an array containing software information on a per hypervisor cluster basis.
Each item in this array will correspond to software information of one hypervisor cluster. The item will have information about the current software version, the available software versions, and the unavailable software versions for that hypervisor cluster. If `availableSoftwareCatalogs` is not empty, then a software update can be initiated on the hypervisor cluster. You can select an available software version from this array and initiate software prechecks and update operations on it. If multiple hypervisor clusters have an update available to the same software catalog version, then you can initiate a software prechecks or update to that version in the same request.

If successful, this request returns an HTTP 202 response with the URI of the async operation in the `location` header. You can use it to monitor the progress of the software update prechecks operation.


```bash
POST https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/systems/{id}/software-prechecks
```

Payload:


```json
{
  "catalogVersion": "7.5.34.18.36",
  "hypervisorClusterIds": [
    "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "354d4acd-5465-1215-fefd-45cbcada5c98"
  ]
}
```

Sample response header:


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/8e594a77-3809-4620-be52-74270abdf60b
```

If there is any error in input parameters, the request will immediately fail with a 4XX error and details of the failure.

If the request is accepted with a 202 response and subsequently the software update prechecks async operation fails for any reason, the details of the failure are captured in the async operation obtained by querying the URI in the `location` header. Take corrective actions as needed and rerun the operation. Once successful, you can initiate a software update on the same set of inputs while the result of prechecks is still valid.

If the software update prechecks succeed on a subset of hypervisor clusters submitted in this request and fail on the remaining, you can still submit the software update request (explained in next section) by explicitly submitting their ids in the software update request.

##### Initiate software update on one or more hypervisor clusters in a system

A full-stack software update operation can be initiated on a given system by submitting the following request.
Before submitting this request, ensure that software update prechecks on the same parameters have successfully completed and are still valid.

If you get an error implying the result of software update prechecks is not valid anymore, it means it has been a while after you last ran the prechecks and its results are not valid anymore. In this case you need to rerun the software update prechecks on the same inputs (explained in the previous section), and then attempt the software update request again.

If successful, this request returns an HTTP 202 response with the URI of the async operation in the `location` header. You can use it to monitor the progress of the software update operation.


```bash
POST https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/systems/{id}/software-update
```

Payload:


```json
{
  "catalogVersion": "7.5.34.18.36",
  "hypervisorClusterIds": [
    "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "354d4acd-5465-1215-fefd-45cbcada5c98"
  ]
}
```

Sample response header:


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/765f4c89-1203-6547-de24-53645acff66d
```

If there is any error in input parameters, the request will immediately fail with a 4XX error and details of the failure.

If the request is accepted with a 202 response and subsequently the software update async operation fails for any reason, the details of such failure are captured in the async operation obtained by querying the URI in the `location` header. Once you take corrective actions as needed you can resume the software update operation from the point of last known failure using the software update resume operation explained in next section.

##### Resume software update on a system

A failed software update can be resumed from the last known failure step.
Submit this request only after taking the corrective actions needed to resolve the underlying issue highlighted in failed software update async operation. This request does not take any inputs other than the id of the system on which software update needs to be resumed as the resumption is always on a failed software update, the catalog version and hypervisor cluster ids for which were already submitted through the software update request.


```bash
POST https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/systems/{id}/software-update-resume
```

Sample response header:


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/423f4c89-1543-7747-de23-64645adef54f
```

If this request is submitted for a system that is not in a failed state, the request will immediately fail with a 400 Bad Request error.

If accepted, a 202 response will be returned along with the URI of the resultant async operation in the `location` header.
This URI can be further queried to monitor the progress of resumed software update async operation.
If the async operation eventually fails, submit the same request again after taking corrective actions as needed.

##### Refresh software versions on a system

Current and available software versions of hypervisor clusters in all systems are refreshed at regular intervals. Submit this request if you want to refresh the software version information on-demand for a given system at any point in time before the next scheduled software version refresh triggers.
This is an async operation and will return a `202 Accepted` response with the URI of the async operation in the `location` header.


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/systems/{id}/software-version-refresh
```

Sample response header:


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/654f4c89-4323-6654-63de-76435adef78c
```

In case of errors, the request can be submitted again after resolving the issues highlighted in response or in the async operation.

##### Get all system software catalogs

Submit this request to get information of all system software catalogs available with Private Cloud Business Edition.
These are the software catalogs used for computing the current and available software catalogs for all systems, either on a periodic basis or on-demand, as explained in the previous section.

To get system software catalog with a particular version, use the filter on `version` property. Refer to API specification for more details. For example, to get the end user license agreement (`eula` property) for a given version or all systems that have update path (have at least one hypervisor cluster with this version in its available catalogs array) to a given version.


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/system-software-catalogs
```

Sample response:


```json
{
  "items": [
    {
      "eula": "https://update.nimblestorage.com/catalog/download/eula-rel-pebble-300.html",
      "systemsWithUpdatePath": [..],
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "00000000000000000000000000000000",
      "generation": 0,
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "",
      "resourceUri": "/private-cloud-business/v1beta1/system-software-catalogs/497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "type": "private-cloud-business/system-software-catalog",
      "updatedAt": "2019-08-24T14:15:22Z",
      "hypervisor": {..},
      "hypervisorManager": {..},
      "releaseDate": "2023-06-13",
      "serverFirmware": {..},
      "storageConnectionManager": {..},
      "storageSoftware": {..},
      "version": "7.5.34.18.36"
    },
    {
      "eula": "https://update.nimblestorage.com/catalog/download/eula-rel-pebble-300.html",
      "systemsWithUpdatePath": [..],
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "00000000000000000000000000000000",
      "generation": 0,
      "id": "645f6eca-7634-2536-cdde-74cbbbba6f76",
      "name": "",
      "resourceUri": "/private-cloud-business/v1beta1/system-software-catalogs/645f6eca-7634-2536-cdde-74cbbbba6f76",
      "type": "private-cloud-business/system-software-catalog",
      "updatedAt": "2019-08-24T14:15:22Z",
      "hypervisor": {..},
      "hypervisorManager": {..},
      "releaseDate": "2023-06-13",
      "serverFirmware": {..},
      "storageConnectionManager": {..},
      "storageSoftware": {..},
      "version": "7.5.36.18.36"
    }
  ],
  "count": 2,
  "offset": 0,
  "total": 2
}
```

##### Get a specific system software catalog

Submit this request to get information about the specified system software catalog.


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/system-software-catalogs/{id}
```

Sample response:


```json
{
  "eula": "https://update.nimblestorage.com/catalog/download/eula-rel-pebble-300.html",
  "systemsWithUpdatePath": [..],
  "createdAt": "2019-08-24T14:15:22Z",
  "customerId": "00000000000000000000000000000000",
  "generation": 0,
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "name": "",
  "resourceUri": "/private-cloud-business/v1beta1/system-software-catalogs/497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "type": "private-cloud-business/system-software-catalog",
  "updatedAt": "2019-08-24T14:15:22Z",
  "hypervisor": {..},
  "hypervisorManager": {..},
  "releaseDate": "2023-06-13",
  "serverFirmware": {..},
  "storageConnectionManager": {..},
  "storageSoftware": {..},
  "version": "7.5.34.18.36"
}
```

#### Infrastructure expansion

Submit this request to add an empty hypervisor cluster to the system identified by `id`.
This is an async operation and will return a `202 Accepted` response with the URI of the async operation in the `location` header.


```bash
POST https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/systems/{id}/add-hypervisor-cluster
```

Payload:


```json
{
  "configureVds": true,
  "hypervisorClusterName": "production-cluster",
  "vsphereDatacenterName": "production-datacenter"
}
```

Sample response header:


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/754f4c67-5537-2436-67ac-91435adef67d
```

In case of errors, the request can be submitted again after resolving the issues highlighted in response or in the async operation.

#### Provisioning policies

##### List provisioning policies

Returns a list of provisioning policies based on the query parameters for paging, filtering, and sorting.


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/vm-provisioning-policies
```

Sample response:


```json
{
  "count": 0,
  "items": [
    {
      "associatedObjects": [
        {
          "generation": 0,
          "resourceUri": "string",
          "type": "string",
          "associatedDatastores": [
            {
              "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
              "name": "string",
              "type": "string"
            }
          ],
          "associatedVmCount": 0,
          "associatedVms": [
            {
              "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
              "name": "string"
            }
          ],
          "storageProfileId": "string",
          "clusterId": "string",
          "clusterName": "string"
        }
      ],
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "string",
      "description": "string",
      "generation": 0,
      "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
      "name": "myProvisioningPolicy",
      "performancePolicy": {
        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"
      },
      "protectionPolicy": {
        "description": "string",
        "effectiveFromDateTime": "2020-03-03T05:03:08.902Z",
        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
        "name": "string",
        "overrides": {
          "backupGranularity": "VOLUME",
          "consistency": "APPLICATION"
        }
      },
      "resourceUri": "string",
      "storageType": "Alletra dHCI",
      "type": "string",
      "updatedAt": "2019-08-24T14:15:22Z",
      "volumeInfo": {
        "allFlash": true,
        "conversionType": "CONVERSIONTYPE_THIN",
        "dataReduction": true,
        "deduplication": true,
        "encryption": {
          "cipher": "AES_256_XTS",
          "provider": "string",
          "scope": "Volume"
        },
        "qos": {
          "perfIopsLimit": 1200,
          "perfMbpsLimit": 1200
        },
        "snapshotAllocWarning": 0,
        "userAllocWarning": 0
      }
    }
  ],
  "offset": 0,
  "total": 0
}
```

##### Get a provisioning policy

Returns details for the specified provisioning policy.


```bash
GET https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/vm-provisioning-policies/{id}
```

Sample response:


```json
{
  "associatedObjects": [
    {
      "generation": 0,
      "resourceUri": "string",
      "type": "string",
      "associatedDatastores": [
        {
          "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
          "name": "string",
          "type": "string"
        }
      ],
      "associatedVmCount": 0,
      "associatedVms": [
        {
          "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
          "name": "string"
        }
      ],
      "storageProfileId": "string",
      "clusterId": "string",
      "clusterName": "string"
    }
  ],
  "createdAt": "2019-08-24T14:15:22Z",
  "customerId": "string",
  "description": "string",
  "generation": 0,
  "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
  "name": "myProvisioningPolicy",
  "performancePolicy": {
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"
  },
  "protectionPolicy": {
    "description": "string",
    "effectiveFromDateTime": "2020-03-03T05:03:08.902Z",
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "name": "string",
    "overrides": {
      "backupGranularity": "VOLUME",
      "consistency": "APPLICATION"
    }
  },
  "resourceUri": "string",
  "storageType": "Alletra dHCI",
  "type": "string",
  "updatedAt": "2019-08-24T14:15:22Z",
  "volumeInfo": {
    "allFlash": true,
    "conversionType": "CONVERSIONTYPE_THIN",
    "dataReduction": true,
    "deduplication": true,
    "encryption": {
      "cipher": "AES_256_XTS",
      "provider": "string",
      "scope": "Volume"
    },
    "qos": {
      "perfIopsLimit": 1200,
      "perfMbpsLimit": 1200
    },
    "snapshotAllocWarning": 0,
    "userAllocWarning": 0
  }
}
```

##### Create a provisioning policy


```bash
POST https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/vm-provisioning-policies
```

Payload:


```json
{
  "description": "string",
  "name": "myProvisioningPolicy",
  "protectionPolicy": {
    "description": "string",
    "effectiveFromDateTime": "2020-03-03T05:03:08.902Z",
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "name": "string",
    "overrides": {
      "backupGranularity": "VOLUME",
      "consistency": "APPLICATION"
    }
  },
  "storageType": "Alletra dHCI",
  "volumeInfo": {
    "allFlash": true,
    "conversionType": "CONVERSIONTYPE_THIN",
    "dataReduction": true,
    "deduplication": true,
    "encryption": {
      "cipher": "AES_256_XTS",
      "provider": "string",
      "scope": "Volume"
    },
    "qos": {
      "perfIopsLimit": 1200,
      "perfMbpsLimit": 1200
    },
    "snapshotAllocWarning": 0,
    "userAllocWarning": 0
  }
}
```

Sample response:


```json
HTTP/2 200
{
  "associatedObjects": [
    {
      "generation": 0,
      "resourceUri": "string",
      "type": "string",
      "associatedDatastores": [
        {
          "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
          "name": "string",
          "type": "string"
        }
      ],
      "associatedVmCount": 0,
      "associatedVms": [
        {
          "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
          "name": "string"
        }
      ],
      "storageProfileId": "string",
      "clusterId": "string",
      "clusterName": "string"
    }
  ],
  "createdAt": "2019-08-24T14:15:22Z",
  "customerId": "string",
  "description": "string",
  "generation": 0,
  "id": "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4",
  "name": "myProvisioningPolicy",
  "performancePolicy": {
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"
  },
  "protectionPolicy": {
    "description": "string",
    "effectiveFromDateTime": "2020-03-03T05:03:08.902Z",
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "name": "string",
    "overrides": {
      "backupGranularity": "VOLUME",
      "consistency": "APPLICATION"
    }
  },
  "resourceUri": "string",
  "storageType": "Alletra dHCI",
  "type": "string",
  "updatedAt": "2019-08-24T14:15:22Z",
  "volumeInfo": {
    "allFlash": true,
    "conversionType": "CONVERSIONTYPE_THIN",
    "dataReduction": true,
    "deduplication": true,
    "encryption": {
      "cipher": "AES_256_XTS",
      "provider": "string",
      "scope": "Volume"
    },
    "qos": {
      "perfIopsLimit": 1200,
      "perfMbpsLimit": 1200
    },
    "snapshotAllocWarning": 0,
    "userAllocWarning": 0
  }
}
```

##### Update a provisioning policy


```bash
PATCH https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/vm-provisioning-policies/{id}
```

Payload:


```json
{
  "description": "string",
  "protectionPolicy": {
    "description": "string",
    "effectiveFromDateTime": "2020-03-03T05:03:08.902Z",
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "name": "string",
    "overrides": {
      "backupGranularity": "VOLUME",
      "consistency": "APPLICATION"
    }
  },
  "storageType": "Alletra dHCI",
  "volumeInfo": {
    "allFlash": true,
    "conversionType": "CONVERSIONTYPE_THIN",
    "dataReduction": true,
    "deduplication": true,
    "encryption": {
      "cipher": "AES_256_XTS",
      "provider": "string",
      "scope": "Volume"
    },
    "qos": {
      "perfIopsLimit": 1200,
      "perfMbpsLimit": 1200
    },
    "snapshotAllocWarning": 0,
    "userAllocWarning": 0
  }
}
```

Sample response header:


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/754f4c67-5537-2436-67ac-91365adef67d
```

##### Delete a provisioning policy


```bash
DELETE https://us-west.api.greenlake.hpe.com/private-cloud-business/v1beta1/vm-provisioning-policies/{id}
```

Sample response header:


```bash
HTTP/2 202
location: /data-services/v1beta1/async-operations/754f4c67-5537-2436-67ac-91444adef67d
```