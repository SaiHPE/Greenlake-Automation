---
title: "Data Services API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1.md"
scraped_at: "2026-06-07T06:13:36.566595+00:00Z"
---

# Data Services API

Data Services API

Version: 1.3.0
License: HPE End User License Agreement

## Servers

```
https://us-west.api.greenlake.hpe.com
```

```
https://eu-west.api.greenlake.hpe.com
```

```
https://eu-central.api.greenlake.hpe.com
```

```
https://ap-northeast.api.greenlake.hpe.com
```

## Security

### bearer

The Data Service Cloud Console API uses a JWT bearer token for authentication.
An authentication token can be obtained from the HPE GreenLake console.


Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Data Services API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/index.yaml)

## async-operations

Async Operations API

### Returns a list of async-operations accessible by the user

 - [GET /data-services/v1beta1/async-operations](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/async-operations/listasyncoperations.md): Returns a list of async-operations that are visible to the user. The response can
be paged by using the limit and offset query parameters and filtered and
sorted by using the filter and sort query parameters.

### Returns details of a specific async-operation

 - [GET /data-services/v1beta1/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/async-operations/getasyncoperation.md): Returns the async-operation with the given id.

## dual-auth-operations

Dual Authorization API

### List Dual Authorization operations

 - [GET /data-services/v1beta1/dual-auth-operations](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/dual-auth-operations/dualauthoperationslist.md): Returns the list of Dual Authorization operations for the current account. The list will include only the resource types (Application Resource) the user has read permission for. The user must have permission to read pending operations.

### Get Dual Authorization operation by Id

 - [GET /data-services/v1beta1/dual-auth-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/dual-auth-operations/dualauthoperationget.md): Returns the Dual Authorization operation for the given Id. The operation must belong to the current account and be a resource type the user has read permission for.  The user must also have permission to read pending operations.

### Changes the value of the given Dual Authorization operation. Approve/Deny the pending operation by changing its state in DB

 - [PATCH /data-services/v1beta1/dual-auth-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/dual-auth-operations/dualauthoperationupdate.md): Approve/Deny the pending operation by changing its state in DB.

## issues

Issues API

### List active issues

 - [GET /data-services/v1beta1/issues](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/issues/listissues.md): Returns the list of active issues for the account and user obtained from the request header. The list includes
issues only for the resource-types that the user has permissions to view. Active issues are issues in the CREATED 
state. Clients using this API must process the returned issues for any desired groupings.

### Returns all the supported Issues metadata relevant to the UI and API clients

 - [GET /data-services/v1beta1/issues-metadata](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/issues/getissuesmetadata.md): Returns the list of values of category, services, and severity supported by Issues.
Functionalities like query parameters, filtering, sorting, grouping, and paging are not supported.

### Get a singular issue

 - [GET /data-services/v1beta1/issues/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/issues/getissue.md): Returns an active issue with the specified id for the account obtained from the request header. The issue must be in the CREATED state

### Changes the attributes of an existing Issue object

 - [PATCH /data-services/v1beta1/issues/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/issues/patchissue.md): To snooze an Issue, this API should get a request with body {snoozedFor: timeperiod}. 
Currently, the allowed time-period for snoozing can be a day, a week, a month or infinite.
Hence, the values for snoozedFor should be from this set {"DAY", "WEEK", "MONTH", "INFINITE", "NONE"}.
"NONE" corresponds to unsnoozing a snoozed issue. When the Issue is unsnoozed, the snoozed_until is
set to zero timestamp. If any other value is received, HTTP 422 may be returned. Also, no other parameters
will be accepted in the body. The caller may get HTTP 422.

## secret-assignments

Secret Assignment Management APIs

### Reports filtered assignments

 - [GET /data-services/v1beta1/secret-assignments](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secret-assignments/reportassignmentsv1.md): Reports the attributes of the assignments owned by the customer. The response can be paged by using the limit and offset query parameters and filtered and sorted by using the filter and sort query parameters.

### Reports a specific assignment

 - [GET /data-services/v1beta1/secret-assignments/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secret-assignments/reportassignmentv1.md): Reports the attributes of the specified assignment.

## secrets

Secret Management APIs

### Reports filtered secrets

 - [GET /data-services/v1beta1/secrets](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secrets/reportsecretsv1.md): Reports the attributes and properties of the secrets owned by the customer. The response can be paged by using the limit and offset query parameters and filtered and sorted by using the filter and sort query parameters.

### Adds a secret

 - [POST /data-services/v1beta1/secrets](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secrets/addsecretv1.md): Adds a new secret using the provided specification.

### Removes a secret

 - [DELETE /data-services/v1beta1/secrets/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secrets/removesecretv1.md): Removes the specified secret. All associated assignments will also be removed.

### Reports a specific secret

 - [GET /data-services/v1beta1/secrets/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secrets/reportsecretv1.md): Reports the attributes and properties of the specified secret.

### Changes a secret

 - [PATCH /data-services/v1beta1/secrets/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secrets/changesecretv1.md): Changes an existing secret using the provided redefinition.

## settings

Settings API

### List settings for the current account.

 - [GET /data-services/v1beta1/settings](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/settings/settingslist.md): Returns all settings values for the current account

### Returns setting with given Id

 - [GET /data-services/v1beta1/settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/settings/settingget.md): Returns the details of the setting with the given ID. If a value does not exist for the setting, the API returns the default value.

### Update a setting

 - [PATCH /data-services/v1beta1/settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/settings/settingupdate.md): Changes the value of the given setting.

## software-components

Software Components

### Find a Software Release to install.

 - [GET /data-services/v1beta1/software-components/{id}/install-release](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/software-components/softwarecomponentsinstall.md): Find the latest stable Software Release that can be installed for the specified Software Component.
A Software Release is considered stable if the stability property is set to GENERAL_AVAILABILITY.

## software-releases

Software Releases

### List Software Releases

 - [GET /data-services/v1beta1/software-releases](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/software-releases/softwarereleaseslist.md): List multiple Software Releases with filtering, sorting and pagination.

Filtering is supported on the softwareComponent/id and version properties using the
eq, in, and and or operators. Sorting is supported on the id and version properties.

### Get a Software Release

 - [GET /data-services/v1beta1/software-releases/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/software-releases/softwarereleasesget.md): Get a single Software Release by its ID.

### Download a Software Release file

 - [POST /data-services/v1beta1/software-releases/{id}/download](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/software-releases/softwarereleasesdownload.md): Download a file within a Software Release.

## software-upgrades

Software Upgrades

### List upgrades for a Software Release

 - [GET /data-services/v1beta1/software-upgrades](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/software-upgrades/softwareupgradeslist.md): List the available upgrades for an installed Software Release, identified by a version and
Software Component ID. Pagination is not supported on the returned items.

The returned items are upgrades that can be applied to an existing installation of a Software
Release. Some releases can be applied immediately, while others may require corrective
actions to be completed before the release is allowed.

Upgrades beyond those initially returned can be found by recursively calling this API with
the new Software Release version. This can be useful for presenting the series of updates
required to bring an installation to the latest version.

## storage-locations

storage-locations API.

### List storage locations

 - [GET /data-services/v1beta1/storage-locations](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/storage-locations/listlocations.md): Returns a list of enabled storage locations. The following parameters are supported to
reduce the collection according to the specified criteria:

- filtering locations by capabilities;

## tags

Tags APIs

### GET tags

 - [GET /data-services/v1beta1/tags](https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/tags/listtags.md): Returns a list of all tags when no select query parameter is provided. 
When a select query parameter is provided, then key or value of the tags are returned.

