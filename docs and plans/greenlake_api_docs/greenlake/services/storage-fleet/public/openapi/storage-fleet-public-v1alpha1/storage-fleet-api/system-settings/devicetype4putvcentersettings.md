---
title: "PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4putvcentersettings.md"
scraped_at: "2026-06-07T06:16:20.230808+00:00Z"
---

# Edit vCenter setting identified by {vcenterSettingId} on HPE Alletra Storage MP B10000 identified by {systemId}

Edit vCenter setting identified by {vcenterSettingId} on HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `vcenterSettingId` (string, required)
    UID(vcenterSettingId) of the storage system
    Example: "7e92269a-12d1-35b4-60e8-5919edfc5475"

## Request fields (application/json):

  - `certChainPem` (string)
    Certificate chain of the VCenter server as PEM data
    Example: "-----BEGIN CERTIFICATE-----\nMIID2jCCAsKgAwIBAgIJAOiAEUfqLBfBMA0GCSqGSIb3DQEBCwUAMIGQMQswCQYD\n-----END CERTIFICATE-----\n"

  - `description` (string)
    Description of the vCenter setting
    Example: "vCenter - dataCenter1"

  - `inetaddress` (string)
    Host name or IP address of vCenter server
    Example: "15.71.130.25"

  - `name` (string)
    Name of the vCenter setting
    Example: "dataCenter1"

  - `password` (string)
    Password to login to the vCenter server
    Example: "pass"

  - `port` (integer)
    Port number of the vCenter server.
    Example: 443

  - `username` (string)
    Username to login to the vCenter server
    Example: "user1"

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


