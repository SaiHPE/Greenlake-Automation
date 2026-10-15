---
title: "Group Operating System Installation Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/group-os-install.md"
scraped_at: "2026-06-07T06:13:23.466585+00:00Z"
---

# Group Operating System Installation Job

## Overview

This job initiates a server group operating system installation that will affect some or all of the
server group members.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| e2952628-2629-4088-93db-91742304ef0c | compute-ops-mgmt/group | See [Job Parameters](#job-parameters) section |


> **Note** Before initiating the group operating system installation job, run the [Analyze server configuration for operating system installation](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/post_v1_analyze_os_install/) API to validate the presence of at least one storage volume on the server. If the server does not have any storage volumes, failing to run this API will lead to the failure of the OS installation job.


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
| `devices` | array | List of server IDs | No |
| `parallel` | boolean | Perform server OS installation in parallel | No |
| `stopOnFailure` | boolean | Stop after the first server OS installation failure | No |
| `osCompletionTimeoutMin` | integer | Amount of time (minutes) that Compute Ops Management waits before automatically marking an OS installation job complete | No |


### Parameter properties

- `devices`: This property is a list of server IDs to include in the server group Operating system installation. If specified, this non-empty list of server IDs limits the scope of the operation to the specified servers in the group. If left unspecified, all servers in the group are targeted.
- `parallel`: This flag determines if the operating system installation to each device in the group should occur in parallel or not.
  - Default: `true`
- `stopOnFailure`: This flag is applicable for serial operating system installation (i.e. `parallel: false`). It determines if the group
operating system installation process will continue after the first failure. If the flag is `false`, the installation continues after a failure. If
the flag is `true`, the installation stops after a failure and the remaining devices in the group will not undergo operating system installation.
  - Default: `false`
- `osCompletionTimeoutMin`: This property determines the amount of time (minutes) that Compute Ops Management waits before automatically marking an OS installation job complete. The operating system image is then unmounted from the server. The specified timeout value applies to each server group member.
  - Default: 240
  - Minimum: 60
  - Maximum: 720


## Patch Job

A job can be patched by issuing a `PATCH` to the `/compute-ops-mgmt/v1/jobs/<job-id>` endpoint with the correct payload for the job.

The following property is used when patching a job:

| Property | JSON Type | Description |
|  --- | --- | --- |
| `input` | object | Any input data required by the job. |


If the job was patched successfully, a `200` response is returned. The response includes the job resource which has a
job `resourceUri` that you can use to track the progress of the job.

## Examples

Here are a couple of example request payloads for creating this job.

### Example 1

Operating system installation for all servers in a group.


```json
{
  "jobTemplate": "e2952628-2629-4088-93db-91742304ef0c",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "04460955-6038-4339-ba72-c9b05a03876e"
}
```

### Example 2

Operating system installation for two servers in a group in parallel.


```json
{
  "jobTemplate": "e2952628-2629-4088-93db-91742304ef0c",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "parallel": true
  }
}
```

### Example 3

Operating system installation for two servers in a group in serial.


```json
{
  "jobTemplate": "e2952628-2629-4088-93db-91742304ef0c",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "parallel": false
  }
}
```

### Example 4

Operating system installation for two servers in a group with the timeout value set to 200 minutes.


```json
{
  "jobTemplate": "e2952628-2629-4088-93db-91742304ef0c",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "parallel": true,
    "osCompletionTimeoutMin": 200
  }
}
```