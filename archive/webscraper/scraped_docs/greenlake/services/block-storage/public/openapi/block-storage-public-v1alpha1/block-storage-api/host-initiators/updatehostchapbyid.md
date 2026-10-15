---
title: "PUT /block-storage/v1alpha1/host-initiators/{hostId}/chap"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-initiators/updatehostchapbyid.md"
scraped_at: "2026-06-07T06:14:31.535457+00:00Z"
---

# Update Host CHAP by {hostId}

CHAP can be updated only on iSCSI host on HPE GreenLake for Block Storage 10.4.0 or later and NVMe/TCP host on HPE GreenLake for Block Storage 10.5.0 or later.

Endpoint: PUT /block-storage/v1alpha1/host-initiators/{hostId}/chap
Version: 1.0.0
Security: bearer

## Path parameters:

  - `hostId` (string, required)
    Id of the Host.
    Example: "2b09e744496246859fde6c132b2091d3"

## Request fields (application/json):

  - `items` (array,null)

  - `items.initiatorChapEnabled` (boolean,null)
    Initiator CHAP enabled or disabled
    Example: true

  - `items.initiatorChapKey` (string)
    Initiator CHAP key for NVMe/TCP host
    Example: "DHHC-1:01:xvNDJvVLNeOi/fC808nmnw3JTYFxRcGMkEewhdzia2P9LM6Z:"

  - `items.initiatorChapName` (string,null)
    Name of initiator CHAP
    Example: "chapnameSetDSCC"

  - `items.initiatorEncryptedChapSecret` (string)
    Base64 encoded Initiator CHAP Secret
    Example: "dGVzdGNoYXBzZWNyZXQ"

  - `items.system` (string)
    Host CHAP details for a given system
    Example: "SGH014XGSP"

  - `items.targetChapEnabled` (boolean,null)
    Target CHAP enabled or disabled
    Example: true

  - `items.targetChapKey` (string)
    Target CHAP key for NVMe/TCP host
    Example: "DHHC-1:01:xvNDJvVLNeOi/fC808nmnw3JTYFxRcGMkEewhdzia2P9LM6Z:"

  - `items.targetChapName` (string,null)
    Name of target CHAP
    Example: "chapnameSetDSCC"

  - `items.targetEncryptedChapSecret` (string)
    Base64 encoded Target CHAP Secret
    Example: "dGVzdGNoYXBzZWNyZXQ"

## Response 202 fields (application/json):

  - `taskUri` (string, required)
    Task URI which can be used to monitor the status of the operation.
    Example: "/rest/vega/v1/tasks/4969a568-6fed-4915-bcd5-e4566a75e00c"

  - `message` (string)
    Task Message.
    Example: "Successfully submitted"

  - `status` (string)
    Status of the task.
    Example: "SUBMITTED"

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


