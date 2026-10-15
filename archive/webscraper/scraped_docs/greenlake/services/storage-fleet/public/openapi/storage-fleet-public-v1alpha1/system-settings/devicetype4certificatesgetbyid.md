---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4certificatesgetbyid.md"
scraped_at: "2026-06-07T06:16:02.551338+00:00Z"
---

# Get array certificates by HPE Alletra Storage MP B10000 identified by {id}

Get array certificates by HPE Alletra Storage MP B10000 identified by {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    ID of the certificate
    Example: "99691e493067b2b2acf1774fc0ccc011"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Identifier of the resource
    Example: "99691e493067b2b2acf1774fc0ccc011"

  - `type` (string, required)
    The type of resource.
    Example: "certificates"

  - `associatedLinks` (array)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `certType` (string,null)
    Type of array certificate
    Example: "cert"

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string)
    The cloud connectivity status of the system associated with this resource
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `commonname` (string,null)
    Commonname of the resource
    Example: "HPE_3PAR C630-4UW0002940\""

  - `customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `displayname` (string,null)
    Displayname of the resource
    Example: "Certificate HPE_3PAR C630-4UW0002940"

  - `domain` (string,null)
    Domain of the resource
    Example: "hpe.com"

  - `enddate` (object,null)
    End date of the array certificate

  - `enddate.ms` (integer,null)
    time in millisecond
    Example: 1611599192000

  - `enddate.tz` (string,null)
    timezone
    Example: "Local"

  - `fingerprint` (string,null)
    Fingerprint of the resource

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627533096726

  - `issuer` (string,null)
    Issuer of the resource
    Example: "CN=HPE_3PAR C630-4UW0002940"

  - `pem` (string,null)
    array certificate pem

  - `serial` (string,null)
    Serial of the resource
    Example: "1"

  - `service` (string,null)
    Service name of the resource
    Example: "unified-server"

  - `signaturetype` (string,null)
    Signature type of the resource
    Example: "self-signed"

  - `startdate` (object,null)
    Start date of the array certificate

  - `subject` (string,null)
    Subject of the resource
    Example: "CN=HPE_3PAR C630-4UW0002940"

  - `subjectaltname` (string,null)
    Subjectaltname of the resource
    Example: "DNS:HPE_3PAR C630-4UW0002940"

  - `systemId` (string)
    SystemID of the array
    Example: "7CE809P009"

  - `text` (string,null)
    array certificate text

  - `uri` (string,null)
    URI of the resource
    Example: "/api/v3/certificates/99691e493067b2b2acf1774fc0ccc011"

  - `vcGuid` (string,null)
    vcGuid of the vCenter
    Example: "09r907r9hinfniauhfiqh98qh"

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


