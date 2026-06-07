---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4systemsettingslist.md"
scraped_at: "2026-06-07T06:16:05.553672+00:00Z"
---

# Get the system settings configuration details

Get the system settings configuration details

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings
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

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier for the resource.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.type` (string, required)
    The type of resource.
    Example: "system-settings"

  - `items.associatedLinks` (array,null)
    Associated Links Details
    Example: [{"resourceUri":"/storage-fleet/v1alpha1/devtype4-storage-systems/{id}","type":"systems"}]

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.authMode` (string,null)
    Password Authentication Mode
    Example: "Time-based one-time password mode"

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

  - `items.customerId` (string)
    The customer application identifier
    Example: "fv5f41632a53497e88cdcebc715cc1cf"

  - `items.encryption` (object,null)

  - `items.encryption.backupSaved` (boolean,null)
    Encryption settings and/or key backed up

  - `items.encryption.darState` (string,null)
    DAR state
    Example: "normal"

  - `items.encryption.enabled` (boolean,null)
    Encryption enabled

  - `items.encryption.failedDisks` (number,null)
    Number of failed disks
    Example: 2

  - `items.encryption.fipsCompliant` (string,null)
    FIPS compliant
    Example: "NotCompliant"

  - `items.encryption.keyLocation` (string,null)
    Location of encyption key Local or External key management
    Example: "LKM"

  - `items.encryption.kmpiProtocols` (array,null)
    KMIP protocols set
    Example: ["1.1","1.2"]

  - `items.encryption.licensed` (boolean,null)
    Encryption licensed

  - `items.encryption.notFipsPd` (number,null)
    Number of non FIPS compliant physical disks
    Example: 2

  - `items.encryption.notNodeSed` (number,null)
    Number of non SED node drives
    Example: 2

  - `items.encryption.notSedPd` (number,null)
    Number of non SED physical disks
    Example: 2

  - `items.encryption.seqNum` (number,null)
    Sequence number
    Example: 2

  - `items.encryption.serverCount` (number,null)
    Count of External Key Management servers
    Example: 2

  - `items.encryption.serverNames` (array,null)
    List of External Key Management servers
    Example: ["server1","server2"]

  - `items.encryption.serverPort` (number,null)
    Connection port number for External Key Managers
    Example: 2

  - `items.encryption.serverUser` (string,null)
    Username on External Key Manager
    Example: "Username"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627541300145

  - `items.installationsites` (object,null)

  - `items.installationsites.city` (string,null)
    City of the installation site
    Example: "Bangalore"

  - `items.installationsites.company` (string,null)
    Company name of the installation site
    Example: "Hewlett Packard Enterprise"

  - `items.installationsites.country` (string,null)
    Country of the installation site
    Example: "India"

  - `items.installationsites.hpePassportId` (string,null)
    HPE passport ID
    Example: "annajohn@gmail.com"

  - `items.installationsites.hpePassword` (string,null)
    Password of an HPE passport ID
    Example: "password"

  - `items.installationsites.id` (string)
    Unique identifier of the installation site
    Example: "2FF70002AC07E9C6"

  - `items.installationsites.postalCode` (string,null)
    Postal code of the installation site
    Example: "560001"

  - `items.installationsites.setSystemLocation` (boolean,null)
    Apply system location to the system descriptor property

  - `items.installationsites.state` (string,null)
    State of the installation site
    Example: "Karnataka"

  - `items.installationsites.streetAddress` (string,null)
    Street address of the installation site
    Example: "7992 Woodland Street"

  - `items.installationsites.supportProvider` (string,null)
    Support provider of the installation site
    Example: "HPE"

  - `items.installationsites.systemId` (string,null)
    SystemId/serialNumber of the array.
    Example: "7CE751P312"

  - `items.isFileEnabled` (boolean,null)
    Specifies whether the File persona is enabled or not

  - `items.isFipsEnabled` (boolean,null)
    Apply FIPS Standard

  - `items.name` (string,null)
    system name
    Example: "Array1"

  - `items.ntpServer` (string,null)
    ntp server
    Example: "15.213.68.208"

  - `items.remoteSyslogSettings` (object,null)

  - `items.remoteSyslogSettings.remoteSysLog` (integer,null)
    Remote Syslog Enabled/Disabled

  - `items.remoteSyslogSettings.remoteSysLogHost` (string,null)
    Host details for Remote Syslog
    Example: "[ 4.3.2.1:8080,1.2.3.4:8080 ]"

  - `items.remoteSyslogSettings.remoteSysLogSecurityHost` (string,null)
    Security Host details for Remote Syslog
    Example: "[ 5.6.7.8:8080,8.7.5.6:8080 ]"

  - `items.srinfo` (object,null)

  - `items.srinfo.percentUsed` (number,null)
    Used Percentage
    Example: 2

  - `items.srinfo.totalCapacityMiB` (number,null)
    Total Capacity in MiB
    Example: 90714

  - `items.srinfo.usedCapacityMiB` (number,null)
    Used Capacity in MiB
    Example: 1559

  - `items.supportcontact` (object,null)
    Contacts details set to receive alerts

  - `items.supportcontact.company` (string,null)
    Company
    Example: "HPE"

  - `items.supportcontact.companyCode` (string,null)
    Company code
    Example: "HPE"

  - `items.supportcontact.country` (string,null)
    Country
    Example: "US"

  - `items.supportcontact.fax` (string,null)
    Fax number
    Example: "fax_id"

  - `items.supportcontact.firstName` (string,null)
    First name
    Example: "john"

  - `items.supportcontact.id` (string)
    Unique Identifier of the contact and this can not be changed
    Example: "67d09515-8526-9b02-c0c4-c1f443a39402"

  - `items.supportcontact.includeSvcAlerts` (boolean,null)
    Email sent to contact shall include service alert

  - `items.supportcontact.lastName` (string,null)
    Last name
    Example: "kevin"

  - `items.supportcontact.notificationSeverities` (array,null)
    Severities of notifications the contact will be notificated. An array of number: 0 - Fatal, 1 - Critical, 2 - Major, 3 - Minor, 4 - Degraded, 5 - Info, 6 - Debug
    Example: [0,1,2,3,4,5]

  - `items.supportcontact.preferredLanguage` (string,null)
    Preferred language when being contacted or emailed
    Example: "en"

  - `items.supportcontact.primaryEmail` (string,null)
    Primary email address
    Example: "kevin.john@hpe.com"

  - `items.supportcontact.primaryPhone` (string,null)
    Primary phone
    Example: "98783456"

  - `items.supportcontact.receiveEmail` (boolean,null)
    Contact will receive email notifications
    Example: true

  - `items.supportcontact.receiveGrouped` (boolean,null)
    Contact will receive grouped low urgency email notifications
    Example: true

  - `items.supportcontact.secondaryEmail` (string,null)
    Secondary email address
    Example: "winny.pooh@hpe.com"

  - `items.supportcontact.secondaryPhone` (string,null)
    Secondary phone
    Example: "23456789"

  - `items.supportcontact.systemId` (string,null)
    SystemId/serialNumber of the array and this can not be changed
    Example: "7CE751P312"

  - `items.supportcontact.systemSupportContact` (boolean,null)
    Contact will be called for any system issues

  - `items.systemDate` (integer,null)
    system date time
    Example: 1580068830

  - `items.systemParameters` (object,null)

  - `items.systemParameters.cablingConfig` (string,null)
    Current Optimized cabling configuration. Value can be Performance or Capacity. This value is obtained only in HPE Alletra Storage MP B10000 systems with 10.5.0 and later OS version.
    Example: "Capacity"

  - `items.systemParameters.dsccReadOnly` (string)
    Read-Only mode for Data Services Cloud Console. Value can be "yes" or "no". Data Services Cloud Console Management Mode will be "Read Only" in Data Services Cloud Console if dsccReadOnly is set to "yes". In this mode, user is allowed only read-only (GET) operations from Data Services Cloud Console on the system which is enabled with read-only access for Data Services Cloud Console. The read-only mode can be enabled in HPE Alletra Storage MP B10000 systems from 10.5.0 and later OS versions.
    Example: "yes"

  - `items.systemParameters.fcRawSpaceAlert` (integer,null)
    FC raw space alert setting in MiB
    Example: 1

  - `items.systemParameters.maxVolumeRetention` (integer,null)
    Maximum global volume retention policy in seconds
    Example: 1209600

  - `items.systemParameters.overprovRatioLimit` (number,null)
    Over provisioning ratio limit setting

  - `items.systemParameters.overprovRatioWarning` (number,null)
    Over provisioning ratio warning setting

  - `items.systemParameters.rwareConfidence` (string,null)
    Confidence level with which the ransomware detection is enabled (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and later). Higher confidence levels decrease the sensitivity of the detection process. Lower confidence levels increase the sensitivity of the detection process. Lower confidence levels could lead to excessive numbers of false positive notifications. Possible values are high, medium and low. Defaults to medium.

  - `items.systemParameters.rwareRetentionTime` (number,null)
    Duration in seconds for which the alert snapshot generated during ransomware detection process, is retained. Defaults to 48 hours (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and later). Input can range from a minimum of 4 hours to a maximum of 30 days.
    Example: 1209600

  - `items.timezone` (string,null)
    system time zone
    Example: "Asia/Calcutta"

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


