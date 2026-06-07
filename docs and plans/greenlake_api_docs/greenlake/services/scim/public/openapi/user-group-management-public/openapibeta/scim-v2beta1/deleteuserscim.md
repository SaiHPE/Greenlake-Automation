---
title: "DELETE /identity/v2beta1/scim/v2/Users/{userId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/deleteuserscim.md"
scraped_at: "2026-06-07T06:15:35.395501+00:00Z"
---

# Delete a user

Delete a user. Compliant with SCIM 2.0.

Endpoint: DELETE /identity/v2beta1/scim/v2/Users/{userId}
Version: v2.0
Security: Bearer

## Path parameters:

  - `userId` (string, required)
    The HPE GreenLake global user ID. Retrieve the ID from the CREATE User endpoint or the GET User endpoint.

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


## Response 204 fields
