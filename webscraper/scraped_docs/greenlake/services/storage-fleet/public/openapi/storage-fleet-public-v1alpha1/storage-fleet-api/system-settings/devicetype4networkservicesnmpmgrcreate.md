---
title: "POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicesnmpmgrcreate.md"
scraped_at: "2026-06-07T06:16:18.209799+00:00Z"
---

# Add SNMP Manager settings

Add SNMP Manager settings

Endpoint: POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `snmpConfig` (array,null)
    Specify the SNMP params

  - `snmpConfig.authenticationPassword` (string,null)
    Specify the SNMPv3 Authentication Password
    Example: "password_1"

  - `snmpConfig.managerIp` (string)
    Specify the IP address of the host from which the manager runs
    Example: "15.218.169.163"

  - `snmpConfig.notify` (string,null)
    Indicates the trap notification types defined by the HPE deviceType1 MIB
    Enum: "ALL", "NODUP", "STANDARD"

  - `snmpConfig.port` (integer,null)
    Specify the port number where the SNMP manager receives traps
    Example: 162

  - `snmpConfig.privPassword` (string,null)
    Specify the SNMPv3 Authentication Password
    Example: "password_1"

  - `snmpConfig.retry` (integer,null)
    Specify the number of times to send a trap (retry) if the SNMP manager is not available.
    Example: 2

  - `snmpConfig.timeoutSecs` (integer,null)
    Specify the number of seconds to wait before sending a trap (timeout).
    Example: 162

  - `snmpConfig.user` (string,null)
    Specify the SNMPv3 user name
    Example: "user1"

  - `snmpConfig.userMode` (string,null)
    Specify the SNMPv3 user mode
    Enum: "NEW", "EXISTING"

  - `snmpConfig.version` (integer,null)
    Specify the SNMP version supported
    Example: 2

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


