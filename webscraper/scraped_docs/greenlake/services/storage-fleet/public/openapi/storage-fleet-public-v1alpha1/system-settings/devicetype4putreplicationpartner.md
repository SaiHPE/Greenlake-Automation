---
title: "PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners/{replicationPartnerId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4putreplicationpartner.md"
scraped_at: "2026-06-07T06:16:04.298868+00:00Z"
---

# Edit replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 identified by {systemId}

Edit replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners/{replicationPartnerId}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `replicationPartnerId` (string, required)
    ID of device-type4 replication partner
    Example: "aedec7d11d02f73611a6ff992c256bdb"

## Request fields (application/json):

  - `addRcLinks` (object)
    Request body for adding remote copy links

  - `addRcLinks.source` (array, required)
    List of remote copy links to be added to source replication partner

  - `addRcLinks.source.address` (string, required)
    IP Address or WWN of Remote Copy target for this link, depending on the link type IP or FC
    Example: "10.100.65.128"

  - `addRcLinks.source.portPos` (object, required)
    Location (node, slot and port) of this link. For IP links, to be created with just node then the slot and port positions will be empty

  - `addRcLinks.source.portPos.node` (integer, required)
    Port position node number

  - `addRcLinks.source.portPos.port` (integer,null, required)
    Port position port number
    Example: 3

  - `addRcLinks.source.portPos.slot` (integer,null, required)
    Port position slot number
    Example: 1

  - `addRcLinks.source.targetName` (string, required)
    Remote Copy target with which the link is affiliated
    Example: "Sample_RCTarget"

  - `addRcLinks.source.type` (string, required)
    Remote Copy link type. 1 for IP and 2 for FC
    Example: 1

  - `addRcLinks.replicationPartnerSystemId` (string, required)
    SystemId of target replication partner
    Example: "7CE816P0SR"

  - `addRcLinks.target` (array, required)
    List of remote copy links to be added to target replication partner

  - `removeRcLinks` (object,null)
    Request Body for removing remote copy links

  - `removeRcLinks.source` (array, required)
    List of remote copy links to be deleted from source replication partner

  - `removeRcLinks.source.rcLinkId` (string, required)
    Id of remote copy link
    Example: "afb4961e47212e5bc88dd35db5be5c82"

  - `removeRcLinks.target` (array, required)
    List of remote copy links to be deleted from target replication partner

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


