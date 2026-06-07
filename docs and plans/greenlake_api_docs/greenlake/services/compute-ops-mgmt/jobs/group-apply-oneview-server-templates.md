---
title: "Group Apply OneView Server Templates Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/group-apply-oneview-server-templates.md"
scraped_at: "2026-06-07T05:46:01.274421+00:00Z"
---

# Group Apply OneView Server Templates Job

## Overview

This job copies the server templates in the configured setting to the selected target appliance group members. The group must have a configured 'OVE_SERVER_TEMPLATES_VM' or 'OVE_SERVER_TEMPLATES_SYNERGY' setting.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| db3620d4-19a4-4b54-9804-83f8f59d48a4 | compute-ops-mgmt/group | `targetApplianceIds*` |


> Job parameters marked with a `*` are required.


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

The following table summarizes the supported properties in `jobParams`.

| Property | JSON Type | Values | Required? |
|  --- | --- | --- | --- |
| `targetApplianceIds` | array | List of device IDs | Yes |


### Parameter properties

- `targetApplianceIds`: This property lists the appliance IDs to include in the group apply setting. If specified, this non-empty list of appliance IDs limits the scope of the operation to the specified appliances in the group. If no device IDs are specified, an error occurs.


## Example

Here is an example request payload for creating this job.

### Example 1

Copy OneView server templates associated with a group to specific appliance group members.


```json
{
  "jobTemplate": "db3620d4-19a4-4b54-9804-83f8f59d48a4",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "213e7c32-3046-4419-95dc-cc816adb95e9",
  "jobParams": {
    "targetApplianceIds": ["oneview+2ec6bdbf-59e2-4d1c-b59e-8147927321fd"]
  }
}
```