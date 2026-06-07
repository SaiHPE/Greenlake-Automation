---
title: "HPE Compute Ops Management API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest.md"
scraped_at: "2026-06-07T05:46:29.487763+00:00Z"
---

# HPE Compute Ops Management API

HPE Compute Operations Management provides a Restful API to
customers who want to manage their devices programmatically or through
a command line. The API enables customers to invoke operations or tasks
such as list devices, see device details, device health, and manage their
device's firmware.

<div style="background-color: #EBEDF0; color: #444444; padding: 20px; margin: 10px 0px; border-radius: 8px; font-size: 16px;">
<h5 style="padding: 0px; margin: 0px; letter-spacing: 0.3px; text-transform: uppercase; font-size: 16px;">UPDATED API ENDPOINTS</h5>

Compute Ops Management now supports the HPE GreenLake API endpoints (`<region>.api.greenlake.hpe.com`).
The [Guide](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/guide/) contains more information
about this change.
</div>

Version: latest
License: HPE End User License Agreement

## Servers

API endpoint for US West
```
https://us-west.api.greenlake.hpe.com
```

API endpoint for EU Central
```
https://eu-central.api.greenlake.hpe.com
```

API endpoint for AP Northeast
```
https://ap-northeast.api.greenlake.hpe.com
```

## Security

### Bearer

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE Compute Ops Management API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/index.yaml)

## accounts - v1beta1

### Get account details

 - [GET /compute-ops-mgmt/v1beta1/accounts/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/accounts-v1beta1/get_accounts.md): Retrieve account details by ID.

### Get list of tenant accounts

 - [GET /compute-ops-mgmt/v1beta1/accounts/{id}/tenants](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/accounts-v1beta1/get_uidoorway_v1_tenant_details_by_id.md): Get list of tenant accounts for an MSP account

## activation-keys - v1beta1

### Generate an activation key to onboard a device or appliance

 - [POST /compute-ops-mgmt/v1beta1/activation-keys](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/activation-keys-v1beta1/create_activation-keys_v1_beta1.md): Note: This API only works with iLO 6 1.62 and later or with iLO 5 3.09 and later
Generates a new activation key for onboarding iLO for direct management or secure gateway management, or secure gateway appliances

### Retrieve all activation keys to onboard a device or appliance

 - [GET /compute-ops-mgmt/v1beta1/activation-keys](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/activation-keys-v1beta1/get_activation-keys_v1_beta1.md): Retrieve a paginated collection of activation keys for onboarding iLO for direct management or secure gateway management, or secure gateway appliances.

### Delete an activation key by activation key

 - [DELETE /compute-ops-mgmt/v1beta1/activation-keys/{activation_key}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/activation-keys-v1beta1/delete_activation-keys_v1_beta1_by_id.md): This API deletes an activation key generated to onboard iLO for direct management or secure gateway management.

## activation-tokens - v1beta1

### Generate an activation token to onboard servers (deprecated)

 - [POST /compute-ops-mgmt/v1beta1/activation-tokens](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/activation-tokens-v1beta1/create_activation-tokens_v1_beta1.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 07 March 2025 23:59:59 GMT
- Sunset at: Mon, 07 April 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1beta1/activation-keys

This API generates a new activation token, valid for a specified duration. 
Once created, the activation token cannot be retrieved. If needed, a new
activation token can be generated.

## activities - v1beta2

### List all activities

 - [GET /compute-ops-mgmt/v1beta2/activities](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/activities-v1beta2/get_v1beta2_activities.md): Retrieve the list of activities


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

## ahs-files - v1beta1

### Create AHS file upload

 - [POST /compute-ops-mgmt/v1beta1/ahs-files](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/ahs-files-v1beta1/post_ahs_file_upload_request_v1beta1.md): A pre-signed URL can be created by issuing this POST call with correct payload for the task.
The pre-signed URL allows the user to upload the selected file directly and securely to the 
Compute Ops Management data store provided by Amazon Web Services (AWS) Simple Storage Service (S3).

The pre-signed URL is valid for a maximum of 10 minutes. The user must upload the file within this 
time period, or the link will expire, and the upload will fail.

Note: Use the “parameters” list to create a pre-signed URL response to fill all the values in . 
It will form the upload command.

An example curl command to upload an AHS file is shown below:

curl -i -F key=AHS_DISCONNECTED/427275fcddef29436/c924e770-...-9219276d2a5f/upload_file_presigned_post.ahs 
-F x-amz-algorithm=AWS4-HMAC-SHA256 -F x-amz-credential=example_credential -F x-amz-date=20250213T000000Z 
-F x-amz-security-token=example_token 
-F policy=example_policy 
-F x-amz-signature=example_signature -F file=@P05172-B21+2M2D110304_FWUFailure.ahs 
'https://dev-hpecomputesupport-us-west-2.s3.amazonaws.com/'

Sample Success Response:

HTTP/1.1 200 Connection Established
Proxy-Agent: Zscaler/6.2
HTTP/1.1 100 Continue
HTTP/1.1 204 No Content
x-amz-id-2: LYH6S+m7DrtihxwwXGNm8l7DFsJNwlBS5ps0+vOuucVy2dzDd9OMBZLeund2vJvUUtBWiQETYn0=
x-amz-request-id: 3RNFF7X985Y2M0WV
Date: Mon, 16 Dec 2024 14:17:04 GMT
x-amz-server-side-encryption: aws:kms
x-amz-server-side-encryption-aws-kms-key-id: arn:aws:kms:us-west-2:647619633241:key/ebcad3a6-b6e2-4314-acf1-447f9f38f9bc
x-amz-server-side-encryption-bucket-key-enabled: true
ETag: "6e215e86cc62e52ad1ff5f184edd483d"
Location: https://dev-hpecomputesupport-us-west-2.s3.amazonaws.com/AHS_DISCONNECTED%2F427275fcddef11ebaeaea25b204e9436%2F72684583-59cf-4a81-b4c4-c4e586c8b0c1%2FP05172-B21+2M2D110304_FWUFailure.ahs
Server: AmazonS3

### List of all AHS files

 - [GET /compute-ops-mgmt/v1beta1/ahs-files](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/ahs-files-v1beta1/get_ahs_files_parse_request_v1beta1.md): Retrieves the status of the AHS file parsing request.

### Get AHS file by id

 - [GET /compute-ops-mgmt/v1beta1/ahs-files/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/ahs-files-v1beta1/get_ahs_file_parse_request_v1beta1_by_id.md): Retrieves the status of the AHS file parsing request by its id.

### Update the parsing status of an AHS file

 - [PATCH /compute-ops-mgmt/v1beta1/ahs-files/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/ahs-files-v1beta1/patch_ahs_file_parse_status_request_v1beta1_by_id.md): This API triggers a patch request to update the parsing status of an AHS file.
The patch request allows updating the existing parsing status of an AHS file from ANALYSIS_PENDING or ANALYSIS_IN_PROGRESS to ANALYSIS_FAILED.

### Parse uploaded AHS file

 - [POST /compute-ops-mgmt/v1beta1/ahs-files/{id}/parse](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/ahs-files-v1beta1/post_ahs_file_parse_request_v1beta1_by_id.md): This API triggers a post request to parse an AHS file.

### Download parsed AHS file contents

 - [GET /compute-ops-mgmt/v1beta1/ahs-files/{id}/download](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/ahs-files-v1beta1/get_ahs_file_download_request_v1beta1.md): This API triggers a get request to download parsed (CSV/JSON) AHS file contents.

## secure-gateway-appliances - v1beta2

### List all secure gateway appliances

 - [GET /compute-ops-mgmt/v1beta2/appliances](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/secure-gateway-appliances-v1beta2/get_v1beta2_appliances.md): Retrieve data for all secure gateway appliances.

### Get a secure gateway appliance by id

 - [GET /compute-ops-mgmt/v1beta2/appliances/{device_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/secure-gateway-appliances-v1beta2/get_v1beta2_appliances_by_id.md): Get a specific secure gateway appliance by id.

### Delete a secure gateway appliance by id

 - [DELETE /compute-ops-mgmt/v1beta2/appliances/{device_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/secure-gateway-appliances-v1beta2/delete_v1beta2_appliances_by_id.md): Delete a specific secure gateway appliance by id.

### Get secure gateway appliance certificate by id

 - [GET /compute-ops-mgmt/v1beta2/appliances/{device_id}/certificate](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/secure-gateway-appliances-v1beta2/get_v1beta2_appliances_certificate_by_id.md): Get specific secure gateway appliance certificate by id.

## appliance-firmware-bundles - v1

### List all appliance firmware bundles

 - [GET /compute-ops-mgmt/v1/appliance-firmware-bundles](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/appliance-firmware-bundles-v1/get_v1_appliance_firmware_bundles.md): Retrieve the list of appliance firmware bundles

### Get an appliance firmware bundle by ID

 - [GET /compute-ops-mgmt/v1/appliance-firmware-bundles/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/appliance-firmware-bundles-v1/get_v1_appliance_firmware_bundle_by_id.md): Retrieve the appliance firmware bundle details by its id

## appliance-firmware-bundles - v1beta1

### List all appliance firmware bundles

 - [GET /compute-ops-mgmt/v1beta1/appliance-firmware-bundles](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/appliance-firmware-bundles-v1beta1/get_v1beta1_appliance_firmware_bundles.md): Retrieve the list of appliance firmware bundles

### Get an appliance firmware bundle by ID

 - [GET /compute-ops-mgmt/v1beta1/appliance-firmware-bundles/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/appliance-firmware-bundles-v1beta1/get_v1beta1_appliance_firmware_bundle_by_id.md): Retrieve the appliance firmware bundle details by its id

## approval-policy - v1beta2

### Create an approval policy

 - [POST /compute-ops-mgmt/v1beta2/approval-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-policy-v1beta2/post_create_approval_policy_v1beta2.md): Creates an approval policy

### List all approval policies

 - [GET /compute-ops-mgmt/v1beta2/approval-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-policy-v1beta2/get_v1beta2_approval_policies.md): Retrieves all active approval policies

### Get approval policy by id

 - [GET /compute-ops-mgmt/v1beta2/approval-policies/{policy_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-policy-v1beta2/get_v1beta2_approval_policy_by_id.md): Retrieves approval policy by id

### Update the policy by id

 - [PATCH /compute-ops-mgmt/v1beta2/approval-policies/{policy_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-policy-v1beta2/patch_v1beta2_approval_policy_by_id.md): Updates an approval policy

### Delete an approval policy

 - [DELETE /compute-ops-mgmt/v1beta2/approval-policies/{policy_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-policy-v1beta2/delete_v1beta1_approval_policy_by_id.md): Deletes an approval policy

## approval-request - v1beta2

### List all approval requests

 - [GET /compute-ops-mgmt/v1beta2/approval-requests](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-request-v1beta2/get_v1beta1_approval_requests.md): Retrieves all active approval requests

### Get approval request by id

 - [GET /compute-ops-mgmt/v1beta2/approval-requests/{request_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-request-v1beta2/get_v1beta1_approval_request_by_id.md): Retrieves an approval request by id

### Update the request by id

 - [PATCH /compute-ops-mgmt/v1beta2/approval-requests/{request_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-request-v1beta2/patch_v1beta1_approval_request_by_id.md): Updates an approval request

### Approve request

 - [POST /compute-ops-mgmt/v1beta2/approval-requests/{request_id}/approve](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-request-v1beta2/post_create_approval_request_v1beta2.md): Approves or declines an approval request

## async-operations - v1

### List all async operations

 - [GET /compute-ops-mgmt/v1/async-operations](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/async-operations-v1/get_v1_async_operations.md): Retrieve a list of async operations for the last 7 days

### Retrieve an async operation by ID

 - [GET /compute-ops-mgmt/v1/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/async-operations-v1/get_v1_async_operations_by_id.md): Retrieve a specific async operation by ID for the last 7 days

### Cancel an async operation by ID

 - [POST /compute-ops-mgmt/v1/async-operations/{id}/cancel](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/async-operations-v1/cancel_v1_async_operation_by_id.md): Cancel a specific async operation by ID. Only async operations of following operation types can be cancelled.
- SUSTAINABILITY_METRICS_COLLECTION

## async-operations - v1beta1

### List all async operations

 - [GET /compute-ops-mgmt/v1beta1/async-operations](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/async-operations-v1beta1/get_v1beta1_async_operations.md): Retrieve a list of async operations for the last 7 days

### Retrieve an async operation by ID

 - [GET /compute-ops-mgmt/v1beta1/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/async-operations-v1beta1/get_v1beta1_async_operations_by_id.md): Retrieve a specific async operation by ID for the last 7 days

## energy-over-time - v1beta1

### Retrieve energy usage over time

 - [GET /compute-ops-mgmt/v1beta1/energy-over-time](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/energy-over-time-v1beta1/get_energy_over_time.md): Retrieve energy consumption, carbon emissions and cost statistics over a time interval.

## energy-by-entity - v1beta1

### Retrieve energy usage by entity

 - [GET /compute-ops-mgmt/v1beta1/energy-by-entity](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/energy-by-entity-v1beta1/get_energy_by_entity.md): Retrieve energy consumption, CO2 emissions and cost details per entity.

## external-services - v1beta1

### List all external services

 - [GET /compute-ops-mgmt/v1beta1/external-services](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/external-services-v1beta1/get_v1beta1_external_services.md): Get the list of external services configured


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Create external services

 - [POST /compute-ops-mgmt/v1beta1/external-services](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/external-services-v1beta1/create_external_services.md): Create configuration for external service


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.


### Supported Service Types

| Service Type | Description |
|--------------|-------------|
| SERVICE_NOW | ServiceNow integration for incident management |
| DSCC | Data Services Cloud Console integration |
| VMWARE_VCENTER | HPE Compute Ops Management plug-in for VMware vCenter integration |

### ServiceNow Integration
When an external configuration is configured on Compute Ops Management, these attributes will be used to set the
scope of events for which incidents will be created on the external service.

Incident scope selections are made such that each selection increases the scope
of the set of events that will be included.
The order of event selections from minimum to maximum scope are

  * serviceEventIssues - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalEventIssues - Events that are not service events but have
  a severity level of 'critical'
  * warningEventIssues - Events that are not service events but have a
  severity level of 'warning'

Below software events are independent of above events, but either one of the above or below option must be selected. 
  * utilizationAlerts - Events that are generated for breaching configured 
  power utilization threshold.

Below events are independent of above events, and may be selected independently.
  * disconnectedEvent - Events that are generated for after waiting for configured hours of disconnectivity.
  * powerResetEvent - Events that are generated for power change events.

Note that healthNotification is not part of the event notification set and
may be set independently.

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| serviceEventIssues    | criticalEventIssues       | warningEventIssues   | utilizationAlerts   | powerResetEvent     | disconnectedEvent   |
|:---------------------:|:-------------------------:|:--------------------:|:-------------------:|:-------------------:|:-------------------:|
| False                 | False                     | False                | True                | True/False          | [0/1/2/3]           |
| True                  | False                     | False                | True                | True/False          | [0/1/2/3]           |
| True                  | False                     | False                | False               | True/False          | [0/1/2/3]           |
| True                  | True                      | False                | True                | True/False          | [0/1/2/3]           |
| True                  | True                      | False                | False               | True/False          | [0/1/2/3]           |
| True                  | True                      | True                 | True                | True/False          | [0/1/2/3]           |
| True                  | True                      | True                 | False               | True/False          | [0/1/2/3]           |

### Initial values
All values are initially false except serviceEventIssues with the result being that incidents will be created only for service events.

### VMware vCenter Integration
When adding VMware vCenter as an external service for the HPE Compute Ops Management plug‑in for VMware vCenter integration, provide the following attributes:

  * vCenterUrl - The URL or IP address of the vCenter server
  * associatedGatewayUri - The URI of the associated secure gateway appliance
  * vCenterCertFingerprint - The SHA-256 fingerprint of the vCenter server certificate
  * authenticationType - Must be BASIC with username and password credentials

### Get an external-services item by ID

 - [GET /compute-ops-mgmt/v1beta1/external-services/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/external-services-v1beta1/get_v1beta1_external_services_by_id.md): Get a specific external-services item by external-services id.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Delete an external-services item

 - [DELETE /compute-ops-mgmt/v1beta1/external-services/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/external-services-v1beta1/delete_v1beta1_external_services_by_id.md): Delete an external-services item.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Patch an external-services item

 - [PATCH /compute-ops-mgmt/v1beta1/external-services/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/external-services-v1beta1/patch_v1beta1_external_services_by_id.md): Partially update an external-services item


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.


### Supported Service Types

| Service Type | Description |
|--------------|-------------|
| SERVICE_NOW | ServiceNow integration for incident management |
| DSCC | Data Services Cloud Console integration |
| VMWARE_VCENTER | HPE Compute Ops Management plug-in for VMware vCenter integration |

### ServiceNow Integration
When an external configuration is configured on Compute Ops Management, these attributes will be used to set the
scope of events for which incidents will be created on the external service.

Incident scope selections are made such that each selection increases the scope
of the set of events that will be included.
The order of event selections from minimum to maximum scope are

  * serviceEventIssues - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalEventIssues - Events that are not service events but have
  a severity level of 'critical'
  * warningEventIssues - Events that are not service events but have a
  severity level of 'warning'

Below software events are independent of above events, but either one of the above or below option must be selected. 
  * utilizationAlerts - Events that are generated for breaching configured 
  power utilization threshold

Below events are independent of above events, and may be selected independently.
  * disconnectedEvent - Events that are generated for after waiting for configured hours of disconnectivity.
  * powerResetEvent - Events that are generated for power change events.

Note that healthNotification is not part of the event notification set and
may be set independently.

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| serviceEventIssues    | criticalEventIssues       | warningEventIssues   | utilizationAlerts   | powerResetEvent     | disconnectedEvent   |
|:---------------------:|:-------------------------:|:--------------------:|:-------------------:|:-------------------:|:-------------------:|
| False                 | False                     | False                | True                | True/False          | [0/1/2/3]           |
| True                  | False                     | False                | True                | True/False          | [0/1/2/3]           |
| True                  | False                     | False                | False               | True/False          | [0/1/2/3]           |
| True                  | True                      | False                | True                | True/False          | [0/1/2/3]           |
| True                  | True                      | False                | False               | True/False          | [0/1/2/3]           |
| True                  | True                      | True                 | True                | True/False          | [0/1/2/3]           |
| True                  | True                      | True                 | False               | True/False          | [0/1/2/3]           |

### Initial values
All values are initially false except serviceEventIssues with the result being that incidents will be created only for service events.

### VMware vCenter Integration
When updating the VMware vCenter external service, provide the following attributes:

  * name - The display name of the vCenter integration
  * vCenterUrl - The URL or IP address of the vCenter server
  * associatedGatewayUri - The URI of the associated secure gateway appliance
  * vCenterCertFingerprint - The SHA-256 fingerprint of the vCenter server certificate
  * authentication - Username and password credentials

### Perform a test with a configured external service

 - [POST /compute-ops-mgmt/v1beta1/external-services/{id}/test](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/external-services-v1beta1/test_external_services.md): Used for performing a test to verify the integration of the configured external service.  An activity will be generated as a result of this test and indicates the success or failure of this test.
* For external service with serviceType as SERVICE_NOW, this endpoint will generate a test incident for ServiceNow.

* For external service with serviceType as DSCC, this endpoint will test the integration connection to Data Services Cloud Console.  This endpoint is available even if the configured Data Services Cloud Console integration is disabled.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

## filters - v1beta1

### List all saved filters

 - [GET /compute-ops-mgmt/v1beta1/filters](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/filters-v1beta1/get_filters.md): Retrieve a paginated collection of saved filter resources.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Save a filter

 - [POST /compute-ops-mgmt/v1beta1/filters](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/filters-v1beta1/create_filter.md): Create a new saved filter resource.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get filterable properties

 - [GET /compute-ops-mgmt/v1beta1/filters/properties](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/filters-v1beta1/get_filter_properties.md): Retrieve information about resource properties usable in saved filters.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get a saved filter

 - [GET /compute-ops-mgmt/v1beta1/filters/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/filters-v1beta1/get_filter.md): Retrieve a single saved filter resource by ID.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Delete a saved filter

 - [DELETE /compute-ops-mgmt/v1beta1/filters/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/filters-v1beta1/delete_filter.md): Delete a saved filter resource.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Update a saved filter

 - [PATCH /compute-ops-mgmt/v1beta1/filters/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/filters-v1beta1/patch_filter.md): Update a saved filter resource by using the RFC 7396 (JSON Merge Patch) format.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### List resources matching a filter

 - [GET /compute-ops-mgmt/v1beta1/filters/{id}/matches](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/filters-v1beta1/get_filter_matches.md): Retrieve a paginated collection of match entries that indicate which resources match a saved filter.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

## firmware-bundles - v1

### List all firmware bundles

 - [GET /compute-ops-mgmt/v1/firmware-bundles](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/firmware-bundles-v1/get_v1_firmware_bundles.md): Retrieve the list of firmware bundles

### Get a firmware bundle by ID

 - [GET /compute-ops-mgmt/v1/firmware-bundles/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/firmware-bundles-v1/get_v1_firmware_bundle_by_id.md): Retrieve the firmware bundle details by its id

## firmware-bundles-details - v1

### Get component details by firmware bundle ID

 - [GET /compute-ops-mgmt/v1/firmware-bundles/{id}/bundle-details](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/firmware-bundles-details-v1/get_v1_firmware_bundle_details_by_id.md): Retrieve component details by firmware bundle id

## firmware-bundles - v1beta2

### List all firmware bundles

 - [GET /compute-ops-mgmt/v1beta2/firmware-bundles](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/firmware-bundles-v1beta2/get_v1beta2_firmware_bundles.md): Retrieve the list of firmware bundles


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get a firmware bundle by ID

 - [GET /compute-ops-mgmt/v1beta2/firmware-bundles/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/firmware-bundles-v1beta2/get_v1beta2_firmware_bundle_by_id.md): Retrieve the firmware bundle details by its id


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

## groups - v1

### List all groups

 - [GET /compute-ops-mgmt/v1/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/get_v1_groups.md): Get the list of a user's groups.

### Create a group

 - [POST /compute-ops-mgmt/v1/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/create_v1_group.md): Create a group for a specific user.

### Get a group by ID

 - [GET /compute-ops-mgmt/v1/groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/get_v1_group_by_id.md): Get a specific group by group id.

### Delete a group

 - [DELETE /compute-ops-mgmt/v1/groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/delete_v1_group_by_id.md): Delete a group.

### Patch a group

 - [PATCH /compute-ops-mgmt/v1/groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/patch_v1_group_by_id.md): Partially update a group.

### List all devices compliance in a group

 - [GET /compute-ops-mgmt/v1/groups/{group-id}/compliance](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/get_v1_group_devices_compliance.md): List all the device's compliance detail

### Get a device compliance by compliance Id

 - [GET /compute-ops-mgmt/v1/groups/{group-id}/compliance/{compliance-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/get_v1_compliance_by_compliance_id.md): Get a specific device compliance detail of the group by passing group id and compliance id.

### List all devices in a group

 - [GET /compute-ops-mgmt/v1/groups/{group-id}/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/get_v1_group_devices.md): List all devices in a group

### Assign device(s) to a group

 - [POST /compute-ops-mgmt/v1/groups/{group-id}/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/assign_v1_group_devices.md): Assign device(s) to a group using an asynchronous operation. On a successful request this endpoint will return a 202 Accepted response with a Location header that contains the resource URI of the operation. That resource URI can then be used to monitor the asynchronous operation's status.

### Unassign device(s) from a group

 - [POST /compute-ops-mgmt/v1/groups/{group-id}/devices/unassign](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/unassign_v1_group_devices.md): Unassign device(s) from a group using an asynchronous operation. On a successful request this endpoint will return a 202 Accepted response with a Location header that contains the resource URI of the operation. That resource URI can then be used to monitor the asynchronous operation's status.

### Get external storage compliance

 - [GET /compute-ops-mgmt/v1/groups/{group-id}/external-storage-compliance](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/get_v1_group_external_storage_compliance.md): List all the external storage's compliance detail

## groups - v1beta3

### List all groups

 - [GET /compute-ops-mgmt/v1beta3/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_groups.md): Get the list of a user's groups.

### Create a group

 - [POST /compute-ops-mgmt/v1beta3/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/create_v1beta3_group.md): Create a group for a specific user.

### Get a group by ID

 - [GET /compute-ops-mgmt/v1beta3/groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_group_by_id.md): Get a specific group by group id.

### Delete a group

 - [DELETE /compute-ops-mgmt/v1beta3/groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/delete_v1beta3_group_by_id.md): Delete a group.

### Patch a group

 - [PATCH /compute-ops-mgmt/v1beta3/groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/patch_v1beta3_group_by_id.md): Partially update a group.

### List all devices compliance in a group

 - [GET /compute-ops-mgmt/v1beta3/groups/{group-id}/compliance](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_group_devices_compliance.md): List all the device's compliance detail

### Get a device compliance by compliance Id

 - [GET /compute-ops-mgmt/v1beta3/groups/{group-id}/compliance/{compliance-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_compliance_by_compliance_id.md): Get a specific device compliance detail of the group by passing group id and compliance id.

### List all devices in a group

 - [GET /compute-ops-mgmt/v1beta3/groups/{group-id}/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_group_devices.md): List all devices in a group

### Assign device(s) to a group

 - [POST /compute-ops-mgmt/v1beta3/groups/{group-id}/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/assign_v1beta3_group_devices.md): Assign device(s) to a group using an asynchronous operation. On a successful request this endpoint will return a 202 Accepted response with a Location header that contains the resource URI of the operation. That resource URI can then be used to monitor the asynchronous operation's status.

### Unassign device(s) from a group

 - [POST /compute-ops-mgmt/v1beta3/groups/{group-id}/devices/unassign](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/unassign_v1beta3_group_devices.md): Unassign device(s) from a group using an asynchronous operation. On a successful request this endpoint will return a 202 Accepted response with a Location header that contains the resource URI of the operation. That resource URI can then be used to monitor the asynchronous operation's status.

### Get external storage compliance

 - [GET /compute-ops-mgmt/v1beta3/groups/{group-id}/external-storage-compliance](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_group_external_storage_compliance.md): List all the external storage's compliance detail

### List all devices iLO Settings compliance in a group

 - [GET /compute-ops-mgmt/v1beta3/groups/{group-id}/ilo-settings-compliance](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_group_ilo_settings_compliance.md): List all the device's iLO Settings compliance detail

### Get a device compliance by iLO Settings compliance Id

 - [GET /compute-ops-mgmt/v1beta3/groups/{group-id}/ilo-settings-compliance/{ilo-settings-compliance-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_ilo_settings_compliance_by_compliance_id.md): Get a specific device compliance detail of the group by passing group id and iLO Settings compliance id.

## groups - v1beta2

### List all groups

 - [GET /compute-ops/v1beta2/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_groups.md): Get the list of a user's groups.

### Create a group

 - [POST /compute-ops/v1beta2/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/create_v1beta2_group.md): Create a group for a specific user.

To create a OneView appliance group, please use the v1beta3 API.

### Get a group by ID

 - [GET /compute-ops/v1beta2/groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_group_by_id.md): Get a specific group by group id.

### Delete a group

 - [DELETE /compute-ops/v1beta2/groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/delete_v1beta2_group_by_id.md): Delete a group.

### Patch a group

 - [PATCH /compute-ops/v1beta2/groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/patch_v1beta2_group_by_id.md): Partially update a group.

### List all devices compliance in a group

 - [GET /compute-ops/v1beta2/groups/{group-id}/compliance](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_group_devices_compliance.md): List all the device's compliance detail

### Get a device compliance by compliance Id

 - [GET /compute-ops/v1beta2/groups/{group-id}/compliance/{compliance-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_compliance_by_compliance_id.md): Get a specific device compliance detail of the group by passing group id and compliance id.

### List all devices in a group

 - [GET /compute-ops/v1beta2/groups/{group-id}/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_group_devices.md): List all devices in a group

### Assign a device to a group

 - [POST /compute-ops/v1beta2/groups/{group-id}/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/assign_v1beta2_group_devices.md): Assign a device to a group

### Bulk unassign devices from a group

 - [DELETE /compute-ops/v1beta2/groups/{group-id}/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/unassign_v1beta2_group_devices.md): Bulk unassign devices from a group

### Unassign a device from a group

 - [DELETE /compute-ops/v1beta2/groups/{group-id}/devices/{device-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/unassign_v1beta2_group_device_by_id.md): Unassign a device from a group

### Get external storage compliance

 - [GET /compute-ops/v1beta2/groups/{group-id}/external-storage-compliance](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_group_external_storage_compliance.md): List all the external storage's compliance detail

### Get iLO Settings compliance

 - [GET /compute-ops/v1beta2/groups/{group-id}/ilo-settings-compliance](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_group_ilo_settings_compliance.md): List all the iLO Settings compliance detail

### Get a device iLO Settings compliance by iLO Settings compliance Id

 - [GET /compute-ops/v1beta2/groups/{group-id}/ilo-settings-compliance/{ilo-settings-compliance-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_ilo_settings_compliance_by_compliance_id.md): Get a specific device compliance detail of the group by passing group id and iLO Settings compliance id.

## job-templates - v1beta2

### List all job templates

 - [GET /compute-ops-mgmt/v1beta2/job-templates](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/job-templates-v1beta2/get_v1beta2_job_templates.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 28 Feb 2025 23:59:59 GMT
- Sunset at : Tue, 1 Apr 2025 23:59:59 GMT
- This resource is being removed. The information necessary to create jobs is documented in the Jobs Definition section. There you can find all available jobs and details on how to create each job.

Retrieve the list of job templates

### Get a job template

 - [GET /compute-ops-mgmt/v1beta2/job-templates/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/job-templates-v1beta2/get_v1beta2_job_template_by_id.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 28 Feb 2025 23:59:59 GMT
- Sunset at : Tue, 1 Apr 2025 23:59:59 GMT
- This resource is being removed. The information necessary to create jobs is documented in the Jobs Definition section. There you can find all available jobs and details on how to create each job.

Retrieve details about the job template referenced by its id

## jobs - v1

### List all jobs

 - [GET /compute-ops-mgmt/v1/jobs](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1/get_v1_jobs.md): Retrieve the list of jobs

### Create a job

 - [POST /compute-ops-mgmt/v1/jobs](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1/create_v1_job.md): Create a job for a given resource. A job is a multi-step task performed by Compute Ops Manager.

This table summarizes the jobs and their template IDs. For more information about each job template, expand the Job
Definitions section and click on Overview to get started.

| Name                                 | Description                                         | Resource Type      | Template ID                          |
| ------------------------------------ | --------------------------------------------------  | ------------------ | ------------------------------------ |
| Server Power Off                     | Power off a server                                  | compute-ops/server | d0c13b58-748c-461f-9a61-c0c5c71f1bb4 |
| Server Power On                      | Power on a server                                   | compute-ops/server | 0cbb2377-1834-488d-840c-d5bf788c34fb |
| Server Restart                       | Restart a server                                    | compute-ops/server | 30110551-cad6-4069-95b8-dbce9bbd8525 |
| Server Cold Boot                     | Cold boot a server                                  | compute-ops/server | aacfb3e0-6575-4d4f-a711-1ee1ae768407 |
| Server Firmware Update               | Update firmware on a server                         | compute-ops/server | fd54a96c-cabc-42e3-aee3-374a2d009dba |
| Server iLO Firmware Update           | Update iLO component firmware on a server           | compute-ops/server | 94caa4ef-9ff8-4805-9e97-18a09e673b66 |
| Server External Storage Details      | Collect external storage details for a server       | compute-ops/server | 9310319e-7b7f-41ba-8b24-8b34eed1ca62 |
| Server Firmware Download             | Download firmware on a server                       | compute-ops/server | 0683ada8-1a89-49dd-bf04-6df715b708a6 |
| Server Set UID Indicator On          | Turn on the UID indicator light on a server         | compute-ops/server | a46b210a-b0c7-4223-ab43-c4c1e77e680c |
| Server Set UID Indicator Off         | Turn off the UID indicator light on a server        | compute-ops/server | fd837434-a2f2-4bc8-b1b4-ec068bd036aa |
| Server Enable Maintenance Mode       | Enable maintenance mode for a server                | compute-ops/server | 4eb92af1-1ce4-4cb0-8581-fb5a7dcdbf2b |
| Server Disable Maintenance Mode      | Disable maintenance mode for a server               | compute-ops/server | 2798720f-b090-427d-b210-e48d33ce2f27 |
| Appliance Software Update            | Update OneView appliance                            | compute-ops/oneview-appliance | 1c4ac4be-8eeb-49f2-a86a-fd8c9182616c |
| Synchronize firmware baseline        | Synchronize firmware baseline of a vcenter          | compute-ops/external-service | 0fe73adb-9d52-4f00-9540-6ec82f265d82 |
| Remove vCenter                       | Remove a vCenter                                    | compute-ops/external-service | 3f06fd6b-dfb1-4bad-bd04-939951797e97 |
| Group Firmware Update                | Update firmware on servers in a group               | compute-ops/group  | 91159b5e-9eeb-11ec-a9da-00155dc0a0c0 |
| Group Firmware Compliance            | Calculate firmware compliance of servers in a group | compute-ops/group  | 23b8ba2a-6c46-4223-b028-919382c7dcac |
| Group Appliance Update               | Update OneView appliances in a group                | compute-ops/group  | f69f553a-5004-4a08-9283-5b60abd9eb4a |
| Group Apply Internal Storage Settings | Apply internal storage settings on servers in a group | compute-ops/group | 54095626-3911-4fea-9741-816e2531994e |
| Group Apply Server Setting           | Apply server setting on a group                     | compute-ops/group  | beff07ce-f36d-4699-9ac3-f872dcd63133 |
| Group Apply External Storage Settings | Apply external storage settings on servers in a group | compute-ops/group  | fcb79270-5954-42e9-9374-6a065b6d494a |
| Group External Storage Compliance    | Calculate external storage compliance of servers in a group | compute-ops/group | 7177aa6a-e8f8-4e9b-ae31-e01dafcc81df |
| Group Firmware Download              | Download firmware on servers in a group             | compute-ops/group  | a17a7aa9-4540-4c21-bbf2-31af4ff65e98 |
| Collect Server Inventory             | Collect complete or filtered server inventory       | compute-ops/server | d6595f1b-84e6-4587-ade5-656e2a5ea20d |
| Collect Server Network Connectivity  | Collect server adapter port to switch port mappings | compute-ops/server | b21ca9e2-8a1b-11ee-b9d1-0242ac120002 |
| Group Operating System Installation  | Install operating system on servers in a group      | compute-ops/group  | e2952628-2629-4088-93db-91742304ef0c |
| Collect Server log                   | Collect server log                                  | compute-ops/server | 2d744494-22d4-4d61-8c65-647ccadeb6b6 |

### Get a job by ID

 - [GET /compute-ops-mgmt/v1/jobs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1/get_v1_job_by_id.md): Retrieve details about the job referenced by its id

### Patch a job by ID

 - [PATCH /compute-ops-mgmt/v1/jobs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1/patch_v1_job_by_id.md): Updates an existing job

## jobs - v1beta3

### List all jobs (deprecated)

 - [GET /compute-ops-mgmt/v1beta3/jobs](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta3/get_v1beta3_jobs.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs

Retrieve the list of jobs

### Create a job (deprecated)

 - [POST /compute-ops-mgmt/v1beta3/jobs](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta3/create_v1beta3_job.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs

Create a job for a given resource. A job is a multi-step task performed by Compute Ops Manager.

This table summarizes the jobs and their template IDs. For more information about each job template, expand the Job
Definitions section and click on Overview to get started.

| Name                                 | Description                                         | Resource Type      | Template ID                          |
| ------------------------------------ | --------------------------------------------------  | ------------------ | ------------------------------------ |
| Server Power Off                     | Power off a server                                  | compute-ops/server | d0c13b58-748c-461f-9a61-c0c5c71f1bb4 |
| Server Power On                      | Power on a server                                   | compute-ops/server | 0cbb2377-1834-488d-840c-d5bf788c34fb |
| Server Restart                       | Restart a server                                    | compute-ops/server | 30110551-cad6-4069-95b8-dbce9bbd8525 |
| Server Cold Boot                     | Cold boot a server                                  | compute-ops/server | aacfb3e0-6575-4d4f-a711-1ee1ae768407 |
| Server Firmware Update               | Update firmware on a server                         | compute-ops/server | fd54a96c-cabc-42e3-aee3-374a2d009dba |
| Server iLO Firmware Update           | Update iLO component firmware on a server           | compute-ops/server | 94caa4ef-9ff8-4805-9e97-18a09e673b66 |
| Server External Storage Details      | Collect external storage details for a server       | compute-ops/server | 9310319e-7b7f-41ba-8b24-8b34eed1ca62 |
| Appliance Software Update            | Update OneView appliance                            | compute-ops/oneview-appliance | 1c4ac4be-8eeb-49f2-a86a-fd8c9182616c |
| Group Firmware Update                | Update firmware on servers in a group               | compute-ops/group  | 91159b5e-9eeb-11ec-a9da-00155dc0a0c0 |
| Group Firmware Compliance            | Calculate firmware compliance of servers in a group | compute-ops/group  | 23b8ba2a-6c46-4223-b028-919382c7dcac |
| Group Appliance Update               | Update OneView appliances in a group                | compute-ops/group  | f69f553a-5004-4a08-9283-5b60abd9eb4a |
| Group Apply Internal Storage Settings | Apply internal storage settings on servers in a group | compute-ops/group | 54095626-3911-4fea-9741-816e2531994e |
| Group Apply Server Setting           | Apply server setting on a group                     | compute-ops/group  | beff07ce-f36d-4699-9ac3-f872dcd63133 |
| Group Apply External Storage Settings | Apply external storage settings on servers in a group | compute-ops/group  | fcb79270-5954-42e9-9374-6a065b6d494a |
| Group External Storage Compliance    | Calculate external storage compliance of servers in a group | compute-ops/group | 7177aa6a-e8f8-4e9b-ae31-e01dafcc81df |
| Collect Server Inventory             | Collect complete or filtered server inventory       | compute-ops/server | d6595f1b-84e6-4587-ade5-656e2a5ea20d |
| Collect Server Network Connectivity  | Collect server adapter port to switch port mappings | compute-ops/server | b21ca9e2-8a1b-11ee-b9d1-0242ac120002 |
| Group Operating System Installation  | Install operating system on servers in a group      | compute-ops/group  | e2952628-2629-4088-93db-91742304ef0c |
| Group iLO Settings Compliance | Calculate ilo settings compliance of servers in a group | compute-ops/group | a55c8b26-3c57-4044-a4ee-1d0e3c108286 |

### Get a job by ID (deprecated)

 - [GET /compute-ops-mgmt/v1beta3/jobs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta3/get_v1beta3_job_by_id.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs/id

Retrieve details about the job referenced by its id

### Patch a job by ID (deprecated)

 - [PATCH /compute-ops-mgmt/v1beta3/jobs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta3/patch_v1beta3_job_by_id.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs/id

Updates an existing job

## jobs - v1beta2

### List all jobs (deprecated)

 - [GET /compute-ops-mgmt/v1beta2/jobs](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta2/get_v1beta2_jobs.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs

Retrieve the list of jobs

### Create a job (deprecated)

 - [POST /compute-ops-mgmt/v1beta2/jobs](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta2/create_v1beta2_job.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs

Create a job for a given resource. A job is a multi-step task performed by Compute Ops Manager.

This table summarizes the jobs and their template IDs. For more information about each job template, expand the Job
Definitions section and click on Overview to get started.

| Name                                 | Description                                         | Resource Type      | Template ID                          |
| ------------------------------------ | --------------------------------------------------  | ------------------ | ------------------------------------ |
| Server Power Off                     | Power off a server                                  | compute-ops/server | d0c13b58-748c-461f-9a61-c0c5c71f1bb4 |
| Server Power On                      | Power on a server                                   | compute-ops/server | 0cbb2377-1834-488d-840c-d5bf788c34fb |
| Server Restart                       | Restart a server                                    | compute-ops/server | 30110551-cad6-4069-95b8-dbce9bbd8525 |
| Server Cold Boot                     | Cold boot a server                                  | compute-ops/server | aacfb3e0-6575-4d4f-a711-1ee1ae768407 |
| Server Firmware Update               | Update firmware on a server                         | compute-ops/server | fd54a96c-cabc-42e3-aee3-374a2d009dba |
| Server iLO Firmware Update           | Update iLO component firmware on a server           | compute-ops/server | 94caa4ef-9ff8-4805-9e97-18a09e673b66 |
| Group Firmware Update                | Update firmware on servers in a group               | compute-ops/group  | 91159b5e-9eeb-11ec-a9da-00155dc0a0c0 |
| Group Firmware Compliance            | Calculate firmware compliance of servers in a group | compute-ops/group  | 23b8ba2a-6c46-4223-b028-919382c7dcac |
| Group Apply Internal Storage Settings | Apply internal storage settings on servers in a group | compute-ops/group | 54095626-3911-4fea-9741-816e2531994e |
| Group Apply Server Setting           | Apply server setting on a group                     | compute-ops/group  | beff07ce-f36d-4699-9ac3-f872dcd63133 |
| Collect Server Inventory             | Collect complete or filtered server inventory       | compute-ops/server | d6595f1b-84e6-4587-ade5-656e2a5ea20d |
| Collect Server Network Connectivity  | Collect server adapter port to switch port mappings | compute-ops/server | b21ca9e2-8a1b-11ee-b9d1-0242ac120002 |
| Group iLO Settings Compliance        | Calculate ilo settings compliance of servers in a group | compute-ops/group  | a55c8b26-3c57-4044-a4ee-1d0e3c108286 |

### Get a job by ID (deprecated)

 - [GET /compute-ops-mgmt/v1beta2/jobs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta2/get_v1beta2_job_by_id.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs/id

Retrieve details about the job referenced by its id

### Patch a job by ID (deprecated)

 - [PATCH /compute-ops-mgmt/v1beta2/jobs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta2/patch_v1beta2_job_by_id.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs/id

Updates an existing job

## metrics-configurations - v1

### List metrics data collection configuration

 - [GET /compute-ops-mgmt/v1/metrics-configurations](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/metrics-configurations-v1/get_v1_metrics_configurations.md): List metrics data collection configuration

### Create metrics data collection configuration

 - [POST /compute-ops-mgmt/v1/metrics-configurations](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/metrics-configurations-v1/create_v1_metrics_configurations.md): Create metrics data collection configuration

### Get metrics-configuration item by ID

 - [GET /compute-ops-mgmt/v1/metrics-configurations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/metrics-configurations-v1/get_v1_metrics_configuration_by_id.md): Get specific metrics-configuration item by metrics-configuration id.

### Delete a metrics-configuration item

 - [DELETE /compute-ops-mgmt/v1/metrics-configurations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/metrics-configurations-v1/delete_v1_metrics_configuration_by_id.md): Delete a metrics-configuration item.

### Patch a metrics-configuration item

 - [PATCH /compute-ops-mgmt/v1/metrics-configurations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/metrics-configurations-v1/patch_v1_metrics_configuration_by_id.md): Partially update a metrics-configuration item

## metrics-collection-requests - v1beta1

### Create a metrics collection request

 - [POST /compute-ops-mgmt/v1beta1/metrics-collection-requests](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/metrics-collection-requests-v1beta1/create_v1beta1_metrics_collection_request.md): Initiate a metrics collection request. On a successful request, this endpoint will return a 202 Accepted response
with a Location header that contains the resource URI of the async operation, which can then be used
to monitor the request's status.

## oneview-appliances - v1beta1

### List all OneView appliances

 - [GET /compute-ops-mgmt/v1beta1/oneview-appliances](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/oneview-appliances-v1beta1/get_v1beta1_oneview_appliances.md): Retrieve data for all OneView appliances.

Without a valid COM OneView Edition subscription, the response will not include the following fields:
  - activationKey
  - templateId
  - complianceId
  - complianceState
  - templateName
  - complianceLastChecked
  - lastDisconnect
  - health
  - associatedFirmwareUri
  - publicKey
  - publicKeyAlgo
  - applianceCert
  - applianceMode


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Add a OneView appliance

 - [POST /compute-ops-mgmt/v1beta1/oneview-appliances](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/oneview-appliances-v1beta1/add_v1beta1_oneview_appliances.md): Add a OneView appliance for management.

URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get a OneView appliance by id

 - [GET /compute-ops-mgmt/v1beta1/oneview-appliances/{device-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/oneview-appliances-v1beta1/get_v1beta1_oneview_appliances_by_id.md): Get a specific OneView appliance by id.

URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Delete a OneView appliance by id

 - [DELETE /compute-ops-mgmt/v1beta1/oneview-appliances/{device-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/oneview-appliances-v1beta1/delete_v1beta1_oneview_appliances_by_id.md): Delete a specific OneView appliance by id.

URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

## oneview-settings - v1beta1

### List all OneView appliance settings

 - [GET /compute-ops-mgmt/v1beta1/oneview-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/oneview-settings-v1beta1/get_v1beta1_oneview_appliance_settings.md): Retrieve data for all OneView appliance settings

## oneview-server-templates - v1beta1

### List all OneView server templates

 - [GET /compute-ops-mgmt/v1beta1/oneview-server-templates](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/oneview-server-templates-v1beta1/get_v1beta1_oneview_server_templates.md): Retrieve data for all OneView server templates

### Get a OneView server template by template id

 - [GET /compute-ops-mgmt/v1beta1/oneview-server-templates/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/oneview-server-templates-v1beta1/get_v1beta1_oneview_server_templates_by_templateid.md): Get a specific OneView server template by template id.

## reports - v1beta2

### List all reports

 - [GET /compute-ops-mgmt/v1beta2/reports](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/reports-v1beta2/get_reports_v1beta2.md): Retrieve a paginated collection of report metadata resources.  Currently, only the latest report of each
type is retained.

### Create report

 - [POST /compute-ops-mgmt/v1beta2/reports](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/reports-v1beta2/post_reports_v1beta2.md): Create a report for specified time interval.

### Get report metadata

 - [GET /compute-ops-mgmt/v1beta2/reports/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/reports-v1beta2/get_report_v1beta2.md): Retrieve a single report metadata resource by ID.

### Get report data

 - [GET /compute-ops-mgmt/v1beta2/reports/{id}/data](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/reports-v1beta2/get_report_data_v1beta2.md): Retrieve the data for a report

## schedules - v1beta2

### List all schedules

 - [GET /compute-ops-mgmt/v1beta2/schedules](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/schedules-v1beta2/get_v1beta2_schedules.md): Retrieve a paginated collection of schedule resources.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Create a schedule

 - [POST /compute-ops-mgmt/v1beta2/schedules](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/schedules-v1beta2/create_v1beta2_schedule.md): Create a new schedule resource. This endpoint requires permission to call the uri endpoint specified in the operation of the request.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get a schedule

 - [GET /compute-ops-mgmt/v1beta2/schedules/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/schedules-v1beta2/get_v1beta2_schedule.md): Retrieve a single schedule resource by ID.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Delete a schedule

 - [DELETE /compute-ops-mgmt/v1beta2/schedules/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/schedules-v1beta2/delete_v1beta2_schedule.md): Delete a schedule resource and its associated history.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Update a schedule

 - [PATCH /compute-ops-mgmt/v1beta2/schedules/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/schedules-v1beta2/patch_v1beta2_schedule.md): A update a schedule resource, using the RFC 7396 (JSON Merge Patch) format.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### List all history of a schedule

 - [GET /compute-ops-mgmt/v1beta2/schedules/{id}/history](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/schedules-v1beta2/get_v1beta2_schedule_history.md): Retrieve a paginated collection of history entries for a schedule resource.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get a history resource

 - [GET /compute-ops-mgmt/v1beta2/schedules/{id}/history/{history-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/schedules-v1beta2/get_v1beta2_schedule_history_entry.md): Retrieve a single history entry for a schedule resource.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

## server-locations - v1beta1

### Get location details

 - [GET /compute-ops-mgmt/v1beta1/server-locations/{location_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-locations-v1beta1/get_v1beta1_server_locations.md): Get location details with id of the servers associated with the location.
 The associted servers for the location includes both direct connect and OneView managed servers.

### Assign location to servers

 - [POST /compute-ops-mgmt/v1beta1/server-locations/{location_id}/servers](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-locations-v1beta1/post_v1beta1_server_locations.md): Assign a location for servers managed by HPE OneView. Use HPE GreenLake Locations API for managing location of servers which are managed directly by Compute Ops Management.

### Remove location of servers

 - [DELETE /compute-ops-mgmt/v1beta1/server-locations/{location_id}/servers](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-locations-v1beta1/delete_v1beta1_server_locations.md): Remove location of one or more servers managed by HPE OneView. Use HPE GreenLake Locations API for managing location of servers which are managed directly by Compute Ops Management.

## server-settings - v1beta1

### List all server settings

 - [GET /compute-ops/v1beta1/server-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-settings-v1beta1/get_v1beta1_server_settings.md): Get the list of a user's server-settings

### Create server settings

 - [POST /compute-ops/v1beta1/server-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-settings-v1beta1/create_server_settings.md): Create a server settings entry

### Get a server-settings item by ID

 - [GET /compute-ops/v1beta1/server-settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-settings-v1beta1/get_v1beta1_server_settings_by_id.md): Get a specific server-settings item by server-settings id.

### Delete a server-settings item

 - [DELETE /compute-ops/v1beta1/server-settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-settings-v1beta1/delete_v1beta1_server_settings_by_id.md): Delete a server-settings item.

### Patch a server-settings item

 - [PATCH /compute-ops/v1beta1/server-settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-settings-v1beta1/patch_v1beta1_server_settings_by_id.md): Partially update a server-settings item.

## settings - v1

### List all device settings

 - [GET /compute-ops-mgmt/v1/settings](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1/get_v1_settings.md): Get the list of a user's device settings

### Create a device setting

 - [POST /compute-ops-mgmt/v1/settings](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1/create_v1_settings.md): Create a device setting entry

### Get a device setting by ID

 - [GET /compute-ops-mgmt/v1/settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1/get_v1_settings_by_id.md): Get a specific device settings item by its id.

### Delete a device setting

 - [DELETE /compute-ops-mgmt/v1/settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1/delete_v1_settings_by_id.md): Delete a device settings item.

### Patch a device setting

 - [PATCH /compute-ops-mgmt/v1/settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1/patch_v1_settings_by_id.md): Partially update a device settings item.

## settings - v1beta1

### List all device settings

 - [GET /compute-ops-mgmt/v1beta1/settings](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1beta1/get_v1beta1_settings.md): Get the list of a user's device settings

### Create a device setting

 - [POST /compute-ops-mgmt/v1beta1/settings](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1beta1/create_settings.md): Create a device setting entry

### Get a device setting by ID

 - [GET /compute-ops-mgmt/v1beta1/settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1beta1/get_v1beta1_settings_by_id.md): Get a specific device settings item by its id.

### Delete a device setting

 - [DELETE /compute-ops-mgmt/v1beta1/settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1beta1/delete_v1beta1_settings_by_id.md): Delete a device settings item.

### Patch a device setting

 - [PATCH /compute-ops-mgmt/v1beta1/settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/settings-v1beta1/patch_v1beta1_settings_by_id.md): Partially update a device settings item.

## servers - v1

### List all servers

 - [GET /compute-ops-mgmt/v1/servers](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_servers.md): Retrieve data for all Servers

Servers without a valid subscription will not return the following:
  - hardware.health
  - hardware.memoryMb
  - hardware.formFactor
  - hardware.bmc
  - hardware.platform
  - hardware.powerState
  - hardware.indicatorLed
  - firmwareInventory
  - softwareInventory
  - lastFirmwareUpdate
  - host
  - firmwareBundleUri
  - tags
  - originIp
  - biosFamily
  - storageInventory
  - processorVendor
  - autoIloFwupdate
  - serverGeneration
  - connectionType
  - oneview

### Patch multiple servers

 - [PATCH /compute-ops-mgmt/v1/servers](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/patch_v1_servers_by_ids.md): Update multiple server(s) specified by the id(s). The operation is atomic (either fully successful or failing without modifying any servers).

### Create credential based server

 - [POST /compute-ops-mgmt/v1/servers](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/post_v1_server.md): Create a credential based server with the specified user defined properties.

### Get a server

 - [GET /compute-ops-mgmt/v1/servers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_server_by_id.md): Retrieve data for a Server specified by its id

Servers without a valid subscription will not return the following:
  - hardware.health
  - hardware.memoryMb
  - hardware.formFactor
  - hardware.bmc
  - hardware.platform
  - hardware.powerState
  - hardware.indicatorLed
  - firmwareInventory
  - softwareInventory
  - lastFirmwareUpdate
  - host
  - firmwareBundleUri
  - tags
  - originIp
  - biosFamily
  - storageInventory
  - processorVendor
  - autoIloFwupdate
  - serverGeneration
  - connectionType
  - oneview

### Patch a server

 - [PATCH /compute-ops-mgmt/v1/servers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/patch_v1_server_by_id.md): Partially update a Server specified by its id

Servers without a valid subscription will not return the following:
  - hardware.health
  - hardware.memoryMb
  - hardware.formFactor
  - hardware.bmc
  - hardware.platform
  - hardware.powerState
  - hardware.indicatorLed
  - firmwareInventory
  - softwareInventory
  - lastFirmwareUpdate
  - host
  - firmwareBundleUri
  - tags
  - originIp
  - biosFamily
  - storageInventory
  - processorVendor
  - autoIloFwupdate
  - serverGeneration
  - connectionType
  - oneview

### Delete a credential based server

 - [DELETE /compute-ops-mgmt/v1/servers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/delete_v1_server_by_id.md): Delete a credential based server.

### List all alerts for a server

 - [GET /compute-ops-mgmt/v1/servers/{id}/alerts](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_server_alerts.md): Retrieve alert data for a Server specified by the id of the server

### Clear power utilization alerts for a server

 - [POST /compute-ops-mgmt/v1/servers/{id}/clear-alert](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/clear_v1_software_alerts.md): Clear power utilization alerts for a server

### Analyze server configuration for operating system installation

 - [POST /compute-ops-mgmt/v1/servers/{id}/analyze-os-install](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/post_v1_analyze_os_install.md): Validate the presence of storage volume for the server specified by the id for operating system installation. The request body is empty.

### Get external storage details

 - [GET /compute-ops-mgmt/v1/servers/{id}/external-storage-details](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_server_external_storage_details.md): Retrieves external storage hosts and volume details for a server specified by the server id.  The Server External Storage Details job must be run successfully before this endpoint will be accessible.

### List inventories for a server

 - [GET /compute-ops-mgmt/v1/servers/{id}/inventory](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_server_inventory.md): Retrieve firmware, software, storage inventories, PCI devices and smart update tool settings for a server specified by the id of the server

### List subset of a Server Inventory

 - [POST /compute-ops-mgmt/v1/servers/{id}/inventory](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/post_v1_subset_server_inventory.md): Lists the subset of the server hardware inventory. The request body can either specify a subset of attributes, or can be empty, and a subset of attributes or the full inventory response is returned.

### Get the event and health notification status for a server

 - [GET /compute-ops-mgmt/v1/servers/{id}/notifications](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_server_notifications.md): ### Purpose
Retrieves the current values of the event and health notification options.
* For criticalNotification a notification will be sent if the value is true, and no notification will be sent if the value is false.
* For disconnectNotification a notification will be sent after the specified number of hours if the server becomes disconnected or not monitored. No notification will be sent if the value is null.
* For the following properties a notification will be sent if the value is true. No notification will be sent if the value is null or false.
  * criticalNonServiceNotification
  * warningNotification
  * healthNotification
  * powerResetNotification

### Update event and health notifications for yourself

 - [PUT /compute-ops-mgmt/v1/servers/{id}/notifications](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/update_v1_server_notifications.md): ### Purpose
Configure your notification settings for the provided server.

For criticalNotification, criticalNonServiceNotification, and warningNotification, 
each selection increases the scope of the set of events that will be included.
The order of event selections from minimum to maximum scope are:

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| criticalNotification  | criticalNonServiceNotification  | warningNotification  |
|:---------------------:|:-------------------------------:|:--------------------:|
| False                 | False                           | False                |
| True                  | False                           | False                |
| True                  | True                            | False                |
| True                  | True                            | True                 |

healthNotification, powerResetNotification, and disconnectNotification do not build on each other
and may be configured independently.

  * healthNotification enables the daily summary health report for the server.
  * powerResetNotification enables notifications for out-of-band power operations.
  * disconnectNotification enables notifications to be sent when the server remains in the disconnected
  or not monitored state after the configured number of hours. A null value in this field
  disables disconnect and not monitored notifications.

### Initial values
All values are initially 'off' (false or null) with the result being that no notifications will be sent.

### Update event and health notifications for others

 - [POST /compute-ops-mgmt/v1/servers/{id}/notifications](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/update_v1_server_notifications_on_behalf.md): ### Purpose
Configure the notification settings for the provided server on behalf of other users in your workspace.
The recipients field expects a list of emails; the users provided in this list will be configured based
on the settings passed in the data field.

For criticalNotification, criticalNonServiceNotification, and warningNotification, 
each selection increases the scope of the set of events that will be included.
The order of event selections from minimum to maximum scope are:

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| criticalNotification  | criticalNonServiceNotification  | warningNotification  |
|:---------------------:|:-------------------------------:|:--------------------:|
| False                 | False                           | False                |
| True                  | False                           | False                |
| True                  | True                            | False                |
| True                  | True                            | True                 |

healthNotification, powerResetNotification, and disconnectNotification do not build on each other
and may be configured independently.

  * healthNotification enables the daily summary health report for the server.
  * powerResetNotification enables notifications for out-of-band power operations.
  * disconnectNotification enables notifications to be sent when the server remains in the disconnected
  or not monitored state after the configured number of hours. A null value in this field
  disables disconnect and not monitored notifications.

### Initial values
All values are initially 'off' (false or null) with the result being that no notifications will be sent.

### Get security parameters for a server

 - [GET /compute-ops-mgmt/v1/servers/{id}/security-parameters](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_server_security_parameters.md): Retrieve a list of security parameters for a server specified by the id of the server

### List of adapter to switch port mappings for a server

 - [GET /compute-ops-mgmt/v1/servers/{id}/tor-port-mappings](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_server_network_connectivity.md): Retrieve network connectivity of adapter port to connected switch port for a server specified by the id of the server

### Download Server Logs in zip format

 - [GET /compute-ops-mgmt/v1/servers/{id}/download-logs](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/download_v1_server_logs.md): This API returns a pre-signed URL to download server logs in zip format

### List raw inventories for a server (deprecated)

 - [GET /compute-ops-mgmt/v1/servers/{id}/raw-inventory](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1/get_v1_server_raw_inventory.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 7 Nov 2024 23:59:59 GMT
- Sunset at: Fri, 30 May 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/servers/{id}/inventory

Retrieve firmware, software, storage inventories, PCI devices and smart update tool settings for a server specified by the id of the server.

## servers - v1beta2

### List all servers

 - [GET /compute-ops-mgmt/v1beta2/servers](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_servers.md): Retrieve data for all Servers

Servers without a valid subscription will not return the following:
  - hardware.health
  - hardware.memoryMb
  - hardware.formFactor
  - hardware.bmc
  - hardware.platform
  - hardware.powerState
  - hardware.indicatorLed
  - firmwareInventory
  - softwareInventory
  - lastFirmwareUpdate
  - host
  - firmwareBundleUri
  - tags
  - originIp
  - biosFamily
  - storageInventory
  - processorVendor
  - autoIloFwupdate
  - serverGeneration
  - connectionType
  - oneview


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Patch multiple servers

 - [PATCH /compute-ops-mgmt/v1beta2/servers](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/patch_v1beta2_servers_by_ids.md): Update multiple server(s) specified by the id(s). The operation is atomic (either fully successful or failing without modifying any servers).


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Create credential based server

 - [POST /compute-ops-mgmt/v1beta2/servers](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/post_v1beta2_server.md): Create a credential based server with the specified user defined properties.

### Get a server

 - [GET /compute-ops-mgmt/v1beta2/servers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_server_by_id.md): Retrieve data for a Server specified by its id

Servers without a valid subscription will not return the following:
  - hardware.health
  - hardware.memoryMb
  - hardware.formFactor
  - hardware.bmc
  - hardware.platform
  - hardware.powerState
  - hardware.indicatorLed
  - firmwareInventory
  - softwareInventory
  - lastFirmwareUpdate
  - host
  - firmwareBundleUri
  - tags
  - originIp
  - biosFamily
  - storageInventory
  - processorVendor
  - autoIloFwupdate
  - serverGeneration
  - connectionType
  - oneview


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Patch a server

 - [PATCH /compute-ops-mgmt/v1beta2/servers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/patch_v1beta2_server_by_id.md): Partially update a Server specified by its id

Servers without a valid subscription will not return the following:
  - hardware.health
  - hardware.memoryMb
  - hardware.formFactor
  - hardware.bmc
  - hardware.platform
  - hardware.powerState
  - hardware.indicatorLed
  - firmwareInventory
  - softwareInventory
  - lastFirmwareUpdate
  - host
  - firmwareBundleUri
  - tags
  - originIp
  - biosFamily
  - storageInventory
  - processorVendor
  - autoIloFwupdate
  - serverGeneration
  - connectionType
  - oneview


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Delete a credential based server

 - [DELETE /compute-ops-mgmt/v1beta2/servers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/delete_v1beta2_server_by_id.md): Delete a credential based server.

### List all alerts for a server

 - [GET /compute-ops-mgmt/v1beta2/servers/{id}/alerts](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_server_alerts.md): Retrieve alert data for a Server specified by the id of the server


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Clear power utilization alerts for a server

 - [POST /compute-ops-mgmt/v1beta2/servers/{id}/clear-alert](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/clear_v1beta2_software_alerts.md): Clear power utilization alerts for a server

### Analyze server configuration for operating system installation

 - [POST /compute-ops-mgmt/v1beta2/servers/{id}/analyze-os-install](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/post_v1beta2_analyze_os_install.md): Validate the presence of storage volume for the server specified by the id for operating system installation. The request body is empty.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get external storage details

 - [GET /compute-ops-mgmt/v1beta2/servers/{id}/external-storage-details](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_server_external_storage_details.md): Retrieves external storage hosts and volume details for a server specified by the server id


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### List inventories for a server

 - [GET /compute-ops-mgmt/v1beta2/servers/{id}/inventory](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_server_inventory.md): Retrieve firmware, software, storage inventories, PCI devices and smart update tool settings for a server specified by the id of the server


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### List subset of a Server Inventory

 - [POST /compute-ops-mgmt/v1beta2/servers/{id}/inventory](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/post_v1beta2_subset_server_inventory.md): Lists the subset of the server hardware inventory. The request body can either specify a subset of attributes, or can be empty, and a subset of attributes or the full inventory response is returned.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get the event and health notification status for a server

 - [GET /compute-ops-mgmt/v1beta2/servers/{id}/notifications](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_server_notifications.md): ### Purpose
Retrieves the current values of the event and health notification options.
* For criticalNotification a notification will be sent if the value is true, and no notification will be sent if the value is false.
* For the following properties a notification will be sent if the value is true. No notification will be sent if the value is null or false.
  * criticalNonServiceNotification
  * warningNotification
  * healthNotification


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Update event and health notifications for a server

 - [PUT /compute-ops-mgmt/v1beta2/servers/{id}/notifications](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/update_v1beta2_server_notifications.md): ### Purpose
When a server is added to Compute Ops Management, these attributes will be used to set the
initial email notification subscription choices for event and daily health email notifications.

Event notification selections are made such that each selection increases the scope
of the set of events that will be included.
The order of event selections from minimum to maximum scope are

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

Note that healthNotification is not part of the event notification set and
may be set independently.

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| criticalNotification  | criticalNonServiceNotification  | warningNotification  |
|:---------------------:|:-------------------------------:|:--------------------:|
| False                 | False                           | False                |
| True                  | False                           | False                |
| True                  | True                            | False                |
| True                  | True                            | True                 |

### Initial values
All values are initially false with the result being that no notifications will be sent.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get security parameters for a server

 - [GET /compute-ops-mgmt/v1beta2/servers/{id}/security-parameters](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_server_security_parameters.md): Retrieve a list of security parameters for a server specified by the id of the server


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### List of adapter to switch port mappings for a server

 - [GET /compute-ops-mgmt/v1beta2/servers/{id}/tor-port-mappings](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_server_network_connectivity.md): Retrieve network connectivity of adapter port to connected switch port for a server specified by the id of the server


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### List raw inventories for a server (deprecated)

 - [GET /compute-ops-mgmt/v1beta2/servers/{id}/raw-inventory](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_server_raw_inventory.md): Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 7 Nov 2024 23:59:59 GMT
- Sunset at: Fri, 30 May 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/servers/{id}/inventory

Retrieve firmware, software, storage inventories, PCI devices and smart update tool settings for a server specified by the id of the server.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

## server-warranty - v1beta2

### Lists the warranty information for all servers.

 - [GET /compute-ops-mgmt/v1beta2/server-warranty](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-warranty-v1beta2/get_v1beta2_server_warranty.md): Retrieve warranty data for all servers.

### List server warranty information for a given UUID

 - [GET /compute-ops-mgmt/v1beta2/server-warranty/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/server-warranty-v1beta2/get_v1beta2_server_warranty_by_id.md): Retrieve server warranty data for the specified UUID.

## user-preferences - v1

### Get user preferences for the current user

 - [GET /compute-ops-mgmt/v1/user-preferences](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1/get_v1_user_preferences.md): Retrieves the user preferences for the current user.  The returned list will contain only one element if preferences have been set, zero otherwise.

### Create user preferences for the current user

 - [POST /compute-ops-mgmt/v1/user-preferences](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1/post_v1_user_preferences.md): ### Purpose
When a server is added to Compute Ops Management, these attributes will be used to set the
initial email notification subscription choices for event and daily health email notifications.

For criticalNotification, criticalNonServiceNotification, and warningNotification, 
each selection increases the scope of the set of events that will be included.
The order of event selections from minimum to maximum scope are:

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| criticalNotification  | criticalNonServiceNotification  | warningNotification  |
|:---------------------:|:-------------------------------:|:--------------------:|
| False                 | False                           | False                |
| True                  | False                           | False                |
| True                  | True                            | False                |
| True                  | True                            | True                 |

healthNotification, powerResetNotification, and disconnectNotification do not build on each other
and may be configured independently.

  * healthNotification enables the daily summary health report for the server.
  * powerResetNotification enables notifications for out-of-band power operations.
  * disconnectNotification enables notifications to be sent when the server remains in the disconnected
  or not monitored state after the configured number of hours. A null value in this field
  disables disconnect and not monitored notifications.

### Initial values
All values are initially 'off' (false or null) with the result being that no notifications will be sent.

### Get a specific user preference object

 - [GET /compute-ops-mgmt/v1/user-preferences/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1/get_v1_user_preference_by_id.md): Retrieve a user preference object specified by its id

### Update user preferences

 - [PUT /compute-ops-mgmt/v1/user-preferences/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1/put_v1_user_preferences.md): ### Purpose
When a server is added to Compute Ops Management, these attributes will be used to set the
initial email notification subscription choices for event and daily health email notifications.

For criticalNotification, criticalNonServiceNotification, and warningNotification, 
each selection increases the scope of the set of events that will be included.
The order of event selections from minimum to maximum scope are:

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| criticalNotification  | criticalNonServiceNotification  | warningNotification  |
|:---------------------:|:-------------------------------:|:--------------------:|
| False                 | False                           | False                |
| True                  | False                           | False                |
| True                  | True                            | False                |
| True                  | True                            | True                 |

healthNotification, powerResetNotification, and disconnectNotification do not build on each other
and may be configured independently.

  * healthNotification enables the daily summary health report for the server.
  * powerResetNotification enables notifications for out-of-band power operations.
  * disconnectNotification enables notifications to be sent when the server remains in the disconnected
  or not monitored state after the configured number of hours. A null value in this field
  disables disconnect and not monitored notifications.

### Initial values
All values are initially 'off' (false or null) with the result being that no notifications will be sent.

### Subscribe users

 - [POST /compute-ops-mgmt/v1/user-preferences/subscribe](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1/post_v1_user_preferences_subscribe.md): ### Purpose
This endpoint allows you to set the user preferences for other users in your workspace.
This endpoint only allows subscribing, meaning configuration will only be applied for properties
set to true or a valid integer in the case of disconnectNotification.

The user preference attributes to configure should be included in requestData.
The lists in the recipients object will be used to subscribe each individual user.
For example, if healthNotification is set to true and example@email.com is included in either the all
list or the health list, the user example@email.com will end up with healthNotification set to true. If
healthNotification is set to false, or example@email.com is not included in all or health, then healthNotification
will be unaffected for example@email.com.

### Request Data
For criticalNotification, criticalNonServiceNotification, and warningNotification, 
each selection increases the scope of the set of events that will be included.
The order of event selections from minimum to maximum scope are:

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| criticalNotification  | criticalNonServiceNotification  | warningNotification  |
|:---------------------:|:-------------------------------:|:--------------------:|
| False                 | False                           | False                |
| True                  | False                           | False                |
| True                  | True                            | False                |
| True                  | True                            | True                 |

healthNotification, powerResetNotification, and disconnectNotification do not build on each other
and may be configured independently.

  * healthNotification enables the daily summary health report for the server.
  * powerResetNotification enables notifications for out-of-band power operations.
  * disconnectNotification enables notifications to be sent when the server remains in the disconnected
  or not monitored state after the configured number of hours.

### Unsubscribe users

 - [POST /compute-ops-mgmt/v1/user-preferences/unsubscribe](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1/post_v1_user_preferences_unsubscribe.md): ### Purpose
This endpoint allows you to unset the user preferences for other users in your workspace.
Users will be unsubscribed based on the lists in the request body.

For example, a user included in the critical list will have their preferences for 
criticalNotification, criticalNonServiceNotification, and warningNotification set to false.

## user-preferences - v1beta1

### Get user preferences for the current user

 - [GET /compute-ops-mgmt/v1beta1/user-preferences](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1beta1/get_v1beta1_user_preferences.md): Retrieves the user preferences for the current user.  The returned list will contain only one element if preferences have been set, zero otherwise.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Create user preferences for the current user

 - [POST /compute-ops-mgmt/v1beta1/user-preferences](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1beta1/post_v1beta1_user_preferences.md): ### Purpose
When a server is added to Compute Ops Management, these attributes will be used to set the
initial email notification subscription choices for event and daily health email notifications.

Event notification selections are made such that each selection increases the scope
of the set of events that will be included.
The order of event selections from minimum to maximum scope are

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

Note that healthNotification is not part of the event notification set and
may be set independently.

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| criticalNotification  | criticalNonServiceNotification  | warningNotification  |
|:---------------------:|:-------------------------------:|:--------------------:|
| False                 | False                           | False                |
| True                  | False                           | False                |
| True                  | True                            | False                |
| True                  | True                            | True                 |

### Initial values
All values are initially false with the result being that no notifications will be sent.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Get a specific user preference object

 - [GET /compute-ops-mgmt/v1beta1/user-preferences/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1beta1/get_v1beta1_user_preference_by_id.md): Retrieve a user preference object specified by its id


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

### Update user preferences

 - [PUT /compute-ops-mgmt/v1beta1/user-preferences/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1beta1/put_v1beta1_user_preferences.md): ### Purpose
When a server is added to Compute Ops Management, these attributes will be used to set the
initial email notification subscription choices for event and daily health email notifications.

Event notification selections are made such that each selection increases the scope
of the set of events that will be included.
The order of event selections from minimum to maximum scope are

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

Note that healthNotification is not part of the event notification set and
may be set independently.

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| criticalNotification  | criticalNonServiceNotification  | warningNotification  |
|:---------------------:|:-------------------------------:|:--------------------:|
| False                 | False                           | False                |
| True                  | False                           | False                |
| True                  | True                            | False                |
| True                  | True                            | True                 |

### Initial values
All values are initially false with the result being that no notifications will be sent.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

## utilization-over-time - v1beta1

### Retrieve utilization data over time

 - [GET /compute-ops-mgmt/v1beta1/utilization-over-time](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/utilization-over-time-v1beta1/get_utilization_over_time.md): Retrieve CPU, memory bus, I/O bus or CPU interconnect utilization data over a time interval.

## utilization-by-entity - v1beta1

### Retrieve utilization data by entity

 - [GET /compute-ops-mgmt/v1beta1/utilization-by-entity](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/utilization-by-entity-v1beta1/get_utilization_by_entity.md): Retrieve CPU, memory bus, I/O bus or CPU interconnect utilization data per entity.

## webhooks - v1beta1

### Retrieve all webhooks

 - [GET /compute-ops-mgmt/v1beta1/webhooks](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/webhooks-v1beta1/get_v1beta1_webhooks.md): Purpose Retrieve all available webhooks as a list.  More Information For more information about this feature and how to use this API, go to the Event Webhook page to view a getting started guide.

### Create a webhook

 - [POST /compute-ops-mgmt/v1beta1/webhooks](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/webhooks-v1beta1/post_v1beta1_webhooks.md): Creates a webhook.

### Get a webhook

 - [GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/webhooks-v1beta1/get_v1beta1_webhooks_by_id.md): Retrieve a single webhook by webhook ID.

### Patch a webhook

 - [PATCH /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/webhooks-v1beta1/patch_v1beta1_webhook_by_id.md): Update a saved webhook.

### Delete a saved webhook

 - [DELETE /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/webhooks-v1beta1/delete_webhook.md): Deletes a saved webhook resource. This will also delete any deliveries associated with the deleted webhook.

### Get details on all webhook deliveries.

 - [GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}/deliveries](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/webhooks-v1beta1/get_v1beta1_webhooks_deliveries.md): Retrieve details of the most recent deliveries that were attempted. Compute Ops Management stores the most recent ten deliveries and the five most recent failures, so this endpoint will return between 10 and 15 deliveries once deliveries have been attempted.

### Get details for a specific delivery

 - [GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}/deliveries/{delivery_id}](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/webhooks-v1beta1/get_v1beta1_webhooks_delivery_by_id.md): Retrieve details for a specific delivery using the ID.

