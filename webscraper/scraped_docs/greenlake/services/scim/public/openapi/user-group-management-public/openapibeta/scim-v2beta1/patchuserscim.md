---
title: "PATCH /identity/v2beta1/scim/v2/Users/{userId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/patchuserscim.md"
scraped_at: "2026-06-07T06:15:35.802655+00:00Z"
---

# Patch user attributes

Updates one or more user attributes. Compliant with SCIM 2.0, except the attributes field is not supported.

Endpoint: PATCH /identity/v2beta1/scim/v2/Users/{userId}
Version: v2.0
Security: Bearer

## Path parameters:

  - `userId` (string, required)
    The HPE GreenLake global user ID. Retrieve the ID from the CREATE User endpoint or the GET User endpoint.

## Request fields (application/scim+json):

  - `schemas` (array, required)
    Collection of schema URIs that define the structure and valid attributes for this resource. Each URI represents a schema that determines which properties can be included and how they should be formatted.
    Enum: "urn:ietf:params:scim:api:messages:2.0:PatchOp"

  - `Operations` (array, required)
    List of operations to be performed on the user. See [RFC 7644, Section 3.5.2](https://www.rfc-editor.org/rfc/rfc7644#section-3.5.2).

  - `Operations.op` (string, required)
    Operations performed by patch.
  - add or Add—The user object has the specified attribute added to it or updated if it already exists.
  - remove or Remove—The user object has the specified attribute removed from it.
  - replace or Replace—The user object has the specified attribute replaced with the new value.
    Enum: "add", "Add", "remove", "Remove", "replace", "Replace"

  - `Operations.path` (string)
    Attribute path describing the target of the operation. 
This optional attribute must be only one path to a valid target in 
the user schemas.
    Example: "emails"

  - `Operations.value` (any)
    The value of the attribute or attributes to be added, removed, or replaced.
    Example: [{"value":"babs@jensen.org","primary":true}]

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


## Response 200 fields

## Response 204 fields
