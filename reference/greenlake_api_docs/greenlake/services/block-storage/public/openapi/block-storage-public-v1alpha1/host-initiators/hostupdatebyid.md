---
title: "PUT /block-storage/v1alpha1/host-initiators/{hostId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostupdatebyid.md"
scraped_at: "2026-06-07T06:14:22.847876+00:00Z"
---

# Update Host by {hostId}

Update host details by {hostId}. Host can only be updated with the same protocol initiators

Endpoint: PUT /block-storage/v1alpha1/host-initiators/{hostId}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `hostId` (string, required)
    Id of the Host.
    Example: "2b09e744496246859fde6c132b2091d3"

## Request fields (application/json):

  - `initiatorsToCreate` (array)
    List of initiators to be created and added to this host

  - `initiatorsToCreate.address` (string,null, required)
    Address of the initiator.
    Example: "iqn.1998-01.com.vmware:61f7c688-3e93-d360-8043-70106f7a7e18-0cba0054"

  - `initiatorsToCreate.protocol` (string,null, required)
    protocol supported are : FC, iSCSI or NVMe
    Example: "iSCSI"

  - `initiatorsToCreate.driverVersion` (string,null)
    Driver version of the host initiator.
    Example: "4.1"

  - `initiatorsToCreate.firmwareVersion` (string,null)
    Firmware version of the host initiator.
    Example: "10.0"

  - `initiatorsToCreate.hbaModel` (string,null)
    Host bus adaptor model of the host initiator
    Example: "model-5"

  - `initiatorsToCreate.hostSpeed` (integer,null)
    Host speed
    Example: 1000

  - `initiatorsToCreate.ipAddress` (string,null)
    IP address of the initiator. Supported only for iSCSI and NVMe protocols
    Example: "15.212.100.100"

  - `initiatorsToCreate.name` (string,null)
    Name of the initiator.
    Example: "init1"

  - `initiatorsToCreate.vendor` (string,null)
    Vendor of the host initiator
    Example: "hpe"

  - `name` (string,null)
    Name of the host.
    Example: "host1"

  - `updatedInitiators` (array,null)
    List of existing initiator IDs to be replaced to the host

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


