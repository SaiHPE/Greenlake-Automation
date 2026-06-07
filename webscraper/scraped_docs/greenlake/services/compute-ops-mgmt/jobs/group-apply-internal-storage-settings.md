---
title: "Group Apply Internal Storage Settings Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/group-apply-internal-storage-settings.md"
scraped_at: "2026-06-07T05:46:00.483499+00:00Z"
---

# Group Apply Internal Storage Settings Job

## Overview

This job initiates a server group internal storage configuration that will affect some or all of the
server group members. As a pre-requisite, create a server setting with "STORAGE" as the category and assign it to the server group.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 54095626-3911-4fea-9741-816e2531994e | compute-ops-mgmt/group | `devices` `initialize*` `volumes*` |


> Job parameters marked with an `*` are required.


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
| `devices` | array | List of device IDs | No |
| `initialize` | boolean | When true, the existing internal storage configuration will be erased prior to applying the settings | Yes |
| `volumes` | array | Objects containing the `id` of an internal storage settings volume and a `name` for that volume | Yes |


### Parameter properties

- `devices`: The list of device IDs to apply the internal storage settings to. The devices must be members of the group. If omitted, the settings will be applied to all devices in the group.
- `initialize`: When true, any existing internal storage configuration will be erased prior to applying the configuration defined in the internal storage settings.
If existing volumes are present and this property is false, the job will fail without modifying the existing configuration.
- `volumes`: A list associating a name with each volume in the internal storage settings. Each member of the list is an object containing the `id` of an internal storage settings volume and a `name` for that volume.


## Examples

Here are a couple of example request payloads for creating this job.

### Example 1

Internal storage configuration with volume names for one server in a group.


```json
{
  "jobTemplate": "54095626-3911-4fea-9741-816e2531994e",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "04460955-6038-4339-ba72-c9b05a03876e",
  "jobParams": {
    "devices": ["059826-706+8899059826806785"],
    "initialize": true,
    "volumes": [
      {
        "id": "40af517d-3812-4038-b9f7-1c7ef65e091f",
        "name": "OS Volume"
      },
      {
        "id": "cc86b1ed-566d-4d0a-b35c-f0a50876c642",
        "name": "Data Volume"
      }
    ]
  }
}
```

### Example 2

Internal storage configuration with default volume names for multiple servers in a group.


```json
{
  "jobTemplate": "54095626-3911-4fea-9741-816e2531994e",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "initialize": true,
    "volumes": []
  }
}
```