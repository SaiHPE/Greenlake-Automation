---
title: "POST /backup-recovery/v1beta1/protection-store-gateways/{id}/updateNic"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaynicupdate.md"
scraped_at: "2026-06-07T06:14:00.738749+00:00Z"
---

# Modifies a network interface on the Protection Store Gateway

Modify the network interface on the Protection Store Gateway

Endpoint: POST /backup-recovery/v1beta1/protection-store-gateways/{id}/updateNic
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    The UUID of the object
    Example: "c1a0eb78-41a0-4151-93b2-f057ffeca3f3"

## Request fields (application/json):

  - `force` (boolean)
    Optional. Defaults to 'true' if not specified. If specified and 'false' ,  the network changes will not be applied to Protection Store Gateway instance but will be applied to DSCC.  If specified and 'true' the network changes will be applied to both Catalyst Store Gateway instance and DSCC.
    Example: true

  - `nic` (object)

  - `nic.gateway` (string)
    Gateway associated with the network interface.

  - `nic.id` (string)
    id of the nic

  - `nic.networkAddress` (string)
    IP address associated with the network interface.

  - `nic.networkName` (string)
    Name of the hypervisor network.

  - `nic.networkType` (string)
    Type of the network
    Enum: "DHCP", "STATIC"

  - `nic.subnetMask` (string)
    Subnet mask.

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

## Response 412 fields (application/json):

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


