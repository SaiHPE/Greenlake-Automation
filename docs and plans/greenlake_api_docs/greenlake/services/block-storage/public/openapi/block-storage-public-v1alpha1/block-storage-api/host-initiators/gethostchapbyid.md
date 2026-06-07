---
title: "GET /block-storage/v1alpha1/host-initiators/{hostId}/chap"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-initiators/gethostchapbyid.md"
scraped_at: "2026-06-07T06:14:31.557682+00:00Z"
---

# Get Host CHAP details by {hostId}

Get Host CHAP details by {hostId}

Endpoint: GET /block-storage/v1alpha1/host-initiators/{hostId}/chap
Version: 1.0.0
Security: bearer

## Path parameters:

  - `hostId` (string, required)
    Id of the Host.
    Example: "2b09e744496246859fde6c132b2091d3"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier for duplicate host group.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.type` (string, required)
    type
    Example: "Type of the resource"

  - `items.initiatorChapEnabled` (boolean,null)
    Initiator CHAP enabled or disabled
    Example: true

  - `items.initiatorChapKey` (string,null)
    Initiator CHAP key for NVMe/TCP host
    Example: "DHHC-1:01:xvNDJvVLNeOi/fC808nmnw3JTYFxRcGMkEewhdzia2P9LM6Z:"

  - `items.initiatorChapName` (string,null)
    Name of initiator CHAP set on iSCSI host
    Example: "chapnameSetDSCC"

  - `items.initiatorEncryptedChapSecret` (string,null)
    Encrypted Initiator CHAP secret set on iSCSI host
    Example: "aa7164fee47c0723"

  - `items.system` (string,null)
    Host CHAP details for a given system
    Example: "SGH014XGSP"

  - `items.targetChapEnabled` (boolean,null)
    Target CHAP enabled or disabled
    Example: true

  - `items.targetChapKey` (string,null)
    Target CHAP key for NVMe/TCP host
    Example: "DHHC-1:01:xvNDJvVLNeOi/fC808nmnw3JTYFxRcGMkEewhdzia2P9LM6Z:"

  - `items.targetChapName` (string,null)
    Name of target CHAP set on iSCSI host
    Example: "chapnameSetDSCC"

  - `items.targetEncryptedChapSecret` (string,null)
    Encrypted Target CHAP secret set on iSCSI host
    Example: "aa7164fee47c0723"

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

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


