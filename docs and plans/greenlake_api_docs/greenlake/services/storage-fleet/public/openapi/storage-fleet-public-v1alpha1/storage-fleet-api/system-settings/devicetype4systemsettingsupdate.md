---
title: "PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4systemsettingsupdate.md"
scraped_at: "2026-06-07T06:16:19.380571+00:00Z"
---

# Edit system settings configuration

Edit system settings configuration. Only one type of system settings i.e. either "authMode or dateTime or installationSites or name or ntpAddresses or remoteSyslogSettings or srinfo or supportContact or systemParameters" is allowed to be configured at a time.

Endpoint: PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `authMode` (object,null)

  - `authMode.authmode` (string,null)
    Sets password authentication mode (totp or ciphertext) for a system
    Example: "ciphertext"

  - `dateTime` (string,null)
    system date time. timezone is mandatory to configure this parameter.
    Example: "01/15/2020 10:00:00"

  - `installationSites` (object,null)

  - `installationSites.city` (string,null)
    City of the installation site
    Example: "Bangalore"

  - `installationSites.company` (string,null)
    Company name of the installation site
    Example: "Hewlett Packard Enterprise"

  - `installationSites.country` (string)
    Country of the installation site
    Example: "India"

  - `installationSites.postalCode` (string,null)
    Postal code of the installation site
    Example: "560001"

  - `installationSites.setSystemLocation` (boolean,null)
    Apply system location to the system descriptor property

  - `installationSites.state` (string,null)
    State of the installation site
    Example: "Karnataka"

  - `installationSites.streetAddress` (string,null)
    Street address of the installation site
    Example: "7992 Woodland Street"

  - `installationSites.supportProvider` (string,null)
    Support provider of the installation site
    Example: "HPE"

  - `name` (string,null)
    system name
    Example: "Array1"

  - `ntpAddresses` (array,null)
    system ntp addresses. timezone is mandatory to configure this parameter.

  - `remoteSyslogSettings` (object,null)

  - `remoteSyslogSettings.remoteSysLog` (integer,null)
    Remote Syslog Enabled/Disabled

  - `remoteSyslogSettings.remoteSysLogHost` (array,null)
    Host details for Remote Syslog
    Example: ["4.3.2.1:8080,1.2.3.4:8080"]

  - `remoteSyslogSettings.remoteSysLogSecurityHost` (array,null)
    Security Host details for Remote Syslog
    Example: ["5.6.7.8:8080,8.7.5.6:8080"]

  - `srinfo` (object,null)

  - `srinfo.newCapacityMiB` (number,null)
    New Capacity value should be given in MiB
    Example: 11000

  - `supportContact` (object,null)
    Contacts details set to receive alerts

  - `supportContact.company` (string,null)
    Company
    Example: "HPE"

  - `supportContact.companyCode` (string,null)
    Company code
    Example: "HPE"

  - `supportContact.country` (string,null)
    Country code as per official iso-countries list.
    Enum: "AF", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF", "BI", "KH", "CM", "CA", "CV", "KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR", "CU", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GN", "GW", "GY", "HT", "HM", "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IL", "IT", "JM", "JP", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MK", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "SH", "KN", "LC", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "SC", "SL", "SG", "SK", "SI", "SB", "SO", "ZA", "GS", "ES", "LK", "SD", "SR", "SJ", "SZ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU", "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW", "AX", "BQ", "CW", "GG", "IM", "JE", "ME", "BL", "MF", "RS", "SX", "SS", "XK"

  - `supportContact.fax` (string,null)
    Fax number
    Example: "fax_id"

  - `supportContact.firstName` (string,null)
    First name
    Example: "john"

  - `supportContact.id` (string)
    Unique Identifier of the contact and this can not be changed
    Example: "67d09515-8526-9b02-c0c4-c1f443a39402"

  - `supportContact.lastName` (string,null)
    Last name
    Example: "kevin"

  - `supportContact.notificationSeverities` (array,null)
    Severities of notifications the contact will be notificated. An array of number: 0 - Fatal, 1 - Critical, 2 - Major, 3 - Minor, 4 - Degraded, 5 - Info, 6 - Debug
    Example: [0,1,2,3,4,5]

  - `supportContact.preferredLanguage` (string,null)
    Preferred language when being contacted or emailed
    Example: "en"

  - `supportContact.primaryEmail` (string,null)
    Primary email address
    Example: "kevin.john@hpe.com"

  - `supportContact.primaryPhone` (string,null)
    Primary phone
    Example: "98783456"

  - `supportContact.receiveEmail` (boolean,null)
    Contact will receive email notifications
    Example: true

  - `supportContact.receiveGrouped` (boolean,null)
    Contact will receive grouped low urgency email notifications
    Example: true

  - `supportContact.secondaryEmail` (string,null)
    Secondary email address
    Example: "winny.pooh@hpe.com"

  - `supportContact.secondaryPhone` (string,null)
    Secondary phone
    Example: "23456789"

  - `supportContact.systemId` (string,null)
    SystemUid/serialNumber of the array and this can not be changed
    Example: "7CE751P312"

  - `systemParameters` (object,null)

  - `systemParameters.overprovRatioLimit` (number,null)
    Over provisioning ratio limit setting
    Example: 2

  - `systemParameters.overprovRatioWarning` (number,null)
    Over provisioning ratio warning setting
    Example: 1

  - `systemParameters.rwareConfidence` (string,null)
    Confidence level with which the ransomware detection is enabled (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and later). Higher confidence levels decrease the sensitivity of the detection process. Lower confidence levels increase the sensitivity of the detection process. Lower confidence levels could lead to excessive numbers of false positive notifications. Possible values are high, medium and low. Defaults to medium.
    Enum: "low", "medium", "high"

  - `systemParameters.rwareRetentionTime` (number,null)
    Duration in seconds for which the alert snapshot generated during ransomware detection process, is retained. Defaults to 48 hours (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and later). Input can range from a minimum of 4 hours to a maximum of 30 days.
    Example: 1209600

  - `timezone` (string,null)
    system time zone
    Example: "Asia/Calcutta"

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


