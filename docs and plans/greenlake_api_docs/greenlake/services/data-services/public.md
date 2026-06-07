---
title: "HPE GreenLake for Data Services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public.md"
scraped_at: "2026-06-07T05:46:09.047430+00:00Z"
---

# HPE GreenLake for Data Services

This page provides an introduction and quick start guide for the Data Services API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

HPE GreenLake for Data Services offers a RESTful API for
capabilities common to the following APIs: Backup Recovery, Public Cloud Business
Edition and Virtualization.

### Features

- Asynchronous Operations
- Dual Authorization Operations
- Issues
- Settings
- Software Catalog
- Storage Locations
- Tags


## Developer guide

This HPE GreenLake for Data Services API provides common capabilities used by a
number of HPE GreenLake services including Disaster Recovery and Private Cloud
Business Edition. The API follows the HPE GreenLake API standard.

The prerequisites section covers the endpoints, authentication, and authorization required to access the API, while the Making it all work section provides code samples for the API's various features.

### Prerequisites

#### Endpoints

Endpoints are the host URLs that you will submit your API requests to.
Data Services has unique endpoints in specific regions.
Use the following list to identify your application endpoint.

- US West: [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)
- EU West : [https://eu-west.api.greenlake.hpe.com](https://eu-west.api.greenlake.hpe.com)
- EU Central: [https://eu-central.api.greenlake.hpe.com](https://eu-central.api.greenlake.hpe.com)
- AP NorthEast: [https://ap-northeast.api.greenlake.hpe.com](https://ap-northeast.api.greenlake.hpe.com)


#### Authentication

The Data Services API uses an access token for authentication. Instructions
for obtaining an access token can be found on the [Authentication](/docs/greenlake/guides/public/authentication/authentication)
page.

The HTTP Authorization request header is used to provide the access token in
all API requests as a Bearer token.

- `Authorization:Bearer <access token>`


#### Authorization

All API requests are authorized using permissions. The user owning the access
token must have the required permissions assigned for the resources being accessed
in order to be authorized. The required permissions are documented in the
following guide pages.

### Making it all work

This section provides code samples of API requests and payloads for the various features of the Data Service API.

#### Asynchronous operations

Asynchronous operations track the progress of tasks or workflows performed by
services to manage resources. API operations that cannot be completed immediately
return the `202 Accepted` response code and a `Location` header containing the
URI of the asynchronous operation that can be used to track progress.
Asynchronous operations are also used to track scheduled operations that are initiated
by services on behalf of the user.

In some cases, an asynchronous operation may be composed of multiple sub-parts
that are processed independently. In such cases, the asynchronous operation
may have one or more child operations to represent the sub-parts. The parent will
always provide a summary view of progress for the overall operation or workflow.

##### URIs

- `/data-services/v1beta1/async-operations`
- `/data-services/v1beta1/async-operations/{id}`


##### Permissions

- `data-services.task.read`


##### List asynchronous operations


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/async-operations
```

The list operation can be modified using the standard filter, sort and pagination
query parameters.

##### Get an asynchronous operation


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/async-operations/21d09afe-5e5c-4993-99be-25772b67982d
```

The information returned for each asynchronous operation includes:

- `associatedResources` lists resources associated with the asynchronous
operation. These may be resources that are created by the operation or resources
involved in the operation. For example, an operation to create a volume may include
the storage-system that will host the volume and the volume itself once created.
- `state` indicates the current state of the operation:
  - `INITIALIZED` indicates the operation has not yet started.
  - `RUNNING` indicates the operation is in progress.
  - `SUCCEEDED` indicates successful completion.
  - `FAILED` indicates a failure state. If failed, the `error` property will
contain further details of the error condition.
  - `CANCELLED` indicates the operation was cancelled.
  - `PAUSED` indicates user interaction is required. If paused, the
`additionalDetails` property will contain a link to a console page that
can be used to perform the required interaction.
  - `TIMEDOUT` indicates that the agent processing the operation has not
reported progress for some time, for example, if the system performing the
operation has become disconnected.
- `error` records an error condition, including an error message and error code.
- `healthStatus` indicates if the operation has encountered any problems. The
values `ERROR` and `WARNING` indicate a known problem or problems that will be recorded in the
`error` property. The value `UNKNOWN` indicates that the agent processing the
operation has not reported progress for some time, for example, if the system
performing the operation has become disconnected.
- `logMessages` lists messages that indicate steps of progress.
- `progressPercentage` indicates how far the operation has progressed as a
percentage of total processing.
- `createdAt` is the time the operation was created.
- `startedAt` is the time the operation entered the `RUNNING` state.
- `endedAt` is the time the operation completed.
- `updatedAt` is the time of the last update to the operation.
- `hasChildOperations` indicates if there are any sub-operations, each is another
asynchronous operation.
- `parent` is a reference to the parent if this is a sub-operation or `null` if
it is the top level operation.
- `rootOperation` is a reference to the top level operation if this is a
sub-operation or `null` if this is the top level operation.


#### Dual authorization operations

Dual authorization is a security process that requires a second user to approve requests. A storage service determines which objects can be protected by dual authorization by adding the object as a system setting stored in the Settings Service or through onboarding an application with dual authorization itself. The Submitter and the Approver cannot be the same user.

- Ransomware attacks or insider attacks, where the malicious user attempts to delete the customers' data, are increasing in frequency. Dual Authorization provides strong protections from ransomware and insider attacks.
- Dual authorization is also a requirement for federal standards such as NIST 800-53.
- APIs can `GET` all dual authorization operations.
- APIs can `GET` a specific requested operation.
- APIs can Approve/Deny the pending operation by changing its state in the database.


##### URIs

- `/data-services/v1beta1/dual-auth-operations`
- `/data-services/v1beta1/dual-auth-operations/{id}`


##### Permissions

- `data-services.dual-auth-operation.read`
- `data-services.dual-auth-operation.update`
- `data-services.dual-auth-operation.delete`


##### List dual-authorization operations


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/dual-auth-operations
```

Response Fields:

- `count`: The total number of items in the response.
- `items`: A list of items, each representing a specific operation.
  - `associatedResources`: Lists resources associated with the operation.
    - `groups`: A list of groups associated with the resource.
      - `id`: The unique identifier of the group.
      - `name`: The name of the group.
    - `resource`: Details about the resource.
      - `consoleUri`: The URI to access the resource in the console.
      - `name`: The name of the resource.
      - `resourceUri`: The URI of the resource.
      - `type`: The type of the resource.
  - `checkedAt`: The timestamp when the operation was last checked.
  - `checkedByEmail`: The email of the user who last checked the operation.
  - `checkedByUri`: The URI of the user who last checked the operation.
  - `consoleUri`: Deprecated - use associatedResources instead.
  - `createdAt`: The timestamp when the operation was created.
  - `customerId`: The unique identifier of the customer.
  - `description`: A description of the operation.
  - `generation`: The generation or version of the operation.
  - `groups`: Deprecated - use associatedResources instead.
    - `id`: The unique identifier of the group.
    - `name`: The name of the group.
  - `id`: The unique identifier of the operation.
  - `name`: The name of the operation.
  - `operationResource`: Deprecated - use associatedResources instead.
    - `name`: The name of the resource.
    - `resourceUri`: The URI of the resource.
    - `type`: The type of the resource.
  - `requestedAt`: The timestamp when the operation was requested.
  - `requestedByEmail`: The email of the user who requested the operation.
  - `requestedByUri`: The URI of the user who requested the operation.
  - `requestedOperation`: The operation that was requested.
  - `resourceUri`: The self reference for this resource.
  - `sourceServiceExternalName`: The external name of the source service.
  - `state`: The current state of the operation.
  - `type`: The type of the operation.
  - `updatedAt`: The timestamp when the operation was last updated.
- `offset`: The offset for pagination.


##### Get a dual-authorization operation


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/dual-auth-operations/{id}
```

Response Fields:

- `associatedResources`: Lists resources associated with the operation.
  - `groups`: A list of groups associated with the resource.
    - `id`: The unique identifier of the group.
    - `name`: The name of the group.
  - `resource`: Details about the resource.
    - `consoleUri`: The URI to access the resource in the console.
    - `name`: The name of the resource.
    - `resourceUri`: The URI of the resource.
    - `type`: The type of the resource.
- `checkedAt`: The timestamp when the operation was last checked.
- `checkedByEmail`: The email of the user who last checked the operation.
- `checkedByUri`: The URI of the user who last checked the operation.
- `consoleUri`: Deprecated - use associatedResources instead.
- `createdAt`: The timestamp when the operation was created.
- `customerId`: The unique identifier of the customer.
- `description`: A description of the operation.
- `generation`: The generation or version of the operation.
- `groups`: Deprecated - use associatedResources instead.
  - `id`: The unique identifier of the group.
  - `name`: The name of the group.
- `id`: The unique identifier of the operation.
- `name`: The name of the operation.
- `operationResource`: Deprecated - use associatedResources instead.
  - `name`: The name of the resource.
  - `resourceUri`: The URI of the resource.
  - `type`: The type of the resource.
- `requestedAt`: The timestamp when the operation was requested.
- `requestedByEmail`: The email of the user who requested the operation.
- `requestedByUri`: The URI of the user who requested the operation.
- `requestedOperation`: The operation that was requested.
- `resourceUri`: The self reference for this resource.
- `sourceServiceExternalName`: The external name of the source service.
- `state`: The current state of the operation.
- `type`: The type of the operation.
- `updatedAt`: The timestamp when the operation was last updated.


##### Patch a dual-authorization operation


```bash
PATCH https://us-west.api.greenlake.hpe.com/data-services/v1beta1/dual-auth-operations/{id}
```

Response Fields:

- `associatedResources`: Lists resources associated with the operation.
  - `groups`: A list of groups associated with the resource.
    - `id`: The unique identifier of the group.
    - `name`: The name of the group.
  - `resource`: Details about the resource.
    - `consoleUri`: The URI to access the resource in the console.
    - `name`: The name of the resource.
    - `resourceUri`: The URI of the resource.
    - `type`: The type of the resource.
- `checkedAt`: The timestamp when the operation was last checked.
- `checkedByEmail`: The email of the user who last checked the operation.
- `checkedByUri`: The URI of the user who last checked the operation.
- `consoleUri`: Deprecated - use associatedResources instead.
- `createdAt`: The timestamp when the operation was created.
- `customerId`: The unique identifier of the customer.
- `description`: A description of the operation.
- `generation`: The generation or version of the operation.
- `groups`: Deprecated - use associatedResources instead.
  - `id`: The unique identifier of the group.
  - `name`: The name of the group.
- `id`: The unique identifier of the operation.
- `name`: The name of the operation.
- `operationResource`: Deprecated - use associatedResources instead.
  - `name`: The name of the resource.
  - `resourceUri`: The URI of the resource.
  - `type`: The type of the resource.
- `requestedAt`: The timestamp when the operation was requested.
- `requestedByEmail`: The email of the user who requested the operation.
- `requestedByUri`: The URI of the user who requested the operation.
- `requestedOperation`: The operation that was requested.
- `resourceUri`: The self reference for this resource.
- `sourceServiceExternalName`: The external name of the source service.
- `state`: The current state of the operation.
- `type`: The type of the operation.
- `updatedAt`: The timestamp when the operation was last updated.


#### Issues

Issues are used for tracking an issue or error that occurs in another service.

- Returns all the active issues related to the current user. Active issues have state = "CREATED".
- The issues are filtered by the user. For example, if there are 100 issues associated with 50 resources (of a specific resource-type), but the user has access to only 20 of those resources, this API will return only the issues associated with those 20 resources. In addition, the user must have the correct permissions to view issues.
- Returns the active issue with the given ID.
- Changes the attributes of an existing Issue object.
- Deletes the Issue object from the database.
- Returns all the supported Issues metadata relevant to the UI and API clients.


##### URIs

- `/data-services/v1beta1/issues`
- `/data-services/v1beta1/issues/{id}`
- `/data-services/v1beta1/issues-metadata`


##### Permissions

- `data-services.issue.read`
- `data-services.issue.update`


##### List issues


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/issues
```

##### Get an issue


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/issues/{id}
```

##### Patch an issue


```bash
PATCH https://us-west.api.greenlake.hpe.com/data-services/v1beta1/issues/{id}
```

##### Delete an issue


```bash
DELETE https://us-west.api.greenlake.hpe.com/data-services/v1beta1/issues/{id}
```

##### Get a list of valid values supported for a category, services, and severity supported by issues


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/issues-metadata
```

#### Secrets

Secrets are collections of properties that are used as security credentials and shared between customers and HPE GreenLake
applications and services. The Secrets service is responsible for securely storing secrets and then tracking how they
are assigned and applied to other customer-managed assets referred to by the service as appliances. Access to these
features is provided by API endpoints that work with *secret* and *secret-assignment* resources. A secret resource
contains a collection of credential properties of well-defined types along with information such as name, description,
and status. A secret-assignment resource represents an association between a secret resource identifier and a
consumer-provided appliance identifier along with application goal and progress information.

Reports of secret resources will include their *non-sensitive* properties as well as summary information aggregated
from associated secret-assignment resources. Properties considered to be *sensitive*, such as passwords and private
keys, will not be conveyed back to the consumer through the API and are available only to other services as required.

##### URIs

- `/data-services/v1beta1/secrets/{id}`
- `/data-services/v1beta1/secrets`
- `/data-services/v1beta1/secret-assignments/{id}`
- `/data-services/v1beta1/secret-assignments`


##### Permissions

- `data-services.secret.create`
- `data-services.secret.delete`
- `data-services.secret.read`
- `data-services.secret.update`


##### Report a specific secret


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/secrets/{id}
```

Reports the contents of a specific secret resource.
Attributes specific to secret resources include:

- `domain` An object describing the domain-level properties of the secret resource.
  - `name` This will always be `CONFIGURATION` for secret resources.
  - `properties` An object containing name/value pairs:
    - `CREATED_BY` The name of the user who created the secret.
    - `DESCRIPTION` The long description of the secret provided by the consumer.
    - `LAST_UPDATED_BY` The name of the user who last updated the secret.
    - `LIFECYCLE_EVENT_KEY` A consumer-provided identifier that accompanies secret resource lifecycle events
reported by the service.
    - `LOCK_DELETE` Set to true when the secret resource has been advisory delete-locked by a service.
- `subclassifier` An object describing the subclassifier-level properties of the secret resource. This will contain
the consumer-provided properties for credential values.
  - `name` Names the "type" of the secret and its intended use, determining which properties it is expected to
be composed of. It must be one of the following:
    - `AZURE_SPCLIENT` A Microsoft Azure Service Principal client.
    - `BASIC_AUTH` A secret used for password challenge-based authentication (for example, RFC 2617).
    - `BEARER_AUTH` A secret used for bearer token-based authorization (for example, RFC 6750).
    - `CERTIFICATE` A secret used for X.509-based authentication (for example, RFC 5280).
    - `GENERIC` A secret that may be used for any purpose.
    - `JSON_WEB_TOKEN` A secret used for JSON Web Token-based authorization (for example, RFC 7519).
    - `OAUTH_CLIENT` A secret used for OAuth 2.0-based authorization (for example, RFC 6749).
    - `PASSWORD` A secret used for password or passphrase authentication without the context of a principal
identifier.
    - `PRIVATE_KEY` A secret used for PKI-based authentication without the context of a public key.
    - `SSH_KEYPAIR` A secret used for Secure Shell (SSH)-based authentication (for example, RFC 4716).
  - `properties` An object containing name/value pairs of secret property values. Only non-sensitive properties are
conveyed here. As a result, the object may be reported as empty for some subclassifiers which represent only
sensitive properties (for example, `GENERIC`, `PASSWORD`, and `PRIVATE_KEY`).  The names of the properties may be one or
more of the following as determined by the subclassifier `name`:
    - `CLIENT_ID` A client principal's ID. Provided by subclassifiers `AZURE_SPCLIENT` and `OAUTH_CLIENT`.
    - `DER` A Base64-encoding of a PKI certificate in DER format. Provided by subclassifier `CERTIFICATE`.
    - `PEM` A Base64-encoding of a PKI certificate in PEM format. Provided by subclassifier `CERTIFICATE`.
    - `PUBLIC_KEY` Public key material. Provided by the subclassifier `SSH_KEYPAIR`.
    - `TENANT_ID` An Azure service principal client's tenant ID (or equivalent).  Provided by subclassifier
`AZURE_SPCLIENT`.
    - `TOKEN` Tokenized data used for authentication or authorization purposes. Provided by subclassifiers
`JSON_WEB_TOKEN` and `BEARER_AUTH`.
    - `USERNAME` A username or user ID. Provided by the subclassifier `BASIC_AUTH`.


##### Report filtered secrets


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/secrets
```

Reports all the secret resources owned by the customer, subject to filtering query parameters.

##### Add a secret


```bash
POST https://us-west.api.greenlake.hpe.com/data-services/v1beta1/secrets
```

Used to create a new secret resource using the secret specification provided in the request body.
The request body is a JSON object with the following *required* attributes:

- `service` (string) The name of a service or category associated with the secret resource at the time of its
creation. The value is limited to 256 Unicode characters (see note 1).  Consumers may provide an empty string if
non-specific. Can be used in query filter criteria.
- `name` (string) The name assigned to the secret resource. The value is limited to 256 Unicode characters
(see note 1) and must contain at least one character. It must be unique among all other secret resources owned by the
customer. Can be used in query filter criteria.
- `secret` (object) A JSON object that represents the desired subclassifier name and properties of the
secret. The form of the object depends on the subclassifier used:
  - for `AZURE_SPCLIENT`:
    - `{"azureSPClient": {"clientId": "string", "clientSecret": "string", "tenantId": "string"}}` where
      - `clientId` (required; non-sensitive) is the service principal's client ID. The value is limited to 512
Unicode characters (see note 1).
      - `clientSecret` (required; sensitive) is the service principal's client secret. The value is limited
to 512 Unicode characters (see note 1).
      - `tenantId` (optional; non-sensitive) is the service principal's tenant ID. The value is limited to 36
Unicode characters (see note 1).
  - for `BASIC_AUTH`:
    - `{"basicAuth": {"username": <string>, "password": <string>}}` where
      - `username` (required; non-sensitive) is the username or user ID. The value is limited to 256 Unicode
characters (see note 1) and must not contain white-space characters.
      - `password` (required; sensitive) is the password or passphrase. The value is limited to 256 Unicode
characters (see note 1).
  - for `BEARER_AUTH`:
    - `{"bearerAuth": {"token": <string>}}` where
      - `token` (required; non-sensitive) is the token material. The value is limited to 8192 Unicode
characters (see note 1) and must match the regex pattern `^[\w -.=]+$`.
  - for `CERTIFICATE`:
    - `{"certificate": {"pem": <string>}}` or `{"certificate": {"der": <string>}}` where
      - `der` (this or `pem` required; non-sensitive) is the Base64-encoding of a DER format PKI certificate.
The value is limited to 8192 characters and must match the pattern for a Base64 encoding.
      - `pem` (this or `der` required; non-sensitive) is the Base64-encoding of a PEM format PKI certificate.
The value has the same limitations as `der`.
  - for `GENERIC`:
    - `{"generic": {"secret": <string>}}` where
      - `secret` (required; sensitive) may be used for any kind of secret. The consumer must ensure it is
escaped properly for JSON encoding (Base64 is recommended).  The value is limited to 1024 Unicode characters
(see note 1).
  - for `JSON_WEB_TOKEN`:
    - `{"jsonWebToken": {"token": <string>}}` where
      - `token` (required; non-sensitive) is the JSON web token (JWT). The value is limited to 8192 Unicode
characters (see note 1) and must match the regex pattern `^[\w -.=]+$`.
  - for `OAUTH_CLIENT`:
    - `{"oauthClient": {"clientId": <string>, "clientSecret": <string>}}` where
      - `clientId` (required; non-sensitive) is the OAuth client ID. The value is limited to 512
Unicode characters (see note 1).
      - `clientSecret` (required; sensitive) is the OAuth client secret. The value is limited to 512
Unicode characters (see note 1).
  - for `PASSWORD`:
    - `{"password": {"password": <string>}}` where
      - `password` (required; sensitive) is the password or passphrase. The value is limited to 256 Unicode
characters (see note 1).
  - for `PRIVATE_KEY`:
    - `{"privateKey": {"privateKey": <string>}}` where
      - `privateKey` (required; sensitive) PKI private key material used for symmetric or asymmetric key
encryption. The value is limited to 4096 characters and must match the pattern for a Base64 encoding.
  - for `SSH_KEYPAIR`:
    - `{"sshKeypair": {"publicKey": <string>, "privateKey": <string>}}` where
      - `publicKey` (required; non-sensitive) PKI public key material used for asymmetric key encryption. The
value is limited to 4096 characters and must match the pattern for a Base64 encoding.
      - `privateKey` (required; sensitive) PKI private key material used for symmetric or asymmetric key
encryption. The value has the same limitations as `publicKey`.


Note 1
Except where explicitly stated otherwise, the acceptable characters are limited to the Unicode general categories
Letter, Mark, Number, Punctuation, and Symbol, and the Separator category Space. Any characters of the general category
Other as well as the Separator categories Line or Paragraph will be rejected.

Example:


```bash
curl -X 'POST' \
  'https://us-west.api.greenlake.hpe.com/data-services/v1beta1/secrets' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "service": "MycorpIT",
  "name": "Azure App 1",
  "secret": {
    "azureSPClient": {
      "clientId": "app1",
      "clientSecret": "cRyq8P8bbDxx7qrrWpG939Xr"
    }
  }
}'
```

##### Change a secret


```bash
PATCH https://us-west.api.greenlake.hpe.com/data-services/v1beta1/secrets/{id}
```

Used to update a secret resource using the secret redefinition provided in the request body.
The request body is a JSON Merge Patch object that must have at least one of the following attributes:

- `secret` (object) A JSON object that represents the desired changes to the secret's
subclassifier. Only the `properties` values of the subclassifier may be changed. The `name` value of the subclassifier
cannot be changed. The object takes the same form as the `secret` attribute object of the
[Add a secret](#add-a-secret) operation except that partial sets of properties are allowed with this attribute.
- `description` (string) Identical to the `description` attribute of the [Add a secret](#add-a-secret) operation.


Example:


```bash
curl -X 'PATCH' \
  'https://us-west.api.greenlake.hpe.com/data-services/v1beta1/secrets/bdaadb98-e3a2-11ee-8542-0100afe933f4' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "secret": {
    "azureSPClient": {
      "clientSecret": "BcytLruvkHk7X6wrTUS842Kf"
    }
  },
  "description": "Rotated secret 29-Feb-2024"
}'
```

##### Remove a secret


```bash
DELETE https://us-west.api.greenlake.hpe.com/data-services/v1beta1/secrets/{id}
```

Used to delete the specified secret resource and all its associated secret-assignment resources.
(Secret-assignment resources are not allowed to refer to non-existent secret resources.)

If the optional query parameter `safe` is set to `true` then the secret resource is checked for a service-applied
delete-lock constraint before it is removed.
If found, then the operation will fail with an HTTP status code `409 CONFLICT` response.
If the parameter is not requested, then the resource will be removed regardless of delete-lock status.
Thus, to override a conflicting delete-lock constraint a consumer may simply call the operation again without the
`safe` parameter or with it set to `false`.

##### Report a specific assignment


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/secret-assignments/{id}
```

Reports the contents of a specific secret-assignment resource.

##### Report filtered assignments


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/secret-assignments
```

Reports all the secret-assignment resources owned by the customer subject to filtering query parameters.

#### Settings

Settings holds one or more system settings of a service. These services can be set to require an approver when changing a system setting value by using the Dual-Authorization Operations service.

- Gets all the setting values for the current account.
- Gets the value for the current account for the input setting.
- Changes the value of the given setting.


##### URIs

- `/data-services/v1beta1/settings`
- `/data-services/v1beta1/settings/{id}`


##### Permissions

- `data-services.customer-setting.read`
- `data-services.customer-setting.update`


##### List all settings of a service


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/settings
```

##### Get a specific setting of a service


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/settings/{id}
```

##### Patch a specific setting of a service


```bash
PATCH https://us-west.api.greenlake.hpe.com/data-services/v1beta1/settings/{id}
```

#### Software catalog

The Software Catalog performs distribution for HPE developed software. It provides access to software and its metadata to support managed software offerings.

The specific list of available actions is as follows:

- List software releases with filters, sorting, and pagination.
- Get a software release by its ID.
- Download a file within specific software releases.


##### URIs

The URIs for the Software Catalog releases APIs are as follows:

- `GET /data-services/v1beta1/software-releases`
- `GET /data-services/v1beta1/software-releases/{id}`
- `POST /data-services/v1beta1/software-releases/{id}/download`


##### Permissions

There are no permissions associated with Software Catalog.

##### Get a release


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/software-releases/{id}
```

Where {id} is the ID of the release you would like to retrieve.

Returns:


```json
{
  "createdAt": "2019-08-24T14:15:22Z",
  "customerId": "00000000000000000000000000000000",
  "downloadable": true,
  "generation": 1,
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "name": "Example v1.0.0",
  "resourceUri": "/data-services/v1beta1/software-releases/497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "signature": {
    "filename": "example.ova.sig",
    "sha256Checksum": "c6a73c39b2c0d1f91594f81d01f0b79f40f6cd7a939cb3b6f1775fcf939ab3e6",
    "sizeInBytes": 1000
  },
  "software": {
    "filename": "example.ova",
    "sha256Checksum": "d63c742ff2c761619914400c18f34d2368ae84babc7eac9ffcaea8f40b68b505",
    "sizeInBytes": 10000
  },
  "softwareComponent": {
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "name": "Example",
    "type": "data-services/software-component"
  },
  "stability": "GENERAL_AVAILABILITY",
  "type": "data-services/software-release",
  "updatedAt": "2019-08-24T14:15:22Z",
  "usage": "INSTALL",
  "version": "1.0.0"
}
```

##### List releases


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/software-releases/?filter=version+eq+'1.0.0'&sort=id+asc
```

Where filter and sort are your chosen parameters. If left empty it will default to return all releases in ascending order by their ID.

Returns:


```json
{
  "count": 2,
  "items": [
    {
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "00000000000000000000000000000000",
      "downloadable": true,
      "generation": 1,
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "Example v1.0.0",
      "resourceUri": "/data-services/v1beta1/software-releases/497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "signature": {
        "filename": "example.ova.sig",
        "sha256Checksum": "c6a73c39b2c0d1f91594f81d01f0b79f40f6cd7a939cb3b6f1775fcf939ab3e6",
        "sizeInBytes": 1000
      },
      "software": {
        "filename": "example.ova",
        "sha256Checksum": "d63c742ff2c761619914400c18f34d2368ae84babc7eac9ffcaea8f40b68b505",
        "sizeInBytes": 10000
      },
      "softwareComponent": {
        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
        "name": "Example",
        "type": "data-services/software-component"
      },
      "stability": "GENERAL_AVAILABILITY",
      "type": "data-services/software-release",
      "updatedAt": "2019-08-24T14:15:22Z",
      "usage": "INSTALL",
      "version": "1.0.0"
    },
    {
      "createdAt": "2019-08-24T14:15:22Z",
      "customerId": "00000000000000000000000000000000",
      "downloadable": true,
      "generation": 1,
      "id": "e1a2d4a0-d5f1-429e-b10f-b4dc96e12b2c",
      "name": "Example 2 v1.0.0",
      "resourceUri": "/data-services/v1beta1/software-releases/e7a2d4a0-d5f1-429e-b10f-b4dc96e12b2c",
      "signature": {
        "filename": "example_2.ova.sig",
        "sha256Checksum": "c86dabc8e2e05c527f77b2858769efddfbb31efd476703c832f4bfb45c2e1eb3",
        "sizeInBytes": 1000
      },
      "software": {
        "filename": "example_2.ova",
        "sha256Checksum": "553295e4b848bee781c30a0c86a5b731330806eaaca214de195e48761b8a61ee",
        "sizeInBytes": 10000
      },
      "softwareComponent": {
        "id": "531bdc02-b2db-4a13-b640-f346fa09fa57",
        "name": "Example 2",
        "type": "data-services/software-component"
      },
      "stability": "GENERAL_AVAILABILITY",
      "type": "data-services/software-release",
      "updatedAt": "2019-08-24T14:15:22Z",
      "usage": "INSTALL",
      "version": "1.0.0"
    }
  ],
  "offset": 0,
  "total": 2
}
```

##### Download a release


```bash
POST https://us-west.api.greenlake.hpe.com/data-services/v1beta1/software-releases/{id}/download
```

Where {id} is the ID of the release you intend to download.

Combined with a request body such as below:


```json
{
  "file": "SOFTWARE"
}
```

Will return a 303 response code that redirects the user to a URL, to then download the software.

#### Storage locations

A Storage Location is a cloud service provider location that Data Services Cloud Console supports storing data in.

Storage Locations provides a single endpoint that returns a list of all of these locations.

Data Services Cloud Console products enable a subset of these locations according to their capabilities, and consumers are expected to use the relevant product or feature filter to return only the locations that are valid for that product or feature.

A selection from that list can then be used in other APIs on the platform to create storage resources in those locations.

##### URIs

- `/data-services/v1beta1/storage-locations`


##### Permissions

There are no permissions associated with Storage Locations, as information about which locations are supported is considered global information.

##### List locations

This is the only endpoint and provides a list of all supported locations.


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/storage-locations
```

The response returns a list of all locations with information about each including:

- `capabilities` a list of Data Services Cloud Console products that support the storage location.
- `generation` the revision of the storage location that increases every time it is updated.
- `id` the canonical ID of the location in Data Services Cloud Console, and is the ID to be used in downstream requests to Data Services Cloud Console APIs to create storage resources in that location.


The filter expression for this endpoint accepts the following operators on the following properties:

- `in` operator on the `capabilities` property;


For example:

- `'backup-and-recovery' in capabilities`;


Example Response:


```bash
GET "https://us-west.api.greenlake.hpe.com/data-services/v1beta1/storage-locations?filter='backup-and-recovery'+in+capabilities"
```


```json
{
  "count": 2,
  "items": [
    {
      "capabilities": [
        "backup-and-recovery"
      ],
      "city": "Washington",
      "cloudServiceProvider": "AWS",
      "cloudServiceProviderId": "us-east-1",
      "createdAt": "2024-02-05T16:02:31.329685Z",
      "generation": 1,
      "geography": "North America",
      "id": "aws:us-east-1",
      "name": "N. Virginia - AWS",
      "resourceUri": "/data-services/v1beta1/storage-locations/aws:us-east-1",
      "timezone": "US/Eastern",
      "type": "data-services/storage-location",
      "updatedAt": "2024-02-05T16:02:31.329685Z"
    },
    {
      "capabilities": [
        "backup-and-recovery"
      ],
      "city": "Columbus",
      "cloudServiceProvider": "AWS",
      "cloudServiceProviderId": "us-east-2",
      "createdAt": "2024-02-05T16:02:31.329685Z",
      "generation": 1,
      "geography": "North America",
      "id": "aws:us-east-2",
      "name": "Ohio - AWS",
      "resourceUri": "/data-services/v1beta1/storage-locations/aws:us-east-2",
      "timezone": "US/Eastern",
      "type": "data-services/storage-location",
      "updatedAt": "2024-02-05T16:02:31.329685Z"
    }
  ],
  "offset": 0,
  "total": 2
}
```

#### Tags

Tags are key-value pair metadata applied on Data Services Cloud Console managed resources for classification and categorization purposes. Tags API provides an endpoint to query a list of all available tags applied to Data Services Cloud Console resources for the requesting tenant.

The returned result set can be used to apply the same tags to other Data Services Cloud Console managed resource-types.

##### URIs

- `/data-services/v1beta1/tags`


##### Permissions

- There are no permissions required for the Tags API endpoint.


##### List tags

This endpoint provides a list of available tags for applying to Data Services Cloud Console managed resources.


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/tags
```


```json
{
  "items": [
    {
      "id": "053c447f-898f-41b0-9207-1464d90a7255",
      "key": "backup-schedule",
      "value": "",
      "type": "data-services/tag",
      "customerId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    },
    {
      "id": "d096962a-e2e2-4c47-86b9-625381508497",
      "key": "region",
      "value": "amr",
      "type": "data-services/tag",
      "customerId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
  ],
  "count": 2,
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

The filter expression for this endpoint accepts the following operators:

- `contains` operator on the `key` or `value` properties
- `value` operator on the `key` or `value` properties
- `sort` operator on the `key` or `value` properties
- `limit` and `offset` operator for paging returned `items`


For example:


```bash
GET https://us-west.api.greenlake.hpe.com/data-services/v1beta1/tags?filter=contains(key, 'reg') and value eq 'amr'&sort=key asc&limit=20&offset=0
```