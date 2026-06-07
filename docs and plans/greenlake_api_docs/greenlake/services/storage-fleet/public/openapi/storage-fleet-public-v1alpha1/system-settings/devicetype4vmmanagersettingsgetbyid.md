---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4vmmanagersettingsgetbyid.md"
scraped_at: "2026-06-07T06:16:06.602034+00:00Z"
---

# Get vCenter setting detail for a given vCenter setting of a HPE Alletra Storage MP B10000 storage system

Get vCenter setting detail for a given vCenter setting of a HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `vcenterSettingId` (string, required)
    UID(vcenterSettingId) of the storage system
    Example: "7e92269a-12d1-35b4-60e8-5919edfc5475"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique identifier of the vcenter settings.
    Example: "c0e4e72b-c9d3-54a4-312f-4ec0f8da498a"

  - `type` (string, required)
    The type of resource.
    Example: "vm-manager-settings"

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

  - `customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1ca"

  - `description` (string,null)
    Vcenter description
    Example: "sample vc description"

  - `friendlyCert` (object,null)
    Certificate detail in readable format

  - `friendlyCert.issuedTo` (string,null)
    Name of the certificate issued to
    Example: "15.213.64.88"

  - `friendlyCert.issuer` (string,null)
    Name of Certificate issued to
    Example: "CA"

  - `friendlyCert.validFrom` (object,null)
    The validity of the certificates

  - `friendlyCert.validFrom.ms` (integer,null)
    Epoch time in milliseconds
    Example: 1591601529000

  - `friendlyCert.validFrom.tz` (string,null)
    Time zone name
    Example: "Local"

  - `friendlyCert.validUntil` (object,null)
    The validity of the certificates

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627540916540

  - `inetaddress` (string,null)
    Address of the vcenter.
    Example: "18.213.214.145"

  - `name` (string,null)
    Name of vcenter.
    Example: "sample_vc_name"

  - `port` (integer,null)
    port number of vcenter.
    Example: 162

  - `resourceUri` (string,null)
    resourceUri for detailed vcenter setting object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE809P009/vm-manager-settings/centerid123"

  - `status` (object,null)
    Status of the vcenter setting

  - `status.default` (string,null)
    Default status value
    Example: "Ok"

  - `status.key` (string,null)
    Status key of vcenter
    Example: "VMPERF_FAILED"

  - `systemId` (string)
    SystemID of the array
    Example: "7CE809P009"

  - `username` (string,null)
    User of the vcenter configured.
    Example: "SysAdmin@machine.local"

  - `vmManagerType` (string,null)
    Type of the vmmanager settings.
    Example: "hyperV"

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


