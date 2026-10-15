---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4certificateslist.md"
scraped_at: "2026-06-07T06:16:02.403727+00:00Z"
---

# Get array certificates by HPE Alletra Storage MP B10000

Get array certificates by HPE Alletra Storage MP B10000

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    Lucene query to filter Certificates by Key.
    Example: "service eq qw-client"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Unique Identifier of the resource. Filter
    Example: "99691e493067b2b2acf1774fc0ccc011"

  - `items.type` (string, required)
    The type of resource. Filter
    Example: "certificates"

  - `items.associatedLinks` (array)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.certType` (string,null)
    Type of array certificate
    Example: "cert"

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string)
    The cloud connectivity status of the system associated with this resource
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.commonname` (string,null)
    Commonname of the resource
    Example: "HPE_3PAR C630-4UW0002940"

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.displayname` (string,null)
    Displayname of the resource
    Example: "Certificate HPE_3PAR C630-4UW0002940"

  - `items.domain` (string,null)
    Domain of the resource
    Example: "hpe.com"

  - `items.enddate` (object,null)
    End date of the array certificate

  - `items.enddate.ms` (integer,null)
    time in millisecond
    Example: 1611599192000

  - `items.enddate.tz` (string,null)
    timezone
    Example: "Local"

  - `items.fingerprint` (string,null)
    Fingerprint of the resource

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627533096726

  - `items.issuer` (string,null)
    Issuer of the resource
    Example: "CN=HPE_3PAR C630-4UW0002940"

  - `items.pem` (string,null)
    array certificate pem

  - `items.serial` (string,null)
    Serial of the resource
    Example: "1"

  - `items.service` (string,null)
    Service name of the resource. Filter
    Example: "unified-server"

  - `items.signaturetype` (string,null)
    Signature type of the resource
    Example: "self-signed"

  - `items.startdate` (object,null)
    Start date of the array certificate

  - `items.subject` (string,null)
    Subject of the resource
    Example: "CN=HPE_3PAR C630-4UW0002940"

  - `items.subjectaltname` (string,null)
    Subjectaltname of the resource
    Example: "DNS:HPE_3PAR C630-4UW0002940"

  - `items.systemId` (string)
    SystemID of the array
    Example: "7CE809P009"

  - `items.text` (string,null)
    array certificate text

  - `items.uri` (string,null)
    URI of the resource
    Example: "/api/v3/certificates/99691e493067b2b2acf1774fc0ccc011"

  - `items.vcGuid` (string,null)
    vcGuid of the vCenter
    Example: "09r907r9hinfniauhfiqh98qh"

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

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


