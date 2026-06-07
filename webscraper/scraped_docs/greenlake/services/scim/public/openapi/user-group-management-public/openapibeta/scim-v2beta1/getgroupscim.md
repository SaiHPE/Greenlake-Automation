---
title: "GET /identity/v2beta1/scim/v2/Groups/{groupId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/getgroupscim.md"
scraped_at: "2026-06-07T06:15:36.006043+00:00Z"
---

# Get a user group

Get a user group. Compliant with SCIM 2.0.

Endpoint: GET /identity/v2beta1/scim/v2/Groups/{groupId}
Version: v2.0
Security: Bearer

## Path parameters:

  - `groupId` (string, required)
    The HPE GreenLake user group ID. Retrieve the ID from the CREATE Group endpoint or the GET Group endpoint.

## Response 200 fields (application/scim+json):

  - `schemas` (array, required)
    Collection of schema URIs that define the structure and valid attributes for this resource.
Each URI represents a schema that determines which properties can be included and how they should be formatted.
    Enum: "urn:ietf:params:scim:schemas:core:2.0:Group", "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Group"

  - `id` (string, required)
    The unique identifier for an HPE GreenLake user group.
    Example: "448ebfdb-7bc9-402f-9eb0-f9a86c06ca5a"

  - `displayName` (string, required)
    Unique display name for the user group. A valid displayName can contain alphanumeric characters, space, 
      or any of the following: -, /, _, ., !, (, ), [, ], ``
    Example: "Sales Group"

  - `meta` (object, required)
    resource metadata

  - `meta.created` (string)
    The date and time the resource was created.
    Example: "2022-01-01T00:00:00Z"

  - `meta.lastModified` (string)
    The date and time the resource was last modified.
    Example: "2022-01-01T00:00:00Z"

  - `meta.location` (string)
    The resource location URI.
    Example: "/identity/v2beta1/scim/v2/Groups/12345ef4-c6d5-4288-b5f7-71730bd12345"

  - `meta.resourceType` (string)
    The type of the resource.
    Enum: "Group"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Group` (object, required)
    The SCIM group extension defines additional attributes and structure
for group resources in the SCIM API. This extension is compliant
with [SCIM 2.0](https://tools.ietf.org/html/rfc7644).

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Group.hpe_principal` (string)
    The security principal for role assignments.
    Example: "user-group:448ebfdb-7bc9-402f-9eb0-f9a86c06ca5a"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Group.groupDescription` (string)
    A description of the user group. This might include the group's purpose or responsibilities. This helps administrators understand the group's role in the Organization.
    Example: "Office users"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Group.source` (string)
    The source of the user group, defines where the user's group lifecycle is being controlled from.
    Enum: "Local", "SCIM", "External"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Group.sourceInstance` (string)
    The source instance is set according to the source of the user group.
It will be the following according to the source type:

- Local—A group managed by the current organization. 
  - Source instance—The current organization's orgId.

- SCIM—A group managed by a SCIM integration, for example, Azure.
  - Source instance—The SCIM Integration's scimId.

- External—A group managed by a different organization.
  - Source instance—The external controlling organization's ID.
    Example: "d27e9581-f879-4c3d-b902-29c0a48f0002"

## Response 400 fields (application/scim+json):

  - `schemas` (array, required)
    Enum: "urn:ietf:params:scim:api:messages:2.0:Error", "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error"

  - `status` (string, required)
    The HTTP status code
    Example: "400"

  - `detail` (string, required)
    Additional detailed information about the error.
    Example: "Request is unparsable, syntactically incorrect, or violates schema."

  - `scimType` (string)
    A machine-readable error type that indicates the nature of the error.
This is a SCIM-specific error type.
    Example: "invalidSyntax"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error` (object)
    The HPE GreenLake error extension defines additional attributes and structure
for error responses in the SCIM API.

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.httpStatusCode` (integer, required)
    http error code
    Example: 400

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.
    Example: "HPE_GL_IDENTITY_BAD_REQUEST"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.message` (string, required)
    A user-friendly error message.
    Example: "Bad request"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "a1f13ec0-8391-46ed-8517-f13ef13da145"

## Response 401 fields (application/scim+json):

  - `schemas` (array, required)
    Enum: "urn:ietf:params:scim:api:messages:2.0:Error", "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error"

  - `status` (string, required)
    The HTTP status code
    Example: "400"

  - `detail` (string, required)
    Additional detailed information about the error.
    Example: "Request is unparsable, syntactically incorrect, or violates schema."

  - `scimType` (string)
    A machine-readable error type that indicates the nature of the error.
This is a SCIM-specific error type.
    Example: "invalidSyntax"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error` (object)
    The HPE GreenLake error extension defines additional attributes and structure
for error responses in the SCIM API.

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.httpStatusCode` (integer, required)
    http error code
    Example: 400

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.
    Example: "HPE_GL_IDENTITY_BAD_REQUEST"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.message` (string, required)
    A user-friendly error message.
    Example: "Bad request"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "a1f13ec0-8391-46ed-8517-f13ef13da145"

## Response 403 fields (application/scim+json):

  - `schemas` (array, required)
    Enum: "urn:ietf:params:scim:api:messages:2.0:Error", "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error"

  - `status` (string, required)
    The HTTP status code
    Example: "400"

  - `detail` (string, required)
    Additional detailed information about the error.
    Example: "Request is unparsable, syntactically incorrect, or violates schema."

  - `scimType` (string)
    A machine-readable error type that indicates the nature of the error.
This is a SCIM-specific error type.
    Example: "invalidSyntax"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error` (object)
    The HPE GreenLake error extension defines additional attributes and structure
for error responses in the SCIM API.

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.httpStatusCode` (integer, required)
    http error code
    Example: 400

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.
    Example: "HPE_GL_IDENTITY_BAD_REQUEST"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.message` (string, required)
    A user-friendly error message.
    Example: "Bad request"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "a1f13ec0-8391-46ed-8517-f13ef13da145"

## Response 404 fields (application/scim+json):

  - `schemas` (array, required)
    Enum: "urn:ietf:params:scim:api:messages:2.0:Error", "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error"

  - `status` (string, required)
    The HTTP status code
    Example: "400"

  - `detail` (string, required)
    Additional detailed information about the error.
    Example: "Request is unparsable, syntactically incorrect, or violates schema."

  - `scimType` (string)
    A machine-readable error type that indicates the nature of the error.
This is a SCIM-specific error type.
    Example: "invalidSyntax"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error` (object)
    The HPE GreenLake error extension defines additional attributes and structure
for error responses in the SCIM API.

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.httpStatusCode` (integer, required)
    http error code
    Example: 400

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.
    Example: "HPE_GL_IDENTITY_BAD_REQUEST"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.message` (string, required)
    A user-friendly error message.
    Example: "Bad request"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "a1f13ec0-8391-46ed-8517-f13ef13da145"

## Response 429 fields (application/scim+json):

  - `schemas` (array, required)
    Enum: "urn:ietf:params:scim:api:messages:2.0:Error", "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error"

  - `status` (string, required)
    The HTTP status code
    Example: "400"

  - `detail` (string, required)
    Additional detailed information about the error.
    Example: "Request is unparsable, syntactically incorrect, or violates schema."

  - `scimType` (string)
    A machine-readable error type that indicates the nature of the error.
This is a SCIM-specific error type.
    Example: "invalidSyntax"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error` (object)
    The HPE GreenLake error extension defines additional attributes and structure
for error responses in the SCIM API.

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.httpStatusCode` (integer, required)
    http error code
    Example: 400

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.
    Example: "HPE_GL_IDENTITY_BAD_REQUEST"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.message` (string, required)
    A user-friendly error message.
    Example: "Bad request"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "a1f13ec0-8391-46ed-8517-f13ef13da145"

## Response 500 fields (application/scim+json):

  - `schemas` (array, required)
    Enum: "urn:ietf:params:scim:api:messages:2.0:Error", "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error"

  - `status` (string, required)
    The HTTP status code
    Example: "400"

  - `detail` (string, required)
    Additional detailed information about the error.
    Example: "Request is unparsable, syntactically incorrect, or violates schema."

  - `scimType` (string)
    A machine-readable error type that indicates the nature of the error.
This is a SCIM-specific error type.
    Example: "invalidSyntax"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error` (object)
    The HPE GreenLake error extension defines additional attributes and structure
for error responses in the SCIM API.

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.httpStatusCode` (integer, required)
    http error code
    Example: 400

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.
    Example: "HPE_GL_IDENTITY_BAD_REQUEST"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.message` (string, required)
    A user-friendly error message.
    Example: "Bad request"

  - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Error.debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "a1f13ec0-8391-46ed-8517-f13ef13da145"


