---
title: "POST /virtualization/v1beta1/virtual-machines/migrate"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/migratevm.md"
scraped_at: "2026-06-07T06:16:30.309558+00:00Z"
---

# Migrate virtual machines

Migrate virtual machines to another cluster or datastore

Endpoint: POST /virtualization/v1beta1/virtual-machines/migrate
Version: 1.2.0
Security: bearer

## Query parameters:

  - `parameter-type` (string)
    Type of the query parameter (vms or sourceDataStoreIDs)

  - `vms` (array)
    A list of VM IDs to migrate or a list of SourceDatastoreIDs. If you specify the list of SourceDatastoreIDs, all VMs within the specified datastores are migrated. If you specify a list of VM IDs, only those VMs are migrated.

## Request fields (application/json):

  - `targetDatastoreId` (string, required)
    Target Datastore ID to which VMs will be migrated.

  - `hypervisorManagerId` (string, required)
    An identifier for the Hypervisor Manager.

  - `targetHypervisorClusterId` (string, required)
    An identifier for the target Hypervisor cluster.

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


