---
title: "POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4postreplicationpartners.md"
scraped_at: "2026-06-07T06:16:17.949057+00:00Z"
---

# Create replication partners on HPE Alletra Storage MP B10000 identified by {systemId}

Create replication partners on HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `replicationPartners` (array, required)

  - `replicationPartners.source` (object,null, required)
    Request body for creating remote copy targets

  - `replicationPartners.source.name` (string, required)
    Name of the remote copy target
    Example: "sample_RCtarget"

  - `replicationPartners.source.type` (integer, required)
    Specifies the link protocol. Do not use UNKNOWN as a linkType enumeration value when creating a Remote Copy target. 1 for IP Target Type, 2 for FC Target Type
    Example: 1

  - `replicationPartners.source.portPosAndLink` (array, required)
    Specifies all locations (portPos) of the local system, and all links(IP or WWN) of the remote system

  - `replicationPartners.source.portPosAndLink.link` (string, required)
    Specifies the link for the remote system. If the Link Protocol Type is IP, specify an IP address for the corresponding port on the remote system. If the Link Protocol Type is FC, specify the WWN of the peer port on the remote system
    Example: "10.100.65.128"

  - `replicationPartners.source.portPosAndLink.portPosition` (object, required)
    Specifies the port information of the local system (n:s:p) for Remote Copy.

  - `replicationPartners.source.portPosAndLink.portPosition.node` (integer, required)
    Port position node number

  - `replicationPartners.source.portPosAndLink.portPosition.port` (integer, required)
    Port position port number
    Example: 3

  - `replicationPartners.source.portPosAndLink.portPosition.slot` (integer, required)
    Port position slot number
    Example: 1

  - `replicationPartners.source.disabled` (boolean,null)
    Enable (true) or disable (false) the creation of the target in disabled mode
    Example: true

  - `replicationPartners.source.nodeWwn` (string,null)
    WWN of the node on the target system for FC Link type. Ignored if specified for IP type.
    Example: "2FF70002AC020DA1"

  - `replicationPartners.replicationPartnerSystemId` (string, required)
    SystemId of target array

  - `replicationPartners.target` (object,null, required)
    Request body for creating remote copy targets

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


