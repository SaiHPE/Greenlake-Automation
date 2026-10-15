---
title: "POST /compute-ops-mgmt/v1beta1/activation-keys"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/activation-keys-v1beta1/create_activation-keys_v1_beta1.md"
scraped_at: "2026-06-07T06:14:57.498129+00:00Z"
---

# Generate an activation key to onboard a device or appliance

Note: This API only works with iLO 6 1.62 and later or with iLO 5 3.09 and later
Generates a new activation key for onboarding iLO for direct management or secure gateway management, or secure gateway appliances

Endpoint: POST /compute-ops-mgmt/v1beta1/activation-keys
Version: latest
Security: Bearer

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/json' in order for the request to be performed.

## Request fields (application/json):

  - `targetDevice` (string, required)
    Target device to be onboarded using the activation key. The following target device types are supported: iLO and secure gateway appliances.
    Enum: "ILO", "SECURE_GATEWAY"

  - `expirationInHours` (number)
    Expiration duration of the generated activation key. Default is set as 72 hours.

  - `applianceUri` (string)
    The secure gateway appliance URI is required for onboarding a server for management through a secure gateway.

  - `subscriptionKey` (string)
    Specifies the device subscription to be associated with the generated activation key. The subscription must have at least one available seat. Once the activation key is generated, the subscription will be automatically added to the HPE GreenLake workspace and linked to all servers onboarded using that key, regardless of the auto-subscribe configuration.

  - `locationId` (string)
    Specifies the location to be associated with the generated activation key. The locationId should exist in the HPE GreenLake workspace.

  - `serviceDeliveryContact` (string)
    Specifies the service delivery contact to be associated with the generated activation key.

  - `tags` (array)
    Specifies the tags to be associated with the generated activation key. Any tags not already present in the HPE GreenLake workspace will be created. If a tag matches an existing server group, the server will be added to that group after onboarding.

  - `tags.name` (string)
    Name of the tag to be associated with the generated activation key.

  - `tags.value` (string)
    Value of the tag to be associated with the generated activation key.

## Response 201 fields (application/json):

  - `id` (string)
    Primary identifier of the activation key resource given by the system.
    Example: "5fae6c47-13f4-42f3-97b5-540f3d085791"

  - `type` (string)
    Type of the resource

  - `targetDevice` (string)
    Target device to be onboarded
    Enum: "ILO", "SECURE_GATEWAY"

  - `expiresAt` (string)
    Time of activation key expiration.
    Example: "2024-07-25T12:21:05.448576Z"

  - `activationKey` (string)
    Activation key generated to onboard the target device.

  - `subscriptionKey` (string)
    Device subscription that is associated with this activation key.

  - `applianceUri` (string)
    Appliance URI of the onboarded appliance.

  - `applianceName` (string)
    Name of the appliance.

  - `createdAt` (string)
    Time of activation key creation.
    Example: "2024-07-25T10:21:05.475123Z"

  - `updatedAt` (string)
    Time of activation key updation.
    Example: "2024-07-25T10:21:05.475123Z"

  - `generation` (number)
    Monotonically increasing update counter.
    Example: 1

  - `details` (object)
    Details of location, tags, sdc and appliance

  - `details.locationId` (string)
    Unique identifier for the location.

  - `details.serviceDeliveryContact` (string)
    Service delivery contact email address.

  - `details.tags` (array)
    Tag related information.

  - `details.tags.name` (string)
    Name of the tag.

  - `details.tags.value` (string)
    Value of the tag.

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

## Response 404 fields (application/json):

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


