---
title: "POST /devices/v1beta1/devices"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1beta1/postdevices.md"
scraped_at: "2026-06-07T06:15:19.335303+00:00Z"
---

# Add devices (deprecated)

Add one or more devices to a workspace. This API provides an asynchronous response and will always  return 202 Accepted if basic input validations are successful. The  location header in the response provides the URI to be invoked for  fetching the progress of the device addition task. For details about the  status fetch URL, refer to the API Get progress or status of async operations in devices. NOTE: You need edit permissions for the Devices and Subscription service to invoke this API. Rate limits are enforced on this API. 25 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

Endpoint: POST /devices/v1beta1/devices
Version: latest
Security: Bearer

## Request fields (application/json):

  - `compute` (array, required)

  - `compute.partNumber` (string, required)
    Identifier of a product component or part.

  - `compute.serialNumber` (string, required)
    The serial number of the device.

  - `compute.tags` (object)

  - `network` (array, required)

  - `network.macAddress` (string, required)
    The media access control (MAC) address of the device.

  - `storage` (array, required)

  - `storage.partNumber` (string, required)
    The part number of the device.

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


