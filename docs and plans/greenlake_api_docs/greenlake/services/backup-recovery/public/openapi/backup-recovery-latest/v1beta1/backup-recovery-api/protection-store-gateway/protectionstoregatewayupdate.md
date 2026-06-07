---
title: "PATCH /backup-recovery/v1beta1/protection-store-gateways/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewayupdate.md"
scraped_at: "2026-06-07T06:14:11.125546+00:00Z"
---

# Modify the configuration of a Protection Store Gateway

Update a Protection Store Gateway.

Endpoint: PATCH /backup-recovery/v1beta1/protection-store-gateways/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    The UUID of the object
    Example: "c1a0eb78-41a0-4151-93b2-f057ffeca3f3"

## Request fields (application/merge-patch+json):

  - `dateTime` (object)

  - `dateTime.methodDateTimeSet` (string)
    Allowed:Ntp, VmHost. Method for how data and time is set on the appliance.
    Enum: "NTP", "VM_HOST"

  - `dateTime.timezone` (string)
    Timezone set on the appliance.

  - `dateTime.utcDateTime` (string)
    UTC date and time set on the appliance.

  - `dns` (array)
    DNS servers of the appliance

  - `dns.networkAddress` (string)
    DNS server configured on the appliance.

  - `ntp` (array)
    NTP servers of the appliance

  - `ntp.networkAddress` (string)
    An IP address or FQDN of the NTP server.

  - `proxy` (object)

  - `proxy.credentials` (object)

  - `proxy.credentials.password` (string)
    Password of proxy server

  - `proxy.credentials.username` (string)
    Username of proxy server

  - `proxy.networkAddress` (string)
    An IP address or FQDN to address the proxy server

  - `proxy.port` (integer)
    Port number of the proxy server

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


