---
title: "POST /private-cloud-business/v1beta1/systems/{id}/add-hypervisor-cluster"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/systems/addhypervisorclustertosystem.md"
scraped_at: "2026-06-07T06:15:38.502115+00:00Z"
---

# Initiates addition of a hypervisor cluster to system with the given id.

Adds the specified hypervisor cluster to the specified system. The user must have permissions to update this system. 
Returns a task identifier to be used by clients to track the progress of the operation.

Endpoint: POST /private-cloud-business/v1beta1/systems/{id}/add-hypervisor-cluster
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    Unique Identifier of the system, usually a UUID.

## Request fields (application/json):

  - `configureVds` (boolean)
    Specifies if vSphere Distributed Switch (VDS) should be configured for the hypervisor cluster
being added.

  - `hypervisorClusterName` (string)
    Name of the hypervisor cluster to be added.

  - `vsphereDatacenterName` (string)
    vSphere datacenter name where this hypervisor cluster is to be added.

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

## Response 409 fields (application/json):

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


