---
title: "Delete vCenter Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/vcenter-delete.md"
scraped_at: "2026-06-07T06:13:25.387947+00:00Z"
---

# Delete vCenter Job

## Overview

Use this job to delete a VMware vCenter external service connection.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 3f06fd6b-dfb1-4bad-bd04-939951797e97 | compute-ops-mgmt/external-service | See [Job Parameters](#job-parameters) section |


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

This table summarizes the supported properties in `data`.

| Property | JSON Type | Description | Required? |
|  --- | --- | --- | --- |
| `vCenterUrl`* | string | The URL or IP address of the vCenter server | Yes |
| `associatedGatewayUri`* | string (uri) | The URI of the associated gateway appliance | Yes |
| `externalServiceId`* | string (uuid) | The ID of the external service to delete | Yes |
| `vCenterUuid`* | string (uuid) | The UUID of the vCenter server | Yes |


### Parameter properties

- `vCenterUrl`: This **required** property specifies the URL or IP address of the vCenter server to be deleted.
- `associatedGatewayUri`: This **required** property is the URI of the gateway appliance associated with the vCenter connection.
  - Example: `/compute-ops-mgmt/v1beta1/appliances/gateway+eace0910-8007-4e1d-b1b4-0ed10c004d4e`
- `externalServiceId`: This **required** property is the UUID of the external service representing the vCenter connection.
- `vCenterUuid`: This **required** property is the UUID of the vCenter server as known by VMware.


## Example

The following example shows a request payload for creating this job.

### Example 1

Delete a vCenter external service.


```json
{
  "jobTemplate": "3f06fd6b-dfb1-4bad-bd04-939951797e97",
  "resourceId": "edee6027-f210-4546-bbee-9d5847e39bef",
  "jobParams": {
    "vCenterUrl": "192.0.2.50",
    "associatedGatewayUri": "/compute-ops-mgmt/v1beta1/appliances/gateway+eace0910-8007-4e1d-b1b4-0ed10c004d4e",
    "externalServiceId": "edee6027-f210-4546-bbee-9d5847e39bef",
    "vCenterUuid": "6c62c4f8-c4f2-470c-a6aa-9e5c18bd5355"
  }
}
```