---
title: "POST /compute-ops-mgmt/v1beta1/external-services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/external-services-v1beta1/create_external_services.md"
scraped_at: "2026-06-07T06:15:00.680911+00:00Z"
---

# Create external services

Create configuration for external service


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

Endpoint: POST /compute-ops-mgmt/v1beta1/external-services
Version: latest
Security: Bearer

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/json' in order for the request to be performed.

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Request fields (application/json):

  - `name` (string, required)
    Name given to resource

  - `serviceType` (string, required)
    Used for specifying the type of external service.
| Value           | Description                               |
|-----------------|-------------------------------------------|
| SERVICE_NOW     | ServiceNow integration                    |
| DSCC            | Data Services Cloud Console integration   |
| VMWARE_VCENTER  | VMware vCenter integration                |
    Enum: "SERVICE_NOW", "DSCC", "VMWARE_VCENTER"

  - `authenticationType` (string, required)
    Used to specify which authentication method is used for authenticating the external service.
| Value | Description                                                 |
|-------|-------------------------------------------------------------|
| OAUTH | OAuth authentication (for SERVICE_NOW, DSCC)                |
| BASIC | Basic authentication with username/password (for VMWARE_VCENTER) |
    Enum: "OAUTH", "BASIC"

  - `description` (string,null, required)
    An optional longer description of the external service
    Example: "Service now configuration"

  - `authentication` (any, required)
    Authentication credentials based on authenticationType

  - `serviceData` (any, required)
    Service data corresponding to the specified serviceType

  - `state` (string)
    State of the external service
    Enum: "ENABLED", "DISABLED"

## Response 201 fields (application/json):

  - `name` (string)
    Name given to resource

  - `serviceType` (string)
    Used for specifying the type of external service.
| Value           | Description                               |
|-----------------|-------------------------------------------|
| SERVICE_NOW     | ServiceNow integration                    |
| DSCC            | Data Services Cloud Console integration   |
| VMWARE_VCENTER  | VMware vCenter integration                |
    Enum: "SERVICE_NOW", "DSCC", "VMWARE_VCENTER"

  - `authenticationType` (string)
    Used to specify which authentication method is used for authenticating the external service.
| Value | Description                                                 |
|-------|-------------------------------------------------------------|
| OAUTH | OAuth authentication (for SERVICE_NOW, DSCC)                |
| BASIC | Basic authentication with username/password (for VMWARE_VCENTER) |
    Enum: "OAUTH", "BASIC"

  - `description` (string,null)
    An optional longer description of the external service
    Example: "Service now configuration"

  - `authentication` (any)
    Authentication credentials based on authenticationType

  - `serviceData` (object)
    Service data corresponding to the specified serviceType

  - `status` (string)
    Status of the external service
    Enum: "ENABLED", "SUSPENDED"

  - `state` (string)
    State of the external service
    Enum: "ENABLED", "DISABLED"

  - `id` (string)
    Primary identifier for the external services resource given by the system.
    Example: "b870f080-6448-48c5-b23a-d04f2d489174"

  - `type` (string)
    Type of the resource

  - `resourceUri` (string)
    URI to the external-services itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta1/external-services/ff5798d5-b029-4452-b958-b33eabbe44d2"

  - `generation` (integer)
    Monotonically increasing update counter

  - `createdAt` (string)
    Time of external-services configuration creation

  - `updatedAt` (string)
    Time of the external-services configuration update

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 406 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 415 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error


