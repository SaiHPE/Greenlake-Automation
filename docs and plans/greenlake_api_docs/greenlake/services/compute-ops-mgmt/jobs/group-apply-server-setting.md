---
title: "Group Apply Server Settings Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/group-apply-server-setting.md"
scraped_at: "2026-06-07T05:46:01.264179+00:00Z"
---

# Group Apply Server Settings Job

## Overview

This job applies Redfish configuration settings to one or more servers in a group. Currently, this job supports "BIOS/ILO_SETTINGS" configuration. The target group must have a corresponding server setting configured.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| beff07ce-f36d-4699-9ac3-f872dcd63133 | compute-ops-mgmt/group | `redfish_subsystem*` `devices` `batch_size` |


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

## Job Parameters

This table summarizes the supported properties in `jobParams`.

| Property | JSON Type | Values | Required? |
|  --- | --- | --- | --- |
| `redfish_subsystem` | string(enum) | Checks Server setting category | Yes |
| `devices` | array | List of server IDs | No |
| `batch_size` | integer | Helps batch devices for parallel job execution | No |


### Parameter properties

- `redfish_subsystem`: This **required** field signifies the server setting category. The following values are supported:
  - `BIOS`: Update the server BIOS
  - `ILO_SETTINGS`: Update the server ILO Settings
- `devices`: This property is a list of server IDs to include in the server group apply setting. If specified, this non-empty list of server IDs limits the scope of the operation to the specified servers in the group. If left unspecified, all servers in the group are targeted.
- `batch_size`: This property enumerates the maximum number of devices to be considered while applying settings to improve parallelization. A batch size of one will update all devices sequentially. A batch size greater than one (up to the maximum) will create child jobs with the specified number of devices per job. These jobs will execute sequentially, however the devices within each batch will be updated in parallel.
  - Default: 1
  - Minimum: 1
  - Maximum: 20


## Examples

Here are some example request payloads for creating this job.

### Example 1


```json
{
  "jobTemplate": "beff07ce-f36d-4699-9ac3-f872dcd63133",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "8a3a2a46-0102-48e2-bdd9-a29ee6909860",
  "jobParams": {
    "devices": ["010639-C81+899010639081954", "824017-D94+788923530293582"],
    "redfish_subsystem": "BIOS",
    "batch_size": 1
  }
}
```

- This will result in multiple jobs with one device each, essentially updating all devices sequentially.


### Example 2


```json
{
  "jobTemplate": "beff07ce-f36d-4699-9ac3-f872dcd63133",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "8a3a2a46-0102-48e2-bdd9-a29ee6909860",
  "jobParams": {
    "devices": ["010639-C81+899010639081954"],
    "redfish_subsystem": "BIOS",
    "batch_size": 5
  }
}
```

- This will result in one child job with all devices.


### Example 3


```json
{
  "jobTemplate": "beff07ce-f36d-4699-9ac3-f872dcd63133",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "8a3a2a46-0102-48e2-bdd9-a29ee6909860",
  "jobParams": {
    "devices": ["010639-C81+899010639081954", "824017-D94+788923530293582"],
    "redfish_subsystem": "BIOS",
    "batch_size": 2
  }
}
```

- This will result in one child job with all devices.


### Example 4


```json
{
  "jobTemplate": "beff07ce-f36d-4699-9ac3-f872dcd63133",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "8a3a2a46-0102-48e2-bdd9-a29ee6909860",
  "jobParams": {
    "devices": [
      "010639-C81+899010639081954",
      "824017-D94+788923530293582",
      "350258-E98+302496249634750",
      "529473-F49+681036294925633"
    ],
    "redfish_subsystem": "BIOS",
    "batch_size": 2
  }
}
```

- This will result in 2 jobs that each have 2 devices.



```json
{
  "jobTemplate": "beff07ce-f36d-4699-9ac3-f872dcd63133",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "8a3a2a46-0102-48e2-bdd9-a29ee6909860",
  "jobParams": {
    "devices": [
      "010639-C81+899010639081954",
      "824017-D94+788923530293582",
      "350258-E98+302496249634750",
      "529473-F49+681036294925633",
      "23950-G30+394672147531944"
    ],
    "redfish_subsystem": "BIOS",
    "batch_size": 2
  }
}
```

- This will result in 3 jobs where the 2 jobs have 2 devices, and the last job has 1 device.


### Example 5


```json
{
  "jobTemplate": "beff07ce-f36d-4699-9ac3-f872dcd63133",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "8a3a2a46-0102-48e2-bdd9-a29ee6909860",
  "jobParams": {
    "devices": ["010639-C81+899010639081954", "824017-D94+788923530293582"],
    "redfish_subsystem": "ILO_SETTINGS",
    "batch_size": 1
  }
}
```

- This will result in multiple jobs with one device each, essentially updating all devices sequentially.