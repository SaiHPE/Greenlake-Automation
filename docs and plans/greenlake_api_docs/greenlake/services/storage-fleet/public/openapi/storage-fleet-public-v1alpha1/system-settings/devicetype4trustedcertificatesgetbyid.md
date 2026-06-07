---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4trustedcertificatesgetbyid.md"
scraped_at: "2026-06-07T06:16:05.783811+00:00Z"
---

# Get certificates trusted by HPE Alletra Storage MP B10000 identified by {id}

Get certificates trusted by HPE Alletra Storage MP B10000 identified by {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates/{id}
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
    Example: "other"

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
    Displayname of the resource
    Example: "c3-hp-eskm-01"

  - `detail` (object,null)
    Detail of the trusted certificate

  - `detail.default` (string,null)
    default value of trusted certificate
    Example: "Valid Certificate"

  - `detail.key` (string,null)
    detail key of trusted certificate
    Example: "CERTIFICATE_VALID"

  - `displayname` (object,null)

  - `displayname.default` (string,null)
    Displayname of the resource
    Example: "Trust Certificate HPE_3PAR C630-4UW0002940"

  - `displayname.key` (string,null)
    Displayname of the resource
    Example: "Trust Certificate HPE_3PAR C630-4UW0002940"

  - `domain` (string,null)
    Domain of the resource
    Example: "hpe.com"

  - `enddate` (object,null)
    End date of the trusted certificate

  - `enddate.ms` (integer,null)
    time in millisecond
    Example: 1611599192000

  - `enddate.tz` (string,null)
    timezone
    Example: "Local"

  - `fingerprint` (string,null)
    Fingerprint of the resource
    Example: "2e92f97ad86fdcfff295841fefe20a1d71944923"

  - `hash` (string,null)
    Hash of the resource
    Example: "47efc91a.0"

  - `isValid` (boolean,null)
    validity of the resource
    Example: true

  - `issuer` (string,null)
    Issuer of the resource
    Example: "CN=c3-hp-eskm-01"

  - `keyUsage` (string,null)
    key usage of the resource

  - `pem` (string,null)
    trusted certificate pem
    Example: "-----BEGIN CERTIFICATE REQUEST-----abc----END CERTIFICATE REQUEST-----"

  - `serial` (string,null)
    Serial of the resource
    Example: "0"

  - `signaturetype` (string,null)
    Signature type of the resource
    Example: "self-signed"

  - `startdate` (object,null)
    Start date of the trusted certificate

  - `subject` (string,null)
    Subject of the resource
    Example: "CN=c3-hp-eskm-01"

  - `subjectaltname` (string,null)
    Alternate name of the subject of the resource
    Example: "CN=c3-hp-eskm-02"

  - `systemId` (string)
    SystemID of the array
    Example: "7CE809P009"

  - `uri` (string,null)
    URI of the resource
    Example: "/api/v3/trustcerts/99691e493067b2b2acf1774fc0ccc011"

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


