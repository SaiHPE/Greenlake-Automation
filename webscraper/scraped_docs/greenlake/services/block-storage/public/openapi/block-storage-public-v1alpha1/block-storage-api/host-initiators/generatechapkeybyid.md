---
title: "POST /block-storage/v1alpha1/host-initiators/{hostId}/chapkey"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-initiators/generatechapkeybyid.md"
scraped_at: "2026-06-07T06:14:31.557992+00:00Z"
---

# Generate a DH-HMAC-CHAP host key usable for NVMe In-Band Authentication for Host by {hostId}

CHAP key can be generated only on NVMe/TCP host on HPE GreenLake for Block Storage 10.5.0 and later system OS versions.

Endpoint: POST /block-storage/v1alpha1/host-initiators/{hostId}/chapkey
Version: 1.0.0
Security: bearer

## Path parameters:

  - `hostId` (string, required)
    Id of the Host.
    Example: "2b09e744496246859fde6c132b2091d3"

## Request fields (application/json):

  - `system` (string, required)
    system to which NVMe/TCP initiator has connectivity
    Example: "15.212.100.100"

  - `type` (string, required)
    type for generate CHAP key. Allowed values are INITIATOR | TARGET.
    Enum: "INITIATOR", "TARGET"

  - `secret` (string, required)
    secret (in hexadecimal characters) to be used to initialize the key. Length of secret should be one of 64 | 96 | 128 based on hmacNum. (hmacNum, Length of secret): (NONE, 64) | (SHA256, 64) | (SHA384, 96) | (SHA512, 128)
    Example: "DB174528097951E0CCF41D92476FCA228E77717F1AE82AB380FCA07A2A91ABCD"

  - `hmacNum` (string,null)
    HMAC function to use for key transformation. Expected values are NONE | SHA256 | SHA384 | SHA512. Default value is NONE.
    Enum: "NONE", "SHA256", "SHA384", "SHA512"

## Response 200 fields (application/json):

  - `chapkey` (string)
    Generated CHAP key for NVMe/TCP initiator
    Example: "DHHC-1:00:2xdFKAl5UeDM9B2SR2/KIo53cX8a6CqzgPygeiqRq83MSNuW:"

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response default fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


