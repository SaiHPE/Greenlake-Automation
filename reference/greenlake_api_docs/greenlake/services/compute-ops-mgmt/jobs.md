---
title: "HPE Compute Ops Management Jobs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs.md"
scraped_at: "2026-06-07T06:13:23.587698+00:00Z"
---

# HPE Compute Ops Management Jobs

## Job Definition

A job is a multi-step task that is managed by Compute Ops Management to perform an action on a resource. For example performing
power operations or firmware updates on a server.

## Available Jobs

The following table summarizes the jobs that can be performed in COM.

Job Template IDs
The template ID of a job is *durable* which means that it's the same across all Compute Ops Management regions. It uniquely
identifies a job and can be hard-coded in your scripts and tools.

| Name | Description | Resource Type | Template ID | Required JobParams |
|  --- | --- | --- | --- | --- |
| [Server Power Off](/docs/greenlake/services/compute-ops-mgmt/jobs/server-power-off) | Power off a server | compute-ops-mgmt/server | d0c13b58-748c-461f-9a61-c0c5c71f1bb4 | -- |
| [Server Power On](/docs/greenlake/services/compute-ops-mgmt/jobs/server-power-on) | Power on a server | compute-ops-mgmt/server | 0cbb2377-1834-488d-840c-d5bf788c34fb | -- |
| [Server Restart](/docs/greenlake/services/compute-ops-mgmt/jobs/server-restart) | Restart a server | compute-ops-mgmt/server | 30110551-cad6-4069-95b8-dbce9bbd8525 | -- |
| [Server Cold Boot](/docs/greenlake/services/compute-ops-mgmt/jobs/server-cold-boot) | Cold boot a server | compute-ops-mgmt/server | aacfb3e0-6575-4d4f-a711-1ee1ae768407 | -- |
| [Server Firmware Update](/docs/greenlake/services/compute-ops-mgmt/jobs/server-firmware-update) | Update firmware on a server | compute-ops-mgmt/server | fd54a96c-cabc-42e3-aee3-374a2d009dba | `bundle_id` |
| [Server iLO Firmware Update](/docs/greenlake/services/compute-ops-mgmt/jobs/server-ilo-firmware-update) | Update iLO component firmware on a server | compute-ops-mgmt/server | 94caa4ef-9ff8-4805-9e97-18a09e673b66 | -- |
| [Server External Storage Details](/docs/greenlake/services/compute-ops-mgmt/jobs/server-external-storage-details) | Collect external storage details | compute-ops-mgmt/server | 9310319e-7b7f-41ba-8b24-8b34eed1ca62 | -- |
| [Server UID Indicator On](/docs/greenlake/services/compute-ops-mgmt/jobs/server-uid-indicator-on) | Turn on the UID indicator light on a server | compute-ops-mgmt/server | a46b210a-b0c7-4223-ab43-c4c1e77e680c | -- |
| [Server UID Indicator Off](/docs/greenlake/services/compute-ops-mgmt/jobs/server-uid-indicator-off) | Turn off the UID indicator light on a server | compute-ops-mgmt/server | fd837434-a2f2-4bc8-b1b4-ec068bd036aa | -- |
| [Server Enable Maintenance Mode](/docs/greenlake/services/compute-ops-mgmt/jobs/server-enable-maintenance-mode) | Enable maintenance mode for a server | compute-ops-mgmt/server | 4eb92af1-1ce4-4cb0-8581-fb5a7dcdbf2b | -- |
| [Server Disable Maintenance Mode](/docs/greenlake/services/compute-ops-mgmt/jobs/server-disable-maintenance-mode) | Disable maintenance mode for a server | compute-ops-mgmt/server | 2798720f-b090-427d-b210-e48d33ce2f27 | -- |
| [Group Firmware Update](/docs/greenlake/services/compute-ops-mgmt/jobs/group-firmware-update) | Update firmware on servers in a group | compute-ops-mgmt/group | 91159b5e-9eeb-11ec-a9da-00155dc0a0c0 | -- |
| [Group Firmware Compliance](/docs/greenlake/services/compute-ops-mgmt/jobs/group-firmware-compliance) | Calculate firmware compliance of servers in a group | compute-ops-mgmt/group | 23b8ba2a-6c46-4223-b028-919382c7dcac | `devices` |
| [Group Apply Internal Storage Settings](/docs/greenlake/services/compute-ops-mgmt/jobs/group-apply-internal-storage-settings) | Configures internal storage volume for servers in a group | compute-ops-mgmt/group | 54095626-3911-4fea-9741-816e2531994e | `initialize` `volumes` |
| [Group Apply Server Setting](/docs/greenlake/services/compute-ops-mgmt/jobs/group-apply-server-setting) | Apply server setting on a group | compute-ops-mgmt/group | beff07ce-f36d-4699-9ac3-f872dcd63133 | `redfish_subsystem` |
| [Group Apply External Storage Settings](/docs/greenlake/services/compute-ops-mgmt/jobs/group-apply-external-storage-settings) | Apply external storage settings on servers in a group | compute-ops-mgmt/group | fcb79270-5954-42e9-9374-6a065b6d494a | -- |
| [Group Apply OneView Server Templates](/docs/greenlake/services/compute-ops-mgmt/jobs/group-apply-oneview-server-templates) | Apply server template settings on appliances in a group | compute-ops-mgmt/group | db3620d4-19a4-4b54-9804-83f8f59d48a4 | `targetApplianceIds` |
| [Group Appliance Update](/docs/greenlake/services/compute-ops-mgmt/jobs/group-appliance-update) | Update appliances in a group | compute-ops-mgmt/group | f69f553a-5004-4a08-9283-5b60abd9eb4a | `targetApplianceIds` |
| [Group External Storage Compliance](/docs/greenlake/services/compute-ops-mgmt/jobs/group-external-storage-compliance) | Calculate external storage compliance of servers in a group | compute-ops-mgmt/group | 7177aa6a-e8f8-4e9b-ae31-e01dafcc81df | -- |
| [Settings Update OneView Server Template](/docs/greenlake/services/compute-ops-mgmt/jobs/setting-update-oneview-server-template) | Update server template settings | compute-ops-mgmt/setting | abfda355-6e58-4c00-be0a-af35dbd70398 | `templatesData` |
| [Appliance Software Update](/docs/greenlake/services/compute-ops-mgmt/jobs/appliance-software-update) | Update software of an appliance | compute-ops-mgmt/oneview-appliance | 1c4ac4be-8eeb-49f2-a86a-fd8c9182616c | `applianceFirmwareId` |
| [Group OS Installation](/docs/greenlake/services/compute-ops-mgmt/jobs/group-os-install) | Install operating system on servers in a group | compute-ops-mgmt/group | e2952628-2629-4088-93db-91742304ef0c | -- |
| [Server Inventory](/docs/greenlake/services/compute-ops-mgmt/jobs/server-inventory) | Collect server inventory | compute-ops-mgmt/server | d6595f1b-84e6-4587-ade5-656e2a5ea20d | -- |
| [Server Network Connectivity](/docs/greenlake/services/compute-ops-mgmt/jobs/server-network-connectivity) | Collect Server Network Connectivity | compute-ops-mgmt/server | b21ca9e2-8a1b-11ee-b9d1-0242ac120002 | -- |
| [Configure ignore iLO security risk settings](/docs/greenlake/services/compute-ops-mgmt/jobs/configure-ignore-ilo-security-risk-settings) | update ilo security ignore settings | compute-ops-mgmt/server | e1d69e76-38cc-4079-9192-a380baea2973 | -- |
| [Group Apply OneView appliance settings](/docs/greenlake/services/compute-ops-mgmt/jobs/group-apply-oneview-appliance-settings) | Apply OneView appliance settings to specified appliance group members | compute-ops-mgmt/group | a229a162-b43f-45b0-b7bb-692df77b9746 | `targetApplianceIds` |
| [Refresh OneView appliance settings](/docs/greenlake/services/compute-ops-mgmt/jobs/refresh-oneview-appliance-settings) | Refresh the OneView appliance settings cache in Compute Ops Management | compute-ops-mgmt/oneview-appliance | fc16aa48-c73c-4463-9112-e061383ebfa9 | -- |
| [Collect Server log](/docs/greenlake/services/compute-ops-mgmt/jobs/collect-server-log) | Collect server log | compute-ops-mgmt/server | 2d744494-22d4-4d61-8c65-647ccadeb6b6 | -- |
| [Server Firmware Download](/docs/greenlake/services/compute-ops-mgmt/jobs/server-firmware-download) | Download firmware on a server | compute-ops-mgmt/server | 0683ada8-1a89-49dd-bf04-6df715b708a6 | `bundle_id` |
| [Group Firmware Download](/docs/greenlake/services/compute-ops-mgmt/jobs/group-firmware-download) | Download firmware on servers in a group | compute-ops-mgmt/group | a17a7aa9-4540-4c21-bbf2-31af4ff65e98 | -- |
| [vCenter Firmware Bundles Sync](/docs/greenlake/services/compute-ops-mgmt/jobs/vcenter-firmware-bundles-sync) | Synchronize firmware bundles with vCenter | compute-ops-mgmt/external-service | 0fe73adb-9d52-4f00-9540-6ec82f265d82 | -- |
| [Delete vCenter](/docs/greenlake/services/compute-ops-mgmt/jobs/vcenter-delete) | Delete a vCenter external service integration | compute-ops-mgmt/external-service | 3f06fd6b-dfb1-4bad-bd04-939951797e97 | `vCenterUrl`, `associatedGatewayUri`, `externalServiceId`, `vCenterUuid` |


> Note: Click on the job name to learn more about the required and optional data on the job details page.


## Create Job

A job can be created by issuing a `POST` to the `/compute-ops-mgmt/v1/jobs` endpoint with the correct payload for the job.

The following properties are used when creating a job:

| Property | JSON Type | Description | Required? |
|  --- | --- | --- | --- |
| `jobTemplate` | string (id) | The durable Template ID of the job | Yes |
| `resourceType` | string (type) | The TYPE of the resource the job will operate on | Yes |
| `resourceId` | string (id) | The ID of the resource the job will operate on | Yes |
| `jobParams` | object | Any additional data required by the job | No |


If the job was created successfully, a `201 Created` response is returned. The response includes the job resource which has a
job `resourceUri` that you can use to track the progress of the job.

### Migrating Job Creation to the Stable v1 API

To transition from the deprecated beta versions (`v1beta2` and `v1beta3`) to the stable `v1` API for job creation, refer to the following. It outlines how to replace previous parameters.

This migration ensures compatibility with the stable API and aligns with the latest Compute Ops Management standards.

**Template Identifier** The template is now identified only by the template's durable ID.

- Deprecated:
  - jobTemplateUri= "/compute-ops-mgmt/v1beta2/job-templates/91159b5e-9eeb-11ec-a9da-00155dc0a0c0"
- V1 Stable:
  - jobTemplate= "91159b5e-9eeb-11ec-a9da-00155dc0a0c0"


**Resource Identifier** The resource is now identified by two attributes the resourceType and resourceId

- Deprecated:
  - resourceUri= "/compute-ops-mgmt/v1beta2/groups/a3853ee1-da05-47d6-bcc4-d35244d59605"
- V1 Stable:
  - resourceType= "compute-ops-mgmt/group"
  - resourceId= "a3853ee1-da05-47d6-bcc4-d35244d59605"


**Job Parameters** The parameters for the job haven't changed, but now go to the jobParams property.

- Deprecated:
  - data= {json body}
- V1 Stable:
  - jobParams= {json body (same contents)}


## Monitoring Jobs

In order to track job progress, request the current job using `GET /compute-ops-mgmt/{version}/jobs/{job-id}` with `v1` as the `{version}`, or the deprecated values `v1beta3` and `v1beta2`.

### Using v1

The response includes a `state` and `resultCode` which allow you to monitor the current job state and result.
The job also includes a `status` which can provide more details about the current job progress.

The job `state` and `resultCode` are defined as follows:

| State | Description |
|  --- | --- |
| `PENDING` | The job is queued behind other running jobs |
| `RUNNING` | The job is currently running |
| `STALLED` | The job is not making progress and needs to be terminated manually |
| `ERROR` | The job terminated unexpectedly due to an error |
| `COMPLETE` | The job completed |


> Note: `ERROR` and `COMPLETE` are both terminal states for a job.


| Result Code | Description |
|  --- | --- |
| `SUCCESS` | The job completed successfully |
| `FAILURE` | The job completed without achieving its intended outcome |
| `null` | The job is in a non-terminal state |


#### Example

The following example shows a completed GroupFirmwareCompliance job using the `v1` jobs route.


```json
{
  "id": "2b8540fc-f275-48bb-ae4b-bf9a42b6cc91",
  "parentJobId": null,
  "type": "compute-ops-mgmt/job",
  "resourceUri": "/compute-ops-mgmt/v1/jobs/2b8540fc-f275-48bb-ae4b-bf9a42b6cc91",
  "createdAt": "2022-08-04T18:52:26.278608+00:00",
  "updatedAt": "2022-08-04T18:54:09.903588+00:00",
  "deleteOnComplete": false,
  "cancelable": true,
  "name": "GroupFirmwareCompliance",
  "jobTemplate": "23b8ba2a-6c46-4223-b028-919382c7dcac",
  "resource": {
    "type": "compute-ops-mgmt/group",
    "id": "8a3a2a46-0102-48e2-bdd9-a29ee6909860"
  },
  "jobParams": {},
  "state": "COMPLETE",
  "resultCode": "SUCCESS",
  "status": "Complete",
  "statusDetails": {},
  "generation": 6
}
```

### Using v1beta3

The older `v1bets3` response tracks resource by URIs, not ID & TYPE like in the stable '`v1` api.

#### Example

The following example shows a completed GroupFirmwareCompliance job using the `v1beta3` jobs route.


```json
{
  "id": "2b8540fc-f275-48bb-ae4b-bf9a42b6cc91",
  "parentJobId": null,
  "type": "compute-ops-mgmt/job",
  "resourceUri": "/compute-ops-mgmt/v1beta3/jobs/2b8540fc-f275-48bb-ae4b-bf9a42b6cc91",
  "createdAt": "2022-08-04T18:52:26.278608+00:00",
  "updatedAt": "2022-08-04T18:54:09.903588+00:00",
  "displayName": "GroupFirmwareCompliance",
  "name": "GroupFirmwareCompliance",
  "jobTemplateUri": "/compute-ops-mgmt/v1beta3/job-templates/23b8ba2a-6c46-4223-b028-919382c7dcac",
  "associatedResourceUri": "/compute-ops-mgmt/v1beta3/groups/8a3a2a46-0102-48e2-bdd9-a29ee6909860",
  "resource": {
    "resourceUri": "/compute-ops-mgmt/v1beta3/groups/8a3a2a46-0102-48e2-bdd9-a29ee6909860",
    "type": "groups"
  },
  "data": {},
  "state": "COMPLETE",
  "resultCode": "SUCCESS",
  "status": "Complete",
  "statusDetails": {},
  "generation": 6
}
```

### Using v1beta2

The older `v1beta2` response uses URIs, and does not have `resultCode`, but includes a `state` and `status`.

#### Example

The following example shows a completed GroupFirmwareCompliance job using the `v1beta2` jobs route.


```json
{
  "id": "2b8540fc-f275-48bb-ae4b-bf9a42b6cc91",
  "parentJobId": null,
  "type": "compute-ops-mgmt/job",
  "resourceUri": "/compute-ops-mgmt/v1beta2/jobs/2b8540fc-f275-48bb-ae4b-bf9a42b6cc91",
  "createdAt": "2022-08-04T18:52:26.278608+00:00",
  "updatedAt": "2022-08-04T18:54:09.903588+00:00",
  "displayName": "GroupFirmwareCompliance",
  "name": "GroupFirmwareCompliance",
  "jobTemplateUri": "/compute-ops-mgmt/v1beta2/job-templates/23b8ba2a-6c46-4223-b028-919382c7dcac",
  "associatedResourceUri": "/compute-ops-mgmt/v1beta2/groups/8a3a2a46-0102-48e2-bdd9-a29ee6909860",
  "resource": {
    "resourceUri": "/compute-ops-mgmt/v1beta2/groups/8a3a2a46-0102-48e2-bdd9-a29ee6909860",
    "type": "groups"
  },
  "data": {},
  "state": "COMPLETE",
  "status": "Complete",
  "statusDetails": {},
  "generation": 6
}
```