---
title: "GET /compute-ops-mgmt/v1beta1/activation-keys"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/activation-keys-v1beta1/get_activation-keys_v1_beta1.md"
scraped_at: "2026-06-07T06:14:39.811202+00:00Z"
---

# Retrieve all activation keys to onboard a device or appliance

Retrieve a paginated collection of activation keys for onboarding iLO for direct management or secure gateway management, or secure gateway appliances.

Endpoint: GET /compute-ops-mgmt/v1beta1/activation-keys
Version: latest
Security: Bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Server IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

Activation-Keys can be filtered by:
- targetDevice
- activationKey
- applianceUri
- subscriptionKey

The following examples are not an exhaustive list of all possible filtering options.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `items` (array, required)
    Array of resources in the page of the collection.

  - `items.id` (string)
    Primary identifier of the activation key resource given by the system.
    Example: "5fae6c47-13f4-42f3-97b5-540f3d085791"

  - `items.type` (string)
    Type of the resource

  - `items.targetDevice` (string)
    Target device to be onboarded
    Enum: "ILO", "SECURE_GATEWAY"

  - `items.expiresAt` (string)
    Time of activation key expiration.
    Example: "2024-07-25T12:21:05.448576Z"

  - `items.activationKey` (string)
    Activation key generated to onboard the target device.

  - `items.subscriptionKey` (string)
    Device subscription that is associated with this activation key.

  - `items.applianceUri` (string)
    Appliance URI of the onboarded appliance.

  - `items.applianceName` (string)
    Name of the appliance.

  - `items.createdAt` (string)
    Time of activation key creation.
    Example: "2024-07-25T10:21:05.475123Z"

  - `items.updatedAt` (string)
    Time of activation key updation.
    Example: "2024-07-25T10:21:05.475123Z"

  - `items.generation` (number)
    Monotonically increasing update counter.
    Example: 1

  - `items.details` (object)
    Details of location, tags, sdc and appliance

  - `items.details.locationId` (string)
    Unique identifier for the location.

  - `items.details.serviceDeliveryContact` (string)
    Service delivery contact email address.

  - `items.details.tags` (array)
    Tag related information.

  - `items.details.tags.name` (string)
    Name of the tag.

  - `items.details.tags.value` (string)
    Value of the tag.

  - `offset` (integer, required)
    Zero-based resource offset

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

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


