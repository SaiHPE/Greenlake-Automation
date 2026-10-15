---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4trustedcertificateslist.md"
scraped_at: "2026-06-07T06:16:19.375019+00:00Z"
---

# Get certificates trusted by HPE Alletra Storage MP B10000

Get certificates trusted by HPE Alletra Storage MP B10000

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates
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
    Example: "other"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Unique Identifier of the resource
    Example: "99691e493067b2b2acf1774fc0ccc011"

  - `items.type` (string, required)
    The type of resource.
    Example: "other"

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
    Displayname of the resource
    Example: "c3-hp-eskm-01"

  - `items.detail` (object,null)
    Detail of the trusted certificate

  - `items.detail.default` (string,null)
    default value of trusted certificate
    Example: "Valid Certificate"

  - `items.detail.key` (string,null)
    detail key of trusted certificate
    Example: "CERTIFICATE_VALID"

  - `items.displayname` (object,null)

  - `items.displayname.default` (string,null)
    Displayname of the resource
    Example: "Trust Certificate HPE_3PAR C630-4UW0002940"

  - `items.displayname.key` (string,null)
    Displayname of the resource
    Example: "Trust Certificate HPE_3PAR C630-4UW0002940"

  - `items.domain` (string,null)
    Domain of the resource
    Example: "hpe.com"

  - `items.enddate` (object,null)
    End date of the trusted certificate

  - `items.enddate.ms` (integer,null)
    time in millisecond
    Example: 1611599192000

  - `items.enddate.tz` (string,null)
    timezone
    Example: "Local"

  - `items.fingerprint` (string,null)
    Fingerprint of the resource
    Example: "2e92f97ad86fdcfff295841fefe20a1d71944923"

  - `items.hash` (string,null)
    Hash of the resource
    Example: "47efc91a.0"

  - `items.isValid` (boolean,null)
    validity of the resource
    Example: true

  - `items.issuer` (string,null)
    Issuer of the resource
    Example: "CN=c3-hp-eskm-01"

  - `items.keyUsage` (string,null)
    key usage of the resource

  - `items.pem` (string,null)
    trusted certificate pem
    Example: "-----BEGIN CERTIFICATE REQUEST-----abc----END CERTIFICATE REQUEST-----"

  - `items.serial` (string,null)
    Serial of the resource
    Example: "0"

  - `items.signaturetype` (string,null)
    Signature type of the resource
    Example: "self-signed"

  - `items.startdate` (object,null)
    Start date of the trusted certificate

  - `items.subject` (string,null)
    Subject of the resource
    Example: "CN=c3-hp-eskm-01"

  - `items.subjectaltname` (string,null)
    Alternate name of the subject of the resource
    Example: "CN=c3-hp-eskm-02"

  - `items.systemId` (string)
    SystemID of the array
    Example: "7CE809P009"

  - `items.uri` (string,null)
    URI of the resource
    Example: "/api/v3/trustcerts/99691e493067b2b2acf1774fc0ccc011"

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


