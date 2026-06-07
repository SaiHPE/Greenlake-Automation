---
title: "Configure Ignore Risk settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/configure-ignore-ilo-security-risk-settings.md"
scraped_at: "2026-06-07T06:13:22.516674+00:00Z"
---

# Configure Ignore Risk settings

## Overview

This job is used to configure ignore iLO security risk settings.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| e1d69e76-38cc-4079-9192-a380baea2973 | compute-ops-mgmt/server | See [Job Parameters](#job-parameters) section |


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
| `ignoreSecuritySettings` | array | See [IgnoreSecuritySettings](#ignoresecuritysettings) section | yes |


## IgnoreSecuritySettings

This table summarizes the supported properties in `ignoresecuritysettings`.

| Property | JSON Type | Values | Required? |
|  --- | --- | --- | --- |
| `name` | string | name of the parameter | yes |
| `ignore` | boolean | perform ignore action | yes |
| `id` | string | parameter id | yes |


### Parameter properties

- `name` : This is the name of the parameter which need to be updated. It need to be same as it is in security parameters list under servers.
- `ignore` : This flag allows to configure ilo security ignore risk settings.
- `id` : This is the Id of the parameter.


## Examples

Configure ignore iLO security risk settings request payload examples for creating this job.

### Example 1

This will configure ilo security settings of 2 parameters to ignore true


```json
{
  "jobTemplate": "e1d69e76-38cc-4079-9192-a380baea2973",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "854361-001+2C201515GR",
  "jobParams": {
    "ignoreSecuritySettings": [
      {
        "name": "Authentication Failure Logging",
        "ignore": true,
        "id": "4"
      },
      {
        "name": "Secure Boot",
        "ignore": true,
        "id": "5"
      }
    ]
  }
}
```

### Example 2

This will configure ilo security settings of 2 parameters to ignore false


```json
{
  "jobTemplate": "e1d69e76-38cc-4079-9192-a380baea2973",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "854361-001+2C201515GR",
  "jobParams": {
    "ignoreSecuritySettings": [
      {
        "name": "Authentication Failure Logging",
        "ignore": false,
        "id": "4"
      },
      {
        "name": "Secure Boot",
        "ignore": false,
        "id": "5"
      }
    ]
  }
}
```