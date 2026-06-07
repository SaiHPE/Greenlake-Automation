---
title: "PATCH /devices/v2beta1/devices"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v2beta1/patchdevicesv2beta1.md"
scraped_at: "2026-06-07T06:15:17.980595+00:00Z"
---

# Update devices

Update devices by passing one or more device IDs.  The API supports Device operations such as:
Assigning and unassigning devices to and from a service. Adding, updating and removing tags to devices. Archiving and un-archiving the devices.   The API endpoint supports subscription operations of applying and removing subscriptions to and from devices.
To remove an application, set the id under application to null and region to null. Set an empty array to the attribute subscription to remove a subscription. For each tag provided in the request body: Tags are created and inserted into the specified devices if the provided tags do not map to null and are not already present. Tags are updated with the provided if the provided tag key is already present in a device, but the provided value differs from the existing value. Tags are removed from devices when a tag key is mapped to a null tag value. The tags are removed from any devices with a matching tag with the same key. The endpoint only supports either a device or a subscription operation per API call. For example, you cannot assign devices to an application and assign subscriptions to devices in a single API call. You can achieve this with two separate API calls. However, a single API call can perform device operations together; for example, assigning an application and adding tags can be performed. The archive device operation is incompatible with any other device operation in the same API call. For example, you cannot remove an application and archive a device using the same API call. This is an asynchronous API endpoint and it returns the 202 Accepted response code and a Location header containing the URI of the asynchronous operation that can be used to track progress. For details about the status fetch URL, refer to the API Get progress or status of async operations in devices. NOTE: You need edit permissions for the Devices and Subscription service to initiate this API call. Rate limits are enforced, and 20 requests per minute are supported per workspace. The API returns 429 if this threshold is breached.

Endpoint: PATCH /devices/v2beta1/devices
Version: latest
Security: Bearer

## Query parameters:

  - `id` (array, required)
    Array of device resource IDs. Maximum twenty five devices per request.
    Example: "05fc0c47-e517-5709-976e-c0b726977477&id=08a42d07-b144-5602-9a82-7927d6e44616"

  - `dry-run` (boolean)
    The dry-run query parameter is used to perform the resource update operation (POST, PUT, PATCH, DELETE) and return a response as if the operation had completed, but without actually creating, updating, or deleting the resource. This allows you to test if the request would succeed before making the change. If set to true, the request is validated but not executed.

## Request fields (application/merge-patch+json):

  - `subscription` (array)

  - `subscription.id` (string, required)
    The unique identifier of the subscription.

  - `application` (object)

  - `application.id` (string, required)
    The unique identifier of the application.

  - `region` (string)
    The region of the application the device is provisioned in.

  - `tenantWorkspaceId` (string)
    The platform customer ID of the tenant.

  - `archived` (boolean)

  - `tags` (object)
    Provide a map of tags to create or delete for the given DeviceID (or multiple DeviceID's). Tags are saved with the character casing preserved (uppercase, lowercase, mixed, and so on). For example, adding a new tag with the key Location will fail if the Device already has a tag with the key LOCATION as they are considered the same key. Tag keys and tag values can comprise letters, numbers, spaces (represented in UTF-8), and only the characters: _, ., :, =, +, -, and  @. NOTE: Do not store sensitive data, such as personally identifiable information, in tags.

  - `location` (object)
    The location of the device.

  - `location.id` (string, required)
    The unique identifier of the location.
    Example: "4b2da819-be18-4793-befb-ab42866eadec"

  - `contact` (object)
    The contact information for the device.

  - `contact.type` (string, required)
    Enum: "WORKSPACE-USER", "NON-WORKSPACE-USER"

  - `contact.workspaceUser` (object)
    Details for workspace users, that is, users already added to the workspace.

  - `contact.workspaceUser.id` (string)
    The unique identifier of the workspace user.

  - `contact.nonWorkspaceUser` (object)
    Details for non-workspace users.

  - `contact.nonWorkspaceUser.email` (string, required)
    The email address of the non-workspace user.

  - `contact.nonWorkspaceUser.firstName` (string)
    The first name of the non-workspace user.

  - `contact.nonWorkspaceUser.lastName` (string)
    The last name of the non-workspace user.

  - `contact.nonWorkspaceUser.phoneNumber` (string)
    The phone number of the non-workspace user.

## Response 202 fields (application/json):

  - `code` (integer, required)
    Three digit HTTP status code.

  - `status` (string, required)
    Three digit HTTPS status code and message.
    Enum: "100 CONTINUE", "101 SWITCHING_PROTOCOLS", "102 PROCESSING", "103 CHECKPOINT", "200 OK", "201 CREATED", "202 ACCEPTED", "203 NON_AUTHORITATIVE_INFORMATION", "204 NO_CONTENT", "205 RESET_CONTENT", "206 PARTIAL_CONTENT", "207 MULTI_STATUS", "208 ALREADY_REPORTED", "226 IM_USED", "300 MULTIPLE_CHOICES", "301 MOVED_PERMANENTLY", "302 FOUND", "302 MOVED_TEMPORARILY", "303 SEE_OTHER", "304 NOT_MODIFIED", "305 USE_PROXY", "307 TEMPORARY_REDIRECT", "308 PERMANENT_REDIRECT", "400 BAD_REQUEST", "401 UNAUTHORIZED", "402 PAYMENT_REQUIRED", "403 FORBIDDEN", "404 NOT_FOUND", "405 METHOD_NOT_ALLOWED", "406 NOT_ACCEPTABLE", "407 PROXY_AUTHENTICATION_REQUIRED", "408 REQUEST_TIMEOUT", "409 CONFLICT", "410 GONE", "411 LENGTH_REQUIRED", "412 PRECONDITION_FAILED", "413 PAYLOAD_TOO_LARGE", "413 REQUEST_ENTITY_TOO_LARGE", "414 URI_TOO_LONG", "414 REQUEST_URI_TOO_LONG", "415 UNSUPPORTED_MEDIA_TYPE", "416 REQUESTED_RANGE_NOT_SATISFIABLE", "417 EXPECTATION_FAILED", "418 I_AM_A_TEAPOT", "419 INSUFFICIENT_SPACE_ON_RESOURCE", "420 METHOD_FAILURE", "421 DESTINATION_LOCKED", "422 UNPROCESSABLE_ENTITY", "423 LOCKED", "424 FAILED_DEPENDENCY", "425 TOO_EARLY", "426 UPGRADE_REQUIRED", "428 PRECONDITION_REQUIRED", "429 TOO_MANY_REQUESTS", "431 REQUEST_HEADER_FIELDS_TOO_LARGE", "451 UNAVAILABLE_FOR_LEGAL_REASONS", "500 INTERNAL_SERVER_ERROR", "501 NOT_IMPLEMENTED", "502 BAD_GATEWAY", "503 SERVICE_UNAVAILABLE", "504 GATEWAY_TIMEOUT", "505 HTTP_VERSION_NOT_SUPPORTED", "506 VARIANT_ALSO_NEGOTIATES", "507 INSUFFICIENT_STORAGE", "508 LOOP_DETECTED", "509 BANDWIDTH_LIMIT_EXCEEDED", "510 NOT_EXTENDED", "511 NETWORK_AUTHENTICATION_REQUIRED"

  - `transactionId` (string, required)
    The unique identifier of the transaction.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `badRequestErrorDetails` (array)

  - `badRequestErrorDetails.type` (string, required)
    The type of error details.

  - `badRequestErrorDetails.issues` (array, required)
    An array of request issues.

  - `badRequestErrorDetails.issues.source` (string)
    The part of the request with an issue.

  - `badRequestErrorDetails.issues.subject` (string)
    The issue key.

  - `badRequestErrorDetails.issues.description` (string)
    An explanation of the issue.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 422 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `serverErrorDetails` (array)

  - `serverErrorDetails.type` (string, required)

  - `serverErrorDetails.retryAfterSeconds` (integer, required)


