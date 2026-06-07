---
title: "Collect Server Inventory"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-inventory.md"
scraped_at: "2026-06-07T06:13:24.602353+00:00Z"
---

# Collect Server Inventory

## Overview

This job initiates a server inventory data collection job on directly managed or OneView managed servers.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| d6595f1b-84e6-4587-ade5-656e2a5ea20d | compute-ops-mgmt/server | `filters` `is_reports_call` |


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
| `filters` | array | List of inventory subresources to be requested | No |
| `is_reports_call` | boolean | Populates inventory to roundup DB | No |


### Parameter properties

- `filters`: This property is a list of inventory resources that should be collected from the server. An empty list will collect all inventory resources. The following case sensitive values are supported:
  - `Chassis`
  - `Processor`
  - `memory`
  - `networkAdapters`
  - `localStorage`
  - `localStorageV2`
  - `devices`
  - `devicesV2`
  - `powerSupplies`
  - `fans`
  - `firmware`
  - `software`
- `is_reports_call`: This flag determines if the inventory should be made available to reports.
  - Default: `false`


## Examples

Inventory request payload examples for creating this job.

### Example 1

Collect complete inventory of a server.


```json
{
  "jobTemplate": "d6595f1b-84e6-4587-ade5-656e2a5ea20d",
  "resourceType": "ccompute-ops-mgmt/server",
  "resourceId": "854361-001+2C201515GR",
  "jobParams": {
    "operationType": "GracefulShutdown"
  }
}
```

### Example 2

Collect complete server inventory and make it available for reporting.


```json
{
  "jobTemplate": "d6595f1b-84e6-4587-ade5-656e2a5ea20d",
  "resourceType": "ccompute-ops-mgmt/server",
  "resourceId": "854361-001+2C201515GR",
  "jobParams": {
    "is_reports_call": true
  }
}
```

### Example 3

Collect server inventory for the provided subresources in the filters.


```json
{
  "jobTemplate": "d6595f1b-84e6-4587-ade5-656e2a5ea20d",
  "resourceType": "ccompute-ops-mgmt/server",
  "resourceId": "854361-001+2C201515GR",
  "jobParams": {
    "filters": ["Chassis", "Processor", "memory", "networkAdapters"]
  }
}
```

### Example 4

Collect server inventory for the provided subresources in the filters and also make it available for reporting.


```json
{
  "jobTemplate": "d6595f1b-84e6-4587-ade5-656e2a5ea20d",
  "resourceType": "ccompute-ops-mgmt/server",
  "resourceId": "854361-001+2C201515GR",
  "jobParams": {
    "is_reports_call": true,
    "filters": ["devices", "powerSupplies", "fans", "firmware", "software"]
  }
}
```