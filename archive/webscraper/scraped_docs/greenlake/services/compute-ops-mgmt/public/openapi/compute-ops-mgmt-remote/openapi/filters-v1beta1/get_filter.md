---
title: "GET /compute-ops-mgmt/v1beta1/filters/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/filters-v1beta1/get_filter.md"
scraped_at: "2026-06-07T06:14:43.643412+00:00Z"
---

# Get a saved filter

Retrieve a single saved filter resource by ID.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: GET /compute-ops-mgmt/v1beta1/filters/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Filter ID

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `id` (string)
    Primary identifier for the filter resource given by the system.
    Example: "b870f080-6448-48c5-b23a-d04f2d489174"

  - `type` (string)
    The type of the resource.

  - `generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `createdAt` (string)
    Time of filter resource creation.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `updatedAt` (string)
    Time of the last update to the filter resource.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `resourceUri` (string)
    URI to the filter resource itself (i.e. a self link).
    Example: "/compute-ops-mgmt/v1beta1/filters/b870f080-6448-48c5-b23a-d04f2d489174"

  - `name` (string)
    The display name of the filter, must be unique.

  - `description` (string,null)
    An optional longer description of the filter.

  - `readOnly` (boolean)
    If true, the filter is pre-defined and cannot be edited or deleted.

  - `filterResourceType` (string)
    The type of the resource that the filter matches against.  New resource types may be added as a backward
compatible change to the API.
    Enum: "compute-ops-mgmt/server"

  - `enabledForRRP` (boolean)
    Flags the filter for use with resource restriction policies used by scope-based access control (SBAC). Only administrators with full access to all scopes can create, edit, or delete RRP-enabled filters. The use of some resource properties may be disallowed in RRP-enabled filters.

  - `filter` (string,null)
    The filter expression, in the same syntax as the filter query parameter common to many
collection endpoints.  At least one of filter and filterTags must be specified.  If both are specified,
both filter expressions much match for a resource to match the filter.

  - `filterTags` (string,null)
    An optional filter expression for tags, in the same syntax as the filter-tags query parameter common to many
collection endpoints.  Used to handle tag keys with special characters.  At least one of filter and filterTags
must be specified.  If both are specified, both filter expressions much match for a resource to match the filter.

  - `uiData` (object,null)
    Opaque JSON structure used by the Compute Ops Management UI.  Other clients should not read or set this property.
Note that the format of the data is subject to change without notice, even with the same API version of filters.

  - `matchesUri` (string)
    URI of collection of match entities that indicate which resources match the filter.
    Example: "/compute-ops-mgmt/v1beta1/filters/b870f080-6448-48c5-b23a-d04f2d489174/matches"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 406 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error


