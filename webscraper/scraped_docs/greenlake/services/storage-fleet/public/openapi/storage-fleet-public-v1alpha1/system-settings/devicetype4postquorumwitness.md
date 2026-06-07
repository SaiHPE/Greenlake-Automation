---
title: "POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4postquorumwitness.md"
scraped_at: "2026-06-07T06:16:03.499047+00:00Z"
---

# Create quorum witness on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Create quorum witness on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Endpoint: POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `srcReplicationId` (string, required)
    Id of source replication partner on which quorum witness is to be configured
    Example: "afb4961e47212e5bc88dd35db5be5c83"

  - `targetReplicationId` (string, required)
    Id of target replication partner on which quorum witness is to be configured
    Example: "afb4961e47212e5bc88dd35db5be5c83"

  - `replicationPartnerSystemId` (string, required)
    SystemId of target replication partner
    Example: "7CE816P0SR"

  - `parameters` (object, required)
    Parameters for create quorum witness action

  - `parameters.ipAddress` (string, required)
    Specifies the IP address of the Quorum Witness (QW) application to which the connectivity is created
    Example: "15.112.47.239"

  - `parameters.port` (integer,null)
    Specifies port number to be used to communicate with SSL to the Quorum Witness application.Default value is 8843
    Example: 8843

  - `parameters.ssl` (boolean,null)
    Specifies the SSL connectivity to the Quorum Witness to be created
    Example: true

  - `startQuorumWitness` (boolean,null)
    Specifies start/stop Quorum Witness connectivity on the storage system. If set true, ATF configuration is activated. If set false, ATF configuration is deactivated.
    Example: true

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


